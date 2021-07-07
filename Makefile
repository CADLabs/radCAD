test:
	poetry run python3 -m pytest tests

profile-memory-radcad:
	poetry run python3 -m mprof run --include-children benchmarks/benchmark_memory_radcad.py && poetry run python3 -m mprof plot

profile-memory-cadcad:
	poetry run python3 -m mprof run --include-children benchmarks/benchmark_memory_cadcad.py && poetry run python3 -m mprof plot

coverage:
	poetry run python3 -m pytest tests --cov=radcad
	poetry run coveralls

start-jupyter-lab:
	poetry run python3 -m jupyter lab 

plotly-jupyter-lab-support:
	# JupyterLab renderer support
	jupyter labextension install jupyterlab-plotly@4.14.3
	# OPTIONAL: Jupyter widgets extension
	jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.14.3