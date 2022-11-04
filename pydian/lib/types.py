from enum import Enum
from typing import Any, Callable, TypeAlias

ApplyFunc: TypeAlias = Callable[[Any], Any]
ConditionalCheck: TypeAlias = Callable[[Any], bool]
MappingFunc: TypeAlias = Callable[..., dict[str, Any]]


class DROP(Enum):
    """
    A DeleteRelativeObjectPlaceholder (abbrv. DROP) is a placeholder object that indicates
      the object relative to the current value should be dropped. An "object" in this context
      is a dict or a list.

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


class KEEP:
    """
    A value wrapped in a KEEP object should be ignored by the Mapper class when removing values.

    Partial keeping is _not_ supported (i.e. a KEEP object within an object to be DROP-ed).
    """

    def __init__(self, v: Any):
        self.value = v
