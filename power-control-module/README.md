# power-control-module

A modular, all-solid-state 12 V power distribution module for a Jeep JK and
other off-road vehicles: configurable inputs, 4 high-side outputs in mixed
current classes plus a bank of coil drivers, per-channel current measurement
and electronic fusing, CAN control, read access to the Jeep's own buses, and
autonomous rules that run with no CAN host.

## Status

**Design phase.** Requirements, architecture, protocol, vehicle integration
and budgets are written; schematics, layout, firmware and enclosure CAD are
not started. Part numbers are candidates until the BOM is frozen — see
[open questions](docs/10-decisions-and-open-questions.md#open-questions).

## At a glance (JK build)

| | |
|---|---|
| Main outputs | 4 high-side solid-state, each slot one of three classes |
| Classes | **S** 10 A (PROFET+2, PWM) · **M** 20 A (PROFET+2, PWM) · **L** 40 A (discrete FETs + smart driver, reverse-blocking) |
| JK build | `MMSS` — light bar, front pods, rear floods, rock lights; 60 A total |
| AUX outputs | 4 × 5 A coil drivers: ARB twin compressor relay, winch isolator contactor, indicator, spare |
| Inputs | 8 × configurable (ground-switched, 12 V-switched, analog 0–16 V, frequency) + ignition/wake |
| Protection | Hardware short-circuit trip per channel, firmware instantaneous + I²t e-fuse, retries, interlocks, load shed, thermal derating |
| CAN | Accessory bus 500 kbit/s (control + telemetry, [DBC](can/pcm.dbc)); JK CAN-IHS 125 kbit/s receive-only in hardware; OBD-II port listen-only, optional standard-PID polling |
| Autonomy | Per-output rules on inputs, ignition, panel buttons, vehicle signals (speed, RPM, high beam), battery voltage, load current; timers and interlocks |
| Compressor | ARB twin keeps its relay and pressure switch; the module drives the coil, interlocks it to the engine, detects running from coil current, stops on a continuous-run limit |
| Winch | Isolator contactor armed from the panel, auto-disarmed when driving or after a timeout, hardwired override that works without the module, welded-contact detection |
| Mounting | In the cab; ASA shell printed on a Bambu X1C over a 6 mm aluminium heat-sink plate |
| Expansion | Up to 4 modules per bus (16 main outputs) |
| Sleep current | ≤ 250 µA requirement, 193 µA estimated |
| Environment | Components −40…+85 °C; IP65 cab build; ISO 16750 / ISO 7637 design targets |

## "Different flavors" of channel

Yes — that is the core of the modularity. A mix of medium and small
channels for lighting is cheaper, cooler and smaller than four 40 A
channels. Each class is a reusable *cell* behind a common slot interface, so
a different mix (`LMSS`, `SSSS`, …) is a new power board built from the same
cells, with the same logic board and firmware; firmware reads which class is
fitted in each slot. Details in
[02-architecture](docs/02-architecture.md#modularity--three-levels) and
[03-output-channels](docs/03-output-channels.md).

## Documents

| Doc | Content |
|---|---|
| [01-requirements](docs/01-requirements.md) | Use cases, functional/electrical/environmental requirements with IDs |
| [02-architecture](docs/02-architecture.md) | System diagram, modularity, board variants, slot interface, arbitration |
| [03-output-channels](docs/03-output-channels.md) | S/M/L cells, AUX bank, current sensing, protection layers, thermal check |
| [04-inputs](docs/04-inputs.md) | Input circuit and modes, trailer harness decoding, ignition, JK allocation |
| [05-logic-power-can](docs/05-logic-power-can.md) | Logic supply, MCU, CAN hardware, sleep |
| [06-can-protocol](docs/06-can-protocol.md) | Message map, failsafe, fault codes, configuration access |
| [07-firmware](docs/07-firmware.md) | Loops, protection state machine, e-fuse, rule engine, feedback, vehicle signals, storage, update |
| [08-mechanical-and-wiring](docs/08-mechanical-and-wiring.md) | Printed enclosure, materials, switch panel, connectors and pinouts, harness |
| [09-validation-plan](docs/09-validation-plan.md) | Bring-up, protection, transient, thermal, CAN, compressor/winch, environmental tests |
| [10-decisions-and-open-questions](docs/10-decisions-and-open-questions.md) | Decision log, open questions, roadmap |
| [11-jeep-jk-integration](docs/11-jeep-jk-integration.md) | Mounting location, power, wired signals, CAN-IHS and OBD port, sniffing procedure |
| [12-compressor-and-winch](docs/12-compressor-and-winch.md) | ARB twin integration, winch isolator options, wiring, rules |

## Folder layout

```
power-control-module/
├── README.md
├── docs/                  # design documents (above)
├── can/pcm.dbc            # CAN database for the accessory-bus protocol
├── config/jk-example.yaml # example autonomous configuration for a JK
├── hardware/              # KiCad projects (planned structure + layout rules)
├── firmware/              # firmware (planned structure)
├── mechanical/            # enclosure and bracket CAD for the X1C (planned)
└── tools/
    ├── budget.py          # thermal, copper, harness and sleep-current budgets
    └── test_budget.py
```

## Tools

The numbers in the docs come from `tools/budget.py` (standard library only):

```bash
cd power-control-module
python3 tools/budget.py                    # JK build: MMSS, cab, printed shell + plate
python3 tools/budget.py --build LMSS --location engine_bay --enclosure alu
python3 -m pytest tools                    # margin checks (pytest from the repo's dev env)
```

Decode logged CAN traffic with the DBC, e.g. with
[cantools](https://github.com/cantools/cantools):

```bash
python3 -m cantools dump can/pcm.dbc
```

## Legal note

Auxiliary off-road lighting is restricted on public roads in most
jurisdictions. Rules such as "light bar only with high beams" are
conveniences, not compliance; road-legal behaviour is the installer's
responsibility.
