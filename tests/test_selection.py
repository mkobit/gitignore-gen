from unittest.mock import Mock

from gitignore_gen.cli import SelectionRequest, TemplateMember


def test_selection_request_filename():
    req = SelectionRequest("filename", "Python")
    member = Mock(spec=TemplateMember)
    member.path = "Python.gitignore"
    assert req.matches(member)

    member.path = "Global/macOS.gitignore"
    assert not req.matches(member)


def test_selection_request_path():
    req = SelectionRequest("path", "Global/macOS.gitignore")
    member = Mock(spec=TemplateMember)
    member.path = "Global/macOS.gitignore"
    assert req.matches(member)
