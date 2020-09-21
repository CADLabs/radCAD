use pyo3::exceptions::TypeError;
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict, PyList, PyTuple};
use pyo3::wrap_pyfunction;
use std::convert::TryFrom;

// use rustpython_compiler as compiler;
// use rustpython_vm as vm;

// use inline_python::python;

use std::collections::HashMap;
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

// fn python_vm(code: String) -> vm::pyobject::PyResult<PyObject> {
//     let vm = vm::VirtualMachine::new(vm::PySettings::default());

//     let scope = vm.new_scope_with_builtins();

//     let code_obj = vm
//         .compile(
//             r#"{code}"#,
//             compiler::compile::Mode::Exec,
//             "<embedded>".to_owned(),
//         )
//         .map_err(|err| vm.new_syntax_error(&err))?;

//     let res: vm::pyobject::PyResult = vm.run_code_obj(code_obj, scope)?;

//     vm.unwrap_pyresult(res)
// }

// let c: Context = python! {
//     params = 'params
//     substep = 'substep
//     state_history = 'result
//     previous_state = 'substate
//     policy_input = 'policy_results
// };
// c.run(python! {
//     r#"{'function}"#
// })

#[pyfunction]
fn run(
    timesteps: usize,
    runs: usize,
    states: &PyDict,
    psubs: &PyList,
    params: &PyDict,
) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();
    let result: &PyList = PyList::empty(py);
    for run in 0..runs {
        result
            .call_method(
                "extend",
                (single_run(timesteps, run, states, psubs, params)?,),
                None,
            )
            .unwrap();
    }
    Ok(result.into())
}

fn reduce_signals(
    params: &PyDict,
    substep: usize,
    result: &PyList,
    substate: &PyDict,
    psub: &PyDict,
) -> HashMap<String, f64> {
    let mut policy_results = Vec::<HashMap<String, f64>>::with_capacity(psub.len());
    for (_var, function) in psub
        .get_item("policies")
        .expect("Get policies failed")
        .cast_as::<PyDict>()
        .expect("Get policies failed")
    {
        policy_results.push(
            function
                .call((params, substep, result, substate.copy().unwrap()), None)
                .unwrap()
                .extract()
                .unwrap(),
        );
    }

    match policy_results.len() {
        0 => HashMap::new(),
        1 => policy_results.last().unwrap().clone(),
        _ => policy_results
            .iter_mut()
            .fold(HashMap::new(), |mut acc, a| {
                for (key, value) in a {
                    match acc.get_mut(&key.to_string()) {
                        Some(value_) => {
                            *value_ += *value;
                        }
                        None => {
                            acc.insert(key.to_string(), *value);
                        }
                    }
                }
                acc
            }),
    }
}

#[pyfunction]
fn single_run(
    timesteps: usize,
    run: usize,
    states: &PyDict,
    psubs: &PyList,
    params: &PyDict,
) -> PyResult<PyObject> {
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
        let previous_state: &PyDict = result
            .get_item(isize::try_from(result.len() - 1).expect("Failed to fetch previous state"))
            .cast_as::<PyDict>()?
            .copy()?;
        previous_state.set_item("simulation", 0).unwrap();
        previous_state.set_item("subset", 0).unwrap();
        previous_state.set_item("run", run + 1).unwrap();
        previous_state.set_item("timestep", timestep + 1).unwrap();
        let substeps: &PyList = PyList::empty(py);
        for (substep, psub) in psubs.into_iter().enumerate() {
            let substate: &PyDict = match substep {
                0 => previous_state.cast_as::<PyDict>()?.copy()?,
                _ => substeps
                    .get_item(isize::try_from(substep - 1).expect("Failed to fetch substate"))
                    .cast_as::<PyDict>()?
                    .copy()?,
            };
            substate.set_item("substep", substep + 1).unwrap();
            for (state, function) in psub
                .get_item("variables")
                .expect("Get variables failed")
                .cast_as::<PyDict>()
                .expect("Get variables failed")
            {
                let state_update: &PyTuple = match function.is_callable() {
                    true => function
                        .call(
                            (
                                params,
                                substep,
                                result,
                                substate,
                                reduce_signals(
                                    params,
                                    substep,
                                    result,
                                    substate,
                                    psub.cast_as::<PyDict>()?,
                                )
                                .into_py_dict(py)
                                .clone(),
                            ),
                            None,
                        )?
                        .extract()?,
                    false => {
                        return Err(PyErr::new::<TypeError, _>(
                            "State update function is not callable",
                        ));
                    }
                };
                let state_key = state_update.get_item(0);
                let state_value = state_update.get_item(1);
                match state == state_key {
                    true => substate.set_item(state_key, state_value).unwrap(),
                    false => {
                        return Err(PyErr::new::<TypeError, _>(
                            "PSUB state key doesn't match function state key",
                        ))
                    }
                }
            }
            substeps
                .insert(
                    isize::try_from(substep).expect("Failed to insert substep"),
                    substate,
                )
                .unwrap();
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
