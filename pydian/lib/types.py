from enum import Enum
from typing import Any, Callable, TypeAlias

ApplyFunc: TypeAlias = Callable[[Any], Any]
ConditionalCheck: TypeAlias = Callable[[Any], bool]
MappingFunc: TypeAlias = Callable[..., dict[str, Any]]


class DROP(Enum):
    """
    A DeleteRelativeObjectPlaceholder (abbrv. DROP) is a placeholder object
      that indicates the object relative to the current value should be
      dropped. An "object" in this context is a dict or a list.

    Examples:

    {   <-- Grandparent (rel to _value)
        'A': {   <-- Parent (rel to _value)
            'B': {      <-- This Object (rel to _value)
                'C': _value
            }
        }
    }

    {   <-- Grandparent (rel to _value1 and _value2)
        'A': [  <-- Parent (rel to _value1 and _value2)
            {       <-- This Object (rel to _value1)
                'B': _value1
            },
            {       <-- This Object (rel to _value2)
                'B': _value2
            }
        ]
    }
    """

    THIS_OBJECT = -1
    PARENT = -2
    GRANDPARENT = -3
    GREATGRANDPARENT = -4


class EMPTY(Enum):
    """
    An EMPTY enum is an intentional declaration in a data mapping that the specific "empty" value
      should be intentionally kept by the Mapper class.
    """

    @staticmethod
    def _get_immutable_enum_value(uid: str) -> Any:
        """Dynamically gets the enum value (simulates immutability)"""
        match uid:
            case "dict":
                return dict()
            case "list":
                return list()
            case "str":
                return ""
            case _:
                raise RuntimeError(f"Unhandled EMPTY enum, got: {uid}")

    DICT = _get_immutable_enum_value("dict")
    LIST = _get_immutable_enum_value("list")
    STRING = _get_immutable_enum_value("str")
    NONE = None
