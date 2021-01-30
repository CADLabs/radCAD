from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

import pandas as pd
import pytest


a = 0

def update_a(params, substep, state_history, previous_state, policy_input):
    a = previous_state['a']
    a = a + 1
    return 'a', a

def test_basic_state_update():
    initial_state = {
        'a': a
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'a': update_a
            }
        },
    ]

    params = {}

    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    result = experiment.run()

    assert result[0]['a'] == 0
    assert result[1]['a'] == 1

    assert result[-2]['a'] == 9
    assert result[-1]['a'] == 10

def test_multiple_partial_state_updates():
    initial_state = {
        'a': 0
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'a': lambda params, substep, state_history, previous_state, policy_input: ('a', previous_state['a'] + 1),
            }
        },
        {
            'policies': {},
            'variables': {
                'a': lambda params, substep, state_history, previous_state, policy_input: ('a', previous_state['a'] + 1),
            }
        },
        {
            'policies': {},
            'variables': {
                'a': lambda params, substep, state_history, previous_state, policy_input: ('a', previous_state['a'] + 1),
            }
        },
    ]

    params = {}

    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)
    
    result = experiment.run()
    df = pd.DataFrame(result)

    assert df.query('timestep == 10 and substep == 3')['a'].item() == 30
