"""User-facing classes for describing and running radCAD simulations.

This module provides the three classes that make up the radCAD modelling
hierarchy: [Model][radcad.wrappers.Model] > [Simulation][radcad.wrappers.Simulation] > [Experiment][radcad.wrappers.Experiment]. A
[Model][radcad.wrappers.Model] captures *what* the system is, a [Simulation][radcad.wrappers.Simulation] captures
*how long* and *how many times* to run it, and an [Experiment][radcad.wrappers.Experiment] groups
one or more simulations so they can be executed together by the
[Engine][radcad.engine.Engine].
"""

import copy

from radcad.core import SimulationExecution, multiprocess_wrapper
from radcad.engine import Engine
from radcad.types import Context, SimulationResults
from radcad.utils import generate_parameter_sweep


class Model:
    """A dynamical-system model: an initial state plus the rules that evolve it.

    A Model bundles together the three things needed to describe a system:
    the ``initial_state`` of its State Variables, the ``state_update_blocks``
    (Partial State Update Blocks) that transition state from one timestep to
    the next, and the ``params`` (System Parameters) those rules depend on.

    A Model is also iterable: iterating over it advances the system one
    timestep at a time, which is useful for live digital twins, gradient
    descent, or composing one model inside another. See `__iter__` and
    `__call__`.

    Args:
        initial_state (dict): Mapping of State Variable name to initial value.
        state_update_blocks (list): Ordered list of Partial State Update
            Blocks, each a dict with ``"policies"`` and ``"variables"`` keys.
        params (dict | dataclass): System Parameters, either as a dict of
            lists (for sweeps) or a (possibly nested) dataclass.
    """

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
        self._deepcopy_method = SimulationExecution.deepcopy_method
        self._drop_substeps = False

    def __iter__(self):
        """Advance the model one timestep per iteration, yielding ``self``.

        Each iteration runs a single-timestep simulation from the current
        `state`, updates `state` and `substeps`, and yields
        the model so the caller can read the new state. Only single-subset
        models are supported (no parameter sweeps when iterating).
        """
        param_sweep = generate_parameter_sweep(self.params)
        while True:
            _params = param_sweep[0] if param_sweep else {}
            simulation_execution = SimulationExecution(
                # Model / simulation settings
                timesteps = 1,
                initial_state = copy.deepcopy(self.state),
                state_update_blocks = self.state_update_blocks,
                params = _params,
                # Execution settings
                enable_deepcopy = self._deepcopy,
                drop_substeps = self._drop_substeps,
                raise_exceptions = self._raise_exceptions,
            )
            simulation_execution.deepcopy_method = self._deepcopy_method
            result, exception = multiprocess_wrapper(simulation_execution)
            if exception: self.exceptions.append(exception)
            self.substeps = result.pop()
            self.state = self.substeps[-1] if self.substeps else self.state
            yield self

    def __call__(self, **kwargs):
        """Configure execution options for iteration, then return ``self``.

        Lets you set engine-style options before iterating, e.g.
        ``next(model(deepcopy=False, drop_substeps=True))``.

        Args:
            **raise_exceptions (bool): Raise on failure rather than collecting
                exceptions. Defaults to ``True``.
            **deepcopy (bool): Deepcopy state to prevent unintended mutation.
                Defaults to ``True``.
            **deepcopy_method (Callable): Custom deepcopy implementation.
            **drop_substeps (bool): Keep only the final substep per timestep.
                Defaults to ``False``.

        Returns:
            Model: ``self``, ready to be iterated.
        """
        self._raise_exceptions = kwargs.pop("raise_exceptions", True)
        self._deepcopy = kwargs.pop("deepcopy", True)
        self._deepcopy_method = kwargs.pop("deepcopy_method", SimulationExecution.deepcopy_method)
        self._drop_substeps = kwargs.pop("drop_substeps", False)
        return self


