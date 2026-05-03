import io
import tarfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gitignore_gen.cli import async_main


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
        # GitHub tarballs have a root directory
        info = tarfile.TarInfo(name="repo-main/Python.gitignore")
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))
    archive_data = out.getvalue()

    # MagicMock handles context managers automatically
    mock_response = MagicMock()
    mock_response.read.return_value = archive_data
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        await async_main(
            [
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

    captured = capsys.readouterr()
    assert "__pycache__/" in captured.out

    # Verify cache
    cache_files = list(cache_dir.glob("*.tar.gz"))
    assert len(cache_files) == 1
    assert "user_repo_main.tar.gz" in cache_files[0].name

    # Test cache hit
    with patch("urllib.request.urlopen") as mock_url:
        await async_main(
            [
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
        mock_url.assert_not_called()
