import itertools
import copy
import datetime
from dataclasses import field
from functools import partial


def flatten(nested_list):
    def generator(nested_list):
        for sublist in nested_list:
            if isinstance(sublist, list):
                for item in sublist:
                    yield item
            else:
                yield sublist

    return list(generator(nested_list))


def extract_exceptions(results_with_exceptions):
    results, exceptions = zip(*results_with_exceptions)
    return (list(flatten(flatten(list(results)))), list(exceptions))


def generate_cartesian_product_parameter_sweep(params):
    cartesian_product = list(itertools.product(*params.values()))
    param_sweep = {key: [x[i] for x in cartesian_product] for i, key in enumerate(params.keys())}
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
