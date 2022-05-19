
# Ideas

List of some feature/design ideas that aren't a priority now though could be interesting.

Remove from this list and re-scope accordingly once actually actively working an idea.

## Incorporate Existing Functional Libraries
Like [funcy](https://github.com/Suor/funcy) (thank you Chris). This will remove the need for some higher-order functions and give more structured recommendations/design decisions on how to model some of the mappings

## Table-based Compatibility
Idea: Some sort of Pandas/Numpy compatibility (e.g. dataframe way of approaching data interop)
- Would probably be linked to a csv version of some sort


Input: 
```
api_sometable

c1,c2,c3,...,cn
asdfa,hgfdb,afdghc,...,dcxvb
ezcbv,fsdg,gSDF,...,sdfh
...
```

Mapping:
```
{
    "output_col": get('c1')
}

```

Output:
```
c1
asdfa
```

## Query/Conditional Logic Syntax
Query idea:
```
{
'id': 'coding[?: v["coding"] == "SNOMED"].text'
'ids': 'coding[*]'
}
```
... really is a filter function