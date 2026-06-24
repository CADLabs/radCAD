# Migrate from cadCAD

radCAD already uses the cadCAD generalised dynamical-systems model structure, so your existing state update blocks, policies, and state update functions work as-is. You have two migration paths: rewrite the configuration using radCAD's API, or keep your cadCAD configuration and use **compatibility mode**.

## Option 1: Rewrite using the radCAD API

radCAD replaces cadCAD's multi-step configuration (`config_sim`, `append_configs`, `ExecutionContext`, `Executor`, the global `configs` list) with three classes.

=== "cadCAD"

    ```python
    from cadCAD.configuration.utils import config_sim
    from cadCAD.configuration import Experiment
    from cadCAD.engine import ExecutionMode, ExecutionContext, Executor
    from cadCAD import configs

    del configs[:]  # clear any prior configs

    sim_config = config_sim({
        "N": 1,            # Monte Carlo runs
        "T": range(100),   # timesteps
        "M": system_params,
    })

    experiment.append_configs(
        initial_state=initial_state,
        partial_state_update_blocks=partial_state_update_blocks,
        sim_configs=sim_config,
    )

    exec_context = ExecutionContext()
    simulation = Executor(exec_context=exec_context, configs=configs)
    result, _tensor_field, _sessions = simulation.execute()

    df = pd.DataFrame(result)
    ```

=== "radCAD"

    ```python
    from radcad import Model, Simulation, Experiment

    model = Model(
        initial_state=initial_state,
        state_update_blocks=state_update_blocks,
        params=params,
    )
    simulation = Simulation(
        model=model,
        timesteps=100,   # Number of timesteps
        runs=1,          # Number of Monte Carlo runs
    )

    result = simulation.run()
    df = pd.DataFrame(result)
    ```

Note the rename: cadCAD's `partial_state_update_blocks` is `state_update_blocks` in radCAD.

## Option 2: Compatibility mode

Compatibility mode translates the cadCAD configuration and execution process into radCAD, so you can run an existing cadCAD model with minimal changes. It does not handle every cadCAD option, but works for most models.

**1. Install the `compat` extra:**

=== "pip"
    ```bash
    pip install -e ".[compat]"
    ```
=== "Poetry"
    ```bash
    poetry install -E compat
    ```
=== "uv"
    ```bash
    uv sync --extra compat
    ```

**2. Repoint your cadCAD imports** from `cadCAD.*` to `radcad.compat.cadCAD.*`:

```python
from radcad.compat.cadCAD.configuration import Experiment
from radcad.compat.cadCAD.engine import Executor, ExecutionMode, ExecutionContext
from radcad.compat.cadCAD.configuration.utils import config_sim
from radcad.compat.cadCAD import configs
```

Your existing cadCAD model now runs on radCAD.

## See also

- [radCAD and cadCAD](../explanation/radcad-and-cadcad.md): how the two relate and differ.
- [Model structure & data](../reference/data-structures.md): the shared data structures.
