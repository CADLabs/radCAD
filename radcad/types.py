from typing import Any, Callable, Dict, List, Tuple, Union
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
StateUpdate = Tuple[str, Any]
