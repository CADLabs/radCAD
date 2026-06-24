start-jupyter-lab:
	uv run jupyter lab

plotly-jupyter-lab-support:
	# JupyterLab renderer support
	jupyter labextension install jupyterlab-plotly@4.14.3
	# OPTIONAL: Jupyter widgets extension
	jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.14.3

lock:
	uv lock

install:
	uv sync

test:
	uv run pytest tests

coverage:
	uv run pytest tests --cov=radcad
	uv run coveralls

profile-memory-radcad:
	uv run mprof run --include-children benchmarks/benchmark_memory_radcad.py && uv run mprof plot

profile-memory-cadcad:
	uv run --extra compat mprof run --include-children benchmarks/benchmark_memory_cadcad.py && uv run mprof plot
