import pytest
from pydian import Mapper, DictWrapper, ROL
from pydian import get

@pytest.fixture
def simple_data() -> dict:
    return {
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

@pytest.fixture
def nested_data() -> dict:
    return {
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

# TODO: Consolidate syntax -- i.e. pick one primary (either `get(m,...) OR `m.getn(...)`)
def test_get(simple_data):
    source = simple_data
    mod_fn = lambda msg: msg['data']['patient']['id'] + '_modified'
    def mapping(m: DictWrapper) -> dict:
        return {
            'CASE_constant': 123,
            'CASE_single': m.get('data'),
            'CASE_nested': m.getn('data.patient.id'),
            'CASE_nested_as_list': [
                m.getn('data.patient.active')
            ],
            'CASE_modded': mod_fn(m),
            'CASE_index_list': {
                'first': m.getn('list_data[0].patient'),
                'second': m.getn('list_data[1].patient'),
                'out_of_bounds': m.getn('list_data[2].patient')
            }
        }
    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
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

def test_get_fn(simple_data):
    source = simple_data
    mod_fn = lambda msg: msg['data']['patient']['id'] + '_modified'
    def mapping(m: dict) -> dict:
        return {
            'CASE_constant': 123,
            'CASE_single': get(m, 'data'),
            'CASE_nested': get(m, 'data.patient.id'),
            'CASE_nested_as_list': [
                get(m, 'data.patient.active')
            ],
            'CASE_modded': mod_fn(m),
            'CASE_index_list': {
                'first': get(m, 'list_data[0].patient'),
                'second': get(m, 'list_data[1].patient'),
                'out_of_bounds': get(m, 'list_data[2].patient')
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


def test_nested_get(nested_data):
    source = nested_data
    def mapping(m: DictWrapper):
        return {
            'CASE_constant': 123,
            'CASE_unwrap_active': m.getn('data[*].patient.active'),
            'CASE_unwrap_id': m.getn('data[*].patient.id'),
            'CASE_unwrap_list': m.getn('data[*].patient.ints'),
            'CASE_unwrap_list_twice': m.getn('data[*].patient.ints[*]'),
            'CASE_unwrap_list_dict': m.getn('data[*].patient.dicts[*].num'),
            'CASE_unwrap_list_dict_twice': m.getn('data[*].patient.dicts[*].num[*]')
        }
    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {
        'CASE_constant': 123,
        'CASE_unwrap_active': [True, False, True, True],
        'CASE_unwrap_id': ['abc123', 'def456', 'ghi789', 'jkl101112'],
        'CASE_unwrap_list': [[1,2,3], [4,5,6], [7,8,9]],
        'CASE_unwrap_list_twice': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'CASE_unwrap_list_dict': [[1,2], [3,4] ,[5,6], [7]],
        'CASE_unwrap_list_dict_twice': [1, 2, 3, 4, 5, 6, 7],
    }

def test_conditional_drop(simple_data):
    source = simple_data
    def mapping(m: DictWrapper):
        return {
            'CASE_not_found': m.get('INVALID_KEY'),
            'CASE_constant': 123,
            'CASE_single': m.get('data'),
            'CASE_nested': {
                'id': m.getn('data.INVALID_KEY')
            },
            'CASE_list': [
                m.getn('data.patient.active')
            ],
            'CASE_deeply': {
                'nested': {
                    'thing': 'here',
                    'other_thing': 'untouched'
                }
            }
        }
    cond_drop = {
        'CASE_not_found': {
            'CASE_constant',
            'CASE_single',
            'CASE_deeply.nested.thing'
        },
        'CASE_nested.id': {
            'CASE_list'
        }
    }
    mapper = Mapper(mapping, remove_empty=True, conditionally_drop=cond_drop)
    res = mapper(source)
    assert res == {
        'CASE_deeply': {
            'nested': {
                'other_thing': 'untouched'
            }
        }
    }

def test_rol_drop(simple_data):
    source = simple_data
    def mapping(m: dict):
        return {
            'CASE_parent_keep': {
                'CASE_curr_drop': {
                    'a': get(m, 'notFoundKey', drop_rol=ROL.CURRENT),
                    'b': 'someValue'
                },
                'CASE_curr_keep': {
                    'id': get(m, 'data.patient.id', drop_rol=ROL.CURRENT)
                }
            }
        }
    mapper = Mapper(mapping, remove_empty=True)
    res = mapper(source)
    assert res == {
        'CASE_parent_keep': {
            'CASE_curr_keep': {
                'id': get(source, 'data.patient.id')
            }
        }
    }