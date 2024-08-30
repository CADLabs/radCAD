import pytest
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine
from tests.test_cases import basic

import pandas as pd
import datetime


def save_to_HDF5(experiment, store_file_name, store_key):
    now = datetime.datetime.now()
    store = pd.HDFStore(store_file_name)
    store.put(store_key, pd.DataFrame(experiment.results))
    store.get_storer(store_key).attrs.metadata = {
        'date': now.isoformat()
    }
    store.close()
    print(f"Saved experiment results to HDF5 store file {store_file_name} with key {store_key}")

@pytest.mark.skip(reason="failing for Python 3.12")
def test_to_HDF5():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

    HDF5_store_file = 'experiment_results.hdf5'
    
    experiment = Experiment(simulations=[simulation])
    experiment.after_experiment = lambda experiment: save_to_HDF5(experiment, HDF5_store_file, 'experiment_0')

    raw_result = experiment.run()

    df = pd.read_hdf(HDF5_store_file, 'experiment_0')
    assert df.equals(pd.DataFrame(raw_result))

    experiment = Experiment(simulations=[simulation])
    experiment.after_experiment = lambda experiment: save_to_HDF5(experiment, HDF5_store_file, 'experiment_1')

    raw_result = experiment.run()

    df = pd.read_hdf(HDF5_store_file, 'experiment_1')
    assert df.equals(pd.DataFrame(raw_result))
    
    assert len(raw_result) > 0
    assert raw_result == experiment.results
    assert simulation.run() == raw_result
