from radcad.core import Simulation
from radcad.engine import Engine


class Experiment():
    """
    An Experiment.
    """
    def __init__(self, simulations=[], **kwargs):
        self.engine = kwargs.pop('engine', Engine())

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
    
    def run(self):
        return self.engine._run(experiment=self)

    def add_simulations(self, simulations):
        if not isinstance(simulations, list):
            simulations = [simulations]
        if any(not isinstance(sim, Simulation) for sim in simulations):
            raise Exception("Invalid simulation added")
        self.simulations.extend(simulations)
    
    def clear_simulations(self):
        cleared = True if self.simulations else False
        self.simulations = []
        return cleared

    def get_simulations(self):
        return self.simulations

    # Hooks receive: params, substep, state_history, previous_state
    def _before_experiment(self, engine=None):
        if self.before_experiment:
            self.before_experiment(engine=engine)

    def _after_experiment(self, engine=None):
        if self.after_experiment:
            self.after_experiment(engine=engine)

    def _before_simulation(self, simulation=None, simulation_index=-1):
        if self.before_simulation:
            self.before_simulation(simulation=simulation, simulation_index=simulation_index)

    def _after_simulation(self, simulation=None, simulation_index=-1):
        if self.after_simulation:
            self.after_simulation(simulation=simulation, simulation_index=simulation_index)

    def _before_run(self, simulation=None, run_index=-1):
        if self.before_run:
            self.before_run(simulation=simulation, run_index=run_index)

    def _after_run(self, simulation=None, run_index=-1):
        if self.after_run:
            self.after_run(simulation=simulation, run_index=run_index)
