from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend
import pytest
import logging

FORMAT = '%(levelname)s %(name)s %(asctime)-15s %(filename)s:%(lineno)d %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel(logging.INFO)


def update_state_a(params, substep, state_history, previous_state, policy_input):
    raise Exception('Forced exception from state update function')
    return 'state_a', 1

def test_state_update_exception():
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

    with pytest.raises(RuntimeError) as e:
        result = simulation.run()
    assert str(e.value) == "Forced exception from state update function"

def policy_function_raises(params, substep, state_history, previous_state):
    raise Exception('Forced exception from policy function')
    return {'signal', 1}

def test_policy_exception():
    initial_state = {
        'state_a': 0
    }

    state_update_blocks = [
        {
            'policies': {
                'p1': policy_function_raises
            },
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

    with pytest.raises(RuntimeError) as e:
        result = simulation.run()
    assert str(e.value) == "Forced exception from policy function"

def policy_function_invalid_result(params, substep, state_history, previous_state):
    return 'a', 1

def test_policy_result_type_error():
    initial_state = {
        'state_a': 0
    }

    state_update_blocks = [
        {
            'policies': {
                'p1': policy_function_invalid_result
            },
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

    with pytest.raises(RuntimeError) as e:
        result = simulation.run()
    assert str(e.value) == "Failed to extract policy function result as dictionary"

def update_state_invalid_result(params, substep, state_history, previous_state, policy_input):
    return {'state_a', 1}

def test_state_update_result_type_error():
    initial_state = {
        'state_a': 0
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'state_a': update_state_invalid_result
            }
        },
    ]

    params = {}

    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

    with pytest.raises(RuntimeError) as e:
        result = simulation.run()
    assert str(e.value) == "Failed to extract state update function result as tuple"