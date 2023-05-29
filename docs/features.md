# Features

---

## Table of Contents

 - [Main Features](#main-features)
 - [Advanced Features](#advanced-features)

---

## Main Features

To aid in parameter selection, system parametrization in radCAD supports simulation techniques like **parameter sweeps**, **Monte Carlo simulations** or **A/B tests** can be easily performed. 

For a user unfamiliar with these techniques, we suggest introduction to these methods in the context of cadCAD in Section 6 of [cadCAD Complete Foundations Bootcamp](https://www.cadcad.education/course/bootcamp). 

* Parameter sweeps

```python
params = {
    'a': [1, 2, 3],
    'b': [1, 2],
    'c': [1]
}
# Creates a parameter sweep of:
# [{'a': 1, 'b': 1, 'c': 1}, {'a': 2, 'b': 2, 'c': 1}, {'a': 3, 'b': 2, 'c': 1}]
```



* Monte Carlo runs

```python
RUNS = 100 # Set to the number of Monte Carlo Runs
Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
```

* A/B tests

```python
model_a = Model(initial_state=states_a, state_update_blocks=state_update_blocks_a, params=params_a)
model_b = Model(initial_state=states_b, state_update_blocks=state_update_blocks_b, params=params_b)

simulation_1 = Simulation(model=model_a, timesteps=TIMESTEPS, runs=RUNS)
simulation_2 = Simulation(model=model_b, timesteps=TIMESTEPS, runs=RUNS)

# Simulate any number of models in parallel
experiment = Experiment([simulation_1, simulation_2])
result = experiment.run()
```

* cadCAD compatibility and familiar data structure

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

### Advanced Features

RadCAD offers a range of special features that allow a wide range of model classes, great flexibility and extendibility, customisation and improved performance.

#### Advanced features - model classes and specifications:

* Model classes are iterable, so you can iterate over them step-by-step from one state to the next (useful for gradient descent, live digital twins)
* Supports  [state-space analysis](https://en.wikipedia.org/wiki/State-space_representation)  (i.e. simulation of system state over time) and [phase-space analysis](https://en.wikipedia.org/wiki/Phase_space) analysis (i.e. generation of all unique system states in a given experimental setup).


#### Advanced features - model implementations:

* Disable `deepcopy` option for improved performance (at cost of mutability)
* Robust exception handling with partial results, and tracebacks
* Parallel processing with multiple backend options: `multiprocessing`, `pathos`, `ray`
* Distributed computing and remote execution in a cluster (AWS, GCP, Kubernetes, ...) using [Ray - Fast and Simple Distributed Computing](https://ray.io/)
* Hooks to easily extend the functionality - e.g. save results to HDF5 file format after completion
* Parameters can be a dataclass! This enables typing and dot notation for accessing parameters.



