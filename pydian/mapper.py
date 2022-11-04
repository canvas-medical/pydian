from typing import Any

from .dicts import drop_keys, impute_enum_values
from .lib.types import DROP, KEEP, MappingFunc
from .lib.util import get_keys_containing_class, remove_empty_values


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
        keys_to_drop = get_keys_containing_class(res, DROP)
        if keys_to_drop:
            res = drop_keys(res, keys_to_drop)

        # Remove empty values
        if self.remove_empty:
            res = remove_empty_values(res)

        # Impute KEEP values with corresponding value
        keys_to_impute = get_keys_containing_class(res, KEEP)
        if keys_to_impute:
            res = impute_enum_values(res, keys_to_impute)

        return res
