import pandas as pd

from radcad import Model, Simulation, Experiment, Engine, Backend


global timesteps
global substeps

timesteps = []
substeps = []


def policy_check_timestep_substep(params, substep, state_history, previous_state):
    timestep = previous_state["timestep"]
    substep = previous_state["substep"]

    return {"timestep": timestep, "substep": substep}

def update_check_timestep_substep(params, substep, state_history, previous_state, policy_input):
    timestep = previous_state["timestep"]
    substep = previous_state["substep"]

    # Assert that the State Update and Policy Functions share the same previous state
    assert timestep == policy_input["timestep"]
    assert substep == policy_input["substep"]

    timesteps.append(timestep)
    substeps.append(substep)

    return ("a", None)

state_update_blocks = [
    {
        'policies': {
            'p': policy_check_timestep_substep
        },
        'variables': {
            'a': update_check_timestep_substep
        }
    },
    {
        'policies': {
            'p': policy_check_timestep_substep
        },
        'variables': {
            'a': update_check_timestep_substep
        }
    },
    {
        'policies': {
            'p': policy_check_timestep_substep
        },
        'variables': {
            'a': update_check_timestep_substep
        }
    }
]

initial_state = {
    "a": None
}


def test_initial_state_and_previous_state():
    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks)
    simulation = Simulation(model=model, timesteps=10, runs=1)
    simulation.engine = Engine(backend=Backend.SINGLE_PROCESS)

    result = simulation.run()
    df = pd.DataFrame(result)

    # Check that the initial state transition is correct
    assert timesteps[:4] == [
        0, # Timestep 1; substep 1
        1, # Timestep 1; substep 2
        1, # Timestep 1; substep 3
        1 # Timestep 2; substep 1
    ]
    assert substeps[:4] == [
        0, # Timestep 1; substep 1
        1, # Timestep 1; substep 2
        2, # Timestep 1; substep 3
        3 # Timestep 2; substep 1
    ]

    # Check that the previous state is correctly passed to next timestep/substep
    assert timesteps[len(timesteps) - 4:] == [
        9, # Timestep 9; substep 3
        9, # Timestep 10; substep 1
        10, # Timestep 10; substep 2
        10 # Timestep 10; substep 3
    ]
    assert substeps[len(substeps) - 4:] == [
        2, # Timestep 9; substep 3
        3, # Timestep 10; substep 1
        1, # Timestep 10; substep 2
        2 # Timestep 10; substep 3
    ]

    assert df.query("timestep == 0")["substep"].iloc[0] == 0
    assert df.query("timestep == 1")["substep"].iloc[0] == df.query("timestep == 2")["substep"].iloc[0]
    assert df.query("timestep == 9")["substep"].iloc[0] == df.query("timestep == 10")["substep"].iloc[0]
