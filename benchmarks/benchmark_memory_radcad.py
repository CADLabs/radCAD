import pytest
import pandas as pd

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

import tests.test_cases.predator_prey_model as benchmark_model


initial_state = benchmark_model.initial_state
state_update_blocks = benchmark_model.state_update_blocks
params = benchmark_model.params
TIMESTEPS = 1000
RUNS = 1

model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
experiment = Experiment([simulation])
experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)

if __name__ == "__main__":
    results = experiment.run()
    assert len(results) > 0
