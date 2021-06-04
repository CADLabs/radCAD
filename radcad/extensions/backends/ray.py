try:
    import ray
except ImportError:
    _has_extension = False
else:
    _has_extension = True


if not _has_extension:
    raise Exception("Optional extension dependency Ray not installed")


from radcad.backends import Executor
import radcad.core as core


class ExecutorRay(Executor):
    @ray.remote
    def _proxy_single_run(args):
        return core._single_run_wrapper(args)
    
    def execute_runs(self):
        ray.init(num_cpus=self.engine.processes, ignore_reinit_error=True)
        futures = [
            ExecutorRay._proxy_single_run.remote((config, self.engine.raise_exceptions))
            for config in self.engine._run_generator
        ]
        return ray.get(futures)

class ExecutorRayRemote(Executor):
    @ray.remote
    def _proxy_single_run(args):
        return core._single_run_wrapper(args)

    def execute_runs(self):
        print(
            "Using Ray remote backend, please ensure you've initialized Ray using ray.init(address=***, ...)"
        )
        futures = [
            ExecutorRayRemote._proxy_single_run.remote((config, self.engine.raise_exceptions))
            for config in self.engine._run_generator
        ]
        return ray.get(futures)
