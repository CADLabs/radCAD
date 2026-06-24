# Extend radCAD with hooks

Hooks let you run your own code at key points in the execution lifecycle without touching radCAD's core. Use them for logging, progress bars, setup/teardown, or persisting results. The hook API is stable, so it is the recommended extension point.

## Available hooks

Set any of these callables on a [`Simulation`](../reference/api.md#radcad.wrappers.Simulation) or [`Experiment`](../reference/api.md#radcad.wrappers.Experiment):

```python
experiment.before_experiment = lambda experiment: print(f"Before experiment with {len(experiment.simulations)} simulations")
experiment.after_experiment  = lambda experiment: print(f"After experiment with {len(experiment.simulations)} simulations")
experiment.before_simulation = lambda context: print(f"Before simulation {context.simulation}")
experiment.after_simulation  = lambda context: print(f"After simulation {context.simulation}")
experiment.before_run        = lambda context: print(f"Before run {context.run}")
experiment.after_run         = lambda context: print(f"After run {context.run}")
experiment.before_subset     = lambda context: print(f"Before subset {context.subset}")
experiment.after_subset      = lambda context: print(f"After subset {context.subset}")
```

The `*_experiment` hooks receive the experiment; the others receive a [`Context`](../reference/api.md#radcad.types.Context) object carrying `simulation`, `run`, `subset`, `timesteps`, `initial_state`, `parameters`, and `state_update_blocks`.

!!! note "Precedence"
    When both an `Experiment` and one of its `Simulation`s define the same hook, the **Experiment's** hook takes precedence.

See [`tests/test_hooks.py`](https://github.com/CADLabs/radCAD/blob/master/tests/test_hooks.py) for the exact firing order and expected behaviour.

## Example: save results to HDF5

A common use is persisting results once an experiment finishes:

```python
import datetime
import pandas as pd

def save_to_HDF5(experiment, store_file_name, store_key):
    now = datetime.datetime.now()
    store = pd.HDFStore(store_file_name)
    store.put(store_key, pd.DataFrame(experiment.results))
    store.get_storer(store_key).attrs.metadata = {"date": now.isoformat()}
    store.close()
    print(f"Saved results to {store_file_name} with key {store_key}")

experiment.after_experiment = lambda experiment: save_to_HDF5(
    experiment, "experiment_results.hdf5", "experiment_0"
)
```

!!! note "HDF5 support"
    The HDF5 hook requires the `tables` package and a local HDF5 library. If installation reports `Could not find a local HDF5 installation`, install HDF5 and set the `HDF5_DIR` environment variable to its location, or pass `--hdf5`.

## See also

- [Context in the API reference](../reference/api.md#radcad.types.Context).
- [Iterate over a model](iterate-over-a-model.md): a different extension pattern, stepping a model by hand.
