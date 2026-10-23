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
| JK system | 2016 two-door Rubicon. Two modules on one bus: front (glovebox, `MMSS`) — light bar, bumper pods, ditch lights, front rock lights, compressor and winch on AUX; rear (inside the Tuffy cargo enclosure, `SSSS`) — RIGID Chase 90133 (AUX bank plus one S output) and a rear flood, with slots for rear rock lights and camp lights if fitted |
| AUX outputs | 4 × 5 A drivers: ARB twin compressor relay, winch isolator contactor, indicator, spare on the front module; four of the RIGID Chase's five functions on the rear |
| Inputs | 8 × configurable (ground-switched, 12 V-switched, analog 0–16 V, frequency) + ignition/wake |
| Protection | Hardware short-circuit trip per channel, firmware instantaneous + I²t e-fuse, retries, interlocks, load shed, thermal derating, per-output supply limit for 12 V-only lamps (24 V jump start) |
| CAN | Accessory bus 500 kbit/s (control + telemetry, [DBC](can/pcm.dbc)); JK CAN-IHS 125 kbit/s receive-only in hardware; OBD-II port listen-only, optional standard-PID polling |
| Autonomy | Per-output rules on inputs, ignition, panel buttons, vehicle signals (speed, RPM, high beam), battery voltage, load current; timers and interlocks |
| Compressor | ARB twin keeps its relay and pressure switch; the module drives the coil, interlocks it to the engine, detects running from coil current, stops on a continuous-run limit |
| Winch | Isolator contactor armed from the panel, auto-disarmed when driving or after a timeout, hardwired override that works without the module, welded-contact detection |
| Lamp keep-alive | 2 adjustable 5–8 V outputs injected into the turn/position circuits through diodes, so LED lamps with controllers (EVO J3) stay booted between flashes; the factory flasher stays in control |
| Bluetooth | J-Link lamp modes and brightness: investigation plan, with a BLE bridge in the switch panel if the protocol allows |
| Mounting | Glovebox and rear cargo area: ASA shells printed on a Bambu X1C over 6 mm aluminium heat-sink plates. Engine bay supported: PAHT-CF shell on the same plate, or a die-cast box |
| Expansion | Up to 4 modules per bus (16 main outputs); modules share values as peers, no master |
| Sleep current | ≤ 250 µA requirement per module, 195 µA estimated; ≈ 0.5 mA for the parked two-module system with its panel |
| Environment | Grade 1 (−40…+125 °C) parts; IP65 cab build, IP67 engine-bay build; ISO 16750 / ISO 7637 design targets |

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
| [13-multi-module-system](docs/13-multi-module-system.md) | Glovebox + rear modules: allocation, power feeds, trunk cable, peer signals, sleep, thermal |
| [14-lamp-keep-alive-and-bluetooth](docs/14-lamp-keep-alive-and-bluetooth.md) | 6 V lamp keep-alive injection, bench characterisation, diagnostics, Bluetooth investigation |

## Folder layout

```
power-control-module/
├── README.md
├── docs/                  # design documents (above)
├── can/pcm.dbc            # CAN database for the accessory-bus protocol (module 0)
├── can/pcm-jk.dbc         # generated: both JK modules
├── config/jk-front.yaml   # JK front module (glovebox)
├── config/jk-rear.yaml    # JK rear module (cargo area)
├── hardware/              # KiCad projects (planned structure + layout rules)
├── firmware/              # firmware (planned structure)
├── mechanical/            # enclosure and bracket CAD for the X1C (planned)
└── tools/
    ├── budget.py          # thermal, copper, harness and sleep-current budgets
    ├── gen_dbc.py         # multi-module DBC from can/pcm.dbc
    └── test_*.py
```

## Tools

The numbers in the docs come from `tools/budget.py` (standard library only):

```bash
cd power-control-module
python3 tools/budget.py                    # JK build: MMSS, cab, printed shell + plate
python3 tools/budget.py --build LMSS --location engine_bay --enclosure alu
python3 tools/budget.py --build M+MSS --location engine_bay_hot --scenario jk_expected
python3 tools/budget.py --build SSSS --location tuffy --scenario jk_rear_expected --aux rear
python3 tools/gen_dbc.py --modules 2 --out can/pcm-jk.dbc   # after editing can/pcm.dbc
python3 -m pytest tools                    # margin and generator checks (pytest from the repo's dev env)
```

Decode logged CAN traffic with the DBC, e.g. with
[cantools](https://github.com/cantools/cantools):

```bash
python3 -m cantools dump can/pcm-jk.dbc
```

## Legal note

Auxiliary off-road lighting is restricted on public roads in most
jurisdictions. Rules such as "light bar only with high beams" are
conveniences, not compliance; road-legal behaviour is the installer's
responsibility.
