from enum import Enum


class Backend(Enum):
    DEFAULT = 0
    MULTIPROCESSING = 1
    RAY = 2
    RAY_REMOTE = 3
    PATHOS = 4
    SINGLE_PROCESS = 5

class Executor(object):
    def __init__(self, engine):
        self.engine = engine

    def execute_runs(self):
        raise Exception("Backend executor not implemented")
