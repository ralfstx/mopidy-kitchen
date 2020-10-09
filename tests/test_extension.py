from mopidy import config

from mopidy_kitchen import Extension


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert "[kitchen]" in config
    assert "enabled = true" in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()

    assert "media_dir" in schema
    assert type(schema.get("media_dir")) == config.Path
