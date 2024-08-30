import os
import nox

# Ensure the Nox virtualenv is used instead of PDM's
os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
# os.environ.pop("VIRTUAL_ENV", None)
# os.environ.pop("PYTHONPATH", None)

# Select the Python versions to test against (these must be installed on the system)
python_versions = ['3.8', '3.9', '3.10', '3.11', '3.12']


def select_lockfile(session):
    '''Select the PDM package manager lockfile based on the Python version'''
    if session.python == '3.8':
        return 'pdm-py38.lock'
    return 'pdm.lock'

def install_dependencies(session):
    '''Install the dependencies for the current Python version'''
    lockfile = select_lockfile(session)
    session.install('pdm')
    session.run_always(
        'pdm', 'sync', '-d',
        '-G', 'compat',
        '-G', 'extension-backend-ray',
        '--lockfile', lockfile,
    )

@nox.session(python=python_versions)
def tests(session):
    install_dependencies(session)
    session.run('pdm', 'run', 'pytest', 'tests')

@nox.session(python=python_versions)
def benchmarks(session):
    install_dependencies(session)
    session.run('pdm', 'run', 'pytest',
        'benchmarks/benchmark_radcad.py',
        f'--benchmark-save=py{session.python}',
    )
    session.notify("compare_benchmarks")

@nox.session(python='3.10')
def compare_benchmarks(session):
    install_dependencies(session)
    session.run('pdm', 'run', 'pytest-benchmark', 'compare')
