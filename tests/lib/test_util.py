from pydian.lib.util import remove_empty_values, split_key


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


def test_split_key() -> None:
    # Test regular keys
    assert split_key("a.b.c") == ["a", "b", "c"]
    assert split_key("a[*].b.c[*]") == ["a[*]", "b", "c[*]"]
    assert split_key("a") == ["a"]
    assert split_key("") == [""]

    # Test tuples. Variance in whitespace is intentional
    assert split_key("a.b.(c, d)") == ["a", "b", "c,d"]
    assert split_key("a.b.(c, d).e") == ["a", "b", "c,d", "e"]
    assert split_key("a.b.(c,d).e.(f, g)") == ["a", "b", "c,d", "e", "f,g"]
    assert split_key("(c, d).e.(f,g)") == ["c,d", "e", "f,g"]

    # Test nested keys within the tuples
    assert split_key("a.b.(c.first,d.second).e") == ["a", "b", "c.first,d.second", "e"]
    assert split_key("(c.first,d.second).e.(f.third, g.fourth)") == [
        "c.first,d.second",
        "e",
        "f.third,g.fourth",
    ]
