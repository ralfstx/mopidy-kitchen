from pathlib import Path
import json


def make_config(tmp_path: Path):
    data_dir = tmp_path.joinpath("data")
    data_dir.mkdir(exist_ok=True)
    media_dir = tmp_path.joinpath("media")
    media_dir.mkdir(exist_ok=True)
    return {
        "core": {"data_dir": str(data_dir)},
        "kitchen": {"media_dir": str(media_dir)},
    }


def make_album(album_path: Path, index=None):
    album_path.mkdir(parents=True, exist_ok=True)
    index_json = index if isinstance(index, str) else json.dumps(index)
    with open(album_path / "index.json", mode="w") as f:
        f.write(index_json)


def make_station(station_path: Path, index=None):
    station_path.mkdir(parents=True, exist_ok=True)
    station_json = index if isinstance(index, str) else json.dumps(index)
    with open(station_path / "station.json", mode="w") as f:
        f.write(station_json)


def make_image(image_path: Path, data=None):
    with open(image_path, mode="w") as f:
        f.write(data or "")


EXAMPLE_ALBUM = {
    "name": "John Doe - One Day",
    "artist": "John Doe",
    "title": "One Day",
    "discs": [
        {
            "path": "01",
            "tracks": [
                {"path": "01.ogg", "title": "The Morning", "length": 101},
                {"path": "02.ogg", "title": "The Afternoon", "length": 202},
            ],
        },
        {
            "path": "02",
            "tracks": [
                {"path": "01.ogg", "title": "The Evening", "length": 303},
            ],
        },
    ],
}
