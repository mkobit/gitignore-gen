import datetime
import os

import pytest

from gitignore_gen.cli import _get_default_cache, _parse_duration


def test_get_default_cache(tmp_path):
    """Test XDG_CACHE_HOME usage."""
    original_xdg = os.environ.get("XDG_CACHE_HOME")
    try:
        os.environ["XDG_CACHE_HOME"] = str(tmp_path)
        cache = _get_default_cache()
        assert cache == tmp_path / "gitignore-gen"
    finally:
        if original_xdg:
            os.environ["XDG_CACHE_HOME"] = original_xdg
        else:
            del os.environ["XDG_CACHE_HOME"]


def test_parse_duration():
    """Test duration parsing."""
    assert _parse_duration("7d") == datetime.timedelta(days=7)
    assert _parse_duration("12h") == datetime.timedelta(hours=12)
    assert _parse_duration("30m") == datetime.timedelta(minutes=30)
    assert _parse_duration("5") == datetime.timedelta(days=5)

    with pytest.raises(ValueError, match="Invalid duration format"):
        _parse_duration("invalid")

    with pytest.raises(ValueError, match="Invalid duration format"):
        _parse_duration("7x")
