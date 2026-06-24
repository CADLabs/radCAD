# State mutation & performance

The single biggest performance factor in radCAD, and in cadCAD, is **deep-copying state**. Understanding why explains most of radCAD's performance options.

## The problem: accidental mutation

State Update Functions receive the current state and return new values. But Python passes dictionaries and objects *by reference*. If a function mutated the state it was handed (say, appending to a list inside it), that change would leak into the framework's own copy of the state, corrupting later timesteps and other runs.

To prevent this, radCAD **deep-copies the state before passing it to your functions**. Your function gets its own private copy; whatever it does to that copy can't affect the canonical state.

## The cost

Deep copying is expensive. It must recreate the object *and* every key and value it contains, recursively. For a model with large or deeply nested state, this copying can dominate total runtime, outweighing the arithmetic of the model itself.

radCAD makes two pragmatic choices to manage this cost:

1. **Mutation of `state_history` is allowed; mutation of the current state is prevented.** Copying the entire history every substep would be prohibitive, so radCAD only protects the current state and trusts you to treat history as read-only (standard Python good practice).
2. **The default copy method is `pickle`, not `copy.deepcopy`.** Pickle's `dumps`/`loads` round-trip is faster than the standard library's `deepcopy` for typical model state, at the cost of only supporting picklable (serialisable) types. See this [benchmark discussion](https://stackoverflow.com/questions/24756712/deepcopy-is-extremely-slow). These could be interchanged in future.

## The performance levers

Given the above, your options form a spectrum from *safest* to *fastest*:

| Lever | Effect | Trade-off |
| --- | --- | --- |
| `deepcopy=True` (default) | Full protection against state mutation. | Slowest. |
| Custom `deepcopy_method` | Pick the copy strategy best suited to your state types. | Requires knowing your data. |
| `drop_substeps=True` | Less data copied/stored per timestep. | Lose substep detail. |
| `deepcopy=False` | No copying; fastest possible. | **You** must guarantee your functions never mutate state. |

See [Improve performance](../how-to/improve-performance.md) for how to set each.

## Choosing wisely

- Start with the defaults. Correctness first.
- If a profile shows copying dominates, try `drop_substeps=True` (free if you don't need substeps) and a [custom `deepcopy_method`](../how-to/improve-performance.md#choose-a-faster-deepcopy-method).
- Only reach for `deepcopy=False` once you're confident every State Update Function treats its inputs as immutable. The speed-up is large, but a single in-place mutation becomes a hard-to-find bug.

## See also

- [Improve performance](../how-to/improve-performance.md): the practical steps.
- [Architecture & execution flow](architecture.md): where copying happens in the loop.
