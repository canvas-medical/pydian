from enum import Enum


class DeleteRelativeObjectPlaceholder(Enum):
    """
    A DeleteRelativeObjectPlaceholder (abbrv. DROP) is a placeholder object 
      that indicates the object relative to the current value should be 
      dropped. An "object" in this context is a dict or a list.

    Examples:

    {   <-- Grandparent (rel to _value)
        'A': {   <-- Parent (rel to _value)
            'B': {      <-- Current (rel to _value)
                'C': _value
            }
        }
    }

    {   <-- Grandparent (rel to _value1 and _value2)
        'A': [  <-- Parent (rel to _value1 and _value2)
            {       <-- Current (rel to _value1)
                'B': _value1
            },
            {       <-- Current (rel to _value2)
                'B': _value2
            }
        ]
    }
    """

    CURRENT_OBJECT = -1
    PARENT = -2
    GRANDPARENT = -3
    GREATGRANDPARENT = -4
