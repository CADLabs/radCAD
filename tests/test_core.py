import radcad.core as core
from radcad.core import generate_parameter_sweep

from radcad import Model, Simulation, Experiment
from radcad.engine import flatten
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
