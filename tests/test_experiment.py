from radcad import Model, Simulation, Experiment, Engine
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

def test_add_simulations():
    experiment = Experiment()
    experiment.add_simulations([simulation, simulation, simulation])
    assert experiment.get_simulations() == [simulation, simulation, simulation]

def test_clear_simulations():
    experiment = Experiment()
    experiment.add_simulations([simulation, simulation, simulation])
    assert experiment.clear_simulations()
    assert experiment.get_simulations() == []
    assert not experiment.clear_simulations()
    assert experiment.get_simulations() == []

def test_hooks(capfd):
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=3)
    experiment = Experiment(simulation)

    experiment.before_experiment = lambda engine=None: print(f"Before experiment with {len(engine.experiment.simulations)} simulations")
    experiment.after_experiment = lambda engine=None: print(f"After experiment with {len(engine.experiment.simulations)} simulations")
    experiment.before_simulation = lambda simulation=None, simulation_index=-1: print(f"Before simulation {simulation_index} with params {simulation.model.params}")
    experiment.after_simulation = lambda simulation=None, simulation_index=-1: print(f"After simulation {simulation_index} with params {simulation.model.params}")
    experiment.before_run = lambda run_index=-1, simulation=None: print(f"Before run {run_index}")
    experiment.after_run = lambda run_index=-1, simulation=None: print(f"After run {run_index}")
    
    experiment.run()
    # out, err = capfd.readouterr()

    assert True
