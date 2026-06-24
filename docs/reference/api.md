# API reference

Auto-generated from the radCAD source docstrings.

## `radcad.wrappers`

The user-facing modelling classes: `Model`, `Simulation`, and `Experiment`.

::: radcad.wrappers
    options:
      members:
        - Model
        - Simulation
        - Experiment
        - Executable

## `radcad.engine`

The execution engine.

::: radcad.engine
    options:
      members:
        - Engine

## `radcad.backends`

Parallel-processing backends.

::: radcad.backends
    options:
      members:
        - Backend
        - Executor

## `radcad.core`

The core simulation loop. Most users never use this directly, but it defines radCAD's execution semantics.

::: radcad.core
    options:
      members:
        - SimulationExecution
        - SimulationExecutionSpecification
        - multiprocess_wrapper

## `radcad.types`

Type aliases describing radCAD's core data structures.

::: radcad.types

## `radcad.utils`

Helpers for parameter sweeps, common State Update Functions, and dataclass parameters.

::: radcad.utils
    options:
      members:
        - update_from_signal
        - accumulate_from_signal
        - update_timestamp
        - generate_parameter_sweep
        - generate_cartesian_product_parameter_sweep
        - default
        - flatten
        - extend_list
        - extract_exceptions
        - local_variables
