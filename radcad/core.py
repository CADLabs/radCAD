from functools import reduce, partial
import logging
import pickle
import traceback
from typing import Dict, Iterator, List, Tuple, Callable
from dataclasses import is_dataclass
from radcad.types import Dataclass, PolicySignal, SimulationResults, StateUpdate, StateUpdateBlock, StateVariables, SystemParameters
from radcad.utils import extend_list


# Use "radCAD" logging instance to avoid conflict with other projects
logger = logging.getLogger("radCAD")

# Define the default method used for deepcopy operations
# Must be a function and not a lambda function to ensure multiprocessing can Pickle the object
def default_deepcopy_method(obj):
    return pickle.loads(pickle.dumps(obj=obj, protocol=-1))


def _update_state(
    initial_state: StateVariables,
    params: SystemParameters,
    substep: int,
    result: SimulationResults,
    substate: StateVariables,
    signals: PolicySignal,
    deepcopy: bool,
    deepcopy_method: Callable,
    state_update_tuple: StateUpdate,
) -> StateUpdate:
    _substate = deepcopy_method(substate) if deepcopy else substate.copy()
    _signals = deepcopy_method(signals) if deepcopy else signals.copy()

    state, function = state_update_tuple
    if not state in initial_state:
        raise KeyError(f"Invalid state key {state} in partial state update block")
    state_key, state_value = function(
        params, substep, result, _substate, _signals
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
    result: SimulationResults,
    simulation: int,
    timesteps: int,
    run: int,
    subset: int,
    initial_state: StateVariables,
    state_update_blocks: List[StateUpdateBlock],
    params: SystemParameters,
    deepcopy: bool,
    deepcopy_method: Callable,
    drop_substeps: bool,
) -> SimulationResults:
    logger.info(f"Starting simulation {simulation} / run {run} / subset {subset}")

    initial_state["simulation"] = simulation
    initial_state["subset"] = subset
    initial_state["run"] = run
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
            
            signals: dict = reduce_signals(
                params, substep, result, substate, psu, deepcopy, deepcopy_method
            )

            updated_state = map(
                partial(
                    _update_state,
                    initial_state,
                    params,
                    substep,
                    result,
                    substate,
                    signals,
                    deepcopy,
                    deepcopy_method,
                ),
                psu["variables"].items()
            )
            
            substate.update(updated_state)
            substate["timestep"] = (previous_state["timestep"] + 1) if timestep == 0 else timestep + 1
            substate["substep"] = substep + 1
            substeps.append(substate)

        substeps = [substate] if not substeps else substeps
        result.append(substeps if not drop_substeps else [substeps.pop()])
    return result


def single_run(
    simulation: int=0,
    timesteps: int=1,
    run: int=0,
    subset: int=0,
    initial_state: StateVariables={},
    state_update_blocks: List[StateUpdateBlock]=[],
    params: SystemParameters={},
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


def _get_sweep_lengths(params: Dict) -> Iterator[int]:
    for value in params.values():
        if isinstance(value, dict):
            yield from _get_sweep_lengths(value)
        elif isinstance(value, list):
            yield len(value)


def _get_sweep_length(params: Dict) -> int:
    sweep_lengths = list(_get_sweep_lengths(params))
    return max(sweep_lengths) if sweep_lengths else 1


def _nested_asdict(params: Dataclass) -> Dict:
    """
    Recursively follow any continuous nested chain of dataclasses
    converting to dictionaries, e.g.:

    @dataclass
    class D:
        e = [3, 4]
        f = 5

    @dataclass
    class I:
        j: int = 9

    @dataclass
    class H:
        i: I = I()

    @dataclass
    class NestedParams:
        a: dict = default({
            'b': 1,
            'c': [2],
            'd': D(),
        })
        g: list = default([6, 7, 8])
        h: list = H()

    _nested_asdict(NestedParams()) == {
        'a': {'b': 1, 'c': [2], 'd': D()},
        'g': [6, 7, 8],
        'h': {'i': {'j': 9}}
    }
    """
    dict_params = {}
    if is_dataclass(params):
        for (key, value) in params.__dict__.items():
            if is_dataclass(value):
                value = _nested_asdict(value)
            dict_params[key] = value
    return dict_params


def _traverse_params(params: SystemParameters) -> SystemParameters:
    parent_class = None
    dict_params = {}
    if is_dataclass(params):
        parent_class = params.__class__
        for (key, value) in params.__dict__.items():
            if is_dataclass(value):
                value = _traverse_params(value)
            elif not isinstance(value, list):
                value = [value]
            dict_params[key] = value

    return parent_class(**dict_params) if parent_class else dict_params


def _traverse_sweep_params(params: SystemParameters, max_len: int, sweep_index: int):
    parent_class = None
    dict_params = {}
    if is_dataclass(params):
        parent_class = params.__class__
        children = params.__dict__.items()
    elif isinstance(params, dict):
        children = params.items()
    else:
        return dict_params

    for (key, value) in children:
        if is_dataclass(value):
            value = _traverse_sweep_params(value, max_len, sweep_index)
        elif not isinstance(value, list):
            value = [value]
        if isinstance(value, list):
            value = extend_list(value, max_len)[sweep_index]
        dict_params[key] = value

    return parent_class(**dict_params) if parent_class else dict_params


def generate_parameter_sweep(params: SystemParameters) -> List[SystemParameters]:
    _is_dataclass = is_dataclass(params)
    _params = _nested_asdict(params) if _is_dataclass else params
    max_len = _get_sweep_length(_params)

    param_sweep = []
    for sweep_index in range(0, max_len):
        param_set = _traverse_sweep_params(params, max_len, sweep_index)
        param_sweep.append(param_set)
    return param_sweep


def _add_signals(acc: PolicySignal, a: PolicySignal) -> PolicySignal:
    for (key, value) in a.items():
        if acc.get(key, None):
            acc[key] += value
        else:
            acc[key] = value
    return acc


def reduce_signals(
    params: SystemParameters,
    substep: int,
    result: list,
    substate: StateVariables,
    psu: StateUpdateBlock,
    deepcopy: bool=True,
    deepcopy_method: Callable=default_deepcopy_method
) -> PolicySignal:
    policy_results: List[PolicySignal] = list(
        map(lambda function: function(
            params,
            substep,
            result,
            deepcopy_method(substate) if deepcopy else substate.copy()
        ), psu["policies"].values())
    )

    result: dict = {}
    result_length = len(policy_results)
    if result_length == 0:
        return result
    elif result_length == 1:
        return policy_results[0]
    else:
        return reduce(_add_signals, policy_results, result)
