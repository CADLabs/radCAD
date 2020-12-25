from radcad.core import generate_parameter_sweep


def test_generate_parameter_sweep():
    params = {
        'a': [0],
        'b': [0]
    }
    param_sweep = generate_parameter_sweep(params)
    assert param_sweep == [{'a': 0, 'b': 0}]

    params = {
        'a': [0, 1, 2],
        'b': [0]
    }
    param_sweep = generate_parameter_sweep(params)
    assert param_sweep == [{'a': 0, 'b': 0}, {'a': 1, 'b': 0}, {'a': 2, 'b': 0}]

    params = {
        'a': [0, 1, 2],
        'b': [0, 1],
        'c': [0]
    }
    param_sweep = generate_parameter_sweep(params)
    assert param_sweep == [{'a': 0, 'b': 0, 'c': 0}, {'a': 1, 'b': 1, 'c': 0}, {'a': 2, 'b': 1, 'c': 0}]