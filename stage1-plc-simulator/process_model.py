"""
Physical process model: a tank that can be filled, heated, and drained.

This stands in for real field devices (a level float switch, an RTD
temperature probe, a solenoid valve, a heating element). A real PLC reads
these through I/O modules; here we just compute the next physical state
each scan based on which outputs are currently energized.
"""

from dataclasses import dataclass

AMBIENT_TEMP_C = 20.0
FILL_RATE_PCT_PER_SCAN = 0.8      # tank level rise per scan while inlet valve open
DRAIN_RATE_PCT_PER_SCAN = 1.2     # tank level fall per scan while drain valve open
HEAT_RATE_C_PER_SCAN = 0.5        # temperature rise per scan while heater on and tank has liquid
COOL_RATE_C_PER_SCAN = 0.05       # passive heat loss per scan when heater is off

LEVEL_LOW_THRESHOLD_PCT = 5.0
LEVEL_HIGH_THRESHOLD_PCT = 90.0


@dataclass
class ProcessState:
    level_pct: float = 0.0
    temperature_c: float = AMBIENT_TEMP_C

    @property
    def level_high_sensor(self) -> bool:
        return self.level_pct >= LEVEL_HIGH_THRESHOLD_PCT

    @property
    def level_low_sensor(self) -> bool:
        return self.level_pct <= LEVEL_LOW_THRESHOLD_PCT


def step(state: ProcessState, inlet_valve: bool, heater: bool, drain_valve: bool) -> ProcessState:
    """Advance the physical process by one scan, given the current outputs."""
    level = state.level_pct
    temp = state.temperature_c

    if inlet_valve:
        level = min(100.0, level + FILL_RATE_PCT_PER_SCAN)
    if drain_valve:
        level = max(0.0, level - DRAIN_RATE_PCT_PER_SCAN)

    has_liquid = level > LEVEL_LOW_THRESHOLD_PCT
    if heater and has_liquid:
        temp = temp + HEAT_RATE_C_PER_SCAN
    elif temp > AMBIENT_TEMP_C:
        temp = max(AMBIENT_TEMP_C, temp - COOL_RATE_C_PER_SCAN)

    return ProcessState(level_pct=level, temperature_c=temp)
