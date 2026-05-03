from unittest.mock import Mock

import pytest

from gitignore_gen.cli import SelectionRequest, TemplateMember


@pytest.mark.asyncio
async def test_selection_request_filename():
    req = SelectionRequest("filename", "Python")
    member = Mock(spec=TemplateMember)
    member.path = "Python.gitignore"
    assert req.matches(member)

    member.path = "Global/macOS.gitignore"
    assert not req.matches(member)


@pytest.mark.asyncio
async def test_selection_request_path():
    req = SelectionRequest("path", "Global/macOS.gitignore")
    member = Mock(spec=TemplateMember)
    member.path = "Global/macOS.gitignore"
    assert req.matches(member)
