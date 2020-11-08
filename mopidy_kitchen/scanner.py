import logging
from pathlib import Path
from typing import List

from .album_index import AlbumIndex, AlbumIndexError

logger = logging.getLogger(__name__)


def scan_albums(root_dir: Path):
    root = Path(root_dir).resolve()
    if not root.is_dir():
        logger.error("Not a directory: %s", root)
        return []
    found = []
    _scan_dir(root, found)
    return sorted(found, key=lambda a: a.name)


def _scan_dir(dir: Path, found: List[AlbumIndex]):
    index_file = dir / "index.json"
    if index_file.is_file():
        album = _read_album_index(index_file)
        if album:
            found.append(album)
    else:
        for child in dir.iterdir():
            if child.is_dir():
                _scan_dir(child, found)


def read_album(dir: Path):
    index_file = dir / "index.json"
    return _read_album_index(index_file)


def _read_album_index(file_path: Path):
    try:
        return AlbumIndex.read_from_file(file_path)
    except AlbumIndexError as err:
        logger.error(str(err))
    except Exception:
        logger.exception("Failed reading album index at %s", file_path)
