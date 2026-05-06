from pathlib import Path

import pytest

from vcs_gen.cli import async_main


@pytest.mark.remote
@pytest.mark.asyncio
async def test_cli_remote_e2e(tmp_path: Path):
    """Verify full download -> cache -> generate pipeline with real network access."""
    cache_dir = tmp_path / "cache"
    output_file = tmp_path / ".gitignore"

    # We use a specific, small SHA to keep the test fast and deterministic
    sha = "1046d8fba6b42d367da6314c934cddb6bfe5662e"

    await async_main(
        [
            "generate",
            "--repo",
            "github/gitignore",
            "--sha",
            sha,
            "--download-location",
            str(cache_dir),
            "Python",
            "--output",
            str(output_file),
        ]
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert "### BEGIN Python.gitignore" in content
    assert "__pycache__/" in content

    # Verify the cache file was actually created
    cache_files = list(cache_dir.glob("*.tar.gz"))
    assert len(cache_files) == 1
    assert "github_gitignore" in cache_files[0].name
