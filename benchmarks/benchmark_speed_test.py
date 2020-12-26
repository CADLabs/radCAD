import pytest

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
state_update_blocks = basic.state_update_blocks
params = basic.params
TIMESTEPS = 10_000
RUNS = 10

model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
simulation_radcad = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

def test_benchmark_radcad(benchmark):
    benchmark.pedantic(radcad_simulation, iterations=1, rounds=10)

def radcad_simulation():
    data_radcad = run([simulation_radcad])
