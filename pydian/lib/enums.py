from enum import Enum

class RelativeObjectLevel(Enum):
    """
    A RelativeObjectLevel (abbrv. ROL) is the object relative to 
    the current value. An "object" in this context is a dict or a list.
    Thus, CURRENT is the object containing the value, PARENT is the
    parent object containing the current object (if it exists), etc.

    Examples:

    {   <-- Grandparent
        'A': {   <-- Parent
            'B': {      <-- Current (rel to _value)
                'C': _value
            } 
        }
    }

    {   <-- Grandparent
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
    CURRENT = -1
    PARENT = -2
    GRANDPARENT = -3
    GREATGRANDPARENT = -4
