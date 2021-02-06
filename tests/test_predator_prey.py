import unittest
import pytest
from pandas.testing import assert_frame_equal

import pandas as pd

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment as cadCADExperiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD import configs

from tests.test_cases.predator_prey_model import *


@pytest.mark.skip(reason="issue in remote test environment")
def test_simulation_dataframe_structure():
    model = Model(initial_state=initial_state, params=params, state_update_blocks=state_update_blocks)
    simulation_radcad = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)
    experiment = Experiment(simulation_radcad)
    experiment.engine = Engine()

    result_radcad = experiment.run()
    
    df = pd.DataFrame(result_radcad)
    print(df)
    df_radcad = run.postprocessing(df)
    
    c = config_sim({
        "N": MONTE_CARLO_RUNS,
        "T": range(TIMESTEPS),
        "M": params
    })

    exp = cadCADExperiment()
    del configs[:]
    exp.append_configs(
        initial_state = initial_state,
        partial_state_update_blocks = state_update_blocks,
        sim_configs = c
    )

    exec_mode = ExecutionMode()
    local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
    simulation_cadcad = Executor(exec_context=local_mode_ctx, configs=configs)

    data_cadcad, tensor_field, sessions = simulation_cadcad.execute()

    df = pd.DataFrame(data_cadcad)
    print(df)
    df_cadcad = run.postprocessing(df)
    
    assert_frame_equal(df_radcad, df_cadcad)
    assert df_radcad.equals(df_cadcad)
