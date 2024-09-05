import os
import copy
import multiprocessing
from typing import Iterator

import radcad.core as core
import radcad.types
import radcad.utils as utils
import radcad.wrappers as wrappers
from radcad.backends import Backend
from radcad.utils import extract_exceptions

# Get machine CPU count
cpu_count = multiprocessing.cpu_count() - 1 or 1

class Engine:
    def __init__(self, **kwargs):
        """
        Handles configuration and execution of experiments and simulations.

        Args:
            **backend (Backend): Which execution backend to use (e.g. Pathos, Multiprocessing, etc.). Defaults to `Backend.DEFAULT` / `Backend.PATHOS`. Can be set via the `RADCAD_BACKEND` environment variable which takes precedence.
            **processes (int, optional): Number of system CPU processes to spawn. Defaults to `multiprocessing.cpu_count() - 1 or 1`
            **raise_exceptions (bool): Whether to raise exceptions, or catch them and return exceptions along with partial results. Default to `True`.
            **deepcopy (bool): Whether to enable deepcopy of State Variables to avoid unintended state mutation. Defaults to `True`.
            **deepcopy_method (Callable): Method to use for deepcopy of State Variables. By default uses Pickle for improved performance, use `copy.deepcopy` for an alternative to Pickle.
            **drop_substeps (bool): Whether to drop simulation result substeps during runtime to save memory and improve performance. Defaults to `False`.
            **simulation_execution (SimulationExecution): Set a custom radCAD SimulationExecution class instance. Overrides setting of `raise_exceptions`, `deepcopy`, `deepcopy_method`, and `drop_substeps`.
            **_run_generator (tuple_iterator): Generator to generate simulation runs, used to implement custom execution backends. Defaults to  `iter(())`.
        """
        self.executable = None
        self.processes = kwargs.pop("processes", cpu_count)

        ENV_RADCAD_BACKEND = os.getenv('RADCAD_BACKEND', None)
        if ENV_RADCAD_BACKEND:
            kwargs.pop("backend", None)
            self.backend = Backend[ENV_RADCAD_BACKEND]
        else:
            self.backend = kwargs.pop("backend", Backend.DEFAULT)

        _simulation_execution = kwargs.pop("simulation_execution", None)
        if _simulation_execution:
            self.simulation_execution = _simulation_execution
        else:
            self.raise_exceptions = kwargs.pop("raise_exceptions", True)
            self.deepcopy = kwargs.pop("deepcopy", True)
            self.deepcopy_method = kwargs.pop("deepcopy_method", core.SimulationExecution.deepcopy_method)
            self.drop_substeps = kwargs.pop("drop_substeps", False)

            self.simulation_execution = core.SimulationExecution(
                enable_deepcopy=self.deepcopy,
                drop_substeps=self.drop_substeps,
                raise_exceptions=self.raise_exceptions,
            )
            self.simulation_execution.deepcopy_method = self.deepcopy_method

        self._run_generator = iter(())

        if kwargs:
            raise Exception(f"Invalid Engine option in {kwargs}")

    def _run(self, executable=None, **kwargs):
        if not executable:
            raise Exception("Experiment or simulation required as Executable argument")
        self.executable = executable

        if kwargs:
            raise Exception(f"Invalid Engine option in {kwargs}")

        simulations = executable.simulations if isinstance(executable, wrappers.Experiment) else [executable]
        if not isinstance(self.backend, Backend):
            raise Exception(f"Execution backend must be one of {Backend._member_names_}, not {self.backend}")

        self.executable._before_experiment(experiment=(executable if isinstance(executable, wrappers.Experiment) else None))

        self._run_generator = self._run_stream(simulations)

        # Select backend executor
        if self.backend in [Backend.RAY, Backend.RAY_REMOTE]:
            if self.backend == Backend.RAY_REMOTE:
                from radcad.extensions.backends.ray import \
                    ExecutorRayRemote as Executor
            else:
                from radcad.extensions.backends.ray import \
                    ExecutorRay as Executor
        elif self.backend in [Backend.PATHOS, Backend.DEFAULT]:
            from radcad.backends.pathos import ExecutorPathos as Executor
        elif self.backend in [Backend.MULTIPROCESSING]:
            from radcad.backends.multiprocessing import \
                ExecutorMultiprocessing as Executor
        elif self.backend in [Backend.SINGLE_PROCESS]:
            from radcad.backends.single_process import \
                ExecutorSingleProcess as Executor
        else:
            raise Exception(f"Execution backend must be one of {Backend._member_names_}, not {self.backend}")
        
        result = Executor(self).execute_runs()
        
        self.executable.results, self.executable.exceptions = extract_exceptions(result)
        self.executable._after_experiment(experiment=(executable if isinstance(executable, wrappers.Experiment) else None))
        return self.executable.results

    def _run_stream(self, simulations) -> Iterator[core.SimulationExecution]:
        for simulation_index, simulation in enumerate(simulations):
            simulation.index = simulation_index
            
            timesteps = simulation.timesteps
            runs = simulation.runs
            initial_state = simulation.model.initial_state
            state_update_blocks = simulation.model.state_update_blocks
            params = simulation.model.params
            param_sweep = utils.generate_parameter_sweep(params)

            context = copy.deepcopy(radcad.types.Context(
                simulation=simulation_index,
                timesteps=timesteps,
                initial_state=initial_state,
                parameters=params,  # NOTE Each parameter is a list of all subsets in before_run() method and a single subset in before_subset()
                state_update_blocks=state_update_blocks,
            ))

            # For each hook, Experiment setting takes preference over Simulation setting
            # Before simulation hook
            before_simulation = self.executable.before_simulation or simulation.before_simulation
            if before_simulation: before_simulation(context=context)

            for run_index in range(0, runs):
                context.run = run_index + 1  # +1 to remain compatible with cadCAD implementation

                # Before run hook
                before_run = self.executable.before_run or simulation.before_run
                if before_run: before_run(context=context)

                for subset_index, param_set in enumerate(param_sweep if param_sweep else [params]):
                    context.subset = subset_index
                    context.parameters = param_set

                    # Before subset hook
                    before_subset = self.executable.before_subset or simulation.before_subset
                    if before_subset: before_subset(context=context)

                    self.simulation_execution.simulation_index = context.simulation
                    self.simulation_execution.timesteps = context.timesteps
                    self.simulation_execution.run_index = context.run
                    self.simulation_execution.subset_index = context.subset
                    self.simulation_execution.initial_state = context.initial_state
                    self.simulation_execution.state_update_blocks = context.state_update_blocks
                    self.simulation_execution.params = context.parameters

                    yield copy.deepcopy(self.simulation_execution)

                    # After subset hook
                    after_subset = self.executable.after_subset or simulation.after_subset
                    if after_subset: after_subset(context=context)

                # After run hook
                after_run = self.executable.after_run or simulation.after_run
                if after_run: after_run(context=context)

            # After simulation hook
            after_simulation = self.executable.after_simulation or simulation.after_simulation
            if after_simulation: after_simulation(context=context)
