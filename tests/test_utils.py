from radcad.utils import generate_cartesian_product_parameter_sweep


def test_generate_cartesian_product_parameter_sweep():
    params = {
        'a': [0],
        'b': [0, 1],
        'c': [0, 1, 2],
    }
    sweep = generate_cartesian_product_parameter_sweep(params)
    assert sweep == {
        'a': [0, 0, 0, 0, 0, 0],
        'b': [0, 0, 0, 1, 1, 1],
        'c': [0, 1, 2, 0, 1, 2]
    }
