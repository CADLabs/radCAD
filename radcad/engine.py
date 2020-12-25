import radcad.core as core

import multiprocessing
from multiprocessing import Pool

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
    PATHOS = 3


def run(simulations, processes=cpu_count, backend=Backend.DEFAULT):
    if not isinstance(backend, Backend):
        raise Exception(f"Execution backend must be one of {Backend.list()}")
    configs = [
        (
            sim.model.initial_state,
            sim.model.psubs,
            sim.model.params,
            sim.timesteps,
            sim.runs,
        )
        for sim in simulations
    ]
    result = []

    if backend == Backend.RAY:
        ray.init()

        @ray.remote
        def proxy_single_run_ray(args):
            return core.single_run(*args)

        futures = [proxy_single_run_ray.remote(config) for config in run_stream(configs)]
        result = flatten(ray.get(futures))
    elif backend == Backend.PATHOS:
        with PathosPool(processes=processes) as pool:
            mapped = pool.map(proxy_single_run, run_stream(configs))
            result = flatten(mapped)
    elif backend in [Backend.MULTIPROCESSING, Backend.DEFAULT]:
        with Pool(processes=processes) as pool:
            mapped = pool.map(proxy_single_run, run_stream(configs))
            result = flatten(mapped)
    else:
        raise Exception(f"Execution backend must be one of {Backend.list()}")

    return result


def proxy_single_run(args):
    return core.single_run(*args)


def get_simulation_from_config(config):
    states, psubs, params, timesteps, runs = config
    model = core.Model(initial_state=states, psubs=psubs, params=params)
    return core.Simulation(model=model, timesteps=timesteps, runs=runs)


def run_stream(configs):
    simulations = [get_simulation_from_config(config) for config in configs]

    for simulation_index, simulation in enumerate(simulations):
        timesteps = simulation.timesteps
        runs = simulation.runs
        initial_state = simulation.model.initial_state
        psubs = simulation.model.psubs
        params = simulation.model.params
        param_sweep = core.generate_parameter_sweep(params)

        for run in range(0, runs):
            if param_sweep:
                for subset, param_set in enumerate(param_sweep):
                    yield (
                        simulation_index,
                        timesteps,
                        run,
                        subset,
                        initial_state,
                        psubs,
                        param_set,
                    )
            else:
                yield (
                    simulation_index,
                    timesteps,
                    run,
                    0,
                    initial_state,
                    psubs,
                    params,
                )
