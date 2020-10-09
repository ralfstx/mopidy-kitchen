from pytest import raises

from mopidy_kitchen.album_index import AlbumIndex, AlbumIndexError
from .helpers import make_album


def test_read_file_not_found(tmp_path):
    with raises(FileNotFoundError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert "No such file or directory" in str(ex_info.value)
    assert str(tmp_path / "index.json") in str(ex_info.value)


def test_read_invalid_json(tmp_path):
    make_album(tmp_path, "not json")

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert str(ex_info.value) == f"Could not parse JSON in '{tmp_path}/index.json': Expecting value at 1:1"


def test_read_invalid_json_type(tmp_path):
    make_album(tmp_path, "[]")

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert str(ex_info.value) == f"Invalid index format in '{tmp_path}/index.json': Album is not an object"


def test_read_missing_album_name(tmp_path):
    make_album(tmp_path, "{}")

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert (
        str(ex_info.value) == f"Invalid index format in '{tmp_path}/index.json': Attribute 'name' is missing in album"
    )


def test_read_invalid_album_name(tmp_path):
    make_album(tmp_path, {"name": 23})

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert (
        str(ex_info.value)
        == f"Invalid index format in '{tmp_path}/index.json': Attribute 'name' in album is not a string"
    )


def test_read_album_path(tmp_path):
    index = {"name": "foo"}
    make_album(tmp_path, index)

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert result.path == tmp_path


def test_read_album_defaults(tmp_path):
    make_album(tmp_path, '{"name": "foo"}')

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert result.title == ""
    assert result.artists == []
    assert result.musicbrainz_id == ""


def test_read_album_without_tracks(tmp_path):
    index = {"name": "John Doe - One Day"}
    make_album(tmp_path, index)

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert len(result.tracks) == 0


def test_read_with_tracks(tmp_path):
    index = {"name": "John Doe - One Day", "tracks": [{"path": "01.ogg"}, {"path": "02.ogg"}]}
    make_album(tmp_path, index)

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert len(result.tracks) == 2
    assert result.tracks[0].disc_no == 1
    assert result.tracks[0].track_no == 1
    assert result.tracks[0].path == tmp_path / "01.ogg"
    assert result.tracks[1].disc_no == 1
    assert result.tracks[1].track_no == 2
    assert result.tracks[1].path == tmp_path / "02.ogg"


def test_read_with_single_disc_without_path(tmp_path):
    index = {"name": "John Doe - One Day", "discs": [{"tracks": [{"path": "01.ogg"}, {"path": "02.ogg"}]}]}
    make_album(tmp_path, index)

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert len(result.tracks) == 2
    assert result.tracks[0].disc_no == 1
    assert result.tracks[0].track_no == 1
    assert result.tracks[0].path == tmp_path / "01.ogg"
    assert result.tracks[1].disc_no == 1
    assert result.tracks[1].track_no == 2
    assert result.tracks[1].path == tmp_path / "02.ogg"


def test_read_with_multiple_discs_with_path(tmp_path):
    index = {
        "name": "John Doe - One Day",
        "discs": [
            {"path": "01", "tracks": [{"path": "01.ogg"}]},
            {"path": "02", "tracks": [{"path": "01.ogg"}, {"path": "02.ogg"}]},
        ],
    }
    make_album(tmp_path, index)

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert len(result.tracks) == 3
    assert result.tracks[0].disc_no == 1
    assert result.tracks[0].track_no == 1
    assert result.tracks[0].path == tmp_path / "01/01.ogg"
    assert result.tracks[1].disc_no == 2
    assert result.tracks[1].track_no == 1
    assert result.tracks[1].path == tmp_path / "02/01.ogg"
    assert result.tracks[2].disc_no == 2
    assert result.tracks[2].track_no == 2
    assert result.tracks[2].path == tmp_path / "02/02.ogg"


def test_read_track_defaults(tmp_path):
    make_album(tmp_path, '{"name": "foo", "tracks": [{"path": "01.ogg"}]}')

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert result.tracks[0].title == ""
    assert result.tracks[0].artists == []
    assert result.tracks[0].musicbrainz_id == ""


def test_read_invalid_tracks_type(tmp_path):
    make_album(tmp_path, '{"name": "foo", "tracks": 12}')

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert (
        str(ex_info.value)
        == f"Invalid index format in '{tmp_path}/index.json': Attribute 'tracks' in album is not an array"
    )


def test_read_missing_track_path(tmp_path):
    make_album(tmp_path, '{"name": "foo", "tracks": [{"length": 101}]}')

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert (
        str(ex_info.value)
        == f"Invalid index format in '{tmp_path}/index.json': Attribute 'path' is missing in track 1 of disc 1"
    )


def test_read_invalid_track_length_type(tmp_path):
    make_album(
        tmp_path,
        {"name": "foo", "tracks": [{"path": "01.ogg", "length": "23"}]},
    )

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert (
        str(ex_info.value)
        == f"Invalid index format in '{tmp_path}/index.json': Attribute 'length' in track 1 of disc 1 is not a number"
    )


def test_read_negative_track_length(tmp_path):
    make_album(
        tmp_path,
        {"name": "foo", "tracks": [{"path": "01.ogg", "length": -23}]},
    )

    with raises(AlbumIndexError) as ex_info:
        AlbumIndex.read_from_file(tmp_path / "index.json")

    assert (
        str(ex_info.value)
        == f"Invalid index format in '{tmp_path}/index.json': Attribute 'length' in track 1 of disc 1 is negative"
    )


def test_read_with_complete_metadata(tmp_path):
    index = {
        "name": "John Doe - One Day",
        "artist": "John Doe",
        "title": "One Day",
        "musicbrainz_id": "000-0",
        "discs": [
            {
                "path": "01",
                "tracks": [
                    {
                        "path": "01.ogg",
                        "title": "Another Dreadful Morning",
                        "artist": "John Doe",
                        "musicbrainz_id": "000-1",
                        "length": 101,
                    }
                ],
            }
        ],
    }
    make_album(tmp_path, index)

    result = AlbumIndex.read_from_file(tmp_path / "index.json")

    assert result.title == "One Day"
    assert result.artists == ["John Doe"]
    assert result.musicbrainz_id == "000-0"
    assert result.tracks[0].title == "Another Dreadful Morning"
    assert result.tracks[0].artists == ["John Doe"]
    assert result.tracks[0].musicbrainz_id == "000-1"
    assert result.tracks[0].duration_ms == 101000
