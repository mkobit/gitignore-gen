import io
import tarfile
from pathlib import Path

import pytest

from vcs_gen.cli import async_main


@pytest.mark.asyncio
async def test_local_archive_source(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Test using a local .tar.gz archive as a source."""
    archive_path = tmp_path / "templates.tar.gz"

    # Create a dummy archive
    with tarfile.open(archive_path, "w:gz") as tar:
        content = b"node_modules/"
        info = tarfile.TarInfo(name="Node.gitignore")
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))

        content2 = b"__pycache__/"
        info2 = tarfile.TarInfo(name="Python.gitignore")
        info2.size = len(content2)
        tar.addfile(info2, io.BytesIO(content2))

    await async_main(
        [
            "gitignore",
            "generate",
            "--local-archive",
            str(archive_path),
            "Python",
            "--no-include-file-header",
            "--no-include-section-header",
        ]
    )
    captured = capsys.readouterr()
    assert "__pycache__/" in captured.out
    assert "node_modules/" not in captured.out


@pytest.mark.asyncio
async def test_local_archive_source_failure(tmp_path: Path):
    """Test local archive source with a non-existent file."""
    with pytest.raises(SystemExit) as exc:
        await async_main(
            [
                "gitignore",
                "ls",
                "--local-archive",
                str(tmp_path / "missing.tar.gz"),
                "Python",
            ]
        )
    assert exc.value.code == 1
