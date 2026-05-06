from unittest.mock import Mock

import pytest

from vcs_gen.cli import SelectionRequest, TemplateMember


@pytest.mark.asyncio
async def test_selection_request_filename():
    """Test exact filename matching."""
    req = SelectionRequest("filename", "Python")
    member = Mock(spec=TemplateMember)
    member.path = "Python.gitignore"
    assert req.matches(member)

    # Test without suffix in query but exists in path
    req = SelectionRequest("filename", "Python")
    assert req.matches(member)

    # Test with suffix in query
    req = SelectionRequest("filename", "Python.gitignore")
    assert req.matches(member)

    member.path = "Global/macOS.gitignore"
    assert not req.matches(member)


@pytest.mark.asyncio
async def test_selection_request_nested_path():
    """Test matching with nested paths in positional arguments."""
    req = SelectionRequest("templates", "Global/macOS")
    member = Mock(spec=TemplateMember)
    member.path = "Global/macOS.gitignore"
    assert req.matches(member)

    member.path = "Python.gitignore"
    assert not req.matches(member)


@pytest.mark.asyncio
async def test_selection_request_path():
    """Test path suffix matching."""
    req = SelectionRequest("path", "Global/macOS.gitignore")
    member = Mock(spec=TemplateMember)
    member.path = "Global/macOS.gitignore"
    assert req.matches(member)

    member.path = "SomeOther/Global/macOS.gitignore"
    assert req.matches(member)

    member.path = "Python.gitignore"
    assert not req.matches(member)


@pytest.mark.asyncio
async def test_selection_request_case_insensitive():
    """Test case-insensitive matching."""
    req = SelectionRequest("include_file_i", "python")
    member = Mock(spec=TemplateMember)
    member.path = "Python.gitignore"
    assert req.matches(member)

    member.path = "PYTHON.gitignore"
    assert req.matches(member)

    # Test with suffix
    req = SelectionRequest("include_file_i", "PYTHON.GITIGNORE")
    assert req.matches(member)


@pytest.mark.asyncio
async def test_selection_request_regex():
    """Test regex matching."""
    req = SelectionRequest("include_regex", ".*Py.*")
    member = Mock(spec=TemplateMember)
    member.path = "Python.gitignore"
    assert req.matches(member)

    member.path = "Global/PyCharm.gitignore"
    assert req.matches(member)

    member.path = "macOS.gitignore"
    assert not req.matches(member)


@pytest.mark.asyncio
async def test_selection_request_file_type():
    """Test 'file' type matching."""
    req = SelectionRequest("include_file", "Python")
    member = Mock(spec=TemplateMember)
    member.path = "Python.gitignore"
    assert req.matches(member)


@pytest.mark.asyncio
async def test_selection_request_standardization():
    """Test that 'include_' prefix is correctly stripped."""
    req = SelectionRequest("include_file", "Python.gitignore")
    assert req.type == "file"
