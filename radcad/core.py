import logging
import pickle
import traceback
from dataclasses import dataclass
from functools import reduce
from typing import Any, List

from radcad.types import (PolicySignal, SimulationResults, StateUpdate,
                          StateUpdateBlock, StateUpdateResult, StateVariables,
                          SystemParameters)
from radcad.utils import default


@dataclass
class SimulationExecution:
    # Simulation settings
    initial_state: StateVariables = default({})
    params: SystemParameters = default({})
    state_update_blocks: List[StateUpdateBlock] = default([])
    timesteps: int = 0

    # Execution settings
    enable_deepcopy: bool = True
    drop_substeps: bool = False
    raise_exceptions: bool = True
    logger = logging.getLogger("radCAD")
    """Use "radCAD" logging instance to avoid conflict with other projects"""

    # Simulation state
    simulation_index: int = 0
    subset_index: int = 0
    run_index: int = 1
    """
    Index starts at +1 to remain compatible with cadCAD implementation
    """

    # Simulation runtime state
    timestep: int = None
    substep_index: int = None
    previous_state: StateVariables = None
    substeps: List[StateVariables] = None
    result: SimulationResults = default([])

    def execute(
        self,
    ) -> SimulationResults:
        self.before_execution()
        self.initialise_state()

        for timestep in range(0, self.timesteps):
            self.timestep = timestep

            self.before_step()
            self.process_substeps(self.step())
            self.after_step()

        self.after_execution()
        return self.result

    def initialise_state(self):
        self.initial_state["simulation"] = self.simulation_index
        self.initial_state["subset"] = self.subset_index
        self.initial_state["run"] = self.run_index
        self.initial_state["substep"] = 0
        # Needed to properly handle model generator
        if not self.initial_state.get("timestep", False):
            self.initial_state["timestep"] = 0

        self.result.append([self.initial_state])

    def step(self) -> List[StateVariables]:
        self.previous_state: StateVariables = (
            self.result[0][0].copy()
            if self.timestep == 0
            else self.result[-1][-1:][0].copy()
        )

        self.substeps: List = []
        for (substep, state_update_block) in enumerate(self.state_update_blocks):
            self.substep_index = substep
            self.substep(state_update_block)

        return self.substeps or [self.previous_state.copy()]

    def process_substeps(self, substeps: List[StateVariables]) -> None:
        self.result.append(substeps if not self.drop_substeps else [substeps.pop()])

    def substep(self, state_update_block: StateUpdateBlock) -> None:
        substate: StateVariables = (
            self.previous_state.copy() if self.substep_index == 0 else self.substeps[self.substep_index - 1].copy()
        )

        signals: PolicySignal = self.execute_policies(substate, state_update_block)

        updated_state: List[StateUpdateResult] = [
            self.update_state(substate, signals, state_update)
            for state_update in state_update_block["variables"].items()
        ]
        self.process_updated_state(substate, updated_state)
    
    def process_updated_state(self, substate: StateVariables, updated_state: List[StateUpdateResult]) -> None:
        substate.update(updated_state)
        substate["timestep"] = (self.previous_state["timestep"] + 1) if self.timestep == 0 else self.timestep + 1
        substate["substep"] = self.substep_index + 1
        self.substeps.append(substate)

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
        if not state in self.initial_state:
            raise KeyError(f"Invalid state key {state} in partial state update block")
        state_key, state_value = function(
            self.params, self.substep, self.result, _substate, _signals
        )
        if not state_key in self.initial_state:
            raise KeyError(
                f"Invalid state key {state} returned from state update function"
            )
        if state == state_key:
            return (state_key, state_value)
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
    def deepcopy_method(obj) -> Any:
        """
        Define the default method used for deepcopy operations
        Must be a function and not a lambda function to ensure multiprocessing can Pickle the object
        """
        return pickle.loads(pickle.dumps(obj=obj, protocol=-1))

    def before_execution(self) -> None:
        self.logger.info(f"Starting simulation {self.simulation_index} / run {self.run_index} / subset {self.subset_index}")

    def before_step(self) -> None:
        pass

    def after_step(self) -> None:
        pass
    
    def after_execution(self) -> None:
        pass


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
            simulation_execution.logger.warning(
                f"""Simulation {
                    simulation_execution.simulation_index
                } / run {
                    simulation_execution.run_index
                } / subset {
                    simulation_execution.subset_index
                } failed! Returning partial results if Engine.raise_exceptions == False."""
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
