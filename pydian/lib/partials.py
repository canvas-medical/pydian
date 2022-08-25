from functools import partial
from typing import Callable


def str_replace(old: str, new: str) -> Callable[[str], str]:
    """
    Partial wrapper for `str.replace`
    """
    return partial(_str_replace, old=old, new=new)


def _str_replace(s: str, old: str, new: str) -> str:
    """
    A wrapper to allow passing kwargs to `str.replace`
    """
    return s.replace(old, new)
