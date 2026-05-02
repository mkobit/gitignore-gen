# Objective
Address the codebase investigator's findings: fix the path-stripping bug, decouple `TemplateMember` logic, resolve Windows path issues, fix metadata for local sources, add positional template support to `ls`, and document/toggle `GITHUB_TOKEN` usage.

# Key Files & Context
- `gitignore_gen.py`

# Implementation Steps
1.  **Refine CLI**:
    - Add `--no-auth` flag to the "Repository source" group. Document that `GITHUB_TOKEN` is used automatically otherwise.
    - Make `--local-dir` and `--local-archive` mutually exclusive with remote options (or at least document precedence clearly). Let's put them in a mutually exclusive group with `--repo` in the parser if possible, or just document precedence in help text.
    - Add the `templates` positional argument to the `ls` subcommand to match `generate`.
2.  **Source Abstraction Hierarchy**:
    - Define a `TemplateSource` interface (Protocol or ABC) with methods `get_members() -> list[TemplateMember]`, and properties `source_label` and `ref_label` (for the header).
    - Refactor `TemplateMember` to be an abstract base class with a `path` property (the canonical posix path used for matching/display) and an abstract `read() -> str | None` method.
3.  **Concrete Implementations**:
    - **`GitHubArchiveSource`**: Handles the `urllib` download and cache. When returning members, it strips the first directory component (e.g., `gitignore-main/`) from the `tarinfo.name` to create the canonical `path`. Checks `os.environ.get("GITHUB_TOKEN")` unless `--no-auth` is set.
    - **`LocalArchiveSource`**: Opens a local `.tar.gz`. Does not strip any path components; uses `tarinfo.name` directly as the `path`.
    - **`LocalDirSource`**: Uses `Path.rglob("*.gitignore")`. The canonical `path` is calculated via `p.relative_to(base_dir).as_posix()`, fixing the Windows backslash issue.
4.  **Metadata Fix**:
    - Update `_do_generate` to use `source.source_label` and `source.ref_label` in the `args.file_header_template.format(...)` call instead of hardcoded `args.repo` and `ref`.
5.  **Documentation Updates**:
    - Add the requested `# TODO (Out of scope):` list at the very top of the script.
    - Add comments explaining the `GITHUB_TOKEN` injection.
6.  **Verification**:
    - Run the strict `ruff` and `ty` verification commands.
    - Test local directory parsing to ensure `as_posix()` works and the path isn't broken.