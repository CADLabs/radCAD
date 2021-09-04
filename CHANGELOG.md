# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.4] - 2021-09-04
### Added
= Overide for `__deepcopy__` method of Executable class to enable deepcopy after a simulation/experiment has been run
- Add regression test for above `__deepcopy__` method

## [0.8.3] - 2021-08-30
### Changed
- Update radCAD package version in __init__.py

## [0.8.2] - 2021-08-27
### Changed
- Update cadCAD from v0.4.23 to v0.4.27, fixing breaking changes to compat module

## [0.8.1] - 2021-08-24
### Changed
- Minor update: Module package version & package details

## [0.8.0] - 2021-06-28
### Changed
- `engine.deepcopy` setting now disables deepcopy of State as well as Policy Signals

## [0.7.1] - 2021-06-11
### Added
- Fix for Pathos multiprocessing issue - "NameError: Name '_' is not defined". See https://github.com/uqfoundation/multiprocess/issues/6

## [0.7.0] - 2021-06-09
### Changed
- Experiment and Simulation extend the Executable class (not a breaking change, but significant improvement to API)

## [0.6.7] - 2021-06-08
### Added
- `generate_cartesian_product_parameter_sweep(...)` method to `radcad.utils`

## [0.6.6] - 2021-06-08
### Added
- Base wrapper class

## [0.6.5] - 2021-06-03
### Added
- Iterable Models

## [0.6.4] - 2021-05-31
### Added
- Support for Python 3.9 (<4.0)

## [0.6.3] - 2021-04-30
### Added
- Update dependencies

## [0.6.2] - 2021-04-30
### Added
- Removed Streamlit which requires Python <3.9

## [0.6.1] - 2021-04-30
### Added
- Support for Python 3.9

### Changed
- Added tests for hook functionality, fixed minor error, removed WIP tag
- Updated log statement for "Starting simulation ..."

## [0.6.0] - 2021-02-20
### Changed
- Moved Ray and dependencies to optional extension `extension-backend-ray`
- Refactored `Backend` module
- Introduced idea of extensions

## [0.5.6] - 2021-02-10
### Added
- `drop_substeps` (default False) option to Engine

## [0.5.5] - 2021-02-08
### Changed
- Incorrect argument given to Pathos pool for number of processes
- Update memory benchmarks to not test A/B testing
- Change Python max version from <3.9 to <=3.9
- Update hook API and add subset hook

## [0.5.4] - 2021-02-08
### Added
- Error tracebacks to exceptions data

## [0.5.3] - 2021-02-07
### Changed
- Close Pathos, Multiprocessing pools

## [0.5.2] - 2021-02-06
### Changed
- Pandas version ^1.0.0

## [0.5.1] - 2021-02-06
### Added
- Add hook example for saving experiment results to HDF5 file format

## [0.5.0] - 2021-02-05
### Added
- Predator-prey benchmark test

### Changed
- Refactor core from Rust to Python

## [0.4.1] - 2021-02-02
### Added
- Add engine `deepcopy` option, to disable deepcopy of state

### Changed
- Significant performance tuning of Rust core for 2x increase in speed and reduction in memory use

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
