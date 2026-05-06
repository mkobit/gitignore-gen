import datetime
import io
import os
import tarfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vcs_gen.cli import async_main


@pytest.mark.asyncio
async def test_github_archive_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """Test downloading and caching from GitHub."""
    cache_dir = tmp_path / "cache"

    # Create a dummy archive in memory
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w:gz") as tar:
        content = b"__pycache__/"
        info = tarfile.TarInfo(name="repo-main/Python.gitignore")
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))
    archive_data = out.getvalue()

    mock_response = MagicMock()
    mock_response.read.return_value = archive_data
    mock_response.__enter__.return_value = mock_response

    # Test with GITHUB_TOKEN
    with (
        patch("urllib.request.urlopen", return_value=mock_response) as mock_url,
        patch.dict(os.environ, {"GITHUB_TOKEN": "secret"}),
    ):
        await async_main(
            [
                "gitignore",
                "generate",
                "--repo",
                "user/repo",
                "--download-location",
                str(cache_dir),
                "Python",
                "--no-include-file-header",
                "--no-include-section-header",
            ]
        )
        call_args = mock_url.call_args[0][0]
        assert call_args.get_header("Authorization") == "token secret"

    captured = capsys.readouterr()
    assert "__pycache__/" in captured.out


@pytest.mark.asyncio
async def test_github_archive_download_failure(tmp_path: Path):
    """Test handling of download failure."""
    cache_dir = tmp_path / "cache"
    with patch("urllib.request.urlopen", side_effect=Exception("Net Error")):
        with pytest.raises(SystemExit) as exc:
            await async_main(
                [
                    "gitignore",
                    "ls",
                    "--repo",
                    "user/repo",
                    "--download-location",
                    str(cache_dir),
                    "Python",
                ]
            )
        assert exc.value.code == 1


@pytest.mark.asyncio
async def test_tar_read_failure(tmp_path: Path):
    """Test handling of tar read failure."""
    archive_path = tmp_path / "bad.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.addfile(tarfile.TarInfo(name="Python.gitignore"), io.BytesIO(b"content"))

    with patch("tarfile.TarFile.extractfile", side_effect=Exception("Read Error")):
        await async_main(
            ["gitignore", "generate", "--local-archive", str(archive_path), "Python"]
        )


@pytest.mark.asyncio
async def test_local_file_read_failure(tmp_path: Path):
    """Test handling of local file read failure."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    p = templates_dir / "Python.gitignore"
    p.write_text("content", encoding="utf-8")

    with patch("pathlib.Path.read_text", side_effect=Exception("IO Error")):
        await async_main(
            ["gitignore", "generate", "--local-dir", str(templates_dir), "Python"]
        )


@pytest.mark.asyncio
async def test_cache_write_failure(tmp_path: Path):
    """Test handling of cache write failure (OSError)."""
    cache_dir = tmp_path / "cache"

    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w:gz") as tar:
        tar.addfile(
            tarfile.TarInfo(name="repo-main/Python.gitignore"), io.BytesIO(b"p")
        )
    archive_data = out.getvalue()

    mock_response = MagicMock()
    mock_response.read.return_value = archive_data
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("pathlib.Path.write_bytes", side_effect=OSError("Disk Full")),
    ):
        await async_main(
            [
                "gitignore",
                "ls",
                "--repo",
                "user/repo",
                "--download-location",
                str(cache_dir),
                "Python",
            ]
        )


@pytest.mark.asyncio
async def test_cache_period_logic(tmp_path: Path):
    """Test the refresh period logic in GitHubArchiveSource."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cache_file = cache_dir / "user_repo_main.tar.gz"

    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w:gz") as tar:
        tar.addfile(
            tarfile.TarInfo(name="repo-main/Python.gitignore"), io.BytesIO(b"cached")
        )
    cache_file.write_bytes(out.getvalue())

    # Fresh cache
    with patch("urllib.request.urlopen") as mock_url:
        await async_main(
            [
                "gitignore",
                "generate",
                "--repo",
                "user/repo",
                "--download-location",
                str(cache_dir),
                "--refresh-period",
                "7d",
                "Python",
                "--no-include-file-header",
                "--no-include-section-header",
            ]
        )
        mock_url.assert_not_called()

    # Expired cache
    old_time = (
        datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=10)
    ).timestamp()
    os.utime(cache_file, (old_time, old_time))

    out_new = io.BytesIO()
    with tarfile.open(fileobj=out_new, mode="w:gz") as tar:
        tar.addfile(
            tarfile.TarInfo(name="repo-main/Python.gitignore"), io.BytesIO(b"new")
        )

    mock_response = MagicMock()
    mock_response.read.return_value = out_new.getvalue()
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_url:
        await async_main(
            [
                "gitignore",
                "generate",
                "--repo",
                "user/repo",
                "--download-location",
                str(cache_dir),
                "--refresh-period",
                "1d",
                "Python",
                "--no-include-file-header",
                "--no-include-section-header",
            ]
        )
        mock_url.assert_called()


@pytest.mark.asyncio
async def test_cache_read_failure(tmp_path: Path):
    """Test handling of cache read failure."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cache_file = cache_dir / "user_repo_main.tar.gz"
    cache_file.write_bytes(b"some data")

    # Create a valid gzip for the download fallback
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w:gz") as tar:
        tar.addfile(
            tarfile.TarInfo(name="repo-main/Python.gitignore"), io.BytesIO(b"content")
        )
    archive_data = out.getvalue()

    with patch("pathlib.Path.read_bytes", side_effect=Exception("Read Error")):
        mock_response = MagicMock()
        mock_response.read.return_value = archive_data
        mock_response.__enter__.return_value = mock_response
        with patch("urllib.request.urlopen", return_value=mock_response):
            await async_main(
                [
                    "gitignore",
                    "ls",
                    "--repo",
                    "user/repo",
                    "--download-location",
                    str(cache_dir),
                    "Python",
                ]
            )
