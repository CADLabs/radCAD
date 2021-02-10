import radcad.core as core
import radcad.wrappers as wrappers
from radcad.utils import flatten, extract_exceptions

import multiprocessing

# Pathos re-writes the core code in Python rather than C, for ease of maintenance at cost of performance
from pathos.multiprocessing import ProcessPool as PathosPool
import dill

import ray

from enum import Enum
import copy


cpu_count = multiprocessing.cpu_count() - 1 or 1


class Backend(Enum):
    DEFAULT = 0
    MULTIPROCESSING = 1
    RAY = 2
    RAY_REMOTE = 3
    PATHOS = 4
    SINGLE_PROCESS = 5


class Engine:
    def __init__(self, **kwargs):
        self.experiment = None
        self.processes = kwargs.pop("processes", cpu_count)
        self.backend = kwargs.pop("backend", Backend.DEFAULT)
        self.raise_exceptions = kwargs.pop("raise_exceptions", True)
        self.deepcopy = kwargs.pop("deepcopy", True)
        self.drop_substeps = kwargs.pop("drop_substeps", False)

        if kwargs:
            raise Exception(f"Invalid Engine option in {kwargs}")

    def _run(self, experiment=None, **kwargs):
        if not experiment:
            raise Exception("Experiment required as argument")
        self.experiment = experiment

        if kwargs:
            raise Exception(f"Invalid Engine option in {kwargs}")

        simulations = experiment.simulations
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

        self.experiment._before_experiment(experiment=self.experiment)

        run_generator = self._run_stream(configs)

        if self.backend in [Backend.RAY, Backend.RAY_REMOTE]:
            if self.backend == Backend.RAY_REMOTE:
                print(
                    "Using Ray remote backend, please ensure you've initialized Ray using ray.init(address=***, ...)"
                )
            else:
                ray.init(num_cpus=self.processes, ignore_reinit_error=True)

            futures = [
                Engine._proxy_single_run_ray.remote((config, self.raise_exceptions))
                for config in run_generator
            ]
            result = ray.get(futures)
        elif self.backend in [Backend.PATHOS, Backend.DEFAULT]:
            with PathosPool(self.processes) as pool:
                result = pool.map(
                    Engine._proxy_single_run,
                    [
                        (config, self.raise_exceptions)
                        for config in run_generator
                    ],
                )
                pool.close()
                pool.join()
                pool.clear()
        elif self.backend in [Backend.MULTIPROCESSING]:
            with multiprocessing.get_context("spawn").Pool(
                processes=self.processes
            ) as pool:
                result = pool.map(
                    Engine._proxy_single_run,
                    [
                        (config, self.raise_exceptions)
                        for config in run_generator
                    ],
                )
                pool.close()
                pool.join()
        elif self.backend in [Backend.SINGLE_PROCESS]:
            result = [
                Engine._proxy_single_run((config, self.raise_exceptions))
                for config in run_generator
            ]
        else:
            raise Exception(f"Execution backend must be one of {Backend._member_names_}, not {self.backend}")
        
        self.experiment.results, self.experiment.exceptions = extract_exceptions(result)
        self.experiment._after_experiment(experiment=self.experiment)
        return self.experiment.results

    @ray.remote
    def _proxy_single_run_ray(args):
        return Engine._proxy_single_run(args)
    
    def _proxy_single_run(args):
        return Engine._single_run(args)

    def _single_run(args):
        run_args, raise_exceptions = args
        try:
            results, exception, traceback = core.single_run(*tuple(run_args))
            if raise_exceptions and exception:
                raise exception
            else:
                return results, {
                        'exception': exception,
                        'traceback': traceback,
                        'simulation': run_args.simulation,
                        'run': run_args.run,
                        'subset': run_args.subset,
                        'timesteps': run_args.timesteps,
                        'parameters': run_args.parameters,
                        'initial_state': run_args.initial_state,
                    }
        except Exception as e:
            if raise_exceptions:
                raise e
            else:
                return [], e

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

            self.experiment._before_simulation(
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
                    self.experiment._before_run(context=context)
                    for subset_index, param_set in enumerate(param_sweep):
                        context = wrappers.Context(
                            simulation_index,
                            run_index,
                            subset_index,
                            timesteps,
                            initial_state,
                            params
                        )
                        self.experiment._before_subset(context=context)
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
                        self.experiment._after_subset(context=context)
                    self.experiment._before_run(context=context)
                else:
                    context = wrappers.Context(
                        simulation_index,
                        run_index,
                        0,
                        timesteps,
                        initial_state,
                        params
                    )
                    self.experiment._before_run(context=context)
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
                    self.experiment._after_run(context=context)

            self.experiment._after_simulation(
                simulation=simulation
            )
