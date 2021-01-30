import streamlit as st

import numpy as np
import pandas as pd
import time
import io

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import streamlit.components.v1 as components


"""
# radCAD Game of Life Demo

See https://github.com/BenSchZA/radCAD/tree/master/examples/game_of_life

Based on [drsfenner.org "Game of Life in Numpy"](http://drsfenner.org/blog/2015/08/game-of-life-in-numpy-2/) and the notebook [http://drsfenner.org/public/notebooks/GameOfLife.ipynb](http://drsfenner.org/public/notebooks/GameOfLife.ipynb).

```python

# radCAD Modules
from radcad import Model, Simulation, Experiment
# from radcad.engine import Engine, Backend

# radCAD Model
from model import loop, state_update_full, state_update_board

...

params = {
    "dims": [len(board.shape)],
    "nd_slice": [nd_slice],
    "ruleOfLifeAlive": [ruleOfLifeAlive],
    "ruleOfLifeDead": [ruleOfLifeDead],
}

initial_state = {
    "full": full,
    "board": board,
}

state_update_blocks = [
    {
        "policies": {"loop": loop},
        "variables": {"full": state_update_full, "board": state_update_board},
    }
]

TIMESTEPS = 100
RUNS = 1

model = Model(
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
    params=params,
)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

result = simulation.run()
```
"""

# radCAD Model
from model import loop, state_update_full, state_update_board

# radCAD Modules
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend


board_size = (50, 50)
nd_slice = (slice(1, -1),) * len(board_size)


def generate_new_board():
    full_size = tuple(i + 2 for i in board_size)
    full = np.zeros(full_size, dtype=np.uint8)
    board = full[nd_slice]
    return full, board


full, board = generate_new_board()

ruleOfLifeAlive = np.zeros(8 + 1, np.uint8)
ruleOfLifeAlive[[2, 3]] = 1

ruleOfLifeDead = np.zeros(8 + 1, np.uint8)
ruleOfLifeDead[3] = 1

params = {
    "dims": [len(board.shape)],
    "nd_slice": [nd_slice],
    "ruleOfLifeAlive": [ruleOfLifeAlive],
    "ruleOfLifeDead": [ruleOfLifeDead],
}

initial_state = {
    "full": full,
    "board": board,
}

state_update_blocks = [
    {
        "policies": {"loop": loop},
        "variables": {"full": state_update_full, "board": state_update_board},
    }
]


TIMESTEPS = 100
RUNS = 1

model = Model(
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
    params=params,
)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)

full, board = generate_new_board()


def cells_to_board(cells):
    string = io.StringIO(cells)

    for row, line in enumerate(string):
        for column, char in enumerate(line):
            if char == 'O':
                board[row, column] = 1

# Source: https://www.conwaylife.com/patterns/gosperglidergun.cells
cells = '''
........................O
......................O.O
............OO......OO............OO
...........O...O....OO............OO
OO........O.....O...OO
OO........O...O.OO....O.O
..........O.....O.......O
...........O...O
............OO
'''

cells_to_board(cells)

model.initial_state = {
    "full": full,
    "board": board,
}
simulation.model = model

if __name__ == "__main__":
    result = simulation.run()

    df = pd.DataFrame(result)
    df

    fig = plt.figure(figsize=(8, 8))
    fig.set_tight_layout(True)
    fig = plt.figure()

    state = df.iloc[0]
    im = plt.imshow(state["board"], cmap="binary", interpolation="none")
    plt.axis("off")

    def animate_func(timestep):
        state = df.iloc[timestep]
        im.set_array(state["board"])
        return [im]

    anim = animation.FuncAnimation(
        fig,
        animate_func,
        frames=TIMESTEPS,
        interval=100,  # in ms
    )

    components.html(anim.to_jshtml(), height=800)
