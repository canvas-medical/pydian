from pydian import Mapper, DictWrapper
from pydian import nested_get, single_get

# TODO: Use fixtures

def test_get():
    source = {
        'data': {
            'patient': {
                'id': 'abc123',
                'active': True
            }
        },
        'list_data': [
            {
                'patient': {
                    'id': 'def456',
                    'active': True
                }
            },
            {
                'patient': {
                    'id': 'ghi789',
                    'active': False
                }
            },
        ]
    }
    mod_fn = lambda msg: msg['data']['patient']['id'] + '_modified'
    def mapping(m: DictWrapper) -> dict:
        return {
            'CASE_constant': 123,
            'CASE_single': m.get('data'),
            'CASE_nested': m.get('data.patient.id'),
            'CASE_nested_as_list': [
                m.get('data.patient.active')
            ],
            'CASE_modded': mod_fn(m.source),
            'CASE_index_list': {
                'first': m.get('list_data[0].patient'),
                'second': m.get('list_data[1].patient'),
                'out_of_bounds': m.get('list_data[2].patient')
            }
        }
    mapper = Mapper(mapping, remove_empty=True)
    res = mapper.run(source)
    assert res == {
        'CASE_constant': 123,
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

def test_get_alt_syntax():
    source = {
        'data': {
            'patient': {
                'id': 'abc123',
                'active': True
            }
        },
        'list_data': [
            {
                'patient': {
                    'id': 'def456',
                    'active': True
                }
            },
            {
                'patient': {
                    'id': 'ghi789',
                    'active': False
                }
            },
        ]
    }
    mod_fn = lambda msg: msg['data']['patient']['id'] + '_modified'
    def mapping(m: dict) -> dict:
        return {
            'CASE_constant': 123,
            'CASE_single': single_get(m, 'data'),
            'CASE_nested': nested_get(m, 'data.patient.id'),
            'CASE_nested_as_list': [
                nested_get(m, 'data.patient.active')
            ],
            'CASE_modded': mod_fn(m),
            'CASE_index_list': {
                'first': nested_get(m, 'list_data[0].patient'),
                'second': nested_get(m, 'list_data[1].patient'),
                'out_of_bounds': nested_get(m, 'list_data[2].patient')
            }
        }
    # Note syntax difference
    res = mapping(source)
    assert res == {
        'CASE_constant': 123,
        'CASE_single': source.get('data'),
        'CASE_nested': source['data']['patient']['id'],
        'CASE_nested_as_list': [
            source['data']['patient']['active']
        ],
        'CASE_modded': mod_fn(source),
        'CASE_index_list': {
            'first': source['list_data'][0]['patient'],
            'second': source['list_data'][1]['patient'],
            'out_of_bounds': None # This _doesn't_ get deleted 
        }
    }


def test_nested_get():
    source = {
        'data': [{
            'patient': {
                'id': 'abc123',
                'active': True,
                'ints': [1, 2, 3],
                'dicts': [
                    {'num': 1},
                    {'num': 2}
                ]
            }
        },
        {
            'patient': {
                'id': 'def456',
                'active': False,
                'ints': [4, 5, 6],
                'dicts': [
                    {'num': 3},
                    {'num': 4}
                ]
            }
        },
        {
            'patient': {
                'id': 'ghi789',
                'active': True,
                'ints': [7, 8, 9],
                'dicts': [
                    {'num': 5},
                    {'num': 6}
                ]
            }
        },
        {
            'patient': {
                'id': 'jkl101112',
                'active': True,
                # 'ints' is deliberately missing
                'dicts': [
                    {'num': 7}
                ]
            }
        },
        ]
    }
    def mapping(m: DictWrapper):
        return {
            'CASE_constant': 123,
            'CASE_unwrap_active': m.get('data[*].patient.active'),
            'CASE_unwrap_id': m.get('data[*].patient.id'),
            'CASE_unwrap_list': m.get('data[*].patient.ints'),
            'CASE_unwrap_list_twice': m.get('data[*].patient.ints[*]'),
            'CASE_unwrap_list_dict': m.get('data[*].patient.dicts[*].num'),
            'CASE_unwrap_list_dict_twice': m.get('data[*].patient.dicts[*].num[*]')
        }
    mapper = Mapper(mapping, remove_empty=True)
    res = mapper.run(source)
    assert res == {
        'CASE_constant': 123,
        'CASE_unwrap_active': [True, False, True, True],
        'CASE_unwrap_id': ['abc123', 'def456', 'ghi789', 'jkl101112'],
        'CASE_unwrap_list': [[1,2,3], [4,5,6], [7,8,9]],
        'CASE_unwrap_list_twice': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'CASE_unwrap_list_dict': [[1,2], [3,4] ,[5,6], [7]],
        'CASE_unwrap_list_dict_twice': [1, 2, 3, 4, 5, 6, 7],
    }

def test_conditional_drop():
    source = {
        'data': {
            'patient': {
                'id': 'abc123',
                'active': True
            }
        },
        'list_data': [
            {
                'patient': {
                    'id': 'def456',
                    'active': True
                }
            },
            {
                'patient': {
                    'id': 'ghi789',
                    'active': False
                }
            },
        ]
    }
    def mapping(m: DictWrapper):
        return {
            'CASE_not_found': m.get('schmayda'),
            'CASE_constant': 123,
            'CASE_single': m.get('data'),
            'CASE_nested': m.get('data.patient.id'),
            'CASE_nested_as_list': [
                m.get('data.patient.active')
            ],
        }
    cond_drop = {
        'CASE_not_found': {
            'CASE_constant',
            'CASE_single'
        },
        'CASE_nested': 'CASE_nested_as_list'
    }
    mapper = Mapper(mapping, remove_empty=True, conditionally_drop=cond_drop)
    res = mapper.run(source)
    assert res == {
        'CASE_nested': source['data']['patient']['id'],
        'CASE_nested_as_list': [
            source['data']['patient']['active']
        ]
    }