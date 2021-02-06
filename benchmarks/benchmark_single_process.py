import pytest

import pandas as pd

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment as cadCADExperiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD import configs

from tests.test_cases import benchmark_model

states = benchmark_model.states
state_update_blocks = benchmark_model.state_update_blocks
params = benchmark_model.params
TIMESTEPS = benchmark_model.TIMESTEPS
RUNS = benchmark_model.RUNS

model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
simulation_radcad = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
experiment = Experiment(simulation_radcad)
experiment.engine = Engine(backend=Backend.BASIC)

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
local_mode_ctx = ExecutionContext(context=exec_mode.single_proc)
simulation_cadcad = Executor(exec_context=local_mode_ctx, configs=configs)

def test_benchmark_radcad(benchmark):
    benchmark.pedantic(radcad_simulation, iterations=1, rounds=3)
    
def test_benchmark_cadcad(benchmark):
    benchmark.pedantic(cadcad_simulation, iterations=1, rounds=3)

def radcad_simulation():
    data_radcad = experiment.run()

def cadcad_simulation():
    data_cadcad, tensor_field, sessions = simulation_cadcad.execute()
