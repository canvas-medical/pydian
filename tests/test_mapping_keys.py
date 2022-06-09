import pydian.eval as E
import pydian.mapping as M
from pydian.lib.enums import RelativeObjectLevel as ROL
from functools import partial

def test_drop_object_if():
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
    is_odd = lambda x: x % 2 == 1
    mapping = {
        'parent': {
            'first': { 
                ("CASE_drop_constant", M.drop_object_if(is_odd)): 123,
            },
            'second': {
                ('CASE_keep_constant', M.drop_object_if(is_odd)): 124,
            }
        },
        'dropped_parent': {
            'first': { 
                ("CASE_drop_constant", M.drop_object_if(is_odd, ROL.PARENT)): 123,
            },
            'second': {
                ('CASE_keep_constant', M.drop_object_if(is_odd, ROL.PARENT)): 124,
            }
        },
        'kept_parent': {
            'second': {
                ('CASE_keep_constant', M.drop_object_if(is_odd, ROL.PARENT)): 124,
            }
        },
        'dropped_grandparent': {
            'inner': {
                'first': { 
                    ("CASE_drop_constant", M.drop_object_if(is_odd, ROL.GRANDPARENT)): 123,
                },
                'second': {
                    ('CASE_keep_constant', M.drop_object_if(is_odd, ROL.GRANDPARENT)): 124,
                }
            }
        },
        'kept_grandparent': {
            'parent': {
                'second': {
                    ('CASE_keep_constant', M.drop_object_if(is_odd, ROL.GRANDPARENT)): 124,
                }
            } 
        },
        'dropped_greatgrandparent': {
            'grandparent': {
                'parent': {
                    'first': { 
                        ("CASE_drop_constant", M.drop_object_if(is_odd, ROL.GREATGRANDPARENT)): 123,
                    },
                    'second': {
                        ('CASE_keep_constant', M.drop_object_if(is_odd, ROL.GREATGRANDPARENT)): 124,
                    }
                }
            }
        },
        'kept_greatgrandparent': {
            'grandparent': {
                'parent': {
                    'second': {
                        ('CASE_keep_constant', M.drop_object_if(is_odd, ROL.GREATGRANDPARENT)): 124,
                    }
                } 
            }
        },
        'other_val': 123
    }
    res = E.apply_mapping(source, mapping, remove_empty=True)
    assert res == {
        'parent': {
            'second': {
                'CASE_keep_constant': 124
            }
        },
        'kept_parent': {
            'second': {
                'CASE_keep_constant': 124
            }
        },
        'other_val': mapping.get('other_val'),
        'kept_grandparent': {
            'parent': {
                'second': {
                    'CASE_keep_constant': 124,
                }
            } 
        },
        'kept_greatgrandparent': {
            'grandparent': {
                'parent': {
                    'second': {
                        'CASE_keep_constant': 124,
                    }
                } 
            }
        },
    }

    # TODO: See why this breaks other tests -- remove the `ROL.ENTIRE_OBJECT` feature in the meantime
    # # Test wiping entire object if specified
    # new_mapping = {
    #     'some_parent': {
    #         'nesting': {
    #             'nesting': {
    #                 'nesting': {
    #                     ('odd', M.drop_object_if(is_odd, ROL.ENTIRE_OBJECT)): 123
    #                 }
    #             }
    #         }
    #     },
    #     'some_other_val': 124
    # }

    # res = E.apply_mapping(source, new_mapping)
    # assert res == {}