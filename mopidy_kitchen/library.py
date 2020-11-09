import logging
from pathlib import Path
from typing import Mapping

from mopidy import backend
from mopidy.models import Album, Artist, Image, Ref, SearchResult, Track

from . import Extension
from .index_files import AlbumIndex, AlbumIndexTrack, StationIndex
from .hash import make_hash
from .scanner import read_album, scan_dir
from .uri import (
    ROOT_URI,
    AlbumsUri,
    AlbumTrackUri,
    AlbumUri,
    ArtistUri,
    SearchUri,
    StationStreamUri,
    StationUri,
    StationsUri,
    parse_uri,
)

logger = logging.getLogger(__name__)


class KitchenLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(uri=str(ROOT_URI), name="Kitchen media")

    def __init__(self, backend, config):
        super().__init__(backend)
        self._albums_dir = Extension.get_albums_dir(config)
        self._config = config[Extension.ext_name]
        self._initialize()

    def _initialize(self):
        media_dir = Path(self._config["media_dir"])
        found = scan_dir(media_dir)
        self._albums: Mapping[str, AlbumIndex] = {}
        self._stations: Mapping[str, StationIndex] = {}
        for item in found:
            item_id = make_hash(item.name)
            if isinstance(item, AlbumIndex):
                if item_id in self._albums:
                    logger.warning("Duplicate albums: '%s' and '%s'", item.path, self._albums[item_id].path)
                    continue
                self._albums[item_id] = item
            elif isinstance(item, StationIndex):
                if item_id in self._stations:
                    logger.warning("Duplicate stations: '%s' and '%s'", item.path, self._stations[item_id].path)
                    continue
                self._stations[item_id] = item
        logger.info("Found %d albums", len(self._albums))
        logger.info("Found %d stations", len(self._stations))
        self._cleanup_albums_dir()
        self._create_symlinks()

    def _cleanup_albums_dir(self):
        logger.info("Cleaning up albums directory")
        try:
            files = self._albums_dir.glob("*")
            for file in files:
                file.unlink()
        except IOError as err:
            logger.warning("Error cleaning up albums directory: %s", err)

    def _create_symlinks(self):
        logger.info("Creating symlinks in albums directory")
        try:
            for album_id, album in self._albums.items():
                symlink_path = self._albums_dir / album_id
                if not symlink_path.exists():
                    symlink_path.symlink_to(album.path)
        except IOError as err:
            logger.warning("Error creating symlinks in albums directory: %s", err)

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
            if isinstance(kitchen_uri, StationsUri):
                return self._browse_stations()
            if isinstance(kitchen_uri, StationUri):
                return self._browse_station(kitchen_uri)
            raise ValueError("Unsupported URI")
        except Exception as e:
            logger.error("Error in browse for %s: %s", uri, e)
        return []

    def _browse_root(self):
        return [
            Ref.directory(uri=str(AlbumsUri()), name="Albums"),
            Ref.directory(uri=str(StationsUri()), name="Stations"),
        ]

    def _browse_albums(self):
        return [_make_album_ref(album_id, album) for album_id, album in self._albums.items()]

    def _browse_album(self, uri: AlbumUri):
        album = self._albums.get(uri.album_id)
        if album:
            return [_make_album_track_ref(uri.album_id, track) for track in album.tracks]
        return []

    def _browse_stations(self):
        return [_make_station_ref(station_id, station) for station_id, station in self._stations.items()]

    def _browse_station(self, uri: StationUri):
        station = self._stations.get(uri.station_id)
        if station:
            stream_uri = str(StationStreamUri(uri.station_id, 1))
            return [Ref.track(uri=stream_uri, name=station.name)]
        return []

    # == lookup ==

    def lookup(self, uri: str):
        try:
            kitchen_uri = parse_uri(uri)
            if isinstance(kitchen_uri, AlbumUri):
                return self._lookup_album(kitchen_uri)
            if isinstance(kitchen_uri, AlbumTrackUri):
                return self._lookup_album_track(kitchen_uri)
            if isinstance(kitchen_uri, StationUri):
                return self._lookup_station(kitchen_uri)
            if isinstance(kitchen_uri, StationStreamUri):
                return self._lookup_station_stream(kitchen_uri)
            raise ValueError("Unsupported URI")
        except Exception as e:
            logger.error("Error in lookup for %s: %s", uri, e)
            return []

    def _lookup_album(self, uri: AlbumUri):
        album = self._albums.get(uri.album_id)
        if album:
            return _make_album_tracks(uri.album_id, album)
        return []

    def _lookup_album_track(self, uri: AlbumTrackUri):
        album = self._albums.get(uri.album_id)
        if album:
            track = _find_track(album, uri.disc_no, uri.track_no)
            if track:
                return [_make_album_track(uri.album_id, album, track)]
        return []

    def _lookup_station(self, uri: StationUri):
        station = self._stations.get(uri.station_id)
        if station:
            return [_make_station_track(uri.station_id, station, 1)]
        return []

    def _lookup_station_stream(self, uri: StationStreamUri):
        station = self._stations.get(uri.station_id)
        if station:
            return [_make_station_track(uri.station_id, station, uri.stream_no)]
        return []

    # == search ==

    def search(self, query, uris=None, exact=False):
        q = []
        for field, values in query.items() if query else []:
            q.extend((field, value) for value in values)
        match_fn = _match_exact if exact else _match_start
        albums = []
        tracks = []
        for album_id, album in self._albums.items():
            for field, value in q:
                matches = _make_matcher(value, match_fn)
                if field in ("any", "album"):
                    if matches(album.title):
                        albums.append(_make_album(album_id, album))
                        continue
                if field in ("any", "albumartist"):
                    if any(matches(artist) for artist in album.artists):
                        albums.append(_make_album(album_id, album))
                        continue
                if field in ("any", "track_name"):
                    for track in album.tracks:
                        if track.title and matches(track.title):
                            tracks.append(_make_album_track(album_id, album, track))
        search_uri = str(SearchUri())
        return SearchResult(uri=search_uri, albums=albums, tracks=tracks)

    # == get_images ==

    def get_images(self, uris):
        images = {}
        for uri in uris:
            kitchen_uri = parse_uri(uri)
            if isinstance(kitchen_uri, (AlbumUri, AlbumTrackUri)):
                album_id = kitchen_uri.album_id
                album = self._albums.get(album_id)
                if album:
                    img_path = album.path / "cover.jpg"
                    if img_path.exists():
                        image_uri = f"/kitchen/albums/{album_id}/cover.jpg"
                        images[uri] = [Image(uri=image_uri)]
        return images

    # == refresh ==

    def refresh(self, uri):
        if uri:
            kitchen_uri = parse_uri(uri)
            if isinstance(kitchen_uri, AlbumUri):
                self._refresh_album(kitchen_uri.album_id)
            elif isinstance(kitchen_uri, AlbumsUri):
                self._initialize()
        else:
            self._initialize()

    def _refresh_album(self, album_id):
        album = self._albums.get(album_id)
        if album:
            del self._albums[album_id]
            new_album = read_album(album.path)
            if new_album:
                album_id = make_hash(new_album.name)
                self._albums[album_id] = new_album

    # == get_playback_uri (extension) ==

    def get_playback_uri(self, uri: str):
        kitchen_uri = parse_uri(uri)
        if isinstance(kitchen_uri, AlbumTrackUri):
            album = self._albums.get(kitchen_uri.album_id)
            if album:
                track = _find_track(album, kitchen_uri.disc_no, kitchen_uri.track_no)
                if track:
                    return track.path.as_uri()
        elif isinstance(kitchen_uri, StationStreamUri):
            station = self._stations.get(kitchen_uri.station_id)
            if station and kitchen_uri.stream_no == 1:
                return station.stream


