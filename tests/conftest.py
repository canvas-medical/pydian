from typing import Any

import pytest


@pytest.fixture(scope="function")
def simple_data() -> dict[str, Any]:
    return {
        "data": {"patient": {"id": "abc123", "active": True}},
        "list_data": [
            {"patient": {"id": "abc123", "active": True}},
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
                    "dict": {"char": "a", "inner": {"msg": "A!"}},
                    "dicts": [
                        {"num": 1, "text": "one", "inner": {"msg": "One!"}},
                        {"num": 2, "text": "two", "inner": {"msg": "Two!"}},
                    ],
                }
            },
            {
                "patient": {
                    "id": "def456",
                    "active": False,
                    "ints": [4, 5, 6],
                    "dict": {"char": "b", "inner": {"msg": "B!"}},
                    "dicts": [
                        {"num": 3, "text": "three", "inner": {"msg": "Three!"}},
                        {"num": 4, "text": "four", "inner": {"msg": "Four!"}},
                    ],
                }
            },
            {
                "patient": {
                    "id": "ghi789",
                    "active": True,
                    "ints": [7, 8, 9],
                    "dict": {"char": "c", "inner": {"msg": "C!"}},
                    "dicts": [
                        {"num": 5, "text": "five", "inner": {"msg": "Five!"}},
                        {"num": 6, "text": "six", "inner": {"msg": "Six!"}},
                    ],
                }
            },
            {
                "patient": {
                    "id": "jkl101112",
                    "active": True,
                    # 'ints' is deliberately missing
                    "dict": {"char": "d", "inner": {"msg": "D!"}},
                    "dicts": [{"num": 7, "text": "seven", "inner": {"msg": "Seven!"}}],
                }
            },
        ]
    }
