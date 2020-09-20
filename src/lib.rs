use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::{wrap_pyfunction};
// use std::collections::HashMap;
// use rayon::prelude::*;
// use num::Float;

// #[pyfunction]
// fn state_update(func: &PyAny) -> PyResult<(String, i64)> {
//     let result: i64 = func.call(("Hello, world!",), None)?.extract()?;
//     Ok(("yay".to_string(), result))
// }

// #[pymodule]
// fn wrapper(_py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_wrapped(wrap_pyfunction!(state_update))?;
//     Ok(())
// }

// [{'a': 1.0,
//   'b': 2.0,
//   'simulation': 0,
//   'subset': 0,
//   'run': 1,
//   'substep': 0,
//   'timestep': 0},

#[pyfunction]
fn run(timesteps: usize, runs: usize, states: &PyDict, psubs: &PyList) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();
    let result: &PyList = PyList::empty(py);
    for run in 0..runs {
        result
            .call_method(
                "extend",
                (single_run(timesteps, run, states, psubs)?,),
                None,
            )
            .unwrap();
    }
    Ok(result.into())
}

#[pyfunction]
fn single_run(timesteps: usize, run: usize, states: &PyDict, psubs: &PyList) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();
    let result: &PyList = PyList::empty(py);
    let intial_state: &PyDict = states;
    intial_state.set_item("simulation", 0).unwrap();
    intial_state.set_item("subset", 0).unwrap();
    intial_state.set_item("run", run + 1).unwrap();
    intial_state.set_item("substep", 0).unwrap();
    intial_state.set_item("timestep", 0).unwrap();
    result.append(intial_state.copy()?).unwrap();
    for timestep in 0..timesteps {
        let previous_state: &PyDict = result.get_item(result.len() as isize - 1).cast_as::<PyDict>()?.copy()?;
        previous_state.set_item("simulation", 0).unwrap();
        previous_state.set_item("subset", 0).unwrap();
        previous_state.set_item("run", run + 1).unwrap();
        previous_state.set_item("timestep", timestep + 1).unwrap();
        let substeps: &PyList = PyList::empty(py);
        for (substep, psub) in psubs.into_iter().enumerate() {
            let substate: &PyDict = match substep {
                0 => previous_state.cast_as::<PyDict>()?.copy()?,
                _ => substeps.get_item(substep as isize - 1).cast_as::<PyDict>()?.copy()?,
            };
            substate.set_item("substep", substep + 1).unwrap();
            for (state, function) in psub.get_item("variables")?.cast_as::<PyDict>()? {
                substate
                    .set_item(state, function.call((substate,), None)?)
                    .unwrap();
            }
            substeps.insert(substep as isize, substate).unwrap();
        }
        result.call_method("extend", (substeps,), None).unwrap();
    }
    Ok(result.into())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rad_cad(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_wrapped(wrap_pymodule!(wrapper))?;
    m.add_wrapped(wrap_pyfunction!(run))?;
    m.add_wrapped(wrap_pyfunction!(single_run))?;

    Ok(())
}
