# Pydian - pythonic data mapping

Pydian is a pure Python library for repeatable and sharable data mapping. Pydian reduces boilerplate and provides a framework for expressively mapping data through Python `dict` objects.

## Running Tests
At the top level dir: `PYTHONPATH=. pytest`

## Example
With Pydian, you can specify your transforms within a single dictionary as follows:
```python
from pydian import Mapper, get

# Same example as above
example_source_data = {
    'sourceId': 'Abc123',
    'sourceName': 'Pydian Example',
    'sourceNested': {
        'some': {
            'nested': {
                'value': 'here'
            }
        }
    }
}

def example_mapping(m: dict):
    return {
        'targetId': get(m, 'sourceId'),
        'targetArray': [
            get(m, 'sourceId'),
            get(m, 'sourceName')
        ],
        'targetNested': get(m, 'sourceNested.some.nested.value', then=str.upper),
        'staticData': 'Any JSON primitive',
        'targetMaybe': get(m, 'sourceMaybe.nope.its.None', then=str.upper)
    }

mapper = Mapper(example_mapping, remove_empty=True)

assert mapper(example_source_data) ==  {
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'targetNested': 'HERE',
    'staticData': 'Any JSON primitive'
}
```

See the [mapping test examples](./tests/test_mapping.py) for a more involved look at some of the features + intended use-cases.

## Complimentary Libraries
Pydian leverages [benedict](https://github.com/fabiocaccamo/python-benedict) internally, and `benedict` objects can be used to facilitate mapping as well. In addition to the standard library [itertools](https://docs.python.org/3/library/itertools.html), functional tools like [funcy](https://github.com/Suor/funcy) and [more-itertools](https://github.com/more-itertools/more-itertools) can improve development and make data transforms more consistent and elegant.
