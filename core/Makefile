setup:
	rustup install stable
	rustup default stable

release-linux:
	cargo build --release
	cp target/release/libradCAD.so output/radCAD.so

release-windows:
	cargo build --release
	cp target/release/libradCAD.dll output/radCAD.pyd

release-macos:
	cargo rustc --release -- -C link-arg=-undefined -C link-arg=dynamic_lookup
	cp target/release/libradCAD.dylib output/radCAD.so

test:
	python3 -m unittest tests/integration_test.py

benchmark:
	python3 -m pytest tests/benchmark_test.py

mprof:
	python3 -m mprof run --multiprocess benchmark.py
	python3 -m mprof plot

publish:
	maturin publish
