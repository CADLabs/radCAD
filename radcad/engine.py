import radcad.core as core

import multiprocessing

# Pathos re-writes the core code in Python rather than C, for ease of maintenance at cost of performance
from pathos.multiprocessing import ProcessPool as PathosPool
import dill

import ray

from enum import Enum

flatten = lambda list: [item for sublist in list for item in sublist]

cpu_count = multiprocessing.cpu_count() - 1 or 1

class Backend(Enum):
    DEFAULT = 0
    MULTIPROCESSING = 1
    RAY = 2
    RAY_REMOTE = 3
    PATHOS = 4
    BASIC = 5

class Engine():
    def __init__(self, **kwargs):
        self.experiment = None
        self.processes = kwargs.pop('processes', cpu_count)
        self.backend = kwargs.pop('backend', Backend.DEFAULT)

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

        self.experiment._before_experiment(engine=self)

        if self.backend in [Backend.RAY, Backend.RAY_REMOTE]:
            if self.backend == Backend.RAY_REMOTE:
                print("Using Ray remote backend, please ensure you've initialized Ray using ray.init(address=***, ...)")
            else:
                ray.init(num_cpus=self.processes, ignore_reinit_error=True)

            futures = [Engine._proxy_single_run_ray.remote(config) for config in self._run_stream(configs)]
            result = flatten(flatten(ray.get(futures)))
        elif self.backend == Backend.PATHOS:
            with PathosPool(processes=self.processes) as pool:
                mapped = pool.map(Engine._proxy_single_run, self._run_stream(configs))
                result = flatten(flatten(mapped))
        elif self.backend in [Backend.MULTIPROCESSING, Backend.DEFAULT]:
            with multiprocessing.get_context("spawn").Pool(processes=self.processes) as pool:
                mapped = pool.map(Engine._proxy_single_run, self._run_stream(configs))
                result = flatten(flatten(mapped))
        elif self.backend in [Backend.BASIC]:
            result = flatten(flatten([Engine._proxy_single_run(config) for config in self._run_stream(configs)]))
        else:
            raise Exception(f"Execution backend must be one of {Backend.list()}")

        self.experiment._after_experiment(engine=self)

        return result


    @ray.remote
    def _proxy_single_run_ray(args):
        return core.single_run(*args)


    def _proxy_single_run(args):
        return core.single_run(*args)


    def _get_simulation_from_config(config):
        states, state_update_blocks, params, timesteps, runs = config
        model = core.Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
        return core.Simulation(model=model, timesteps=timesteps, runs=runs)


    def _run_stream(self, configs):
        simulations = [Engine._get_simulation_from_config(config) for config in configs]

        for simulation_index, simulation in enumerate(simulations):
            timesteps = simulation.timesteps
            runs = simulation.runs
            initial_state = simulation.model.initial_state
            state_update_blocks = simulation.model.state_update_blocks
            params = simulation.model.params
            param_sweep = core.generate_parameter_sweep(params)

            self.experiment._before_simulation(simulation=simulation, simulation_index=simulation_index)

            for run_index in range(0, runs):
                self.experiment._before_run(simulation=simulation, run_index=run_index)
                if param_sweep:
                    for subset, param_set in enumerate(param_sweep):
                        yield (
                            simulation_index,
                            timesteps,
                            run_index,
                            subset,
                            initial_state,
                            state_update_blocks,
                            param_set,
                        )
                else:
                    yield (
                        simulation_index,
                        timesteps,
                        run_index,
                        0,
                        initial_state,
                        state_update_blocks,
                        params,
                    )
                self.experiment._after_run(simulation=simulation, run_index=run_index)
            
            self.experiment._after_simulation(simulation=simulation, simulation_index=simulation_index)
