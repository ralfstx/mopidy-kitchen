from mopidy import backend


class KitchenPlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        return self.backend.library.get_playback_uri(uri)
