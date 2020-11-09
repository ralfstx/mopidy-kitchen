import json
from pathlib import Path


class AlbumIndex:
    @staticmethod
    def read_from_file(file_path: Path):
        with open(file_path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as err:
                raise IndexFileError(
                    "Could not parse JSON in '%s': %s at %d:%d" % (file_path, err.msg, err.lineno, err.colno)
                )
        try:
            return AlbumIndex(data, file_path.parent)
        except IndexFileError as err:
            raise IndexFileError("Invalid index format in '%s': %s" % (file_path, err))

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def title(self):
        return self._title

    @property
    def artists(self):
        return self._artists

    @property
    def musicbrainz_id(self):
        return self._musicbrainz_id

    @property
    def tracks(self):
        return self._tracks

    def __init__(self, data: dict, root_path: Path):
        context = "album"
        _check_object(data, context)
        self._path = root_path
        self._name = _extract_name(data, context)
        self._title = _extract_title(data, context)
        self._artists = _extract_artists(data, context)
        self._musicbrainz_id = _extract_musicbrainz_id(data, context)
        self._tracks = self._extract_tracks(data, context)

    def _extract_tracks(self, data: dict, context: str):
        discs = _extract_discs(data, context)
        tracks = []
        for disc_no, disc in enumerate(discs, start=1):
            context = f"disc {disc_no}"
            _check_object(disc, context)
            path = self._path / _get(disc, "path", context, default=".", check=_check_string)
            for track_no, track in enumerate(_get(disc, "tracks", context, check=_check_array), start=1):
                tracks.append(AlbumIndexTrack(path, disc_no, track_no, track))
        return tuple(tracks)


class AlbumIndexTrack:
    @property
    def path(self):
        return self._path

    @property
    def disc_no(self):
        return self._disc_no

    @property
    def track_no(self):
        return self._track_no

    @property
    def duration_ms(self):
        return self._duration_ms

    @property
    def title(self):
        return self._title

    @property
    def artists(self):
        return self._artists

    @property
    def musicbrainz_id(self):
        return self._musicbrainz_id

    def __init__(self, root_path: Path, disc_no: int, track_no: int, data: dict):
        context = f"track {track_no} of disc {disc_no}"
        _check_object(data, context)
        self._path = root_path / _get(data, "path", context, required=True, check=_check_string)
        self._disc_no = disc_no
        self._track_no = track_no
        self._duration_ms = _extract_length(data, context)
        self._title = _extract_title(data, context)
        self._artists = _extract_artists(data, context)
        self._musicbrainz_id = _extract_musicbrainz_id(data, context)


class StationIndex:
    @staticmethod
    def read_from_file(file_path: Path):
        with open(file_path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as err:
                raise IndexFileError(
                    "Could not parse JSON in '%s': %s at %d:%d" % (file_path, err.msg, err.lineno, err.colno)
                )
        try:
            return StationIndex(data, file_path.parent)
        except IndexFileError as err:
            raise IndexFileError("Invalid index format in '%s': %s" % (file_path, err))

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def stream(self):
        return self._stream

    def __init__(self, data: dict, root_path: Path):
        context = "album"
        _check_object(data, context)
        self._path = root_path
        self._name = _extract_name(data, context)
        self._stream = _extract_stream(data, context)


def _extract_name(data: dict, context: str):
    return _get(data, "name", context, required=True, check=_check_string)


def _extract_stream(data: dict, context: str):
    return _get(data, "stream", context, required=True, check=_check_string)


def _extract_title(data: dict, context: str):
    return _get(data, "title", context, default="", check=_check_string)


def _extract_artists(data: dict, context: str):
    artist = _get(data, "artist", context, check=_check_string)
    return [artist] if artist else []


def _extract_musicbrainz_id(data: dict, context: str):
    return _get(data, "musicbrainz_id", context, default="", check=_check_string)


def _extract_length(data: dict, context: str):
    length = _get(data, "length", context, default=0, check=_check_non_negative_number)
    return int(length * 1000) if length else 0


def _extract_discs(data: dict, context: str):
    if "discs" in data:
        discs = _get(data, "discs", context, check=_check_array)
    elif "tracks" in data:
        tracks = _get(data, "tracks", context, check=_check_array)
        discs = [{"tracks": tracks}]
    else:
        discs = [{"tracks": []}]
    return discs


def _get(object: dict, name: str, context: str, check=None, default=None, required=False):
    if name not in object:
        if required:
            raise IndexFileError(f"Attribute '{name}' is missing in {context}")
        else:
            return default
    value = object[name]
    if check:
        check(value, f"Attribute '{name}' in {context}")
    return value


def _check_object(value, name: str):
    if not isinstance(value, dict):
        raise IndexFileError(f"{name.capitalize()} is not an object")


def _check_array(value, name: str):
    if not isinstance(value, list):
        raise IndexFileError(f"{name.capitalize()} is not an array")


def _check_string(value, name: str):
    if not isinstance(value, str):
        raise IndexFileError(f"{name.capitalize()} is not a string")


def _check_non_negative_number(value, name: str):
    if not isinstance(value, (int, float)):
        raise IndexFileError(f"{name.capitalize()} is not a number")
    if value < 0:
        raise IndexFileError(f"{name.capitalize()} is negative")


class IndexFileError(ValueError):
    def __init__(self, message) -> None:
        super().__init__(message)
