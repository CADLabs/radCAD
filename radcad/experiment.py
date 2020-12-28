import radcad.engine as engine
from radcad import Simulation

class Experiment():
    """
    An Experiment.
    """
    def __init__(self, simulations=[], **kwargs):
        self.simulations = []
        # Add and validate simulations
        self.add_simulations(simulations)

        self.before_experiment = kwargs.pop('before_experiment', None)
        self.after_experiment = kwargs.pop('after_experiment', None)
        self.before_simulation = kwargs.pop('before_simulation', None)
        self.after_simulation = kwargs.pop('after_simulation', None)
        self.before_run = kwargs.pop('before_run', None)
        self.after_run = kwargs.pop('after_run', None) 

        if kwargs:
            raise Exception(f"Invalid Experiment option in {kwargs}")
    
    def run(self, **kwargs):
        return engine.run(experiment=self, **kwargs)

    def add_simulations(self, simulations):
        if not isinstance(simulations, list):
            simulations = [simulations]
        if any(not isinstance(sim, Simulation) for sim in simulations):
            raise Exception("Invalid simulation added")
        self.simulations = simulations
    
    def clear_simulations(self):
        cleared = True if self.simulations else False
        self.simulations = []
        return cleared

    def get_simulations(self):
        return self.simulations

    # Hooks receive: params, substep, state_history, previous_state
    def __before_experiment(self, **kwargs):
        if self.before_experiment:
            self.before_experiment(**kwargs)

    def __after_experiment(self, params, substep, state_history, previous_state):
        if self.after_experiment:
            self.after_experiment(**kwargs)

    def __before_simulation(self, params, substep, state_history, previous_state):
        if self.before_simulation:
            self.before_simulation(**kwargs)

    def __after_simulation(self, params, substep, state_history, previous_state):
        if self.after_simulation:
            self.after_simulation(**kwargs)

    def __before_run(self, params, substep, state_history, previous_state):
        if self.before_run:
            self.before_run(**kwargs)

    def __after_run(self, params, substep, state_history, previous_state):
        if self.after_run:
            self.after_run(**kwargs)
