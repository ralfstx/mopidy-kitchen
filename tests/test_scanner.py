import logging

from mopidy_kitchen.index_files import AlbumIndex
from mopidy_kitchen.scanner import scan_dir, read_album

from .helpers import make_album


def test_scan_dir_empty(tmp_path, caplog):
    result = scan_dir(tmp_path)

    assert caplog.text == ""
    assert result == []


def test_scan_dir_valid(tmp_path, caplog):
    make_album(tmp_path / "a", '{"name": "Foo"}')
    result = scan_dir(tmp_path)

    assert caplog.text == ""
    assert len(result) == 1
    assert type(result[0]) == AlbumIndex
    assert result[0].name == "Foo"
    assert result[0].path == tmp_path / "a"


def test_scan_dir_invalid(tmp_path, caplog):
    make_album(tmp_path / "a", '{"name": "Foo"}')
    make_album(tmp_path / "b", '{"name": 23}')
    make_album(tmp_path / "c", '{"name": "Bar"}')

    result = scan_dir(tmp_path)

    assert [a.name for a in result] == ["Bar", "Foo"]
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert (
        caplog.records[0].getMessage()
        == f"Invalid index format in '{tmp_path / 'b/index.json'}': Attribute 'name' in album is not a string"
    )


def test_read_album_valid(tmp_path, caplog):
    make_album(tmp_path, '{"name": "Foo"}')

    result = read_album(tmp_path)

    assert caplog.text == ""
    type(result) == AlbumIndex
    assert result.name == "Foo"
    assert result.path == tmp_path


def test_read_album_invalid(tmp_path, caplog):
    make_album(tmp_path, '{"name": 23}')

    result = read_album(tmp_path)

    assert result is None
    assert (
        caplog.records[0].getMessage()
        == f"Invalid index format in '{tmp_path / 'index.json'}': Attribute 'name' in album is not a string"
    )
