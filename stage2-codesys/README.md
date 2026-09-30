# Stage 2: Real PLC Runtime (CODESYS)

The same tank fill, heat, drain sequence from Stage 1, now written in genuine
Structured Text and running live on a real PLC runtime (CODESYS Control Win),
exposed over real Modbus TCP.

## What this demonstrates

- **Real IEC 61131-3 logic**: the state machine and timers from Stage 1,
  translated into Structured Text and compiled by a real PLC toolchain,
  not just simulated to look like one.
- **A real PLC runtime**, not a script pretending to be one: the compiled
  program runs continuously on CODESYS Control Win, independent of the
  engineering tool that wrote it.
- **Real Modbus TCP exposure**: a Modbus TCP Server device serves the
  program's tags on port 502. StartButton, StopButton, and the level
  sensors are writable Coils; InletValve, Heater, and DrainValve are
  readable Discrete Inputs.
- **Independent verification**: a hand-built Python script (raw sockets,
  no Modbus library) connects externally, reads the Coils, writes
  StartButton, and confirms InletValve responds correctly, with zero
  involvement from the engineering tool that built the program.

## Files

- `Stage2_TankSequence.project`: the CODESYS project (open with CODESYS
  V3.5). Contains the PLC_PRG structured text program, the TankSequence_LD
  ladder diagram program, and the Modbus TCP Server device configuration.

## Same logic, second language: Ladder Diagram

The same tank sequence also exists as `TankSequence_LD`, a Ladder Diagram
program in the same project. It implements identical behavior to PLC_PRG,
including both TON timers, but the state memory design is simplified: instead
of separate step flags, the InletValve, Heater, and DrainValve outputs
themselves (via Set and Reset coils) double as the state memory, since they
are mutually exclusive by design. This cuts the rung count and keeps the
logic closer to how a plant electrician reading a ladder printout would
expect it to look.

TankSequence_LD is not currently called by MainTask. It compiles cleanly on
its own and is wired to a second IEC task (LadderTask) gated behind a Bool
that is never set to TRUE, so it stays structurally present without
conflicting with PLC_PRG's live control of the same I/O.

## Why CODESYS

An earlier attempt used OpenPLC, but hit a reproducible bug where
declared I/O variables were silently dropped from the generated program
specifically when targeting a real deployment device, while working fine
in the built-in simulator. CODESYS, a mature and widely used industrial
tool, compiled and ran the same logic correctly on the first real attempt.

## What's next

More stages build on this foundation. Details to follow as they land.
