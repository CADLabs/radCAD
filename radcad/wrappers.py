from radcad.core import _single_run_wrapper, generate_parameter_sweep, default_deepcopy_method
from radcad.engine import Engine
from collections import namedtuple
import copy


RunArgs = namedtuple("RunArgs", [
    "simulation",
    "timesteps",
    "run",
    "subset",
    "initial_state",
    "state_update_blocks",
    "parameters",
    "deepcopy",
    "deepcopy_method",
    "drop_substeps",
])
Context = namedtuple("Context", "simulation run subset timesteps initial_state parameters")


class Model:
    def __init__(self, initial_state={}, state_update_blocks=[], params={}):
        self.substeps = []
        self.state = {
            **copy.deepcopy(initial_state),
            'simulation': 0,
            'subset': 0,
            'run': 1,
            'substep': 0,
            'timestep': 0
        }
        self.initial_state = copy.deepcopy(initial_state)
        self.state_update_blocks = state_update_blocks
        self.params = copy.deepcopy(params)
        self.exceptions = []
        self._raise_exceptions = True
        self._deepcopy = True
        self._deepcopy_method = default_deepcopy_method
        self._drop_substeps = False

    def __iter__(self):
        while True:
            param_sweep = generate_parameter_sweep(self.params)
            _params = param_sweep[0] if param_sweep else {}
            run_args = RunArgs(
                simulation = 0,
                timesteps = 1,
                run = 0,
                subset = 0,
                initial_state = copy.deepcopy(self.state),
                state_update_blocks = self.state_update_blocks,
                parameters = _params,
                deepcopy = self._deepcopy,
                deepcopy_method = self._deepcopy_method,
                drop_substeps = self._drop_substeps,
            )
            result, exception = _single_run_wrapper((run_args, self._raise_exceptions))
            if exception: self.exceptions.append(exception)
            self.substeps = result.pop()
            self.state = self.substeps[-1] if self.substeps else self.state
            yield self

    def __call__(self, **kwargs):
        self._raise_exceptions = kwargs.pop("raise_exceptions", True)
        self._deepcopy = kwargs.pop("deepcopy", True)
        self._deepcopy_method = kwargs.pop("deepcopy_method", default_deepcopy_method)
        self._drop_substeps = kwargs.pop("drop_substeps", False)
        return self


class Executable:
    def __init__(self, **kwargs) -> None:
        self.engine = kwargs.pop("engine", Engine())

        self.results = []
        self.exceptions = []

        # Hooks
        self.before_experiment = kwargs.pop("before_experiment", None)
        self.after_experiment = kwargs.pop("after_experiment", None)
        self.before_simulation = kwargs.pop("before_simulation", None)
        self.after_simulation = kwargs.pop("after_simulation", None)
        self.before_run = kwargs.pop("before_run", None)
        self.after_run = kwargs.pop("after_run", None)
        self.before_subset = kwargs.pop("before_subset", None)
        self.after_subset = kwargs.pop("after_subset", None)

    def __deepcopy__(self, memo={}):
        # Reset iterators to enable deepcopy after simulation run
        self.engine._run_generator = iter(())

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def run(self):
        raise NotImplementedError("Method run() not implemented for class that extends Base")

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


class Simulation(Executable):
    def __init__(self, model: Model, timesteps=100, runs=1, **kwargs):
        super().__init__(**kwargs)

        self.model = model
        self.timesteps = timesteps
        self.runs = runs

        self.index = kwargs.pop("index", 0)

        if kwargs:
            raise Exception(f"Invalid Simulation option in {kwargs}")

    def run(self):
        return self.engine._run(executable=self)


class Experiment(Executable):
    """
    An Experiment is a collection of Simulations.
    """

    def __init__(self, simulations=[], **kwargs):
        super().__init__(**kwargs)

        # Add and validate simulations
        self.simulations = []
        self.add_simulations(simulations)

        if kwargs:
            raise Exception(f"Invalid Experiment option in {kwargs}")

    def run(self):
        return self.engine._run(executable=self)

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
