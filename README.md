# Pydian - pythonic data mapping

Pydian is a pure Python library for repeatable and sharable data mapping. Pydian reduces boilerplate and provides a framework for expressively mapping data through Python `dict` objects. 

## Running Tests
At the top level dir: `PYTHONPATH=. pytest`

## Example
With Pydian, you can specify your transforms within a single dictionary as follows:
```python
from pydian import Mapper, DictWrapper

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

def example_mapping(m: DictWrapper):
    return {
        'targetId': m.get('sourceId'),
        'targetArray': [
            m.get('sourceId'),
            m.get('sourceName')
        ],
        'targetNested': m.get('sourceNested.some.nested.value'),
        'staticData': 'Any JSON primitive',
        'targetMaybe': m.get('sourceMaybe.nope.its.None')
    }

mapper = Mapper(example_mapping, remove_empty=True)

assert mapper(example_source_data) == {
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'targetNested': 'here',
    'staticData': 'Any JSON primitive'
}
```

See the [mapping test examples](./tests/test_mapping.py) for a more involved look at some of the features + intended use-cases.

The general `get` method is available as well -- e.g. this is equivalent to the example above:
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
        'targetNested': get(m, 'sourceNested.some.nested.value'),
        'staticData': 'Any JSON primitive',
        'targetMaybe': get(m, 'sourceMaybe.nope.its.None')
    }

mapper = Mapper(example_mapping, remove_empty=True)

assert mapper(example_source_data) ==  {
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'targetNested': 'here',
    'staticData': 'Any JSON primitive'
}
```

Using the `Mapper` class is still preferred for consistency and mapping-related features, however this option is provided so the function can be used independently in other contexts as well!