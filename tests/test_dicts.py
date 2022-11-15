from typing import Any

import pydian.partials as p
from pydian import Mapper, get
from pydian.dicts import drop_keys


def test_get(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "CASE_constant": 123,
            "CASE_single": get(m, "data"),
            "CASE_nested": get(m, "data.patient.id"),
            "CASE_nested_as_list": [get(m, "data.patient.active")],
            "CASE_modded": get(m, "data.patient.id", apply=lambda s: s + "_modified"),
        }

    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {
        "CASE_constant": 123,
        "CASE_single": source.get("data"),
        "CASE_nested": source["data"]["patient"]["id"],
        "CASE_nested_as_list": [source["data"]["patient"]["active"]],
        "CASE_modded": source["data"]["patient"]["id"] + "_modified",
    }


def test_get_index(simple_data: dict[str, Any]) -> None:
    source = simple_data

    def mapping(m: dict[str, Any]) -> dict[str, Any]:
        return {
            "first": get(m, "list_data[0].patient"),
            "second": get(m, "list_data[1].patient"),
            "out_of_bounds": get(m, "list_data[50].patient"),
            "negative_index": get(m, "list_data[-1].patient"),
            "slice": {
                "both": get(m, "list_data[1:3]"),
                "left": get(m, "list_data[1:]"),
                "right": get(m, "list_data[:2]"),
                "all": get(m, "list_data[:]"),
            },
        }

    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {
        "first": source["list_data"][0]["patient"],
        "second": source["list_data"][1]["patient"],
        "negative_index": source["list_data"][-1]["patient"],
        "slice": {
            "both": source["list_data"][1:3],
            "left": source["list_data"][1:],
            "right": source["list_data"][:2],
            "all": source["list_data"][:],
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
            "CASE_unwrap_list_twice": get(m, "data[*].patient.ints", flatten=True),
            "CASE_unwrap_list_dict": get(m, "data[*].patient.dicts[*].num"),
            "CASE_unwrap_list_dict_twice": get(m, "data[*].patient.dicts[*].num", flatten=True),
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


def test_drop_keys(nested_data: dict[str, Any]) -> None:
    source = nested_data
    keys_to_drop = {
        "data[0].patient",
        "data[2].patient.id",
        "data[3].patient.active",
    }
    res = drop_keys(source, keys_to_drop)
    for k in keys_to_drop:
        assert get(res, k) is None


def test_get_apply(simple_data: dict[str, Any]) -> None:
    source = simple_data
    OLD_STR, NEW_STR = "456", "FourFiveSix"
    single_apply = str.upper
    chained_apply = [str.upper, p.do(str.replace, OLD_STR, NEW_STR)]
    failed_chain_apply = [str.upper, lambda _: None, p.do(str.replace, OLD_STR, NEW_STR)]
    res = {
        "single_apply": get(source, "data.patient.id", apply=single_apply),
        "chained_apply": get(source, "list_data[0].patient.id", apply=chained_apply),
        "failed_chained_apply": get(source, "list_data[0].patient.id", apply=failed_chain_apply),
        "not_found": get(source, "data.notFoundKey", apply=chained_apply),
    }
    assert res == {
        "single_apply": str.upper(source["data"]["patient"]["id"]),
        "chained_apply": (str.upper(source["list_data"][0]["patient"]["id"])).replace(
            OLD_STR, NEW_STR
        ),
        "failed_chained_apply": None,
        "not_found": None,
    }


def test_get_only_if(simple_data: dict[str, Any]) -> None:
    source = simple_data
    KEY = "data.patient.id"
    passes_check = get(source, KEY, only_if=lambda s: str.startswith(s, "abc"), apply=str.upper)
    fails_check = get(source, KEY, only_if=lambda s: str.startswith(s, "000"), apply=str.upper)
    assert passes_check == source["data"]["patient"]["id"].upper()
    assert fails_check is None


def test_get_single_key_tuple(simple_data: dict[str, Any]) -> None:
    source = simple_data
    assert get(source, "data.patient.[id,active]") == [
        source["data"]["patient"]["id"],
        source["data"]["patient"]["active"],
    ]
    # Allow whitespace within parens
    assert get(source, "data.patient.[id, active]") == get(source, "data.patient.[id,active]")
    assert get(source, "data.patient.[id,active,missingKey]") == [
        source["data"]["patient"]["id"],
        source["data"]["patient"]["active"],
        None,
    ]
    # Expect list unwrapping to still work
    assert get(source, "list_data[*].patient.[id, active]") == [
        [p["patient"]["id"], p["patient"]["active"]] for p in source["list_data"]
    ]
    assert get(source, "list_data[*].patient.[id, active, missingKey]") == [
        [p["patient"]["id"], p["patient"]["active"], None] for p in source["list_data"]
    ]

    # Test default (expect at each tuple item on a failed get)
    STR_DEFAULT = "Missing!"
    assert get(source, "data.patient.[id, active, missingKey]", default=STR_DEFAULT) == [
        source["data"]["patient"]["id"],
        source["data"]["patient"]["active"],
        STR_DEFAULT,
    ]

    # Test apply
    assert (
        get(source, "data.patient.[id, active, missingKey]", apply=p.index(1))
        == source["data"]["patient"]["active"]
    )
    assert get(source, "data.patient.[id, active, missingKey]", apply=p.keep(2)) == [
        source["data"]["patient"]["id"],
        source["data"]["patient"]["active"],
    ]

    # Test only_if filtering
    assert get(source, "data.patient.[id, active, missingKey]", only_if=lambda _: False) == None


def test_get_nested_key_tuple(nested_data: dict[str, Any]) -> None:
    source = nested_data

    # Single item example
    single_item_example = source["data"][0]["patient"]["dicts"][0]
    assert get(source, "data[0].patient.dicts[0].[num, text]") == [
        single_item_example["num"],
        single_item_example["text"],
    ]
    assert get(source, "data[0].patient.dicts[0].[num,inner.msg]") == [
        single_item_example["num"],
        single_item_example["inner"]["msg"],
    ]

    # Multi-item example
    assert get(source, "data[*].patient.dict.[char, inner.msg]") == [
        [d["patient"]["dict"]["char"], d["patient"]["dict"]["inner"]["msg"]] for d in source["data"]
    ]

    # Multi-item on multi-[*] example
    assert get(source, "data[*].patient.dicts[*].[num, inner.msg]") == [
        [[obj["num"], obj["inner"]["msg"]] for obj in d["patient"]["dicts"]] for d in source["data"]
    ]
