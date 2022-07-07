# Pydian - pythonic data mapping

Pydian is a pure Python library for repeatable and sharable data mapping. Pydian reduces boilerplate and provides a framework for expressively mapping data through Python `dict` objects and native list/dict comprehension.

With Pydian, you can specify your transforms within a single dictionary as follows:
```python
from pydian import Mapper, get

# Some arbitrary source data
source = {
    'sourceId': 'Abc123',
    'sourceName': 'Pydian Example',
    'sourceNested': {
        'some': {
            'nested': {
                'value': 'here!'
            }
        }
    },
    'sourceList': [
        {'val': 1},
        {'val': 2},
        {'val': 3}
    ]
}

# A centralized mapping function -- specify your logic as data!
def mapping_fn(m: dict) -> dict:
    return {
        'staticData': 'Any JSON primitive',
        'targetId': get(m, 'sourceId'),
        'targetArray': [
            get(m, 'sourceId'),
            get(m, 'sourceName')
        ],
        'targetNested': get(m, 'sourceNested.some.nested.value', apply=str.upper), # Get deeply nested values
        'targetMaybe': get(m, 'sourceMaybe.nope.its.None', apply=str.upper), # Null-check handling is built-in!
        'targetList': get(m, 'sourceList[*].val') # Unwrap list structures with [*]
    }

# A `Mapper` class that runs the provided function and some built-in post-processing features
mapper = Mapper(mapping_fn)

# A result that syntactically matches the mapping!
assert mapper(source) == {
    'staticData': 'Any JSON primitive',
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'targetNested': 'HERE!',
    'targetMaybe': None,
    'targetList': [1, 2, 3]
}
```

See the [mapping test examples](./tests/test_mapping.py) for a more involved look at some of the features + intended use-cases.

## `get` Functionality
Pydian defines a special `get` function that provides a simple syntax for:
- Getting nested items
    - Chain gets with `.`
    - Index into lists
    - Unwrap a list of dicts with `[*]`
- Chaining successful operations with `apply`
- Specifying conditional dropping (see [below](./README.md#conditional-dropping))

`None` handling is built-in which reduces boilerplate code!

## `Mapper` Functionality
The `Mapper` framework provides a consistent way of abstracting mapping steps as well as several useful post-processing steps, including:
1. [Null value removal](./README.md#null-value-removal): Removing `None`, `''`, `[]`, `{}` values from the final result
2. [Conditional dropping](./README.md#conditional-dropping): Drop key(s)/object(s) if a specific value is `None`
3. [Tuple-key comprehension](./README.md#tuple-key-comprehension): Map multiple keys to a single value
### Null value removal
This is just a parameter on the `Mapper` object, e.g.:
```python
mapper = Mapper(mapping_fn, remove_empty=True) # Defaults to False
```

### Conditional dropping
This can be done during value evaluation in `get` (preferred) and/or as a postprocessing step in the `Mapper` object:
```python
from pydian import Mapper, get
from pydian import DROP

source = {
    # `source_k` is missing!
}

def mapping_fn(m: dict) -> dict:
    return {
        'obj': {
            # Specify in `get`, or as an if comprehension
            'res_k': get(m, 'source_k', drop_level=DROP.CURRENT_OBJECT), # Sets the entire object to `None` if this is `None`
            'other_k': 'Some value',
        }
    }

mapper = Mapper(mapping_fn)

assert mapper(source) == {
    'obj': None
}
```

### Tuple-key comprehension
Need to get multiple key-value pairs from a single function call? This can done within the mapping function:
```python
from pydian import Mapper, get

source = {
    'source_list': list(range(3)) # [0, 1, 2]
}

def mapping_fn(m: dict) -> dict:
    return {
        # A tuple-key and tuple-value will be unwrapped in-order
        ('first',
        'second',
        'third'): get(m, 'source_list', apply=tuple)
    }

mapper = Mapper(mapping_fn)

assert mapper(source) == {
    'first': 0,
    'second': 1,
    'third': 2
}
```
