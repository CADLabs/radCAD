from radcad.backends import Executor
import radcad.core as core


class ExecutorSingleProcess(Executor):
    def execute_runs(self):
        result = [
            core._single_run_wrapper((config, self.engine.raise_exceptions))
            for config in self.engine._run_generator
        ]
        return result
