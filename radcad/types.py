from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple, Union, NamedTuple
from typing_extensions import Protocol


class Dataclass(Protocol):
    # Checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: Dict


StateUpdateBlock = Dict[str, Dict[str, Callable]]
SystemParameters = Union[Dict[str, List[Any]], Dataclass]
StateVariables = Dict[str, Any]
SimulationResults = List[List[Dict[str, Any]]]
PolicySignal = Dict[str, Any]
StateUpdate = Tuple[str, Callable]
StateUpdateResult = Tuple[str, Any]


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
