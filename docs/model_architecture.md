# Model Architecture

---

## Table of Contents

 - [Main classes](#main-classes) 
 - [Additional Classes](#additional-classes)
 - [Extensions](#extensions)
 - [All modules, automated documentation](#all-modules-automated-documentation)


---



## Main classes

We have already mentioned the hierarchy of the four most important classes which, ffrom the point of view of function, could be expressed as: `Model` > `Simulation` > `Experiment` > `Engine`.

* `Model` class expresses the model specification, most important part of which is passed throught the parameters `initial_state`, `state_update_blocks=state_update_blocks`, `params`. Below is an example of an instance from the Model class:

```python
model = Model(initial_state=initial_state, 
              state_update_blocks=state_update_blocks, 
              params=params)
```

* `Simulation` is a class used for simulating a `Model`. It extends the class `Executable` and contains nan implemetnation of the method `run`, most other elements are inherited from the class `Executable`. Example of initiating the simulation:

```python
simulation = Simulation(model=model, timesteps=100_000, runs=1)

result = simulation.run()
df = pd.DataFrame(result)
```

* `Experiment` consists of one or more `Simulation` snd is sldo an extension of the class `Executable`. Example of initiating an experiment consisting of one or more of `Simulation`:

```python
experiment = Experiment([simulation_1, simulation_2, simulation_3])
result = experiment.run()

df = pd.DataFrame(result)
```

* `Engine` - class that handles configuration and execution of experiments and simulations. It is a method first defined for the class `Executable` and then inherited by classes  `Simulation` and `Experiment`.


## Additional Classes

### Configuration

* `SimulationExecutionSpecification` - a data class that prepares some of the elements of simulation specification that are common for most experiments, in particular the organisation into blocks, steps and substeps.
* `SimulationExecution` - extends `SimulationExecutionSpecification` and defines various properties and functions needed to execute the simulation.
* `Executable` - instances of class `Executable` contain all information about the model specification and simulation configuration and can be passed to either `Simulation` (for a single simulation) or to `Experiment` (for multiple simulations). `E` contains a method `run` which is not implemented, as that implementation takes place at the level of either `Simulation` or `Experiment`.

### Serial or Parallel Processes

All the classes below extend the `Executor` and provide an implementation of the `execute_runs` method. Refer to [Selecting single or multi-process modes](advanced_features/#selecting-single-or-multi-process-modes).

* ExecutorSingleProcess - simulation will be executed using single (serial) process
* ExecutorMultiprocessing - simulation will be executed using multiple processes with [`multiprocessing` library](https://pypi.org/project/multiprocessing/), the number of parallel processes used is set up to the number of system CPUs less one
* ExecutorPathos - simulation will be executed using multiple processes; Pathos re-writes the core code in Python rather than C, for ease of maintenance at cost of performance, see: [pathos.multiprocessing](https://pathos.readthedocs.io/en/latest/pathos.html#module-pathos.multiprocessing)
* ExecutorRay - multiprocessing backend based on Ray, run locally.
* ExecutorRayRemote -  multiprocessing backend based on Ray, run remotely.



### Helper classes

* `Dataclass` - used to ascertain that something is a `dataclass` from module [`dataclasses`](https://pypi.org/project/dataclasses/),
* `Context` - mutable context passed to [simulation hooks](advanced_features/#hooks-to-extend-functionality).
* `Backend` - codes which backend to use, current options: single process, multiprocessing, Pathos, Ray and Ray remote, with Pathos being the default.
* `Executor` - class that defines the template for executing runs, but itself doesn't provide any implementation for the backend run execution, see: [Single or Parallel Process](#single-or-parallel-process).

## Extensions

### For cadCAD compatibility mode: 

In `radcad/compat/cadCAD/engine` the class `Executor` is used to extend the cadCAD class `Executor` from `cadcad/engine`. Jump here to read more about the [cadCAD compatibility mode](cadcad_compatibility.md).

### For remote cluster execution (using Ray)

In `radcad/extensions/backends` the classes `ExecutorRay` and `ExecutorRayRemote` are used to extend the standard radCAD class `Executor`. Jump here to read more about using the [remote cluster execution](advanced_features/#wip-remote-cluster-execution-using-ray).



## All modules, automated documentation


::: radcad

