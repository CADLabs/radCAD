from radcad import Model, Simulation
from radcad.engine import run, Backend
from tests.test_cases import basic
import pandas as pd
import ray
import os
import pytest


RAY_ADDRESS = os.getenv('RAY_ADDRESS')
RAY_REDIS_PASSWORD = os.getenv('RAY_REDIS_PASSWORD')


@pytest.mark.skip(reason="Requires AWS credentials")
def test_run_ray_remote():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

    if not RAY_ADDRESS or not RAY_REDIS_PASSWORD:
        assert False, "RAY_ADDRESS or RAY_REDIS_PASSWORD not set"
    ray.init(address=RAY_ADDRESS, _redis_password=RAY_REDIS_PASSWORD)
    result = run(simulation, backend=Backend.RAY_REMOTE)

    df = pd.DataFrame(result)
    print(df)

    assert True
