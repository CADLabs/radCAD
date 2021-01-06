# radCAD
![PyPI](https://badge.fury.io/py/radcad.svg)
[![Build Status](https://travis-ci.com/BenSchZA/radCAD.svg?branch=master)](https://travis-ci.com/BenSchZA/radCAD)
[![Coverage Status](https://coveralls.io/repos/github/BenSchZA/radCAD/badge.svg?branch=master)](https://coveralls.io/github/BenSchZA/radCAD?branch=master)

A Python framework for modelling and simulating [dynamical systems](https://en.wikipedia.org/wiki/Dynamical_system). Models are structured using state transitions for encoding differential equations, or any other logic, as an example. Simulations are configured using methods such as parameter sweeps, Monte Carlo runs, and A/B testing. See [cadCAD.education](https://cadcad.education) for the most comprehensive cadCAD beginner course.

radCAD extends on [cadCAD](https://github.com/cadCAD-org/cadCAD). It uses Rust for the core, using PyO3 to generate Rust bindings for Python to be used as a native Python module - the performance and expressiveness of Rust, with the utility of the Python data-science stack.

Goals:
* simple API for ease of use
* performance driven (more speed = more experiments, larger parameter sweeps, in less time)
* cadCAD compatible (standard functions, data structures, and simulation results)
* maintainable, testable codebase

## Example Models

### [Game of Life](https://www.conwaylife.com/)

A simple game where at each timestep, the following transitions occur:

1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
2. Any live cell with two or three live neighbours lives on to the next generation.
3. Any live cell with more than three live neighbours dies, as if by overpopulation.
4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

See [examples/game-of-life/game-of-life.ipynb](examples/game-of-life/game-of-life.ipynb)

![Game of Life](https://github.com/BenSchZA/radCAD/blob/master/examples/game-of-life/game-of-life.gif)
![Gosper Glider Gun](https://github.com/BenSchZA/radCAD/blob/master/examples/game-of-life/gosper-glider-gun.gif)

### [Predator-Prey](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations)

A simple model that applies the two Lotka-Volterra differential equations, frequently used to describe the dynamics of biological systems in which two species interact:

See [examples/predator-prey.ipynb](examples/predator-prey.ipynb)

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

* [x] Parallel processing with multiple backend options: `multiprocessing`, `pathos`, `ray`
* [x] Distributed computing and remote execution in a cluster (AWS, GCP, Kubernetes, ...) using [Ray - Fast and Simple Distributed Computing](https://ray.io/)
* [x] (WIP) Hooks to easily extend the functionality

```python
experiment.before_experiment = lambda engine=None: print(f"Before experiment with {len(engine.experiment.simulations)} simulations")
experiment.after_experiment = lambda engine=None: print(f"After experiment with {len(engine.experiment.simulations)} simulations")
experiment.before_simulation = lambda simulation=None, simulation_index=-1: print(f"Before simulation {simulation_index} with params {simulation.model.params}")
experiment.after_simulation = lambda simulation=None, simulation_index=-1: print(f"After simulation {simulation_index} with params {simulation.model.params}")
experiment.before_run = lambda run_index=-1, simulation=None: print(f"Before run {run_index}")
experiment.after_run = lambda run_index=-1, simulation=None: print(f"After run {run_index}")
```

## Installation

```bash
pip install radcad
```

## Use

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

### Selecting single or multi-process modes

By default `radCAD` sets the number of parallel processes used by the `Engine` to the number of system CPUs less one, but this can be customized as follows:
```python
from radacad import Engine

...

experiment.engine = Engine(processes=1)
result = experiment.run()
```

### Remote Cluster Execution (using Ray)

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

## Development

Build the [Rust](https://www.rust-lang.org/) core using [Nix](https://nixos.org/):
```bash
cd core/
nix-shell
make setup
make release-linux # For Linux
make release-macos # For macOS
make release-windows # For Windows
```

Set up and enter the Python environment with [Poetry](https://python-poetry.org/):
```bash
poetry --help
poetry install
poetry env use python3
poetry shell
```

### Pip or alternative package managers

See `requirements.txt`.

Export `requirements.txt` using Poetry:
```bash
poetry export --without-hashes -f requirements.txt --output requirements.txt
```

## Testing

```bash
poetry shell
python3 -m pytest
python3 -m unittest
```

## Jupyter Notebooks

```bash
poetry run python -m ipykernel install --user --name python3-radcad
```

## Benchmarking

See `benchmarks/`. radCAD has approximately a 10x speed increase over cadCAD locally - results may vary. Using Ray, potentially much better performance utilizing remote parallel processing.
