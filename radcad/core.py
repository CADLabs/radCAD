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
    timesteps: int = 0
    timestep: int = None

    substep_index: int = 0
    substeps: List = default([])

    state_update_blocks: List[StateUpdateBlock] = default([])
    result: SimulationResults = default([])

    def execute(
        self,
    ) -> SimulationResults:
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
