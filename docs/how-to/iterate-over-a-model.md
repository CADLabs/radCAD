# Iterate over a model

A [`Model`](../reference/api.md#radcad.wrappers.Model) is iterable: each iteration advances the system by one timestep and yields the model with its updated `state`. This turns a model into a live, in-the-loop generator, useful for digital twins, gradient descent, streaming visualisations, or composing one model inside another (e.g. within a Policy Function).

## Step through a model

```python
from radcad import Model

model_generator = iter(Model(
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
    params=params,
))

timesteps = 100
results = []
for t in range(timesteps):
    model = next(model_generator)   # advance one timestep
    state = model.state             # read the current state
    results.append(state["a"])
```

## Live-update a Plotly figure

Because iteration hands control back to you each timestep, you can drive a live visualisation:

```python
import plotly.graph_objects as go

fig = go.FigureWidget()
fig.add_scatter()
fig.show()

model_generator = iter(Model(initial_state=initial_state,
                             state_update_blocks=state_update_blocks,
                             params=params))

results = []
for t in range(100):
    model = next(model_generator)
    results.append(model.state["a"])
    fig.data[0].y = results[:t]
```

## Configure execution options

Use the model's `__call__` to set engine-style options before iterating:

```python
model(raise_exceptions=False, deepcopy=True, drop_substeps=False)
_model = next(model)
```

After stepping, `model.state` holds the latest state and `model.substeps` holds the substeps of the most recent timestep.

## Limitations

- Iteration supports **single subsets only**: no parameter sweeps. Use one concrete parameter set.

## See also

- [`Model.__iter__`](../reference/api.md#radcad.wrappers.Model) and [`Model.__call__`](../reference/api.md#radcad.wrappers.Model) in the API reference.
- [Improve performance](improve-performance.md): the `deepcopy` and `drop_substeps` options also apply here.
