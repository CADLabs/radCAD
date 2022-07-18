import numpy as np
import random
from typing import *
import uuid
import matplotlib.pyplot as plt
import pandas as pd

# Initialization
def new_agent(agent_type: str, location: Tuple[int, int],
              food: int=10, age: int=0) -> dict:
    agent = {'type': agent_type,
             'location': location,
             'food': food,
             'age':age}
    return agent


def generate_agents(N: int,M: int,initial_sites: int,
                    n_predators: int,
                    n_prey: int) -> Dict[str, dict]:
    
    available_locations = [(n, m) for n in range(N) for m in range(M)]
    initial_agents = {}
    type_queue = ['prey'] * n_prey
    type_queue += ['predator'] * n_predators
    random.shuffle(type_queue)
    for agent_type in type_queue:
        location = random.choice(available_locations)
        available_locations.remove(location)
        created_agent = new_agent(agent_type, location)
        initial_agents[uuid.uuid4()] = created_agent
    return initial_agents


# Environment
@np.vectorize
def calculate_increment(value, growth_rate, max_value):
    new_value = (value + growth_rate
                 if value + growth_rate < max_value
                 else max_value)
    return new_value

# Location heper
def check_location(position: tuple,
                   all_sites: np.matrix,
                   busy_locations: List[tuple]) -> List[tuple]:
    """
    Returns an list of available location tuples neighboring an given
    position location.
    """
    N, M = all_sites.shape
    potential_sites = [(position[0], position[1] + 1),
                       (position[0], position[1] - 1),
                       (position[0] + 1, position[1]),
                       (position[0] - 1, position[1])]
    potential_sites = [(site[0] % N, site[1] % M) for site in potential_sites]
    valid_sites = [site for site in potential_sites if site not in busy_locations]
    return valid_sites


def get_free_location(position: tuple,
                      all_sites: np.matrix,
                      used_sites: List[tuple]) -> tuple:
    """
    Gets an random free location neighboring an position. Returns False if
    there aren't any location available.
    """
    available_locations = check_location(position, all_sites, used_sites)
    if len(available_locations) > 0:
        return random.choice(available_locations)
    else:
        return False


def nearby_agents(location: tuple, agents: Dict[str, dict]) -> Dict[str, dict]:
    """
    Filter the non-nearby agents.
    """
    neighbors = {label: agent for label, agent in agents.items()
                 if is_neighbor(agent['location'], location)}
    return neighbors


def is_neighbor(location_1: tuple, location_2: tuple) -> bool:
    dx = np.abs(location_1[0] - location_2[0])
    dy = (location_1[1] - location_2[0])
    distance = dx + dy
    if distance == 1:
        return True
    else:
        return False

# plotting
def aggregate_runs(df,aggregate_dimension):
    '''
    Function to aggregate the monte carlo runs along a single dimension.

    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.

    Example run:
    mean_df,median_df,std_df,min_df = aggregate_runs(df,'timestep')
    '''

    mean_df = df.groupby(aggregate_dimension).mean().reset_index()
    median_df = df.groupby(aggregate_dimension).median().reset_index()
    std_df = df.groupby(aggregate_dimension).std().reset_index()
    min_df = df.groupby(aggregate_dimension).min().reset_index()

    return mean_df,median_df,std_df,min_df

def monte_carlo_plot(df,aggregate_dimension,x,y,runs):
    '''
    A function that generates timeseries plot of Monte Carlo runs.

    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting
    run_count = the number of monte carlo simulations

    Example run:
    monte_carlo_plot(df,'timestep','timestep','revenue',run_count=100)
    '''
    mean_df,median_df,std_df,min_df = aggregate_runs(df,aggregate_dimension)
    plt.figure(figsize=(10,6))
    for r in range(1,runs+1):
        legend_name = 'Run ' + str(r)
        plt.plot(df[df.run==r].timestep, df[df.run==r][y], label = legend_name )
    plt.plot(mean_df[x], mean_df[y], label = 'Mean', color = 'black')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Performance of ' + y + ' over ' + str(runs) + ' Monte Carlo Runs'
    plt.title(title_text)