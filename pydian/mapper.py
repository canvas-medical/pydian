from typing import Any

from .dicts import nested_delete
from .lib.util import remove_empty_values
from .types import DROP, MappingFunc


class Mapper:
    def __init__(
        self,
        map_fn: MappingFunc,
        remove_empty: bool = True,
    ) -> None:
        self.map_fn = map_fn
        self.remove_empty = remove_empty

    def __call__(self, source: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """
        Calls `map_fn` and then performs postprocessing into the result dict.
        """
        res = self.map_fn(source, **kwargs)

        # Handle any DROP-flagged values
        keys_to_drop = self._get_keys_to_drop_set(res)
        if keys_to_drop:
            res = nested_delete(res, keys_to_drop)

        # Remove empty values
        if self.remove_empty:
            res = remove_empty_values(res)

        return res

    def _get_keys_to_drop_set(self, source: dict[str, Any], key_prefix: str = "") -> set[str]:
        """
        Recursively finds all keys where a DROP object is found.
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
                        elif isinstance(item, DROP):
                            res.add(indexed_keypath)
                case DROP() as v:
                    res.add(curr_key)
        return res
