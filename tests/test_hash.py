import re

import pytest

from mopidy_kitchen.hash import make_hash


def test_make_hash_string():
    result = make_hash("foo")

    assert re.match("^[0-9a-f]{32}$", result)


def test_make_hash_empty():
    result = make_hash("")

    assert re.match("^[0-9a-f]{32}$", result)


def test_make_hash_none():
    with pytest.raises(TypeError) as e_info:
        make_hash(None)

    assert str(e_info.value) == "Not a string: None"
