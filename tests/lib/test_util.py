from pydian.lib.util import remove_empty_values, split_key_with_tuples


def test_remove_empty_values() -> None:
    # List cases
    assert remove_empty_values([[], {}]) == []
    assert remove_empty_values(["a", [], {}, "", None]) == ["a"]
    # Dict cases
    assert remove_empty_values({"empty_list": [], "empty_dict": {}}) == {}
    assert remove_empty_values({"empty_list": [], "empty_dict": {}, "a": "b"}) == {"a": "b"}
    # Nested cases
    assert remove_empty_values([{}, ["", None], [{"empty": {"dict": {"key": None}}}]]) == []
    assert remove_empty_values({"empty_list": [{}, {}, {}], "empty_dict": {"someKey": {}}}) == {}


def test_split_key_with_tuples() -> None:
    # Test tuples. Variance in whitespace is intentional
    assert split_key_with_tuples("a.b.(c, d)") == ["a", "b", "c,d"]
    assert split_key_with_tuples("a.b.(c, d).e") == ["a", "b", "c,d", "e"]
    assert split_key_with_tuples("a.b.(c,d).e.(f, g)") == ["a", "b", "c,d", "e", "f,g"]
    assert split_key_with_tuples("(c, d).e.(f,g)") == ["c,d", "e", "f,g"]

    # Test nested keys within the tuples
    assert split_key_with_tuples("a.b.(c.first,d.second).e") == ["a", "b", "c.first,d.second", "e"]
    assert split_key_with_tuples("(c.first,d.second).e.(f.third, g.fourth)") == [
        "c.first,d.second",
        "e",
        "f.third,g.fourth",
    ]
