#!/usr/bin/env python3
# Usage (ephemeral):
#   GIST_URL="https://gist.github.com/mkobit/gitignore-gen/raw/gitignore_gen.py"
#   curl -sSfL $GIST_URL | python3 - generate Python
#
# Development commands:
#   uv run ruff check .
#   uv run ty check src/
#   uv run pytest tests/
#
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Generator to compose .gitignore templates from upstream sources.

Source:  https://github.com/github/gitignore
Mirrors: https://codeload.github.com (default)

Example usage:
  # Define the gist URL for convenience
  GIST_URL="https://gist.github.com/mkobit/gitignore-gen/raw/gitignore_gen.py"

  # List all available templates
  curl -sSfL $GIST_URL | python3 - ls

  # List templates matching a regex
  curl -sSfL $GIST_URL | python3 - ls --include-regex '.*Python.*'

  # Generate a combined file for a typical cross-platform project
  curl -sSfL $GIST_URL | python3 - generate Python macOS Windows Node \\
    --output .gitignore

  # Appending to an existing file
  curl -sSfL $GIST_URL | python3 - generate macOS >> .gitignore

  # Interactive selection using fzf (highly recommended)
  # 1. Store the script in a variable to avoid multiple downloads
  GIST_SCRIPT=$(curl -sSfL $GIST_URL)
  # 2. Select interactively and generate
  python3 -c "$GIST_SCRIPT" generate $(python3 -c "$GIST_SCRIPT" ls | fzf --multi)

Storage & caching:
  Repository archives (.tar.gz) are stored locally to avoid redundant downloads.
  The default location is $XDG_CACHE_HOME/gitignore-gen or ~/.cache/gitignore-gen.
  In restricted environments, it falls back to /tmp/gitignore-gen.

  Note: This tool does not automatically purge old archives. To reclaim space,
  manually delete the cache directory.
