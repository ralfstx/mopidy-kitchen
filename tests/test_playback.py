from mopidy_kitchen.uri import AlbumsUri

from mopidy_kitchen.library import KitchenLibraryProvider
from mopidy_kitchen.playback import KitchenPlaybackProvider

from .helpers import EXAMPLE_ALBUM, make_album, make_config


def test_parse_uri_none(tmp_path):
    library = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    playback = KitchenPlaybackProvider(None, FakeBackend(library))

    result = playback.translate_uri("kitchen:nonsense")

    assert result is None


def test_parse_uri_match(tmp_path):
    make_album(tmp_path / "media" / "a1", EXAMPLE_ALBUM)
    library = KitchenLibraryProvider(backend={}, config=make_config(tmp_path))
    playback = KitchenPlaybackProvider(None, FakeBackend(library))
    album_uri = library.browse(str(AlbumsUri()))[0].uri

    result = playback.translate_uri(album_uri + ":1:2")

    assert result == f"file://{tmp_path}/media/a1/01/02.ogg"


class FakeBackend:
    def __init__(self, library):
        self.library = library
