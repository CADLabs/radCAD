# Engine settings

The [`Engine`](api.md#radcad.engine.Engine) owns all execution-time configuration. Construct one and assign it to a `Simulation` or `Experiment`:

```python
from radcad import Engine, Backend

experiment.engine = Engine(
    backend=Backend.PATHOS,
    processes=4,
    deepcopy=True,
    drop_substeps=False,
    raise_exceptions=True,
)
result = experiment.run()
```

## Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `backend` | `Backend` | `Backend.DEFAULT` (= `PATHOS`) | Parallel-processing backend. The `RADCAD_BACKEND` environment variable, if set, takes precedence. See [Choose a backend](../how-to/choose-a-backend.md). |
| `processes` | `int` | `cpu_count - 1` (min `1`) | Number of worker processes to spawn. |
| `raise_exceptions` | `bool` | `True` | Raise on failure, or catch and return partial results plus exception metadata. See [Handle exceptions](../how-to/handle-exceptions.md). |
| `deepcopy` | `bool` | `True` | Deepcopy State Variables to prevent unintended mutation. Disable for speed. See [Improve performance](../how-to/improve-performance.md). |
| `deepcopy_method` | `Callable` | `pickle`-based | Method used for deepcopies. Defaults to Pickle dumps/loads for speed; supply `copy.deepcopy` for broader type support. |
| `drop_substeps` | `bool` | `False` | Keep only the final substep per timestep, saving memory and time. |
| `simulation_execution` | `SimulationExecution` | auto | A custom [`SimulationExecution`](api.md#radcad.core.SimulationExecution) instance/subclass. Overrides `raise_exceptions`, `deepcopy`, `deepcopy_method`, and `drop_substeps`. |

Passing an unrecognised option raises an exception, so typos fail fast.

## Environment variables

| Variable | Effect |
| --- | --- |
| `RADCAD_BACKEND` | Overrides the `backend` option, e.g. `RADCAD_BACKEND=SINGLE_PROCESS`. Used in CI and required for Windows tests to avoid recursion-depth errors. |

## Customising the simulation loop

To change execution behaviour beyond the options above (for example, the deepcopy method, or any step of the loop), subclass [`SimulationExecution`](api.md#radcad.core.SimulationExecution) and assign it:

```python
import copy
from radcad.core import SimulationExecution

class CustomSimulationExecution(SimulationExecution):
    @staticmethod
    def deepcopy_method(obj):
        return copy.deepcopy(obj)

experiment.engine.simulation_execution = CustomSimulationExecution
```

See [Improve performance](../how-to/improve-performance.md) for the rationale.
