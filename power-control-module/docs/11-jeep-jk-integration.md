# 11 — Jeep JK integration

How the module connects to a 2007–2018 Wrangler JK: power, wired signals,
the vehicle networks, and the mounting location. Anything marked
*community* comes from owner reverse-engineering, not FCA documentation, and
must be confirmed on the actual vehicle before a rule depends on it.

## Summary

| Interface | Where | Port | Direction |
|---|---|---|---|
| Battery feed | Battery + (driver side, engine bay), 80 A fuse at the battery | J1 | Power in |
| Module ground | Body ground point near the module | J2 | — |
| Ignition | Add-a-fuse tap in the TIPM, 2 A | J5 `IGN` | In |
| Reverse | Trailer harness reverse circuit (any year, any transmission) | J5 `IN2` | In |
| CAN-IHS (interior, 125 kbit/s) | Radio or instrument-cluster harness, pass-through pigtail | J6, CAN3 | **Listen-only, hardware-enforced** |
| OBD-II port (diagnostic CAN, 500 kbit/s) | DLC under the dash, Y-cable | J6, CAN2 | Listen; optional OBD-II polling (see below) |
| ARB rocker, light toggles | Dash | J5 `IN1`, `IN5`, `IN6` | In |
| Winch contactor coil and winch-side sense | Engine bay, through the firewall | J5 `IN3`, `IN4` | In |
| Compressor relay, winch contactor | Engine bay, coil wires through the firewall | J7 | AUX out |

## Mounting location: cab

Decision D-12. The question was engine bay or cab; with the compressor and
winch switched by their own relay and contactor (see [12](12-compressor-and-winch.md)),
the module only carries lighting current, which settles it:

| | Cab (chosen) | Engine bay |
|---|---|---|
| Ambient (design point) | 65 °C | 85 °C+ |
| Hottest junction, `MMSS`, printed shell + Al plate | 106 °C | 126 °C |
| Enclosure base temperature | 81 °C — ASA is fine (HDT 100 °C) | 101 °C — needs PET-CF / PAHT-CF |
| Water | Splash and wash-outs; mount high | Spray, fording, mud |
| CAN taps (DLC, radio/cluster) | Under the dash, short stubs | Through the firewall, long stubs |
| Dash switches / panel | Short runs | Through the firewall |
| Battery feed | 6 AWG through the firewall (2.5 m, 0.19 V drop at 60 A) | Under 1 m |
| Front light outputs | Back out through the firewall | Short |
| Compressor relay / winch contactor | Thin coil wires through the firewall | Short |

Thermal figures from `python3 tools/budget.py`. Something crosses the
firewall either way; in the cab it is mostly thin signal wire and one 6 AWG
feed, and everything electronic lives in the cooler, drier place.

