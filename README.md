# radCAD
![PyPI](https://badge.fury.io/py/radcad.svg)
[![Build Status](https://github.com/CADLabs/radCAD/actions/workflows/python.yml/badge.svg)](https://github.com/CADLabs/radCAD/actions/workflows/python.yml)
[![Coverage Status](https://coveralls.io/repos/github/CADLabs/radCAD/badge.svg?branch=master&service=github)](https://coveralls.io/github/CADLabs/radCAD?branch=master&service=github)
[![Maintainability](https://api.codeclimate.com/v1/badges/a65a6fb94f052cd804c2/maintainability)](https://codeclimate.com/github/CADLabs/radCAD/maintainability)

![Gosper Glider Gun](https://github.com/CADLabs/radCAD/blob/master/examples/game_of_life/gosper-glider-gun.gif)

**radCAD is a [cadCAD](https://github.com/cadCAD-org/cadCAD)-compatible Python framework for modelling and simulating [dynamical systems](https://en.wikipedia.org/wiki/Dynamical_system).** A dynamical system is one whose state evolves over time according to a fixed set of rules that depend on its current state and, optionally, external inputs.

You describe a system as a set of **state transitions** (encoding differential equations, agent behaviour, or other logic), then run **parameter sweeps**, **Monte Carlo runs**, and **A/B tests** over it in parallel across multiple processing backends. radCAD is compatible with cadCAD: its functions, data structures, and simulation results follow the same conventions, so existing cadCAD models run with minimal changes.

> 📚 **[Read the documentation →](https://cadlabs.github.io/radCAD/)** &nbsp;|&nbsp; 🎓 **[cadCAD.education](https://cadcad.education)** beginner course &nbsp;|&nbsp; 💬 **[cadCAD Discord](https://discord.gg/HrJUh2FD)**

### Why radCAD?

* **Simple API**: describe a model, wrap it in a simulation, run it.
* **Fast**: optimised for large parameter sweeps and Monte Carlo runs.
* **cadCAD compatible**: standard functions, data structures, and simulation results, plus a [compatibility mode](https://cadlabs.github.io/radCAD/how-to/migrate-from-cadcad/) for existing cadCAD models.
* **Extensible**: [hooks](https://cadlabs.github.io/radCAD/how-to/use-hooks/), [iterable models](https://cadlabs.github.io/radCAD/how-to/iterate-over-a-model/), and typed [dataclass parameters](https://cadlabs.github.io/radCAD/how-to/use-dataclass-parameters/).
* **Robust exception handling**: failed runs return [partial results and tracebacks](https://cadlabs.github.io/radCAD/how-to/handle-exceptions/), so one error won't discard a long-running simulation.
* **Distributed execution**: parallel processing across [multiple backends](https://cadlabs.github.io/radCAD/how-to/choose-a-backend/), including [remote Ray clusters](https://cadlabs.github.io/radCAD/how-to/run-on-a-ray-cluster/).
* **Tested**: against Python 3.8–3.12 on Linux, macOS, and Windows.

## Installation

```bash
pip install radcad
```

Optional extras:

```bash
pip install "radcad[compat]"                  # cadCAD compatibility layer
pip install "radcad[extension-backend-ray]"   # Ray backend
```

## Quick start

```python
import pandas as pd
from radcad import Model, Simulation

initial_state = {"x": 1}
params = {"growth": [1, 2, 3]}

def policy(params, substep, state_history, previous_state):
    return {"dx": params["growth"]}

def update_x(params, substep, state_history, previous_state, policy_input):
    return "x", previous_state["x"] + policy_input["dx"]

state_update_blocks = [
    {
        "policies": {"growth_policy": policy},
        "variables": {"x": update_x},
    }
]

model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
simulation = Simulation(model=model, timesteps=10, runs=1)

df = pd.DataFrame(simulation.run())
print(df[["simulation", "subset", "run", "timestep", "substep", "x"]].tail())
```

## Core concepts

The primary API is:

1. `Model`: initial state, state update blocks, and parameters.
2. `Simulation`: one model plus timesteps and Monte Carlo runs.
3. `Experiment`: one or more simulations, useful for A/B tests and batches.
4. `Engine`: execution settings, backend selection, deepcopy behaviour, substep retention, and exception handling.

```python
from radcad import Experiment

experiment = Experiment([simulation_a, simulation_b])
result = experiment.run()
```

## Documentation

The documentation site is built with MkDocs Material and organised with the [Diátaxis](https://diataxis.fr/) framework:

- **Tutorials**: learn radCAD from a complete first simulation.
- **How-to guides**: configure sweeps, hooks, backends, experiments, and exception handling.
- **Reference**: API docs generated from docstrings plus the simulation data model.
- **Explanation**: concepts, execution model, and performance trade-offs.

Docs are published to GitHub Pages at <https://cadlabs.github.io/radCAD/>.

Build locally:

```bash
pdm install -G docs
pdm run mkdocs serve
```

## Examples

- [Iterable models](examples/iterable_models/iterable-models.ipynb): use models as step-by-step generators and live digital twins.
- [Game of Life](examples/game_of_life/game-of-life.ipynb): Conway's cellular automaton.
- [Predator-prey system dynamics](examples/predator_prey_sd/predator-prey-sd.ipynb): Lotka-Volterra equations.
- [Predator-prey agent-based model](examples/predator_prey_abm/predator-prey-abm.ipynb): agent-based ecological model.
- [Harmonic oscillator](examples/harmonic_oscillator/harmonic_oscillator.ipynb): oscillatory system example.

## Open-source models using radCAD

- [Ethereum Economic Model](https://github.com/CADLabs/ethereum-economic-model) by CADLabs.
- [Beacon Runner](https://github.com/ethereum/beaconrunner) by Ethereum RIG.
- [GEB Controller Simulations](https://github.com/reflexer-labs/geb-simulations) by BlockScience.
- [Fei Protocol Model](https://github.com/CADLabs/fei-protocol-model) by CADLabs.

## Development

Set up the development environment with [PDM](https://pdm-project.org/):

```bash
pdm use "python3.10"
pdm install --lockfile pdm.lock
```

Use `pdm-py38.lock` for Python 3.8.

Run tests and benchmarks with Nox:

```bash
nox --session tests
nox --session benchmarks
```

See the [Contributing guide](https://cadlabs.github.io/radCAD/contributing/) for environment setup, profiling, releasing, and other development tasks.

## Acknowledgements

Thanks to [@danlessa](https://github.com/danlessa), [@rogervs](https://github.com/rogervs), [@abzaremba](https://github.com/abzaremba), and [@smngvlkz](https://github.com/smngvlkz) for contributions to examples, documentation, compatibility, and CI.

## License

radCAD is released under the license in [LICENSE](LICENSE).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CADLabs/radCAD&type=Date)](https://star-history.com/#CADLabs/radCAD&Date)