def _match_exact(word: str, term: str):
    return word == term


def _match_start(word: str, term: str):
    return word.startswith(term)


def _make_matcher(expr: str, match_fn):
    terms = _split_lower(expr)

    def matches_all_terms(string: str):
        words = _split_lower(string)
        return all(_matches_any_word(term, words, match_fn) for term in terms)

    return matches_all_terms


def _matches_any_word(term: str, words, match_fn):
    for word in words:
        if match_fn(word, term):
            return True
    return False


def _split_lower(string: str):
    return [part for part in string.lower().split() if part]


def _find_track(album: AlbumIndex, disc_no: int, track_no: int):
    for track in album.tracks:
        if track.disc_no == disc_no and track.track_no == track_no:
            return track


def _make_album_ref(album_id: str, album: AlbumIndex):
    return Ref.album(uri=str(AlbumUri(album_id)), name=album.name)


def _make_station_ref(station_id: str, station: StationIndex):
    return Ref.album(uri=str(StationUri(station_id)), name=station.name)


def _make_album_track_ref(album_id, track: AlbumIndexTrack):
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


def _make_album_track(album_id: str, album: AlbumIndex, track: AlbumIndexTrack):
    mop_album = _make_album(album_id, album)
    return _make_track_with_album(album_id, track, mop_album)


def _make_album_tracks(album_id: str, album: AlbumIndex):
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


def _make_station_track(station_id: str, station: StationIndex, stream_no: int):
    kwargs = {
        "uri": str(StationStreamUri(station_id, stream_no)),
        "name": station.name,
    }
    return Track(**kwargs)


def _make_artist(name: str):
    uri = str(ArtistUri(make_hash(name)))
    return Artist(uri=uri, name=name)
