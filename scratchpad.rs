use rustpython_compiler as compiler;
use rustpython_vm as vm;

use inline_python::python;

use rayon::prelude::*;
use num::Float;

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

fn python_vm(code: String) -> vm::pyobject::PyResult<PyObject> {
    let vm = vm::VirtualMachine::new(vm::PySettings::default());

    let scope = vm.new_scope_with_builtins();

    let code_obj = vm
        .compile(
            r#"{code}"#,
            compiler::compile::Mode::Exec,
            "<embedded>".to_owned(),
        )
        .map_err(|err| vm.new_syntax_error(&err))?;

    let res: vm::pyobject::PyResult = vm.run_code_obj(code_obj, scope)?;

    vm.unwrap_pyresult(res)
}

let c: Context = python! {
    params = 'params
    substep = 'substep
    state_history = 'result
    previous_state = 'substate
    policy_input = 'policy_results
};
c.run(python! {
    r#"{'function}"#
})