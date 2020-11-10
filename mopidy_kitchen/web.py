from pathlib import Path

import tornado.web

from . import Extension


def webapp_factory(config, core):
    albums_dir = Extension.get_albums_dir(config)
    www_dir = Path(__file__).parent / "www"
    return [
        (r"/albums/(.+)", FileHandler, {"path": albums_dir}),
        (r"/(.*)", FileHandler, {"path": www_dir}),
    ]


class FileHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path: str) -> str:
        return super().parse_url_path(url_path or "index.html")
