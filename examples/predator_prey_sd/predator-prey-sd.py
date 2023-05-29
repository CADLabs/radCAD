"""Predator-Prey model, analogous to the Jupyter notebook version predator-prey-sd.ipynb

Especially useful if you're struggling to run the Jupyten notebook, but still want to be able to proudly announce that you've run your first radCAD model!

"""


# 0. Import section
import pandas as pd
import numpy as np

from radcad import Model, Simulation

# 1. System parameters
system_params = {
    'prey_reproduction_rate': [0.6, 0.3],
    'predator_interaction_factor': [0.0002, 0.0001],
    'prey_interaction_factor': [0.002, 0.001],
    'prey_death_rate': [0.02, 0.01],
    'predator_death_rate': [1.0, 0.5],
    'dt': [0.1]
}

# 2. Initial state
initial_state = {
    'prey_population': 100,
    'predator_population': 50
}

# 3. Policy functions
def p_reproduce_prey(params, substep, state_history, prev_state, **kwargs):
    born_population = prev_state['prey_population'] * params['prey_reproduction_rate'] * params['dt']
    return {'add_prey': born_population}


def p_reproduce_predators(params, substep, state_history, prev_state, **kwargs):
    born_population = prev_state['predator_population'] * prev_state['prey_population'] * params['predator_interaction_factor'] * params['dt']
    return {'add_predators': born_population}


def p_eliminate_prey(params, substep, state_history, prev_state, **kwargs):
    population = prev_state['prey_population']
    natural_elimination = population * params['prey_death_rate']
    
    interaction_elimination = population * prev_state['predator_population'] * params['prey_interaction_factor']
    
    eliminated_population = natural_elimination + interaction_elimination * params['dt']
    return {'add_prey': -1.0 * eliminated_population}


def p_eliminate_predators(params, substep, state_history, prev_state, **kwargs):
    population = prev_state['predator_population']
    eliminated_population = population * params['predator_death_rate'] * params['dt']
    return {'add_predators': -1.0 * eliminated_population}

# 4. State update functions
def s_prey_population(params, substep, state_history, prev_state, policy_input, **kwargs):
    updated_prey_population = np.ceil(prev_state['prey_population'] + policy_input['add_prey'])
    return ('prey_population', max(updated_prey_population, 0))


def s_predator_population(params, substep, state_history, prev_state, policy_input, **kwargs):
    updated_predator_population = np.ceil(prev_state['predator_population'] + policy_input['add_predators'])
    return ('predator_population', max(updated_predator_population, 0))
	
# 5. Partial state update blocks

state_update_blocks = [
    {
        'policies': {
            'reproduce_prey': p_reproduce_prey,
            'reproduce_predators': p_reproduce_predators,
            'eliminate_prey': p_eliminate_prey,
            'eliminate_predators': p_eliminate_predators
        },
        'variables': {
            'prey_population': s_prey_population,
            'predator_population': s_predator_population            
        }
    }

]

# 6. Simulation configuration parameters
TIMESTEPS = 1000
RUNS = 1

# 7. Model
model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=system_params)

# 8. Simulation 
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

# 9. Execute the simulation
result = simulation.run()

# 10. Look at the results
df = pd.DataFrame(result)
# To analyse the first 10 rows of the raw results
# print(df.head(10))
# To analyse the last 10 rows of the raw results
# print(df.tail(10))
print(f"The final sizes of the populations are, prey: {df['prey_population'][2001]} and predator: {df['predator_population'][2001]}.")