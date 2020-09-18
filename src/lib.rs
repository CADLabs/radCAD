use pyo3::prelude::*;
use pyo3::{wrap_pyfunction, wrap_pymodule};
use pyo3::types::{PyIterator, IntoPyDict, PyDict, PyList};
use std::collections::HashMap;
use rayon::prelude::*;
// use num::Float;


#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn py_dict() -> PyResult<HashMap<String, i32>> {
    let mut result = HashMap::new();
    result.insert("a".to_string(), 1);
    Ok(result)
}

#[pyfunction]
fn state_update(func: &PyAny) -> PyResult<(String, i64)> {
    let result: i64 = func.call(("Hello, world!",), None)?.extract()?;
    Ok(("yay".to_string(), result))
}

#[pymodule]
fn wrapper(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(state_update))?;
    Ok(())
}

#[pyfunction]
fn print_psubs(psubs: &PyAny) -> PyResult<()> {
    print!("{}", psubs.str().unwrap());
    Ok(())
}

#[pyfunction]
fn run(timesteps: usize, states: &PyDict, psubs: &PyList) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();
    let result: &PyList = PyList::empty(py);
    let intial_state: &PyDict = states;
    result.append(intial_state);
    for timestep in 0..timesteps {
        let previous_state: &PyDict = result.get_item(timestep as isize).extract()?;
        let next_state: &PyDict = previous_state.copy().unwrap();
        for psub in psubs {
            match psub.get_item("updates") {
                Err(_e) => println!("No such key \"updates\""),
                Ok(updates_) => {
                    let updates: &PyDict = updates_.extract()?;
                    for (state, function) in updates {
                        next_state.set_item(state, function.call((next_state,), None)?);
                    }
                }
            }
        }
        result.append(next_state);
    }
    Ok(result.into())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rad_cad(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pymodule!(wrapper))?;

    m.add_wrapped(wrap_pyfunction!(sum_as_string))?;
    m.add_wrapped(wrap_pyfunction!(py_dict))?;
    m.add_wrapped(wrap_pyfunction!(print_psubs))?;
    m.add_wrapped(wrap_pyfunction!(run))?;

    Ok(())
}
