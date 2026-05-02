from pathlib import Path

import pytest

from gitignore_gen.cli import async_main


@pytest.mark.asyncio
async def test_cli_ls(templates_dir: Path):
    """Test the 'ls' subcommand using a local directory."""
    # We pass --local-dir to avoid network requests
    await async_main(["ls", "--local-dir", str(templates_dir), "Python"])
    # If it doesn't crash and completes, the basic wiring is working


@pytest.mark.asyncio
async def test_cli_generate_to_stdout(
    templates_dir: Path, capsys: pytest.CaptureFixture[str]
):
    """Test generating a gitignore to stdout."""
    await async_main(
        [
            "generate",
            "--local-dir",
            str(templates_dir),
            "Python",
            "--no-include-file-header",
        ]
    )
    captured = capsys.readouterr()
    assert "### BEGIN Python.gitignore ###" in captured.out
    assert "__pycache__/" in captured.out


@pytest.mark.asyncio
async def test_cli_generate_to_file(templates_dir: Path, tmp_path: Path):
    """Test generating a gitignore to a file."""
    output_file = tmp_path / ".gitignore"
    await async_main(
        [
            "generate",
            "--local-dir",
            str(templates_dir),
            "Python",
            "macOS",
            "--output",
            str(output_file),
        ]
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert "### BEGIN Python.gitignore ###" in content
    assert "### BEGIN Global/macOS.gitignore ###" in content
