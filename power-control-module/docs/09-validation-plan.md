# 09 — Validation plan

Bench-first, then vehicle. Each test lists the requirement it closes. Tests
marked **lab** need equipment beyond a bench supply (transient generator,
climatic chamber, shaker); for a personal build these can be done at a
rented test house or approximated as noted.

## Bring-up (per board)

| ID | Test | Pass |
|---|---|---|
| BU-1 | Power logic board alone from a current-limited supply at 13.5 V | Rails in tolerance, MCU enumerates over USB/SWD |
| BU-2 | Read slot ID and EEPROM on a fitted power board | Classes and calibration read back |
| BU-3 | Each output into a resistive load at 10 % and 80 % rating | Calibrated current within FN-3 |
| BU-4 | Logic board removed, power board powered | All outputs off (pull-downs) |

## Protection

| ID | Test | Closes | Pass |
|---|---|---|---|
| PR-1 | Hard short (≤ 10 mΩ) on each output, MCU running | FN-4 | Hardware trip, no damage, fault reported, retries per config |
| PR-2 | PR-1 with the MCU halted by the debugger, output on | FN-4 | Hardware trip still protects; no damage |
| PR-3 | Overload at 1.5×, 2×, 3×, 5× rating | FN-5 | Trip time within ±20 % of the I²t table in [07](07-firmware.md#electronic-fuse) |
| PR-4 | Compressor (or a motor + flywheel load) start, 10 cycles | FN-5 | No nuisance trip; inrush logged |
| PR-5 | Light bar start, cold, 10 cycles with and without soft-start | FN-6 | No trip with soft-start configured |
| PR-6 | Inductive turn-off: relay coil, air-locker solenoid, compressor | — | Output voltage clamped; no device stress beyond datasheet |
| PR-7 | Output shorted to VBAT while off, and while on | EL-6 | `EXT_VOLTAGE` reported; no damage |
| PR-8 | Module ground (J2) disconnected with outputs on | EL-6 | Outputs turn off or stay safe; no damage; recovers on reconnect |

## Supply transients

| ID | Test | Closes | Method |
|---|---|---|---|
| TR-1 | Cranking profile down to 6 V and 4.5 V | EL-1 | Programmable supply |
| TR-2 | Suppressed load dump, 35 V clamped | EL-2 | **lab** (ISO 16750-2 5b); approximation: supply step to 35 V for 400 ms |
| TR-3 | ISO 7637-2 pulses 1, 2a, 3a, 3b | EL-3 | **lab** |
| TR-4 | 24 V for 60 s with all outputs on at rating | EL-4 | Bench supply |
| TR-5 | −14 V for 60 s, outputs commanded on and off | EL-5 | Bench supply, current limited to 100 A |
| TR-6 | Short interruptions 10 µs – 100 ms | EL-1 | Programmable supply / MOSFET interrupter |

## Thermal

| ID | Test | Closes | Pass |
|---|---|---|---|
| TH-1 | All channels at rating, lid on, 25 °C ambient, 2 h | EN-1 | Measure ΔT of each switch and the enclosure; replace assumed K/W in `tools/budget.py` |
| TH-2 | TH-1 at 85 °C ambient (oven), 1 h | EN-1 | No thermal shutdown; derating engages as designed |
| TH-3 | −40 °C cold start (freezer to −20 °C as approximation) | EN-1 | Normal start; current calibration within FN-3 |

## Sleep and CAN

| ID | Test | Closes | Pass |
|---|---|---|---|
| SL-1 | Sleep current, IGN off, CAN idle | EL-7 | ≤ 250 µA |
| SL-2 | Wake on IGN, CAN frame, each input | — | Wakes within 150 ms |
| CN-1 | Full message set against `can/pcm.dbc` (decode with cantools/SavvyCAN) | FN-8 | All signals decode as specified |
| CN-2 | Host loss with each `on_host_loss` mode | FN-10 | Behaviour as configured |
| CN-3 | CAN-H and CAN-L shorted to 12 V and 24 V | EL-9 | Bus recovers after removal; no damage |
| CN-4 | CAN 2 on a live vehicle bus with a logic analyser on TXD and the bus | FN-9 | No dominant bit ever originates from the module |
| CN-5 | Four modules on one bus, addresses 0–3 | FN-11 | No ID clashes, all controllable |

## Environment

| ID | Test | Closes | Method |
|---|---|---|---|
| EV-1 | Immersion 1 m, 30 min, after thermal cycling | EN-2 | Tank; check inside for moisture |
| EV-2 | Vibration, body-mounted profile | EN-3 | **lab**; approximation: 100 h on the vehicle off-road with a logging host |
| EV-3 | Pressure wash on connectors | EN-2 | Garden test; no ingress |

## Vehicle

| ID | Test | Pass |
|---|---|---|
| VH-1 | Install on the JK, all four loads, 2 weeks daily use | No unexpected behaviour; logs reviewed |
| VH-2 | Sniff CAN-C, populate the vehicle signal map (speed, gear, high beam) | Signals decode and track the vehicle |
| VH-3 | Trail day with a logging host on CAN 1 | No nuisance trips; temperatures within TH-2 |
