# Architecture & execution flow

This page traces how a declarative model description becomes a concrete result, and explains the role of each component.

## The class hierarchy

```
Model  >  Simulation  >  Experiment  >  Engine
```

- **[`Model`](../reference/api.md#radcad.wrappers.Model)**: *what* the system is: initial state, state update blocks, parameters.
- **[`Simulation`](../reference/api.md#radcad.wrappers.Simulation)**: *how long and how many times*: a model plus `timesteps` and `runs`.
- **[`Experiment`](../reference/api.md#radcad.wrappers.Experiment)**: a collection of simulations run together.
- **[`Engine`](../reference/api.md#radcad.engine.Engine)**: *how to execute*: backend, processes, deepcopy, exception handling.

`Simulation` and `Experiment` both inherit from `Executable`, which holds the shared `engine`, `results`, `exceptions`, and lifecycle hooks. This is why a lone `Simulation` can be run directly *or* grouped into an `Experiment`: both are things the `Engine` knows how to run.

## What happens when you call `run()`

1. **`Executable.run()`** delegates to `Engine._run(executable=self)`.
2. The engine fires the **`before_experiment`** hook and builds a **run generator** (`_run_stream`).
3. `_run_stream` walks the nested loops (for each *simulation*, each *run*, and each *parameter subset*), firing the `before_simulation`/`before_run`/`before_subset` hooks. It expands parameter sweeps via [`generate_parameter_sweep`](../reference/api.md#radcad.utils.generate_parameter_sweep) and **yields one deepcopied [`SimulationExecution`](../reference/api.md#radcad.core.SimulationExecution) per unit of work**. Deepcopying each unit is what makes them safe to run concurrently.
4. The engine selects a **backend executor** based on the chosen [`Backend`](../reference/api.md#radcad.backends.Backend) and calls `execute_runs()`.
5. The backend distributes each `SimulationExecution` to a worker, where [`multiprocess_wrapper`](../reference/api.md#radcad.core.multiprocess_wrapper) runs it (catching exceptions if `raise_exceptions=False`).
6. Results stream back, are flattened and split into `results` and `exceptions`, the **`after_experiment`** hook fires, and the flat results list is returned.

```
run() → Engine._run → _run_stream (yields SimulationExecutions)
                          │
                          ▼
                  Backend.execute_runs
                          │  (per worker process)
                          ▼
              multiprocess_wrapper → SimulationExecution.execute
```

## Inside a single execution

A [`SimulationExecution`](../reference/api.md#radcad.core.SimulationExecution) represents exactly one run of one parameter subset. Its loop is defined abstractly in `SimulationExecutionSpecification` as a sequence of hook methods:

```
execute → for each timestep: before_step → step → after_step
                  step → for each block (substep): substep
                       substep → execute_policies → update_state (per variable)
```

Separating the loop *structure* (`SimulationExecutionSpecification`) from the *behaviour* (`SimulationExecution`) is a deliberate design choice: it makes the execution semantics explicit and lets you override any step by subclassing, for example to change the [deepcopy method](state-mutation-and-performance.md) or instrument the loop.

## Why backends are pluggable

Each unit of work is independent and self-contained, so *how* the units are executed is orthogonal to *what* they compute. radCAD can therefore offer single-process, local-multiprocessing, and distributed (Ray) backends behind one interface ([`Executor.execute_runs`](../reference/api.md#radcad.backends.Executor)). See [Choose a backend](../how-to/choose-a-backend.md).

## See also

- [State mutation & performance](state-mutation-and-performance.md): why each unit is deepcopied.
- [Engine settings](../reference/engine-settings.md): the settings the engine exposes.
