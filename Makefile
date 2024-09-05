start-jupyter-lab:
	pdm run jupyter lab

plotly-jupyter-lab-support:
	# JupyterLab renderer support
	jupyter labextension install jupyterlab-plotly@4.14.3
	# OPTIONAL: Jupyter widgets extension
	jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.14.3

lock-py38:
	pdm lock \
		-G compat -G extension-backend-ray \
		--python="==3.8.*" \
		--lockfile pdm-py38.lock

lock-py39+:
	pdm lock \
		-G compat -G extension-backend-ray \
		--python=">=3.9" \
		--lockfile pdm.lock

lock: lock-py38 lock-py39+

install-py38:
	pdm install --lockfile pdm-py38.lock

install-py39+:
	pdm install --lockfile pdm.lock

test:
	pdm run pytest tests

coverage:
	pdm run pytest tests --cov=radcad
	pdm run coveralls

profile-memory-radcad:
	pdm run mprof run --include-children benchmarks/benchmark_memory_radcad.py && pdm run mprof plot

profile-memory-cadcad:
	pdm run mprof run --include-children benchmarks/benchmark_memory_cadcad.py && pdm run mprof plot
