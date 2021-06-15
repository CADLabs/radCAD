import pytest

from radcad import Model, Simulation, Experiment
from tests.test_cases import basic


def test_simulation_init():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)

    with pytest.raises(Exception):
        Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS, invalid_arg=None)

def test_run():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation])
    
    raw_result = experiment.run()
    
    assert len(raw_result) > 0
    assert raw_result == experiment.results
    assert simulation.run() == raw_result
