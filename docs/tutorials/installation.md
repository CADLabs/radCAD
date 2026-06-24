# Installation

In this tutorial you will install radCAD and confirm it runs.

## Requirements

- Python **3.8 – 3.12**
- A package manager such as `pip`

## Install from PyPI

```bash
pip install radcad
```

The default installation includes everything you need to build and run models, including the default `pathos` parallel-processing backend.

## Optional extras

radCAD ships several optional dependency groups. Install only the ones you need:

=== "pip"

    ```bash
    # cadCAD compatibility mode (run existing cadCAD models)
    pip install "radcad[compat]"

    # Ray backend for local and remote/cluster execution
    pip install "radcad[extension-backend-ray]"
    ```

=== "Poetry"

    ```bash
    poetry install -E compat
    poetry install -E extension-backend-ray
    ```

=== "PDM"

    ```bash
    pdm install -G compat
    pdm install -G extension-backend-ray
    ```

See [Migrate from cadCAD](../how-to/migrate-from-cadcad.md) and [Run on a Ray cluster](../how-to/run-on-a-ray-cluster.md) for when you need these.

## Verify the installation

Run the following to confirm radCAD imports and reports its version:

```python
import radcad
from radcad import Model, Simulation, Experiment, Engine, Backend

print(radcad.__version__)
```

If that prints a version number without errors, you're ready to [build your first model](first-model.md).

## Run the example notebooks

radCAD's [examples](https://github.com/CADLabs/radCAD/tree/master/examples) are Jupyter notebooks. Clone the repository, install JupyterLab, and launch it:

```bash
pip install jupyterlab
jupyter lab
```

Individual notebooks may require extra packages, such as `matplotlib` or `plotly`.
