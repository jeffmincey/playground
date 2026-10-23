# 08 — Mechanical, connectors and wiring

## Enclosure — printed shell on an aluminium base plate

The JK module mounts in the cab ([11](11-jeep-jk-integration.md#mounting-location-cab))
and its enclosure is printed on the Bambu Lab X1C, on top of a flat
aluminium plate that does the heat sinking and mounting (decision D-13).
The [thermal table](03-output-channels.md#thermal-check) is why the plate is
not optional: a printed-only box traps the heat and runs its own walls above
ASA's softening point.

| Item | Choice |
|---|---|
| Base plate | 6 mm 6061 aluminium, ~170 × 130 mm, flat-bar stock or laser/water-jet cut; 4 × M6 mounting holes on the plate, outside the shell |
| Heat path | Power board → 1 mm gap pad → plate → vehicle structure. Bolt the plate to metal where possible. |
| Shell | ASA printed on the X1C (cab). Engine-bay builds: PET-CF or PAHT-CF (see [materials](#printed-materials)). Target outside 160 × 120 × 50 mm. |
| Seal | Groove in the shell rim with 2 mm silicone cord, or a printed TPU 95A gasket; ~25 % compression; screws every ≤ 50 mm around the rim |
| Fasteners | M3/M4 brass heat-set inserts in the shell; never self-tapping screws into plastic for anything that will be opened again |
| Connectors | Flange-mount sealed receptacles bolted through the shell wall (with their flange gaskets and a backing plate), short pigtails to board headers inside |
| Board stack | Power board (on the plate) → 2 × 25 board-to-board header + 2 × M3 standoffs → logic board |
| Venting | Screw-in pressure-equalising membrane vent. A sealed box that heats and cools pumps moist air past its gaskets; a membrane vent stops that. |
| Coating | Acrylic or silicone conformal coat on both boards (EN-4), masked at connectors, test points, USB |
| Service | USB-C and address strap under a printed screw cap with an O-ring, not on the harness side |
| Ingress target | IP65 in the cab (EN-2); verify with test EV-1 |

### Printed materials

Heat deflection temperatures from Bambu Lab data (ASA/PC from Bambu's
filament guide and ASA data sheet, PET-CF from its TDS, PAHT-CF from a
reseller quoting Bambu) — confirm on the current data sheets:

| Material | HDT @ 0.45 MPa | Use here | Notes |
|---|---:|---|---|
| PLA, PETG | roughly 55–70 °C | Mock-ups and fit checks only | Softens in a parked cab in summer |
| **ASA** | 100 °C (92 °C @ 1.8 MPa) | Cab shell, panel bezel, cab brackets | Prints well in the X1C's enclosed chamber; UV-stable |
| PC | 117 °C | Cab shell if ASA creeps in testing | Must be dried; warps more |
| ASA-CF | 110 °C | Stiffer cab brackets | Hardened nozzle |
| **PET-CF** | 205 °C (182 °C @ 1.8 MPa) | Engine-bay shell or brackets (relay, contactor, connector holders) | Hardened steel nozzle; dry before printing |
| **PAHT-CF** | 194 °C | Engine-bay parts near the battery and the engine | Hardened steel nozzle required; nylon absorbs water within hours — dry it and print from a dry box |
| TPU 95A | — | Gaskets, grommets, cable boots | Feed from an external spool, not through the AMS |

Rules for printed parts that must seal or carry load:

- Sealing faces printed flat and facing up, with the seam placed away from
  the gasket path; ≥ 4 walls and 100 % infill within 10 mm of any sealing
  face or insert.
- Orient brackets so layer lines are not loaded in peel (layers are the weak
  direction); add metal inserts or through-bolts where cables pull.
- Anything carrying battery-cable strain (winch contactor, ARB relay) gets a
  metal bracket or a PET-CF/PAHT-CF bracket with metal inserts, and the
  cables are clamped separately.

### Printed parts

| Part | Material | Notes |
|---|---|---|
| Module shell + service cap | ASA | Generated from the KiCad board outline once the PCBs are laid out (roadmap phase 4) |
| Gasket | TPU 95A (or silicone cord) | |
| Under-dash mounting bracket | ASA | Fit-check first with a PLA mock-up of the module |
| Switch panel bezel | ASA | See [switch panel](#switch-panel) |
| Winch contactor and ARB relay brackets | PET-CF / PAHT-CF with inserts, or aluminium | Engine bay |
| Firewall pass-through boot | TPU 95A | Around the 6 AWG feed and output bundle |

The CAD lives in [`../mechanical/`](../mechanical/README.md).

## Switch panel

The CAN host for the JK build, and the reason the module needs few physical
switches. Planned as a small companion board (roadmap phase 5):

| Item | Plan |
|---|---|
| Electronics | STM32G0 + CAN transceiver; 6–8 backlit momentary buttons with status LEDs |
| Protocol | Sends `Command.VINn` for its buttons; reads `Status`, `Aux` and `Diag` to drive the LEDs (on, blocked, fault, winch armed/override) |
| Power | Fused battery feed from J6 `PANEL_PWR`; own sleep mode ≤ 100 µA with ignition off, woken by a button press, which wakes the module over CAN |
| Housing | ASA bezel printed on the X1C for a JK dash location (to be measured on the vehicle) |
| Fallback | Physical toggles on IN5/IN6 keep the light bar and pods usable without it |

## Connectors

Contact ratings are the series' nominal values — check the specific contact
part and wire gauge. Part numbers for flange-mount receptacles vary by
series; pick the flange variant of each.

| Ref | Function | Connector | Contacts |
|---|---|---|---|
| J1 | Battery + | M6 brass stud on an insulated terminal block fixed to the base plate (a printed wall cannot take the nut torque), insulating boot | 6 AWG ring (JK); 4 AWG for `LMSS` |
| J2 | Module ground | **M5** stud on the same block (deliberately different size from J1 so the ring terminals cannot be swapped) | 12 AWG ring |
| J3 | L-slot output (`LMSS` only) | Deutsch DTHD 1-way, size 8 contact (~60 A) | 8 AWG |
| J4 | OUT1–OUT4 (M/S slots) | Deutsch DTP 4-way, size 12 contacts (~25 A) | 10–14 AWG |
| J5 | Inputs | Deutsch DT 12-way, size 16 contacts | 18–20 AWG |
| J6 | CAN (accessory, OBD port, CAN-IHS) + panel power | Deutsch DT 12-way | 20 AWG twisted pairs |
| J7 | AUX outputs | Deutsch DT 6-way | 18 AWG |

On variants with an L slot, J3 carries that slot and J4 the remaining three
S/M slots (pin 4 spare); the connector families do not change.

### J4 — outputs (`MMSS`)

| Pin | Signal | JK load |
|---|---|---|
| 1 | OUT1 (M) | Light bar |
| 2 | OUT2 (M) | Front pods |
| 3 | OUT3 (S) | Rear floods |
| 4 | OUT4 (S) | Rock lights |

### J5 — inputs

| Pin | Signal | Notes |
|---|---|---|
| 1–8 | IN1–IN8 | JK allocation in [04](04-inputs.md#example-jk-input-allocation) |
| 9 | IGN | Ignition-switched, 2 A fuse at the tap |
| 10 | +5V_SENS | 50 mA protected sensor supply |
| 11 | SIG_GND | Sensor / switch reference |
| 12 | SIG_GND | |

### J6 — CAN and panel

| Pin | Signal | Notes |
|---|---|---|
| 1 | CAN1_H | Accessory bus in |
| 2 | CAN1_L | |
| 3 | CAN1_H | Accessory bus out (daisy chain) — internally connected to 1 |
| 4 | CAN1_L | Internally connected to 2 |
| 5 | PANEL_PWR | Battery via 1 A PTC on the power board (not switched; the panel sleeps itself) |
| 6 | GND | Panel ground |
| 7 | CAN2_H | OBD-II pin 6 |
| 8 | CAN2_L | OBD-II pin 14 |
| 9 | CAN3_H | CAN-IHS H |
| 10 | CAN3_L | CAN-IHS L |
| 11 | GND | Vehicle-bus signal ground (OBD-II pin 5) |
| 12 | — | Not connected |

### J7 — AUX outputs

| Pin | Signal | JK load |
|---|---|---|
| 1 | AUX1 | ARB relay coil (via ARB pressure switch) |
| 2 | AUX2 | Winch contactor coil (via diode D1) |
| 3 | AUX3 | ARB rocker indicator |
| 4 | AUX4 | Spare |
| 5 | GND | Return for loads that need one at the module |
| 6 | GND | |

## Harness

From `python3 tools/budget.py` (20 °C copper; hot copper is ~15–20 % worse),
module in the cab. "One-way" is the module-to-load distance; for the lights
the drop includes a wired return to a chassis ground point.

| Run | Current (A) | AWG | One-way (m) | Drop (V) | Drop at 13.5 V (%) |
|---|---:|---:|---:|---:|---:|
| Battery feed, engine bay to cab module | 60 | 6 | 2.5 | 0.19 | 1.4 |
| Light bar (OUT1, M) | 20 | 10 | 3.5 | 0.46 | 3.4 |
| Front pods (OUT2, M) | 12 | 12 | 3.0 | 0.38 | 2.8 |
| Rear floods (OUT3, S) | 10 | 14 | 3.0 | 0.50 | 3.7 |
| Rock lights (OUT4, S) | 6 | 16 | 3.0 | 0.47 | 3.5 |
| ARB relay coil (AUX1) | 0.2 | 18 | 3.0 | 0.01 | 0.1 |
| Winch contactor coil, pull-in (AUX2) | 3.8 | 18 | 3.0 | 0.24 | 1.8 |

Rules:

- **Fuse the battery feed at the battery**: 80 A MIDI/MEGA fuse or a
  manual-reset breaker within ~300 mm of the post. Not an auto-reset
  (type I) breaker — it would cycle a fault through the firewall. The module
  protects its outputs; only that fuse protects the feed.
- Size output wire for the channel's **hardware** trip, not its firmware
  setting ([03](03-output-channels.md#protection-layers)).
- Return each load to a clean chassis point near the load; do not bring load
  returns back to J2.
- Cross the firewall through an existing grommet or a sealed bulkhead, with a
  printed TPU boot; keep clear of the exhaust and the steering shaft.
- Use cross-linked (GXL/TXL) wire in the engine bay, convoluted loom over
  everything, and a drip loop below each connector.
- Mount the module with connectors facing down or sideways, never up.
