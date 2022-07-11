from benedict import benedict
from copy import deepcopy
from typing import Any, Callable, Mapping
from pydian.lib.util import remove_empty_values
from pydian.dict import _nested_delete
from pydian.lib.enums import DeleteRelativeObjectPlaceholder as DROP


class Mapper:
    def __init__(
        self,
        map_fn: Callable[[Mapping, ...], dict],
        remove_empty: bool = False,
    ) -> "Mapper":
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

        # Handle any DROP-flagged values
        keys_to_drop = self._get_keys_to_drop_set(res)

        # Remove the keys to drop
        for k in keys_to_drop:
            res = _nested_delete(res, k)

        # Remove empty values
        if self.remove_empty:
            res = remove_empty_values(res)

        return res

    def _get_keys_to_drop_set(self, source: dict, key_prefix: str = "") -> set:
        """
        Finds all keys where an DROP is found
        """
        res = set()
        for k, v in source.items():
            curr_key = f"{key_prefix}.{k}" if key_prefix != "" else k
            match v:
                case dict() as v:
                    res |= self._get_keys_to_drop_set(v, curr_key)
                case list() as v:
                    for i, item in enumerate(v):
                        indexed_keypath = f"{curr_key}[{i}]"
                        if isinstance(item, dict):
                            res |= self._get_keys_to_drop_set(item, indexed_keypath)
                        elif isinstance(v, DROP):
                            res.add(indexed_keypath)
                case DROP() as v:
                    res.add(curr_key)
        return res
