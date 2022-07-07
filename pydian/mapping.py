from benedict import benedict
from copy import deepcopy
from typing import Any, Callable
from pydian.lib.util import remove_empty_values
from pydian.dict import get, _nested_delete
from pydian.lib.enums import DeleteRelativeObjectPlaceholder as DROP


class DictWrapper(benedict):
    def get(
        self,
        key: str,
        default: Any = None,
        apply: Callable | None = None,
        drop_level: DROP | None = None,
    ) -> Any:
        if "*" in key:
            return get(self, key, default, apply, drop_level)
        res = super().get(key, default)
        if apply:
            res = apply(res)
        if res is None and drop_level:
            res = drop_level
        return res

    def __getitem__(self, key: str) -> Any:
        res = self.get(key)
        if res is None:
            raise KeyError(f"{key}")
        return res


class Mapper:
    def __init__(
        self,
        map_fn: Callable[[dict], dict],
        remove_empty: bool = False,
    ) -> None:
        """
        Calls `map_fn` and then performs postprocessing into the final dict
        """
        self.map_fn = map_fn
        self.remove_empty = remove_empty

    def __call__(self, source: dict, **kwargs: Any) -> dict:
        res = self.map_fn(source, **kwargs)
        if not isinstance(res, dict):
            raise TypeError(
                f"Expected {self.map_fn} output to return a dict, got type: {type(res)}"
            )
        res = DictWrapper(res)

        # Unpack Tuple-based keys
        # NOTE: `benedict` assumes tuple keys are intended as a keypath,
        #       so to get around this we manipulate the underlying dict
        res = self._unpack_tuple_keys(res.dict())

        # Handle any DROP-flagged values
        keys_to_drop = self._get_keys_to_drop_set(res)

        # Remove the keys to drop
        for k in keys_to_drop:
            res = _nested_delete(res, k)

        # Remove empty values
        if self.remove_empty:
            res = remove_empty_values(res)

        return res

    def _unpack_tuple_keys(self, source: dict) -> dict:
        """
        Updates tuple key, tuple value pairs into individual key-value pairs
        """
        # NOTE: we iterate over a deepcopy since
        #       we modify the original dict while looping.
        #       So for the recursive subcall, we want the
        #       original object pointer `res[k]` as opposed to `v`
        res = deepcopy(source)
        for k, v in source.items():
            if isinstance(k, tuple):
                # Update the original dict
                vals = res.pop(k)
                if vals:
                    try:
                        assert isinstance(vals, (tuple, dict)) and len(k) == len(vals)
                    except Exception:
                        raise RuntimeError(
                            f"For tuple-based keys, expecting tuple or dict matching {k}, got: {vals}"
                        )
                    for i, new_key in enumerate(k):
                        # Insert back at the same level
                        if isinstance(vals, tuple):
                            res[new_key] = vals[i]
                        elif isinstance(vals, dict):
                            res[new_key] = vals[new_key]
            # Keep recursing as necessary
            elif issubclass(type(v), dict):
                res[k] = self._unpack_tuple_keys(res[k])
            elif isinstance(v, list):
                res[k] = [
                    self._unpack_tuple_keys(obj) if issubclass(type(obj), dict) else obj
                    for obj in res[k]
                ]
        return res

    def _get_keys_to_drop_set(self, source: dict, key_prefix: str = "") -> set:
        """
        Finds all keys where an DROP is found
        """
        res = set()
        for k, v in source.items():
            curr_key = f"{key_prefix}.{k}" if key_prefix != "" else k
            if issubclass(type(v), dict):
                res |= self._get_keys_to_drop_set(v, curr_key)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    indexed_keypath = f"{curr_key}[{i}]"
                    if issubclass(type(item), dict):
                        res |= self._get_keys_to_drop_set(item, indexed_keypath)
                    elif isinstance(v, DROP):
                        res.add(indexed_keypath)
            elif isinstance(v, DROP):
                res.add(curr_key)
        return res
