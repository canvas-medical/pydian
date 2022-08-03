from copy import deepcopy
from typing import Any

from pydian import get
from pydian.dicts import _nested_delete


def test_nested_delete(nested_data: dict[str, Any]) -> None:
    orig = nested_data
    source = deepcopy(nested_data)
    keys_to_drop = {
        "data[0].patient",
        "data[2].patient.id",
        "data[3].patient.active",
    }

    res = _nested_delete(source, keys_to_drop)
    for k in keys_to_drop:
        assert get(res, k) is None
        assert get(orig, k) is not None
