import os
import sys
import nox

# Select the Python versions to test against (these must be installed on the system)
python_versions = ['3.8', '3.9', '3.10', '3.11', '3.12']

# Configure radCAD for tests
if sys.platform.startswith('win'):
    # Use the multiprocessing backend on Windows to avoid recursion depth errors
    # TODO Remove this once the recursion depth issue is resolved
    # (literal name of Backend.MULTIPROCESSING; avoids importing radcad here)
    os.environ['RADCAD_BACKEND'] = 'MULTIPROCESSING'


def install_dependencies(session):
    '''Install the project and its dependencies into the session venv with uv'''
    session.run(
        'uv', 'sync', '--frozen',
        '--extra', 'compat',
        '--extra', 'extension-backend-ray',
        env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
        external=True,
    )

@nox.session(python=python_versions)
def tests(session):
    install_dependencies(session)
    session.run(
        'pytest',
        # Currently failing on Windows due to recursion depth limit
        # '-n', 'auto',  # Run tests in parallel using pytest-xdist
        'tests',
    )

@nox.session(python=python_versions)
def benchmarks(session):
    install_dependencies(session)
    session.run(
        'pytest',
        'benchmarks/benchmark_radcad.py',
        f'--benchmark-save=py{session.python}',
    )
    session.notify("compare_benchmarks")

@nox.session(python='3.10')
def compare_benchmarks(session):
    install_dependencies(session)
    session.run('pytest-benchmark', 'compare')
