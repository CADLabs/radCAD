import os
import nox

# Select the Python versions to test against (these must be installed on the system)
python_versions = ['3.10', '3.11', '3.12']

def install_dependencies(session):
    '''Install the project and its dependencies into the session venv with uv'''
    venv = os.path.abspath(session.virtualenv.location)
    session.run(
        'uv', 'sync', '--frozen',
        '--python', session.python,
        '--extra', 'compat',
        '--extra', 'extension-backend-ray',
        env={'UV_PROJECT_ENVIRONMENT': venv, 'VIRTUAL_ENV': venv},
        external=True,
    )

@nox.session(python=python_versions)
def tests(session):
    install_dependencies(session)
    session.run(
        'python', '-m', 'pytest',
        # Currently failing on Windows due to recursion depth limit
        # '-n', 'auto',  # Run tests in parallel using pytest-xdist
        'tests',
    )

@nox.session(python=python_versions)
def benchmarks(session):
    install_dependencies(session)
    session.run(
        'python', '-m', 'pytest',
        'benchmarks/benchmark_radcad.py',
        f'--benchmark-save=py{session.python}',
    )
    session.notify("compare_benchmarks")

@nox.session(python='3.10')
def compare_benchmarks(session):
    install_dependencies(session)
    session.run('pytest-benchmark', 'compare')
