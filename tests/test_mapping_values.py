import pydian.eval as E
import pydian.mapping as M
from functools import partial

def test_get():
    source = {
        'data': {
            "patient": {
                "id": "abc123",
                "active": True
            }
        },
        "list_data": [
            {
                "patient": {
                    "id": "def456",
                    "active": True
                }
            },
            {
                "patient": {
                    "id": "ghi789",
                    "active": False
                }
            },
        ]
    }
    mod_fn = lambda msg: msg['data']['patient']['id'] + "_modified"
    mapping = {
        "CASE_constant": 123,
        'CASE_single': M.get('data'),
        "CASE_nested": M.get('data.patient.id'),
        "CASE_nested_as_list": [
            M.get('data.patient.active')
        ],
        "CASE_modded": mod_fn,
        'CASE_index_list': {
            'first': M.get('list_data[0].patient'),
            'second': M.get('list_data[1].patient'),
            'out_of_bounds': M.get('list_data[2].patient')
        }
    }
    res = E.apply_mapping(source, mapping, remove_empty=True)
    assert res == {
        'CASE_constant': mapping.get('CASE_constant'),
        'CASE_single': source.get('data'),
        'CASE_nested': source['data']['patient']['id'],
        'CASE_nested_as_list': [
            source['data']['patient']['active']
        ],
        'CASE_modded': mod_fn(source),
        'CASE_index_list': {
            'first': source['list_data'][0]['patient'],
            'second': source['list_data'][1]['patient']
        }
    }

def test_nested_get():
    source = {
        "data": [{
            "patient": {
                "id": "abc123",
                "active": True,
                "ints": [1, 2, 3],
                'dicts': [
                    {'num': 1},
                    {'num': 2}
                ]
            }
        },
        {
            "patient": {
                "id": "def456",
                "active": False,
                "ints": [4, 5, 6],
                'dicts': [
                    {'num': 3},
                    {'num': 4}
                ]
            }
        },
        {
            "patient": {
                "id": "ghi789",
                "active": True,
                "ints": [7, 8, 9],
                'dicts': [
                    {'num': 5},
                    {'num': 6}
                ]
            }
        },
        {
            "patient": {
                "id": "jkl101112",
                "active": True,
                # 'ints' is deliberately missing
                'dicts': [
                    {'num': 7}
                ]
            }
        },
        ]
    }
    mapping = {
        "CASE_constant": 123,
        "CASE_unwrap_active": M.get('data[*].patient.active'),
        "CASE_unwrap_id": M.get('data[*].patient.id'),
        'CASE_unwrap_list': M.get('data[*].patient.ints'),
        'CASE_unwrap_list_twice': M.get('data[*].patient.ints[*]'),
        'CASE_unwrap_list_dict': M.get('data[*].patient.dicts[*].num'),
        'CASE_unwrap_list_dict_twice': M.get('data[*].patient.dicts[*].num[*]')
    }
    res = E.apply_mapping(source, mapping, remove_empty=True) # Here, remove_empty to ignore the None case
    assert res == {
        'CASE_constant': mapping.get('CASE_constant'),
        'CASE_unwrap_active': [True, False, True, True],
        'CASE_unwrap_id': ['abc123', 'def456', 'ghi789', 'jkl101112'],
        'CASE_unwrap_list': [[1,2,3], [4,5,6], [7,8,9]],
        'CASE_unwrap_list_twice': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'CASE_unwrap_list_dict': [[1,2], [3,4] ,[5,6], [7]],
        'CASE_unwrap_list_dict_twice': [1, 2, 3, 4, 5, 6, 7],
    }

def test_eval_then_apply():
    source = {
        'int': 1,
        'float': 5.0,
        'str': 'abc123',
        'list_str': [
            'abc',
            'def',
            'ghi'
        ],
        'dict': {
            'str': 'def456',
            'dict_nested': {
                'str': 'ghi789'
            }
        }
    }
    add_one = lambda x: x + 1
    append_one = lambda x: f'{x}_one'
    mapping = {
        'CASE_int': M.eval_then_apply(M.get('int'), add_one),
        'CASE_float': M.eval_then_apply(M.get('float'), add_one),
        'CASE_str': M.eval_then_apply(M.get('str'), append_one)
    }
    res = E.apply_mapping(source, mapping)
    assert res == {
        'CASE_int': add_one(E.single_get(source, 'int')),
        'CASE_float': add_one(E.single_get(source, 'float')),
        'CASE_str': append_one(E.single_get(source, 'str'))
    }

