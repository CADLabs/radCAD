import pandas as pd
import time

import math

def policy(params, substep, state_history, previous_state):
    return {'step_size': 1}

def update_a(params, substep, state_history, previous_state, policy_input):
    a = b = c = d = e = 100.0
    return 'a', previous_state['a'] * abs(math.cos(previous_state['a']))

def update_b(params, substep, state_history, previous_state, policy_input):
    return 'b', previous_state['b'] + policy_input['step_size'] * params['a']

params = {
    'a': [1, 2],
    'b': [1]
}

states = {
    'a': 1.0,
    'b': 2.0
}

state_update_blocks = [
    {
        'policies': {},
        'variables': {
            'a': update_a
        }
    },
    {
        'policies': {
            'p_1': policy,
            'p_2': policy,
            'p_3': policy,
            'p_4': policy,
            'p_5': policy,
        },
        'variables': {
            'b': update_b
        }
    }
]

TIMESTEPS = 100_000
RUNS = 2

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment as cadCADExperiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

from cadCAD import configs
del configs[:] # Clear any prior configs

from pandas.testing import assert_frame_equal

if __name__ == '__main__':
    # radCAD

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment([simulation, simulation])
    experiment.engine = Engine(backend=Backend.BASIC)

    start = time.time()
    data_rc = experiment.run()
    end = time.time()

    duration_radcad = end - start

    df_radcad = pd.DataFrame(data_rc)
    print(df_radcad)

    # cadCAD

    c = config_sim({
        "N": RUNS,
        "T": range(TIMESTEPS),
        "M": params
    })

    exp = cadCADExperiment()
    exp.append_configs(
        initial_state = states,
        partial_state_update_blocks = state_update_blocks,
        sim_configs = c
    )

    exp.append_configs(
        initial_state = states,
        partial_state_update_blocks = state_update_blocks,
        sim_configs = c
    )

    exec_mode = ExecutionMode()
    local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
    simulation = Executor(exec_context=local_mode_ctx, configs=configs)

    start = time.time()
    data, tensor_field, sessions = simulation.execute()
    end = time.time()

    duration_cadcad = end - start

    df_cadcad = pd.DataFrame(data)
    print(df_cadcad)

    assert_frame_equal(df_radcad.drop(['run'], axis=1), df_cadcad.drop(['run'], axis=1))

    print()
    print(f'radCAD took {duration_radcad} seconds')
    print(f'cadCAD took {duration_cadcad} seconds')
    print(f'Simulation output dataframes are carbon copies')
    print(f'Rust is {duration_cadcad / duration_radcad}X faster than Python')
