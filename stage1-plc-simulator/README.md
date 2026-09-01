# Stage 1: Software PLC Simulator

A Python simulation of PLC-style control logic for a **fill → heat → drain**
tank sequence, the kind of process you'd otherwise program in Structured
Text or an SFC on a Siemens S7-1500.

## What this demonstrates

- **Scan cycle**: the simulator loops on a fixed interval (`SCAN_INTERVAL_S`),
  each scan reading inputs, executing one pass of logic, and writing outputs.
  That's the same read, execute, write model every real PLC runs on.
- **State machine sequencing**: `IDLE → FILLING → HEATING → DRAINING → IDLE`,
  with a `FAULT` state for a safety timeout. This is the same shape as an
  IEC 61131-3 SFC (Sequential Function Chart).
- **TON-style timers**: `Timer` mirrors a Timer-On-Delay block. A condition
  must hold continuously for a preset duration before `.done` becomes true.
  Used for both the fill-timeout safety interlock and the heat-dwell hold.
- **I/O separation**: `Inputs`/`Outputs` dataclasses stand in for discrete
  I/O modules. `process_model.py` is the "plant" the PLC is controlling,
  kept deliberately separate from the control logic in `plc_simulator.py`.

## Run it

```bash
python plc_simulator.py
```

Prints one status line every 5 scans as the tank fills to the high-level
sensor, heats to 60°C and holds for 3s, then drains back to the low-level
sensor and returns to `IDLE`.

## Files

- `process_model.py`: the simulated physical process (tank level and temperature)
- `plc_simulator.py`: scan loop, state machine, timers, demo entry point

## What's next

More stages build on this foundation. Details to follow as they land.
