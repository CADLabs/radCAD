from radcad import Model, Simulation
from radcad.engine import run
from tests.test_cases import basic
import pytest

def test_invalid_state_update_function():
    states = basic.states
    psubs = [
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

    model = Model(initial_state=states, psubs=psubs, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

    with pytest.raises(KeyError) as err:
        run(simulation)

def test_invalid_state():
    states = basic.states
    psubs = [
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

    model = Model(initial_state=states, psubs=psubs, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

    with pytest.raises(KeyError) as err:
        run(simulation)
