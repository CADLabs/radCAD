# Run an A/B test

To compare two (or more) model variants (different rules, parameters, or initial states), wrap each in its own [`Simulation`](../reference/api.md#radcad.wrappers.Simulation) and run them together inside an [`Experiment`](../reference/api.md#radcad.wrappers.Experiment). radCAD executes all simulations in parallel and returns their combined results.

## Build the experiment

```python
from radcad import Model, Simulation, Experiment

model_a = Model(initial_state=states_a,
                state_update_blocks=state_update_blocks_a,
                params=params_a)
model_b = Model(initial_state=states_b,
                state_update_blocks=state_update_blocks_b,
                params=params_b)

simulation_1 = Simulation(model=model_a, timesteps=TIMESTEPS, runs=RUNS)
simulation_2 = Simulation(model=model_b, timesteps=TIMESTEPS, runs=RUNS)

# Simulate any number of models together
experiment = Experiment([simulation_1, simulation_2])
result = experiment.run()
```

## Tell the variants apart

Each simulation is assigned an index, surfaced as the `simulation` column in the results. Use it to separate the variants:

```python
import pandas as pd

df = pd.DataFrame(result)
variant_a = df[df["simulation"] == 0]
variant_b = df[df["simulation"] == 1]
```

## Managing simulations in an experiment

The [`Experiment`](../reference/api.md#radcad.wrappers.Experiment) class lets you build the set of simulations incrementally:

```python
experiment = Experiment()
experiment.add_simulations([simulation_1, simulation_2])
experiment.add_simulations(simulation_3)   # also accepts a single simulation

experiment.get_simulations()   # -> list of simulations
experiment.clear_simulations() # -> removes them all
```

## See also

- [Run a Monte Carlo simulation](monte-carlo.md): set `runs` to repeat each variant.
- [Extend radCAD with hooks](use-hooks.md): run setup/teardown logic per simulation.
