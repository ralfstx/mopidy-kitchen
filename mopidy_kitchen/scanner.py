import logging
from pathlib import Path
from typing import List

from .index_files import AlbumIndex, StationIndex, IndexFileError

logger = logging.getLogger(__name__)


def scan_dir(root_dir: Path):
    root = Path(root_dir).resolve()
    if not root.is_dir():
        logger.error("Not a directory: %s", root)
        return []
    found = []
    _scan_dir(root, found)
    return sorted(found, key=lambda a: a.name)


def _scan_dir(dir: Path, found: List[AlbumIndex]):
    index_file = dir / "index.json"
    station_file = dir / "station.json"
    if index_file.is_file():
        album = _read_album_index(index_file)
        if album:
            found.append(album)
    elif station_file.is_file():
        station = _read_station_index(station_file)
        if station:
            found.append(station)
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
    except IndexFileError as err:
        logger.error(str(err))
    except Exception:
        logger.exception("Failed reading album index at %s", file_path)


def _read_station_index(file_path: Path):
    try:
        return StationIndex.read_from_file(file_path)
    except IndexFileError as err:
        logger.error(str(err))
    except Exception:
        logger.exception("Failed reading station index at %s", file_path)