class Executable:
    """Base class for things the [Engine][radcad.engine.Engine] can run.

    Holds the shared machinery for both [Simulation][radcad.wrappers.Simulation] and
    [Experiment][radcad.wrappers.Experiment]: the [Engine][radcad.engine.Engine] instance, the
    ``results`` and ``exceptions`` populated after a run, and the lifecycle
    hooks used to extend behaviour without modifying the core. Not intended to
    be instantiated directly.

    Accepts the following keyword arguments: ``engine`` (an
    [Engine][radcad.engine.Engine], defaulting to a new instance) and the
    optional lifecycle hooks ``before_experiment``, ``after_experiment``,
    ``before_simulation``, ``after_simulation``, ``before_run``, ``after_run``,
    ``before_subset``, and ``after_subset``.
    """

    def __init__(self, **kwargs) -> None:
        self.engine = kwargs.pop("engine", Engine())

        self.results: SimulationResults = []
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
        """Deepcopy the executable, resetting the engine's run generator first.

        The engine's ``_run_generator`` is not picklable/copyable once a run
        has started, so it is reset to an empty iterator before copying.
        """
        # Reset iterators to enable deepcopy after simulation run
        self.engine._run_generator = iter(())

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def run(self):
        """Run the executable and return its results. Implemented by subclasses."""
        raise NotImplementedError("Method run() not implemented for class that extends Base")

    # Hooks
    def _before_experiment(self, experiment):
        if self.before_experiment:
            self.before_experiment(experiment=experiment)

    def _after_experiment(self, experiment):
        if self.after_experiment:
            self.after_experiment(experiment=experiment)

    def _before_simulation(self, context: Context):
        if self.before_simulation:
            self.before_simulation(context=context)

    def _after_simulation(self, context: Context):
        if self.after_simulation:
            self.after_simulation(context=context)

    def _before_run(self, context: Context):
        if self.before_run:
            self.before_run(context=context)

    def _after_run(self, context: Context):
        if self.after_run:
            self.after_run(context=context)

    def _before_subset(self, context: Context):
        if self.before_subset:
            self.before_subset(context=context)

    def _after_subset(self, context: Context):
        if self.after_subset:
            self.after_subset(context=context)


class Simulation(Executable):
    """A [Model][radcad.wrappers.Model] together with a number of timesteps and runs.

    A Simulation answers "run this model for how long, and how many times?".
    The number of ``runs`` drives Monte Carlo analysis, while the model's
    System Parameters drive parameter sweeps. Call `run` (or wrap it in
    an [Experiment][radcad.wrappers.Experiment]) to execute it via the
    [Engine][radcad.engine.Engine].

    Args:
        model (Model): The model to simulate.
        timesteps (int): Number of timesteps per run. Defaults to ``100``.
        runs (int): Number of (Monte Carlo) runs. Defaults to ``1``.

    Additional [Executable][radcad.wrappers.Executable] keyword arguments (``engine`` and the
    lifecycle hooks) are also accepted.
    """

    def __init__(self, model: Model, timesteps=100, runs=1, **kwargs):
        super().__init__(**kwargs)

        self.model = model
        self.timesteps = timesteps
        self.runs = runs

        self.index = kwargs.pop("index", 0)

        if kwargs:
            raise Exception(f"Invalid Simulation option in {kwargs}")

    def run(self):
        """Execute the simulation and return its results.

        Returns:
            SimulationResults: A flat list of state dictionaries, one per
            substep, suitable for ``pandas.DataFrame(...)``.
        """
        return self.engine._run(executable=self)


class Experiment(Executable):
    """A collection of [Simulation][radcad.wrappers.Simulation] objects run together.

    Grouping simulations into an Experiment lets the
    [Engine][radcad.engine.Engine] execute them in parallel (e.g. for A/B
    tests) and collects their results and exceptions in one place.

    Args:
        simulations (Simulation | list): A simulation or list of simulations.

    Additional [Executable][radcad.wrappers.Executable] keyword arguments (``engine`` and the
    lifecycle hooks) are also accepted.
    """

    def __init__(self, simulations=[], **kwargs):
        super().__init__(**kwargs)

        # Add and validate simulations
        self.simulations = []
        self.add_simulations(simulations)

        if kwargs:
            raise Exception(f"Invalid Experiment option in {kwargs}")

    def run(self):
        """Execute every simulation in the experiment and return the results.

        Returns:
            SimulationResults: A flat list of state dictionaries across all
            simulations, suitable for ``pandas.DataFrame(...)``.
        """
        return self.engine._run(executable=self)

    def add_simulations(self, simulations):
        """Append one or more [Simulation][radcad.wrappers.Simulation] objects to the experiment.

        Args:
            simulations (Simulation | list): Simulation(s) to add.

        Raises:
            Exception: If any item is not a [Simulation][radcad.wrappers.Simulation].
        """
        if not isinstance(simulations, list):
            simulations = [simulations]
        if any(not isinstance(sim, Simulation) for sim in simulations):
            raise Exception("Invalid simulation added")
        self.simulations.extend(simulations)

    def clear_simulations(self):
        """Remove all simulations.

        Returns:
            bool: ``True`` if there were simulations to clear, else ``False``.
        """
        cleared = True if self.simulations else False
        self.simulations = []
        return cleared

    def get_simulations(self):
        """Return the list of simulations in the experiment."""
        return self.simulations
