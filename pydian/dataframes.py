from typing import Any, Iterable, TypeVar

import pandas as pd

from pydian.types import ApplyFunc, ConditionalCheck
import pydian.dicts as D
import pydian.partials as P

def get(
    source: pd.DataFrame | pd.Series,
    cols: Iterable[str],
    missing_default: Any = pd.NA,
    where: ConditionalCheck | Iterable[ConditionalCheck] | None = None,
    then_apply: ApplyFunc | Iterable[ApplyFunc] | None = None,
) -> pd.DataFrame | pd.Series | Any:
    """
    Gets all rows in the specified columns (for a Series, values at the specified headers).

    If there is only a single value, that value is returned "unwrapped" from the DataFrame/Series.

    If an operation fails, the `missing_default` value will be imputed.

    Use `where` filter only values fitting a certain condition. For multiple, AND logic applies

    Use `apply` to apply operations on successful results.
    """
    try:
        # Same for DataFrame and/or Series
        res = source.loc[:, cols]
    except:
        return missing_default

    if where:
        res = keep(res, where)
        
    if then_apply:
        res = apply(res, then_apply=then_apply)

    return res


T = TypeVar("T", pd.DataFrame, pd.Series)


def apply(
    source: T,
    cols: list[str] | None,
    where: ConditionalCheck,
    then_apply: ApplyFunc | Iterable[ApplyFunc],
    missing_default: Any = pd.NA
) -> T:
    res = source
    if not isinstance(then_apply, Iterable):
        then_apply = (then_apply, )
    for fn in then_apply:
        try:
            # TODO: Apply the function to the set of columns
            ...
        except:
            return missing_default
    ...

def keep(source: T, where: ConditionalCheck | Iterable[ConditionalCheck], missing_default: Any=pd.NA ) -> T:
    res = source
    if not isinstance(where, Iterable):
        where = (where, )
    for cond in where:
        try:
            # TODO: Figure-out the right Pandas way to do this
            ...
        except:
            res = missing_default
            break


def remove(source: T, where: ConditionalCheck | Iterable[ConditionalCheck]) -> T:
    ...
