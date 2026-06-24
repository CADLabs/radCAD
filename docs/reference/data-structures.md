# Model structure & data

This page describes the data structures a radCAD model is built from, and the shape of the results a run produces. The class hierarchy is:

```
Model  >  Simulation  >  Experiment  >  Engine
```

A system is described as a **Model**; a Model is run for a number of timesteps/runs by a **Simulation**; one or more Simulations are grouped into an **Experiment**; and an Experiment or Simulation is executed by the **Engine**.

## The function signatures

radCAD models are built from two kinds of function, each with a fixed signature.

**Policy Function** decides what happens, returns a dict of signals:

```python
def policy(params, substep, state_history, previous_state) -> dict:
    return {"signal_key": value}
```

**State Update Function** applies signals, returns a `(variable, value)` tuple:

```python
def state_update(params, substep, state_history, previous_state, policy_input) -> tuple:
    return "variable_name", new_value
```

| Argument | Meaning |
| --- | --- |
| `params` | The current System Parameters (one subset). |
| `substep` | The current substep index. |
| `state_history` | The full results so far: a list of timesteps, each a list of substep states. |
| `previous_state` | The state at the end of the previous substep/timestep. |
| `policy_input` | (State Update Functions only) the aggregated Policy Signals for this block. |

!!! note "Signal aggregation"
    When multiple policies in a block return the same signal key, their values are **summed**. A State Update Function must return the same variable name it is registered under, and that name must exist in the initial state, otherwise radCAD raises a `KeyError`.

## Partial State Update Blocks (PSUBs)

`state_update_blocks` is an ordered list of blocks. Each block is one **substep** and has two keys:

```python
state_update_blocks = [
    {
        "policies": {
            "p_1": policy_one,
            "p_2": policy_two,
        },
        "variables": {
            "a": update_a,
            "b": update_b,
        },
    },
    # ... further blocks run as subsequent substeps
]
```

Within a timestep, blocks execute in order; within a block, policies run first (and are aggregated), then each variable's State Update Function runs.

## System Parameters

Parameters are either a **dict of lists** or a **(nested) dataclass**:

```python
params = {"a": [1, 2, 3], "b": [1]}   # lists define a sweep (read positionally)
```

See [Run a parameter sweep](../how-to/parameter-sweeps.md) and [Use dataclass parameters](../how-to/use-dataclass-parameters.md).

## The results

`Simulation.run()` and `Experiment.run()` return a **flat list of state dictionaries**, one per substep, ready for `pandas.DataFrame(...)`. radCAD adds five bookkeeping columns to every state:

| Column | Meaning |
| --- | --- |
| `simulation` | Index of the simulation (0-based), distinguishes A/B variants. |
| `subset` | Index of the parameter-sweep subset (0-based). |
| `run` | Monte Carlo run number (**1-based**, for cadCAD compatibility). |
| `substep` | Substep index within the timestep (`0` is the initial/carry-over state). |
| `timestep` | Timestep number. |

```python
import pandas as pd
df = pd.DataFrame(result)
#         a    b  simulation  subset  run  substep  timestep
# 0  1.0000  2.0           0       0    1        0         0
# 1  0.5403  2.0           0       0    1        1         1
# ...
```

The raw, un-flattened form (`SimulationResults`) is a list of timesteps, each a list of substep state dicts. This is what your functions see as `state_history`.

## Type aliases

radCAD names these shapes in [`radcad.types`](api.md#radcadtypes) so you can annotate your models:
`StateVariables`, `SystemParameters`, `StateUpdateBlock`, `PolicySignal`, `StateUpdate`, `StateUpdateResult`, and `SimulationResults`.
