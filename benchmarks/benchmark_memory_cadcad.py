import pytest
import pandas as pd

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment as cadCADExperiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

import tests.test_cases.predator_prey_model as benchmark_model


initial_state = benchmark_model.initial_state
state_update_blocks = benchmark_model.state_update_blocks
params = benchmark_model.params
TIMESTEPS = 1000
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
local_mode_ctx = ExecutionContext()
simulation = Executor(exec_context=local_mode_ctx, configs=exp.configs)

if __name__ == "__main__":
    results, _, _ = simulation.execute()
    assert len(results) > 0
