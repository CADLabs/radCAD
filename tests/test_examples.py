import pytest
import os

def check_notebook(notebook):
    result = os.popen(f"jupyter nbconvert --to script --execute --stdout {notebook} | ipython").read()
    return "1" in result

def test_game_of_life():
    assert check_notebook("examples/game-of-life/game-of-life.ipynb")

def test_predator_prey():
    assert check_notebook("examples/predator-prey/predator-prey.ipynb")

def test_predator_prey_abm():
    assert check_notebook("examples/predator-prey-abm/predator-prey-abm.ipynb")
