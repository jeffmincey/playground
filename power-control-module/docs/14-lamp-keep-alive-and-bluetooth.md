# 14 — Lamp keep-alive and Bluetooth lighting control

Two requirements from the JK's lamps:

1. **Keep-alive.** The turn-signal lamps must sit at about **6 V** while idle
   so their electronics stay booted, then go to **12 V** to light for turn,
   marker (front position) and hazard. Powered from 0 V, the lamp's
   controller boots on every flash and the first flash is late or missing.
2. **Bluetooth.** The headlights' brightness and modes are set over
   Bluetooth from a phone app; integrating that is to be investigated.

## The lamps involved

From J.W. Speaker product pages and retailer listings (confirm against the
lamps fitted — open question Q-20):

| Lamp | Relevant facts |
|---|---|
| J.W. Speaker **8700 EVO J3** headlights (most likely the fitted model, given the Bluetooth control) | Built-in turn signal, front position light and DRL alongside low/high beam; anti-flicker built in. The harness plugs into the JK's **factory front turn-signal plug** (wires: black ground, yellow low, white high, orange front turn). Bluetooth through the J-Link app (iOS and Android): Off-Road mode (optics tuned for width or brightness, rock-light feature), Guide and Party modes. J.W. Speaker notes the lamps must be on for Bluetooth to work. |
| J.W. Speaker **239 J2** grille turn signals | 12 V, 9–16 V operating; black ground, white front position, yellow turn; integrated anti-flicker. J.W. Speaker notes that the EVO J3's turn signal is already at the top of the DOT intensity range, so running factory-position turn lamps alongside it takes the setup out of compliance — decide which set is active. |

The 6 V figure is the requirement given for this build; it does not appear
in the published J.W. Speaker material found so far. Bench measurements
(below) set the real level.

## Measure first

Before any hardware, characterise one lamp on a bench supply (test KA-1):

| Measurement | Why |
|---|---|
| Which input powers the electronics (turn, position, or both) | Decides which wire gets the keep-alive |
| Lowest voltage that keeps the controller booted, `V_alive` | Keep-alive must stay above it |
| Voltage where any LED starts to glow, `V_glow` | Keep-alive must stay below it |
| Keep-alive current at the chosen level, warm and in a freezer | Sizes the rail and current limit; shows whether SmartHeat (heated versions) or anything else draws current at keep-alive |
| Boot time from 0 V, and response time from keep-alive to full light | Confirms the benefit |
| Whether Bluetooth is reachable at keep-alive | Decides whether the lamp can be configured with the headlights off |

The keep-alive level is then set between `V_alive` and `V_glow` with margin
on both sides — 6 V if the measurements agree.

## Architecture: inject the keep-alive, leave the factory in control

Turn signals and hazards are safety lamps. The factory flasher (TIPM) stays
in charge of them; the module only **adds** a keep-alive voltage underneath
(decision D-27).

```
TIPM turn / position output ──┬──►|── D_f ──┬──── lamp input (e.g. EVO J3 orange "front turn")
                              │             │
                       (sense, module input) │
                              │             │
      module KA output ───────┼──────►|── D_k┘
      (5–8 V, current-limited) │
                              └── optional R_load to ground (only if the TIPM complains)
```

- **Idle:** the TIPM output is off; the lamp sits at the keep-alive level
  through D_k (the rail is set ~0.3 V above the target to cover the diode).
- **Flash:** the TIPM drives 12 V; the lamp gets VBAT − ~0.3 V through D_f,
  D_k is reverse-biased. Between flashes the lamp drops back to keep-alive,
  not to 0 V, so it never reboots.
- **D_f** stops the keep-alive from back-feeding the TIPM output (which could
  look like a short to battery to its diagnostics). **D_k** stops 12 V from
  back-feeding the module. Schottky, ≥ 3 A, ≥ 40 V; conservative rating
  because D_f now sits in a safety circuit.
- **Sense the factory signal on the TIPM side of D_f**, never on the lamp
  side, which sits at keep-alive voltage.
- If the TIPM flags a lamp fault or hyperflashes with D_f fitted (it now sees
  an open circuit when off), add `R_load` on the TIPM side (start at 1 kΩ).
  Test KA-3 checks this.
- **Fails safe:** module dead or keep-alive off → the lamps work exactly as
  before, just with the boot delay. Hazards with the key off keep working,
  because the TIPM still drives them.

Physically, the two diodes per lamp input live in a small inline adapter at
each front lamp: mating JK turn-signal connectors, the diodes, a keep-alive
wire in from the module and a sense wire (through 10 kΩ, from the vehicle
side of D_f) back to it. The housing is printed on the X1C in
PAHT-CF (grille area: warm and wet), potted with silicone, with sealed
connectors.

### Why not let the module drive the lamps

The module could read the TIPM outputs as inputs and drive the lamps itself
with a three-level output (0 / keep-alive / 12 V). That gives full control,
but it puts a federally regulated safety function behind the module and
needs a fail-safe bypass for when the module fails — which is the injection
circuit above anyway. Not recommended.

## Keep-alive hardware on the logic board

