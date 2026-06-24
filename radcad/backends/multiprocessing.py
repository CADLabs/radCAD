from radcad.backends import Executor
import radcad.core as core

import multiprocessing


class ExecutorMultiprocessing(Executor):
    """Run simulations across local CPU cores using the standard ``multiprocessing`` library.

    Uses a ``spawn`` context for cross-platform consistency. Functions must be
    standard-library picklable; use the ``pathos`` backend for closures/lambdas.
    """

    def execute_runs(self):
        with multiprocessing.get_context("spawn").Pool(
                processes=self.engine.processes
            ) as pool:
            result = pool.map(
                core.multiprocess_wrapper,
                self.engine._run_generator,
            )
            pool.close()
            pool.join()
        return result
