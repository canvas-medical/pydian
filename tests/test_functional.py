import pytest
from pydian.functional import first_of


def test_first_of() -> None:
    # For each test case, tuple format: (input, expected_output)
    test_cases = [
        (["a", None, "b"], "a"),
        ([None, "a", "b"], "a"),
        ([None, None, None], None),
        ([], None),
    ]

    for incoming, expected_output in test_cases:
        assert first_of(incoming) == expected_output

    first_n_test_cases = [
        (["a", None, "b"], 2, ["a", "b"]),
        ([None, "a", "b"], 2, ["a", "b"]),
        ([None, "a", "b"], 1, ["a"]),
        ([None, "a", "b"], 3, ["a", "b"]),
        ([None, None, None], 3, None),
        ([], 1, None),
    ]

    for incoming, first_n, expected_output in first_n_test_cases:
        assert first_of(incoming, keep_n=first_n) == expected_output
