# radCAD
![PyPI](https://badge.fury.io/py/radcad.svg)
[![Build Status](https://github.com/cadCAD-edu/radCAD/actions/workflows/python.yml/badge.svg)](https://github.com/cadCAD-edu/radCAD/actions/workflows/python.yml)
[![Coverage Status](https://coveralls.io/repos/github/cadCAD-edu/radCAD/badge.svg?branch=master&service=github)](https://coveralls.io/github/cadCAD-edu/radCAD?branch=master&service=github)
[![Maintainability](https://api.codeclimate.com/v1/badges/a65a6fb94f052cd804c2/maintainability)](https://codeclimate.com/github/cadCAD-edu/radCAD/maintainability)

![Gosper Glider Gun](https://github.com/cadCAD-edu/radCAD/blob/master/examples/game_of_life/gosper-glider-gun.gif)

A Python framework for modelling and simulating [dynamical systems](https://en.wikipedia.org/wiki/Dynamical_system). Models are structured using state transitions for encoding differential equations, or any other logic, as an example. Simulations are configured using methods such as parameter sweeps, Monte Carlo runs, and A/B testing. See [cadCAD.education](https://cadcad.education) for the most comprehensive cadCAD beginner course.

radCAD extends on [cadCAD](https://github.com/cadCAD-org/cadCAD).

Goals:
* simple API for ease of use
* performance driven (more speed = more experiments, larger parameter sweeps, in less time)
* cadCAD compatible (standard functions, data structures, and simulation results)
* maintainable, testable codebase

## Table of Contents

* [Example Models](#example-models)
* [Features](#features)
* [Advanced Features](#advanced-features)
* [Installation](#installation)
* [Documentation](#documentation)
* [Development](#development)
* [Testing](#testing)
* [Jupyter Notebooks](#jupyter-notebooks)
* [Benchmarking](#benchmarking)

## Example Models

### Iterable Models

Using Models as live in-the-loop digital twins, creating your own model pipelines, and streaming simulation results to update a visualization. That's what an iterable Model class enables.

![Iterable Models](https://github.com/cadCAD-edu/radCAD/blob/master/examples/iterable_models/iterable-models.gif)

### [Game of Life](https://www.conwaylife.com/)

[Live radCAD demo model on Streamlit](https://share.streamlit.io/benschza/radcad/examples/streamlit/game_of_life/app.py)

A simple game where at each timestep, the following transitions occur:

1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
2. Any live cell with two or three live neighbours lives on to the next generation.
3. Any live cell with more than three live neighbours dies, as if by overpopulation.
4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

See [examples/game_of_life/game-of-life.ipynb](examples/game-of-life/game-of-life.ipynb)

![Game of Life](https://github.com/cadCAD-edu/radCAD/blob/master/examples/game_of_life/game-of-life.gif)

### [Predator-Prey](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations)

A simple model that applies the two Lotka-Volterra differential equations, frequently used to describe the dynamics of biological systems in which two species interact:

Original models thanks to [Danilo @danlessa](https://github.com/danlessa/)!
* System dynamics model: [examples/predator_prey_sd/predator-prey-sd.ipynb](examples/predator_prey_sd/predator-prey-sd.ipynb)
* Agent based model: [examples/predator_prey_abm/predator-prey-abm.ipynb](examples/predator_prey_abm/predator-prey-abm.ipynb)

## Features

* [x] Parameter sweeps

```python
params = {
    'a': [1, 2, 3],
    'b': [1, 2],
    'c': [1]
}
# Creates a parameter sweep of:
# [{'a': 1, 'b': 1, 'c': 1}, {'a': 2, 'b': 2, 'c': 1}, {'a': 3, 'b': 2, 'c': 1}]
```

* [x] Monte Carlo runs

```python
RUNS = 100 # Set to the number of Monte Carlo Runs
Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
```

* [x] A/B tests

```python
model_a = Model(initial_state=states_a, state_update_blocks=state_update_blocks_a, params=params_a)
model_b = Model(initial_state=states_b, state_update_blocks=state_update_blocks_b, params=params_b)

simulation_1 = Simulation(model=model_a, timesteps=TIMESTEPS, runs=RUNS)
simulation_2 = Simulation(model=model_b, timesteps=TIMESTEPS, runs=RUNS)

# Simulate any number of models in parallel
experiment = Experiment([simulation_1, simulation_2])
result = experiment.run()
```

* [x] cadCAD compatibility and familiar data structure

```bash
               a          b  simulation  subset  run  substep  timestep
0       1.000000        2.0           0       0    1        0         0
1       0.540302        2.0           0       0    1        1         1
2       0.540302        7.0           0       0    1        2         1
3       0.463338        7.0           0       0    1        1         2
4       0.463338       12.0           0       0    1        2         2
...          ...        ...         ...     ...  ...      ...       ...
799999  0.003162   999982.0           1       1    1        2     99998
800000  0.003162   999982.0           1       1    1        1     99999
800001  0.003162   999992.0           1       1    1        2     99999
800002  0.003162   999992.0           1       1    1        1    100000
800003  0.003162  1000002.0           1       1    1        2    100000
```

## Advanced Features

* [x] Disable `deepcopy` option for improved performance (at cost of mutability)
* [x] Robust exception handling with partial results, and tracebacks
* [x] Parallel processing with multiple backend options: `multiprocessing`, `pathos`, `ray`
* [x] Distributed computing and remote execution in a cluster (AWS, GCP, Kubernetes, ...) using [Ray - Fast and Simple Distributed Computing](https://ray.io/)
* [x] Hooks to easily extend the functionality - e.g. save results to HDF5 file format after completion
* [x] Model classes are iterable, so you can iterate over them step-by-step from one state to the next (useful for gradient descent, live digital twins)

## Installation

```bash
pip install radcad
```

## Documentation

`radCAD` provides the following classes:
1. A system is represented in some form as a `Model`
2. A `Model` can be simulated using a `Simulation`
3. An `Experiment` consists of one or more `Simulation`s
4. An `Experiment` or a `Simulation` is run by the `Engine`

So, the hierarchy is as follows `Model` > `Simulation` > `Experiment` > `Engine`.

```python
from radcad import Model, Simulation, Experiment

model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
simulation = Simulation(model=model, timesteps=100_000, runs=1)

result = simulation.run()
# Or, multiple simulations:
# experiment = Experiment([simulation_1, simulation_2, simulation_3])
# result = experiment.run()

df = pd.DataFrame(result)
```

### cadCAD Compatibility

#### Migrating from cadCAD to radCAD

##### cadCAD
```python
# cadCAD configuration modules
from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment

# cadCAD simulation engine modules
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

# cadCAD global simulation configuration list
from cadCAD import configs

# Clears any prior configs
del configs[:]

sim_config = config_sim({
    'N': 1, # Number of Monte Carlo Runs
    'T': range(100), # Number of timesteps
    'M': system_params # System Parameters
})

experiment.append_configs(
    # Model initial state
    initial_state=initial_state,
    # Model Partial State Update Blocks
    partial_state_update_blocks=partial_state_update_blocks,
    # Simulation configuration
    sim_configs=sim_config
)

# ExecutionContext instance (used for more advanced cadCAD config)
exec_context = ExecutionContext()

# Creates a simulation Executor instance
simulation = Executor(
    exec_context=exec_context,
    # cadCAD configuration list
    configs=configs
)

# Executes the simulation, and returns the raw results
result, _tensor_field, _sessions = simulation.execute()

df = pd.DataFrame(result)
```

##### radCAD
```python
from radcad import Model, Simulation, Experiment

model = Model(
    # Model initial state
    initial_state=initial_state,
    # Model Partial State Update Blocks
    state_update_blocks=state_update_blocks,
    # System Parameters
    params=params
)

simulation = Simulation(
    model=model,
    timesteps=100_000,  # Number of timesteps
    runs=1  # Number of Monte Carlo Runs
)

# Executes the simulation, and returns the raw results
result = simulation.run()

df = pd.DataFrame(result)
```

#### cadCAD Compatibility Mode
radCAD is already compatible with the cadCAD generalized dynamical systems model structure; existing state update blocks, policies, and state update functions should work as is. But to more easily refactor existing cadCAD models to use radCAD without changing the cadCAD API and configuration process, there is a compatibility mode. The compatibility mode doesn't guarrantee to handle all cadCAD options, but should work for most cadCAD models by translating the configuration and execution processes into radCAD behind the scenes.

To use the compatibility mode, install radCAD with the `compat` dependencies:

```bash
pip install -e .[compat]
# Or
poetry install -E compat
```

Then, update the cadCAD imports from `cadCAD._` to `radcad.compat.cadCAD._`

```python
from radcad.compat.cadCAD.configuration import Experiment
from radcad.compat.cadCAD.engine import Executor, ExecutionMode, ExecutionContext
from radcad.compat.cadCAD.configuration.utils import config_sim
from radcad.compat.cadCAD import configs
```

Now run your existing cadCAD model using radCAD!

### Iterating over a Model

Model classes are iterable, so you can iterate over them step-by-step from one state to the next.

This is useful for gradient descent, live digital twins, composing one model within another within a Policy Function...

Here is an example of using a Model to update a Plotly figure live:

```python
from radcad import Model

import time
import plotly.graph_objects as go

# Live update of figure using Model as a generator
fig = go.FigureWidget()
fig.add_scatter()
fig.show()

# Create a generator from the Model iterator
model_generator = iter(Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params))

timesteps = 100
results = []

for t in range(timesteps):
    # Step to next state
    model = next(model_generator)
    # Get state and update figure
    state = model.state
    a = state['a']
    results.append(a)
    fig.data[0].y = results[:t]
```

You have access to the more advanced engine options too, using the `__call__()` method:

```python
model(raise_exceptions=False, deepcopy=True, drop_substeps=False)
_model = next(model)
```

Current limitations:
* Only works for single subsets (no parameter sweeps)

### Engine Settings

#### Selecting single or multi-process modes

By default `radCAD` sets the number of parallel processes used by the `Engine` to the number of system CPUs less one, but this can be customized as follows:
```python
from radcad import Engine

...

experiment.engine = Engine(processes=1)
result = experiment.run()
```

#### Disabling state `deepcopy`

To improve performance, at the cost of mutability, the `Engine` module has the `deepcopy` option which is `True` by default:

```python
experiment.engine = Engine(deepcopy=False)
```

#### Dropping state substeps

If you don't need the substeps in post-processing, you can both improve simulation performance and save post-processing time and dataset size by dropping the substeps:

```python
experiment.engine = Engine(drop_substeps=True)
```

#### Exception handling

radCAD allows you to choose whether to raise exceptions, ending the simulation, or to continue with the remaining runs and return the results along with the exceptions. Failed runs are returned as partial results - the part of the simulation result up until the timestep where the simulation failed.

```python
...
experiment.engine = Engine(raise_exceptions=False)
experiment.run()

results = experiment.results # e.g. [[{...}, {...}], ..., [{...}, {...}]]
exceptions = experiment.exceptions # A dataframe of exceptions, tracebacks, and simulations metadata
```

This also means you can run a specific simulation directly, and access the results later:
```python
predator_prey_simulation.run()

...

results = predator_prey_simulation.results
```

### WIP: Remote Cluster Execution (using Ray)

To use the Ray backend, install radCAD with the `extension-backend-ray` dependencies:

```bash
pip install -e .[extension-backend-ray]
# Or
poetry install -E extension-backend-ray
```

Export the following AWS credentials (or see Ray documentation for alternative providers):
```bash
BACKEND=AWS
AWS_ACCESS_KEY_ID=***
AWS_SECRET_ACCESS_KEY=***
```

Start a new cluster (or use existing):
```bash
# Cluster config: single m5.large EC2 instance, us-west-2 region
ray up cluster/aws/minimal.yaml
# Test the connection
ray exec cluster/aws/minimal.yaml 'echo "hello world"'
```

Change the execution backend to `RAY_REMOTE`:
```python
from radcad.engine import Engine, Backend
import ray

# Connect to cluster head
ray.init(address='***:6379', _redis_password='***')

...

experiment.engine = Engine(backend=Backend.RAY_REMOTE)
result = experiment.run()
```

Finally, spin down the cluster:
```bash
ray down cluster/ray-aws.yaml
```

### Hooks to extend functionality

Hooks allow you to easily extend the functionality of radCAD with a stable API, and without having to manipulate the robust core.

```python
experiment.before_experiment = lambda experiment: print(f"Before experiment with {len(experiment.simulations)} simulations")
experiment.after_experiment = lambda experiment: print(f"After experiment with {len(experiment.simulations)} simulations")
experiment.before_simulation = lambda simulation: print(f"Before simulation {simulation.index} with params {simulation.model.params}")
experiment.after_simulation = lambda simulation: print(f"After simulation {simulation.index} with params {simulation.model.params}")
experiment.before_run = lambda context: print(f"Before run {context}")
experiment.after_run = lambda context: print(f"After run {context}")
experiment.before_subset = lambda context: print(f"Before subset {context}")
experiment.after_subset = lambda context: print(f"After subset {context}")
```

See [tests/test_hooks.py](tests/test_hooks.py) for expected functionality.

#### Example hook: Saving results to HDF5

```python
import pandas as pd
import datetime

def save_to_HDF5(experiment, store_file_name, store_key):
    now = datetime.datetime.now()
    store = pd.HDFStore(store_file_name)
    store.put(store_key, pd.DataFrame(experiment.results))
    store.get_storer(store_key).attrs.metadata = {
        'date': now.isoformat()
    }
    store.close()
    print(f"Saved experiment results to HDF5 store file {store_file_name} with key {store_key}")

experiment.after_experiment = lambda experiment: save_to_HDF5(experiment, 'experiment_results.hdf5', 'experiment_0')
```

### Notes on state mutation

The biggest performance bottleneck with radCAD, and cadCAD for that matter, is avoiding mutation of state variables by creating a deep copy of the state passed to the state update function. This avoids the state update function mutating state variables outside of the framework by creating a copy of it first -  a deep copy creates a copy of the object itself, and the key value pairs, which gets expensive.

To avoid the additional overhead, mutation of state history is allowed, and left up to the developer to avoid using standard Python best practises, but mutation of the current state is disabled.

See https://stackoverflow.com/questions/24756712/deepcopy-is-extremely-slow for some performance benchmarks of different methods. radCAD uses `cPickle`, which is faster than using `deepcopy`, but less flexible about what types it can handle (Pickle depends on serialization) - these could be interchanged in future.

## Development

Set up and enter the Python environment with [Poetry](https://python-poetry.org/):
```bash
poetry --help
poetry install
poetry env use python3
poetry shell
```

### Publishing to PyPI

```bash
# 1. Update `pyproject.toml` package version using semantic versioning
# 2. Update CHANGELOG.md
# 3. Submit PR and run tests
# 4. Merge into master on success
# 5. Build and publish package
poetry publish --build
# Enter in PyPI package repository credentials
# 6. Tag master commit with version e.g. `v0.5.0` and push
```

### Pip or alternative package managers

Export `requirements.txt` using Poetry:
```bash
poetry export --without-hashes -f requirements.txt --output requirements.txt
```

Note: the root `requirements.txt` is used for Streamlit app in examples, and is not for development.

## Testing

```bash
poetry shell
python3 -m pytest
python3 -m unittest
```

## Jupyter Notebooks

```bash
# Install kernel
poetry run python -m ipykernel install --user --name python3-radcad
# Start Jupyter
poetry run python -m jupyter lab
```

## Benchmarking

See [benchmarks](benchmarks/)

### Time Profiling

```bash
poetry run python3 -m pytest run benchmarks/benchmark_radcad.py
poetry run python3 -m pytest run benchmarks/benchmark_single_process.py
```

### Memory Profiling

```bash
poetry run python3 -m mprof run benchmarks/benchmark_memory_radcad.py
poetry run python3 -m mprof plot
```
