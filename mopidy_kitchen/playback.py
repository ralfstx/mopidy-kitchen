from mopidy import backend


class KitchenPlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        path = self.backend.library.get_path(uri)
        if path:
            return path.as_uri()
