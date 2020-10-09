import logging

from mopidy.models import Album, Ref, SearchResult, Track

from mopidy_kitchen.library import KitchenLibraryProvider
from mopidy_kitchen.uri import AlbumsUri

from .helpers import EXAMPLE_ALBUM, make_album, make_config


def test_detects_duplicates(tmp_path, caplog):
    make_album(tmp_path / "media" / "foo", EXAMPLE_ALBUM)
    make_album(tmp_path / "media" / "bar", EXAMPLE_ALBUM)

    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    assert len(provider.browse(str(AlbumsUri()))) == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.WARNING
    assert caplog.records[0].getMessage() in (
        f"Duplicate albums: '{tmp_path}/media/foo' and '{tmp_path}/media/bar'",
        f"Duplicate albums: '{tmp_path}/media/bar' and '{tmp_path}/media/foo'",
    )


# == root_directory ==


def test_root_directory(tmp_path, caplog):
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.root_directory

    assert caplog.text == ""
    assert result == Ref.directory(uri="kitchen:root", name="Kitchen media")


# == browse ==


def test_browse_root(tmp_path, caplog):
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.browse("kitchen:root")

    assert caplog.text == ""
    assert result == [
        Ref.directory(uri="kitchen:albums", name="Albums"),
    ]


def test_browse_albums(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "John Doe - One Day"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.browse("kitchen:albums")

    assert caplog.text == ""
    assert len(result) > 0
    assert result[0].type == "album"
    assert result == [Ref.album(uri="kitchen:album:95506c273e4ecb0333d19824d66ab586", name="John Doe - One Day")]


def test_browse_album(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse("kitchen:albums")[0].uri

    result = provider.browse(album_uri)

    assert caplog.text == ""
    assert len(result) > 0
    assert result[0].type == "track"


def test_browse_missing_album(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.browse("kitchen:album:01234567012345670123456701234567")

    assert caplog.text == ""
    assert result == []


def test_browse_track(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse("kitchen:albums")[0].uri

    result = provider.browse(album_uri + ":1:1")

    assert caplog.text == ""
    assert result == []


def test_browse_other(tmp_path, caplog):
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.browse("kitchen:nonsense")

    assert result == []
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert caplog.records[0].getMessage() == "Error in browse for kitchen:nonsense: Unsupported URI"


# == lookup ==


def test_lookup_album(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse("kitchen:albums")[0].uri

    result = provider.lookup(album_uri)

    assert caplog.text == ""
    assert len(result) > 0
    assert isinstance(result[0], Track)


def test_lookup_missing_album(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.lookup("kitchen:album:01234567012345670123456701234567")

    assert caplog.text == ""
    assert result == []


def test_lookup_track(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse("kitchen:albums")[0].uri

    result = provider.lookup(album_uri + ":1:1")

    assert caplog.text == ""
    assert len(result) > 0
    assert isinstance(result[0], Track)


def test_lookup_missing_track(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse("kitchen:albums")[0].uri

    result = provider.lookup(album_uri + ":9:9")

    assert caplog.text == ""
    assert result == []


def test_lookup_other(tmp_path, caplog):
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.lookup("kitchen:nonsense")

    assert result == []
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert caplog.records[0].getMessage() == "Error in lookup for kitchen:nonsense: Unsupported URI"


# == search ==


def test_search_not_found(tmp_path, caplog):
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"any": ["foo"]})

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search?"
    assert result.albums == ()
    assert result.tracks == ()


def test_search_match_album(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "Goodbye Maria"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Goodbye Marianne"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Goodbye Marlene"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"album": ["mari"]})

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search?"
    assert [album.name for album in result.albums] == ["Goodbye Maria", "Goodbye Marianne"]
    assert result.tracks == ()


def test_search_match_album_exact(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "Goodbye Maria"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Goodbye Marianne"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Goodbye Marlene"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"album": ["maria"]}, exact=True)

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search?"
    assert [album.name for album in result.albums] == ["Goodbye Maria"]
    assert result.tracks == ()


def test_search_match_albumartist(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "One", "artist": "John Jackson"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Two", "artist": "Jack Johnson"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Three", "artist": "James Jameson"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"albumartist": ["jack"]})

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search?"
    assert [album.name for album in result.albums] == ["One", "Two"]
    assert result.tracks == ()


def test_search_match_albumartist_exact(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "One", "artist": "John Jackson"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Two", "artist": "Jack Johnson"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Three", "artist": "James Jameson"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"albumartist": ["jack"]}, exact=True)

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search?"
    assert [album.name for album in result.albums] == ["Two"]
    assert result.tracks == ()


def test_search_match_trackname(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"track_name": ["morn"]})

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search?"
    assert result.albums == ()
    assert [track.name for track in result.tracks] == ["The Morning"]


# == get_path ==


def test_get_path_album_track(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "John Doe - One Day", "tracks": [{"path": "01.ogg"}]})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    track_uri = provider.browse("kitchen:albums")[0].uri + ":1:1"

    result = provider.get_path(track_uri)

    assert caplog.text == ""
    assert result == tmp_path / "media" / "a1" / "01.ogg"


def join_artists(album: Album):
    return ",".join(artist.name for artist in album.artists)
