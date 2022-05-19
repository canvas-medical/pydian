import pydian.mapping as M
import pydian.eval as E

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
    res = E.apply_mapping(source, mapping)
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
        }]
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
    res = E.apply_mapping(source, mapping)
    assert res == {
        'CASE_constant': mapping.get('CASE_constant'),
        'CASE_unwrap_active': [True, False, True],
        'CASE_unwrap_id': ['abc123', 'def456', 'ghi789'],
        'CASE_unwrap_list': [[1,2,3], [4,5,6], [7,8,9]],
        'CASE_unwrap_list_twice': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'CASE_unwrap_list_dict': [[1,2], [3,4] ,[5,6]],
        'CASE_unwrap_list_dict_twice': [1, 2, 3, 4, 5, 6],
    }

def test_eval_then_apply():
    source = {}
    mapping = {}
    res = E.apply_mapping(source, mapping)
    assert res == {}
    raise NotImplementedError('Implement this!')

def test_map_list():
    source = {}
    mapping = {}
    res = E.apply_mapping(source, mapping)
    assert res == {}
    raise NotImplementedError('Implement this!')

def test_concat():
    source = {}
    mapping = {}
    res = E.apply_mapping(source, mapping)
    assert res == {}
    raise NotImplementedError('Implement this!')

def test_filter_list():
    source = {}
    mapping = {}
    res = E.apply_mapping(source, mapping)
    assert res == {}
    raise NotImplementedError('Implement this!')

def test_lookup():
    source = {}
    mapping = {}
    res = E.apply_mapping(source, mapping)
    assert res == {}
    raise NotImplementedError('Implement this!')

def test_apply_mapping():
    source = {}
    mapping = {}
    res = E.apply_mapping(source, mapping)
    assert res == {}
    raise NotImplementedError('Implement this!')