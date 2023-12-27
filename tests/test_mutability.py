from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

import pandas as pd


def update_a(params, substep, state_history, previous_state, policy_input):
    a = previous_state['a']
    a.append(1)
    b = previous_state['b']
    b.append(1)
    return 'a', [0]

def test_state_mutation():
    initial_state = {
        'a': [0],
        'b': [0]
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'a': update_a,
            }
        },
        {
            'policies': {},
            'variables': {
                'a': update_a,
            }
        },
    ]

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params={})
    simulation = Simulation(model=model, timesteps=10)
    experiment = Experiment(simulation)
    experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)

    result = experiment.run()
    df = pd.DataFrame(result)

    assert not 1 in df.iloc[0]['a']
    assert not 1 in df.iloc[10]['a']
    assert not 1 in df.iloc[0]['b']
    assert not 1 in df.iloc[10]['b']

def update_a_no_deepcopy(params, substep, state_history, previous_state, policy_input):
    a = previous_state['a'].copy()
    a.append(1)
    b = previous_state['b'].copy()
    b.append(1)
    return 'a', [0]

def test_state_mutation_no_deepcopy():
    initial_state = {
        'a': [0],
        'b': [0]
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'a': update_a_no_deepcopy,
            }
        },
        {
            'policies': {},
            'variables': {
                'a': update_a_no_deepcopy,
            }
        },
    ]

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params={})
    simulation = Simulation(model=model, timesteps=10)
    experiment = Experiment(simulation)
    experiment.engine = Engine(backend=Backend.SINGLE_PROCESS, deepcopy=False)

    result = experiment.run()
    df = pd.DataFrame(result)

    assert not 1 in df.iloc[0]['a']
    assert not 1 in df.iloc[10]['a']
    assert not 1 in df.iloc[0]['b']
    assert not 1 in df.iloc[10]['b']

def policy_1_mutate_state(params, substep, state_history, previous_state):
    a = previous_state['a']
    assert not 1 in a
    a.append(1)
    return {'signal': {'x': 1}}

def policy_2_mutate_state(params, substep, state_history, previous_state):
    a = previous_state['a']
    assert not 1 in a
    a.append(1)
    return {}

def update_a_mutate_signal(params, substep, state_history, previous_state, policy_input):
    signal = policy_input['signal']
    assert signal['x'] == 1
    signal['x'] = 0
    return 'a', previous_state['a']

def update_b_mutate_signal(params, substep, state_history, previous_state, policy_input):
    signal = policy_input['signal']
    assert signal['x'] == 1
    signal['x'] = 0
    return 'b', previous_state['b']

def test_policy_state_mutation():
    initial_state = {
        'a': [0],
        'b': [0],
    }

    state_update_blocks = [
        {
            'policies': {
                'p1': policy_1_mutate_state,
                'p2': policy_2_mutate_state,
            },
            'variables': {
                'a': update_a_mutate_signal,
                'b': update_b_mutate_signal,
            }
        },
    ]

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params={})
    simulation = Simulation(model=model, timesteps=10)
    experiment = Experiment(simulation)
    experiment.engine = Engine(backend=Backend.SINGLE_PROCESS, deepcopy=True)

    result = experiment.run()
    df = pd.DataFrame(result)

    assert not 1 in df.iloc[0]['a']
    assert not 1 in df.iloc[10]['a']
    assert not 1 in df.iloc[0]['b']
    assert not 1 in df.iloc[10]['b']