"""

# TODO (Out of scope):
# - Support multiple sources in a single run (e.g., --source name=internal,...).
# - Built-in .netrc support for private internal repositories.
# - Optional delegation of downloads to the `gh api` CLI tool if installed.

from __future__ import annotations

import argparse
import asyncio
import datetime
import io
import logging
import os
import re
import sys
import tarfile
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Sequence

_DEFAULT_REPO = "github/gitignore"

logger = logging.getLogger("gitignore-gen")


def _get_default_cache() -> Path:
    """Return the XDG cache directory or a fallback."""
    try:
        home = Path.home()
    except (RuntimeError, ImportError):
        home = Path(os.environ.get("TMPDIR", "/tmp"))  # noqa: S108

    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "gitignore-gen"
    return home / ".cache" / "gitignore-gen"


def _parse_duration(duration_str: str) -> datetime.timedelta:
    """Parse a simple duration string into a timedelta."""
    match = re.match(r"(\d+)([dhm])", duration_str.lower())
    if not match:
        try:
            return datetime.timedelta(days=int(duration_str))
        except ValueError as e:
            msg = f"Invalid duration format: {duration_str}. Use e.g., '7d', '12h'."
            raise ValueError(msg) from e

    value, unit = int(match.group(1)), match.group(2)
    return {
        "d": datetime.timedelta(days=value),
        "h": datetime.timedelta(hours=value),
        "m": datetime.timedelta(minutes=value),
    }[unit]


def _setup_logging(verbosity: int) -> None:
    """Configure standard Python logging to stderr."""
    level = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}.get(
        verbosity, logging.DEBUG
    )
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
    )


class TemplateMember(ABC):
    """Abstract interface for a single template file in a source."""

    def __init__(self, path: str):
        self.path = path  # Canonical POSIX relative path (e.g. 'Python.gitignore')

    @abstractmethod
    async def read(self) -> str | None:
        """Read the content of the template."""


class TarTemplateMember(TemplateMember):
    """Template member stored within a tar archive."""

    def __init__(self, path: str, tar: tarfile.TarFile, internal_name: str):
        super().__init__(path)
        self._tar = tar
        self._internal_name = internal_name

    async def read(self) -> str | None:
        return await asyncio.to_thread(self._sync_read)

    def _sync_read(self) -> str | None:
        try:
            extracted = self._tar.extractfile(self._internal_name)
            if extracted:
                return extracted.read().decode("utf-8").strip()
        except Exception:
            logger.exception("Failed to read tar member: %s", self._internal_name)
        return None


class FileTemplateMember(TemplateMember):
    """Template member stored as a local file."""

    def __init__(self, path: str, full_path: Path):
        super().__init__(path)
        self._full_path = full_path

    async def read(self) -> str | None:
        return await asyncio.to_thread(self._sync_read)

    def _sync_read(self) -> str | None:
        try:
            return self._full_path.read_text(encoding="utf-8").strip()
        except Exception:
            logger.exception("Failed to read local file: %s", self._full_path)
        return None


class TemplateSource(ABC):
    """Abstract interface for a source of gitignore templates."""

    @abstractmethod
    async def get_members(self) -> list[TemplateMember]:
        """Return all available templates in this source."""

    @property
    @abstractmethod
    def source_label(self) -> str:
        """Label for metadata headers (e.g. 'github/gitignore')."""

    @property
    @abstractmethod
    def ref_label(self) -> str:
        """Label for metadata headers (e.g. 'main' or a local path)."""

    async def close(self) -> None:  # noqa: B027
        """Release resources associated with this source."""


class GitHubArchiveSource(TemplateSource):
    """Source that downloads a GitHub repository tarball."""

    def __init__(self, repo: str, ref: str, args: argparse.Namespace):
        self.repo = repo
        self.ref = ref
        self.args = args
        self._tar: tarfile.TarFile | None = None

    @property
    def source_label(self) -> str:
        return self.repo

    @property
    def ref_label(self) -> str:
        return self.ref

    async def _get_data(self) -> bytes | None:
        return await asyncio.to_thread(self._sync_get_data)

    def _sync_get_data(self) -> bytes | None:
        base_url = (
            cast("str", self.args.base_url).rstrip("/")
            if getattr(self.args, "base_url", None)
            else "https://codeload.github.com"
        )
        slug = self.repo.replace("/", "_")
        cache_dir = cast("Path", self.args.download_location)
        cache_file = cache_dir / f"{slug}_{self.ref}.tar.gz"

        if cache_file.exists():
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            mtime = datetime.datetime.fromtimestamp(
                cache_file.stat().st_mtime, tz=datetime.timezone.utc
            )
            period = cast("str", self.args.refresh_period)
            if (now - mtime) < _parse_duration(period):
                logger.info("Using cached archive from %s", cache_file)
                try:
                    return cache_file.read_bytes()
                except Exception:
                    logger.warning("Failed to read cache file")

        url = f"{base_url}/{self.repo}/tar.gz/{self.ref}"
        logger.info("Downloading archive for %s @ %s", self.repo, self.ref)

        try:
            headers = {"User-Agent": "gitignore-gen-script"}
            token = os.environ.get("GITHUB_TOKEN")
            no_auth = getattr(self.args, "no_auth", False)
            if not no_auth and token and "github.com" in url:
                headers["Authorization"] = f"token {token}"

            req = urllib.request.Request(url, headers=headers)  # noqa: S310
            with urllib.request.urlopen(req) as response:  # noqa: S310
                data = response.read()
                try:
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    cache_file.write_bytes(data)
                except OSError as e:
                    logger.warning("Cache write failed (proceeding in memory): %s", e)
                return data
        except Exception:
            logger.exception("Failed to download archive from %s", url)
            return None

    async def get_members(self) -> list[TemplateMember]:
        data = await self._get_data()
        if not data:
            return []

        def open_tar() -> tarfile.TarFile:
            return tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")

        # We store the tarfile object in self._tar to keep it open for later reads.
        self._tar = await asyncio.to_thread(open_tar)
        members: list[TemplateMember] = []
        for m in self._tar.getmembers():
            if m.isfile() and m.name.endswith(".gitignore"):
                # GitHub tarballs prefix every path with a root dir
                parts = m.name.split("/")
                canonical_path = "/".join(parts[1:]) if len(parts) > 1 else m.name
                members.append(TarTemplateMember(canonical_path, self._tar, m.name))
        return members

    async def close(self) -> None:
        if self._tar:
            await asyncio.to_thread(self._tar.close)


class LocalArchiveSource(TemplateSource):
    """Source that reads templates from a local .tar.gz archive."""

    def __init__(self, path: Path):
        self.path = path
        self._tar: tarfile.TarFile | None = None

    @property
    def source_label(self) -> str:
        return "local-archive"

    @property
    def ref_label(self) -> str:
        return str(self.path)

    async def get_members(self) -> list[TemplateMember]:
        try:

            def open_tar() -> tarfile.TarFile:
                return tarfile.open(self.path, mode="r:gz")

            self._tar = await asyncio.to_thread(open_tar)
            return [
                TarTemplateMember(m.name, self._tar, m.name)
                for m in self._tar.getmembers()
                if m.isfile() and m.name.endswith(".gitignore")
            ]
        except Exception:
            logger.exception("Failed to open local archive: %s", self.path)
            return []

    async def close(self) -> None:
        if self._tar:
            await asyncio.to_thread(self._tar.close)


class LocalDirSource(TemplateSource):
    """Source that reads templates from a local directory."""

    def __init__(self, path: Path):
        self.path = path

    @property
    def source_label(self) -> str:
        return "local-dir"

    @property
    def ref_label(self) -> str:
        return str(self.path)

    async def get_members(self) -> list[TemplateMember]:
        return await asyncio.to_thread(self._sync_get_members)

    def _sync_get_members(self) -> list[TemplateMember]:
        members: list[TemplateMember] = []
        for p in self.path.rglob("*.gitignore"):
            if p.is_file():
                # Use .as_posix() to ensure canonical '/' delimiters on Windows
                rel_path = p.relative_to(self.path).as_posix()
                members.append(FileTemplateMember(rel_path, p))
        return members


class SelectionRequest:
    """Represents a single template selection request."""

    def __init__(self, type_: str, pattern: str):
        self.type = type_
        self.pattern = pattern

    def matches(self, m: TemplateMember) -> bool:
        """Check if a template member matches this request."""
        name = m.path.rsplit("/", 1)[-1]
        if self.type == "path":
            return m.path.endswith(self.pattern)
        if self.type == "file":
            return name == self.pattern
        if self.type == "file_i":
            return name.lower() == self.pattern.lower()
        if self.type == "filename":
            if self.pattern.endswith(".gitignore"):
                return m.path.endswith(self.pattern)
            return name == f"{self.pattern}.gitignore"
        return bool(self.type == "regex" and re.search(self.pattern, m.path))


class StoreSelectionAction(argparse.Action):
    """Custom argparse action to store selection requests in order."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        _ = parser
        selections = getattr(namespace, "selections", None)
        if selections is None:
            selections = []
            namespace.selections = selections

        # selections is now known to be a list
        selections_list = cast("list[SelectionRequest]", selections)

        mapping = {
            "--include-path": "path",
            "--include-file": "file",
            "--include-file-i": "file_i",
            "--include-filename": "filename",
            "--include-regex": "regex",
            None: "filename",
        }
        type_ = mapping.get(option_string, "filename")
        if isinstance(values, list):
            for val in values:
                if isinstance(val, str):
                    selections_list.append(SelectionRequest(type_, val))
        elif isinstance(values, str):
            selections_list.append(SelectionRequest(type_, values))


