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
  V3.5). Contains the PLC_PRG structured text program and the Modbus TCP
  Server device configuration.

## Why CODESYS

An earlier attempt used OpenPLC, but hit a reproducible bug where
declared I/O variables were silently dropped from the generated program
specifically when targeting a real deployment device, while working fine
in the built-in simulator. CODESYS, a mature and widely used industrial
tool, compiled and ran the same logic correctly on the first real attempt.

## What's next

More stages build on this foundation. Details to follow as they land.
