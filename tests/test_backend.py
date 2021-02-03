from radcad import Model, Simulation, Experiment, Engine
from radcad.engine import Backend
from tests.test_cases import basic

import pandas as pd
import pytest


@pytest.mark.skip(reason="issue with test")
def test_backend_equality():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    
    experiment.engine = Engine(backend=Backend.MULTIPROCESSING)
    df_multiprocessing = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.RAY)
    df_ray = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.PATHOS)
    df_pathos = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)
    df_basic = pd.DataFrame(experiment.run())

    assert df_multiprocessing.equals(df_ray)
    assert df_multiprocessing.equals(df_pathos)
    assert df_multiprocessing.equals(df_basic)

def test_backend_single_process():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    
    processes = 1

    experiment.engine = Engine(backend=Backend.MULTIPROCESSING, processes=processes)
    df_multiprocessing = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.RAY, processes=processes)
    df_ray = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.PATHOS, processes=processes)
    df_pathos = pd.DataFrame(experiment.run())

    assert df_multiprocessing.equals(df_ray)
    assert df_multiprocessing.equals(df_pathos)
