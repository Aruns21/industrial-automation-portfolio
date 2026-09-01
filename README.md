# Industrial Automation Portfolio

A series of projects building up the industrial **automation pyramid**
bottom-up, from PLC control logic to IIoT dashboards, as part of my
path toward an Industrial Automation / IIoT engineering role.

Built by [Arun Sudhakaran Nair](https://github.com/Aruns21), M.Sc. student
in Automation Technology at Technische Hochschule Deggendorf.

## Progress

**Stage 1 (Field/Control level): done.** [Software PLC simulator](stage1-plc-simulator/):
scan cycle, state machine, and IEC 61131-3-style timers for a tank
fill → heat → drain sequence.

More stages will be added here as they're completed. Each one builds on the
previous one's output rather than standing alone, so the repo's history
tells one continuous story rather than a set of disconnected demos.

## Why this structure

Mirrors the ISA-95 automation pyramid that real plant architectures follow:
field/control devices at the bottom, supervisory/HMI above that, then
MES/historian, then enterprise/cloud analytics. Building it in that order,
starting with actual control logic rather than jumping straight to IIoT
tooling, reflects the core of what a PLC/automation engineer does before
any of the IIoT layer matters.
