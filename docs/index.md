# radCAD

**A [cadCAD](https://github.com/cadCAD-org/cadCAD)-compatible Python framework for modelling and simulating [dynamical systems](https://en.wikipedia.org/wiki/Dynamical_system).**

A dynamical system is one whose state evolves over time according to a fixed set of rules that depend on its current state and, optionally, external inputs. With radCAD you describe a system as a set of **state transitions** (encoding differential equations, agent behaviour, or other logic), then run **parameter sweeps**, **Monte Carlo runs**, and **A/B tests** over it in parallel across multiple processing backends.

```python
import pandas as pd
from radcad import Model, Simulation

initial_state = {"x": 1}
params = {"growth": [1, 2]}

def policy(params, substep, state_history, previous_state):
    return {"dx": params["growth"]}

def update_x(params, substep, state_history, previous_state, policy_input):
    return "x", previous_state["x"] + policy_input["dx"]

state_update_blocks = [{
    "policies": {"growth_policy": policy},
    "variables": {"x": update_x},
}]

model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=params)
simulation = Simulation(model=model, timesteps=10, runs=1)
df = pd.DataFrame(simulation.run())
```

## Where should I go?

<div class="grid cards" markdown>

- :material-school: **[Tutorials](tutorials/index.md)**

    ---

    *Learning-oriented.* New to radCAD? Start here. Install the framework and build your first working model step by step.

- :material-wrench: **[How-to guides](how-to/index.md)**

    ---

    *Task-oriented.* How to get a specific job done: parameter sweeps, Monte Carlo runs, A/B tests, backends, performance, hooks, and more.

- :material-book-open-variant: **[Reference](reference/index.md)**

    ---

    *Information-oriented.* The full API, the model data structures, every `Engine` setting, and a glossary of terms.

- :material-lightbulb-on: **[Explanation](explanation/index.md)**

    ---

    *Understanding-oriented.* The concepts behind radCAD: dynamical systems, the architecture, the deepcopy performance trade-off, and how radCAD relates to cadCAD.

</div>

## Why radCAD?

- **Simple API**: describe a model, wrap it in a simulation, run it.
- **Fast**: optimised for large parameter sweeps and Monte Carlo runs.
- **cadCAD compatible**: standard functions, data structures, and simulation results, plus a [compatibility mode](how-to/migrate-from-cadcad.md) for existing cadCAD models.
- **Extensible**: [hooks](how-to/use-hooks.md), [iterable models](how-to/iterate-over-a-model.md), and typed [dataclass parameters](how-to/use-dataclass-parameters.md).
- **Robust exception handling**: failed runs return [partial results and tracebacks](how-to/handle-exceptions.md), so one error won't discard a long-running simulation.
- **Distributed execution**: parallel processing across [multiple backends](how-to/choose-a-backend.md), including [remote Ray clusters](how-to/run-on-a-ray-cluster.md).
- **Tested**: against Python 3.10–3.12 on Linux, macOS, and Windows.

## Open-source models using radCAD

- [Ethereum Economic Model](https://github.com/CADLabs/ethereum-economic-model) by CADLabs.
- [Beacon Runner](https://github.com/ethereum/beaconrunner) by Ethereum RIG.
- [GEB Controller Simulations](https://github.com/reflexer-labs/geb-simulations) by BlockScience.
- [Fei Protocol Model](https://github.com/CADLabs/fei-protocol-model) by CADLabs.

## Getting help

- 🎓 [cadCAD.education](https://cadcad.education): a cadCAD beginner course.
- 🐛 [GitHub issues](https://github.com/CADLabs/radCAD/issues).

