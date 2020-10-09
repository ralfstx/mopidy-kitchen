import logging
from pathlib import Path

from .album_index import AlbumIndex, AlbumIndexError

logger = logging.getLogger(__name__)


class Scanner:
    def __init__(self, root_dir: Path):
        self._root = Path(root_dir).resolve()

    def scan(self):
        if not self._root.is_dir():
            logger.error("Not a directory: %s", self._root)
            return []
        found = []
        self._scan_dir(self._root, found)
        logger.info("Found %d albums", len(found))
        return sorted(found, key=lambda a: a.name)

    def _scan_dir(self, dir: Path, found: list):
        index_file = dir / "index.json"
        if index_file.is_file():
            album = _read_album_index(index_file)
            if album:
                found.append(album)
        else:
            for child in dir.iterdir():
                if child.is_dir():
                    self._scan_dir(child, found)


def _read_album_index(file_path: Path):
    try:
        return AlbumIndex.read_from_file(file_path)
    except AlbumIndexError as err:
        logger.error(str(err))
    except Exception:
        logger.exception("Failed reading album at %s", file_path)
