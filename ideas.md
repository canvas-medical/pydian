
# Ideas

List of some feature/design ideas that aren't a priority now though could be interesting.

Remove from this list and re-scope accordingly once actually actively working an idea.

## Table-based Compatibility
Idea: Some sort of Pandas/Numpy compatibility (e.g. dataframe way of approaching data interop)
- Would probably be linked to a csv version of some sort

Input: 
```csv
c1,c2,c3,...,cn
abc,...,123,...,...
def,...,456,...,...
...
```

Mapping:
```python
{
    "output_col": get('c1'),
    "other_col": get('c3')
}
```

Output (as a DataFrame):
```csv
output_col,other_col
abc,123
def,456
...
```

Mainly would be a wrapper around `DataFrame.apply(..., axis=0)`, and apply the mapping logic to each row.
Based on this, to add equivalent value would need to do the nice conditional logic, NaN handling, etc.
(this would be clearer based on the use case(s) that come up)

## Query/Conditional Logic Syntax
Query idea:
```python
res = get(d, 'someKey.innerKey?keyInList="someValue"')

# vs.
res = [
    item
    for item in get(d, 'someKey.innerKey', [])
    if get(item, 'keyInList') == 'someValue'
]
```
... really a list comprehension is good enough for now, though could be interesting for later.
Could see this being useful if multiple conditions are involved, though would need to
make sure the logic is implemented correctly + consistently.

### Exclude Syntax
Query syntax, except `~` instead of `?`

For both: `?_expression~_expression2`

### Return Syntax
Query on a specific set of values, but return a different one

Maybe `-> _path_part_of_key_prefix_`

E.g.: `get('a[*].b.code,system ? code="abc" & system="def" -> a[*].b')`

Consider native Python things already available

## Validation Tool
Similar to mapping language, have a validation language that is structurally similar to the output. 

Replaces jsonschema within Python ecosystem, though would make sense to have interop between it

Main existing solution is Pydantic, _which is already very good_. Main rationale for building something new
is having it be data-based rather than class-based (e.g. dealing with heavily nested things).
Would want to make sure performance is up to par (or at the very least isn't that slow)

E.g.:
```python
from pydian import Validator

"""
Ideas for valid key-value pairs in the schema:
{
    'key': 'primitive',
    'key': 'primitive',
    'key': ('primitive', int),
    'key': ('primitive', int, int),
    'key': type,
    'key': (type, ),
    'key': (type, int),
    'key': (type, int, int),
    'key': (type, callable),
    'key': (type, callable, int),
    'key': (type, callable, int, int),
}
"""
v_map = {
    'resourceType': ('Patient', 1), # Exact str match, and required
    'name': [
        {
            'family': (str, 1), # Is a str, and required if present
            'given': [
                (str, 1)
            ],
        } # Optional, since not wrapped in Tuple
    ]
    # etc
}

is_valid_fhir_patient = Validator(v_map)
...

mapper = Mapper(map_fn, validator=is_valid_fhir_patient)
```

## Multiple get syntax (e.g. on unwrap)

While iterating through a list, often we want to get multiple values. What if there was a syntax like:
```python
from pydian import get
source = {
    'l': [
        {'a': 1, 'b': 2},
        {'a': 3, 'a': 4}
    ]
}
assert get(source, 'l[*].a,b') == [(1,2), (3,4)]
```
... then could also query and do more things on top of that

## List Slicing

E.g. `l[1:].a`, or `l[:-1].a`, or `l[1:-1].a,b`, etc.

Don't add this until it's useful (discourage overly complex logic)