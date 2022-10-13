from copy import deepcopy
from typing import Any

import pydian.partials as P


def test_get(simple_data: dict[str, Any]) -> None:
    source = simple_data
    FAIL_DEFAULT_STR = "n/a"
    res = {
        "CASE_successful_get": P.get("data.patient.id", apply=str.upper)(source),
        "CASE_default_get": P.get("something_not_there", default=FAIL_DEFAULT_STR, apply=str.upper)(
            source
        ),
        "CASE_failed_get": P.get("something_not_there", apply=str.upper)(source),
    }
    assert res == {
        "CASE_successful_get": str.upper(source["data"]["patient"]["id"]),
        "CASE_default_get": str.upper(FAIL_DEFAULT_STR),
        "CASE_failed_get": None,
    }


def test_do() -> None:
    def some_function(first: str, second: int) -> str:
        return f"Look {first}, I have an int {second}!"

    kwargs = {"second": 100}  # Passes in any order
    str_param_fn_1 = P.do(some_function, 100)  # Partially applies starting at second parameter
    str_param_fn_2 = P.do(some_function, **kwargs)
    assert some_function("Ma", 100) == str_param_fn_1("Ma") == str_param_fn_2("Ma")

    # Test stdlib wrappers
    EXAMPLE_STR = "Some String"
    assert P.do(str.replace, "S", "Z")(EXAMPLE_STR) == EXAMPLE_STR.replace("S", "Z")
    assert P.do(str.startswith, "S")(EXAMPLE_STR) == EXAMPLE_STR.startswith("S")
    assert P.do(str.endswith, "S")(EXAMPLE_STR) == EXAMPLE_STR.endswith("S")


def test_generic_apply_wrappers() -> None:
    n = 100
    assert P.add(1)(n) == n + 1
    assert P.subtract(1)(n) == n - 1
    assert P.multiply(10)(n) == n * 10
    assert P.divide(10)(n) == n / 10

    l = [1, 2, 3]
    assert P.add([4])(l) == l + [4]
    assert P.multiply(3)(l) == l * 3


def test_generic_conditional_wrappers() -> None:
    value = {"a": "b", "c": "d"}
    copied_value = deepcopy(value)
    example_key = "a"
    assert P.equals(copied_value)(value) == (value == copied_value)
    assert P.not_equal(copied_value)(value) == (value != copied_value)
    assert P.equivalent(copied_value)(value) == (value is copied_value)
    assert P.not_equivalent(copied_value)(value) == (value is not copied_value)
    assert P.contains(example_key)(copied_value) == (example_key in value)
    assert P.not_contains(example_key)(copied_value) == (example_key not in value)
    assert P.contained_in(copied_value)(example_key) == (example_key in value)
    assert P.not_contained_in(copied_value)(example_key) == (example_key not in value)


def test_iterable_wrappers() -> None:
    value = [1, 2, 3, 4, 5]

    assert P.keep(1)(value) == value[:1]
    assert P.keep(50)(value) == value[:50]
    assert P.index(0)(value) == value[0]
    assert P.index(1)(value) == value[1]
    assert P.index(-1)(value) == value[-1]
    assert P.index(-3)(value) == value[-3]


def test_stdlib_wrappers() -> None:
    EXAMPLE_LIST = ["a", "b", "c"]
    assert P.map_to_list(str.upper)(EXAMPLE_LIST) == ["A", "B", "C"]
    assert P.filter_to_list(P.equals("a"))(EXAMPLE_LIST) == ["a"]
