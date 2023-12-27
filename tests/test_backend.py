from radcad import Model, Simulation, Experiment, Engine
from radcad.engine import Backend
from tests.test_cases import basic

import pandas as pd
from pandas._testing import assert_frame_equal

try:
    import ray
except ImportError:
    _has_ray_extension = False
else:
    _has_ray_extension = True


def test_backend_equality():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = 10 #basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    
    experiment.engine = Engine(backend=Backend.MULTIPROCESSING)
    df_multiprocessing = pd.DataFrame(experiment.run())

    if _has_ray_extension:
        experiment.engine = Engine(backend=Backend.RAY)
        df_ray = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.PATHOS)
    df_pathos = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)
    df_single_process = pd.DataFrame(experiment.run())

    if _has_ray_extension: assert df_multiprocessing.equals(df_ray)
    assert_frame_equal(df_multiprocessing, df_pathos)
    assert_frame_equal(df_multiprocessing, df_single_process)

def test_backend_single_process():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = 10 #basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    
    processes = 1

    experiment.engine = Engine(backend=Backend.MULTIPROCESSING, processes=processes)
    df_multiprocessing = pd.DataFrame(experiment.run())

    if _has_ray_extension:
        experiment.engine = Engine(backend=Backend.RAY, processes=processes)
        df_ray = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.PATHOS, processes=processes)
    df_pathos = pd.DataFrame(experiment.run())

    experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)
    df_single_process = pd.DataFrame(experiment.run())

    if _has_ray_extension: assert df_multiprocessing.equals(df_ray)
    assert_frame_equal(df_multiprocessing, df_pathos)
    assert_frame_equal(df_multiprocessing, df_single_process)
