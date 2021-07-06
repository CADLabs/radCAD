from radcad.backends import Executor
import radcad.core as core

# Pathos re-writes the core code in Python rather than C, for ease of maintenance at cost of performance
from pathos.multiprocessing import ProcessPool
import os


class ExecutorPathos(Executor):
    def __init__(self, engine):
        super().__init__(engine=engine)

        # Checks if Windows, then fixes issue - "NameError: Name '_' is not defined"
        # See https://github.com/uqfoundation/multiprocess/issues/6
        if os.name == 'nt':
            import dill
            dill.settings['recurse'] = True

    def execute_runs(self):
        with ProcessPool(self.engine.processes) as pool:
            result = pool.map(
                core._single_run_wrapper,
                [
                    (config, self.engine.raise_exceptions)
                    for config in self.engine._run_generator
                ],
            )
            pool.close()
            pool.join()
            pool.clear()
        return result
