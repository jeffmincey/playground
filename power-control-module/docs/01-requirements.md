# 01 — Requirements

Requirement IDs are stable; reference them from schematics, firmware and
tests. **Shall** is mandatory for rev A, **should** is a goal.

## Use cases (Jeep JK baseline)

| ID | Use case | Typical load | Trigger | Output |
|---|---|---|---|---|
| UC-1 | Front LED light bar | 15–25 A, capacitive LED driver input | Panel, dash toggle, optional high-beam interlock | OUT (M) |
| UC-2 | Bumper / A-pillar / ditch pods | 2–12 A per group | Panel or toggle | OUT (M/S) |
| UC-3 | Rear chase / flood lights | 4–10 A | Reverse (trailer harness or vehicle bus), panel | OUT (S) |
| UC-4 | Rock lights (dimmable) | 2–6 A, PWM | Panel, door-open courtesy, timer | OUT (S) |
| UC-5 | ARB twin compressor (CKMTA12) | ~50 A under load through **ARB's own relay and pressure switch**; the module drives the relay coil (~0.2 A) | ARB rocker, interlocked to engine running | AUX |
| UC-6 | Relay / solenoid coils, indicators | < 5 A, inductive | Panel or rule | AUX |
| UC-7 | Fridge / radio feed with low-voltage cut-off | 3–10 A continuous | Always-on with load shed | OUT (S) |
| UC-8 | Winch isolator | Contactor coil: 3.8 A pull-in, 0.13 A hold (economised) | Panel arm, auto-disarm | AUX |

Out of scope: winch or compressor motor current through the module (they
have their own contactor/relay, see [12](12-compressor-and-winch.md)),
anything needing H-bridge reversal, 24 V-only vehicles (24 V tolerated for
jump-start only, see EL-4).

## Functional

| ID | Requirement |
|---|---|
| FN-1 | The module **shall** provide 4 high-side switched main outputs. |
| FN-1a | The module **shall** provide 4 AUX high-side outputs for coils and indicators: ≤ 5 A each, on/off, with current sense. |
| FN-2 | Each main output **shall** be built from one of three channel classes (S 10 A, M 20 A, L 40 A continuous) chosen at assembly time; firmware **shall** detect the class fitted in each slot. |
| FN-3 | Each main output **shall** measure load current; accuracy ±5 % of reading above 20 % of rating, ±0.3 A below. |
| FN-4 | Every output **shall** have a hardware short-circuit trip that works with the MCU halted. |
| FN-5 | Every output **shall** have a configurable firmware electronic fuse (rating, I²t curve, inrush blanking, retry count). |
| FN-6 | S and M outputs **shall** support PWM (dimming, soft-start); L output **shall** support soft-start. |
| FN-7 | The module **shall** provide 8 configurable inputs: active-high, active-low (ground switch), analog 0–16 V or frequency; plus a dedicated ignition/wake input. (Raised from 4 by decision D-17.) |
| FN-8 | The module **shall** accept commands and report status on an accessory CAN bus (ISO 11898-2, 500 kbit/s default). |
| FN-9 | The module **shall** read two vehicle buses: an interior bus (JK CAN-IHS) that it can never transmit on (hardware-enforced), and the OBD-II port, listen-only by default with optional, whitelisted OBD-II mode 01 polling ([11](11-jeep-jk-integration.md#obd-ii-port--secondary-tap-can2)). |
| FN-10 | The module **shall** run configured rules autonomously with no CAN host present, and **shall** define behaviour on loss of a previously present host. |
| FN-11 | Up to 4 modules **shall** coexist on one CAN bus, addressed by a strap. |
| FN-12 | Configuration **shall** persist across power loss and be readable/writable over CAN and USB. |
| FN-13 | Firmware **shall** be updatable over USB without opening the enclosure seal on the harness side; over CAN **should**. |
| FN-14 | Outputs **shall** default OFF through reset, brown-out, watchdog and firmware update. |
| FN-15 | A winch isolator controlled by the module **shall** remain operable with the module failed or unpowered, through a hardwired override that bypasses the module. |
| FN-16 | Any output **shall** support optional feedback supervision (an input that must follow the real-world state of the load), reporting `FEEDBACK_MISMATCH`. |

## Electrical environment (12 V vehicle)

Test methods are in [09-validation-plan.md](09-validation-plan.md).

| ID | Requirement | Reference |
|---|---|---|
| EL-1 | Full function 9–16 V; outputs held and logic alive 6–9 V (cranking, winching); logic survives 4.5 V dips with reset-free recovery as a goal. | ISO 16750-2 starting profile |
| EL-2 | Survive suppressed load dump (clamped ≤ 35 V at the module). Vehicles without alternator suppression need an external clamp. | ISO 16750-2 pulse 5b |
| EL-3 | Survive ISO 7637-2 pulses 1, 2a, 3a, 3b on the battery feed. | ISO 7637-2 |
| EL-4 | Survive 24 V jump start for 60 s with outputs commanded on. | ISO 16750-2 |
| EL-5 | Survive −14 V reverse battery for 60 s without damage; logic and L channel **shall** block reverse current. | ISO 16750-2 |
| EL-6 | Survive loss of module ground with outputs on, and with any output shorted to battery. | — |
| EL-7 | Sleep current ≤ 250 µA with ignition off and outputs off (estimate 193 µA, [budget](../tools/budget.py)). | — |
| EL-8 | Total continuous current ≤ 80 A through the battery stud (`LMSS`); 60 A for the JK `MMSS` build. | — |
| EL-9 | CAN inputs survive ±27 V DC on CAN-H/CAN-L (short to battery). | ISO 11898-2 |
| EL-10 | Vehicle CAN ports **shall** present no termination and high impedance when unpowered. | ISO 11898-2 |

## Environmental and mechanical

| ID | Requirement |
|---|---|
| EN-1 | Electronic components AEC-Q100/Q200 Grade 1 (−40…+125 °C) in every build. Module ambient: cab build −40…+85 °C (JK default, design point 65 °C, D-12); engine-bay build −40…+105 °C (D-19), with firmware derating on estimated junction temperature. |
| EN-2 | Cab build: IP65 with a pressure-equalising membrane vent (printed ASA shell on an aluminium base plate, D-13). Engine-bay build: IP67 plus pressure wash and hot-quench (EV-4), printed PAHT-CF shell on the plate or a die-cast box. Connectors sealed when mated in both. |
| EN-3 | Vibration per ISO 16750-3, body-mounted profile; no through-hole parts heavier than 5 g without adhesive staking. |
| EN-4 | Conformal coating on both boards except connectors, test points and the USB port. |
| EN-5 | Envelope target 160 × 120 × 50 mm, 4 × M6 mounting through the base plate. |

## Non-goals for rev A

- Bluetooth/phone app (reserved as an optional companion board, see roadmap).
- Transmitting on any vehicle bus, except the optional whitelisted OBD-II
  polling in FN-9.
- Motor speed control on the L channel.
- Certification (E-mark, FCC). Design follows the standards above so
  certification is possible later, but rev A is a personal off-road build.
