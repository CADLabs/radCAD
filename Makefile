release:
	cargo build --release

release-macos:
	cargo rustc --release -- -C link-arg=-undefined -C link-arg=dynamic_lookup
	cp target/release/librad_cad.dylib output/rad_cad.so

test:
	python3 -m unittest tests/integration_test.py

benchmark:
	python3 -m pytest tests/benchmark_test.py

mprof:
	python3 -m mprof run --multiprocess benchmark.py
	python3 -m mprof plot

publish:
	maturin publish
