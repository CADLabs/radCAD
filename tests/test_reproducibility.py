from radcad import Model, Simulation
from tests.test_cases import basic
import pandas as pd
from pandas._testing import assert_frame_equal

def test_consecutive_simulation_runs():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

    results_run_1 = pd.DataFrame(simulation.run())
    results_run_2 = pd.DataFrame(simulation.run())

    assert_frame_equal(
        results_run_1,
        results_run_2
    )
