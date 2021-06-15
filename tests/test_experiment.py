import pytest

from radcad import Model, Simulation, Experiment
from tests.test_cases import basic


states = basic.states
state_update_blocks = basic.state_update_blocks
params = basic.params
TIMESTEPS = basic.TIMESTEPS
RUNS = basic.RUNS

model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

def test_experiment_init():
    experiment = Experiment(simulations=[simulation])
    assert experiment.get_simulations() == [simulation]
    
    experiment = Experiment(simulations=simulation)
    assert experiment.get_simulations() == [simulation]

    experiment = Experiment(simulation)
    assert experiment.get_simulations() == [simulation]

    experiment = Experiment([simulation])
    assert experiment.get_simulations() == [simulation]

    with pytest.raises(Exception):
        Experiment(invalid_arg=None)

def test_add_simulations():
    experiment = Experiment()
    experiment.add_simulations([simulation, simulation])
    assert experiment.get_simulations() == [simulation, simulation]
    experiment.add_simulations(simulation)
    assert experiment.get_simulations() == [simulation, simulation, simulation]
    with pytest.raises(Exception):
        experiment.add_simulations(None)

def test_clear_simulations():
    experiment = Experiment()
    experiment.add_simulations([simulation, simulation, simulation])
    assert experiment.clear_simulations()
    assert experiment.get_simulations() == []
    assert not experiment.clear_simulations()
    assert experiment.get_simulations() == []
