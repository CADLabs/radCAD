test:
	poetry run python3 -m pytest tests

profile-memory-radcad:
	poetry run python3 -m mprof run --include-children benchmarks/benchmark_memory_radcad.py && poetry run python3 -m mprof plot

profile-memory-cadcad:
	poetry run python3 -m mprof run --include-children benchmarks/benchmark_memory_cadcad.py && poetry run python3 -m mprof plot

coverage:
	poetry run python3 -m pytest tests --cov=radcad
  	poetry run coveralls
