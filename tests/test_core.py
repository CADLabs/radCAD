from typing import List
import pytest
from dataclasses import dataclass

import radcad.core as core
from radcad.core import generate_parameter_sweep, reduce_signals

from radcad import Model, Simulation, Experiment
from radcad.engine import flatten
from radcad.utils import default

from tests.test_cases import basic


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


def test_generate_single_value_dataclass_parameter_sweep():
    @dataclass
    class P1:
        a: int = 0
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


def test_reduce_signals():
    psu = {
        'policies': {
            '1': lambda params, substep, state_history, previous_state: {'signal_a': 1.0, 'signal_b': 100.0, 'signal_d': 0.00000000011111},
            '2': lambda params, substep, state_history, previous_state: {'signal_a': 1.0, 'signal_b': -100.0, 'signal_d': 0.00000000011111},
            '3': lambda params, substep, state_history, previous_state: {'signal_a': 1.0, 'signal_c': 100e52, 'signal_d': 0.00000000011111},
            '4': lambda params, substep, state_history, previous_state: {},
        },
        'variables': {}
    }

    signals = reduce_signals({}, 1, [], {}, psu)
    assert signals['signal_a'] == 3.0
    assert signals['signal_b'] == 0
    assert signals['signal_c'] == 100e52
    assert signals['signal_d'] == 3.3333000000000003e-10

@pytest.mark.skip(reason="deprecated API")
def test_run():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)

    assert flatten(core.run([simulation])) == experiment.run()
