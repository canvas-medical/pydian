# Pydian - A data mapping framework

Pydian is a pure Python library for repeatable and sharable data mapping. It specifies data transforms from one dictionary into another using higher-order functions grouped together in a mapping object (also just a dictionary).

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
        'targetNested': m.getn('sourceNested.some.nested.value'),
        'staticData': 'Any JSON primitive',
    }

mapper = Mapper(example_mapping, remove_empty=False)

assert mapper.run(example_source_data) == {
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

The `DictWrapper` class is there for convenience -- this is equivalent:
```python
from pydian import get

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
    }

assert example_mapping(example_source_data) ==  {
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'targetNested': 'here',
    'staticData': 'Any JSON primitive'
}
```

This removes the need for the `Mapper` class, however you lose whatever features come with it (e.g. empty value handling, conditional deleting, etc.). Using the `Mapper` class is preferred for consistency and code sharing, however this option is provided so the function can be used independently as necessary!