from radcad import Model, Simulation, Experiment
from tests.test_cases import basic
import pytest

def test_invalid_state_update_function():
    states = basic.states
    state_update_blocks = [
        {
            'policies': {
                'p': basic.policy,
            },
            'variables': {
                'a': basic.update_b
            }
        },
    ]
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)

    with pytest.raises(KeyError) as err:
        experiment.run()

def test_invalid_state():
    states = basic.states
    state_update_blocks = [
        {
            'policies': {
                'p': basic.policy,
            },
            'variables': {
                'c': basic.update_a
            }
        },
    ]
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)

    with pytest.raises(KeyError) as err:
        experiment.run()
