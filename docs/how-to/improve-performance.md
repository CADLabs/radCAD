# Improve performance

The biggest cost in a radCAD (and cadCAD) simulation is **deep-copying state** to protect it from accidental mutation. These options trade safety or detail for speed. Measure before and after; the right choice depends on your model.

## Disable `deepcopy`

By default radCAD deep-copies State Variables before each state update so your functions can't mutate state outside the framework. Disabling this is the single biggest performance win, at the cost of mutability safety:

```python
from radcad import Engine

experiment.engine = Engine(deepcopy=False)
```

!!! warning
    With `deepcopy=False`, mutating a nested object in your state (e.g. a list or dict) **will** leak across timesteps. Only disable it if your state update functions treat state as immutable. See [State mutation & performance](../explanation/state-mutation-and-performance.md).

## Choose a faster `deepcopy` method

When you do need copying, the *method* matters. radCAD defaults to `pickle` (faster than `copy.deepcopy`, but limited to picklable types). To use a different method, subclass [`SimulationExecution`](../reference/api.md#radcad.core.SimulationExecution) and override `deepcopy_method`:

```python
import copy
from radcad.core import SimulationExecution

class CustomSimulationExecution(SimulationExecution):
    @staticmethod
    def deepcopy_method(obj):
        """Use copy.deepcopy instead of the default Pickle dumps/loads."""
        return copy.deepcopy(obj)

experiment.engine.simulation_execution = CustomSimulationExecution
```

The same subclassing technique works for overriding any other step of the simulation loop.

## Drop substeps

If you don't need intermediate substeps in post-processing, drop them to cut both runtime and dataset size. Only the final substep of each timestep is kept:

```python
experiment.engine = Engine(drop_substeps=True)
```

## Tune parallelism

- Make sure you're on a parallel [backend](choose-a-backend.md) (`PATHOS` is the default).
- For very large ensembles, scale onto [Ray](run-on-a-ray-cluster.md).
- More processes isn't always faster: process startup and data serialisation have overhead. Benchmark with your real model.

## Benchmark your changes

The repository includes time and memory benchmarks under [`benchmarks/`](https://github.com/CADLabs/radCAD/tree/master/benchmarks):

```bash
# Time profiling
pdm run pytest benchmarks/benchmark_radcad.py
pdm run pytest benchmarks/benchmark_single_process.py

# Memory profiling
pdm run mprof run benchmarks/benchmark_memory_radcad.py
pdm run mprof plot
```

## See also

- [State mutation & performance](../explanation/state-mutation-and-performance.md): why deepcopy is the bottleneck.
- [Engine settings](../reference/engine-settings.md): all execution options in one place.
