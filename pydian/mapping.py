from benedict import benedict
from typing import Any, Callable
from pydian.lib.util import remove_empty_values
from pydian.lib.dict import get, nested_delete
from pydian.lib.enums import RelativeObjectLevel as ROL

# TODO: Make this a wrapper around benedict
class DictWrapper(benedict):
    def get(self, key: str, default: Any = None, then: Callable | None = None, drop_rol: ROL | None = None) -> Any:
        if '*' in key:
            return get(self, key, default, then, drop_rol)
        res = super().get(key, default)
        if then:
            res = then(res)
        if res is None and drop_rol:
            res = drop_rol
        return res

    def __getitem__(self, key: str) -> Any:
        res = self.get(key)
        if res is None:
            raise KeyError(f'{key}')
        return res
    

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

    def __call__(self, source: dict, **kwargs: Any) -> dict:
        try:
            if type(source) == dict:
                source = DictWrapper(source)
            res = self.map_fn(source, **kwargs)
            assert issubclass(type(res), dict)
        except Exception as e:
            raise RuntimeError(f'Failed to call {self.map_fn} on source data. Error: {e}')

        if type(res) == dict:
            res = DictWrapper(res)

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
            if issubclass(type(v), dict):
                self._add_rol_keys_to_drop(k_set, v, curr_nesting)
            elif type(v) == list:
                for i, item in enumerate(v):
                    indexed_nesting = f'{curr_nesting}[{i}]'
                    if issubclass(type(item), dict):
                        self._add_rol_keys_to_drop(k_set, item, indexed_nesting)
                    elif type(v) == ROL:
                        k_set.add(indexed_nesting)
            elif type(v) == ROL:
                k_set.add(curr_nesting)
