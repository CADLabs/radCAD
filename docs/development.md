## Development

### Set up environment with Poetry

Suggested dependency management and packaging [Poetry](https://python-poetry.org/)

Set up and enter the Python environment with Poetry:
```bash
poetry --help
poetry install
poetry env use python3
poetry shell
```
Requires [>= Python 3.8](https://www.python.org/downloads/) 


### Jupyter Notebooks with Poetry

```bash
# Install kernel
poetry run python -m ipykernel install --user --name python3-radcad
# Start Jupyter
poetry run python -m jupyter lab
```

### Publishing to PyPI

```bash
# 1. Update `pyproject.toml` package version using semantic versioning
# 2. Update CHANGELOG.md
# 3. Submit PR and run tests
# 4. Merge into master on success
# 5. Build and publish package
poetry publish --build
# Enter in PyPI package repository credentials
# 6. Tag master commit with version e.g. `v0.5.0` and push
```

### Pip or alternative package managers

Export `requirements.txt` using Poetry:
```bash
poetry export --without-hashes -f requirements.txt --output requirements.txt
```

Note: the root `requirements.txt` is used for Streamlit app in examples, and is not for development.