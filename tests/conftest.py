import shutil
import tarfile
import urllib.request
from pathlib import Path

import pytest

TEMPLATE_SHA = "1046d8fba6b42d367da6314c934cddb6bfe5662e"
TEMPLATE_URL = f"https://codeload.github.com/github/gitignore/tar.gz/{TEMPLATE_SHA}"


@pytest.fixture(scope="session")
def templates_dir() -> Path:
    """Fixture to provide a local directory of gitignore templates."""
    # Move from tests/fixtures/gitignore to .test_fixtures/gitignore at the root
    fixture_dir = Path(__file__).parent.parent / ".test_fixtures" / "gitignore"

    if not fixture_dir.exists():
        fixture_dir.mkdir(parents=True, exist_ok=True)
        tar_path = fixture_dir.parent / "templates.tar.gz"

        # Download the tarball
        with (
            urllib.request.urlopen(TEMPLATE_URL) as response,  # noqa: S310
            tar_path.open("wb") as f,
        ):
            f.write(response.read())

        # Extract it
        with tarfile.open(tar_path, mode="r:gz") as tar:
            tar.extractall(path=fixture_dir.parent)  # noqa: S202

        # The extraction creates a directory like 'gitignore-SHA'
        # We move its contents to our target directory
        extracted_dir = fixture_dir.parent / f"gitignore-{TEMPLATE_SHA}"
        for item in extracted_dir.iterdir():
            shutil.move(str(item), str(fixture_dir / item.name))

        extracted_dir.rmdir()
        tar_path.unlink()

    return fixture_dir
