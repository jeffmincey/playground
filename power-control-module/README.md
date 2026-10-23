# power-control-module

A modular, all-solid-state 12 V power distribution module for a Jeep JK and
other off-road vehicles: 4 configurable inputs, 4 high-side outputs in
mixed current classes, per-channel current measurement and electronic
fusing, CAN control, and autonomous rules that run with no CAN host.

## Status

**Design phase.** Requirements, architecture, protocol and budgets are
written; schematics, layout and firmware are not started. Part numbers are
candidates until the BOM is frozen — see
[open questions](docs/10-decisions-and-open-questions.md#open-questions).

## At a glance

| | |
|---|---|
| Outputs | 4 high-side solid-state, each slot one of three classes |
| Classes | **S** 10 A (PROFET+2, PWM) · **M** 20 A (PROFET+2, PWM) · **L** 40 A (discrete FETs + smart driver, reverse-blocking) |
| Default build | `LMSS` — compressor, light bar, rear floods, rock lights; 80 A total |
| Inputs | 4 × configurable (ground-switched, 12 V-switched, analog 0–16 V, frequency) + ignition/wake |
| Protection | Hardware short-circuit trip per channel, firmware instantaneous + I²t e-fuse, retries, load shed, thermal derating |
| CAN | Accessory bus 500 kbit/s (control + telemetry, [DBC](can/pcm.dbc)); vehicle bus listen-only, enforced in hardware |
| Autonomy | Per-output rules on inputs, ignition, virtual CAN inputs, vehicle signals, battery voltage; timers and interlocks |
| Expansion | Up to 4 modules per bus (16 outputs) |
| Sleep current | ≤ 250 µA requirement, 145 µA estimated |
| Environment | −40…+85 °C, IP67 with membrane vent, ISO 16750 / ISO 7637 design targets |

## "Different flavors" of channel

Yes — that is the core of the modularity. One heavy channel for the
compressor and a mix of medium and small channels for lighting is cheaper,
cooler and smaller than four 40 A channels. Each class is a reusable
*cell* behind a common slot interface, so a different mix (`MMMM`, `SSSS`,
…) is a new power board built from the same cells, with the same logic
board and firmware; firmware reads which class is fitted in each slot.
Details in [02-architecture](docs/02-architecture.md#modularity--three-levels)
and [03-output-channels](docs/03-output-channels.md).

## Documents

| Doc | Content |
|---|---|
| [01-requirements](docs/01-requirements.md) | Use cases, functional/electrical/environmental requirements with IDs |
| [02-architecture](docs/02-architecture.md) | System diagram, modularity, board variants, slot interface, arbitration |
| [03-output-channels](docs/03-output-channels.md) | S/M/L cells, current sensing, protection layers, thermal check |
| [04-inputs](docs/04-inputs.md) | Input circuit and modes, trailer harness decoding, ignition |
| [05-logic-power-can](docs/05-logic-power-can.md) | Logic supply, MCU, CAN hardware, JK vehicle bus, sleep |
| [06-can-protocol](docs/06-can-protocol.md) | Message map, failsafe, fault codes, configuration access |
| [07-firmware](docs/07-firmware.md) | Loops, protection state machine, e-fuse, rule engine, storage, update |
| [08-mechanical-and-wiring](docs/08-mechanical-and-wiring.md) | Enclosure, connectors and pinouts, harness sizing, JK mounting |
| [09-validation-plan](docs/09-validation-plan.md) | Bring-up, protection, transient, thermal, CAN, environmental tests |
| [10-decisions-and-open-questions](docs/10-decisions-and-open-questions.md) | Decision log, open questions, roadmap |

## Folder layout

```
power-control-module/
├── README.md
├── docs/                 # design documents (above)
├── can/pcm.dbc           # CAN database for the accessory-bus protocol
├── config/jk-example.yaml# example autonomous configuration for a JK
├── hardware/             # KiCad projects (planned structure + layout rules)
├── firmware/             # firmware (planned structure)
└── tools/
    ├── budget.py         # thermal, copper, harness and sleep-current budgets
    └── test_budget.py
```

## Tools

The numbers in the docs come from `tools/budget.py` (standard library only):

```bash
cd power-control-module
python3 tools/budget.py               # all tables at 85 °C ambient
python3 tools/budget.py --ambient 60  # thermal table at another ambient
python3 -m pytest tools               # margin checks (pytest from the repo's dev env)
```

Decode logged CAN traffic with the DBC, e.g. with
[cantools](https://github.com/cantools/cantools):

```bash
python3 -m cantools dump can/pcm.dbc
```

## Legal note

Auxiliary off-road lighting is restricted on public roads in most
jurisdictions. Rules such as "light bar only with ignition on" are
conveniences, not compliance; road-legal behaviour is the installer's
responsibility.
