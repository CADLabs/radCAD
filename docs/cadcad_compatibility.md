## cadCAD Compatibility

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