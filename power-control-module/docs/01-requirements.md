# 01 — Requirements

Requirement IDs are stable; reference them from schematics, firmware and
tests. **Shall** is mandatory for rev A, **should** is a goal.

## Use cases (Jeep JK baseline)

| ID | Use case | Typical load | Trigger |
|---|---|---|---|
| UC-1 | Front LED light bar | 15–25 A, capacitive LED driver input | Dash toggle, CAN keypad, optional high-beam interlock |
| UC-2 | A-pillar / ditch pods | 2–8 A per pair | Toggle or CAN |
| UC-3 | Rear chase / flood lights | 4–10 A | Reverse signal from trailer harness, toggle, CAN |
| UC-4 | Rock lights (dimmable) | 2–6 A, PWM | CAN, timer |
| UC-5 | On-board air compressor | 30–50 A running, 3–5× inrush for ~100–300 ms | Toggle + tank pressure switch, interlocked to engine running |
| UC-6 | Relay / solenoid coil (winch contactor, air locker, horn relay) | < 2 A, inductive | Toggle or CAN |
| UC-7 | Fridge / radio feed with low-voltage cut-off | 3–10 A continuous | Always-on with load shed |

Out of scope: winch motor current (200–450 A), anything needing H-bridge
reversal, 24 V-only vehicles (24 V tolerated for jump-start only, see EL-4).

## Functional

| ID | Requirement |
|---|---|
| FN-1 | The module **shall** provide 4 high-side switched outputs. |
| FN-2 | Each output **shall** be built from one of three channel classes (S 10 A, M 20 A, L 40 A continuous) chosen at assembly time; firmware **shall** detect the class fitted in each slot. |
| FN-3 | Each output **shall** measure load current; accuracy ±5 % of reading above 20 % of rating, ±0.3 A below. |
| FN-4 | Each output **shall** have a hardware short-circuit trip that works with the MCU halted. |
| FN-5 | Each output **shall** have a configurable firmware electronic fuse (rating, I²t curve, inrush blanking, retry count). |
| FN-6 | S and M outputs **shall** support PWM (dimming, soft-start); L output **shall** support soft-start. |
| FN-7 | The module **shall** provide 4 configurable inputs: active-high, active-low (ground switch), or analog 0–16 V; plus a dedicated ignition/wake input. |
| FN-8 | The module **shall** accept commands and report status on an accessory CAN bus (ISO 11898-2, 500 kbit/s default). |
| FN-9 | The module **should** listen (never transmit) on a second CAN bus tapped from the vehicle. |
| FN-10 | The module **shall** run configured rules autonomously with no CAN host present, and **shall** define behaviour on loss of a previously present host. |
| FN-11 | Up to 4 modules **shall** coexist on one CAN bus, addressed by a strap. |
| FN-12 | Configuration **shall** persist across power loss and be readable/writable over CAN and USB. |
| FN-13 | Firmware **shall** be updatable over USB without opening the enclosure seal on the harness side; over CAN **should**. |
| FN-14 | Outputs **shall** default OFF through reset, brown-out, watchdog and firmware update. |

## Electrical environment (12 V vehicle)

Test methods are in [09-validation-plan.md](09-validation-plan.md).

| ID | Requirement | Reference |
|---|---|---|
| EL-1 | Full function 9–16 V; outputs held and logic alive 6–9 V (cranking); logic survives 4.5 V dips with reset-free recovery as a goal. | ISO 16750-2 starting profile |
| EL-2 | Survive suppressed load dump (clamped ≤ 35 V at the module). Vehicles without alternator suppression need an external clamp. | ISO 16750-2 pulse 5b |
| EL-3 | Survive ISO 7637-2 pulses 1, 2a, 3a, 3b on the battery feed. | ISO 7637-2 |
| EL-4 | Survive 24 V jump start for 60 s with outputs commanded on. | ISO 16750-2 |
| EL-5 | Survive −14 V reverse battery for 60 s without damage; logic and L channel **shall** block reverse current. | ISO 16750-2 |
| EL-6 | Survive loss of module ground with outputs on, and with any output shorted to battery. | — |
| EL-7 | Sleep current ≤ 250 µA with ignition off and outputs off (estimate 145 µA, [budget](../tools/budget.py)). | — |
| EL-8 | Total continuous current ≤ 80 A through the battery stud. | — |
| EL-9 | CAN inputs survive ±27 V DC on CAN-H/CAN-L (short to battery). | ISO 11898-2 |

## Environmental and mechanical

| ID | Requirement |
|---|---|
| EN-1 | Operating ambient −40 °C to +85 °C (engine bay away from exhaust); full ratings to +65 °C, firmware derates above. |
| EN-2 | IP67 sealed enclosure with pressure-equalising membrane vent; connectors sealed when mated. |
| EN-3 | Vibration per ISO 16750-3, body-mounted profile; no through-hole parts heavier than 5 g without adhesive staking. |
| EN-4 | Conformal coating on both boards except connectors, test points and the USB port. |
| EN-5 | Envelope target 130 × 110 × 45 mm, 4 × M6 mounting. |

## Non-goals for rev A

- Bluetooth/phone app (reserved as an optional companion board, see roadmap).
- Transmitting on the vehicle CAN bus.
- Motor speed control on the L channel.
- Certification (E-mark, FCC). Design follows the standards above so
  certification is possible later, but rev A is a personal off-road build.