| Item | Choice |
|---|---|
| Rail | Small 60 V synchronous buck, ≤ 1 A (LMR3600x-Q1 class), from `VBAT_LOGIC` |
| Level | 5.0–8.0 V, trimmed by an MCU DAC into the buck's feedback node; `keep_alive_v` in configuration |
| Outputs | `KA1`, `KA2`, each through an eFuse with adjustable current limit and a current-monitor output to the ADC (TI TPS2595 class: 2.7–18 V, 0.5–4 A; it is not AEC-Q100, so use an automotive equivalent where one fits) |
| Default limit | 0.5 A per output, set per lamp after KA-1 |
| Connector | J7, now DT 8-way ([08](08-mechanical-and-wiring.md#j7--aux-and-keep-alive-outputs)) |
| Sleep | Buck and eFuses off when parked |

This is the only load current the logic board carries.

## Control

Keep-alive outputs take rules like any other output
([07](07-firmware.md#keep-alive-outputs)):

| Condition | Keep-alive |
|---|---|
| IGN on | On |
| IGN off, turn or hazard activity seen | On, until 10 min after the last flash |
| Parked otherwise | Off — four lamps at keep-alive draw tens of mA from the battery, ~1 Ah/day if left on |

The front module senses the front turn circuits itself (IN7/IN8, wired from
the vehicle side of each injector), so hazards with the key off wake it
directly through the input scan. The first hazard flash may be late; the
rest are not. The front turn circuits carry turn and hazard only — unlike the
rear's combined stop/turn — so they also give a clean reference for the
flash-dip check below.

### Diagnostics

| Check | Detects |
|---|---|
| KA current inside the expected band while on | Lamp unplugged (too low), short or a heater drawing (too high) |
| KA current dips at each flash | During a flash the lamp runs from the TIPM through D_f, so keep-alive current should drop. No dip while IN7/IN8 show the TIPM side flashing → **D_f or its wiring is open**, and that lamp is running on keep-alive only — reported as `FEEDBACK_MISMATCH` |
| eFuse trip | Short on the keep-alive wire |

## Bluetooth brightness and modes

### What is known

- The J-Link app (iOS and Android, free) pairs lamps by scanning for them
  (serial number auto-filled), groups two headlights, and exposes
  Off-Road mode (width/brightness tuning, rock-light feature), Guide and
  Party modes on the EVO J3; brightness on the Trail 6 Pro.
- J.W. Speaker states the lamps must be on for Bluetooth to work. The app
  uses an account login.

### Integration options

| Option | Effort | Notes |
|---|---|---|
| Keep using the J-Link app | None | Works today; no automation |
| **Run J-Link on the NVGOTEV head unit** | A quick test | Only if the head unit's Android exposes Bluetooth LE to apps — many Android head units route Bluetooth through a separate module used only for phone calls and audio. Test: install nRF Connect on the head unit and scan for the headlights; if they appear, install J-Link there. Control then lives on the dash screen with no custom hardware. |
| **BLE bridge in the switch panel** | Investigation + firmware | The panel already sits in the cab on CAN1; give it a BLE-capable MCU (ESP32-S3 class: BLE + a TWAI CAN controller; or nRF52840 + an MCP2518FD). Panel buttons and module rules could then select lamp modes. |
| BLE in the module | Not recommended | Keeps a radio stack and its updates out of the module that switches the loads |
| Module status on the head unit | Later | An ESP32-S3-class panel MCU could also serve a small Wi-Fi status page that the head unit (or a phone) opens in a browser — no app, and no dependence on the head unit's Bluetooth |

### Investigation plan

1. **Identify:** confirm the headlight model and firmware; note which J-Link
   features it offers.
2. **Scan:** with nRF Connect (phone), list the lamp's advertising name,
   services and characteristics, with the headlights on and then at
   keep-alive only.
3. **Capture:** record the app's traffic while changing each setting —
   Android's Bluetooth HCI snoop log (developer options), or Apple's
   Bluetooth logging profile with PacketLogger on iOS — and open it in
   Wireshark.
4. **Map:** find the characteristic and the bytes written for each mode and
   brightness step; check whether bonding, encryption or an app-side token
   is involved (the account login and serial-number pairing hint that it
   might be).
5. **Replay:** send the same writes from a development board (ESP32-S3 or
   nRF52840). If replay works, the bridge is feasible; if the protocol is
   authenticated per session, stop and keep the app.
6. **Decide:** only then commit the panel to a BLE MCU (decision D-29).

Guard rails for any automation: Off-Road mode is for off-road use. The
bridge must never select it automatically on the road — at most when the
vehicle is slow and in 4LO, reverting to the road mode above a set speed —
and turn-signal and hazard intensity is never reduced. A lamp firmware
update can change the protocol, so the bridge must fail quietly back to
"no control".

## Open questions

Q-20 (which headlight model, and whether the 239 J2 grille lamps stay
active alongside the J3 turn signal), Q-21 (bench results: which input,
`V_alive`, `V_glow`, current, boot time), Q-22 (which phone is used for the
Bluetooth capture) — see [10](10-decisions-and-open-questions.md#open-questions).
