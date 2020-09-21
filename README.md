# radCAD
A cadCAD implementation in Rust, using PyO3 to generate Rust bindings for Python to be used as a native Python module. The performance and expressiveness of Rust, with the utility of the Python data-science stack.

## Development

```bash
make release
# or
make release-macos
```

```python
import output.rad_cad as rc

TIMESTEPS = 100_000
RUNS = 1

data = rc.run(TIMESTEPS, RUNS, states, psubs, params)
df = pd.DataFrame(data)
```

## Features

* [x] Parameter sweeps
* [x] Monte Carlo runs
* [x] cadCAD compatibility
* [x] cadCAD simulation data structure

## Benchmark

See `notebook.ipynb`

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

### cadCAD
```bash
Execution Mode: multi_proc
Configuration Count: 1
Dimensions of the first simulation: (Timesteps, Params, Runs, Vars) = (100000, 2, 3, 7)
Execution Method: parallelize_simulations
Execution Mode: parallelized
Total execution time: 17.63s
17.644710063934326
```

### radCAD

```bash
4.089609861373901 seconds
```
