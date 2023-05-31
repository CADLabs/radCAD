# Getting started

---

## Table of Contents

 - [Installation and environment set up](#installation-and-environment-set-up)
 - [Jupyter Notebooks](#jupyter-notebooks)
 - [First model](#first-model)
 - [Elements of the model](#elements-of-the-model)

---


## Installation and environment set up

Please note that for development, we suggest using [Poetry](https://python-poetry.org/) for dependency management and packaging. Instructions for setting up the Python environment with Poetry are in the section [Reference](/reference/#set-up-environment-with-poetry).

### 0. Pre-installation Virtual Environments with [`venv`](https://docs.python.org/3/library/venv.html) (Optional):
If you wish to create an easy to use virtual environment to install radCAD inside of, please use the built in `venv` package [see: [documentation about venv](https://docs.python.org/3/library/venv.html)].

**Create** a virtual environment:
```bash
$ python3 -m venv venv
```

**Activate** an existing virtual environment (Unix/macOS):
```bash
$ source venv/bin/activate
```

**Activate** an existing virtual environment (Windows):
```bash
$ source venv\Scripts\activate
```

### 1. Installation: 
Requires [>= Python 3.8](https://www.python.org/downloads/) 

Install Using [pip](https://pypi.org/project/cadCAD/)
```bash
$ pip install radCAD
```

### 2. Install Python dependencies inside virtual environment

```bash
pip install -r requirements.txt
```



## Jupyter Notebooks

Assuming that the `ipykernel` has been installed together with the other dependencies from `requirements.txt` (step [2](#2-install-python-dependencies-inside-virtual-environment))

```bash
ipython kernel install --user --name=radcad_kernel
```


## First model:

We refer to the section [Examples](examples.md) to see various models and references to tutorials. 

Run `predator-prey-sd.py` to check if radCAD has been successfuly installed. This is a script version of the Jupyter Notebooks model `predator-prey-sd.ipynb` that is refered to in the section [Examples](/examples/#predator-prey).


```bash
cd examples/predator_prey_sd
python predator-prey-sd.py
```

Did you get the expected output, as follows?

```bash
The final sizes of the populations are, prey: 3068.0 and predator: 215.0.
```


## Elements of the model

This section contains high level information about the model, for more details please consult [Features](features.md) for information organised by model functionality, [Model Architecture](/reference/#model-architecture) for more information about the model architecture, [Examples](examples.md) to see some ways how the model can be applied.

### Main classes

`radCAD` provides the following classes:

1. A system is represented in some form as a `Model`
2. A `Model` can be simulated using a `Simulation`
3. An `Experiment` consists of one or more `Simulation`
4. An `Experiment` or a `Simulation` is run by the `Engine`

So, the hierarchy is as follows `Model` > `Simulation` > `Experiment` > `Engine`.

```python
from radcad import Model, Simulation, Experiment

model = Model(initial_state=initial_state, 
              state_update_blocks=state_update_blocks, 
              params=params)
simulation = Simulation(model=model, timesteps=100_000, runs=1)

result = simulation.run()
# Or, multiple simulations:
# experiment = Experiment([simulation_1, simulation_2, simulation_3])
# result = experiment.run()

df = pd.DataFrame(result)
```

### The typical layout of the radCAD model elements:



**Modelling**

<ol>
  <li>System parameters</li>
  <li>State variables (including initial state)</li>
  <li>Policy functions</li>
  <li>State update functions</li>
  <li>Partial state update blocks</li>
</ol>

**Simulation**

<ol start=6>
  <li>Simulation configuration parameters</li>
  <li>Model</li>
  <li>Simulation</li>
  <li>Execute the simulation</li>
  <li>Analysis</li>
</ol>


If you are familiar with cadCAD, you might notice that the classes provided by radCAD are a bit different, and so is the typical layout. Learn more about [cadCAD Compatibility](/reference/#cadcad-compatibility).