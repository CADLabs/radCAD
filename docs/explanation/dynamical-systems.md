# Dynamical systems & the GDS model

## What is a dynamical system?

A [dynamical system](https://en.wikipedia.org/wiki/Dynamical_system) is one whose state evolves over time according to a fixed set of rules. Those rules depend on the system's current state and, optionally, on external inputs. Population dynamics, market mechanics, epidemic spread, and control systems are all dynamical systems.

Formally, you can think of the rules as a function that maps the current state to the next:

$$
\text{state}_{t+1} = f(\text{state}_t,\ \text{parameters},\ \text{inputs})
$$

radCAD evaluates that function repeatedly and efficiently: across many timesteps, many runs, and many parameter combinations.

## The Generalised Dynamical Systems (GDS) model

radCAD (like cadCAD) structures models using the **Generalised Dynamical Systems** representation. Rather than writing one monolithic transition function, you decompose the transition into small, composable pieces:

- **State Variables** hold the system's state.
- **Policy Functions** observe the state and decide *what should happen*: they compute signals but never mutate state. This mirrors how decisions in real systems are made on the basis of information.
- **State Update Functions** take those signals and *apply* them to individual State Variables. This is where state actually changes.
- **Partial State Update Blocks (PSUBs)** group policies and updates into **substeps**, and an ordered list of blocks composes a full **timestep**.

This separation between *decide* (policies) and *act* (state updates) is the heart of the paradigm. It makes models readable, testable in isolation, and faithful to the structure of the systems being modelled.

## Why decompose this way?

- **Composability**: substeps let you sequence interdependent updates within a single timestep (e.g. compute prices, then settle balances).
- **Separation of concerns**: policies encode behaviour and decision-making; state updates encode accounting. Each is simple on its own.
- **Aggregation**: multiple policies can contribute to the same signal, and radCAD sums them, modelling multiple forces acting on one variable.
- **Reuse**: generic State Update Functions like [`update_from_signal`](../reference/api.md#radcad.utils.update_from_signal) and [`accumulate_from_signal`](../reference/api.md#radcad.utils.accumulate_from_signal) remove boilerplate.

## From rules to experiments

Describing the rules is only half the story. The same model can be subjected to different **experiments**:

- **Parameter sweeps** explore how outcomes depend on parameters.
- **Monte Carlo runs** explore the distribution of outcomes under randomness.
- **A/B tests** compare structurally different model variants.

Because the rules are separated from the experiment configuration, you change *how* you interrogate a model without rewriting *what* it is. See the [how-to guides](../how-to/index.md) for each.

## See also

- [Build your first model](../tutorials/first-model.md): the paradigm in practice.
- [Model structure & data](../reference/data-structures.md): the precise data structures.
