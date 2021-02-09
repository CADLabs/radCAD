import pytest
import pandas as pd

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment as cadCADExperiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD import configs

from tests.test_cases import benchmark_model


states = benchmark_model.states
state_update_blocks = benchmark_model.state_update_blocks
params = benchmark_model.params
TIMESTEPS = 100_000
RUNS = 5

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

if __name__ == "__main__":
    results, _, _ = simulation.execute()
    assert len(results) > 0
