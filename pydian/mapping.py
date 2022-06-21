
from typing import Any, Callable
from pydian.lib.util import remove_empty_values
from pydian.lib.dict import get, nested_delete
from pydian.lib.enums import RelativeObjectLevel as ROL

# TODO: Remove this? Not sure what value this could add (yet)
class DictWrapper(dict):
    def getn(self, key: str, default: Any = None, then: Callable | None = None, drop_rol: ROL | None = None) -> Any:
        return get(self, key, default, then, drop_rol)

class Mapper:
    def __init__(self, map_fn: Callable[['DictWrapper'], dict], remove_empty: bool = False, conditionally_drop: dict = {}) -> None:
        """
        The conditional drop dictionary will drop `value` if `key` evaluates to None, e.g.
        {
            'name.val': 'name'
        }
        Means if .get('name.val') == None, then the object at 'name' will be removed from the result

        This supports multiple keys, e.g.:
        {
            'name.val': {
                'name',
                'otherThing'
            }
        }
        Means if .get('name.val') == None, then both objects at 'name' and 'otherThing' will be removed
        """
        self.map_fn = map_fn
        self.remove_empty = remove_empty
        
        #  Validate the conditionally_drop dict
        for k, v in conditionally_drop.items():
            try:
                assert type(k) == str
                assert type(v) in {str, set}
            except Exception as e:
                raise TypeError(f'The conditionally_drop dict can only map `str->(str | set)`, got: {(k, v)}')
        self.conditionally_drop = conditionally_drop

    def __call__(self, source: dict) -> dict:
        try:
            res = self.map_fn(DictWrapper(source))
            assert type(res) == dict
        except Exception as e:
            raise RuntimeError(f'Failed to call {self.map_fn} on source data. Error: {e}')
        
        # Handle conditional drop dict logic
        keys_to_drop = set()
        for k, v in self.conditionally_drop.items():
            if get(res, k) is None:
                if type(v) == str:
                    keys_to_drop.add(v) 
                else:
                    keys_to_drop |= v

        # Handle any ROL-flagged values
        self._add_rol_keys_to_drop(keys_to_drop, res)

        # Remove the keys to drop
        for k in keys_to_drop:
            # Case: ROL received during runtime
            if type(get(res, k)) == ROL:
                rol = get(res, k)
                key_parts = k.split('.')
                # Split by list index as well, e.g. `some.key[1]`, the parent of `key[1]` is `key`, not `some`
                if '[' in k:
                    new_parts = []
                    for part in key_parts:
                        if '[' in part:
                            # Split by, then add back the bracket
                            s = part.split('[')
                            s[-1] = f'[{s[-1]}'
                            new_parts += s
                        else:
                            new_parts.append(part)
                    key_parts = new_parts
                # rol.value should be negative
                assert rol.value < 0
                new_key = '.'.join(key_parts[:rol.value])
                if new_key != '':
                    res = nested_delete(res, new_key)
            # Case: Specified in the Conditional update dict
            else:
                res = nested_delete(res, k)

        # Remove empty values
        if self.remove_empty:
            res = remove_empty_values(res)

        return res
    
    def _add_rol_keys_to_drop(self, k_set: set, msg: dict, key_prefix: str = '') -> None:
        """
        Searches `msg`, then takes each ROL object found and adds the 
          nested key where the ROL was found.

        The logic of which relative key to delete is handled elsewhere!
        """
        for k, v in msg.items():
            curr_nesting = f'{key_prefix}.{k}' if key_prefix != '' else k
            if type(v) == dict:
                self._add_rol_keys_to_drop(k_set, v, curr_nesting)
            elif type(v) == list:
                for i, item in enumerate(v):
                    indexed_nesting = f'{curr_nesting}[{i}]'
                    if type(item) == dict:
                        self._add_rol_keys_to_drop(k_set, item, indexed_nesting)
                    elif type(v) == ROL:
                        k_set.add(indexed_nesting)
            elif type(v) == ROL:
                k_set.add(curr_nesting)
