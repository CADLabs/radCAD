from radcad import Model, Simulation
from radcad.engine import Backend, run
from tests.test_cases import basic
import pandas as pd


def test_backend_equality():
    states = basic.states
    psubs = basic.psubs
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, psubs=psubs, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    
    df_multiprocessing = pd.DataFrame(run([simulation], backend=Backend.MULTIPROCESSING))
    df_ray = pd.DataFrame(run([simulation], backend=Backend.RAY))
    df_pathos = pd.DataFrame(run([simulation], backend=Backend.PATHOS))

    assert df_multiprocessing.equals(df_ray)
    assert df_multiprocessing.equals(df_pathos)

def test_backend_single_process():
    states = basic.states
    psubs = basic.psubs
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, psubs=psubs, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    
    processes = 1
    df_multiprocessing = pd.DataFrame(run([simulation], backend=Backend.MULTIPROCESSING, processes=processes))
    df_ray = pd.DataFrame(run([simulation], backend=Backend.RAY, processes=processes))
    df_pathos = pd.DataFrame(run([simulation], backend=Backend.PATHOS, processes=processes))

    assert df_multiprocessing.equals(df_ray)
    assert df_multiprocessing.equals(df_pathos)
