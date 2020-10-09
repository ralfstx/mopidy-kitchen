import logging
from pathlib import Path

from mopidy import backend
from mopidy.models import Album, Artist, Ref, SearchResult, Track

from . import Extension
from .album_index import AlbumIndex, AlbumIndexTrack
from .hash import make_hash
from .scanner import Scanner
from .uri import (
    ROOT_URI,
    AlbumsUri,
    AlbumTrackUri,
    AlbumUri,
    ArtistUri,
    SearchUri,
    parse_uri,
)

logger = logging.getLogger(__name__)


class KitchenLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(uri=str(ROOT_URI), name="Kitchen media")

    def __init__(self, backend, config):
        super().__init__(backend)
        self._data_dir = Extension.get_data_dir(config)
        self._config = config[Extension.ext_name]
        media_dir = self._config["media_dir"]
        albums = Scanner(Path(media_dir)).scan()
        self._albums = {}
        for album in albums:
            album_id = make_hash(album.name)
            if album_id in self._albums:
                logger.warning("Duplicate albums: '%s' and '%s'", album.path, self._albums[album_id].path)
            self._albums[album_id] = album

    # == browse ==

    def browse(self, uri):
        try:
            kitchen_uri = parse_uri(uri)
            if kitchen_uri == ROOT_URI:
                return self._browse_root()
            if isinstance(kitchen_uri, AlbumsUri):
                return self._browse_albums()
            if isinstance(kitchen_uri, AlbumUri):
                return self._browse_album(kitchen_uri)
            if isinstance(kitchen_uri, AlbumTrackUri):
                return self._browse_album_track(kitchen_uri)
            else:
                raise ValueError("Unsupported URI")
        except Exception as e:
            logger.error("Error in browse for %s: %s", uri, e)
            return []

    def _browse_root(self):
        return [
            Ref.directory(uri=str(AlbumsUri()), name="Albums"),
        ]

    def _browse_albums(self):
        return [_make_album_ref(album_id, album) for album_id, album in self._albums.items()]

    def _browse_album(self, uri: AlbumUri):
        album = self._albums.get(uri.album_id)
        if album:
            return [_make_track_ref(uri.album_id, track) for track in album.tracks]
        return []

    def _browse_album_track(self, uri: AlbumUri):
        return []

    # == lookup ==

    def lookup(self, uri: str):
        try:
            kitchen_uri = parse_uri(uri)
            if isinstance(kitchen_uri, AlbumUri):
                return self._lookup_album(kitchen_uri)
            if isinstance(kitchen_uri, AlbumTrackUri):
                return self._lookup_album_track(kitchen_uri)
            raise ValueError("Unsupported URI")
        except Exception as e:
            logger.error("Error in lookup for %s: %s", uri, e)
            return []

    def _lookup_album(self, uri: AlbumUri):
        album = self._albums.get(uri.album_id)
        if album:
            return _make_tracks(uri.album_id, album)
        return []

    def _lookup_album_track(self, uri: AlbumTrackUri):
        album = self._albums.get(uri.album_id)
        if album:
            track = _find_track(album, uri.disc_no, uri.track_no)
            if track:
                return [_make_track(uri.album_id, album, track)]
        return []

    # == search ==

    def search(self, query, uris=None, exact=False):
        q = []
        for field, values in query.items() if query else []:
            q.extend((field, value.lower()) for value in values)
        albums = []
        tracks = []
        matcher = _matches_exact if exact else _matches_start
        for album_id, album in self._albums.items():
            for field, value in q:
                if field in ("any", "album"):
                    if matcher(album.title, value):
                        albums.append(_make_album(album_id, album))
                        continue
                if field in ("any", "albumartist"):
                    if any(matcher(artist, value) for artist in album.artists):
                        albums.append(_make_album(album_id, album))
                        continue
                if field in ("any", "track_name"):
                    for track in album.tracks:
                        if track.title and matcher(track.title, value):
                            tracks.append(_make_track(album_id, album, track))
        search_uri = str(SearchUri())
        return SearchResult(uri=search_uri, albums=albums, tracks=tracks)

    # == get_path (extension) ==

    def get_path(self, uri: str):
        kitchen_uri = parse_uri(uri)
        if isinstance(kitchen_uri, AlbumTrackUri):
            album = self._albums.get(kitchen_uri.album_id)
            if album:
                track = _find_track(album, kitchen_uri.disc_no, kitchen_uri.track_no)
                if track:
                    return track.path


def _matches_exact(string: str, term: str):
    lower_term = term.lower()
    for word in string.lower().split():
        if word == lower_term:
            return True
    return False


def _matches_start(string: str, term: str):
    lower_term = term.lower()
    for word in string.lower().split():
        if word.startswith(lower_term):
            return True
    return False


def _find_track(album: AlbumIndex, disc_no: int, track_no: int):
    for track in album.tracks:
        if track.disc_no == disc_no and track.track_no == track_no:
            return track


def _make_album_ref(album_id: str, album: AlbumIndex):
    return Ref.album(uri=str(AlbumUri(album_id)), name=album.name)


def _make_track_ref(album_id, track: AlbumIndexTrack):
    uri = str(AlbumTrackUri(album_id, track.disc_no, track.track_no))
    return Ref.track(uri=uri, name=track.title)


def _make_album(album_id: str, album: AlbumIndex):
    kwargs = {
        "uri": str(AlbumUri(album_id)),
        "name": album.title,
        "num_tracks": len(album.tracks),
        "num_discs": album.tracks[-1].disc_no if len(album.tracks) else 1,
    }
    if album.artists:
        kwargs["artists"] = [_make_artist(artist) for artist in album.artists]
    if album.musicbrainz_id:
        kwargs["musicbrainz_id"] = album.musicbrainz_id
    return Album(**kwargs)


def _make_track(album_id: str, album: AlbumIndex, track: AlbumIndexTrack):
    mop_album = _make_album(album_id, album)
    return _make_track_with_album(album_id, track, mop_album)


def _make_tracks(album_id: str, album: AlbumIndex):
    mop_album = _make_album(album_id, album)
    return [_make_track_with_album(album_id, track, mop_album) for track in album.tracks]


def _make_track_with_album(album_id: str, track: AlbumIndexTrack, album: Album):
    kwargs = {
        "uri": str(AlbumTrackUri(album_id, track.disc_no, track.track_no)),
        "name": track.title,
        "album": album,
        "disc_no": track.disc_no,
        "track_no": track.track_no,
    }
    if track.artists:
        kwargs["artists"] = [_make_artist(artist) for artist in track.artists]
    if track.duration_ms:
        kwargs["length"] = track.duration_ms
    if track.musicbrainz_id:
        kwargs["musicbrainz_id"] = track.musicbrainz_id
    return Track(**kwargs)


def _make_artist(name: str):
    uri = str(ArtistUri(make_hash(name)))
    return Artist(uri=uri, name=name)
