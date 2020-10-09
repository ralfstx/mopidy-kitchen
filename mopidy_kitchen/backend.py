import pykka
import logging

from mopidy import backend
from .library import KitchenLibraryProvider
from .playback import KitchenPlaybackProvider

logger = logging.getLogger(__name__)


class KitchenBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = ["kitchen"]

    def __init__(self, config, audio):
        super().__init__()
        self.audio = audio
        self.config = config
        self.library = KitchenLibraryProvider(backend=self, config=config)
        self.playback = KitchenPlaybackProvider(audio=audio, backend=self)
