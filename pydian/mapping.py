
from typing import Any, Callable
from pydian.lib.util import remove_empty_values
from pydian.lib.dict import single_get, nested_get, nested_delete

class DictWrapper(dict):
    def gets(self, key: str, default: Any = None, then: Callable | None = None) -> Any:
        res = single_get(self, key, default)
        if res and callable(then):
            try:
                res = then(res)
            except Exception as e:
                raise RuntimeError(f'`then` callable failed when getting key: {key}, error: {e}')
        return res

    def getn(self, key: str, default: Any = None, then: Callable | None = None) -> Any:
        res = nested_get(self, key, default)
        if res and callable(then):
            try:
                res = then(res)
            except Exception as e:
                raise RuntimeError(f'`then` callable failed when getting key: {key}, error: {e}')
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

    def run(self, source: dict) -> dict:
        try:
            res = self.map_fn(DictWrapper(source))
            assert type(res) == dict
        except Exception as e:
            raise RuntimeError(f'Failed to call {self.map_fn} on source data. Error: {e}')
        
        # Handle conditional drop logic
        keys_to_drop = set()
        for k, v in self.conditionally_drop.items():
            if nested_get(res, k) is None:
                if type(v) == str:
                    keys_to_drop.add(v) 
                else:
                    keys_to_drop |= v
        for k in keys_to_drop:
            if nested_get(res, k):
                res = nested_delete(res, k)

        # Remove empty values
        if self.remove_empty:
            res = remove_empty_values(res)

        return res