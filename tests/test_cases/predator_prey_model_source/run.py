import pandas as pd
from tests.test_cases.predator_prey_model_source.parts.utils import * 


def postprocessing(df):
    '''
    Definition:
    Refine and extract metrics from the simulation
    
    Parameters:
    df: simulation dataframe
    '''
    # subset to last substep
    df = df[df['substep'] == df.substep.max()]

    # Get the ABM results
    agent_ds = df.agents
    site_ds = df.sites
    timesteps = df.timestep
    
    # Get metrics

    ## Agent quantity
    prey_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'prey']))
    predator_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'predator']))


    ## Food quantity
    food_at_sites = site_ds.map(lambda s: s.sum())
    food_at_prey = agent_ds.map(lambda s: sum([agent['food'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'prey']))
    food_at_predators = agent_ds.map(lambda s: sum([agent['food'] 
                                                    for agent in s.values() 
                                                    if agent['type'] == 'predator']))

    ## Food metrics
    median_site_food = site_ds.map(lambda s: np.median(s)) 
    median_prey_food = agent_ds.map(lambda s: np.median([agent['food'] 
                                                         for agent in s.values() 
                                                         if agent['type'] == 'prey']))
    median_predator_food = agent_ds.map(lambda s: np.median([agent['food'] 
                                                             for agent in s.values() 
                                                             if agent['type'] == 'predator']))

    ## Age metrics
    prey_median_age = agent_ds.map(lambda s: np.median([agent['age'] for agent in s.values() if agent['type'] == 'prey']))
    predator_median_age = agent_ds.map(lambda s: np.median([agent['age'] for agent in s.values() if agent['type'] == 'predator']))

    # Create an analysis dataset
    data = (pd.DataFrame({'timestep': timesteps,
                          'run': df.run,
                          'prey_count': prey_count,
                          'predator_count': predator_count,
                          'food_at_sites': food_at_sites,
                          'food_at_prey': food_at_prey,
                          'food_at_predators': food_at_predators,
                          'median_site_food': median_site_food,
                          'median_prey_food': median_prey_food,
                          'median_predator_food': median_predator_food,
                          'prey_median_age': prey_median_age,
                          'predator_median_age': predator_median_age})       
           )
    
    return data