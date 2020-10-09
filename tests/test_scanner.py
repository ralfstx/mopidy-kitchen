import logging

from mopidy_kitchen.album_index import AlbumIndex
from mopidy_kitchen.scanner import Scanner

from .helpers import make_album


def test_scan_empty(tmp_path, caplog):
    scanner = Scanner(root_dir=tmp_path)

    result = scanner.scan()

    assert caplog.text == ""
    assert result == []


def test_scan_valid(tmp_path, caplog):
    make_album(tmp_path / "a", '{"name": "Foo"}')
    scanner = Scanner(root_dir=tmp_path)

    result = scanner.scan()

    assert caplog.text == ""
    assert len(result) == 1
    assert type(result[0]) == AlbumIndex
    assert result[0].name == "Foo"
    assert result[0].path == tmp_path / "a"


def test_scan_invalid(tmp_path, caplog):
    make_album(tmp_path / "a", '{"name": "Foo"}')
    make_album(tmp_path / "b", '{"name": 23}')
    make_album(tmp_path / "c", '{"name": "Bar"}')
    scanner = Scanner(root_dir=tmp_path)

    result = scanner.scan()

    assert [a.name for a in result] == ["Bar", "Foo"]
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert (
        caplog.records[0].getMessage()
        == f"Invalid index format in '{tmp_path / 'b/index.json'}': Attribute 'name' in album is not a string"
    )
