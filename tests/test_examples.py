import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


NOTEBOOK_TIMEOUT_SECONDS = 180


def _tail(text, limit=4000):
    if isinstance(text, bytes):
        text = text.decode(errors="replace")
    return text[-limit:] if text else ""


def check_notebook(notebook):
    notebook = Path(notebook)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        work_dir = temp_dir / notebook.parent.name
        shutil.copytree(notebook.parent, work_dir)
        output_dir = temp_dir / "executed"
        output_dir.mkdir()
        notebook = work_dir / notebook.name

        env = os.environ.copy()
        # Force notebooks to single-process execution. Windows multiprocessing
        # spawn cannot import notebook-defined functions, and PATHOS/dill has
        # historically hit recursion/stack limits with notebook globals on CI.
        env["RADCAD_BACKEND"] = "SINGLE_PROCESS"
        command = [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            f"--ExecutePreprocessor.timeout={NOTEBOOK_TIMEOUT_SECONDS}",
            "--ExecutePreprocessor.kernel_name=python3",
            "--output-dir",
            output_dir,
            str(notebook),
        ]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=NOTEBOOK_TIMEOUT_SECONDS,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            pytest.fail(
                f"Notebook timed out after {NOTEBOOK_TIMEOUT_SECONDS}s: {notebook}\n"
                f"stdout:\n{_tail(exc.stdout)}\n"
                f"stderr:\n{_tail(exc.stderr)}"
            )

    assert result.returncode == 0, (
        f"Notebook failed: {notebook}\n"
        f"stdout:\n{_tail(result.stdout)}\n"
        f"stderr:\n{_tail(result.stderr)}"
    )


def test_game_of_life():
    check_notebook("examples/game_of_life/game-of-life.ipynb")


def test_predator_prey_sd():
    check_notebook("examples/predator_prey_sd/predator-prey-sd.ipynb")


def test_predator_prey_abm():
    check_notebook("examples/predator_prey_abm/predator-prey-abm.ipynb")


def test_harmonic_oscillator():
    check_notebook("examples/harmonic_oscillator/harmonic_oscillator.ipynb")
