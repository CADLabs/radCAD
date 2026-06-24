from radcad.backends import Executor
import radcad.core as core


class ExecutorSingleProcess(Executor):
    """Run every simulation sequentially in the current process (no parallelism)."""

    def execute_runs(self):
        result = [
            core.multiprocess_wrapper(simulation_execution)
            for simulation_execution in self.engine._run_generator
        ]
        return result
