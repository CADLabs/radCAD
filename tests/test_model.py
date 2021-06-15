import pandas as pd
from pandas._testing import assert_frame_equal

from radcad import Model, Simulation, Experiment
import radcad.utils as utils
from tests.test_cases import basic


def test_model_call_method():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    # Test Model __call__() method configuration
    model(
        drop_substeps=True,
        deepcopy=False,
        raise_exceptions=False,
    )

def test_model_generator():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = 10
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation])
    
    raw_result_experiment = experiment.run()
    # The Model generator doesn't handle parameter sweeps, and only executes one run
    df_experiment = pd.DataFrame(raw_result_experiment).query('run == 1 and subset == 0')
    
    assert len(raw_result_experiment) > 0
    assert raw_result_experiment == experiment.results
    assert simulation.run() == raw_result_experiment
    
    # Create a generator from the Model instance
    model_generator = iter(model)
    raw_result_model = []
    # Set initial state
    raw_result_model.append(model.state)

    # Emulate the behaviour of the radCAD Engine
    for t in range(TIMESTEPS):
        _model = next(model_generator)
        raw_result_model.append(_model.substeps)

    # Flatten the results
    raw_result_model = utils.flatten(raw_result_model)
    df_model = pd.DataFrame(raw_result_model)

    assert_frame_equal(df_experiment, df_model)
