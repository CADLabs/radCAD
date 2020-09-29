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

psubs = [
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
RUNS = 1

import radCAD as rc
from radCAD import Model, Simulation

model = Model(initial_state=states, psubs=psubs, params=params)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

start = time.time()
data_rc = rc.run([simulation, simulation, simulation, simulation, simulation])
end = time.time()

duration_radcad = end - start
print(duration_radcad)

df_radcad = pd.DataFrame(data_rc)
print(df_radcad)

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

from cadCAD import configs
del configs[:] # Clear any prior configs

c = config_sim({
    "N": RUNS,
    "T": range(TIMESTEPS),
    "M": params
})

exp = Experiment()
exp.append_configs(
    initial_state = states,
    partial_state_update_blocks = psubs,
    sim_configs = c
)

exp.append_configs(
    initial_state = states,
    partial_state_update_blocks = psubs,
    sim_configs = c
)

exp.append_configs(
    initial_state = states,
    partial_state_update_blocks = psubs,
    sim_configs = c
)

exp.append_configs(
    initial_state = states,
    partial_state_update_blocks = psubs,
    sim_configs = c
)

exp.append_configs(
    initial_state = states,
    partial_state_update_blocks = psubs,
    sim_configs = c
)

exec_mode = ExecutionMode()
local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
simulation = Executor(exec_context=local_mode_ctx, configs=configs)

start = time.time()
data, tensor_field, sessions = simulation.execute()
end = time.time()

duration_cadcad = end - start
print(duration_cadcad)

df_cadcad = pd.DataFrame(data)
print(df_cadcad)

from pandas.testing import assert_frame_equal
assert_frame_equal(df_radcad.drop(['run'], axis=1), df_cadcad.drop(['run'], axis=1))

print()
print(f'radCAD took {duration_radcad} seconds')
print(f'cadCAD took {duration_cadcad} seconds')
print(f'Simulation output dataframes are carbon copies')
print(f'Rust is {duration_cadcad / duration_radcad}X faster than Python')
