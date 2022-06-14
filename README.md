# Pydian - A data mapping framework

Pydian is a pure Python library for repeatable and sharable data mapping. It specifies data transforms from one dictionary into another using higher-order functions grouped together in a mapping object (also just a dictionary).

## Running Tests
At the top level dir: `PYTHONPATH=. pytest`

## Example
With Pydian, you can specify your transforms within a single dictionary as follows:
```python
from pydian.mapping import Mapper, DictWrapper

example_source_data = {
    'sourceId': 'Abc123',
    'sourceName': 'Pydian Example'
}

def example_mapping(m: DictWrapper):
    return {
        'targetId': m.get('sourceId'),
        'targetArray': [
            m.get('sourceId'),
            m.get('sourceName')
        ],
        'staticData': 'Any JSON primitive',
    }

mapper = Mapper(example_mapping, remove_empty=False)

assert mapper.run(example_source_data) == {
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'staticData': 'Any JSON primitive'
}
```

See the [mapping test examples](./tests/test_mapping.py) for a more involved look at some of the features + intended use-cases.
