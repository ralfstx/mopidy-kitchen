import re


def parse_uri(uri: str):
    if uri.startswith("kitchen:"):
        parts = uri.split(":")
        if len(parts) > 1:
            head, tail = parts[1], parts[2:]
            try:
                if head == "root":
                    return _parse_root_uri(tail)
                if head == "albums":
                    return _parse_albums_uri(tail)
                if head == "album":
                    return _parse_album_uri(tail)
                if head == "artist":
                    return _parse_artist_uri(tail)
                if head == "search":
                    return _parse_search_uri(tail)
            except ValueError as error:
                raise ValueError(f"Invalid kitchen URI '{uri}': {str(error)}")


def _parse_root_uri(segments):
    if not segments:
        return ROOT_URI


def _parse_albums_uri(segments):
    if not segments:
        return AlbumsUri()


def _parse_album_uri(segments):
    if len(segments) == 1:
        album_id = _check_id(segments[0])
        return AlbumUri(album_id)
    if len(segments) == 3:
        album_id = _check_id(segments[0])
        disc_no = _check_number(segments[1])
        track_no = _check_number(segments[2])
        return AlbumTrackUri(album_id, disc_no, track_no)


def _parse_artist_uri(segments):
    if len(segments) == 1:
        artist_id = _check_id(segments[0])
        return ArtistUri(artist_id)


def _parse_search_uri(segments):
    return SearchUri()


def _check_id(segment: str):
    if not re.match("^[0-9a-f]{32}$", segment):
        raise ValueError(f"Invalid ID '{segment}'")
    return segment


def _check_number(segment: str):
    if not re.match("^[1-9][0-9]?$", segment):
        raise ValueError(f"Invalid number '{segment}'")
    return int(segment)


class KitchenUri:
    def __init__(self, uri: str):
        self.uri = uri

    def __str__(self) -> str:
        return self.uri

    def __repr__(self) -> str:
        return self.uri

    def __hash__(self) -> int:
        return hash(self.uri)

    def __eq__(self, o: object) -> bool:
        return type(o) == type(self) and str(o) == str(self)


class RootUri(KitchenUri):
    def __init__(self):
        super().__init__("kitchen:root")


class AlbumsUri(KitchenUri):
    def __init__(self):
        super().__init__("kitchen:albums")


class AlbumUri(KitchenUri):
    def __init__(self, album_id: str):
        super().__init__("kitchen:album:%s" % album_id)
        self.album_id = album_id


class AlbumTrackUri(KitchenUri):
    def __init__(self, album_id: str, disc_no: int, track_no: int):
        super().__init__("kitchen:album:%s:%d:%d" % (album_id, disc_no, track_no))
        self.album_id = album_id
        self.disc_no = disc_no
        self.track_no = track_no


class ArtistUri(KitchenUri):
    def __init__(self, artist_id: str):
        super().__init__("kitchen:artist:%s" % artist_id)


class SearchUri(KitchenUri):
    def __init__(self):
        super().__init__("kitchen:search")


ROOT_URI = RootUri()
