# 10 — Decisions and open questions

## Decision log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D-1 | All module outputs solid-state high-side; no relays inside the module | Request; also gives current measurement, PWM and diagnostics. Loads above the L rating (ARB twin, winch) keep their own relay/contactor outside the module (D-15, D-16). | Accepted |
| D-2 | Three channel classes S 10 A / M 20 A / L 40 A | Covers lighting (S/M) and a single-motor compressor (L) without over-building every channel; see [03](03-output-channels.md) | Proposed |
| D-3 | JK default variant **`MMSS`** (was `LMSS`) | The ARB twin keeps its relay, so all four main outputs are lighting; 60 A total allows a 6 AWG feed into the cab | Accepted (Q-1 answered) |
| D-4 | Logic board + power board stack, cells as reusable layout blocks | Logic validated once; heavy copper only where needed; see [02](02-architecture.md#why-a-two-board-stack-instead-of-one-board) | Proposed |
| D-5 | **STM32G474** MCU (was STM32G0B1) | Three FDCAN for accessory bus + OBD port + CAN-IHS. Fallback G0B1 + MCP2518FD if sleep current fails EL-7. | Proposed |
| D-6 | Firmware language: C (STM32 LL) vs Rust (Embassy) | Both workable; C has more reference code for PROFET/TPS4811x | Open |
| D-7 | Vehicle buses are listen-only, enforced in hardware — **amended**: optional, whitelisted OBD-II mode 01 polling on the OBD port, enabled by a solder jumper | The JK OBD port may be quiet without a tester; polling standard PIDs behind the TIPM gateway is what scan gauges do. CAN-IHS stays physically receive-only. | Proposed |
| D-8 | "Current limiting" = trip + duty foldback, not linear limiting | Linear limiting at 40 A is > 100 W in a sealed box | Accepted |
| D-9 | Reverse-battery blocking on logic and L channel only; S/M use PROFET ReverseON | Back-to-back FETs on every channel doubles power-stage parts for little benefit on LED loads | Proposed |
| D-10 | Own protocol on 11-bit IDs, base `0x6A0`, with DBC | Simple to decode with any tool; CANopen keypad bridging can be a host function | Proposed |
| D-11 | Rule engine is fixed function blocks, not a script | Verifiable; covers the stated use cases | Proposed |
| D-12 | **Mount the JK module in the cab** (now the front module, in the glovebox — D-22) | Lighting-only current; ~20 °C cooler; short CAN taps and dash runs; printed enclosure viable. See [11](11-jeep-jk-integration.md#mounting-location-cab). | Accepted (Q-5 answered) |
| D-13 | **Printed ASA shell on a 6 mm aluminium base plate** (Bambu X1C) | Plate sinks the heat and takes the mounting loads; shell gives free-form connector placement. Printed-only fails thermally ([03](03-output-channels.md#thermal-check)). | Proposed |
| D-14 | Fixed AUX bank: 4 × 5 A coil drivers on every power board | Compressor relay, winch contactor and indicators without spending main outputs | Proposed |
| D-15 | ARB twin keeps ARB's relay, fuses and pressure switch; the module drives the coil | ~50 A under load exceeds the L rating; keeps ARB's tested loom; run detection from coil current | Accepted |
| D-16 | Winch isolator: sealed continuous-duty contactor with economised coil (EV200 class), hardwired override, feedback on IN3/IN4 | Engine-bay temperature, fording, fail-safe open, works with the module dead | Proposed |
| D-17 | Inputs raised from 4 to 8 | ARB rocker, reverse, two winch feedback signals and physical light toggles outgrew four inputs | Proposed |
| D-18 | CAN-IHS is the primary vehicle tap; the OBD port is secondary | The cluster lives on CAN-IHS, so speed/RPM/lamp state are likely there; the OBD port may be a quiet diagnostic bus | Proposed — confirm by sniffing (Q-10) |
| D-19 | Engine-bay build is a supported alternative: printed PAHT-CF shell on the aluminium plate (or a die-cast box), silicone gasket, compression limiters, M+ part on the light-bar slot for hot spots | Thermal model passes at 85 °C ambient and, with the M+ part, at a 105 °C hot spot; sealing a printed shell is the main risk and is tested (EV-1, EV-4). See [08](08-mechanical-and-wiring.md#engine-bay-build). | Proposed |
| D-20 | Grade 1 (−40…+125 °C) electronics in every build | One BOM for both locations | Proposed |
| D-21 | Thermal derating on estimated junction temperature, not fixed board thresholds | Same firmware works in the cab and the engine bay | Proposed |
| D-22 | **Two-module JK system:** front module (address 0, `MMSS`) in the glovebox, rear module (address 1, `SSSS`) in the cargo area | Loads switched near where they are; trailer signals local to the rear; the front module keeps the vehicle taps. See [13](13-multi-module-system.md). | Proposed |
| D-23 | Modules are peers sharing broadcast values (`M<address>.<signal>`); no master | No single point of failure; nothing new on the bus | Proposed |
| D-24 | Parked-mode telemetry (10 s `Status` with outputs on, silent otherwise, bursts on change) | One module's overnight load must not hold the others awake | Proposed |
| D-25 | Rear module on its own fused feed: **10 AWG, 30 A** (no rear battery, no fridge) | Rear loads ≤ ~18 A; avoids feeding one module through another; `VBAT_EST` corrects for the feed drop | Accepted (Q-16 answered) |
| D-26 | On this JK, tap CAN-IHS with a T-harness at the aftermarket radio interface's vehicle-side plug; rear lamp signals at the tail-light connector | The interface already occupies the radio connector; no factory wire is cut; the rear module sits next to the tail lights | Proposed — Q-18, Q-19 |
| D-27 | Lamp keep-alive is **injected** through diodes into the factory turn/position circuits; the factory flasher keeps driving 12 V | Turn signals and hazards stay with the vehicle's flasher; module failure leaves the lamps working (boot delay only). See [14](14-lamp-keep-alive-and-bluetooth.md). | Proposed — Q-21 |
| D-28 | Keep-alive rail on the logic board: buck, DAC-trimmed 5–8 V, two current-limited outputs on J7 | Low current; no change to the slot interface | Proposed |
| D-29 | Bluetooth lamp control lives in the switch panel (BLE + CAN MCU), only if the J-Link protocol can be replayed; never in the load-switching module | Keeps a radio stack out of the module; the app stays the fallback | Open — investigation steps in 14 |
| D-30 | The RIGID Chase 90133 is driven by the rear module's AUX bank (power/running, brake, strobe, white reverse/area) and the spare S slot (courtesy) | Low-current trigger wires; the light arbitrates its own modes; rear lamp signals are local to the rear module | Proposed — Q-24 |
| D-31 | Rear module mounted inside the Tuffy 282-01 cargo enclosure, base plate bolted to its wall | Secure, dry, out of the way; thermal margin holds (96 °C junction, 83 °C base at full rating) | Proposed |
| D-32 | Bucks switch above the AM band (~2.1 MHz, spread spectrum where available) | The head unit's tuner and internal amplifier share the vehicle supply and ground | Proposed — EMC-1 |

## Open questions

Answers change the design; listed with the default assumed until answered.

| ID | Question | Default assumed | Affects |
|---|---|---|---|
| Q-1 | ~~Exact compressor model?~~ **Answered:** ARB twin (CKMTA12), which includes its relay | — | D-3, D-15 |
| Q-2 | Light bar and pod part numbers (current, and whether their drivers dim on PWM)? | 50 in bar ~20 A, does not dim; pods ~12 A | M rating, PWM config |
| Q-3 | ~~Read the JK's buses?~~ **Answered:** yes, interface to the Jeep where possible | — | D-5, D-7, D-18 |
| Q-4 | CAN host: build the printed switch panel, buy a CAN keypad, or toggles only for now? | Panel in phase 5; IN5/IN6 toggles meanwhile | Panel design, `on_host_loss` defaults |
| Q-5 | ~~Engine bay or cab?~~ **Answered:** cab (D-12), enclosure printed on the X1C (D-13); engine bay remains a supported alternative (D-19) | — | Thermal, harness |
| Q-6 | Bluetooth wanted? **Partly answered:** yes, for the headlights' J-Link modes and brightness — investigation first (D-29) | BLE bridge in the switch panel if the protocol allows | Panel MCU choice |
| Q-7 | Is a higher channel count expected (e.g. rock-light zones)? | Second module on the bus | Whether to lay out an `SSSS` variant |
| Q-8 | Other vehicles in scope (JL, TJ, trucks) and their bus speeds? | JK only, others via config | Vehicle signal map, bitrate options |
| Q-9 | Build quantity (1–2 or a small batch)? | 2 | Assembly method |
| Q-10 | ~~JK model year, radio, headlamps?~~ **Answered:** 2016 two-door Rubicon, aftermarket radio, J.W. Speaker LED headlamps and 239 J2 turn signals, RIGID red LED tail lights ([11](11-jeep-jk-integration.md#this-vehicle-2016-wrangler-jk-two-door-rubicon)); transmission not stated and no longer needed | — | CAN-IHS tap point, lamp-circuit inputs |
| Q-11 | Winch model and its maximum current draw? | 8–12 k lb class, ≤ 500 A | Contactor choice (EV200 vs GV200 class), feed protection |
| Q-12 | Keep the ARB rocker as the compressor switch, or move it to the panel? | Keep it (IN1), with its indicator on AUX3 | IN1/AUX3 allocation |
| Q-13 | Under-dash space and firewall route on this JK? | Passenger side, existing grommet | Enclosure shape, harness lengths |
| Q-14 | Actual temperatures at the candidate mounting spots (glovebox, rear cargo area, engine bay), including a summer crawl and a heat soak after shutdown? | Cab 65 °C (+ closed-glovebox penalty), engine bay 85 °C / 105 °C hot spot | Location choice, M vs M+ on the light-bar slot, enclosure |
| Q-15 | ~~Where is the ARB twin mounted?~~ **Answered:** engine bay → front module AUX1 | — | — |
| Q-16 | ~~Rear auxiliary battery or fridge?~~ **Answered:** neither → 10 AWG / 30 A rear feed, rear OUT3 freed | — | — |
| Q-17 | ~~Two-door or four-door?~~ **Answered:** two-door, ~4 m rear feed | — | Rear feed gauge and drop |
| Q-18 | ~~Which radio?~~ **Answered:** NVGOTEV Android head unit on the stock four speakers, internal amplifier, no external amp or subwoofer. Still to check: is there a CAN decoder box in its harness (where the CAN-IHS T-tap goes), and does the unit's Android expose Bluetooth LE to apps? | Decoder box on the radio connector; no analog reverse/VSS outputs | T-tap location; J-Link on the head unit |
| Q-19 | ~~Which RIGID tail light?~~ **Answered:** RIGID 90133 is the Chase rear-facing pod, not a tail light; the tail lights stay factory | — | — |
| Q-23 | Which rear loads besides the Chase will be fitted (rear floods, rear rock lights, camp lights)? | Placeholders kept | `SSSS` versus an AUX-only rear build |
| Q-24 | RIGID Chase 90133 wire map from RIGID's instruction sheet (owners report red power/running, black ground, white brake, three more triggers) | As in `config/jk-rear.yaml` | AUX allocation on the rear module |
| Q-20 | Which J.W. Speaker headlight model? Bluetooth brightness control points to the EVO J3 (built-in turn signal). If so, do the 239 J2 grille lamps stay active too (J.W. Speaker says J3 turn signals plus factory-position turn lamps exceed DOT intensity)? | EVO J3; 239 J2 position function only | Keep-alive injection points, DOT compliance |
| Q-21 | Bench results for the lamp that needs keep-alive: which input powers its electronics, `V_alive`, `V_glow`, keep-alive current (warm and cold), boot time, Bluetooth reachable at keep-alive? | Turn input, 6 V, ≤ 0.1 A per lamp | Keep-alive level, current limit, injector design |
| Q-22 | Which phone (iOS or Android) is available for the Bluetooth capture? | Android (HCI snoop log is simplest) | Investigation method |

## Roadmap

| Phase | Scope |
|---|---|
| 0 — now | This design package: requirements, architecture, protocol, budgets |
| 0.5 | **Sniff the JK** with a USB-CAN adapter in listen-only mode (CAN-IHS and the OBD port) and confirm D-18 / the OBD polling need; print PLA mock-ups of the module (glovebox and rear cargo area) and the panel to check the space; log temperatures at the candidate spots for a week (Q-14). All three are cheap and settle questions before schematics freeze. |
| 1 | Schematics in KiCad for the logic board and the `MMSS` power board (with AUX bank); part selection locked; review |
| 2 | Layout, fab, bring-up (BU-*), protection tests (PR-*) |
| 3 | Firmware: protection + CAN protocol + rule engine + vehicle signal map; host config tool (Python) |
| 4 | Enclosure CAD from the board outlines, printed shell and brackets, harness, vehicle install (VH-*, CW-*) |
| 5 | Switch panel; options: CAN bootloader, BLE companion board, `LMSS`/`SSSS` variants, CANopen keypad bridge |
