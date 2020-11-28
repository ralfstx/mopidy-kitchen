from mopidy_kitchen.search_index import SearchIndex


def test_finds_all_matches():
    index = SearchIndex()

    index.add("foo bar", "r1")
    index.add("foo bar", "r2")
    index.add("bar baz", "r3")

    assert index.find("foo") == {"r1", "r2"}


def test_finds_matches_in_range():
    index = SearchIndex()

    index.add("abc", "r1")
    index.add("baa", "r2")
    index.add("bab", "r3")
    index.add("bba", "r4")
    index.add("bbb", "r5")
    index.add("bcd", "r6")

    assert index.find("ba") == {"r2", "r3"}
    assert index.find("bb") == {"r4", "r5"}


def test_finds_exact_matches():
    index = SearchIndex()

    index.add("fo", "r1")
    index.add("foo", "r2")
    index.add("fooo", "r3")
    index.add("oo", "r4")

    assert index.find("foo", exact=True) == {"r2"}
    assert index.find("fooo", exact=True) == {"r3"}
    assert index.find("fool", exact=True) == set()
