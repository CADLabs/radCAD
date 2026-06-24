"""Parallel-processing backends that execute simulation runs.

A backend determines *how* the independent units of work produced by the
[Engine][radcad.engine.Engine] are executed: in a single process, across local
CPU cores, or on a remote cluster. Select one via the
[Engine][radcad.engine.Engine] ``backend`` option or the ``RADCAD_BACKEND``
environment variable.
"""

from enum import Enum


class Backend(Enum):
    """Available execution backends.

    - ``DEFAULT``: alias for ``PATHOS``.
    - ``PATHOS``: local multiprocessing via ``pathos`` (dill-based pickling).
    - ``MULTIPROCESSING``: local multiprocessing via the standard library.
    - ``RAY``: local execution via Ray.
    - ``RAY_REMOTE``: distributed execution on a remote Ray cluster.
    - ``SINGLE_PROCESS``: no parallelisation; useful for debugging.
    """

    DEFAULT = 0
    MULTIPROCESSING = 1
    RAY = 2
    RAY_REMOTE = 3
    PATHOS = 4
    SINGLE_PROCESS = 5

class Executor(object):
    """Abstract base for backend executors.

    Subclasses implement `execute_runs` to consume the engine's run
    generator and return a list of ``(result, exception)`` tuples.
    """

    def __init__(self, engine):
        self.engine = engine

    def execute_runs(self):
        """Execute every run from the engine's generator. Implemented by subclasses."""
        raise Exception("Backend executor not implemented")
