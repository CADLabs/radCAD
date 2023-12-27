from radcad import Model, Simulation
import pandas as pd


def update_a(params, substep, state_history, previous_state, policy_input):
    return 'a', previous_state['a'] + 1

states = {
    'a': 0.0,
}

state_update_blocks = [
    {
        'policies': {},
        'variables': {
            'a': update_a
        }
    }
]

TIMESTEPS = 10
RUNS = 1


def test_set_initial_state_and_timestep_from_previous_sim():
    model_1 = Model(initial_state=states, state_update_blocks=state_update_blocks)
    simulation_1 = Simulation(model=model_1, timesteps=TIMESTEPS, runs=RUNS)
    simulation_1.run()
    df_1 = pd.DataFrame(simulation_1.results)

    assert df_1.iloc[0].timestep == 0
    assert df_1.iloc[-1].timestep == TIMESTEPS
    assert df_1.iloc[0].a == 0
    assert df_1.iloc[-1].a == 10

    model_2 = Model(initial_state=simulation_1.results[-1], state_update_blocks=state_update_blocks)
    simulation_2 = Simulation(model=model_2, timesteps=TIMESTEPS, runs=RUNS)
    simulation_2.engine.simulation_execution.result = simulation_1.results
    simulation_2.run()
    df_2 = pd.DataFrame(simulation_2.results)

    assert df_2.iloc[0].timestep == 0
    assert df_2.iloc[-1].timestep == TIMESTEPS * 2
    assert df_2.iloc[0].a == 0
    assert df_2.iloc[-1].a == 20
