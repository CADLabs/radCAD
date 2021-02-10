from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend
from tests.test_cases import basic

import pandas as pd 


def test_run():
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = basic.params
    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation])
    experiment.engine = Engine(drop_substeps=True)
    
    drop_substeps_result = pd.DataFrame(experiment.run())
    
    simulation_result = pd.DataFrame(simulation.run())
    keep = (simulation_result.substep == simulation_result['substep'].max())
    keep |= (simulation_result.substep == 0)
    simulation_result = simulation_result.loc[keep]
    
    assert simulation_result.reset_index(drop=True).equals(drop_substeps_result.reset_index(drop=True))
