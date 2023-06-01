"""radCAD model model software architecture (structural and configuration modules)

In this package:

- `core` - data classes for simulation configuration (`SimulationExecutionSpecification`, `SimulationExecution`)
- `engine` - configuration and execution of experiments and simulations (`engine`)
- `types` - helper functions for input/data processing `Dataclass`, `Context`
- `utils` - various utility functions for data or variable processing
- `wrappers` - the main classes needed to specify the model and simulation specification (`Model`, `Executable`, `Simulation`, `Experiment`)
"""

__version__ = "0.12.0"

from radcad.wrappers import Model, Simulation, Experiment
from radcad.core import SimulationExecution
from radcad.types import Context
from radcad.engine import Engine
from radcad.backends import Backend
