from radcad.engine import Engine
from collections import namedtuple


RunArgs = namedtuple("RunArgs", "simulation timesteps run subset initial_state state_update_blocks parameters deepcopy drop_substeps")
Context = namedtuple("Context", "simulation run subset timesteps initial_state parameters")

class Model:
    def __init__(self, initial_state={}, state_update_blocks=[], params={}):
        self.initial_state = initial_state
        self.state_update_blocks = state_update_blocks
        self.params = params


class Simulation:
    def __init__(self, model: Model, timesteps=100, runs=1, **kwargs):
        self.model = model
        self.timesteps = timesteps
        self.runs = runs

        self.index = kwargs.pop("index", 0)
        self.engine = kwargs.pop("engine", Engine())
        self.experiment = Experiment(self)

        if kwargs:
            raise Exception(f"Invalid Simulation option in {kwargs}")

    def run(self):
        return self.engine._run(experiment=self.experiment)


class Experiment:
    """
    An Experiment.
    """

    def __init__(self, simulations=[], **kwargs):
        self.engine = kwargs.pop("engine", Engine())

        self.simulations = []

        self.results = []
        self.exceptions = []

        # Add and validate simulations
        self.add_simulations(simulations)

        # Hooks
        self.before_experiment = kwargs.pop("before_experiment", None)
        self.after_experiment = kwargs.pop("after_experiment", None)
        self.before_simulation = kwargs.pop("before_simulation", None)
        self.after_simulation = kwargs.pop("after_simulation", None)
        self.before_run = kwargs.pop("before_run", None)
        self.after_run = kwargs.pop("after_run", None)
        self.before_subset = kwargs.pop("before_subset", None)
        self.after_subset = kwargs.pop("after_subset", None)

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

    # Hooks
    def _before_experiment(self, experiment=None):
        if self.before_experiment:
            self.before_experiment(experiment=experiment)

    def _after_experiment(self, experiment=None):
        if self.after_experiment:
            self.after_experiment(experiment=experiment)

    def _before_simulation(self, simulation=None):
        if self.before_simulation:
            self.before_simulation(
                simulation=simulation
            )

    def _after_simulation(self, simulation=None):
        if self.after_simulation:
            self.after_simulation(
                simulation=simulation
            )

    def _before_run(self, context: Context=None):
        if self.before_run:
            self.before_run(context=context)

    def _after_run(self, context: Context=None):
        if self.after_run:
            self.after_run(context=context)

    def _before_subset(self, context: Context=None):
        if self.before_subset:
            self.before_subset(context=context)

    def _after_subset(self, context: Context=None):
        if self.after_subset:
            self.after_subset(context=context)
