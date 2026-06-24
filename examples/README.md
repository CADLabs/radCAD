# Examples

A collection of radCAD models, from simple system dynamics to agent-based and interactive simulations.

## Predator-Prey (System Dynamics)

Classic [Lotka-Volterra](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations) predator-prey dynamics modelled as a continuous system of differential equations.

- Notebook: `[predator_prey_sd/predator-prey-sd.ipynb](predator_prey_sd/predator-prey-sd.ipynb)`
- Contributors: [@danlessa](https://github.com/danlessa) (model creator)

## Predator-Prey (Agent-Based)

The same dynamics as an agent-based model on a grid world, where prey and predator agents grow food, move, reproduce, feed, hunt, and die each timestep. Demonstrates structuring a larger model across multiple modules.

- Notebook: `[predator_prey_abm/predator-prey-abm.ipynb](predator_prey_abm/predator-prey-abm.ipynb)`
- Model code: `[predator_prey_abm/model/](predator_prey_abm/model)`
- Contributors: [@danlessa](https://github.com/danlessa) (model creator)

## Harmonic Oscillator

Models a damped [harmonic oscillator](https://en.wikipedia.org/wiki/Harmonic_oscillator), wrapping the simulation in a gradient-descent loop to find the damping factor that critically damps the system. Demonstrates iterative optimisation over a radCAD model.

- Notebook: `[harmonic_oscillator/harmonic_oscillator.ipynb](harmonic_oscillator/harmonic_oscillator.ipynb)`
- Contributors: [@rogervs](https://github.com/rogervs) (model creator)

## Iterable Models

Shows how to run a radCAD model iteratively, feeding results back in and stepping the simulation forward over time.

- Notebook: `[iterable_models/iterable-models.ipynb](iterable_models/iterable-models.ipynb)`

## Game of Life

Conway's Game of Life implemented with NumPy and run as a radCAD model, including Gosper glider gun and higher-period patterns. Based on [drsfenner.org's "Game of Life in Numpy"](http://drsfenner.org/blog/2015/08/game-of-life-in-numpy-2/).

- Notebook: `[game_of_life/game-of-life.ipynb](game_of_life/game-of-life.ipynb)`
- Model code: `[game_of_life/game_of_life.py](game_of_life/game_of_life.py)`

## Streamlit App

An interactive [Streamlit](https://streamlit.io/) front-end for the Game of Life model, ready to deploy.

- App: `[streamlit/game_of_life/app.py](streamlit/game_of_life/app.py)`

