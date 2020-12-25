from radcad import Model, Simulation
from radcad.engine import run
from tests.test_cases import basic

def test_run():
    states = basic.states
    psubs = basic.psubs
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, psubs=psubs, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    run(simulation)
    run([simulation])

    assert True
