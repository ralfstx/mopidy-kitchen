import re


def parse_uri(uri: str):
    if uri == "kitchen:root":
        return ROOT_URI
    if uri == "kitchen:albums":
        return AlbumsUri()
    if uri == "kitchen:search?":
        return SearchUri()
    match = re.match("^kitchen:album:([0-9a-f]{32})(:([1-9][0-9]?):([1-9][0-9]?))?$", uri)
    if match:
        album_id = match[1]
        if match[2]:
            return AlbumTrackUri(album_id, int(match[3]), int(match[4]))
        else:
            return AlbumUri(album_id)
    match = re.match("^kitchen:artist:([0-9a-f]{32})$", uri)
    if match:
        artist_id = match[1]
        return ArtistUri(artist_id)


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
    def __init__(self, album_id, disc_no, track_no):
        super().__init__("kitchen:album:%s:%d:%d" % (album_id, disc_no, track_no))
        self.album_id = album_id
        self.disc_no = disc_no
        self.track_no = track_no


class ArtistUri(KitchenUri):
    def __init__(self, artist_id):
        super().__init__("kitchen:artist:%s" % artist_id)


class SearchUri(KitchenUri):
    def __init__(self):
        super().__init__("kitchen:search?")


ROOT_URI = RootUri()
