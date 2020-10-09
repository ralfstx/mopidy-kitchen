from mopidy_kitchen.uri import ROOT_URI, AlbumsUri, AlbumTrackUri, AlbumUri, SearchUri, parse_uri


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


def test_parse_uri_search():
    result = parse_uri("kitchen:search?")

    assert type(result) == SearchUri
    assert str(result) == "kitchen:search?"


def test_parse_uri_album():
    result = parse_uri("kitchen:album:123456789012345678901234567890ab")

    assert type(result) == AlbumUri
    assert str(result) == "kitchen:album:123456789012345678901234567890ab"
    assert result.album_id == "123456789012345678901234567890ab"


def test_parse_uri_album_track():
    result = parse_uri("kitchen:album:123456789012345678901234567890ab:1:2")

    assert type(result) == AlbumTrackUri
    assert str(result) == "kitchen:album:123456789012345678901234567890ab:1:2"
    assert result.album_id == "123456789012345678901234567890ab"
    assert result.disc_no == 1
    assert result.track_no == 2


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