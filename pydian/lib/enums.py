from enum import Enum

TO_DELETE_KEY = 'to_delete'
CURRENT_NESTING_KEY = 'current_nesting'
class RelativeObjectLevel(Enum):
    CURRENT = 0
    PARENT = 1
    GRANDPARENT = 2
    GREATGRANDPARENT = 3
    # ENTIRE_OBJECT = 100_000

class ToDeleteInfo:
    def __init__(self, key: str, rol: RelativeObjectLevel, level: int):
        self.key = key
        self.rol = rol
        self.level = level
        self.delete_threshold = self.level - self.rol.value
