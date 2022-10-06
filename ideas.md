
# Ideas

List of some feature/design ideas that aren't a priority now though could be interesting.

Remove from this list and re-scope accordingly once actually actively working an idea.

## Add Enum to represent an empty object

E.g. `EmptyDict`, `EmptyString`, etc. This will make the `remove_empty` checks more discrete and also give the framework a way of explicitly allowing sending an "empty" object (whenever it's semantically relevant)

## Database-like Support
Support reading from a group of objects, either from SQL or from groups of objects (i.e. NoSQL collections).

Maybe add a wrapper that provides an alternative besides `DataFrames` to work with SQL results (or encourage list of dicts, even with data sharding)?

### Native JOIN Logic Handling
If this connected to a relational database, it could be really interesting to add a way to join tables via the mapping dictionary, e.g.:
```python
join_mapping = {
    # Join all rows in A where col1=tableB.col1, col2=tableC.col2
    'tableA': {
        'col1': 'tableB.col1',
        'col2': 'tableC.col2'
    }
}

# ... and/or somehow process inline. Have an analysis pass, then optimize the query accordingly
mapping = {
    "output_col": get('tableA.col1'),
    "other_col": get('tableB.col1', where_eq='tableA.col1')
}
```
This would be a ton of work though could be interesting


## Validation Tool
Similar to mapping language, have a validation language that is structurally similar to the output.

Replaces jsonschema within Python ecosystem, though would make sense to have interop between it

Main existing solution is Pydantic, _which is already very good_. Main rationale for building something new
is having it be data-based rather than class-based (e.g. dealing with heavily nested things).
Would want to make sure performance is up to par (or at the very least isn't that slow)

E.g.:
```python
from pydian import Validator
from pydian.lib.enums import Required, Between
"""
Ideas for valid key-value pairs in the schema:
{
    'key': 'primitive',
    'key': Required('primitive'),
    'key': Between(0, 1, 'primitive'),
    'key': type,
    'key': Required(type),
    'key': Between(0, 1, type),
    'key': Required(type, must_pass=Callable),
    'key': Between(0, 1, type, must_pass=Callable),
}
"""
v_map = {
    'resourceType': Required('Patient'), # Exact str match, and required
    'name': [
        {
            'family': Required(str), # Is a str, and required if present
            'given': [
                Between(1, 3, str)
            ],
        } # Optional, since not wrapped in Required or Between
    ] # Any length
    # etc
}

is_valid_fhir_patient = Validator(v_map)
...

mapper = Mapper(map_fn, validator=is_valid_fhir_patient)
```

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
import pandas as pd

df = pd.from_csv('...')
{
    "output_col": get(df, 'c1') # df.loc[:, 'c1']
    "other_col": get(df, 'c3') # df.loc[:, 'c3'] (+ other things?)
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
Based on this, to add equivalent value would need to do the nice conditional logic, postproessing steps, etc.
(this would be clearer based on the use case(s) that come up - in fact most stuff like NaN handling is built-in)
