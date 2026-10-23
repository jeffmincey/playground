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
| BU-4 | Logic board removed, power board powered | All main and AUX outputs off (pull-downs) |
| BU-5 | Each AUX output into 0.2 A and 3 A loads; read both channels of each dual device via `AUX_DSEL` | Current reads correct per channel |

## Protection

| ID | Test | Closes | Pass |
|---|---|---|---|
| PR-1 | Hard short (≤ 10 mΩ) on each output and each AUX, MCU running | FN-4 | Hardware trip, no damage, fault reported, retries per config |
| PR-2 | PR-1 with the MCU halted by the debugger, output on | FN-4 | Hardware trip still protects; no damage |
| PR-3 | Overload at 1.5×, 2×, 3×, 5× rating | FN-5 | Trip time within ±20 % of the I²t table in [07](07-firmware.md#electronic-fuse) |
| PR-4 | `LMSS` only: single-motor compressor (or a motor + flywheel load) start, 10 cycles | FN-5 | No nuisance trip; inrush logged |
| PR-5 | Light bar start, cold, 10 cycles with and without soft-start | FN-6 | No trip with soft-start configured |
| PR-6 | Inductive turn-off: ARB relay coil, plain solenoid, economised contactor coil | — | Output voltage clamped; no device stress beyond datasheet |
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
| TR-7 | Winch-style sag: 13.5 → 8 V for 60 s, then 6.5 V for 5 s, with the winch contactor armed | EL-1 | Logic stays up; contactor drop-out voltage recorded |

## Thermal and enclosure

| ID | Test | Closes | Pass |
|---|---|---|---|
| TH-1 | All channels at rating, printed shell on the plate, 25 °C ambient, 2 h | EN-1 | Measure ΔT of each switch, the plate and the shell; replace assumed K/W in `tools/budget.py` |
| TH-2 | TH-1 at 65 °C ambient (oven), 2 h | EN-1 | No thermal shutdown; hottest junction within the budget prediction + 10 °C |
| TH-3 | −40 °C cold start (freezer to −20 °C as approximation) | EN-1 | Normal start; current calibration within FN-3 |
| TH-4 | Parked-cab soak: shell unpowered at 85 °C for 24 h, then gasket compression and insert pull-out checked | EN-2 | No warp beyond the gasket's compression range; inserts hold |
| TH-5 | Engine-bay build: heat soak unpowered at 105 °C for 24 h, ten cycles to 25 °C | EN-1, EN-2 | No shell warp, gasket still compressed, bolts at torque (compression limiters) |
| TH-6 | Engine-bay build: expected JK loads at 85 °C and 105 °C ambient, 2 h each | EN-1 | Junction estimate within 10 °C of the budget; derating engages above 125 °C estimated junction, never trips on temperature |

## Sleep and CAN

| ID | Test | Closes | Pass |
|---|---|---|---|
| SL-1 | Sleep current, IGN off, CAN idle | EL-7 | ≤ 250 µA; record the MCU's share |
| SL-2 | Wake on IGN, CAN frame, each input | — | Wakes within 250 ms |
| CN-1 | Full message set against `can/pcm.dbc` (decode with cantools/SavvyCAN) | FN-8 | All signals decode as specified |
| CN-2 | Host loss with each `on_host_loss` mode | FN-10 | Behaviour as configured |
| CN-3 | CAN-H and CAN-L shorted to 12 V and 24 V | EL-9 | Bus recovers after removal; no damage |
| CN-4 | CAN3 and CAN2 (jumper not fitted) on a live bus with a logic analyser on TXD and the bus | FN-9 | No dominant bit ever originates from the module |
| CN-5 | Four modules on one bus, addresses 0–3 | FN-11 | No ID clashes, all controllable |
| CN-6 | Module unpowered on a live vehicle bus | EL-10 | No error frames; bus load unchanged |
| CN-7 | OBD polling (jumper fitted): request rate, whitelist, back-off when a scan tool is connected, stop on bus-off | FN-9 | ≤ 10 req/s; only `0x7DF` mode 01; pauses with a tester present |
| CN-8 | Engine-bay build: vehicle taps with the real 2–3 m stub, scope on CAN-H/L at the tap | EL-10 | Clean edges; no error frames on the vehicle bus over a 30 min drive |

## Compressor and winch

| ID | Test | Closes | Pass |
|---|---|---|---|
| CW-1 | ARB loom on the bench with a dummy compressor load: rocker on/off, engine-running interlock (VBAT and RPM sources) | UC-5 | AUX1 follows the rules; blocked state shown on AUX3 |
| CW-2 | Pressure switch opened/closed by hand | UC-5 | AUX1 current tracks the switch; "running" state correct |
| CW-3 | Pressure switch held closed past `max_load_on_s` | UC-5 | `RUN_LIMIT`; cleared only by cycling the rocker |
| CW-4 | Winch contactor arm/disarm: long press, IGN off, speed, timer with and without `VBAT_SAG` | UC-8 | Disarms only under the configured conditions |
| CW-5 | Override switch with the module unpowered | FN-15 | Contactor closes and opens from the switch alone |
| CW-6 | Feedback faults: coil wire cut (fails to close), contactor studs bridged while off (simulated weld) | FN-16 | `FEEDBACK_MISMATCH` within the configured timeouts |

## Environment

| ID | Test | Closes | Method |
|---|---|---|---|
| EV-1 | Spray and splash (IP65 intent) after thermal cycling; immersion 1 m for 30 min for engine-bay builds | EN-2 | Hose / tank; open and check inside for moisture |
| EV-2 | Vibration, body-mounted profile | EN-3 | **lab**; approximation: 100 h on the vehicle off-road with a logging host |
| EV-3 | Pressure wash on connectors | EN-2 | Garden test; no ingress |
| EV-4 | Engine-bay build: hot quench — module running at 90 °C, then splashed and dunked in ~10 °C water for 5 min | EN-2 | No water inside (the fording case) |
| EV-5 | Engine-bay build: printed coupons with oil, coolant, brake fluid, fuel and dilute battery acid, 24 h at 80 °C | EN-2 | No softening, cracking or swelling beyond the gasket's tolerance |

## Two-module system

| ID | Test | Closes | Pass |
|---|---|---|---|
| SY-1 | Front module, rear module and panel on one bus with the real trunk cable; unpowered CAN-H to CAN-L resistance | FN-11 | ~60 Ω; every frame of both modules decodes with `can/pcm-jk.dbc` |
| SY-2 | Peer signals: rear rules using `M0.VS2` and `M0.OUT4`; then unplug the front module | FN-17 | Rear follows within 300 ms; with M0 gone the values go stale within 300 ms and the rules fall back as documented |
| SY-3 | Parked: IGN off, fridge on the rear module overnight | FN-18 | Front module sleeps between wake-ups; its average current ≤ 0.3 mA |
| SY-4 | State-change burst: front rock lights switched on with the rear module asleep | FN-18 | Rear rock lights follow within 1 s |
| SY-5 | Rear feed under 40 A: battery voltage estimate vs. a meter at the battery | — | `VBAT_EST` within 0.1 V |
| SY-6 | Ground offset between front and rear modules with all rear loads on | EL-9 | CAN common-mode within the transceiver's range; no error frames |

## Lamp keep-alive and Bluetooth

| ID | Test | Closes | Pass |
|---|---|---|---|
| KA-1 | Bench characterisation of each lamp that needs keep-alive ([14](14-lamp-keep-alive-and-bluetooth.md#measure-first)) | FN-19 | `V_alive`, `V_glow`, current (warm and in a freezer), boot time recorded; keep-alive level chosen with margin both sides |
| KA-2 | Injector on the vehicle, keep-alive on: first flash after idle, hazards, position lamps | FN-19 | No missing or late first flash; lamps dark at keep-alive |
| KA-3 | TIPM behaviour with the injector fitted, keep-alive on and off | FN-20 | No DTC, no hyperflash, no lamp-out warning (fit `R_load` if needed) |
| KA-4 | Module unpowered, and keep-alive wire unplugged | FN-20 | Turn, position and hazard lamps all work (boot delay allowed) |
| KA-5 | Keep-alive wire shorted to ground; lamp unplugged; D_f opened | FN-19 | eFuse trips and `KA_Fault` is reported; current band and flash-dip checks raise their faults |
| KA-6 | Parked with keep-alive rules: hazards with the key off | FN-18 | Keep-alive on from the second flash; off 10 min after the last |
| BT-1 | Bluetooth scan of the headlight with lights on and at keep-alive only | — | Services and characteristics listed; reachability at keep-alive recorded |
| BT-2 | Capture and map the J-Link app's writes for each mode and brightness step | — | Mapping table, including any pairing or authentication |
| BT-3 | Replay from a development board | — | Each mapped setting reproduced, or the protocol shown to be authenticated (stop) |

## Vehicle

| ID | Test | Pass |
|---|---|---|
| VH-1 | Install on the JK, all loads, 2 weeks daily use | No unexpected behaviour; logs reviewed |
| VH-2 | Sniff CAN-IHS and the OBD port; populate the vehicle signal map (speed, RPM, high beam, reverse) | Signals decode and track the vehicle in `VehicleA/B` |
| VH-3 | Trail day with a logging host on CAN1, including compressor use and a winch pull | No nuisance trips; temperatures within TH-2 |
