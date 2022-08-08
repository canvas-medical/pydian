from typing import Any

import pytest

from pydian import DROP, Mapper, get


def test_get(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "CASE_constant": 123,
            "CASE_single": get(m, "data"),
            "CASE_nested": get(m, "data.patient.id"),
            "CASE_nested_as_list": [get(m, "data.patient.active")],
            "CASE_modded": get(m, "data.patient.id", apply=lambda s: s + "_modified"),
            "CASE_index_list": {
                "first": get(m, "list_data[0].patient"),
                "second": get(m, "list_data[1].patient"),
                "out_of_bounds": get(m, "list_data[2].patient"),
            },
        }

    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {
        "CASE_constant": 123,
        "CASE_single": source.get("data"),
        "CASE_nested": source["data"]["patient"]["id"],
        "CASE_nested_as_list": [source["data"]["patient"]["active"]],
        "CASE_modded": source["data"]["patient"]["id"] + "_modified",
        "CASE_index_list": {
            "first": source["list_data"][0]["patient"],
            "second": source["list_data"][1]["patient"],
        },
    }


def test_nested_get(nested_data: dict[str, Any]) -> None:
    source = nested_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "CASE_constant": 123,
            "CASE_unwrap_active": get(m, "data[*].patient.active"),
            "CASE_unwrap_id": get(m, "data[*].patient.id"),
            "CASE_unwrap_list": get(m, "data[*].patient.ints"),
            "CASE_unwrap_list_twice": get(m, "data[*].patient.ints[*]"),
            "CASE_unwrap_list_dict": get(m, "data[*].patient.dicts[*].num"),
            "CASE_unwrap_list_dict_twice": get(m, "data[*].patient.dicts[*].num[*]"),
            # Expect this to get removed
            "CASE_bad_key": {
                "single": get(m, "missing.key"),
                "unwrap": get(m, "missing[*].key"),
                "unwrap_twice": get(m, "missing[*].key[*].here"),
                "overindex": get(m, "data[8888].patient"),
            },
        }

    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {
        "CASE_constant": 123,
        "CASE_unwrap_active": [True, False, True, True],
        "CASE_unwrap_id": ["abc123", "def456", "ghi789", "jkl101112"],
        "CASE_unwrap_list": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        "CASE_unwrap_list_twice": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "CASE_unwrap_list_dict": [[1, 2], [3, 4], [5, 6], [7]],
        "CASE_unwrap_list_dict_twice": [1, 2, 3, 4, 5, 6, 7],
    }


def test_drop(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "CASE_parent_keep": {
                "CASE_curr_drop": {
                    "a": get(m, "notFoundKey", drop_level=DROP.THIS_OBJECT),
                    "b": "someValue",
                },
                "CASE_curr_keep": {
                    "id": get(m, "data.patient.id", drop_level=DROP.THIS_OBJECT)
                },
            },
            "CASE_list": [
                {"a": get(m, "notFoundKey", drop_level=DROP.PARENT), "b": "someValue"},
                {"a": "someValue", "b": "someValue"},
            ],
        }

    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {
        "CASE_parent_keep": {"CASE_curr_keep": {"id": get(source, "data.patient.id")}}
    }


def test_drop_out_of_bounds(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "parent": {
                "CASE_no_grandparent": get(
                    m, "notFoundKey", drop_level=DROP.GREATGRANDPARENT
                )
            }
        }

    mapper = Mapper(mapping)
    with pytest.raises(RuntimeError):
        _ = mapper(source)


def test_drop_exact_level(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "parent": {
                "CASE_has_parent_object": get(m, "notFoundKey", drop_level=DROP.PARENT)
            },
            "other_data": 123,
        }

    mapper = Mapper(mapping)
    res = mapper(source)
    assert res == {}