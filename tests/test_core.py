from typing import Dict, List
from dataclasses import dataclass

from radcad.utils import _get_sweep_length, generate_parameter_sweep, _nested_asdict, default


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


def test_generate_dataclass_parameter_sweep():
    @dataclass
    class P1:
        a: List[int] = default([0])
        b: List[int] = default([0])
    param_sweep = generate_parameter_sweep(P1())
    assert param_sweep == [P1(**{'a': 0, 'b': 0})]

    @dataclass
    class P2:
        a: List[int] = default([0, 1, 2])
        b: List[int] = default([0])
    param_sweep = generate_parameter_sweep(P2())
    assert param_sweep == [P2(**{'a': 0, 'b': 0}), P2(**{'a': 1, 'b': 0}), P2(**{'a': 2, 'b': 0})]

    @dataclass
    class P3:
        a: List[int] = default([0, 1, 2])
        b: List[int] = default([0, 1])
        c: List[int] = default([0])
    param_sweep = generate_parameter_sweep(P3())
    assert param_sweep == [P3(**{'a': 0, 'b': 0, 'c': 0}), P3(**{'a': 1, 'b': 1, 'c': 0}), P3(**{'a': 2, 'b': 1, 'c': 0})]


nested_params = {
    'a': {
        'b': 1,
        'c': [2, 0, 0, 0, 0],
        'd': {
            'e': [3, 4, 0, 0],
            'f': 5
        }
    },
    'g': [6, 7, 8],
    'h': 9
}

@dataclass
class D:
    e: List = default([3, 4, 0, 0])
    f: int = 5

@dataclass
class I:
    j: Dict = default({
        'k': 9
    })

@dataclass
class H:
    i: I = default(I())

@dataclass
class NestedDataclassParams:
    a: Dict = default({
        'b': 1,
        'c': [2, 0, 0, 0, 0],
        'd': D(),
    })
    g: List = default([6, 7, 8])
    h: H = default(H())
    l: int = 10
    m: D = default(D())

nested_dataclass_params = NestedDataclassParams()


def test_nested_asdict():
    assert _nested_asdict(nested_dataclass_params) == {
        'a': {'b': 1, 'c': [2, 0, 0, 0, 0], 'd': D()},
        'g': [6, 7, 8],
        'h': {'i': {'j': {'k': 9}}},
        'l': 10,
        'm': {'e': [3, 4, 0, 0], 'f': 5}
    }


def test_get_sweep_len():
    assert _get_sweep_length(nested_params) == 3
    assert _get_sweep_length(nested_dataclass_params) == 4


def test_generate_nested_parameter_sweep():
    assert _get_sweep_length(nested_params) == 3

    assert generate_parameter_sweep(nested_params) == [
        {
            'a': {
                'b': 1,
                'c': [2, 0, 0, 0, 0],
                'd': {
                    'e': [3, 4, 0, 0],
                    'f': 5
                }
            },
            'g': 6,
            'h': 9
        },
        {
            'a': {
                'b': 1,
                'c': [2, 0, 0, 0, 0],
                'd': {
                    'e': [3, 4, 0, 0],
                    'f': 5
                }
            },
            'g': 7,
            'h': 9
        },
        {
            'a': {
                'b': 1,
                'c': [2, 0, 0, 0, 0],
                'd': {
                    'e': [3, 4, 0, 0],
                    'f': 5
                }
            },
            'g': 8,
            'h': 9
        },
    ]


def test_generate_nested_dataclass_parameter_sweep():
    parameter_sweep = generate_parameter_sweep(nested_dataclass_params)
    assert parameter_sweep == [
        NestedDataclassParams(a={'b': 1, 'c': [2, 0, 0, 0, 0], 'd': D(e=[3, 4, 0, 0], f=5)}, g=6, h=H(i=I(j={'k': 9})), l=10, m=D(e=3, f=5)),
        NestedDataclassParams(a={'b': 1, 'c': [2, 0, 0, 0, 0], 'd': D(e=[3, 4, 0, 0], f=5)}, g=7, h=H(i=I(j={'k': 9})), l=10, m=D(e=4, f=5)),
        NestedDataclassParams(a={'b': 1, 'c': [2, 0, 0, 0, 0], 'd': D(e=[3, 4, 0, 0], f=5)}, g=8, h=H(i=I(j={'k': 9})), l=10, m=D(e=0, f=5)),
        NestedDataclassParams(a={'b': 1, 'c': [2, 0, 0, 0, 0], 'd': D(e=[3, 4, 0, 0], f=5)}, g=8, h=H(i=I(j={'k': 9})), l=10, m=D(e=0, f=5))
    ]


def test_no_sweep_of_dict():
    @dataclass
    class P0:
        a: Dict = default({0: [1, 2, 3]})
        b: List = 1

    @dataclass
    class P1:
        c: List = 1

    @dataclass
    class P:
        p0: P0 = default(P0())
        p1: P1 = default(P1())

    param_sweep = generate_parameter_sweep(P())
    assert param_sweep == [
        P(
            p0 = P0(
                a = {0: [1, 2, 3]},
                b = 1
            ),
            p1 = P1(
                c = 1
            )
        ),
    ]

def test_generate_single_value_dataclass_parameter_sweep():
    @dataclass
    class P0:
        a: int = 0
        b: int = 0
    param_sweep = generate_parameter_sweep(P0())
    assert param_sweep == [P0(**{'a': 0, 'b': 0})]

    @dataclass
    class P1:
        a: List[int] = default([0])
        b: int = 0
    param_sweep = generate_parameter_sweep(P1())
    assert param_sweep == [P1(**{'a': 0, 'b': 0})]

    @dataclass
    class P2:
        a: List[int] = default([0, 1, 2])
        b: int = 0
    param_sweep = generate_parameter_sweep(P2())
    assert param_sweep == [P2(**{'a': 0, 'b': 0}), P2(**{'a': 1, 'b': 0}), P2(**{'a': 2, 'b': 0})]

    @dataclass
    class P3:
        a: List[int] = default([0, 1, 2])
        b: List[int] = default([0, 1])
        c: int = 0
    param_sweep = generate_parameter_sweep(P3())
    assert param_sweep == [P3(**{'a': 0, 'b': 0, 'c': 0}), P3(**{'a': 1, 'b': 1, 'c': 0}), P3(**{'a': 2, 'b': 1, 'c': 0})]


def test_generate_single_value_parameter_sweep():
    params = {
        'a': 0,
        'b': 0
    }
    param_sweep = generate_parameter_sweep(params)
    assert param_sweep == [{'a': 0, 'b': 0}]

    params = {
        'a': [0, 1, 2],
        'b': 0
    }
    param_sweep = generate_parameter_sweep(params)
    assert param_sweep == [{'a': 0, 'b': 0}, {'a': 1, 'b': 0}, {'a': 2, 'b': 0}]

    params = {
        'a': [0, 1, 2],
        'b': [0, 1],
        'c': 0
    }
    param_sweep = generate_parameter_sweep(params)
    assert param_sweep == [{'a': 0, 'b': 0, 'c': 0}, {'a': 1, 'b': 1, 'c': 0}, {'a': 2, 'b': 1, 'c': 0}]
