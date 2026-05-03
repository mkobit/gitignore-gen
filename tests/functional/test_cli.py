from pathlib import Path

import pytest

from gitignore_gen.cli import async_main


@pytest.mark.asyncio
async def test_cli_ls(templates_dir: Path):
    """Test the 'ls' subcommand using a local directory."""
    await async_main(["ls", "--local-dir", str(templates_dir), "Python"])


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
    assert "### BEGIN Python.gitignore" in captured.out
    assert "Source: local-dir" in captured.out
    assert "### END Python.gitignore ###" in captured.out


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
    assert "### BEGIN Python.gitignore" in content
    assert "### BEGIN Global/macOS.gitignore" in content


@pytest.mark.asyncio
async def test_cli_include_text(
    templates_dir: Path, capsys: pytest.CaptureFixture[str]
):
    """Test including literal text."""
    await async_main(
        [
            "generate",
            "--local-dir",
            str(templates_dir),
            "--include-text",
            "# Custom Header",
            "Python",
            "--no-include-file-header",
            "--no-include-section-header",
        ]
    )
    captured = capsys.readouterr()
    assert "# Custom Header" in captured.out
    assert "marimo" in captured.out  # Part of Python.gitignore in fixtures


@pytest.mark.asyncio
async def test_cli_include_local_file(
    templates_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """Test including a local file."""
    custom_file = tmp_path / "custom.gitignore"
    custom_file.write_text("*.log", encoding="utf-8")

    await async_main(
        [
            "generate",
            "--local-dir",
            str(templates_dir),
            "--include-local-file",
            str(custom_file),
            "--no-include-file-header",
            "--no-include-section-header",
        ]
    )
    captured = capsys.readouterr()
    assert "*.log" in captured.out


@pytest.mark.asyncio
async def test_cli_fail_on_missing(templates_dir: Path):
    """Test failure when a template is missing."""
    with pytest.raises(SystemExit):
        await async_main(
            [
                "generate",
                "--local-dir",
                str(templates_dir),
                "NonExistentTemplate",
            ]
        )


@pytest.mark.asyncio
async def test_cli_no_fail_on_missing(
    templates_dir: Path, capsys: pytest.CaptureFixture[str]
):
    """Test --no-fail-on-missing."""
    await async_main(
        [
            "generate",
            "--local-dir",
            str(templates_dir),
            "--no-fail-on-missing",
            "NonExistentTemplate",
            "Python",
            "--no-include-file-header",
        ]
    )
    captured = capsys.readouterr()
    assert "Python.gitignore" in captured.out
