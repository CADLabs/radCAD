from dataclasses import FrozenInstanceError, dataclass
from typing import List
from radcad import Model, Simulation, Experiment, Backend, Context
from radcad.utils import default
import pytest


# NOTE To pickle a dataclass, it must be defined in module and not function scope
@dataclass(frozen=True)
class P1:
    subset: List[int] = default([0, 1, 2])
    a: List[int] = default([0, 1])


def check_dataclass_frozen(context: Context):
    with pytest.raises(FrozenInstanceError) as e:
        context.parameters.a = -1


def policy(params: P1, substep, state_history, previous_state):
    subset = previous_state['subset']
    assert subset == params.subset
    assert params.a == params.subset if subset < 2 else params.a == 1
    return {}


def test_basic_state_update():
    initial_state = {}

    state_update_blocks = [
        {
            'policies': {
                'p': policy
            },
            'variables': {}
        },
    ]

    params = P1()

    TIMESTEPS = 10
    RUNS = 3

    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulation)
    experiment.before_run = check_dataclass_frozen
    _result = experiment.run()
