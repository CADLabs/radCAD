import pytest
import os

def check_notebook(notebook):
    result = os.popen(f"jupyter nbconvert --to script --execute --stdout {notebook} | ipython").read()
    return "1" in result

def test_game_of_life():
    assert check_notebook("examples/game_of_life/game-of-life.ipynb")

def test_predator_prey_sd():
    assert check_notebook("examples/predator_prey_sd/predator-prey-sd.ipynb")

def test_predator_prey_abm():
    assert check_notebook("examples/predator_prey_abm/predator-prey-abm.ipynb")

def test_harmonic_oscillator():
    assert check_notebook("examples/harmonic_oscillator/harmonic_oscillator.ipynb")

