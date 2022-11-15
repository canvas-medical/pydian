from pydian.lib.util import flatten_list, remove_empty_values


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


def test_flatten_list() -> None:
    assert flatten_list([[1], [2], [3]]) == [1, 2, 3]
    assert flatten_list([[1, 2], [3, 4], [5, 6]]) == [1, 2, 3, 4, 5, 6]
    # assert flatten_list([[[1], 2], [[3], 4], [[5], 6]) == [1, 2, 3, 4, 5, 6]
    assert flatten_list([[[1], [2]], [[3], [4]], [[5], [6]]]) == [1, 2, 3, 4, 5, 6]