def test_map_list():
    source = {
        'list_A': [
            'a',
            'b'
        ],
        'list_B': [
            'c',
            'd',
            'e',
            ''
        ],
    }
    append_str = lambda x, s: f'{x}_{s}'
    append_one = partial(append_str, s='one')
    EXAMPLE_STR = 'two'
    mapping = {
        'A': M.map_list(
            M.get('list_A'),
            append_one
        ),
        'B': M.map_list(
            M.get('list_B'),
            partial(append_str, s=EXAMPLE_STR)
        )
    }
    res = E.apply_mapping(source, mapping)
    assert res == {
        'A': [append_one(s) for s in source.get('list_A')],
        'B': [append_str(s, EXAMPLE_STR) for s in source.get('list_B')]
    }

def test_concat():
    source = {
        'list_A': [
            'a',
            'b'
        ],
        'list_B': [
            'c',
            'd',
            'e',
            ''
        ]
    }
    mapping = {
        'res': M.concat(
            M.get('list_A'),
            M.get('list_B'),
            remove_empty=False
        )
    }
    res = E.apply_mapping(source, mapping)
    assert res == {
        'res': ['a', 'b', 'c', 'd', 'e', '']
    }
    res = E.apply_mapping(source, mapping, remove_empty=True)
    assert res == {
        'res': ['a', 'b', 'c', 'd', 'e']
    }

def test_filter_list():
    source = {
        'list_A': [1, 2, 3],
        'list_B': [4, 5, 6, 7, 8]
    }
    is_even = lambda x: x % 2 == 0
    is_odd = lambda x: x % 2 == 1
    is_str = lambda x: type(x) == str
    mapping = {
        'A_odds': M.filter_list(
            M.get('list_A'),
            filter_expr=is_odd
        ),
        'A_evens': M.filter_list(
            M.get('list_A'),
            filter_expr=is_even
        ),
        'B_odds': M.filter_list(
            M.get('list_B'),
            filter_expr=is_odd
        ),
        'B_evens': M.filter_list(
            M.get('list_B'),
            filter_expr=is_even
        ),
        'B_strs': M.filter_list(
            M.get('list_B'),
            filter_expr=is_str
        )
    }
    res = E.apply_mapping(source, mapping)
    assert res == {
        'A_odds': [1, 3],
        'A_evens': [2],
        'B_odds': [5,7],
        'B_evens': [4,6,8],
        'B_strs': []
    }

def test_lookup():
    source = {
        'first': 'A',
        'second': 'B',
        'third': 'not_found'
    }
    d = {
        'A': 'found_A',
        'B': 'found_B'
    }
    mapping = {
        'res_first': M.lookup(M.get('first'), d),
        'res_second': M.lookup(M.get('second'), d),
        'res_third': M.lookup(M.get('third'), d)
    }
    res = E.apply_mapping(source, mapping)
    assert res == {
        'res_first': d.get(source.get('first')),
        'res_second': d.get(source.get('second')),
        'res_third': d.get(source.get('third'))
    }

def test_apply_mapping():
    source = {
        'first': 'A',
        'second': 'B'
    }
    mod_str = lambda x: f'{x}.modded'
    sub_mapping = {
        'second_mod': M.get('second', then=mod_str)
    }
    mapping = {
        'first_mod': M.get('first', then=mod_str),
        'nested_mod': {
            'res':  M.apply_mapping(sub_mapping),
            'const': True,
            'first_mod_again': M.get('first', then=mod_str),
        }
    }
    res = E.apply_mapping(source, mapping)
    assert res == {
        'first_mod': mod_str(source.get('first')),
        'nested_mod': {
            'res': { 'second_mod': mod_str(source.get('second')) },
            'const': True,
            'first_mod_again': mod_str(source.get('first')),
        }
    }