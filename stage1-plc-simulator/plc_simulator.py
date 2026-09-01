"""
Software PLC simulator: scan-cycle loop + state machine for a
fill -> heat -> drain tank sequence.

Mirrors how you'd structure this in IEC 61131-3 Structured Text:
  - a scan cycle: read inputs, execute one pass of logic, write outputs
  - a state variable driving an SFC-style sequence
  - TON-style timers (a value that must hold true continuously for a
    duration before it "times out")
"""

import time
from dataclasses import dataclass, field
from enum import Enum, auto

from process_model import ProcessState, step

SCAN_INTERVAL_S = 0.2          # one scan every 200 ms
HEAT_TARGET_C = 60.0
HEAT_DWELL_S = 3.0             # hold at target temp this long before draining
FILL_TIMEOUT_S = 30.0          # safety timer: fault if tank doesn't fill in time


class State(Enum):
    IDLE = auto()
    FILLING = auto()
    HEATING = auto()
    DRAINING = auto()
    FAULT = auto()


@dataclass
class Timer:
    """TON-style timer: call update(condition) each scan; done becomes True
    once `condition` has been continuously True for `preset_s` seconds."""
    preset_s: float
    elapsed_s: float = 0.0
    done: bool = False

    def update(self, condition: bool, dt_s: float) -> None:
        if condition:
            self.elapsed_s += dt_s
            self.done = self.elapsed_s >= self.preset_s
        else:
            self.elapsed_s = 0.0
            self.done = False

    def reset(self) -> None:
        self.elapsed_s = 0.0
        self.done = False


@dataclass
class Inputs:
    start_button: bool = False
    stop_button: bool = False


@dataclass
class Outputs:
    inlet_valve: bool = False
    heater: bool = False
    drain_valve: bool = False


class PLC:
    def __init__(self) -> None:
        self.state = State.IDLE
        self.process = ProcessState()
        self.outputs = Outputs()
        self.fill_timer = Timer(preset_s=FILL_TIMEOUT_S)
        self.dwell_timer = Timer(preset_s=HEAT_DWELL_S)

    def scan(self, inputs: Inputs, dt_s: float = SCAN_INTERVAL_S) -> None:
        """One full PLC scan: evaluate logic for the current state, then
        advance the physical process by one step using this scan's outputs."""
        out = Outputs()  # outputs default to de-energized each scan unless logic sets them

        if self.state == State.IDLE:
            if inputs.start_button:
                self.state = State.FILLING
                self.fill_timer.reset()

        elif self.state == State.FILLING:
            out.inlet_valve = True
            self.fill_timer.update(condition=not self.process.level_high_sensor, dt_s=dt_s)
            if self.process.level_high_sensor:
                self.state = State.HEATING
                self.dwell_timer.reset()
            elif self.fill_timer.done:
                self.state = State.FAULT

        elif self.state == State.HEATING:
            out.heater = True
            at_target = self.process.temperature_c >= HEAT_TARGET_C
            self.dwell_timer.update(condition=at_target, dt_s=dt_s)
            if self.dwell_timer.done:
                self.state = State.DRAINING

        elif self.state == State.DRAINING:
            out.drain_valve = True
            if self.process.level_low_sensor:
                self.state = State.IDLE

        elif self.state == State.FAULT:
            pass  # all outputs stay de-energized; requires external reset

        if inputs.stop_button and self.state != State.FAULT:
            self.state = State.IDLE
            out = Outputs()

        self.outputs = out
        self.process = step(
            self.process,
            inlet_valve=out.inlet_valve,
            heater=out.heater,
            drain_valve=out.drain_valve,
        )

    def status_line(self) -> str:
        p, o = self.process, self.outputs
        return (
            f"state={self.state.name:<8} "
            f"level={p.level_pct:5.1f}% temp={p.temperature_c:5.1f}C  "
            f"inlet={int(o.inlet_valve)} heater={int(o.heater)} drain={int(o.drain_valve)}"
        )


def run_demo() -> None:
    plc = PLC()
    inputs = Inputs()

    print("Starting cycle: press start_button on scan 1, then let it run.\n")
    for i in range(300):
        inputs.start_button = i == 1  # momentary press, one scan only
        plc.scan(inputs)
        if i % 5 == 0 or plc.state == State.FAULT:
            print(f"scan {i:3d}  {plc.status_line()}")
        if plc.state == State.IDLE and i > 5:
            print(f"\nCycle complete at scan {i}.")
            break
        if plc.state == State.FAULT:
            print("\nFAULT: fill timeout exceeded.")
            break
        time.sleep(0)  # real deployment would sleep(SCAN_INTERVAL_S) here


if __name__ == "__main__":
    run_demo()
