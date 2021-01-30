# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2021-01-30
### Added
- Error handling (default `Engine(raise_exceptions=True)`)
- Partial simulation results (on run failure / exception)
- Memory profiling using mprof

### Changed
- Default simulation engine (changed from MULTIPROCESSING to PATHOS)

### Removed
-
