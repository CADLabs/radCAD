# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.4.0] - 2021-02-01
### Changed
- Fix of critical state update bug, added regression test `test_paralell_state_update()` to `test_regression.py`

## [0.3.1] - 2021-01-31
### Changed
- Python version downgrade to `^3.7` for Streamlit

## [0.3.0] - 2021-01-30
### Added
- Error handling (default `Engine(raise_exceptions=True)`)
- Partial simulation results (on run failure / exception)
- Memory profiling using mprof

### Changed
- Default simulation engine (changed from MULTIPROCESSING to PATHOS)

### Removed
-
