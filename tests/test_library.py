import logging

from mopidy.models import Album, Image, Ref, SearchResult, Track

from mopidy_kitchen.library import KitchenLibraryProvider
from mopidy_kitchen.uri import AlbumsUri, parse_uri

from .helpers import EXAMPLE_ALBUM, make_album, make_config, make_image, make_station


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
        Ref.directory(uri="kitchen:stations", name="Stations"),
    ]


def test_browse_albums(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "John Doe - One Day"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.browse("kitchen:albums")

    assert caplog.text == ""
    assert len(result) > 0
    assert result[0].type == "album"
    assert result == [Ref.album(uri="kitchen:album:95506c273e4ecb0333d19824d66ab586", name="John Doe - One Day")]


def test_browse_stations(tmp_path, caplog):
    make_station(tmp_path / "media" / "r1", {"name": "Radio 1", "stream": "http://radio1.com/stream"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.browse("kitchen:stations")

    assert caplog.text == ""
    assert len(result) > 0
    assert result[0].type == "album"
    assert result == [Ref.album(uri="kitchen:station:770e06d40b8b4d64e89c24098d25fdc2", name="Radio 1")]


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


def test_browse_station(tmp_path, caplog):
    make_station(tmp_path / "media" / "r1", {"name": "Radio 1", "stream": "http://radio1.com/stream"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    station_uri = provider.browse("kitchen:stations")[0].uri

    result = provider.browse(station_uri)

    assert caplog.text == ""
    assert len(result) > 0
    assert result[0].type == "track"


def test_browse_missing_station(tmp_path, caplog):
    make_station(tmp_path / "media" / "r1", {"name": "Radio 1", "stream": "http://radio1.com/stream"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.browse("kitchen:station:01234567012345670123456701234567")

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


def test_lookup_album_track(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse("kitchen:albums")[0].uri

    result = provider.lookup(album_uri + ":1:1")

    assert caplog.text == ""
    assert len(result) > 0
    assert isinstance(result[0], Track)


def test_lookup_missing_album_track(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse("kitchen:albums")[0].uri

    result = provider.lookup(album_uri + ":9:9")

    assert caplog.text == ""
    assert result == []


def test_lookup_station(tmp_path, caplog):
    make_station(tmp_path / "media" / "r1", {"name": "Radio 1", "stream": "http://radio1.com/stream"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    station_uri = provider.browse("kitchen:stations")[0].uri

    result = provider.lookup(station_uri)

    assert caplog.text == ""
    assert len(result) > 0
    assert isinstance(result[0], Track)


def test_lookup_missing_station(tmp_path, caplog):
    make_station(tmp_path / "media" / "r1", {"name": "Radio 1", "stream": "http://radio1.com/stream"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.lookup("kitchen:station:01234567012345670123456701234567")

    assert caplog.text == ""
    assert result == []


def test_lookup_station_stream(tmp_path, caplog):
    make_station(tmp_path / "media" / "r1", {"name": "Radio 1", "stream": "http://radio1.com/stream"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    station_uri = provider.browse("kitchen:stations")[0].uri

    result = provider.lookup(station_uri + ":1")

    assert caplog.text == ""
    assert len(result) > 0
    assert isinstance(result[0], Track)


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
    assert result.uri == "kitchen:search"
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
    assert result.uri == "kitchen:search"
    assert {album.name for album in result.albums} == {"Goodbye Maria", "Goodbye Marianne"}
    assert result.tracks == ()


def test_search_match_multi_words(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "Goodbye Maria"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Goodbye Marianne"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Good Night Marlene"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"album": ["ni mar"]})

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search"
    assert [album.name for album in result.albums] == ["Good Night Marlene"]
    assert result.tracks == ()


def test_search_match_multi_words_across_different_fields(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "Goodbye Maria", "artist": "John Doe"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Goodbye Marianne", "artist": "John Doe"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Good Night Marlene", "artist": "John Doe"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"any": ["john maria"]})

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search"
    assert {album.name for album in result.albums} == {"Goodbye Maria", "Goodbye Marianne"}
    assert result.tracks == ()


def test_search_match_album_exact(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "Goodbye Maria"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Goodbye Marianne"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Goodbye Marlene"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"album": ["maria"]}, exact=True)

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search"
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
    assert result.uri == "kitchen:search"
    assert {album.name for album in result.albums} == {"One", "Two"}
    assert result.tracks == ()


def test_search_match_albumartist_exact(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "test1", "title": "One", "artist": "John Jackson"})
    make_album(tmp_path / "media" / "a2", {"name": "test2", "title": "Two", "artist": "Jack Johnson"})
    make_album(tmp_path / "media" / "a3", {"name": "test3", "title": "Three", "artist": "James Jameson"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"albumartist": ["jack"]}, exact=True)

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search"
    assert [album.name for album in result.albums] == ["Two"]
    assert result.tracks == ()


def test_search_match_trackname(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.search({"track_name": ["morn"]})

    assert caplog.text == ""
    assert type(result) == SearchResult
    assert result.uri == "kitchen:search"
    assert result.albums == ()
    assert [track.name for track in result.tracks] == ["The Morning"]


# == get_images ==


def test_get_images_empty(tmp_path, caplog):
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))

    result = provider.get_images([])

    assert caplog.text == ""
    assert result == {}


def test_get_images_for_album_without_image(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse(str(AlbumsUri()))[0].uri

    result = provider.get_images([album_uri])

    assert caplog.text == ""
    assert result == {}


def test_get_images_for_album_with_image(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    make_image(tmp_path / "media" / "a1" / "cover.jpg")
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    album_uri = provider.browse(str(AlbumsUri()))[0].uri
    album_id = parse_uri(album_uri).album_id

    result = provider.get_images([album_uri])

    assert caplog.text == ""
    assert result == {album_uri: [Image(uri=f"/kitchen/albums/{album_id}/cover.jpg")]}


def test_get_images_for_track_with_image(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    make_image(tmp_path / "media" / "a1" / "cover.jpg")
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    track_uri = provider.browse(str(AlbumsUri()))[0].uri + ":1:1"
    album_id = parse_uri(track_uri).album_id

    result = provider.get_images([track_uri])

    assert caplog.text == ""
    assert result == {track_uri: [Image(uri=f"/kitchen/albums/{album_id}/cover.jpg")]}


def test_get_images_for_multiple_uris(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    make_image(tmp_path / "media" / "a1" / "cover.jpg")
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    track1_uri = provider.browse(str(AlbumsUri()))[0].uri + ":1:1"
    track2_uri = provider.browse(str(AlbumsUri()))[0].uri + ":1:2"
    album_id = parse_uri(track1_uri).album_id

    result = provider.get_images([track1_uri, track2_uri])

    assert caplog.text == ""
    assert result == {
        track1_uri: [Image(uri=f"/kitchen/albums/{album_id}/cover.jpg")],
        track2_uri: [Image(uri=f"/kitchen/albums/{album_id}/cover.jpg")],
    }


# == get_playback_uri ==


def test_get_playback_uri_album_track(tmp_path, caplog):
    make_album(tmp_path / "media" / "a1", {"name": "John Doe - One Day", "tracks": [{"path": "01.ogg"}]})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    track_uri = provider.browse("kitchen:albums")[0].uri + ":1:1"

    result = provider.get_playback_uri(track_uri)

    assert caplog.text == ""
    assert result == f"file://{tmp_path}/media/a1/01.ogg"


def test_get_playback_uri_station_stream(tmp_path, caplog):
    make_station(tmp_path / "media" / "r1", {"name": "Radio 1", "stream": "http://radio1.com/stream"})
    provider = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    stream_uri = provider.browse("kitchen:stations")[0].uri + ":1"

    result = provider.get_playback_uri(stream_uri)

    assert caplog.text == ""
    assert result == "http://radio1.com/stream"


def join_artists(album: Album):
    return ",".join(artist.name for artist in album.artists)
