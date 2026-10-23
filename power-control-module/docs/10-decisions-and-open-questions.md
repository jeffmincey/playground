# 10 — Decisions and open questions

## Decision log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D-1 | All outputs solid-state high-side; no relays | Request; also gives current measurement, PWM and diagnostics for free | Accepted |
| D-2 | Three channel classes S 10 A / M 20 A / L 40 A | Covers lighting (S/M) and compressor (L) without over-building every channel; see [03](03-output-channels.md) | Proposed |
| D-3 | Default variant `LMSS` | Matches the JK load list: compressor, bar, two light groups | Proposed — depends on Q-1 |
| D-4 | Logic board + power board stack, cells as reusable layout blocks | Logic validated once; heavy copper only where needed; see [02](02-architecture.md#why-a-two-board-stack-instead-of-one-board) | Proposed |
| D-5 | STM32G0B1 MCU | 2 × FDCAN + USB + ADC at low cost | Proposed |
| D-6 | Firmware language: C (STM32 LL) vs Rust (Embassy) | Both workable; C has more reference code for PROFET/TPS4811x | Open |
| D-7 | Vehicle CAN is listen-only, enforced in hardware | Never risk disturbing vehicle ECUs | Accepted |
| D-8 | "Current limiting" = trip + duty foldback, not linear limiting | Linear limiting at 40 A is > 100 W in a sealed box | Accepted |
| D-9 | Reverse-battery blocking on logic and L channel only; S/M use PROFET ReverseON | Back-to-back FETs on every channel doubles power-stage parts for little benefit on LED loads | Proposed |
| D-10 | Own protocol on 11-bit IDs, base `0x6A0`, with DBC | Simple to decode with any tool; CANopen keypad bridging can be a host function | Proposed |
| D-11 | Rule engine is fixed function blocks, not a script | Verifiable; covers the stated use cases | Proposed |

## Open questions

Answers change the design; listed with the default assumed until answered.

| ID | Question | Default assumed | Affects |
|---|---|---|---|
| Q-1 | Exact compressor model (single or twin motor, running and peak current)? | Single motor, ≤ 45 A running, ≤ 150 A peak | L-cell rating, D-3 |
| Q-2 | Light bar and pod part numbers (current, and whether their drivers dim on PWM)? | 50 in bar ~20 A, does not dim | M rating, PWM config |
| Q-3 | Should the module read the JK's CAN-C bus (speed, gear, high beam), or wired inputs only? | Hardware fitted, signal map empty | J6, firmware effort |
| Q-4 | What is the CAN host — a commercial CAN keypad (which one?), a custom switch panel, a phone bridge, or none at first? | None at first; autonomous rules + dash toggles | Protocol bridging, `on_host_loss` defaults |
| Q-5 | Engine bay or in-cab mounting? | Engine bay | Thermal margin, harness |
| Q-6 | Bluetooth/phone configuration wanted? | No for rev A; companion board later | Logic board connector reservation |
| Q-7 | Is a higher channel count expected (e.g. 8 small channels for lockers, rock-light zones)? | Second module on the bus | Whether to lay out an `SSSS` or 8-channel S variant |
| Q-8 | Other vehicles in scope (JL, TJ, trucks) and their bus speeds? | JK only, others via config | Vehicle signal map, bitrate options |
| Q-9 | Build quantity (1–2 or a small batch)? | 2 | Enclosure (off-the-shelf vs machined), assembly method |

## Roadmap

| Phase | Scope |
|---|---|
| 0 — now | This design package: requirements, architecture, protocol, budgets |
| 1 | Schematics in KiCad for logic board and `LMSS` power board; part selection locked; review |
| 2 | Layout, fab, bring-up (BU-*), protection tests (PR-*) |
| 3 | Firmware: protection + CAN protocol + rule engine; host config tool (Python) |
| 4 | Enclosure, harness, vehicle install (VH-*) |
| 5 | Options: CAN bootloader, BLE companion board, `MMMM`/`SSSS` variants, CANopen keypad bridge |
