# Build your first model

In this tutorial you'll model a population that grows over time, run it as a simulation, sweep a parameter, and plot the results. By the end you'll understand the five building blocks every radCAD model is made of.

We'll model **logistic growth**, a population that grows quickly when small but slows as it approaches a *carrying capacity* `K`:

$$
\frac{dP}{dt} = r \cdot P \cdot \left(1 - \frac{P}{K}\right)
$$

You don't need to follow the maths; we'll translate it into code one piece at a time.

## Prerequisites

Make sure radCAD is [installed](installation.md). We'll also use `pandas` (installed with radCAD) and `matplotlib` for plotting:

```bash
pip install matplotlib
```

## Step 1: Define the State Variables

**State Variables** describe what the system looks like at a point in time. Our system has one: the `population`. The initial state is a dictionary mapping each variable to its starting value.

```python
initial_state = {
    "population": 10.0,
}
```

## Step 2: Define the System Parameters

**System Parameters** are the knobs of your model: values the rules depend on but that don't themselves change during a run. Ours are the growth rate `r` and the carrying capacity `K`.

In radCAD, each parameter is written as a **list**. A single-element list is a constant; a multi-element list defines a [parameter sweep](../how-to/parameter-sweeps.md) (used in Step 6).

```python
params = {
    "r": [0.1],     # growth rate
    "K": [1000.0],  # carrying capacity
}
```

## Step 3: Write a Policy Function

**Policy Functions** decide *what should happen* this timestep without changing state directly. They read the current state and parameters and return a dictionary of **signals**.

Our policy computes the change in population for this timestep:

```python
def p_growth(params, substep, state_history, previous_state):
    population = previous_state["population"]
    growth = params["r"] * population * (1 - population / params["K"])
    return {"growth": growth}
```

Every Policy Function receives the same four arguments: `params`, `substep`, `state_history`, and `previous_state`.

## Step 4: Write a State Update Function

**State Update Functions** apply the signals to actually update a single State Variable. They return a `(variable_name, new_value)` tuple.

```python
def s_population(params, substep, state_history, previous_state, policy_input):
    new_population = previous_state["population"] + policy_input["growth"]
    return "population", new_population
```

State Update Functions receive the same four arguments as policies, plus `policy_input`, the aggregated signals from the policies in this block.

## Step 5: Assemble the State Update Blocks

A **Partial State Update Block (PSUB)** wires policies and state updates together. Each block represents one substep within a timestep. Ours has a single block:

```python
state_update_blocks = [
    {
        "policies": {
            "growth": p_growth,
        },
        "variables": {
            "population": s_population,
        },
    },
]
```

## Step 6: Create the Model and run a Simulation

Now bundle everything into a [`Model`](../reference/api.md#radcad.wrappers.Model), wrap it in a [`Simulation`](../reference/api.md#radcad.wrappers.Simulation), and run it:

```python
import pandas as pd
from radcad import Model, Simulation

model = Model(
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
    params=params,
)

simulation = Simulation(model=model, timesteps=100, runs=1)

result = simulation.run()        # a list of state dictionaries
df = pd.DataFrame(result)        # load into a pandas DataFrame
print(df.tail())
```

You'll see the `population` column climbing toward the carrying capacity of `1000`, alongside bookkeeping columns radCAD adds automatically: `simulation`, `subset`, `run`, `substep`, and `timestep` (see [Model structure & data](../reference/data-structures.md)).

## Step 7: Sweep a parameter

What happens at different growth rates? Change the `r` parameter from one value to a list of values, and radCAD automatically runs one **subset** per value:

```python
params = {
    "r": [0.05, 0.1, 0.2],   # three subsets in a parameter sweep
    "K": [1000.0],
}

model.params = params
result = simulation.run()
df = pd.DataFrame(result)

# Each subset is identified by the `subset` column
print(df.groupby("subset")["population"].max())
```

## Step 8: Plot the results

```python
import matplotlib.pyplot as plt

for subset, group in df.groupby("subset"):
    plt.plot(group["timestep"], group["population"], label=f"subset {subset}")

plt.xlabel("timestep")
plt.ylabel("population")
plt.legend()
plt.show()
```

You should see three S-shaped logistic curves, each approaching `K = 1000` at a different speed.

## What you learned

You built a complete radCAD model from its five building blocks:

| Building block | Role |
| --- | --- |
| **State Variables** | What the system looks like (`initial_state`) |
| **System Parameters** | The model's knobs (`params`) |
| **Policy Functions** | Decide what happens (return signals) |
| **State Update Functions** | Apply changes to State Variables |
| **Partial State Update Blocks** | Wire policies and updates into substeps |

## Next steps

- Run the same model many times with randomness using a [Monte Carlo simulation](../how-to/monte-carlo.md).
- Compare two model variants with an [A/B test](../how-to/ab-testing.md).
- Speed up large runs by [choosing a backend](../how-to/choose-a-backend.md) and [improving performance](../how-to/improve-performance.md).
- Understand why models are structured this way in [Dynamical systems & the GDS model](../explanation/dynamical-systems.md).
