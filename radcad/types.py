"""Type aliases describing radCAD's core data structures.

These aliases name the data shapes that flow through a simulation: the State
Variables, System Parameters, Policy Signals, and Partial State Update Blocks.
Use them as type hints in model functions for clearer, self-documenting models.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple, Union, NamedTuple
from typing_extensions import Protocol


class Dataclass(Protocol):
    """Structural type matching any ``@dataclass`` instance.

    Used so System Parameters can be either a plain dict or a (nested)
    dataclass. Membership is detected via the ``__dataclass_fields__``
    attribute, currently the most reliable check.
    """

    # Checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: Dict


StateUpdateBlock = Dict[str, Dict[str, Callable]]
"""A Partial State Update Block: ``{"policies": {...}, "variables": {...}}``."""

SystemParameters = Union[Dict[str, List[Any]], Dataclass]
"""System Parameters as a dict of lists (sweepable) or a (nested) dataclass."""

StateVariables = Dict[str, Any]
"""A mapping of State Variable name to value at a single substep."""

SimulationResults = List[List[Dict[str, Any]]]
"""Raw nested results: a list of timesteps, each a list of substep states."""

PolicySignal = Dict[str, Any]
"""The aggregated output of a block's Policy Functions for one substep."""

StateUpdate = Tuple[str, Callable]
"""A ``(state_variable_name, state_update_function)`` pair."""

StateUpdateResult = Tuple[str, Any]
"""The ``(key, value)`` returned by a State Update Function."""


@dataclass
class Context:
    """
    Mutable context passed to simulation hooks
    """
    simulation: int = None
    run: int = None
    subset: int = None
    timesteps: int = None
    initial_state: StateVariables = None
    parameters: SystemParameters = None
    state_update_blocks: List[StateUpdateBlock] = None
