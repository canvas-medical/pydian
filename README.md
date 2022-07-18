# Pydian - pythonic data mapping

Pydian is a pure Python library for repeatable and sharable data mapping. Pydian reduces boilerplate and provides a framework for expressively mapping data through Python `dict` objects and native list/dict comprehension.

With Pydian, you can specify your transforms within a single dictionary as follows:
```python
from pydian import Mapper, get

# Some arbitrary source dict
payload = {
    'some': {
        'deeply': {
            'nested': [{
                'value': 'here!'
            }]
        }
    },
    'list_of_objects': [
        {'val': 1},
        {'val': 2},
        {'val': 3}
    ]
}

# A centralized mapping function -- specify your logic as data
#   This always takes at least a dict and returns a dict
def mapping_fn(source: dict) -> dict:
    return {
        'res_list': [{
            'static_value': 'Some static data',
            'uppercase_nested_val': get(source, 'some.deeply.nested[0].value', apply=str.upper), # Get deeply nested values
            'unwrapped_list': get(source, 'list_of_objects[*].val'), # Unwrap list structures with [*]
            'maybe_present_value?': get(source, 'somekey.nope.not.there', apply=str.upper), # Null-check handling is built-in!
        }]
    }

# A `Mapper` class that runs the provided function and some built-in post-processing features 
#   (e.g. empty value removal)
mapper = Mapper(mapping_fn)

# A result that syntactically matches the mapping function!
assert mapper(payload) == {
    'res_list': [{
        'static_value': 'Some static data',
        'uppercase_nested_val': 'HERE!',
        'unwrapped_list': [1, 2, 3],
        # get(m, 'somekey.nope.not.there') was None, so it was removed automatically from the result
    }],
}
```

See the [mapping test examples](./tests/test_mapping.py) for a more involved look at some of the features + intended use-cases.

## `get` Functionality
Pydian defines a special `get` function that provides a simple syntax for:
- Getting nested items
    - Chain gets with `.`
    - Index into lists, e.g. `[0]`, `[-1]`
    - Unwrap a list of dicts with `[*]`
- Chaining successful operations with `apply`
- Specifying conditional dropping with `drop_level` (see [below](./README.md#conditional-dropping))

`None` handling is built-in which reduces boilerplate code!

## `Mapper` Functionality
The `Mapper` framework provides a consistent way of abstracting mapping steps as well as several useful post-processing steps, including:
1. [Null value removal](./README.md#null-value-removal): Removing `None`, `''`, `[]`, `{}` values from the final result
2. [Conditional dropping](./README.md#conditional-dropping): Drop key(s)/object(s) if a specific value is `None`

### Null value removal
This is just a parameter on the `Mapper` object (`remove_empty`) which defaults to `True`.

An "empty" value is handled in [lib/util.py](./pydian/lib/util.py) and includes: `None`, `''`, `[]`, `{}`

### Conditional dropping
This can be done during value evaluation in `get` which the `Mapper` object cleans up:
```python
from pydian import Mapper, get
from pydian import DROP

payload = {
    'some': 'value'
    # `source_key` is missing!
}

def mapping_fn(source: dict) -> dict:
    return {
        'obj': {
            # Specify in `get`, or as an if comprehension
            'res_k': get(source, 'source_key', drop_level=DROP.THIS_OBJECT), # Sets the entire object to `None` if this is `None`
            'other_k': 'Some value',
        }
    }

mapper = Mapper(mapping_fn, remove_empty=False)

assert mapper(payload) == {
    'obj': None
}
```

## Issues

Please submit a GitHub Issue for any bugs + feature requests and we'll take a look!
