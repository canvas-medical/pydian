
# Ideas

List of some feature/design ideas that aren't a priority now though could be interesting.

Remove from this list and re-scope accordingly once actually actively working an idea.

## Table-based Compatibility
Idea: Some sort of Pandas/Numpy compatibility (e.g. dataframe way of approaching data interop)
- Would probably be linked to a csv version of some sort

Input: 
```csv
c1,c2,c3,...,cn
asdfa,hgfdb,afdghc,...,dcxvb
ezcbv,fsdg,gSDF,...,sdfh
...
```

Mapping:
```python
{
    "output_col": get('c1')
}
```

Output:
```csv
output_col
asdfa
ezcbv
...
```

## Query/Conditional Logic Syntax
Query idea:
```python
res = get(d, 'someKey.innerKey?keyInList="someValue"')

# vs.
res = [
    item
    for item in get(d, 'someKey.innerKey')
    if get(item, 'keyInList') == 'someValue'
]
```
... really a list comprehension is good enough for now, though could be interesting for later.
Could see this being useful if multiple conditions are involved, though would need to
make sure the logic is implemented correctly + consistently.