Location in the cab: high on the passenger side under the dash, clear of the
HVAC box and the steering column, and **above floor level** — JK floors are
drained, hosed out and get wet in water crossings. Check the space with a
printed mock-up before committing (see [08](08-mechanical-and-wiring.md#printed-parts)).

## Power and ground

- **Battery feed:** 6 AWG from battery + through an **80 A fuse or
  manual-reset breaker within ~300 mm of the post**. Avoid auto-reset
  (type I) breakers: on a fault they cycle and reheat the cable through the
  firewall. Pass the firewall through an existing grommet or a sealed
  bulkhead with a rubber boot, away from the exhaust and the steering shaft.
- **Module ground:** 12 AWG to a body ground point near the module (it
  carries only logic and coil current). Load returns go to chassis near each
  light, as before.
- **Ignition:** add-a-fuse in an ignition-switched TIPM slot, 2 A fuse,
  18 AWG to `IGN`. Verify the chosen slot is dead with the key off.
- **Never** tap or route along the yellow SRS (airbag) harness or connectors.

## Wired signals (work on every JK)

| Signal | Source | Notes |
|---|---|---|
| Reverse | Trailer harness reverse circuit, or the reverse-lamp feed | Works for manual and automatic; `ACTIVE_HIGH`, 50 ms debounce |
| High beam | Headlamp connector feed | Fallback only — prefer the CAN-IHS light status. Some aftermarket LED headlamps alter this circuit (owners report swapped high/low indications with LED headlamps). |
| Engine running | Derived from VBAT > 13.2 V for 5 s | Fallback when no RPM signal |

## Vehicle networks

### What is on the JK

| Bus | Speed | Physical layer | Where to reach it | What it carries |
|---|---|---|---|---|
| CAN-C | 500 kbit/s | High-speed (ISO 11898-2) | Powertrain/chassis modules; not directly at the DLC on a JK (*community*) | Engine, transmission, ABS |
| Diagnostic CAN at the DLC | 500 kbit/s | High-speed | OBD-II pins 6 (H) / 14 (L), grounds 4/5 | Diagnostic traffic; gatewayed by the TIPM (*community*) |
| CAN-IHS | 125 kbit/s | High-speed (both lines idle near 2.5 V) | No central connector — splices in the harness. Candidate taps: radio harness (C2), instrument-cluster connector | Body and interior: lights, doors, radio, cluster |

Correction to the first revision of [05](05-logic-power-can.md): the
interior bus on the JK is documented by owners as **CAN-IHS at 125 kbit/s**
(high-speed physical layer), not a low-speed fault-tolerant CAN-B. A standard
high-speed transceiver works. Confirm on the vehicle (both lines near 2.5 V
at idle, traffic at 125 kbit/s) before wiring permanently.

### CAN-IHS — primary vehicle tap (listen-only, CAN3)

- **Why primary:** the instrument cluster sits on CAN-IHS, so the values it
  displays (vehicle speed, engine RPM, gear on automatics, lamp status) are
  very likely present there, gatewayed from CAN-C by the TIPM. Confirm by
  sniffing.
- **Tap points (verify against a wiring diagram for the model year):**
  - Radio harness — the published JK CAN-IHS write-up used the radio's C2
    connector, built as a pass-through pigtail from mating radio connectors
    so no factory wire is cut.
  - Instrument cluster — one older install listing gives CAN-IHS H on the
    brown 20-pin cluster connector pin 16 (white/grey) and L on pin 15.
- **Candidate message (*community*, unverified):** ID `0x208`, byte 0 —
  bit 0 left turn, bit 1 right turn, bit 3 parking lamps, bit 4 low beam,
  bit 5 high beam. The same post's example frames are labelled `0x308`, so
  capture and confirm which ID changes when the high-beam stalk moves.
- Transmit is physically impossible on CAN3: the transceiver `TXD` is tied
  recessive with no link to the MCU.

### OBD-II port — secondary tap (CAN2)

Owners disagree on whether the JK DLC carries broadcast traffic or stays
quiet until a tester asks. The first sniffing step settles it:

| DLC behaviour | Module mode | How |
|---|---|---|
| Broadcast traffic present | Listen-only | Same as CAN3 |
| Quiet until asked | **OBD-II polling** (optional) | Module sends standard SAE J1979 mode 01 requests to `0x7DF`, reads `0x7E8+` replies |

OBD-II polling is the one exception to "never transmit on a vehicle bus"
(decision D-7, amended), with these limits:

- Hardware: the CAN2 `TXD` link is a solder jumper, **not fitted by
  default**. Polling cannot start until someone fits it.
- Firmware whitelist: only ID `0x7DF`, only mode `0x01`, only configured
  PIDs; ≤ 10 requests/s total; IGN on only.
- Backs off when another tester is seen on the port (a scan tool or tuner
  plugged into the Y-cable), reported as `Health.OtherTesterSeen`.
- Any transmit error disables polling until the next ignition cycle; the
  controller's automatic retransmission is off so a fault cannot flood the
  port.

Standard PIDs (SAE J1979):

| PID | Value | Formula |
|---|---|---|
| `0x0C` | Engine RPM | (256·A + B) / 4 |
| `0x0D` | Vehicle speed | A km/h |
| `0x05` | Coolant temperature | A − 40 °C |

If CAN-IHS supplies speed and RPM, polling is unnecessary and the jumper
stays off.

### Bus etiquette

- No termination at the module's vehicle ports (none fitted on CAN2/CAN3).
- Keep stubs short: twisted pair, ≤ ~1 m from the tap to the module; the
  module sits under the dash for this reason.
- Splice by soldering and heat-shrink, or better, pass-through pigtails.
  No insulation-displacement taps on CAN wires.
- The vehicle-bus transceivers are unpowered in sleep; they are chosen for
  passive (high-impedance) behaviour when unpowered, so the module never
  loads the bus with the key off.

## Sniffing procedure

1. Build the OBD-II Y-cable and the CAN-IHS pass-through pigtail; check
   CAN-H/CAN-L idle voltages (~2.5 V each) with the key on.
2. Capture with the module in listen-only mode, or with a USB-CAN adapter in
   listen-only mode and SavvyCAN, at 125 kbit/s (IHS) and 500 kbit/s (DLC).
3. Record 30 s of baseline with the key on and the engine off, then again
   with the engine running.
4. Change one thing at a time — high beam, parking lamps, reverse, a door,
   driving at a steady speed — and diff the captures for the bits that follow.
5. Enter each signal in `vehicle_signals` in the configuration (bus, ID,
   start bit, length, byte order, scale, timeout).
6. Verify with the module's `VehicleA`/`VehicleB` telemetry before any rule
   uses the signal. Rules treat a stale signal as false.

## Features this enables

| Feature | Signals |
|---|---|
| Light bar only with high beams; drops with them when dipping for oncoming traffic (optional) | CAN-IHS high beam |
| Off-road lights auto-off above a set speed | Vehicle speed |
| Rear floods on in reverse, 60 s off-delay, off above 15 km/h | Reverse (wire), speed |
| Rock lights on with a door open (courtesy), off above 15 km/h | Door status (to be found), speed |
| Compressor only with the engine running | RPM, or VBAT fallback |
| Winch isolator auto-disarm when driving | Vehicle speed |

## What the module never does on the Jeep

- Transmit on CAN-IHS or any bus other than the optional, whitelisted
  OBD-II polling on the DLC.
- Send messages to the cluster, radio or body modules (no EVIC messages, no
  lighting commands).
- Connect to SRS wiring.

## Model year and transmission

| Item | Affects |
|---|---|
| Model year | Radio type and CAN-IHS tap point; message IDs may differ between years |
| Automatic vs manual | Whether gear is on the bus (automatic); manual uses the reverse wire |
| Aftermarket headlamps / radio | Can change the lamp and radio-harness signals |

These are open question Q-10 in [10](10-decisions-and-open-questions.md).
