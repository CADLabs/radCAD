# Handle exceptions

By default radCAD raises on the first error, ending the simulation. For long Monte Carlo ensembles or large sweeps, you often want the opposite: keep going, collect partial results, and inspect what failed afterwards.

## Continue on failure and collect partial results

Set `raise_exceptions=False` on the [`Engine`](../reference/api.md#radcad.engine.Engine):

```python
from radcad import Engine

experiment.engine = Engine(raise_exceptions=False)
experiment.run()

results = experiment.results       # e.g. [[{...}, {...}], ..., [{...}, {...}]]
exceptions = experiment.exceptions # DataFrame-friendly list of exception metadata
```

A failed run returns a **partial result**: the trajectory up to the timestep where it failed. Successful runs and the good portion of failed runs are preserved.

## Inspect the exceptions

Each entry in `experiment.exceptions` describes one run, including the exception, its traceback, and the run's metadata:

```python
import pandas as pd

errors = pd.DataFrame(experiment.exceptions)
print(errors[["simulation", "run", "subset", "exception"]])

# Full traceback for the first failure
print(errors.iloc[0]["traceback"])
```

The metadata fields are: `exception`, `traceback`, `simulation`, `run`, `subset`, `timesteps`, `parameters`, and `initial_state`. On a successful run, `exception` and `traceback` are `None`.

## Access results from a stored simulation

Results and exceptions are stored on the executable, so you can run a simulation and read its output later:

```python
predator_prey_simulation.run()
...
results = predator_prey_simulation.results
```

## Debugging tip

To get a clean, in-process traceback while developing, run on a single process so errors aren't marshalled across process boundaries:

```python
from radcad import Engine, Backend
experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)
```

See [Choose a processing backend](choose-a-backend.md).
