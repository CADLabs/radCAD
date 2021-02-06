from tests.test_cases.predator_prey_model_source.parts.utils import *
from tests.test_cases.predator_prey_model_source.sys_params import initial_values


initial_state = {
    'agents': generate_agents(initial_values['world_size_n_dimension'],initial_values['world_size_m_dimension'], 
                              initial_values['initial_food_sites'],initial_values['initial_predator_count'], 
                              initial_values['initial_prey_count']),
    'sites': np.ones((initial_values['world_size_n_dimension'], initial_values['world_size_m_dimension'])) * initial_values['initial_food_sites']
}
