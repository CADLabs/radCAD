from tests.test_cases.predator_prey_model_source.parts.utils import *
import random
from uuid import uuid4

# Behaviors
def digest_and_olden(params, substep, state_history, prev_state):
    agents = prev_state['agents']
    delta_food = {agent: -1 for agent in agents.keys()}
    delta_age = {agent: +1 for agent in agents.keys()}
    return {'agent_delta_food': delta_food,
          'agent_delta_age': delta_age}

def move_agents(params, substep, state_history, prev_state):
    """
    Move agents.
    """
    sites = prev_state['sites']
    agents = prev_state['agents']
    busy_locations = [agent['location'] for agent in agents.values()]
    new_locations = {}
    for label, properties in agents.items():
        new_location = get_free_location(properties['location'], sites, busy_locations)
        if new_location is not False:
            new_locations[label] = new_location
            busy_locations.append(new_location)
        else:
            continue
    return {'update_agent_location': new_locations}

def reproduce_agents(params, substep, state_history, prev_state):
    """
    Generates an new agent through an nearby agent pair, subject to rules.
    Not done.
    """
    agents = prev_state['agents']
    sites = prev_state['sites']
    food_threshold = params['reproduction_food_threshold']
    reproduction_food = params['reproduction_food']
    reproduction_probability = params['reproduction_probability']
    busy_locations = [agent['location'] for agent in agents.values()]
    already_reproduced = []
    new_agents = {}
    agent_delta_food = {}
    for agent_type in set(agent['type'] for agent in agents.values()):
        # Only reproduce agents of the same type
        specific_agents = {label: agent for label, agent in agents.items()
                           if agent['type'] == agent_type}
        for agent_label, agent_properties in specific_agents.items():
            location = agent_properties['location']
            if (agent_properties['food'] < food_threshold or agent_label in already_reproduced):
                continue
            kind_neighbors = nearby_agents(location, specific_agents)
            available_partners = [label for label, agent in kind_neighbors.items()
                                  if agent['food'] >= food_threshold
                                  and label not in already_reproduced]
            reproduction_location = get_free_location(location, sites, busy_locations)
            
            if reproduction_location is not False and len(available_partners) > 0:
                reproduction_partner_label = random.choice(available_partners)
                reproduction_partner = agents[reproduction_partner_label]
                already_reproduced += [agent_label, reproduction_partner_label]

                agent_delta_food[agent_label] = -1.0 * reproduction_food
                agent_delta_food[reproduction_partner_label] = -1.0 * reproduction_food
                new_agent_properties = {'type': agent_type,
                                        'location': reproduction_location,
                                        'food': 2.0 * reproduction_food,
                                        'age': 0}
                new_agents[uuid4()] = new_agent_properties
                busy_locations.append(reproduction_location)
    return {'agent_delta_food': agent_delta_food,'agent_create': new_agents}

def feed_prey(params, substep, state_history, prev_state):
    """
    Feeds the hungry prey with all food located on its site.
    """
    agents = prev_state['agents']
    sites = prev_state['sites']
    preys = {k: v for k, v in agents.items() if v['type'] == 'prey'}
    hungry_preys = {label: properties for label, properties in preys.items()
                    if properties['food'] < params['hunger_threshold']}

    agent_delta_food = {}
    site_delta_food = {}
    for label, properties in hungry_preys.items():
        location = properties['location']
        available_food = sites[location]
        agent_delta_food[label] = available_food
        site_delta_food[location] = -available_food

    return {'agent_delta_food': agent_delta_food,
            'site_delta_food': site_delta_food}



def hunt_prey(params, substep, state_history, prev_state):
    """
    Feeds the hungry predators with an random nearby prey.
    """
    agents = prev_state['agents']
    sites = prev_state['sites']
    hungry_threshold = params['hunger_threshold']
    preys = {k: v for k, v in agents.items()
             if v['type'] == 'prey'}
    predators = {k: v for k, v in agents.items()
                 if v['type'] == 'predator'}
    hungry_predators = {k: v for k, v in predators.items()
                        if v['food'] < hungry_threshold}
    agent_delta_food = {}
    for predator_label, predator_properties in hungry_predators.items():
        location = predator_properties['location']
        nearby_preys = nearby_agents(location, preys)
        if len(nearby_preys) > 0:
            eaten_prey_label = random.choice(list(nearby_preys.keys()))
            delta_food = preys.pop(eaten_prey_label)['food']
            agent_delta_food[predator_label] = delta_food
            agent_delta_food[eaten_prey_label] = -1 * delta_food
        else:
            continue

    return {'agent_delta_food': agent_delta_food}


def natural_death(params, substep, state_history, prev_state):
    """
    Remove agents which are old or hungry enough.
    """
    agents = prev_state['agents']
    maximum_age = params['agent_lifespan']
    agents_to_remove = []
    for agent_label, agent_properties in agents.items():
        to_remove = agent_properties['age'] > maximum_age
        to_remove |= (agent_properties['food'] <= 0)
        if to_remove:
            agents_to_remove.append(agent_label)
    return {'remove_agents': agents_to_remove}



# Mechanisms
def agent_food_age(params, substep, state_history, prev_state, policy_input):
    delta_food_by_agent = policy_input['agent_delta_food']
    delta_age_by_agent = policy_input['agent_delta_age']
    updated_agents = prev_state['agents'].copy()

    for agent, delta_food in delta_food_by_agent.items():
        updated_agents[agent]['food'] += delta_food
    for agent, delta_age in delta_age_by_agent.items():
        updated_agents[agent]['age'] += delta_age
    return ('agents', updated_agents)

def agent_location(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, location in policy_input['update_agent_location'].items():
        updated_agents[label]['location'] = location
    return ('agents', updated_agents)

def agent_create(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, food in policy_input['agent_delta_food'].items():
        updated_agents[label]['food'] += food
    for label, properties in policy_input['agent_create'].items():
        updated_agents[label] = properties
    return ('agents', updated_agents)


def site_food(params, substep, state_history, prev_state, policy_input):
    updated_sites = prev_state['sites'].copy()
    for label, delta_food in policy_input['site_delta_food'].items():
        updated_sites[label] += delta_food
    return ('sites', updated_sites)

def agent_food(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    for label, delta_food in policy_input['agent_delta_food'].items():
        updated_agents[label]['food'] += delta_food
    return ('agents', updated_agents)


def agent_remove(params, substep, state_history, prev_state, policy_input):
    agents_to_remove = policy_input['remove_agents']
    surviving_agents = {k: v for k, v in prev_state['agents'].items()
                        if k not in agents_to_remove}
    return ('agents', surviving_agents)




