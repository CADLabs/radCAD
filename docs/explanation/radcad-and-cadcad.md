# radCAD and cadCAD

radCAD and [cadCAD](https://github.com/cadCAD-org/cadCAD) implement the same modelling paradigm, the [Generalised Dynamical Systems model](dynamical-systems.md), but differ in API ergonomics and performance. This page explains the relationship so you can choose between them and move between them.

## Shared foundations

Both frameworks describe a system as State Variables, Policy Functions, State Update Functions, and Partial State Update Blocks, and both produce results with the same `simulation`/`subset`/`run`/`substep`/`timestep` structure. Crucially, **your model logic is portable**: the policy and state update functions you write for cadCAD work in radCAD unchanged.

## What radCAD changes

**A leaner configuration API.** cadCAD configures a run through several steps: `config_sim`, `append_configs`, an `ExecutionContext`, an `Executor`, and a global `configs` list. radCAD collapses this into three explicit classes: [`Model`](../reference/api.md#radcad.wrappers.Model), [`Simulation`](../reference/api.md#radcad.wrappers.Simulation), and [`Experiment`](../reference/api.md#radcad.wrappers.Experiment). (Note the one rename: `partial_state_update_blocks` to `state_update_blocks`.)

**Performance focus.** radCAD runs faster, so you can fit more runs, larger sweeps, and bigger models in the same time. It exposes performance levers directly on the `Engine`: [pluggable backends](../how-to/choose-a-backend.md), a [configurable deepcopy strategy](state-mutation-and-performance.md), and [substep dropping](../how-to/improve-performance.md).

**Extensibility.** [Hooks](../how-to/use-hooks.md) provide a stable API for extending behaviour without modifying the core, [models are iterable](../how-to/iterate-over-a-model.md) for in-the-loop use, and [System Parameters can be typed dataclasses](../how-to/use-dataclass-parameters.md).

**Distributed execution.** The [Ray backend](../how-to/run-on-a-ray-cluster.md) scales runs across a cluster.

## Compatibility mode

For existing cadCAD codebases, radCAD ships a **compatibility mode** that re-exports the cadCAD configuration and execution API under `radcad.compat.cadCAD.*`, translating it into radCAD behind the scenes. Repoint your imports and an existing cadCAD model runs on radCAD with no further changes. It doesn't promise to cover every cadCAD option, but handles most models.

See [Migrate from cadCAD](../how-to/migrate-from-cadcad.md) for both the rewrite path and the compatibility-mode path.

## Which should I use?

- **New project?** Start with radCAD's native API; it's simpler and faster.
- **Existing cadCAD model?** Use [compatibility mode](../how-to/migrate-from-cadcad.md) to run it on radCAD immediately, then migrate the configuration incrementally if you wish.
- **Learning the paradigm?** The concepts are identical; [cadCAD.education](https://cadcad.education) teaches both.
