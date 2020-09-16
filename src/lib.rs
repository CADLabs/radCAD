use pyo3::prelude::*;
use pyo3::{wrap_pyfunction, wrap_pymodule};
// use pyo3::types::{IntoPyDict, PyDict};
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
fn run(timesteps: usize, states: &PyAny, psubs: &PyAny) -> PyResult<Vec<HashMap<String, f64>>> {
    let mut result: Vec<HashMap<String, f64>> = Vec::with_capacity(timesteps + 1);
    let intial_state: HashMap<String, f64> = states.extract()?;
    result.push(intial_state);
    let psubs_: &Vec<HashMap<String, HashMap<String, &PyAny>>> = &psubs.extract()?;
    for _timestep in 0..timesteps {
        let previous_state: &HashMap<String, f64> = result.last().unwrap();
        let mut next_state: HashMap<String, f64> = previous_state.clone();
        for psub in psubs_ {
            match psub.get("updates") {
                None => println!("No such key \"updates\""),
                Some(updates) => {
                    // for (state, value) in next_state.iter_mut() {
                    //     *value = updates.get(state).unwrap().call((previous_state.clone(),), None)?.extract()?;
                    // }
                    for (state, function) in updates {
                        *next_state.get_mut(state).unwrap() = function.call((previous_state.clone(),), None)?.extract()?;
                    }
                }
            }
        }
        result.push(next_state);
    }
    Ok(result)
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
