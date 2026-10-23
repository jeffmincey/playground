# 03 — Output channels

All outputs are high-side solid-state switches: the module switches battery
positive to the load and the load returns to chassis. Three channel classes
cover the main outputs; each is a *cell* that implements the
[slot interface](02-architecture.md#slot-interface). A fixed bank of four
small AUX outputs drives relay and contactor coils
([AUX bank](#aux-bank-coil-drivers)).

Part numbers are candidates. Figures marked † are typical datasheet values
recalled for sizing and **must be checked against the current datasheet**
before the BOM is frozen.

## Class summary

| | **S — small** | **M — medium** | **L — large** |
|---|---|---|---|
| Continuous rating | 10 A | 20 A (25 A ≤ 60 °C ambient) | 40 A |
| Typical loads | Pods, rock lights, rear floods, fridge feed | Light bars, paired pods | Single-motor compressor, large bar, fridge + inverter feed (not fitted on the JK `MMSS` build) |
| Switch | Infineon **BTS7004-1EPP** (PROFET+2 12 V, 4.4 mΩ†) | Infineon **BTS7002-1EPP** (PROFET+2 12 V, 2.6 mΩ†) | 4 × 60 V automotive N-MOSFET: 2 in parallel, back-to-back common-source |
| Alternates | BTS7006-1EPP (6 mΩ†); TI TPS1HB08-Q1 | BTS50015-1TAD (1.5 mΩ†, TO-263-7) for a 25–30 A M+ cell | Infineon 2ED2410-EM dual-channel driver (natural fit for an `LL` variant) |
| Driver | Integrated | Integrated | TI **TPS48111-Q1** smart high-side gate driver |
| Current sense | PROFET `IS` current mirror → resistor → ADC | Same | 0.25 mΩ 4-terminal shunt → driver's sense amplifier → ADC |
| Hardware trip | Internal current limit + thermal shutdown (~45 A† limit) | Same (~75 A† limit) | Driver short-circuit comparator 150 A, ~10 µs; overcurrent comparator 70 A with 0.5 s timer |
| PWM | 100–250 Hz (dimming, soft-start) | 100–250 Hz (soft-start; dimming if load tolerates it) | Soft-start only; no continuous PWM |
| Reverse battery | ReverseON (channel turns on to limit dissipation; load sees reverse voltage) | Same | Back-to-back FETs block; load sees nothing |
| Temperature | Internal sensing; firmware estimate | Same | NTC beside the FETs |

### Thermal check

Model (`python3 tools/budget.py`):
T<sub>j</sub> = ambient + P<sub>module</sub> × R<sub>th,enclosure</sub>
+ P<sub>switch</sub> × R<sub>th,j-base</sub>, with AUX coils at their JK
loads and 0.5 W of logic. Assumptions: junction-to-base S 15 K/W, M 12 K/W,
M+ 8 K/W, L 20 K/W per FET; enclosure-to-ambient 1.5 K/W (die-cast aluminium
on vehicle metal), 2.5 K/W (printed shell on a 6 mm aluminium base plate),
6 K/W (printed shell only); hot R<sub>DS(on)</sub> = 2× for PROFET, 1.8× for
discrete FETs at 1.2 mΩ each. Design ambients: cab 65 °C, engine bay 85 °C
(front of the bay, moving), engine-bay hot spot 105 °C (slow crawl on a
summer day) — the engine-bay figures are assumptions until the vehicle is
logged.

Two limits apply: hottest junction ≤ 135 °C (15 °C below 150 °C), and
enclosure base ≤ 115 °C, because the base stands in for the logic-board
temperature and Grade 1 parts are rated to 125 °C.

JK build — `MMSS` in the cab, printed shell on an aluminium plate, every
slot at its rating, 6.4 W in the module, base plate at 81 °C:

| Slot | Class | I cont (A) | Path R hot (mΩ) | Drop (mV) | Loss (W) | T<sub>j</sub> est (°C) |
|---|---|---:|---:|---:|---:|---:|
| OUT1 | M | 20 | 5.20 | 104 | 2.08 | 106 |
| OUT2 | M | 20 | 5.20 | 104 | 2.08 | 106 |
| OUT3 | S | 10 | 8.80 | 88 | 0.88 | 94 |
| OUT4 | S | 10 | 8.80 | 88 | 0.88 | 94 |

Hottest junction / enclosure base (°C) with **every slot at its rating**
(bold = over a limit):

| Build | Location | Aluminium box | Printed shell + Al plate | Printed shell only |
|---|---|---:|---:|---:|
| MMSS | cab | 100 / 75 | **106 / 81** (JK default) | 128 / 104 |
| MMSS | engine bay | 120 / 95 | 126 / 101 | **148** / **124** |
| MMSS | engine-bay hot spot | **140** / 115 | **146** / **121** | **168** / **144** |
| M+MSS | cab | 99 / 74 | 105 / 81 | 127 / 102 |
| M+MSS | engine bay | 119 / 94 | 125 / 101 | **147** / **122** |
| M+MSS | engine-bay hot spot | **139** / 114 | **145** / **121** | **167** / **142** |
| LMSS | cab | 102 / 77 | 110 / 85 | **139** / 114 |
| LMSS | engine bay | 122 / 97 | 130 / 105 | **159** / **134** |
| LMSS | engine-bay hot spot | **142** / **117** | **150** / **125** | **179** / **154** |

Hottest junction / enclosure base (°C) with the **expected JK loads**
(light bar 20 A, pods 12 A, rear floods 8 A, rock lights 4 A):

| Build | Location | Aluminium box | Printed shell + Al plate | Printed shell only |
|---|---|---:|---:|---:|
| MMSS | cab | 96 / 71 | 100 / 75 | 114 / 89 |
| MMSS | engine bay | 116 / 91 | 120 / 95 | 134 / 109 |
| MMSS | engine-bay hot spot | **136** / 111 | **140** / **115** | **154** / **129** |
| M+MSS | cab | 79 / 70 | 82 / 73 | 94 / 84 |
| M+MSS | engine bay | 99 / 90 | 102 / 93 | 114 / 104 |
| M+MSS | engine-bay hot spot | 119 / 110 | 122 / 113 | 134 / **124** |

`M+MSS` is the `MMSS` board with the light-bar slot built from the
BTS50015-1TAD (TO-263-7) instead of the BTS7002 — same slot interface, about
40 % less loss at 20 A.

Conclusions:

- The M cell carrying the light bar is the hottest part in every case.
- A printed enclosure needs the aluminium base plate in every location;
  printed-only traps the heat, and even where the junctions pass, the shell
  runs above ASA's 100 °C softening point.
- **Engine bay, printed shell on the plate, is viable** at 85 °C ambient
  for both full-rating and expected loads. At a 105 °C hot spot it needs the
  low-loss M+ part on the light-bar slot, and full-rating operation of every
  slot is not sustainable there in any enclosure — firmware derating
  (based on estimated junction temperature,
  [07](07-firmware.md#system-level-limits)) covers that corner. Requirements
  for that build are in [08](08-mechanical-and-wiring.md#engine-bay-build).
- The JK default — cab, printed shell, aluminium plate — leaves ~30 °C of
  margin. For the two-module layout (front module inside a closed
  glovebox, rear module in the cargo area) see
  [13](13-multi-module-system.md#thermal).

Thermal resistances are the weakest assumption in these tables. They are
replaced with measured values in validation test TH-1.

## S and M cells (PROFET+2)

```
VBAT ──┬───────────────┐
       │           ┌───┴────┐
      Cbulk        │  VS    │
      (local)      │        │ OUT ──┬──[OUT_SENSE divider]── to logic
                   │PROFET+2│       │
CHn_EN  ──[R]──────┤ IN     │       ├── output pin
CHn_DIAG ──[R]─────┤ DEN    │       │
                   │     IS ├──┬────┴─(optional freewheel at load for big solenoids)
                   │  GND   │  │
                   └───┬────┘  R_IS ──┬── RC ── CHn_ISENSE
                       │       │      └── comparator ── CHn_FAULT_N
                     R_GND     GND
                       │
                      GND
```

- `IN` and `DEN` have pull-downs on the power board so the cell is off with
  no logic board.
- `R_IS` is chosen so 1.5 × rating ≈ 2.5 V at the ADC with the datasheet
  k<sub>ILIS</sub> ratio. In a fault the PROFET drives `IS` to its fault
  current, which saturates near the clamp; a comparator at ~2.9 V raises
  `CHn_FAULT_N` so faults reach an interrupt pin, not only the ADC.
- k<sub>ILIS</sub> spreads ±several % part to part and is non-linear at low
  current, so each cell is two-point calibrated at end-of-line (≈ 10 % and
  ≈ 80 % of rating) and the gain/offset stored in the power-board EEPROM.
- `R_GND` (per datasheet) limits ground current in a reverse-battery or
  ground-loss event.
- Inductive loads: the PROFET's integrated output clamp absorbs relay-coil
  energy. Solenoids above ~1 A (air lockers, contactor coils) get a
  freewheel diode at the load.
- Capacitive LED drivers: switch-on charges the driver's bulk capacitance
  through the PROFET's current limit. Firmware soft-start (PWM ramp over
  50–500 ms) keeps the peak below the limit and avoids nuisance trips.

### PWM on light loads — practical note

PWM dimming of a light's *supply* only works if the light's internal driver
follows it. Many light bars have a constant-current driver with bulk
capacitance and either flicker or ignore PWM. Configure those outputs for
soft-start only; use dimming on simple LED strips, rock lights and pods that
are known to dim.

## L cell (discrete MOSFETs + smart driver)

```
VBAT ──┬──────────────[Rshunt 0.25 mΩ, Kelvin]──────┐
       │                                             │
      TVS                       ┌── Q1a ─┐           │
   (module input)       drain ──┤        ├── source ─┼─ common source ─┬─ source ──┤ Q2a ├── drain ── OUT stud
                                └── Q1b ─┘           │                 └─ source ──┤ Q2b ├──┘
                                   gate ─────────────┴── TPS48111-Q1 GATE ──────── gate
                                                         CS+/CS- (Kelvin from shunt)
                                                         IMON → CHn_ISENSE
                                                         FLT_N → CHn_FAULT_N
                                                         EN/INP ← CHn_EN
                                                         NTC → CHn_TEMP
OUT ──┬── Schottky freewheel (cathode at OUT, anode at GND), 60 V, ≥ 40 A pulse
      └── OUT_SENSE divider
```

- Q1a/Q1b (drains to VBAT) block forward current when off — the switching
  function. Q2a/Q2b (drains to OUT) block reverse current — reverse battery,
  or the output back-fed from another source. Together they form a
  bidirectional switch; common source lets one gate drive control all four.
- **MOSFET spec:** 60 V, AEC-Q101, R<sub>DS(on)</sub> ≤ 1.3 mΩ at 10 V
  V<sub>GS</sub>, TOLL / sTOLL / LFPAK88 or equivalent bottom-cooled package.
  60 V rather than 40 V buys margin above the 35 V suppressed load dump plus
  inductive kick at turn-off. Linear-mode SOA is not required because the
  FETs are never held in linear mode.
- **Shunt:** 0.25 mΩ, 4-terminal metal element, ≥ 3 W, Kelvin-routed. 40 A
  gives 10 mV and 0.4 W; 150 A gives 37.5 mV, inside the driver's
  sense-amplifier range (verify for the selected suffix).
- **Inrush (compressor):** the driver's overcurrent comparator has a timer
  so motor inrush (up to the 150 A short-circuit level, ~100–300 ms) passes;
  a sustained > 70 A for 0.5 s trips in hardware; the firmware I²t fuse is
  the primary protection at configured ratings below that.
- **Freewheel:** a motor or long-harness inductance at turn-off is clamped
  by the Schottky to ~−0.6 V instead of avalanching the FETs.
- **Twin-motor compressors** exceed the L rating. The ARB twin (CKMTA12) is
  rated ~50 A under load and ships with its own relay, so it keeps that relay
  and the module drives the coil from AUX1
  ([12](12-compressor-and-winch.md#arb-twin-compressor-ckmta12)).

## AUX bank (coil drivers)

Four on/off outputs for relay and contactor coils, indicators and small
accessories, fitted on every power-board variant.

| | AUX |
|---|---|
| Device | 2 × Infineon **BTS7008-2EPA** (PROFET+2 12 V dual, per-channel R<sub>DS(on)</sub> ~8 mΩ†) — same family and firmware driver as the S/M cells. Alternate: TI TPS2HB16-Q1. |
| Rating | 5 A continuous per channel (firmware default 2 A for coils) |
| Current sense | One `IS` pin per device, channel selected by `AUX_DSEL`; read in turn every 1 ms |
| Hardware trip | Internal current limit and thermal shutdown |
| PWM | No — on/off only. Economised contactor coils must see steady DC. |
| Inductive loads | The integrated output clamp absorbs relay-coil energy; economised coils suppress their own back-EMF; large plain solenoids get a freewheel diode at the coil |
| Connector | J7 ([08](08-mechanical-and-wiring.md#j7--aux-outputs)) |

JK allocation: AUX1 ARB compressor relay, AUX2 winch isolator contactor,
AUX3 rocker indicator, AUX4 spare ([12](12-compressor-and-winch.md)).

Because AUX1 feeds the ARB relay coil through ARB's pressure switch, its
current sense doubles as a "compressor running" signal — see
[run detection](12-compressor-and-winch.md#run-detection-without-a-pressure-sensor).

## Protection layers

| Layer | Mechanism | Response | Independent of firmware? |
|---|---|---|---|
| 1 | Short-circuit trip (PROFET internal limit / L driver comparator) | µs | Yes |
| 2 | Overtemperature (PROFET internal / L driver timer + NTC) | ms | Yes (S/M), partly (L) |
| 3 | Electronic fuse: instantaneous + I²t, per-output configurable | 1 ms loop | No |
| 4 | Inrush blanking and soft-start | per configuration | No |
| 5 | Retry with back-off, then latch | s | No |
| 6 | Load shed: low battery, module current budget, board temperature | s | No |
| 7 | Upstream fuse on the battery feed (80 A at the battery for the JK `MMSS` build) | — | Yes — protects the feed cable only |

**Wire-sizing rule:** size each output wire for the *hardware* trip level
(layers 1–2), not the firmware fuse setting, because hardware is the layer
that still works with the MCU hung. In practice: S → 14 AWG, M → 10–12 AWG,
L → 8 AWG for runs up to ~3 m. [Harness drop table](08-mechanical-and-wiring.md#harness).

## "Current limiting" — what it means here

True linear current limiting (holding a load at, say, 20 A by running the
switch partly on) dissipates `(VBAT − Vload) × I` in the switch — over 100 W
in a 40 A channel — and is not sustainable in a sealed box. This design
therefore **limits by tripping and by duty cycle**, not by linear regulation:

- fast hardware trip for shorts,
- configurable I²t trip for overloads,
- soft-start to cap inrush,
- PWM duty foldback for loads that tolerate it (lights) when the channel,
  board or battery is near a limit.

The only linear limiting is the PROFET's built-in short-circuit limit, which
lasts until its thermal shutdown — milliseconds — and is a protection
behaviour, not a control mode.

## Diagnostics per output

| Condition | Detection | Reported as |
|---|---|---|
| Overcurrent / I²t trip | Firmware, from ISENSE | `FAULT_OVERCURRENT` |
| Short circuit | `CHn_FAULT_N` or ISENSE saturated | `FAULT_SHORT` |
| Overtemperature | PROFET fault with normal current; L NTC | `FAULT_OVERTEMP` |
| Open load (on) | Current below configured minimum while on | `WARN_OPEN_LOAD` |
| Open load (off) | `OUT_SENSE` with off-state pull-up (DEN on PROFET cells) | `WARN_OPEN_LOAD` |
| Output powered externally | `OUT_SENSE` high while commanded off | `WARN_EXT_VOLTAGE` |
| Latched after retries | Retry counter exhausted | `FAULT_LATCHED` |

Fault codes are listed in [06-can-protocol.md](06-can-protocol.md#fault-codes).
