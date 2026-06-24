# Run a Monte Carlo simulation

A Monte Carlo simulation runs the same model many times. When your model contains randomness, each run produces a different trajectory, letting you study the distribution of outcomes rather than a single path.

## Set the number of runs

Set the `runs` argument on the [`Simulation`](../reference/api.md#radcad.wrappers.Simulation):

```python
from radcad import Simulation

RUNS = 100  # number of Monte Carlo runs

simulation = Simulation(model=model, timesteps=1000, runs=RUNS)
result = simulation.run()
```

Each run is identified by the `run` column in the results (numbered from `1` for cadCAD compatibility).

## Add randomness to your model

Randomness lives inside your Policy or State Update Functions. For example:

```python
import numpy as np

def p_shock(params, substep, state_history, previous_state):
    shock = np.random.normal(0, params["volatility"])
    return {"shock": shock}
```

!!! warning "Seeding across parallel processes"
    Runs are distributed across worker processes by the [backend](choose-a-backend.md). If you need reproducibility, seed your random number generator inside the model functions (e.g. keyed off `previous_state["run"]`), not once at import time: a single global seed is not shared across processes. See [Reproducibility in the test suite](https://github.com/CADLabs/radCAD/blob/master/tests/test_reproducibility.py) for patterns.

## Analyse the distribution

Group by `run` (and `timestep`) to summarise across the ensemble:

```python
import pandas as pd

df = pd.DataFrame(result)

# Distribution of a State Variable at the final timestep
final = df[df["timestep"] == df["timestep"].max()]
print(final["population"].describe())

# Mean trajectory across all runs
mean_trajectory = df.groupby("timestep")["population"].mean()
```

## Combine with a parameter sweep

Monte Carlo runs and [parameter sweeps](parameter-sweeps.md) compose: with `runs=100` and a 3-subset sweep, radCAD executes `100 × 3 = 300` runs. Group by both `run` and `subset` to analyse them.

## See also

- [Choose a processing backend](choose-a-backend.md) to parallelise large ensembles.
- [Handle exceptions](handle-exceptions.md) to keep partial results when a single run fails.
