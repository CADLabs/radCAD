import copy
import datetime
import itertools
from dataclasses import field, is_dataclass
from functools import partial
from typing import Dict, Iterator, List

from radcad.types import Dataclass, SystemParameters


def flatten(nested_list):
    def generator(nested_list):
        for sublist in nested_list:
            if isinstance(sublist, list):
                for item in sublist:
                    yield item
            else:
                yield sublist

    return list(generator(nested_list))


def extend_list(list, target_length):
    """Extend list to length by repeating last element"""
    if len(list) >= target_length:
        return list
    else:
        extension = [list[-1] if list else None] * (target_length - len(list))
        return list + extension


def extract_exceptions(results_with_exceptions):
    results, exceptions = zip(*results_with_exceptions)
    return (list(flatten(flatten(list(results)))), list(exceptions))


def generate_cartesian_product_parameter_sweep(params):
    cartesian_product = list(itertools.product(*params.values()))
    param_sweep = {key: [x[i] for x in cartesian_product] for i, key in enumerate(params.keys())}
    return param_sweep


def _get_sweep_lengths(params: SystemParameters) -> Iterator[int]:
    if is_dataclass(params):
        children = params.__dict__.items()
    elif isinstance(params, dict):
        children = params.items()
    else:
        yield []

    for (_key, value) in children:
        if is_dataclass(value):
            yield from _get_sweep_lengths(value)
        elif not isinstance(value, list):
            value = [value]
        if isinstance(value, list):
            yield len(value)


def _get_sweep_length(params: SystemParameters) -> int:
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
    max_len = _get_sweep_length(params)
    param_sweep = []
    for sweep_index in range(0, max_len):
        param_set = _traverse_sweep_params(params, max_len, sweep_index)
        param_sweep.append(param_set)
    return param_sweep


def _update_from_signal(
    state_variable,
    signal_key,
    optional_update,
    params,
    substep,
    state_history,
    previous_state,
    policy_input,
):
    """A private function used to generate the partial function returned by `update_from_signal(...)`."""
    if not signal_key in policy_input and optional_update:
        return state_variable, previous_state[state_variable]
    else:
        return state_variable, policy_input[signal_key]


def update_from_signal(state_variable, signal_key=None, optional_update=False):
    """
    A generic State Update Function to update a State Variable directly from a Policy Signal,
    useful to avoid boilerplate code.
    Args:
        state_variable (str): State Variable key
        signal_key (str, optional): Policy Signal key. Defaults to None.
        optional_update (bool, optional): If True, only update State Variable if Policy Signal key exists.
    Returns:
        Callable: A generic State Update Function
    """
    if not signal_key:
        signal_key = state_variable
    return partial(_update_from_signal, state_variable, signal_key, optional_update)


def _accumulate_from_signal(
    state_variable,
    signal_key,
    params,
    substep,
    state_history,
    previous_state,
    policy_input,
):
    """A private function used to generate the partial function returned by `accumulate_from_signal(...)`."""
    return state_variable, previous_state[state_variable] + policy_input[signal_key]


def accumulate_from_signal(state_variable, signal_key=None):
    """
    A generic State Update Function to accumulate a State Variable directly from a Policy Signal,
    useful to avoid boilerplate code.
    """
    if not signal_key:
        signal_key = state_variable
    return partial(_accumulate_from_signal, state_variable, signal_key)


def update_timestamp(params, substep, state_history, previous_state, policy_input):
    """
    A radCAD State Update Function used to calculate and update the current timestamp
    given a timestep and starting date parameter.
    """
    # Parameters
    dt = params["dt"]
    date_start = params["date_start"]

    # State Variables
    timestep = previous_state["timestep"]

    # Calculate current timestamp from timestep
    timestamp = date_start + datetime.timedelta(days=timestep * dt)

    return "timestamp", timestamp


def local_variables(_locals):
    """Return a dictionary of all local variables, useful for debugging."""
    return {key: _locals[key] for key in [_key for _key in _locals.keys() if "__" not in _key]}


def default(obj):
    """Used and necessary when setting the default value of a dataclass field to a list."""
    return field(default_factory=lambda: copy.copy(obj))
