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
    def _proxy_single_run(run_args):
        return core.multiprocess_wrapper(run_args)
    
    def execute_runs(self):
        ray.init(num_cpus=self.engine.processes, ignore_reinit_error=True)
        futures = [
            ExecutorRay._proxy_single_run.remote(run_args)
            for run_args in self.engine._run_generator
        ]
        return ray.get(futures)

class ExecutorRayRemote(Executor):
    @ray.remote
    def _proxy_single_run(run_args):
        return core.multiprocess_wrapper(run_args)

    def execute_runs(self):
        print(
            "Using Ray remote backend, please ensure you've initialized Ray using ray.init(address=***, ...)"
        )
        futures = [
            ExecutorRayRemote._proxy_single_run.remote(run_args)
            for run_args in self.engine._run_generator
        ]
        return ray.get(futures)
