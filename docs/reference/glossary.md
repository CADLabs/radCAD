# Glossary

Definitions of the terms used throughout radCAD (largely shared with cadCAD).

**Dynamical system**
: A system whose state evolves over time according to a fixed set of rules that depend on its current state and, optionally, external inputs.

**State Variable**
: A named quantity describing the system at a point in time (e.g. `population`). The set of all State Variables is the **state**.

**Initial state**
: The dictionary of State Variables and their starting values, passed to a [`Model`](api.md#radcad.wrappers.Model).

**System Parameters**
: The configurable inputs the model's rules depend on but which don't themselves evolve. Given as a dict of lists or a (nested) dataclass.

**Policy Function**
: A function that decides *what should happen* in a substep. It reads state and parameters and returns a dictionary of **signals**, without modifying state directly.

**Policy Signal**
: The dictionary output of a Policy Function. When a block has multiple policies, signals sharing a key are summed.

**State Update Function**
: A function that applies signals to update a single State Variable, returning a `(variable_name, new_value)` tuple.

**Partial State Update Block (PSUB)**
: One substep of the model, pairing a set of `policies` with a set of `variables` (State Update Functions). Models are an ordered list of these.

**Substep**
: One Partial State Update Block within a timestep. Substeps run in order, each building on the last.

**Timestep**
: One full pass through all Partial State Update Blocks, advancing the system from one state to the next.

**Run**
: One complete execution of a model over all timesteps. Multiple runs enable Monte Carlo analysis. Numbered from `1` for cadCAD compatibility.

**Subset**
: One combination of swept parameter values. A [parameter sweep](../how-to/parameter-sweeps.md) produces one subset per combination.

**Model**
: The description of a system: initial state, state update blocks, and parameters. See [`Model`](api.md#radcad.wrappers.Model).

**Simulation**
: A model plus a number of timesteps and runs. See [`Simulation`](api.md#radcad.wrappers.Simulation).

**Experiment**
: A collection of simulations executed together (e.g. for A/B tests). See [`Experiment`](api.md#radcad.wrappers.Experiment).

**Engine**
: The component that executes an experiment or simulation, handling parallelism, deepcopy, and exceptions. See [`Engine`](api.md#radcad.engine.Engine).

**Backend**
: The parallel-processing strategy the Engine uses: `PATHOS`, `MULTIPROCESSING`, `RAY`, `RAY_REMOTE`, or `SINGLE_PROCESS`. See [Choose a backend](../how-to/choose-a-backend.md).

**Hook**
: A user-supplied callable fired at a lifecycle point (`before_run`, `after_experiment`, …) to extend behaviour. See [Extend radCAD with hooks](../how-to/use-hooks.md).

**Deepcopy**
: Copying state before each update so model functions can't mutate it unexpectedly. The main performance cost of a simulation. See [State mutation & performance](../explanation/state-mutation-and-performance.md).
