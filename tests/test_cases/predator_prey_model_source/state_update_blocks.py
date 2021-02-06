from tests.test_cases.predator_prey_model_source.parts.environment import *
from tests.test_cases.predator_prey_model_source.parts.agents import *
import random


def initialize_seed(params, substep, state_history, prev_state):
    if prev_state['timestep'] == 0:
        print(f"Initializing seed {prev_state['simulation']}/{prev_state['subset']}/{prev_state['run']}")
        random.seed(a=f'{prev_state["simulation"]}/{prev_state["subset"]}/{prev_state["run"]}')
    return {}

state_update_blocks = [
    {
        'policies': {
            'initialize_seed': initialize_seed,
        },
        'variables': {},
    },
    {
        # environment.py
        'policies': {
            'grow_food': grow_food
        },
        'variables': {
            'sites': update_food
        }
    },
    {
        # agents.py
        'policies': {
            'increase_agent_age': digest_and_olden
        },
        'variables': {
            'agents': agent_food_age

        }
    },
    {
        # agents.py
        'policies': {
            'move_agent': move_agents
        },
        'variables': {
            'agents': agent_location

        }
    },
    {
        # agents.py
        'policies': {
            'reproduce_agents': reproduce_agents

        },
        'variables': {
            'agents': agent_create

        }
    },
    {
        # agents.py
        'policies': {
            'feed_prey': feed_prey
        },
        'variables': {
            'agents': agent_food,
            'sites': site_food
        }
    },
    {
        # agents.py
        'policies': {
            'hunt_prey': hunt_prey
        },
        'variables': {
            'agents': agent_food
        }
    },
    {
        # agents.py
        'policies': {
            'natural_death': natural_death
        },
        'variables': {
            'agents': agent_remove
        }
    }
]
