# Contributing

How to set up a radCAD development environment and run the project's tooling.

## Development environment

Set up the environment with the [PDM](https://pdm-project.org/) package manager:

```bash
pdm use "python3.10"
pdm install --lockfile pdm.lock
```

Use `pdm-py38.lock` for Python 3.8 and `pdm.lock` for Python 3.9+.

## Run the tests

The project uses [Nox](https://nox.thea.codes/) to run tests and benchmarks across Python versions. Each Python version used by a session must be available on the system.

Install Nox:

=== "pipx"

    ```bash
    pipx install nox
    ```

=== "pip"

    ```bash
    python3 -m pip install nox
    ```

Run all tests:

```bash
nox --session tests
```

Run the default benchmark across all Python versions:

```bash
nox --session benchmarks
```

See [`noxfile.py`](https://github.com/CADLabs/radCAD/blob/master/noxfile.py) for other sessions. To profile individual benchmarks, see [Improve performance](how-to/improve-performance.md#benchmark-your-changes).

## Run the example notebooks

To register the PDM-managed environment as a Jupyter kernel and start JupyterLab:

```bash
pdm run ipykernel install --user --name python3-radcad
pdm run jupyter lab
```

See [Run the example notebooks](tutorials/installation.md#run-the-example-notebooks) for the general setup.

## Build the documentation

The documentation site is built with MkDocs Material:

```bash
pdm install -G docs
pdm run mkdocs serve
```

## Release a new version

Maintainers publish to PyPI with PDM:

```bash
# 1. Update the version in pyproject.toml (semantic versioning)
# 2. Update CHANGELOG.md
# 3. Open a PR and run the tests
# 4. Merge into master once green
# 5. Build and publish
pdm publish
# 6. Tag the master commit with the version, e.g. v0.5.0, and push
```

### Export requirements.txt

```bash
pdm export -o requirements.txt --without-hashes
```

The root `requirements.txt` is used by the Streamlit example app, not for development.
