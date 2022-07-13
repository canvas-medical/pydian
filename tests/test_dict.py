from copy import deepcopy
from typing import Any

import pytest

from pydian import get
from pydian.dict import _nested_delete


@pytest.fixture
def nested_data() -> dict[str, Any]:
    return {
        "const_data": 123,
        "nested_data": {"a": {"b": "c", "d": "e"}},
        "list_data": [
            {
                "patient": {
                    "id": "abc123",
                    "active": True,
                    "ints": [1, 2, 3],
                    "dicts": [{"num": 1}, {"num": 2}],
                }
            },
            {
                "patient": {
                    "id": "def456",
                    "active": False,
                    "ints": [4, 5, 6],
                    "dicts": [{"num": 3}, {"num": 4}],
                }
            },
            {
                "patient": {
                    "id": "ghi789",
                    "active": True,
                    "ints": [7, 8, 9],
                    "dicts": [{"num": 5}, {"num": 6}],
                }
            },
            {
                "patient": {
                    "id": "jkl101112",
                    "active": True,
                    # "ints" is deliberately missing
                    "dicts": [{"num": 7}],
                }
            },
        ],
    }


def test_nested_delete(nested_data: dict[str, Any]) -> None:
    orig = nested_data
    source = deepcopy(nested_data)
    keys_to_drop = {
        "list_data[0].patient",
        "list_data[2].patient.id",
        "list_data[3].patient.active",
    }

    res = _nested_delete(source, keys_to_drop)
    for k in keys_to_drop:
        assert get(res, k) is None
        assert get(orig, k) is not None
