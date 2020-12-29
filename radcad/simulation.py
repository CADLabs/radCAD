from radcad.experiment import Experiment
from radcad.core import Simulation as CoreSimulation
from radcad.engine import Engine


class Simulation(CoreSimulation):

    def __init__(self, **kwargs):
        self.model = kwargs.pop('model', None)
        self.timesteps = kwargs.pop('timesteps', 100)
        self.runs = kwargs.pop('runs', 1)
        self.engine = kwargs.pop('engine', Engine())

        if kwargs:
            raise Exception(f"Invalid Simulation option in {kwargs}")

    def run(self):
        return self.engine._run(experiment=Experiment(self))
