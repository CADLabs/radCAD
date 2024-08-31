import os
import sys
import threading
import nox

# Ensure the Nox virtualenv is used instead of PDM's
os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})

# Select the Python versions to test against (these must be installed on the system)
python_versions = ['3.8', '3.9', '3.10', '3.11', '3.12']

# Set the platform's hard recursion limit to avoid recursion depth errors on Windows
# See https://stackoverflow.com/questions/2917210/what-is-the-hard-recursion-limit-for-linux-mac-and-windows
threading.stack_size(67108864) # 64MB stack, this limit is hit first in practice
sys.setrecursionlimit(2**20) # Arbitrarily high limit, the stack limit is hit first

# Only new threads get the redefined stack size
# thread = threading.Thread(func=main)
# thread.start()

# Configure radCAD for tests
if sys.platform.startswith('win'):
    # Use the multiprocessing backend on Windows to avoid recursion depth errors
    os.environ['RADCAD_BACKEND'] = 'multiprocessing'


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
