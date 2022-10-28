import re
from collections import deque
from itertools import chain
from typing import Any, Iterable, Sequence, TypeVar

from .lib.types import DROP, KEEP, ApplyFunc, ConditionalCheck


def get(
    source: dict[str, Any],
    key: str,
    default: Any = None,
    apply: ApplyFunc | Iterable[ApplyFunc] | None = None,
    only_if: ConditionalCheck | None = None,
    drop_level: DROP | None = None,
) -> Any:
    """
    Gets a value from the source dictionary using a `.` syntax.
    Handles None-checking (instead of raising error, returns default).

    `key` notes:
     - Use `.` to chain gets
     - Index into lists, e.g. `[0]`, `[-1]`
     - Iterate through and "unwrap" a list using `[*]`

    Use `apply` to safely chain an operation on a successful get.

    Use `only_if` to conditionally decide if the result should be kept + `apply`-ed.

    Use `drop_level` to specify conditional dropping if get results in None.
    """
    res = _nested_get(source, key.split("."), default)

    if res is not None and only_if:
        res = res if only_if(res) else None

    if res is not None and apply:
        if not isinstance(apply, Iterable):
            apply = (apply,)
        for fn in apply:
            try:
                res = fn(res)
            except Exception as e:
                raise RuntimeError(f"`apply` call {fn} failed for value: {res} at key: {key}, {e}")
            if res is None:
                break

    if drop_level and res is None:
        res = drop_level
    return res


REGEX_INDEX = re.compile(r"(.*)\[(-?\d+|\*)\]$")


def _single_get(source: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Gets single item, supports int indexing, e.g. `someKey[0]`
    """
    if key.endswith("]"):
        if match := REGEX_INDEX.fullmatch(key):
            key_part = match.group(1)
            index_part = match.group(2)
            if index_part == "*":
                return _handle_ending_star_unwrap(source.get(key_part))
            values = source.get(key_part)
            if values is None:
                values = []
            try:
                return values[int(index_part)]
            except IndexError:
                return default
    return source.get(key, default)


def _nested_get(source: dict[str, Any], key_list: list[str], default: Any = None) -> Any:
    """
    Expects `.`-delimited string and tries to get the item in the dict.

    If the dict contains an array, the correct index is expected, e.g. for a dict d:
        d.a.b[0]
      will try d['a']['b'][0], where b should be an array with at least 1 item.


    If [*] is passed, then that means get into each object in the list. E.g. for a list l:
        l[*].a.b
      will return the following: [d['a']['b'] for d in l]
    """
    # Handle base cases
    match len(key_list):
        case 0:
            return None
        case 1:
            return _single_get(source, key_list[0], default)

    queue = deque(key_list)
    res = source
    while len(queue) > 0:
        key_part = queue.popleft()
        # If need to unwrap, then empty queue
        if key_part.endswith("[*]"):
            res = res.get(key_part[:-3], [])
            # Handle remaining queue items in the recursive call(s)
            if len(queue) > 0:
                res = [_nested_get(v, list(queue), []) for v in res]  # type: ignore
                queue.clear()
        else:
            res = _single_get(res, key_part)
            if res is None:
                break
    if key_list[-1].endswith("[*]"):
        res = _handle_ending_star_unwrap(res)  # type: ignore
    return res if res is not None else default


def _nested_set(
    source: dict[str, Any], tokenized_key_list: Sequence[str | int], target: Any
) -> dict[str, Any] | None:
    """
    Returns a copy of source with the replace if successful, else None.
    """
    res = source
    try:
        for k in tokenized_key_list[:-1]:
            res = res[k]  # type: ignore
        res[tokenized_key_list[-1]] = target  # type: ignore
    except IndexError:
        return None
    return source


def _get_tokenized_keypath(key: str) -> tuple[str | int, ...]:
    """
    Returns a keypath with str and ints separated.

    E.g.: "a[0].b[-1].c" -> ["a", 0, "b", -1, "c"]
    """
    tokenized_key = key.replace("[", ".").replace("]", "")
    keypath = tokenized_key.split(".")
    return tuple(int(k) if k.removeprefix("-").isnumeric() else k for k in keypath)


def drop_keys(source: dict[str, Any], keys_to_drop: Iterable[str]) -> dict[str, Any]:
    """
    Returns the dictionary with the requested keys set to `None`.

    If a key is a duplicate, then lookup fails so that key is skipped.

    DROP values are checked and handled here.
    """
    res = source
    seen_keys = set()
    for key in keys_to_drop:
        curr_keypath = _get_tokenized_keypath(key)
        if curr_keypath not in seen_keys:
            if v := _nested_get(res, key.split(".")):
                # Check if value has a DROP object
                if isinstance(v, DROP):
                    # If "out of bounds", raise an error
                    if v.value > 0 or -1 * v.value > len(curr_keypath):
                        raise RuntimeError(f"Error: DROP level {v} at {key} is invalid")
                    curr_keypath = curr_keypath[: v.value]
                    # Handle case for dropping entire object
                    if len(curr_keypath) == 0:
                        return dict()
                if updated := _nested_set(res, curr_keypath, None):
                    res = updated
                seen_keys.add(curr_keypath)
        else:
            seen_keys.add(curr_keypath)
    return res


def impute_enum_values(source: dict[str, Any], keys_to_impute: set[str]) -> dict[str, Any]:
    """
    Returns the dictionary with the Enum values set to their corresponding `.value`
    """
    res = source
    for key in keys_to_impute:
        curr_val = _nested_get(res, key.split("."))
        if isinstance(curr_val, KEEP):
            literal_val = curr_val.value
            res = _nested_set(res, _get_tokenized_keypath(key), literal_val)  # type: ignore
    return res


T = TypeVar("T")


def _handle_ending_star_unwrap(res: T) -> T | list[Any]:
    """
    Handles case of [*] unwrap specified at the end

    E.g. given: `a[*].b.c`    -> [[1, 2, 3], [4, 5, 6], None, [7, 8, 9]]
          then: `a[*].b.c[*]` -> [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    if isinstance(res, list):
        if res_without_nones := [l for l in res if (l is not None) and (isinstance(l, list))]:
            return list(chain.from_iterable(res_without_nones))
    return res
