# Pydian - A data mapping framework

Pydian is a pure Python library for repeatable and sharable data mapping. It specifies data transforms from one dictionary into another using higher-order functions grouped together in a mapping object (also just a dictionary).

## Running Tests
At the top level dir: `PYTHONPATH=. pytest`

## Example
With Pydian, you can specify your transforms within a single dictionary as follows:
```python
import pydian.eval as E
import pydian.mapping as M

example_source_data = {
    'sourceId': 'Abc123',
    'sourceName': 'Pydian Example'
}

EXAMPLE_MAPPING = {
    'targetId': M.get('sourceId'),
    'targetArray': [
        M.get('sourceId'),
        M.get('sourceName')
    ],
    'staticData': 'Any JSON primitive',
}

assert E.apply_mapping(example_source_data, EXAMPLE_MAPPING) == {
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'staticData': 'Any JSON primitive'
}
```

See the [mapping test examples](./tests/test_mapping_values.py) for a more involved look at some of the features + intended use-cases.

The `pydian.eval` library can also be used directly, e.g. adapting the above example:
```python
import pydian.eval as E

example_source_data = {
    'sourceId': 'Abc123',
    'sourceName': 'Pydian Example'
}

assert {
    'targetId': E.get(example_source_data, 'sourceId'),
    'targetArray': [
        E.get(example_source_data, 'sourceId'),
        E.get(example_source_data, 'sourceName')
    ],
    'staticData': 'Any JSON primitive'
} == {
    'targetId': 'Abc123',
    'targetArray': [
        'Abc123',
        'Pydian Example'
    ],
    'staticData': 'Any JSON primitive'
}
```

The benefit of the `pydian.mapping` library is it allows better code portability (e.g. reusing components, organizing code in other files, etc.).

This library is still in active developement and feedback is very welcome!