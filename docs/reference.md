# Reference

This part of the project documentation focuses on
an **information-oriented** approach. Use it as a
reference for the technical implementation of the
`radcad` project code.


## Table of Contents

 - [Development](#development-subsection) 
 - [Set up environment with Poetry](#set-up-environment-with-poetry)
 - [cadCAD Compatibility](#cadcad-compatibility)
 - [Migrating from cadCAD to radCAD](#migrating-from-cadcad-to-radcad)


---

## Development subsection

### Set up environment with Poetry

Suggested dependency management and packaging [Poetry](https://python-poetry.org/)

Set up and enter the Python environment with Poetry:
```bash
poetry --help
poetry install
poetry env use python3
poetry shell
```
Requires [>= Python 3.8](https://www.python.org/downloads/) 


### Jupyter Notebooks with Poetry

```bash
# Install kernel
poetry run python -m ipykernel install --user --name python3-radcad
# Start Jupyter
poetry run python -m jupyter lab
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

By default `radCAD` uses the `multiprocessing` library and sets the number of parallel processes used by the `Engine` to the number of system CPUs less one, but this can be customized as follows:
```python
from radcad import Engine

...

experiment.engine = Engine(processes=1)
result = experiment.run()
```

Alternatively, select the `SINGLE_PROCESS` Backend option which doesn't use any parallelisation library:
```python
from radcad import Engine, Backend

...

experiment.engine = Engine(backend=Backend.SINGLE_PROCESS)
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