def _select_templates(
    members: list[TemplateMember], args: argparse.Namespace
) -> list[TemplateMember]:
    """Select members based on user criteria, preserving order."""
    selections = cast("list[SelectionRequest]", getattr(args, "selections", []))
    selected: list[TemplateMember] = []

    for req in selections:
        matches = [m for m in members if req.matches(m)]
        if not matches and getattr(args, "fail_on_missing", True):
            msg = f"No templates matched selection: {req.type}={req.pattern}"
            raise ValueError(msg)
        selected.extend(matches)

    seen: set[str] = set()
    unique_selected: list[TemplateMember] = []
    for m in selected:
        if m.path not in seen:
            unique_selected.append(m)
            seen.add(m.path)
    return unique_selected


def _add_selection_group(parser: argparse.ArgumentParser) -> None:
    """Add template selection arguments to a parser."""
    selection = parser.add_argument_group(
        "Selection options",
        description="Filter which .gitignore templates to include in the output.",
    )
    selection.add_argument(
        "--include-path",
        action=StoreSelectionAction,
        metavar="PATH",
        help=(
            "Include a file by its exact relative path (e.g. 'Global/macOS.gitignore')."
        ),
    )
    selection.add_argument(
        "--include-file",
        action=StoreSelectionAction,
        metavar="FILENAME",
        help="Include a file by its exact filename (e.g. 'Python.gitignore').",
    )
    selection.add_argument(
        "--include-file-i",
        action=StoreSelectionAction,
        metavar="FILENAME",
        help=(
            "Include a file by its filename, case-insensitive "
            "(e.g. 'python.gitignore')."
        ),
    )
    selection.add_argument(
        "--include-filename",
        action=StoreSelectionAction,
        metavar="NAME",
        help="Include a file by its base name; automatically appends '.gitignore'.",
    )
    selection.add_argument(
        "--include-regex",
        action=StoreSelectionAction,
        metavar="PATTERN",
        help="Include files whose repository path matches the provided regex.",
    )
    selection.add_argument(
        "--fail-on-missing",
        action="store_true",
        default=True,
        help="Exit if any requested template is not found (default).",
    )
    selection.add_argument(
        "--no-fail-on-missing",
        action="store_false",
        dest="fail_on_missing",
        help="Continue even if some requested templates are missing.",
    )


