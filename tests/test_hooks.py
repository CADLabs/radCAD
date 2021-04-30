from radcad import Model, Simulation, Experiment
from tests.test_cases import basic


def test_hooks(capsys):
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = params = {
        'a': [1,2],
        'b': [1]
    }
    TIMESTEPS = 1
    RUNS = 2

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation, simulation])

    experiment.before_experiment = lambda experiment=None: print(f'before_experiment')
    experiment.before_simulation = lambda simulation=None: print(f'before_simulation {simulation.index}')
    experiment.before_run = lambda context=None: print(f'before_run {context.run}')
    experiment.before_subset = lambda context=None: print(f'before_subset {context.subset}')
    experiment.after_subset = lambda context=None: print(f'after_subset {context.subset}')
    experiment.after_run = lambda context=None: print(f'after_run {context.run}')
    experiment.after_simulation = lambda simulation=None: print(f'after_simulation {simulation.index}')
    experiment.after_experiment = lambda experiment=None: print(f'after_experiment')

    raw_result = experiment.run()
    captured = capsys.readouterr()

    assert captured.out.replace('\n', '').replace(' ', '') == """
    before_experiment
    before_simulation 0
    before_run 0
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 0
    before_run 1
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 1
    after_simulation 0
    before_simulation 1
    before_run 0
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 0
    before_run 1
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 1
    after_simulation 1
    after_experiment
    """.replace('\n', '').replace(' ', '')
