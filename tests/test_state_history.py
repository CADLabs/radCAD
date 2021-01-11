from radcad import Model, Simulation, Experiment
import pytest
import pandas as pd


def update_a(params, substep, state_history, previous_state, policy_input):
    for substates in state_history:
        for state in substates:
            assert state.get('a', False)
    return 'a', 1

def test_state_history():
    initial_state = {
        'a': 1,
        'b': 1
    }

    state_update_blocks = [
        {
            'policies': {},
            'variables': {
                'a': update_a
            }
        },
        {
            'policies': {},
            'variables': {
                'a': update_a
            }
        },
    ]

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params={})
    simulation = Simulation(model=model, timesteps=10)

    result = simulation.run()

    assert True
