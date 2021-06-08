from radcad import Model, Simulation, Experiment
from tests.test_cases import basic

def test_base_results():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    
    results = simulation.run()

    # Check Base class
    assert simulation.results == results
    assert simulation.results == simulation.experiment.results
    assert simulation.exceptions == simulation.experiment.exceptions
