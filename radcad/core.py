"""The core simulation loop that evaluates a single run of a model.

A [SimulationExecution][radcad.core.SimulationExecution] represents one fully-specified unit of work, a
single run of a single parameter subset. Stepping through it produces the raw
simulation result. The [Engine][radcad.engine.Engine] creates one of these per
run/subset and hands it to a backend, which calls [multiprocess_wrapper][radcad.core.multiprocess_wrapper]
to execute it (with exception handling) in a worker process.

Most models never touch this module directly; it is documented here because its
state-transition logic defines radCAD's execution semantics.
"""

import logging
import pickle
import traceback
import sys
import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from typing import Any, List

from radcad.types import (PolicySignal, SimulationResults, StateUpdate,
                          StateUpdateBlock, StateUpdateResult, StateVariables,
                          SystemParameters)
from radcad.utils import default


@dataclass
class SimulationExecutionSpecification(ABC):
    """Abstract template for the simulation loop, independent of state semantics.

    Defines the nested execution structure (execution > timestep > substep) as
    a sequence of overridable hook methods (``before_step``, ``substep``,
    ``after_step``, ...). [SimulationExecution][radcad.core.SimulationExecution] implements these hooks
    with radCAD's concrete state-transition behaviour. Separating the two
    makes the loop structure explicit and the behaviour easy to customise.
    """

    timesteps: int = 0
    timestep: int = None

    substep_index: int = 0
    substeps: List = default([])

    state_update_blocks: List[StateUpdateBlock] = default([])
    result: SimulationResults = default([])

    def execute(
        self,
    ) -> SimulationResults:
        """Run the full simulation loop and return the accumulated result.

        Calls `before_execution`, iterates over each timestep (which in
        turn iterates over substeps via `step`), then
        `after_execution`.

        Returns:
            SimulationResults: The per-timestep, per-substep state history.
        """
        self.before_execution()

        initial_timestep = self.timestep if self.timestep else 0
        for timestep in range(initial_timestep, initial_timestep + self.timesteps):
            self.timestep = timestep
            self.before_step()
            self.step()
            self.after_step()

        self.after_execution()
        return self.result

    @abstractmethod
    def before_execution(self) -> None:
        pass

    @abstractmethod
    def before_step(self) -> None:
        pass

    def step(self) -> None:
        """Advance the system by one timestep, evaluating every substep.

        Each Partial State Update Block in ``state_update_blocks`` is one
        substep; they are evaluated in order, each building on the previous.
        """
        self.substeps: List = []
        for (substep, state_update_block) in enumerate(self.state_update_blocks):
            self.substep_index = substep
            self.before_substep()
            self.substep(state_update_block)
            self.after_substep()

    @abstractmethod
    def before_substep(self) -> None:
        pass

    @abstractmethod
    def substep(self, state_update_block: StateUpdateBlock) -> List[StateVariables]:
        pass

    @abstractmethod
    def after_substep(self) -> None:
        pass

    @abstractmethod
    def after_step(self) -> None:
        pass

    @abstractmethod
    def after_execution(self) -> None:
        pass


