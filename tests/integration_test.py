import unittest
from pandas.testing import assert_frame_equal

import pandas as pd

import output.rad_cad as rc
from output.rad_cad import Model, Simulation

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD import configs

from .test_cases import basic

class TestBasicFunctionality(unittest.TestCase):

    def test_simulation_dataframe_structure(self):
        states = basic.states
        psubs = basic.psubs
        params = basic.params
        TIMESTEPS = basic.TIMESTEPS
        RUNS = basic.RUNS

        model = Model(initial_state=states, psubs=psubs, params=params)
        simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
        data_radcad = rc.run([simulation])

        df_radcad = pd.DataFrame(data_radcad)

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

        exec_mode = ExecutionMode()
        local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
        simulation = Executor(exec_context=local_mode_ctx, configs=configs)

        data_cadcad, tensor_field, sessions = simulation.execute()
        df_cadcad = pd.DataFrame(data_cadcad)

        self.assertTrue(df_radcad.drop(['run'], axis=1).equals(df_cadcad.drop(['run'], axis=1)))

if __name__ == '__main__':
    unittest.main()
