import unittest
from pandas.testing import assert_frame_equal

import pandas as pd

from radcad import Model, Simulation, Experiment

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment as cadCADExperiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD import configs

from tests.test_cases import basic

def test_simulation_dataframe_structure():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    data_radcad = experiment.run()

    df_radcad = pd.DataFrame(data_radcad)

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

    exec_mode = ExecutionMode()
    local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
    simulation = Executor(exec_context=local_mode_ctx, configs=configs)

    data_cadcad, tensor_field, sessions = simulation.execute()
    df_cadcad = pd.DataFrame(data_cadcad)

    assert_frame_equal(df_radcad, df_cadcad)
    assert df_radcad.equals(df_cadcad)
