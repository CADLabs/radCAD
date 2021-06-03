from radcad import Model, Simulation, Experiment, Engine
from radcad.engine import Backend
from tests.test_cases import basic
import pandas as pd
import os
import pytest
import logging

try:
    import ray
except ImportError:
    _has_extension = False
else:
    _has_extension = True


if not _has_extension:
    logging.warning("Optional extension dependency Ray not installed")


RAY_ADDRESS = os.getenv('RAY_ADDRESS')
RAY_REDIS_PASSWORD = os.getenv('RAY_REDIS_PASSWORD')


@pytest.mark.skipif(not RAY_ADDRESS or not RAY_REDIS_PASSWORD, reason="requires AWS credentials")
def test_run_ray_remote():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    engine = Engine(backend=Backend.RAY_REMOTE)
    experiment = Experiment(simulation, engine=engine)

    if not RAY_ADDRESS or not RAY_REDIS_PASSWORD:
        assert False, "RAY_ADDRESS or RAY_REDIS_PASSWORD not set"
    ray.init(_redis_password=RAY_REDIS_PASSWORD)
    result = experiment.run()

    df = pd.DataFrame(result)
    print(df)

    assert True
