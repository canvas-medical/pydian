import pytest
from pydian.lib.dict import nested_delete
from pydian import get
from copy import deepcopy


@pytest.fixture
def nested_data() -> dict:
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
                    # 'ints' is deliberately missing
                    "dicts": [{"num": 7}],
                }
            },
        ],
    }


def test_nested_delete(nested_data: dict) -> dict:
    orig = nested_data
    source = deepcopy(nested_data)
    keys = (
        "list_data[0].patient",
        "list_data[2].patient.id",
        "list_data[3].patient.active",
    )
    for k in keys:
        res = nested_delete(source, k)
        assert get(res, k) == None
        assert get(orig, k) != None
    # Test [*] format
    source = deepcopy(nested_data)
    single_star_keys = ("list_data[*].patient.dicts",)
    for k in single_star_keys:
        res = nested_delete(source, k)
        assert len(get(res, k)) == len(get(orig, k))
        assert not any(get(res, k))
        assert any(get(orig, k))
    double_star_keys = ("list_data[*].patient.dicts[*].num",)
    for k in double_star_keys:
        res = nested_delete(source, k)
        assert len(get(res, k)) == len(get(orig, k))
        assert not any([any(l) for l in get(res, k)])
        assert any([any(l) for l in get(orig, k)])
