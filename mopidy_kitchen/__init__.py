import logging
import pathlib

import pkg_resources

from mopidy import config, ext

try:
    __version__ = pkg_resources.get_distribution("Mopidy-Kitchen").version
# needed for debugging in VSCode
except pkg_resources.ResolutionError:
    __version__ = "devel"

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = "Mopidy-Kitchen"
    ext_name = "kitchen"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["media_dir"] = config.Path()
        return schema

    def setup(self, registry):
        from .backend import KitchenBackend
        from .web import webapp_factory

        registry.add("backend", KitchenBackend)
        registry.add("http:app", {"name": self.ext_name, "factory": webapp_factory})

    @classmethod
    def get_albums_dir(self, config):
        albums_dir = self.get_data_dir(config) / "albums"
        albums_dir.mkdir(parents=True, exist_ok=True)
        return albums_dir
