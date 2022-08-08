from typing import Any

import pytest


@pytest.fixture(scope="function")
def simple_data() -> dict[str, Any]:
    return {
        "data": {"patient": {"id": "abc123", "active": True}},
        "list_data": [
            {"patient": {"id": "def456", "active": True}},
            {"patient": {"id": "ghi789", "active": False}},
        ],
    }


@pytest.fixture(scope="function")
def nested_data() -> dict[str, Any]:
    return {
        "data": [
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
        ]
    }
