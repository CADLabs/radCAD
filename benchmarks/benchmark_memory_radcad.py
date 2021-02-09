import pytest
import pandas as pd

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

from tests.test_cases import benchmark_model


states = benchmark_model.states
state_update_blocks = benchmark_model.state_update_blocks
params = benchmark_model.params
TIMESTEPS = 100_000
RUNS = 5

model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
experiment = Experiment([simulation])
experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)

if __name__ == "__main__":
    results = experiment.run()
    assert len(results) > 0
