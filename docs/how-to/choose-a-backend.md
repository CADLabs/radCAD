# Choose a processing backend

radCAD runs the independent units of work in a simulation (each run × subset) in parallel. The **backend** determines *how* that parallelism happens. The default works well for most cases. Switch backends to debug, to maximise compatibility, or to scale onto a cluster.

## Available backends

| `Backend` | Description | When to use |
| --- | --- | --- |
| `DEFAULT` | Alias for `PATHOS`. | The default; leave it alone unless you have a reason. |
| `PATHOS` | Local multiprocessing via [`pathos`](https://pathos.readthedocs.io/) (uses `dill`). | Default; handles lambdas, closures, and most objects. |
| `MULTIPROCESSING` | Local multiprocessing via the standard library. | When you want only stdlib pickling semantics. |
| `SINGLE_PROCESS` | No parallelism; runs sequentially. | Debugging, profiling, or small models. |
| `RAY` | Local execution via [Ray](https://ray.io/). | Larger workloads; stepping stone to a cluster. |
| `RAY_REMOTE` | Distributed execution on a remote Ray cluster. | Scaling out; see [Run on a Ray cluster](run-on-a-ray-cluster.md). |

## Select a backend

Pass a [`Backend`](../reference/api.md#radcad.backends.Backend) to the [`Engine`](../reference/api.md#radcad.engine.Engine):

```python
from radcad import Engine, Backend

experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)
result = experiment.run()
```

You can also override the backend via the `RADCAD_BACKEND` environment variable, which takes precedence over the code setting (useful in CI, and required for Windows tests to avoid recursion-depth errors):

```bash
export RADCAD_BACKEND=SINGLE_PROCESS
```

## Control the number of processes

By default radCAD uses `cpu_count - 1` (at least one) processes. Override it with `processes`:

```python
from radcad import Engine

experiment.engine = Engine(processes=1)   # effectively single-process via the pool
result = experiment.run()
```

!!! tip "Debugging a failing model"
    Parallel backends swallow tracebacks behind process boundaries. When a model misbehaves, switch to `Backend.SINGLE_PROCESS` (or `processes=1`) to get clean, in-process stack traces, then switch back for speed. See also [Handle exceptions](handle-exceptions.md).

## See also

- [Improve performance](improve-performance.md): `deepcopy` and substep options that often matter more than the backend.
- [Run on a Ray cluster](run-on-a-ray-cluster.md): distributed execution.
- [Architecture & execution flow](../explanation/architecture.md): how the engine dispatches work to backends.
