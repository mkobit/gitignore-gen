import datetime
import os
from unittest.mock import patch

import pytest

from vcs_gen.cli import (
    Color,
    _get_default_cache,
    _parse_duration,
    async_main,
    main,
)

EXIT_CODE_KBD_INT = 130


def test_color_logic():
    """Test Color class."""
    with (
        patch("sys.stdout.isatty", return_value=True),
        patch.dict(os.environ, {}, clear=True),
    ):
        assert Color.enabled()
        assert "\033" in Color.wrap("test", Color.CYAN)

    with patch("sys.stdout.isatty", return_value=False):
        assert not Color.enabled()
        assert Color.wrap("test", Color.CYAN) == "test"

    with (
        patch("sys.stdout.isatty", return_value=True),
        patch.dict(os.environ, {"NO_COLOR": "1"}),
    ):
        assert not Color.enabled()


def test_get_default_cache_xdg(tmp_path):
    """Test XDG_CACHE_HOME usage."""
    with patch.dict(os.environ, {"XDG_CACHE_HOME": str(tmp_path)}):
        cache = _get_default_cache()
        assert cache == tmp_path / "vcs-gen"


def test_get_default_cache_fallback():
    """Test fallback cache location."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("pathlib.Path.home", side_effect=RuntimeError("No home")),
        patch.dict(os.environ, {"TMPDIR": "/custom/tmp"}),
    ):
        # Should fallback to TMPDIR or /tmp
        cache = _get_default_cache()
        assert "/custom/tmp" in cache.as_posix()


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


@pytest.mark.asyncio
async def test_async_main_runtime_error():
    """Test runtime error handling in async_main."""
    with patch("vcs_gen.cli._run_pipeline", side_effect=RuntimeError("Oops")):
        with pytest.raises(SystemExit) as exc:
            await async_main(["gitignore", "ls"])
        assert exc.value.code == 1


def test_main_keyboard_interrupt():
    """Test KeyboardInterrupt handling in main."""
    with patch("asyncio.run", side_effect=KeyboardInterrupt):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == EXIT_CODE_KBD_INT


@pytest.mark.asyncio
async def test_generate_no_templates(capsys):
    """Test generate command with no matches."""
    # Running without arguments triggers help/warning
    await async_main(["gitignore", "generate"])
    captured = capsys.readouterr()
    assert "Generate .gitignore" in captured.out
