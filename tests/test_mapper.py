from typing import Any

import pytest

from pydian import DROP, Mapper, get


def test_drop(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "CASE_parent_keep": {
                "CASE_curr_drop": {
                    "a": get(m, "notFoundKey", drop_level=DROP.THIS_OBJECT),
                    "b": "someValue",
                },
                "CASE_curr_keep": {"id": get(m, "data.patient.id", drop_level=DROP.THIS_OBJECT)},
            },
            "CASE_list": [get(m, "notFoundKey", drop_level=DROP.THIS_OBJECT)],
            "CASE_list_of_objects": [
                {"a": get(m, "notFoundKey", drop_level=DROP.PARENT), "b": "someValue"},
                {"a": "someValue", "b": "someValue"},
            ],
        }

    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {"CASE_parent_keep": {"CASE_curr_keep": {"id": get(source, "data.patient.id")}}}


def test_drop_out_of_bounds(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "parent": {
                "CASE_no_grandparent": get(m, "notFoundKey", drop_level=DROP.GREATGRANDPARENT)
            }
        }

    mapper = Mapper(mapping)
    with pytest.raises(RuntimeError):
        _ = mapper(source)


def test_drop_exact_level(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "parent": {"CASE_has_parent_object": get(m, "notFoundKey", drop_level=DROP.PARENT)},
            "other_data": 123,
        }

    mapper = Mapper(mapping)
    res = mapper(source)
    assert res == {}
