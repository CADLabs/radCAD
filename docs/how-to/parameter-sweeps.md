# Run a parameter sweep

A parameter sweep runs your model once per combination of parameter values, so you can compare outcomes across the parameter space. Each combination is called a **subset**.

## Define swept parameters

Every System Parameter is a list. radCAD reads across the lists *by position* to build subsets. It does **not** take the full Cartesian product.

```python
params = {
    "a": [1, 2, 3],
    "b": [1, 2],
    "c": [1],
}
```

The sweep length is the longest list (here `3`). Shorter lists are extended by repeating their last value, producing:

```python
[
    {"a": 1, "b": 1, "c": 1},
    {"a": 2, "b": 2, "c": 1},
    {"a": 3, "b": 2, "c": 1},  # b and c repeat their last value
]
```

Pass the parameters to your model as usual:

```python
from radcad import Model, Simulation

model = Model(initial_state=initial_state,
              state_update_blocks=state_update_blocks,
              params=params)
result = Simulation(model=model, timesteps=100, runs=1).run()
```

## Identify subsets in the results

Each row of the results carries a `subset` column identifying which parameter combination produced it:

```python
import pandas as pd
df = pd.DataFrame(result)
for subset, group in df.groupby("subset"):
    ...
```

## Want a full Cartesian product?

Positional sweeps keep the number of runs manageable. If you genuinely want every combination, expand the grid yourself before passing it in:

```python
from radcad.utils import generate_cartesian_product_parameter_sweep

params = generate_cartesian_product_parameter_sweep({
    "a": [1, 2, 3],
    "b": [1, 2],
})
# params now contains every (a, b) combination, aligned positionally
```

## See also

- [Run a Monte Carlo simulation](monte-carlo.md) to repeat each subset with randomness.
- [Use dataclass parameters](use-dataclass-parameters.md) for typed, namespaced parameters that also sweep.
- [`generate_parameter_sweep`](../reference/api.md#radcad.utils.generate_parameter_sweep) in the API reference.
