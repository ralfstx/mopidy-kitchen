import pytest

from mopidy_kitchen.uri import (
    ROOT_URI,
    AlbumsUri,
    AlbumTrackUri,
    AlbumUri,
    SearchUri,
    StationStreamUri,
    StationUri,
    StationsUri,
    parse_uri,
)


def test_parse_uri_none():
    result = parse_uri("foo")

    assert result is None


def test_parse_uri_root():
    result = parse_uri("kitchen:root")

    assert result == ROOT_URI
    assert str(result) == "kitchen:root"


def test_parse_uri_albums():
    result = parse_uri("kitchen:albums")

    assert type(result) == AlbumsUri
    assert str(result) == "kitchen:albums"


def test_parse_uri_stations():
    result = parse_uri("kitchen:stations")

    assert type(result) == StationsUri
    assert str(result) == "kitchen:stations"


def test_parse_uri_album():
    result = parse_uri("kitchen:album:123456789012345678901234567890ab")

    assert type(result) == AlbumUri
    assert str(result) == "kitchen:album:123456789012345678901234567890ab"
    assert result.album_id == "123456789012345678901234567890ab"


def test_parse_uri_album_invalid():
    with pytest.raises(ValueError) as err_inf:
        parse_uri("kitchen:album:INVALID")

    assert str(err_inf.value) == "Invalid kitchen URI 'kitchen:album:INVALID': Invalid ID 'INVALID'"


def test_parse_uri_album_track():
    result = parse_uri("kitchen:album:123456789012345678901234567890ab:1:2")

    assert type(result) == AlbumTrackUri
    assert str(result) == "kitchen:album:123456789012345678901234567890ab:1:2"
    assert result.album_id == "123456789012345678901234567890ab"
    assert result.disc_no == 1
    assert result.track_no == 2


def test_parse_uri_album_track_invalid():
    with pytest.raises(ValueError) as err_inf:
        parse_uri("kitchen:album:123456789012345678901234567890ab:1:a")

    assert (
        str(err_inf.value)
        == "Invalid kitchen URI 'kitchen:album:123456789012345678901234567890ab:1:a': Invalid number 'a'"
    )


def test_parse_uri_station():
    result = parse_uri("kitchen:station:123456789012345678901234567890ab")

    assert type(result) == StationUri
    assert str(result) == "kitchen:station:123456789012345678901234567890ab"
    assert result.station_id == "123456789012345678901234567890ab"


def test_parse_uri_station_stream():
    result = parse_uri("kitchen:station:123456789012345678901234567890ab:1")

    assert type(result) == StationStreamUri
    assert str(result) == "kitchen:station:123456789012345678901234567890ab:1"
    assert result.station_id == "123456789012345678901234567890ab"
    assert result.stream_no == 1


def test_parse_uri_search():
    result = parse_uri("kitchen:search")

    assert type(result) == SearchUri
    assert str(result) == "kitchen:search"


def test_str_repr():
    uri = AlbumUri("foo")

    assert str(uri) == "kitchen:album:foo"
    assert repr(uri) == "kitchen:album:foo"


def test_eq_hash_equal():
    uri1 = AlbumUri("foo")
    uri2 = AlbumUri("foo")

    assert uri1 == uri2
    assert hash(uri1) == hash(uri2)


def test_eq_hash_different():
    uri1 = AlbumUri("foo")
    uri2 = AlbumUri("bar")

    assert uri1 != uri2
    assert hash(uri1) != hash(uri2)
