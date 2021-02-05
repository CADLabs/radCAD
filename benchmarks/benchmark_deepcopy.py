import pytest
import pandas as pd

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine

from tests.test_cases import benchmark_model

states = benchmark_model.states
state_update_blocks = benchmark_model.state_update_blocks
params = benchmark_model.params
TIMESTEPS = 100_000
RUNS = 3

model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
simulation_radcad = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
experiment = Experiment([simulation_radcad, simulation_radcad, simulation_radcad])

def test_benchmark_radcad_no_deepcopy(benchmark):
    benchmark.pedantic(radcad_no_deecopy_simulation, iterations=1, rounds=3)

def radcad_no_deecopy_simulation():
    experiment.engine = Engine(deepcopy=False)
    data_radcad = experiment.run()

def test_benchmark_radcad_with_deepcopy(benchmark):
    benchmark.pedantic(radcad_with_deecopy_simulation, iterations=1, rounds=3)

def radcad_with_deecopy_simulation():
    experiment.engine = Engine(deepcopy=True)
    data_radcad = experiment.run()