def _create_parser() -> argparse.ArgumentParser:
    """Define the command line interface with subcommands."""
    parser = argparse.ArgumentParser(
        description=(
            "A zero-dependency tool to compose .gitignore files from templates."
        ),
    )

    common = argparse.ArgumentParser(add_help=False)
    source = common.add_argument_group(
        "Repository source",
        description="Configure which repository and reference to fetch templates from.",
    )
    source.add_argument(
        "--repo",
        default=_DEFAULT_REPO,
        help=(
            "The GitHub repository (default: %(default)s). "
            "Automatically uses GITHUB_TOKEN."
        ),
    )
    source.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable automatic use of GITHUB_TOKEN.",
    )
    source.add_argument(
        "--base-url",
        metavar="URL",
        help="Override the base URL (default: https://codeload.github.com).",
    )
    ref_group = source.add_mutually_exclusive_group()
    ref_group.add_argument(
        "--branch",
        default="main",
        help="The git branch (default: %(default)s).",
    )
    ref_group.add_argument("--tag", metavar="TAG", help="The git tag.")
    ref_group.add_argument("--sha", metavar="HASH", help="The git commit SHA.")

    local = common.add_argument_group(
        "Local sources",
        description="Use templates from a local directory or archive.",
    )
    local.add_argument(
        "--local-dir",
        type=Path,
        metavar="PATH",
        help="Path to a local directory.",
    )
    local.add_argument(
        "--local-archive",
        type=Path,
        metavar="PATH",
        help="Path to a local .tar.gz archive.",
    )

    storage = common.add_argument_group("Storage and logging")
    storage.add_argument(
        "--download-location",
        type=Path,
        default=_get_default_cache(),
        metavar="DIR",
        help=(
            "Cache directory for archives (default: %(default)s). "
            "Archives are not automatically deleted."
        ),
    )
    storage.add_argument(
        "--log-level",
        type=int,
        choices=[0, 1, 2],
        default=1,
        help="Log verbosity: 0 (errors), 1 (info), 2 (debug).",
    )
    storage.add_argument(
        "--refresh-period",
        metavar="DURATION",
        default="7d",
        help="How long to keep the local cache (e.g. '7d', '12h').",
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, title="Commands", metavar="{ls,generate}"
    )

    ls_parser = subparsers.add_parser(
        "ls", help="List available templates.", parents=[common]
    )
    ls_parser.add_argument(
        "templates",
        nargs="*",
        action=StoreSelectionAction,
        metavar="TEMPLATE",
        help="Template names to filter by.",
    )
    _add_selection_group(ls_parser)

    gen_parser = subparsers.add_parser(
        "generate", help="Generate a combined .gitignore file.", parents=[common]
    )
    gen_parser.add_argument(
        "templates",
        nargs="*",
        action=StoreSelectionAction,
        metavar="TEMPLATE",
        help="Template names to include.",
    )
    _add_selection_group(gen_parser)

    output = gen_parser.add_argument_group("Output options")
    output.add_argument("--output", metavar="FILE", help="Save output to a file.")
    output.add_argument(
        "--section-order",
        choices=["lexicographic", "args_order"],
        default="args_order",
        help="Sort order: 'args_order' or 'lexicographic'.",
    )
    f_header = output.add_mutually_exclusive_group()
    f_header.add_argument("--include-file-header", action="store_true", default=True)
    f_header.add_argument(
        "--no-include-file-header", action="store_false", dest="include_file_header"
    )
    output.add_argument(
        "--file-header-template",
        metavar="STR",
        default=(
            "\n# Generated by gitignore-gen\n# Source: {repo}@{ref}\n# Date: {date}\n\n"
        ),
    )
    s_header = output.add_mutually_exclusive_group()
    s_header.add_argument("--include-section-header", action="store_true", default=True)
    s_header.add_argument(
        "--no-include-section-header",
        action="store_false",
        dest="include_section_header",
    )
    output.add_argument(
        "--section-header-template",
        metavar="STR",
        default="### BEGIN {path} ###\n{content}\n### END {path} ###\n\n",
    )

    return parser


