from pydian.lib.util import remove_empty_values

def test_removing_empty_values():
    # For each test case, tuple format: (input, expected_output)
    test_cases = [
        # List cases
        ([[]], []),
        (['a', [], None], ['a']),
        # Dict cases
        ({'empty_list': [], 'empty_dict': {}}, {}),
        ({'empty_list': [], 'empty_dict': {}, 'a': 'b'}, {'a': 'b'})
        # Nested cases
    ]

    for init, expected_out in test_cases:
        assert remove_empty_values(init) == expected_out
    