from radcad import Model, Simulation, Experiment, Context
from tests.test_cases import basic
import pandas as pd
from pandas._testing import assert_series_equal


def test_hooks(capsys):
    states = basic.states
    state_update_blocks = basic.state_update_blocks
    params = {
        'a': [1,2],
        'b': [1]
    }
    TIMESTEPS = 1
    RUNS = 2

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation, simulation])

    experiment.before_experiment = lambda experiment=None: print(f'before_experiment')
    experiment.before_simulation = lambda context=None: print(f'before_simulation {context.simulation}')
    experiment.before_run = lambda context=None: print(f'before_run {context.run}')
    experiment.before_subset = lambda context=None: print(f'before_subset {context.subset}')
    experiment.after_subset = lambda context=None: print(f'after_subset {context.subset}')
    experiment.after_run = lambda context=None: print(f'after_run {context.run}')
    experiment.after_simulation = lambda context=None: print(f'after_simulation {context.simulation}')
    experiment.after_experiment = lambda experiment=None: print(f'after_experiment')

    experiment.run()
    captured = capsys.readouterr()

    assert captured.out.replace('\n', '').replace(' ', '') == """
    before_experiment
    before_simulation 0
    before_run 1
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 1
    before_run 2
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 2
    after_simulation 0
    before_simulation 1
    before_run 1
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 1
    before_run 2
    before_subset 0
    after_subset 0
    before_subset 1
    after_subset 1
    after_run 2
    after_simulation 1
    after_experiment
    """.replace('\n', '').replace(' ', '')


def test_hook_set_timesteps():
    states = basic.states
    state_update_blocks = []
    params = {}
    TIMESTEPS = 0
    RUNS = 1

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params=params)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation, simulation])

    def set_timesteps(context: Context):
        context.timesteps = (context.simulation + 1) * 10

    experiment.before_run = set_timesteps

    results = experiment.run()

    # 10 * 1 + (1) + 10 * 2 + (1) == 32
    assert len(results) == 32

def test_hook_set_state_update_blocks():
    def update_a_v1(params, substep, state_history, previous_state, policy_input):
        return 'a', 1

    def update_a_v2(params, substep, state_history, previous_state, policy_input):
        return 'a', 2

    states = {
        'a': 0
    }
    state_update_blocks = [{
        'policies': {},
        'variables': {}
    }]
    TIMESTEPS = 10
    RUNS = 1

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params={})
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation, simulation])

    def set_state_update_blocks(context: Context):
        if context.simulation == 0:
            context.state_update_blocks[0]['variables'] = {'a': update_a_v1}
        else:
            context.state_update_blocks[0]['variables'] = {'a': update_a_v2}

    experiment.before_simulation = set_state_update_blocks

    results = experiment.run()
    df = pd.DataFrame(results)

    assert df.query('simulation == 0')['a'].iloc[-1] == 1
    assert df.query('simulation == 1')['a'].iloc[-1] == 2


def test_hook_set_initial_state():
    states = {
        'a': 1
    }
    state_update_blocks = [{
        'policies': {},
        'variables': {}
    }]
    TIMESTEPS = 10
    RUNS = 5

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params={})
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation, simulation])

    def set_initial_state(context: Context):
        context.initial_state['a'] = context.run

    experiment.before_subset = set_initial_state

    results = experiment.run()
    df = pd.DataFrame(results)

    assert (df['a'] == df['run']).all()


def test_hook_experiment_override():
    states = {
        'a': 1
    }
    state_update_blocks = [{
        'policies': {},
        'variables': {}
    }]
    TIMESTEPS = 10
    RUNS = 5

    model = Model(initial_state=states, state_update_blocks=state_update_blocks, params={})
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
    experiment = Experiment(simulations=[simulation, simulation])

    def set_initial_state_a(context: Context):
        context.initial_state['a'] = 1

    def set_initial_state_b(context: Context):
        context.initial_state['a'] = 2

    simulation.before_subset = set_initial_state_a
    experiment.before_subset = set_initial_state_b

    results_b = experiment.run()
    df_b = pd.DataFrame(results_b)

    assert (df_b['a'] == 2).all()

    results_a = simulation.run()
    df_a = pd.DataFrame(results_a)

    assert (df_a['a'] == 1).all()
