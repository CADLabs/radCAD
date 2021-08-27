import unittest
from pandas.testing import assert_frame_equal

import pandas as pd

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

from radcad.compat.cadCAD.configuration.utils import config_sim
from radcad.compat.cadCAD.configuration import Experiment as cadCADExperiment
from radcad.compat.cadCAD.engine import ExecutionMode, ExecutionContext
from radcad.compat.cadCAD.engine import Executor

from tests.test_cases import basic

def test_simulation_dataframe_structure():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment([simulation, simulation, simulation])
    data_radcad = experiment.run()

    df_radcad = pd.DataFrame(data_radcad)

    c = config_sim({
        "N": RUNS,
        "T": range(TIMESTEPS),
        "M": params
    })

    exp = cadCADExperiment()
    exp.append_configs(
        model_id = 'a',
        initial_state = states,
        partial_state_update_blocks = state_update_blocks,
        sim_configs = c
    )
    exp.append_configs(
        model_id = 'b',
        initial_state = states,
        partial_state_update_blocks = state_update_blocks,
        sim_configs = c
    )
    exp.append_configs(
        model_id = 'c',
        initial_state = states,
        partial_state_update_blocks = state_update_blocks,
        sim_configs = c
    )

    exec_mode = ExecutionMode()
    local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
    simulation = Executor(exec_context=local_mode_ctx, configs=exp.configs)

    data_cadcad, tensor_field, sessions = simulation.execute()
    df_cadcad = pd.DataFrame(data_cadcad)

    assert_frame_equal(df_radcad, df_cadcad)
    assert df_radcad.equals(df_cadcad)

def update_state_a(params, substep, state_history, previous_state, policy_input):
    return 'state_a', 1

def test_regression_lambdas():
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
    
    params = {
        'lambda_param': [lambda timestep: timestep % 5]
    }

    TIMESTEPS = 10
    RUNS = 1

    c = config_sim({
        "N": RUNS,
        "T": range(TIMESTEPS),
        "M": params
    })

    exp = cadCADExperiment()
    exp.append_configs(
        initial_state = initial_state,
        partial_state_update_blocks = state_update_blocks,
        sim_configs = c
    )

    exec_mode = ExecutionMode()
    local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
    simulation = Executor(exec_context=local_mode_ctx, configs=exp.configs)

    raw_data, tensor_field, sessions = simulation.execute(engine=Engine(backend=Backend.PATHOS))
    assert isinstance(raw_data, list)
