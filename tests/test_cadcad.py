import unittest
from pandas.testing import assert_frame_equal

import pandas as pd

from radcad import Model, Simulation, Experiment

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment as cadCADExperiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

from tests.test_cases import basic

def test_simulation_dataframe_structure():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = 1000
    RUNS = 1

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment([simulation, simulation, simulation])
    data_radcad = experiment.run()

    df_radcad = pd.DataFrame(data_radcad).drop(['run'], axis=1)

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
    df_cadcad = pd.DataFrame(data_cadcad).drop(['run'], axis=1)

    assert_frame_equal(df_radcad, df_cadcad)
    assert df_radcad.equals(df_cadcad)
