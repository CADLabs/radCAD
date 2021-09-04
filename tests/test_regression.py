from radcad import Model, Simulation, Experiment

import pytest
import pandas as pd
import copy


def update_state_a(params, substep, state_history, previous_state, policy_input):
    return 'state_a', 1

def test_regression_state_names():
    # Test that state names of more than one charachter don't fail!
    initial_state = {
        'state_a': 0
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'state_a': update_state_a
            }
        },
    ]

    params = {}

    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)

    assert isinstance(experiment.run(), list)

def policy_a(params, substep, state_history, previous_state):
    return {'signal_a': 0}

def update_a(params, substep, state_history, previous_state, policy_input):
    return 'a', 1

def test_regression_policy_names():
    initial_state = {
        'a': 0
    }

    state_update_blocks = [
        {
            'policies': {
                'policy': policy_a
            },
            'variables': {
                'a': update_a
            }
        },
    ]

    params = {
        'param_a': [0]
    }

    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)

    assert isinstance(experiment.run(), list)

def policy_two_signals(params, substep, state_history, previous_state):
    return {'signal_a': 1, 'signal_b': 1}

def update_a_from_signal(params, substep, state_history, previous_state, policy_input):
    return 'a', previous_state['a'] + policy_input.get('signal_a', 0)

def update_b_from_signal(params, substep, state_history, previous_state, policy_input):
    return 'b', previous_state['b'] + policy_input.get('signal_b', 0)

def test_regression_policy_signals():
    initial_state = {
        'a': 0,
        'b': 0
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'a': update_a_from_signal,
                'b': update_b_from_signal
            }
        },
        {
            'policies': {
                'policy': policy_two_signals
            },
            'variables': {
                'a': update_a_from_signal,
                'b': update_b_from_signal
            }
        },
    ]

    params = {}

    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    result = simulation.run()

    df = pd.DataFrame(result)
    assert df.query('timestep == 10 and substep == 2')['a'].item() == 10

def test_paralell_state_update():
    def update_a(params, substep, state_history, previous_state, policy_input):
        if previous_state['timestep'] == 1: assert previous_state['b'] == 0
        return 'a', previous_state['a'] + 1

    def update_b(params, substep, state_history, previous_state, policy_input):
        if previous_state['timestep'] == 1: assert previous_state['a'] == 0
        return 'b', previous_state['b'] + 1

    initial_state = {
        'a': 0,
        'b': 0
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'a': update_a,
                'b': update_b
            }
        },
    ]

    params = {}

    TIMESTEPS = 1
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    result = simulation.run()
    df = pd.DataFrame(result)

def test_regression_deepcopy():
    initial_state = {
        'state_a': 0
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'state_a': update_state_a
            }
        },
    ]

    params = {}

    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model)
    experiment = Experiment(simulation)

    simulation.run()
    _ = copy.deepcopy(simulation)