async def _do_list(source: TemplateSource, args: argparse.Namespace) -> None:
    """Handle the 'ls' subcommand."""
    members = await source.get_members()
    if hasattr(args, "selections") and args.selections:
        members = _select_templates(members, args)
    for m in sorted(members, key=lambda x: x.path):
        sys.stdout.write(m.path + "\n")


async def _do_generate(source: TemplateSource, args: argparse.Namespace) -> None:
    """Handle the 'generate' subcommand."""
    members = await source.get_members()
    selected = _select_templates(members, args)
    if getattr(args, "section_order", "args_order") == "lexicographic":
        selected.sort(key=lambda x: x.path)

    if not selected:
        logger.warning("No templates matched the provided criteria.")
        return

    template = cast("str", args.file_header_template)
    file_header = (
        template.format(
            repo=source.source_label,
            ref=source.ref_label,
            date=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        )
        if getattr(args, "include_file_header", True)
        else ""
    )

    sections: list[str] = []
    for m in selected:
        content = await m.read()
        if content:
            if getattr(args, "include_section_header", True):
                sec_tmpl = cast("str", args.section_header_template)
                sections.append(sec_tmpl.format(path=m.path, content=content))
            else:
                sections.append(f"{content}\n\n")

    final_output = file_header + "".join(sections)
    if getattr(args, "output", None):
        output_path = Path(cast("str", args.output))

        def write_file() -> None:
            output_path.write_text(final_output, encoding="utf-8")

        await asyncio.to_thread(write_file)
        logger.info("Successfully wrote output to %s", args.output)
    else:
        sys.stdout.write(final_output)


async def async_main(argv: list[str] | None = None) -> None:
    """Main entry point for the async execution."""
    parser = _create_parser()
    args = parser.parse_args(argv)
    _setup_logging(cast("int", getattr(args, "log_level", 1)))

    try:
        source: TemplateSource
        local_dir = cast("Path | None", getattr(args, "local_dir", None))
        local_archive = cast("Path | None", getattr(args, "local_archive", None))

        if local_dir:
            source = LocalDirSource(local_dir)
        elif local_archive:
            source = LocalArchiveSource(local_archive)
        else:
            ref = cast(
                "str",
                getattr(args, "sha", None)
                or getattr(args, "tag", None)
                or getattr(args, "branch", "main"),
            )
            repo = cast("str", getattr(args, "repo", _DEFAULT_REPO))
            source = GitHubArchiveSource(repo, ref, args)

        async def run() -> None:
            try:
                if args.command == "ls":
                    await _do_list(source, args)
                elif args.command == "generate":
                    await _do_generate(source, args)
            finally:
                await source.close()

        await asyncio.wait_for(run(), timeout=300)

    except Exception:
        logger.exception("Runtime error")
        sys.exit(1)


def main() -> None:
    """Synchronous wrapper for the async main entry point."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
