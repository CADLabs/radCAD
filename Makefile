release:
	cargo build --release

release-macos:
	cargo rustc --release -- -C link-arg=-undefined -C link-arg=dynamic_lookup
	cp target/release/librad_cad.dylib output/rad_cad.so
