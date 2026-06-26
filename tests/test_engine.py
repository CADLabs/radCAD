from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend
from tests.test_cases import basic

def test_radcad_backend_env_sets_default(monkeypatch):
    monkeypatch.setenv('RADCAD_BACKEND', 'SINGLE_PROCESS')
    assert Engine().backend == Backend.SINGLE_PROCESS


def test_radcad_backend_env_overrides_explicit_backend(monkeypatch):
    monkeypatch.setenv('RADCAD_BACKEND', 'SINGLE_PROCESS')
    assert Engine(backend=Backend.PATHOS).backend == Backend.SINGLE_PROCESS


def test_run():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = basic.TIMESTEPS
    RUNS = basic.RUNS

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation])
    experiment.run()
    assert True
