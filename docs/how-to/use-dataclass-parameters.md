# Use dataclass parameters

Instead of a plain dictionary, you can define System Parameters as **(nested) dataclasses**. This gives you typing, dot-notation access, and the ability to group related parameters into namespaces, which helps with large models. Sweeps still work.

## Define typed, nested parameters

Use [`radcad.utils.default`](../reference/api.md#radcad.utils.default) whenever a dataclass field's default is mutable (a list, or a nested dataclass instance):

```python
from dataclasses import dataclass
from radcad.utils import default


@dataclass
class LiquidityPoolParameters:
    initial_liquidity: int = 100_000


@dataclass
class ProtocolParameters:
    liquidity_pool: LiquidityPoolParameters = default(LiquidityPoolParameters())


@dataclass
class Parameters:
    protocol: ProtocolParameters = default(ProtocolParameters())
    agents: AgentParameters = default(AgentParameters())


model.params = Parameters()
```

!!! warning "Always use `default(...)` for mutable defaults"
    Python forbids mutable default values on dataclass fields. `default(obj)` wraps the value in a `field(default_factory=...)` so each instance gets its own copy. Using a bare list or dataclass instance will raise a `ValueError`.

## Access parameters by dot notation

In your model functions, read parameters with attribute access:

```python
from typing import List, Tuple
from radcad.types import StateVariables, PolicySignal

def update_liquidity(
    params: Parameters,
    substep: int,
    state_history: List[List[StateVariables]],
    previous_state: StateVariables,
    policy_input: PolicySignal,
) -> Tuple[str, int]:
    if not previous_state["liquidity"]:
        updated_liquidity = params.protocol.liquidity_pool.initial_liquidity
    else:
        updated_liquidity = ...
    return "liquidity", updated_liquidity
```

## Sweeping dataclass parameters

Sweeps work exactly as they do for dicts: make any field a list of values, and radCAD expands subsets positionally across all lists, anywhere in the nesting. See [Run a parameter sweep](parameter-sweeps.md).

```python
@dataclass
class Parameters:
    rate: list = default([0.05, 0.1, 0.2])   # a 3-subset sweep
    capacity: list = default([1000])
```

## See also

- [`generate_parameter_sweep`](../reference/api.md#radcad.utils.generate_parameter_sweep): how nested dataclasses are expanded.
- [Model structure & data](../reference/data-structures.md).
