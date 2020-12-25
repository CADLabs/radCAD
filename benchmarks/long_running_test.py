import pytest
import unittest
from pandas.testing import assert_frame_equal
import sys

import pandas as pd

from radcad import Model, Simulation
from radcad.engine import run

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD import configs

from tests.test_cases import basic

states = basic.states
psubs = basic.psubs
params = basic.params
TIMESTEPS = sys.maxsize
RUNS = 1

class TestLongRunningSimulation(unittest.TestCase):

    def test_long_running_simulation_radcad(self):
        model = Model(initial_state=states, psubs=psubs, params=params)
        simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
        run([simulation])

        self.assertTrue(True)

    @pytest.mark.skip(reason="Only a single long running test can run at a time")
    def test_long_running_simulation_cadcad(self):
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

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
