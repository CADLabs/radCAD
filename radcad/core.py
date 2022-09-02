from functools import reduce, partial
import logging
import pickle
import traceback
from typing import Dict, List, Tuple, Callable


# Use "radCAD" logging instance to avoid conflict with other projects
logger = logging.getLogger("radCAD")

# Define the default method used for deepcopy operations
# Must be a function and not a lambda function to ensure multiprocessing can Pickle the object
def default_deepcopy_method(obj):
    return pickle.loads(pickle.dumps(obj=obj, protocol=-1))


def _update_state(initial_state, params, substep, result, substate, signals, state_update_tuple):
    state, function = state_update_tuple
    if not state in initial_state:
        raise KeyError(f"Invalid state key {state} in partial state update block")
    state_key, state_value = function(
        params, substep, result, substate, signals
    )
    if not state_key in initial_state:
        raise KeyError(
            f"Invalid state key {state} returned from state update function"
        )
    if state == state_key:
        return (state_key, state_value)
    else:
        raise KeyError(
            f"PSU state key {state} doesn't match function state key {state_key}"
        )


def _single_run(
    result: list,
    simulation: int,
    timesteps: int,
    run: int,
    subset: int,
    initial_state: dict,
    state_update_blocks: list,
    params: dict,
    deepcopy: bool,
    deepcopy_method: Callable,
    drop_substeps: bool,
):
    logger.info(f"Starting simulation {simulation} / run {run} / subset {subset}")

    initial_state["simulation"] = simulation
    initial_state["subset"] = subset
    initial_state["run"] = run + 1
    initial_state["substep"] = 0
    if not initial_state.get("timestep", False):
        initial_state["timestep"] = 0

    result.append([initial_state])

    for timestep in range(0, timesteps):
        previous_state: dict = (
            result[0][0].copy()
            if timestep == 0
            else result[-1][-1:][0].copy()
        )

        substeps: list = []
        substate: dict = previous_state.copy()

        for (substep, psu) in enumerate(state_update_blocks):
            substate: dict = (
                previous_state.copy() if substep == 0 else substeps[substep - 1].copy()
            )

            # Create two independent deepcopies to ensure a policy function
            # can't mutate the state passed to the state update functions
            policy_substate_copy = deepcopy_method(substate) if deepcopy else substate.copy()
            state_update_substate_copy = deepcopy_method(substate) if deepcopy else substate.copy()

            substate["substep"] = substep + 1
            
            signals: dict = reduce_signals(
                params, substep, result, policy_substate_copy, psu, deepcopy
            )

            updated_state = map(
                partial(_update_state, initial_state, params, substep, result, state_update_substate_copy, signals),
                psu["variables"].items()
            )
            substate.update(updated_state)
            substate["timestep"] = (previous_state["timestep"] + 1) if timestep == 0 else timestep + 1
            substeps.append(substate)

        substeps = [substate] if not substeps else substeps
        result.append(substeps if not drop_substeps else [substeps.pop()])
    return result


def single_run(
    simulation=0,
    timesteps=1,
    run=0,
    subset=0,
    initial_state={},
    state_update_blocks=[],
    params={},
    deepcopy: bool=True,
    deepcopy_method: Callable=default_deepcopy_method,
    drop_substeps: bool=False,
) -> Tuple[list, Exception, str]:
    result = []

    try:
        return (
            _single_run(
                result,
                simulation,
                timesteps,
                run,
                subset,
                initial_state,
                state_update_blocks,
                params,
                deepcopy,
                deepcopy_method,
                drop_substeps,
            ),
            None, # Error
            None, # Traceback
        )
    except Exception as error:
        trace = traceback.format_exc()
        print(trace)
        logger.warning(
            f"Simulation {simulation} / run {run} / subset {subset} failed! Returning partial results if Engine.raise_exceptions == False."
        )
        return (result, error, trace)


def _single_run_wrapper(args):
    run_args, raise_exceptions = args
    try:
        results, exception, traceback = single_run(*tuple(run_args))
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


def generate_parameter_sweep(params: Dict[str, List[any]]):
    param_sweep = []
    max_len = 0
    for value in params.values():
        if len(value) > max_len:
            max_len = len(value)

    for sweep_index in range(0, max_len):
        param_set = {}
        for (key, value) in params.items():
            param = (
                value[sweep_index]
                if sweep_index < len(value)
                else value[-1]
            )
            param_set[key] = param
        param_sweep.append(param_set)

    return param_sweep


def _add_signals(acc, a: Dict[str, any]):
    for (key, value) in a.items():
        if acc.get(key, None):
            acc[key] += value
        else:
            acc[key] = value
    return acc


def reduce_signals(params: dict, substep: int, result: list, substate: dict, psu: dict, deepcopy: bool=True, deepcopy_method: Callable=default_deepcopy_method):
    policy_results: List[Dict[str, any]] = list(
        map(lambda function: function(params, substep, result, substate), psu["policies"].values())
    )

    result: dict = {}
    result_length = len(policy_results)
    if result_length == 0:
        return result
    elif result_length == 1:
        return deepcopy_method(policy_results[0]) if deepcopy else policy_results[0].copy()
    else:
        return reduce(_add_signals, policy_results, result)