@dataclass
class SimulationExecution(SimulationExecutionSpecification):
    """One executable run of a model: a single run of a single parameter subset.

    Implements radCAD's state-transition semantics on top of
    [SimulationExecutionSpecification][radcad.core.SimulationExecutionSpecification]. For each substep it executes the
    block's Policy Functions, aggregates their signals, applies the State
    Update Functions, and appends the new state to the result. Execution
    options such as `enable_deepcopy`, `drop_substeps`, and
    `raise_exceptions` control performance and error behaviour.

    Subclass it and override `deepcopy_method` (or other methods) to
    customise execution; see the README for an example.
    """

    # Simulation settings
    initial_state: StateVariables = default({})
    params: SystemParameters = default({})

    # Execution settings
    enable_deepcopy: bool = True
    drop_substeps: bool = False
    raise_exceptions: bool = True
    logger = logging.getLogger("radCAD")
    """Use "radCAD" logging instance to avoid conflict with other projects"""

    # Simulation indices
    simulation_index: int = 0
    run_index: int = 1
    subset_index: int = 0
    """
    Index starts at +1 to remain compatible with cadCAD implementation
    """

    # Simulation runtime state
    previous_state: StateVariables = None

    def before_execution(self) -> None:
        self.logger.info(f"Starting simulation {self.simulation_index} / run {self.run_index} / subset {self.subset_index}")
        self.initialise_state()

    def initialise_state(self):
        """Stamp bookkeeping keys onto the initial state and seed the result.

        Sets the ``simulation``/``subset``/``run``/``substep``/``timestep``
        keys and appends the initial state as the first entry of the result.
        """
        self.initial_state["simulation"] = self.simulation_index
        self.initial_state["subset"] = self.subset_index
        self.initial_state["run"] = self.run_index
        self.initial_state["substep"] = 0
        # If first timestep is not explicitely set in initial state, start from zero
        # Needed to properly handle model generator
        if not "timestep" in self.initial_state:
            self.initial_state["timestep"] = 0
        assert (
            isinstance(self.initial_state["timestep"], int) and self.initial_state["timestep"] >= 0
        ), f"Simulation initial timestep should be a positive integer, not {self.initial_state['timestep']}"
        self.timestep = self.initial_state["timestep"]
        self.result.append([self.initial_state])

    def before_step(self) -> None:
        self.previous_state: StateVariables = (
            self.result[0][0].copy()
            if len(self.result) == 1
            else self.result[-1][-1:][0].copy()
        )

    def before_substep(self) -> None:
        pass

    def substep(self, state_update_block: StateUpdateBlock) -> None:
        """Evaluate a single Partial State Update Block.

        Runs the block's policies to produce aggregated signals, applies each
        State Update Function to compute the new State Variable values, and
        records the resulting substate.
        """
        substate: StateVariables = (
            self.previous_state.copy() if self.substep_index == 0 else self.substeps[self.substep_index - 1].copy()
        )

        signals: PolicySignal = self.execute_policies(substate, state_update_block)

        updated_state: StateVariables = dict([
            self.update_state(substate, signals, state_update)
            for state_update in state_update_block["variables"].items()
        ])
        self.process_substep(substate, updated_state)

    def process_substep(self, substate: StateVariables, updated_state: StateVariables) -> None:
        substate.update(updated_state)
        substate["timestep"] = (self.previous_state["timestep"] + 1) if self.timestep == 0 else self.timestep + 1
        substate["substep"] = self.substep_index + 1
        self.substeps.append(substate)

    def after_substep(self) -> None:
        pass

    def after_step(self) -> None:
        substeps = self.substeps or [self.previous_state.copy()]
        self.result.append(substeps if not self.drop_substeps else [substeps.pop()])

    def after_execution(self) -> None:
        pass

    def execute_policies(
        self,
        substate: StateVariables,
        state_update_block: StateUpdateBlock,
    ) -> PolicySignal:
        """Run a block's Policy Functions and merge their signals into one dict.

        Each policy receives ``(params, substep, state_history, substate)``.
        Where multiple policies emit the same signal key, their values are
        summed (see `add_signals`).
        """
        policy_results: List[PolicySignal] = list(
            map(lambda function: function(
                self.params,
                self.substep,
                self.result,
                self.deepcopy_method(substate) if self.enable_deepcopy else substate.copy()
            ), state_update_block["policies"].values())
        )

        result: dict = {}
        result_length = len(policy_results)
        if result_length == 0:
            return result
        elif result_length == 1:
            return policy_results[0]
        else:
            return reduce(SimulationExecution.add_signals, policy_results, result)

    def update_state(
        self,
        substate: StateVariables,
        signals: PolicySignal,
        state_update: StateUpdate,
    ) -> StateUpdateResult:
        """Apply one State Update Function and validate its returned key.

        Calls ``function(params, substep, state_history, substate, signals)``
        and checks that the returned key matches the declared State Variable
        and exists in the initial state.

        Returns:
            StateUpdateResult: The ``(key, value)`` produced by the function.

        Raises:
            KeyError: If the declared or returned key is unknown, or they differ.
        """
        _substate = self.deepcopy_method(substate) if self.enable_deepcopy else substate.copy()
        _signals = self.deepcopy_method(signals) if self.enable_deepcopy else signals.copy()

        state, function = state_update
        if state not in self.initial_state:
            raise KeyError(f"Invalid state key {state} in partial state update block")
        state_key, state_value = function(
            self.params, self.substep, self.result, _substate, _signals
        )
        if state_key not in self.initial_state:
            raise KeyError(
                f"Invalid state key {state} returned from state update function"
            )
        if state == state_key:
            return state_key, state_value
        else:
            raise KeyError(
                f"PSU state key {state} doesn't match function state key {state_key}"
            )

    @staticmethod
    def add_signals(acc: PolicySignal, a: PolicySignal) -> PolicySignal:
        """Reduce two Policy Signals by summing values that share a key."""
        for (key, value) in a.items():
            if acc.get(key, None):
                acc[key] += value
            else:
                acc[key] = value
        return acc

    @staticmethod
    def deepcopy_method(obj: Any) -> Any:
        """
        The method used for simulation deepcopy operations
        """
        return pickle.loads(pickle.dumps(obj=obj, protocol=-1))


def multiprocess_wrapper(simulation_execution: SimulationExecution):
    """Execute one [SimulationExecution][radcad.core.SimulationExecution], handling exceptions per policy.

    This is the function dispatched to worker processes by every backend. If
    ``raise_exceptions`` is ``True`` the exception propagates; otherwise the
    partial result up to the failing timestep is returned alongside an
    exception/traceback metadata dict.

    Args:
        simulation_execution (SimulationExecution): The run to execute.

    Returns:
        tuple: ``(result, exception_metadata)``, the per-substep result and a
        dict describing any exception (with ``exception``/``traceback`` set to
        ``None`` on success).
    """
    exception = None
    trace = None
    try:
        try:
            simulation_execution.execute()
        except Exception as _exception:
            trace = traceback.format_exc()
            exception = _exception
            print(trace)
            raise_exceptions_message = (
              'Catching exception and returning partial results because option Engine.raise_exceptions == False.'
              if simulation_execution.raise_exceptions
              else 'Raising exception because option Engine.raise_exceptions == True (set to False to catch exception and return partial results).'
            )
            simulation_execution.logger.warning(
                f"""Simulation {
                    simulation_execution.simulation_index
                } / run {
                    simulation_execution.run_index
                } / subset {
                    simulation_execution.subset_index
                } failed!
                {raise_exceptions_message}"""
            )
        if simulation_execution.raise_exceptions and exception:
            raise exception
        else:
            return simulation_execution.result, {
                'exception': exception,
                'traceback': trace,
                'simulation': simulation_execution.simulation_index,
                'run': simulation_execution.run_index,
                'subset': simulation_execution.subset_index,
                'timesteps': simulation_execution.timesteps,
                'parameters': simulation_execution.params,
                'initial_state': simulation_execution.initial_state,
            }
    except Exception as e:
        """
        Fail safe by catching catch any outer exceptions
        """
        if simulation_execution.raise_exceptions:
            raise e
        else:
            return [], e
