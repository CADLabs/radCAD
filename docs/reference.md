# Reference

---

This part of the project documentation focuses on
an **information-oriented** approach. Use it as a
reference for the technical implementation of the
`radcad` project code.


## Table of Contents

 - [Development](#development-subsection) 
 - [cadCAD Compatibility](#cadcad-compatibility)
 - [Directory Structure](#directory-structure)
 - [Model Architecture](#model-architecture)
 - [Known issues](#known-issues)


---

## Development

Jump to [Development](development.md) section for information about:

* Set up environment with Poetry
* Jupyter Notebooks with Poetry

[//]: # ( ## Testing)
[//]: # ( ## Benchmarking)

## cadCAD Compatibility

Jump to [cadCAD Compatibility](cadcad_compatibility.md) to read more about:

* Migrating from cadCAD to radCAD
* cadCAD Compatibility Mode


## Directory Structure

[//]: # ( * [data/](data/): Datasets and API data sources (such as Etherscan.io and Beaconcha.in) used in the model)

* [benchmarks/](benchmarks/): Tests to compare execution time of cadCAD and radCAD.
* [cluster/](cluster/): Tests to compare execution time of cadCAD and radCAD.
* [docs/](docs/): Documentation such as auto-generated docs from Python docstrings and Markdown docs
* [examples/](experiments/): Analysis notebooks and experiment workflow (such as configuration and execution)
* [radcad/](radcad/): Model software architecture (structural and configuration modules)
* [tests/](tests/): Unit and integration tests for model and notebooks

## Model Architecture

In the [Getting started](gettingstarted.md) we have introduced a very general overview of the main classes:  `Model`, `Simulation`, `Experiment`, `Engine`.  

Jump to [Model Architecture](model_architecture.md) for more details about the classes used in radCAD.

## Known issues

### Plotly doesn't display in Jupyter Lab

To install and use Plotly with Jupyter Lab, you might need NodeJS installed to build Node dependencies, unless you're using the Anaconda/Conda package manager to manage your environment. Alternatively, use Jupyter Notebook which works out the box with Plotly.

See https://plotly.com/python/getting-started/

You might need to install the following "lab extension": 
```bash
jupyter labextension install jupyterlab-plotly@4.14.3
```

### Windows Issues

If you receive the following error and you use Anaconda, try: `conda install -c anaconda pywin32`
> DLL load failed while importing win32api: The specified procedure could not be found.
