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

