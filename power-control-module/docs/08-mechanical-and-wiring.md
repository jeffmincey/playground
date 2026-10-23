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
| Shell | ASA printed on the X1C (cab). Engine-bay builds: PAHT-CF, see [engine-bay build](#engine-bay-build). Target outside 160 × 120 × 50 mm. |
| Seal | Groove in the shell rim with 2 mm silicone cord, or a printed TPU 95A gasket (cab only); ~25 % compression; screws every ≤ 50 mm around the rim |
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
| **PET-CF** | 205 °C (182 °C @ 1.8 MPa) | Engine-bay brackets (relay, contactor, connector holders) | Hardened steel nozzle; dry before printing. Polyester can hydrolyse when held hot and wet for long periods, so it is second choice for the engine-bay shell. |
| **PAHT-CF** | 194 °C (Vicat 220 °C) | Engine-bay shell (preferred) and parts near the battery | PA12-based: lower water uptake than ordinary PA-CF, and nylon 12 is the usual automotive fuel-line polymer. Hardened steel nozzle; resellers quote drying at 80 °C for 8–12 h and storage below 20 % RH. Hard to bond or coat (low surface energy). |
| TPU 95A | — | Cab gaskets, grommets, cable boots | Not for engine-bay seals: it softens and takes a compression set at 100 °C+; use silicone there. Feed from an external spool, not through the AMS. |

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
| Gasket | TPU 95A or silicone cord (cab build); silicone only in the engine bay | |
| Under-dash mounting bracket | ASA | Fit-check first with a PLA mock-up of the module |
| Switch panel bezel | ASA | See [switch panel](#switch-panel) |
| Winch contactor and ARB relay brackets | PET-CF / PAHT-CF with inserts, or aluminium | Engine bay |
| Firewall pass-through boot | TPU 95A on the cab side; silicone or EPDM grommet on the engine side | Around the 6 AWG feed and output bundle |

The CAD lives in [`../mechanical/`](../mechanical/README.md).

## Engine-bay build

Mounting in the engine bay is a supported alternative to the cab (decision
D-19), and the shell can still be printed — but only on the aluminium base
plate, only in PAHT-CF (or PET-CF), and only with the changes below. The
numbers behind it are in the [thermal check](03-output-channels.md#thermal-check):
at 85 °C ambient the printed-shell-on-plate build runs its hottest junction
at 120–126 °C with the base at 95–101 °C; at a 105 °C hot spot it needs the
low-loss M+ part on the light-bar slot.

### What changes from the cab build

| Area | Cab build | Engine-bay build |
|---|---|---|
| Location | Under the dash | Front of the bay, high (above fording depth), clear of the exhaust, out of the battery's vent and spill path, **never on the engine**. Log the spot first (Q-14). |
| Design ambient | 65 °C | 85 °C moving, 105 °C hot spot / slow crawl in summer, ~105 °C heat soak after shutdown (module mostly off) |
| Shell | ASA | **PAHT-CF**, solid walls ≥ 3 mm (100 % infill, ≥ 6 perimeters), printed slow and hot enough for full layer fusion |
| Base plate | 6 mm aluminium | Same, mandatory; bolt it to body metal through a thermal pad if the spot allows |
| Gasket | Silicone cord or TPU | **Silicone** cord or cut sheet only (rated well past 150 °C) |
| Clamping | Heat-set inserts in the shell | Bolts through the shell into **tapped holes in the plate**, with metal compression limiters in every shell hole so the plastic never carries the clamp load — CF-nylon creeps at 100 °C+ and would let the gasket relax |
| Expansion | — | Aluminium and the printed shell expand differently (~0.2–0.5 mm over this size and a 100 °C swing): oversize the shell's bolt holes and let the silicone gasket take the slip |
| Ingress target | IP65 | IP67, plus pressure wash and a hot-quench test (EV-4) |
| Vent | Membrane vent | Same, mandatory: a hot module driven into cold water contracts its air and sucks water through any leak path |
| Electronics | Grade 1 parts | Grade 1 parts — already the baseline for both builds ([05](05-logic-power-can.md#temperature-grade)) |
| Light-bar slot | M (BTS7002-1EPP) | M+ (BTS50015-1TAD) if the logged spot runs above ~95 °C; otherwise M with firmware derating |
| Harness | 6 AWG feed through the firewall; outputs back out | Feed under 1 m; rear floods and rock lights ~4.5 m, so 12 AWG to the floods; dash switches, panel and vehicle CAN through the firewall; GXL/TXL throughout |
| Vehicle CAN | Short stubs under the dash | 2–3 m stubs through the firewall: prefer the 125 kbit/s CAN-IHS tap (more stub-tolerant than the 500 kbit/s OBD port) and check for error frames (CN-8). The TIPM gateway sits next to the battery, so both buses pass through its connectors in the bay; tapping there would be short but needs the factory wiring diagram. |
| Extra tests | — | TH-5 heat soak, TH-6 hot-ambient operation, EV-4 hot quench, EV-5 fluids ([09](09-validation-plan.md)) |

### Sealing a printed shell

FDM walls are porous and layer seams leak under pressure; this is the main
risk of a printed engine-bay enclosure, not the heat. In order of
effectiveness:

1. Make the gasket and the plate do the sealing: one continuous silicone
   seal between the shell rim and the plate, connectors in the shell with
   their own flange gaskets, nothing else penetrating the shell.
2. Print the shell solid (100 % infill, thick walls) with good layer fusion;
   put the seam away from the gasket path; print sealing faces facing up.
3. If immersion testing still shows seepage, coat the outside. PA12 resists
   coatings, so prepare the surface (abrade, flame or primer treatment) and
   use a coating rated above the base temperature — many hobby epoxies
   soften around 60–80 °C.
4. If it still leaks, switch the shell to a die-cast aluminium box and keep
   the printed parts for brackets, connector shrouds and strain reliefs.

### What is not an option

- A printed shell **without** the aluminium plate: 148 °C junctions and a
  124 °C board even at 85 °C ambient.
- ASA, PC, PETG or PLA shells in the engine bay (softening points at or below
  the base temperature).
- TPU gaskets in the engine bay.
- Mounting on the engine or any engine-mounted bracket (heat and vibration).

### Lowest-risk engine-bay version

Die-cast aluminium enclosure (bought, machined for the connectors), with the
X1C printing the PAHT-CF mounting bracket, connector shrouds, strain reliefs,
and the relay and contactor brackets. It trades a few dollars and some
machining for no sealing uncertainty.

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
| J7 | AUX and keep-alive outputs | Deutsch DT 8-way | 18 AWG |

On variants with an L slot, J3 carries that slot and J4 the remaining three
S/M slots (pin 4 spare); the connector families do not change.

### J4 — outputs

| Pin | Signal | Front module (`MMSS`) | Rear module (`SSSS`) |
|---|---|---|---|
| 1 | OUT1 | Light bar (M) | Rear flood (S) |
| 2 | OUT2 | Bumper pods (M) | Rear rock lights (S), if fitted |
| 3 | OUT3 | Ditch lights (S) | RIGID Chase green, courtesy (S) |
| 4 | OUT4 | Front rock lights (S) | Camp lights (S), if fitted |

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

### J7 — AUX and keep-alive outputs

| Pin | Signal | Front module | Rear module |
|---|---|---|---|
| 1 | AUX1 | ARB relay coil (via ARB pressure switch) | RIGID Chase red, trail light |
| 2 | AUX2 | Winch contactor coil (via diode D1) | RIGID Chase white, brake |
| 3 | AUX3 | ARB rocker indicator | RIGID Chase yellow, strobe |
| 4 | AUX4 | Spare | RIGID Chase blue, reverse |
| 5 | KA1 | Keep-alive to the front turn/position injectors ([14](14-lamp-keep-alive-and-bluetooth.md)) | Unused |
| 6 | KA2 | Spare keep-alive | Unused |
| 7 | GND | Return for loads that need one at the module | RIGID Chase black, ground |
| 8 | GND | | |

## Harness

From `python3 tools/budget.py` (20 °C copper; hot copper is ~15–20 % worse),
two-module layout on the 2016 two-door JK ([13](13-multi-module-system.md)). "One-way" is the
module-to-load distance; for the lights the drop includes a wired return to a
chassis ground point.

| Module | Run | Current (A) | AWG | One-way (m) | Drop (V) | Drop at 13.5 V (%) |
|---|---|---:|---:|---:|---:|---:|
| Front | Battery feed to the glovebox module | 60 | 6 | 3.0 | 0.23 | 1.7 |
| Front | Light bar (OUT1, M) | 20 | 10 | 3.5 | 0.46 | 3.4 |
| Front | Bumper pods (OUT2, M) | 12 | 12 | 3.0 | 0.38 | 2.8 |
| Front | Ditch lights (OUT3, S) | 6 | 16 | 2.0 | 0.32 | 2.3 |
| Front | Front rock lights (OUT4, S) | 3 | 16 | 2.5 | 0.20 | 1.5 |
| Front | ARB relay coil (AUX1) | 0.2 | 18 | 3.0 | 0.01 | 0.1 |
| Front | Winch contactor coil, pull-in (AUX2) | 3.8 | 18 | 3.0 | 0.24 | 1.8 |
| Rear | Battery feed to the rear module, 10 AWG, at the 30 A fuse | 30 | 10 | 4.0 | 0.39 | 2.9 |
| Rear | Same 10 AWG feed at the expected 20 A | 20 | 10 | 4.0 | 0.26 | 1.9 |
| Rear | Rear flood (OUT1, S) | 8 | 14 | 1.5 | 0.20 | 1.5 |
| Rear | Rear rock lights (OUT2, S) | 4 | 16 | 2.0 | 0.21 | 1.6 |
| Rear | Camp lights (OUT4, S) | 4 | 16 | 3.0 | 0.32 | 2.3 |
| Rear | RIGID Chase, all five functions on (AUX1-4, OUT3) | 3.9 | 18 | 2.5 | 0.41 | 3.0 |

On the rear module the same connector set is fitted but partly used: J6
carries only CAN1 in/out and ground (no vehicle buses, no panel power), the
`IGN` in J5 comes through the front–rear trunk cable, and J7 drives four of
the RIGID Chase's five function wires and takes its ground; the green
courtesy wire comes from OUT3 on J4. The Chase row assumes all five
functions on and counts the full 3.9 A both ways, so it overstates the drop:
only the shared ground carries the sum.

Rules:

- **Fuse each battery feed at the battery**: 80 A (front module) and 30 A
  (rear module) MIDI/MEGA or ATO/ATC-class fuses, or manual-reset breakers,
  within ~300 mm of the post. Not an auto-reset
  (type I) breaker — it would cycle a fault through the firewall. The module
  protects its outputs; only those fuses protect the feeds.
- Size output wire for the channel's **hardware** trip, not its firmware
  setting ([03](03-output-channels.md#protection-layers)).
- Return each load to a clean chassis point near the load; do not bring load
  returns back to J2.
- Cross the firewall through an existing grommet or a sealed bulkhead, with a
  boot (printed TPU on the cab side, silicone or EPDM on the engine side);
  keep clear of the exhaust and the steering shaft.
- Use cross-linked (GXL/TXL) wire in the engine bay, convoluted loom over
  everything, and a drip loop below each connector.
- Mount the module with connectors facing down or sideways, never up.
