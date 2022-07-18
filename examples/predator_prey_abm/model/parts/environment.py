import numpy as np
from .utils import *


# Behaviors
def grow_food(params, substep, state_history, prev_state):
    """
    Increases the food supply in all sites, subject to an maximum.
    """
    regenerated_sites = calculate_increment(prev_state['sites'],
                                          params['food_growth_rate'],
                                          params['maximum_food_per_site'])
    return {'update_food': regenerated_sites}


# Mechanisms
def update_food(params, substep, state_history, prev_state, policy_input):
    key = 'sites'
    value = policy_input['update_food']
    return (key, value)
