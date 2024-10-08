import os
import sys
import nox
from radcad import Backend

# Ensure the Nox virtualenv is used instead of PDM's
os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})

# Select the Python versions to test against (these must be installed on the system)
python_versions = ['3.8', '3.9', '3.10', '3.11', '3.12']

# Configure radCAD for tests
if sys.platform.startswith('win'):
    # Use the multiprocessing backend on Windows to avoid recursion depth errors
    # TODO Remove this once the recursion depth issue is resolved
    os.environ['RADCAD_BACKEND'] = Backend.MULTIPROCESSING.name


def select_lockfile(session):
    '''Select the PDM package manager lockfile based on the Python version'''
    if session.python == '3.8':
        return 'pdm-py38.lock'
    return 'pdm.lock'

def install_dependencies(session):
    '''Install the dependencies for the current Python version'''
    lockfile = select_lockfile(session)
    session.install('pdm')  # 'pytest-xdist', 'pytest-benchmark'
    session.run_always(
        'pdm', 'sync', '-d',
        '-G', 'compat',
        '-G', 'extension-backend-ray',
        '--lockfile', lockfile,
    )

@nox.session(python=python_versions)
def tests(session):
    install_dependencies(session)
    session.run(
        'pdm', 'run', 'pytest',
        # Currently failing on Windows due to recursion depth limit
        # '-n', 'auto',  # Run tests in parallel using pytest-xdist
        'tests'
    )

@nox.session(python=python_versions)
def benchmarks(session):
    install_dependencies(session)
    session.run(
        'pdm', 'run', 'pytest',
        'benchmarks/benchmark_radcad.py',
        f'--benchmark-save=py{session.python}',
    )
    session.notify("compare_benchmarks")

@nox.session(python='3.10')
def compare_benchmarks(session):
    install_dependencies(session)
    session.run('pdm', 'run', 'pytest-benchmark', 'compare')
