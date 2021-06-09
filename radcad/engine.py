import radcad.core as core
import radcad.wrappers as wrappers
from radcad.backends import Backend
from radcad.utils import flatten, extract_exceptions

import multiprocessing
import copy


# Get machine CPU count
cpu_count = multiprocessing.cpu_count() - 1 or 1

class Engine:
    def __init__(self, **kwargs):
        """
        Handles configuration and execution of experiments and simulations.

        Args:
            **backend (Backend): Which execution backend to use (e.g. Pathos, Multiprocessing, etc.). Defaults to `Backend.DEFAULT` / `Backend.PATHOS`.
            **processes (int, optional): Number of system CPU processes to spawn. Defaults to `multiprocessing.cpu_count() - 1 or 1`
            **raise_exceptions (bool): Whether to raise exceptions, or catch them and return exceptions along with partial results. Default to `True`.
            **deepcopy (bool): Whether to enable deepcopy of State Variables, alternatively leaves safety up to user with improved performance. Defaults to `True`.
            **drop_substeps (bool): Whether to drop simulation result substeps during runtime to save memory and improve performance. Defaults to `False`.
            **_run_generator (tuple_iterator): Generator to generate simulation runs, used to implement custom execution backends. Defaults to  `iter(())`.
        """
        self.executable = None
        self.processes = kwargs.pop("processes", cpu_count)
        self.backend = kwargs.pop("backend", Backend.DEFAULT)
        self.raise_exceptions = kwargs.pop("raise_exceptions", True)
        self.deepcopy = kwargs.pop("deepcopy", True)
        self.drop_substeps = kwargs.pop("drop_substeps", False)
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
            raise Exception(f"Execution backend must be one of {Backend.list()}")
        configs = [
            (
                sim.model.initial_state,
                sim.model.state_update_blocks,
                sim.model.params,
                sim.timesteps,
                sim.runs,
            )
            for sim in simulations
        ]

        result = []

        self.executable._before_experiment(experiment=(executable if isinstance(executable, wrappers.Experiment) else None))

        self._run_generator = self._run_stream(configs)

        # Select backend executor
        if self.backend in [Backend.RAY, Backend.RAY_REMOTE]:
            if self.backend == Backend.RAY_REMOTE:
                from radcad.extensions.backends.ray import ExecutorRayRemote as Executor
            else:
                from radcad.extensions.backends.ray import ExecutorRay as Executor
        elif self.backend in [Backend.PATHOS, Backend.DEFAULT]:
            from radcad.backends.pathos import ExecutorPathos as Executor
        elif self.backend in [Backend.MULTIPROCESSING]:
            from radcad.backends.multiprocessing import ExecutorMultiprocessing as Executor
        elif self.backend in [Backend.SINGLE_PROCESS]:
            from radcad.backends.single_process import ExecutorSingleProcess as Executor
        else:
            raise Exception(f"Execution backend must be one of {Backend._member_names_}, not {self.backend}")
        
        result = Executor(self).execute_runs()
        
        self.executable.results, self.executable.exceptions = extract_exceptions(result)
        self.executable._after_experiment(experiment=(executable if isinstance(executable, wrappers.Experiment) else None))
        return self.executable.results

    def _get_simulation_from_config(config):
        states, state_update_blocks, params, timesteps, runs = config
        model = wrappers.Model(
            initial_state=states, state_update_blocks=state_update_blocks, params=params
        )
        return wrappers.Simulation(model=model, timesteps=timesteps, runs=runs)

    def _run_stream(self, configs):
        simulations = [Engine._get_simulation_from_config(config) for config in configs]

        for simulation_index, simulation in enumerate(simulations):
            simulation.index = simulation_index
            
            timesteps = simulation.timesteps
            runs = simulation.runs
            initial_state = simulation.model.initial_state
            state_update_blocks = simulation.model.state_update_blocks
            params = simulation.model.params
            param_sweep = core.generate_parameter_sweep(params)

            self.executable._before_simulation(
                simulation=simulation
            )

            # NOTE Hook allows mutation of RunArgs
            for run_index in range(0, runs):
                if param_sweep:
                    context = wrappers.Context(
                        simulation_index,
                        run_index,
                        None,
                        timesteps,
                        initial_state,
                        params
                    )
                    self.executable._before_run(context=context)
                    for subset_index, param_set in enumerate(param_sweep):
                        context = wrappers.Context(
                            simulation_index,
                            run_index,
                            subset_index,
                            timesteps,
                            initial_state,
                            params
                        )
                        self.executable._before_subset(context=context)
                        yield wrappers.RunArgs(
                            simulation_index,
                            timesteps,
                            run_index,
                            subset_index,
                            copy.deepcopy(initial_state),
                            state_update_blocks,
                            copy.deepcopy(param_set),
                            self.deepcopy,
                            self.drop_substeps,
                        )
                        self.executable._after_subset(context=context)
                    self.executable._after_run(context=context)
                else:
                    context = wrappers.Context(
                        simulation_index,
                        run_index,
                        0,
                        timesteps,
                        initial_state,
                        params
                    )
                    self.executable._before_run(context=context)
                    self.executable._before_subset(context=context)
                    yield wrappers.RunArgs(
                        simulation_index,
                        timesteps,
                        run_index,
                        0,
                        copy.deepcopy(initial_state),
                        state_update_blocks,
                        copy.deepcopy(params),
                        self.deepcopy,
                        self.drop_substeps,
                    )
                    self.executable._after_subset(context=context)
                    self.executable._after_run(context=context)

            self.executable._after_simulation(
                simulation=simulation
            )
