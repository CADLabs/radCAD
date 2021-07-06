import pytest

from radcad import Model, Simulation, Experiment
from radcad.wrappers import Executable
from tests.test_cases import basic


def test_run_method_implementation():
    class ExecutableClass(Executable):
        def __init__(self):
            return
    with pytest.raises(NotImplementedError):
        ex = ExecutableClass()
        ex.run()


def test_base_results():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment([simulation])
    
    simulation_results = simulation.run()
    experiment_results = experiment.run()

    # Check Executable results & exceptions
    assert simulation_results == experiment_results
    assert simulation.results == experiment.results
    assert simulation.exceptions == experiment.exceptions
