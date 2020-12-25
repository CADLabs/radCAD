# radCAD
A [cadCAD](https://cadcad.org/) implementation in Rust, using PyO3 to generate Rust bindings for Python to be used as a native Python module. The performance and expressiveness of Rust, with the utility of the Python data-science stack.

See https://github.com/cadCAD-org/cadCAD

Goals:
* simple API for ease of use
* performance driven (more speed = more experiments, larger parameter sweeps, in less time)
* cadCAD compatible (standard functions, data structures, and simulation results)
* maintainable, testable codebase

```bash
radCAD took 11.190160989761353 seconds
cadCAD took 68.51003003120422 seconds
Simulation output dataframes are carbon copies
Rust is 6.122345343725507X faster than Python
```

## Features

* [x] Parameter sweeps

```python
params = {
    'a': [1, 2, 3],
    'b': [1]
}
```

* [x] Monte Carlo runs

```python
RUNS = 100 # Set to the number of Monte Carlo Runs
Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
```

* [x] A/B tests

```python
model_a = Model(initial_state=states_a, psubs=psubs_a, params=params_a)
model_b = Model(initial_state=states_b, psubs=psubs_b, params=params_b)

simulation_1 = Simulation(model=model_a, timesteps=TIMESTEPS, runs=RUNS)
simulation_2 = Simulation(model=model_b, timesteps=TIMESTEPS, runs=RUNS)

# Simulate any number of models in parallel
data = run([simulation_1, simulation_2])
```

* [x] Multiple backends: 

* [x] cadCAD compatibility
* [x] cadCAD simulation data structure

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

## Installation

```bash
pip install radcad
```

## Development

Build the [Rust](https://www.rust-lang.org/) core using [Nix](https://nixos.org/):
```bash
cd core/
nix-shell
make release
# or
make release-macos
```

Set up and enter the Python environment with [Poetry](https://python-poetry.org/):
```bash
poetry --help
poetry install
poetry env use python3
poetry shell
```

## Testing

```bash
poetry shell
python3 -m pytest
python3 -m unittest
```

## Use

```python
from radcad import Model, Simulation
from radcad.engine import run

model = Model(initial_state=initial_state, psubs=psubs, params=params)
simulation = Simulation(model=model, timesteps=100_000, runs=1)

result = run(simulation)
# Or, multiple simulations: run([simulation_1, simulation_2, simulation_3])

df = pd.DataFrame(result)
```

## Benchmarking

### 1. `100_000` timesteps, `5` runs, `5` benchmark rounds

```bash
python3 -m pytest tests/benchmark_test.py

platform darwin -- Python 3.8.5, pytest-6.0.2, py-1.9.0, pluggy-0.13.1
benchmark: 3.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /Users/_/workspace/radCAD
plugins: benchmark-3.2.3
collected 2 items

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
```

| Name (time in s) | Min | Max | Mean | StdDev | Median | IQR | Outliers | OPS | Rounds | Iterations |
| ---              | --- | --- | ---  | ---    | ---    | --- | ---      | --- | ---    | ---        |
| test_benchmark_radcad  |   11.6412 (1.0)   |   13.0923 (1.0)   |   12.4871 (1.0)   |   0.5904 (1.37)   |  12.7650 (1.0)    |  0.8761 (2.21)     |     2;0 | 0.0801 (1.0)      |     5     |      1 |
| test_benchmark_cadcad  |   57.3148 (4.92)  |   58.4830 (4.47)  |   58.0262 (4.65)  |   0.4324 (1.0)    |  58.0742 (4.55)   |  0.3960 (1.0)      |     2;0 | 0.0172 (0.22)     |     5     |      1 |

### 2. `100_000` timesteps, `5` A/B models

See `benchmarks/benchmark.py`

```python
import math

def policy(params, substep, state_history, previous_state):
    return {'step_size': 1}

def update_a(params, substep, state_history, previous_state, policy_input):
    a = b = c = d = e = 100.0
    return 'a', previous_state['a'] * abs(math.cos(previous_state['a']))

def update_b(params, substep, state_history, previous_state, policy_input):
    return 'b', previous_state['b'] + policy_input['step_size'] * params['a']

params = {
    'a': [1, 2, 3],
    'b': [1]
}

states = {
    'a': 1.0,
    'b': 2.0
}

psubs = [
    {
        'policies': {},
        'variables': {
            'a': update_a
        }
    },
    {
        'policies': {
            'p_1': policy,
            'p_2': policy,
            'p_3': policy,
            'p_4': policy,
            'p_5': policy,
        },
        'variables': {
            'b': update_b
        }
    }
]

TIMESTEPS = 100_000
RUNS = 1
```

```bash
11.190160989761353
                a          b  simulation  subset  run  substep  timestep
0        1.000000        2.0           0       0    1        0         0
1        0.540302        2.0           0       0    1        1         1
2        0.540302        7.0           0       0    1        2         1
3        0.463338        7.0           0       0    1        1         2
4        0.463338       12.0           0       0    1        2         2
...           ...        ...         ...     ...  ...      ...       ...
2000005  0.003162   999982.0           4       1    1        2     99998
2000006  0.003162   999982.0           4       1    1        1     99999
2000007  0.003162   999992.0           4       1    1        2     99999
2000008  0.003162   999992.0           4       1    1        1    100000
2000009  0.003162  1000002.0           4       1    1        2    100000

[2000010 rows x 7 columns]

                  ___________    ____
  ________ __ ___/ / ____/   |  / __ \
 / ___/ __` / __  / /   / /| | / / / /
/ /__/ /_/ / /_/ / /___/ ___ |/ /_/ /
\___/\__,_/\__,_/\____/_/  |_/_____/
by cadCAD

Execution Mode: local_proc
Configuration Count: 5
Dimensions of the first simulation: (Timesteps, Params, Runs, Vars) = (100000, 2, 2, 7)
Execution Method: local_simulations
SimIDs   : [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
SubsetIDs: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
Ns       : [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
ExpIDs   : [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
Execution Mode: parallelized
Total execution time: 68.48s
68.51003003120422
                a          b  simulation  subset  run  substep  timestep
0        1.000000        2.0           0       0    1        0         0
1        0.540302        2.0           0       0    1        1         1
2        0.540302        7.0           0       0    1        2         1
3        0.463338        7.0           0       0    1        1         2
4        0.463338       12.0           0       0    1        2         2
...           ...        ...         ...     ...  ...      ...       ...
2000005  0.003162   999982.0           4       1    2        2     99998
2000006  0.003162   999982.0           4       1    2        1     99999
2000007  0.003162   999992.0           4       1    2        2     99999
2000008  0.003162   999992.0           4       1    2        1    100000
2000009  0.003162  1000002.0           4       1    2        2    100000

[2000010 rows x 7 columns]

radCAD took 11.190160989761353 seconds
cadCAD took 68.51003003120422 seconds
Simulation output dataframes are carbon copies
Rust is 6.122345343725507X faster than Python
```
