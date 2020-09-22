use pyo3::exceptions::TypeError;
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict, PyList, PyTuple};
use pyo3::wrap_pyfunction;
use std::convert::TryFrom;
use std::collections::HashMap;


#[pymodule]
fn rad_cad(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(run))?;
    m.add_wrapped(wrap_pyfunction!(single_run))?;

    Ok(())
}

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

    let param_sweep = PyList::empty(py);
    let mut max_len = 0;
    
    for value in params.values() {
        if value.len()? > max_len {
            max_len = value.len()?;
        }
    }

    for sweep_index in 0..max_len {
        let param_set = PyDict::new(py);
        for (key, value) in params {
            let param = if sweep_index < value.len()? {
                value.get_item(sweep_index)?
            } else {
                value.get_item(value.len()? - 1)?
            };
            param_set.set_item(key, param)?;
        }
        param_sweep.append(param_set)?;
    }

    for run in 0..runs {
        if param_sweep.len() > 0 {
            for (subset, param_set) in param_sweep.iter().enumerate() {
                result
                    .call_method(
                        "extend",
                        (single_run(
                            timesteps,
                            run,
                            subset,
                            states,
                            psubs,
                            param_set.extract()?,
                        )?,),
                        None,
                    )
                    .unwrap();
            }
        } else {
            result
                .call_method(
                    "extend",
                    (single_run(timesteps, run, 0, states, psubs, params)?,),
                    None,
                )
                .unwrap();
        }
    }
    Ok(result.into())
}

#[pyfunction]
fn single_run(
    timesteps: usize,
    run: usize,
    subset: usize,
    states: &PyDict,
    psubs: &PyList,
    params: &PyDict,
) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();
    let result: &PyList = PyList::empty(py);
    let intial_state: &PyDict = states;
    intial_state.set_item("simulation", 0).unwrap();
    intial_state.set_item("subset", subset).unwrap();
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
        previous_state.set_item("subset", subset).unwrap();
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
