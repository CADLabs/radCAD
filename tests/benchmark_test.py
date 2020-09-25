import pytest

import pandas as pd

import output.rad_cad as rc
from output.rad_cad import Model, Simulation

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD import configs

from test_cases import benchmark_model

states = benchmark_model.states
psubs = benchmark_model.psubs
params = benchmark_model.params
TIMESTEPS = benchmark_model.TIMESTEPS
RUNS = benchmark_model.RUNS

model = Model(initial_state=states, psubs=psubs, params=params)
simulation_radcad = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

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
simulation_cadcad = Executor(exec_context=local_mode_ctx, configs=configs)

def test_benchmark_radcad(benchmark):
    benchmark.pedantic(radcad_simulation, iterations=1, rounds=5)
    
def test_benchmark_cadcad(benchmark):
    benchmark.pedantic(cadcad_simulation, iterations=1, rounds=5)

def radcad_simulation():
    data_radcad = rc.run([simulation_radcad])

def cadcad_simulation():
    data_cadcad, tensor_field, sessions = simulation_cadcad.execute()
