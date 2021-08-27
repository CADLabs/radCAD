from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

try:
    from cadCAD.engine import ExecutionMode, ExecutionContext
    import cadCAD.engine as _engine
except ImportError:
    _has_cadCAD = False
else:
    _has_cadCAD = True


if not _has_cadCAD:
    raise Exception("Optional compatibility dependency cadCAD not installed")


class Executor(_engine.Executor):
    def execute(self, engine=Engine()):
        simulations = []
        for config in self.configs:
            initial_state = config.initial_state
            state_update_blocks = config.partial_state_update_blocks

            timesteps = max(list(config.sim_config["T"])) + 1
            runs = config.sim_config["N"]
            params = config.sim_config[
                "M"
            ]  # {key: [value] for key, value in config.sim_config['M'].items()}

            model = Model(
                initial_state=initial_state,
                state_update_blocks=state_update_blocks,
                params=params,
            )
            simulation = Simulation(model=model, timesteps=timesteps, runs=1)

            simulations.append(simulation)

        experiment = Experiment(simulations=simulations)
        experiment.engine = engine
        result = experiment.run()
        return result, None, None
