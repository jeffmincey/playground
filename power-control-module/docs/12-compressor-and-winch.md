# 12 — Compressor (ARB twin) and winch isolator

Both loads draw far more than any module output should carry, so neither is
powered *through* the module. The module switches their control circuits
from the AUX coil-driver bank ([03](03-output-channels.md#aux-bank-coil-drivers))
and adds interlocks, run monitoring and auto-off that a plain dash switch
cannot provide.

| AUX | JK use | Load on the AUX output |
|---|---|---|
| AUX1 | ARB twin compressor relay (through ARB's pressure switch) | Relay coil, ~0.2 A (measure) |
| AUX2 | Winch isolator contactor coil | 3.8 A pull-in for 130 ms, 0.13 A hold (economised coil) |
| AUX3 | Indicator in the ARB rocker (compressor running / blocked) | LED, < 50 mA |
| AUX4 | Spare (horn relay, fridge relay, second indicator) | ≤ 5 A |

## ARB twin compressor (CKMTA12)

### What the ARB kit includes

From ARB's product page, spec sheet and installation manual (as found via
search; confirm against the documents shipped with the unit):

| Item | Value |
|---|---|
| Relay | **Yes — one sealed 12 V 40 A relay** in the supplied wiring loom (parts list) |
| Fuses | Two 40 A maxi fuses, one per motor |
| Pressure switch | Included; opens at ~150 psi, closes at ~135 psi (CKMTA12 manual FAQ) |
| Current draw | 28 A no-load; ~50 A under load (12 V model) |
| Air Locker | Loom has plug-in terminals for Air Locker solenoids; the solenoid manifold is sold separately |
| Switch | ARB dash rocker with loom connector |

So the ARB loom already contains everything the high-current side needs, and
the module does not replace any of it.

### Why not run it from an output

- Up to ~50 A under load exceeds the L cell's 40 A rating, and two motors
  starting together add a large inrush.
- ARB's loom is fused per motor and tested as a unit; keeping it intact keeps
  ARB's support and fault behaviour.
- Switching the relay coil gets every control benefit (interlocks, timers,
  CAN, run monitoring) for ~0.2 A.

This frees the main outputs for lighting, and the default build changes from
`LMSS` to **`MMSS`** (decision D-3 in [10](10-decisions-and-open-questions.md)).

### Wiring

```
High-current side, engine bay — ARB loom exactly as supplied:
  battery + ── ARB loom (40 A relay, 2 × 40 A maxi fuses, one per motor) ── motors A and B

Relay coil circuit (the only change):
  ARB rocker output ──X  (disconnected from the coil feed)

  PCM AUX1 ── 18 AWG through firewall ── ARB pressure switch ── relay coil ── ground
                                         (opens at ~150 psi)

ARB rocker (in cab):  one contact → ground, other contact → PCM IN1 (ACTIVE_LOW)
ARB rocker indicator: PCM AUX3 (optional)
```

The pressure switch stays in series with the coil, so the tank pressure
cut-out works in hardware even if the module misbehaves. Check the exact
switch and loom connections against Figure 9 of the CKMTA12 installation
manual before cutting anything — forum notes on the pin-out vary by loom
revision.

### Run detection without a pressure sensor

With the pressure switch in series, AUX1 current *is* the compressor state:

| AUX1 commanded | AUX1 current | Meaning |
|---|---|---|
| ON | ≈ coil current (~0.2 A) | Pressure switch closed → compressor running |
| ON | ≈ 0 | Tank at cut-out pressure → compressor stopped |
| ON | < 20 mA for > 30 s with tank never filling | Open coil or broken wire → `OPEN_LOAD` |
| OFF | 0 | Off |

That gives a **continuous-run limit**: if the compressor runs without the
pressure switch ever opening for longer than `max_load_on_s` (default
20 min), something is wrong — hose off, fitting leak, stuck pressure switch —
and the module stops it with `RUN_LIMIT` until the rocker is cycled. Tyre
inflation through a hose also runs the compressor for long periods; set the
limit to suit how many tyres are aired up at once. Check ARB's duty-cycle
rating for the unit and keep the limit inside it.

### Rules

| Rule | Default |
|---|---|
| Enable | IN1 (rocker) on **and** engine running (RPM from the vehicle bus, or VBAT > 13.2 V for 5 s) |
| Indicator (AUX3) | Steady while running (AUX1 current present), slow blink while enabled but blocked (engine off), fast blink on `RUN_LIMIT` |
| Continuous-run limit | 20 min → `RUN_LIMIT`, cleared by cycling the rocker |
| Interlocks (`force_off`) | Rocker off, engine not running, or VBAT < 12.0 V for 10 s until it recovers above 12.8 V (the charging system is not keeping up). A CAN request cannot override them, so the panel can only run the compressor while the rocker is on. |
| Host loss | Not relevant: the rocker is local |

### Stock relay rating

One 40 A relay feeding a compressor that ARB rates at ~50 A under load runs
the relay near or past its rating, and owners report blown fuses. If the
relay or fuses give trouble, replace the relay with a higher-rated sealed
relay or a continuous-duty contactor; AUX1 drives up to 5 A of coil, so the
module side does not change.

Air Lockers (if fitted to a non-Rubicon JK): leave them on ARB's own
switches and solenoids. Traction controls should not depend on a custom
module.

## Winch isolator

### Purpose

The winch cable runs from the battery to the bumper and is live all the time
in most installs. An isolator at the battery end:

- de-energises the long cable and the winch control pack when not winching
  (chafe, crash damage and water ingress become non-events),
- stops a dropped or faulty remote from moving the drum,
- gives an "arm before use" step, plus automatic disarm.

### Requirements

| ID | Requirement |
|---|---|
| WI-1 | Continuous-duty contactor (held closed for hours), rated ≥ the winch's maximum draw (typically 350–500 A for 8–12 k lb winches; check the winch spec). |
| WI-2 | Sealed (fording) and rated for the engine bay: −40…+85 °C. |
| WI-3 | Opens when control power is lost (fail-safe). |
| WI-4 | **Winch must remain usable with the module failed** — a hardwired override path that does not pass through the module (FN-15). |
| WI-5 | Low hold current, no flyback energy into the AUX output. |
| WI-6 | The module confirms the real contact state (feedback) and detects welded contacts. |

### Options

| Option | Key ratings (from datasheets/listings via search — verify) | For | Against |
|---|---|---|---|
| **Sealed EV contactor with coil economiser, e.g. TE Kilovac EV200 / LEV200 class** (recommended) | EV200: 500 A at 85 °C (with 400 MCM conductors), hermetically sealed, −40…+85 °C; economiser: 0.13 A hold, 3.8 A for 130 ms pull-in at 12 V, internal back-EMF suppression; hold ≥ 7.5 V, drop-out ~6 V | Built for continuous duty in harsh environments; tiny hold current; meets WI-1…WI-5 | Costly; no manual lever (WI-4 met by the override switch); drops out if a winch drags VBAT below ~6–7.5 V |
| Gigavac GX14 / GV200 class | GX14: 350 A, IP67/IP69K, −55…+85 °C, 12 V coil ~230 mA, economiser option | Sealed, wide temperature | GX14's 350 A is below a large winch's peak; check GV200 ratings for the winch |
| Blue Sea ML-RBS 7713 (auto-release) | 500 A continuous, 700 A 5 min; control 10.1–16.5 V, 13 mA on; manual knob with locked-off; **−10…+50 °C** | Manual override built in; very low control current | Marine temperature rating is below engine-bay temperatures; heavy winching sags VBAT toward its 10.1 V control minimum |
| Manual battery switch | — | No electronics | No module control or auto-disarm; must be reached under the hood |
| Generic "500 A winch solenoid" kits | Intermittent duty | Cheap | **Not rated to stay closed** — overheats as an isolator. Do not use. |

### Wiring (recommended option)

```
Battery + ──[winch feed protection*]──● CONTACTOR ●── winch cable ── winch control pack
                                          coil+  coil−
                                            │      └── chassis ground
        PCM AUX2 ───────────────────►|──────┤   D1  ≥ 5 A Schottky
        fused 5 A ── WINCH OVERRIDE ─►|─────┤   D2  ≥ 5 A Schottky (guarded/locking toggle, in cab)
                                            └──[10 kΩ]──── PCM IN4  (coil sense)
 winch-side stud ──[1 A fuse]──[10 kΩ]─────────────────── PCM IN3  (winch-live sense)
```

\* The isolator is a switch, not overcurrent protection. Protect the winch
feed as the winch maker specifies.

- The diodes OR the two coil sources: the module cannot turn off the
  override, and the override cannot back-feed AUX2.
- Mount the contactor near the battery so the run to the bumper is dead when
  open. Boot both studs. Support the contactor body on a metal bracket (or a
  PET-CF / PAHT-CF printed bracket with metal inserts) and strain-relieve the
  cables separately.
- The economised coil needs steady DC; never PWM AUX2.

### State and feedback

| AUX2 | IN4 coil | IN3 winch-live | State |
|---|---|---|---|
| off | low | low | Disarmed |
| on | high | high | Armed |
| off | high | high | Override switch on |
| on or override | high | low after 500 ms | Failed to close → `FEEDBACK_MISMATCH` |
| off | low | high after 2 s | **Welded contacts** → `FEEDBACK_MISMATCH`, warning on the panel |

This uses the generic per-output `feedback` block in the configuration
([07](07-firmware.md#feedback-supervision)). The 10 kΩ series resistors and
the input divider read ~0.77 × the line voltage, so IN3/IN4 use 4 V / 2 V
thresholds: a battery dragged to 8 V by the winch still reads "live", and a
false `FEEDBACK_MISMATCH` cannot appear mid-pull.

### Rules

| Rule | Default |
|---|---|
| Arm | Panel button held 2 s, with IGN on and vehicle speed < 5 km/h (if the speed signal is available) |
| Disarm | Another 2 s press; IGN off for 60 s; speed > 10 km/h for 5 s; 30 min armed |
| Disarm deferral | Timer disarm waits while `VBAT_SAG` is true (VBAT > 1 V below its 10 s average → winch probably pulling) |
| Warning | Panel blinks for 60 s before a timer disarm |
| Host loss | `HOLD` for 30 min: a panel reboot must never open the contactor mid-pull |
| Override on with IGN off | Warning on the panel and in `Status`; the module cannot open it |

Winching with the engine off is allowed (recovering a stalled vehicle) but
drains the battery quickly; when VBAT sags below the contactor's hold
voltage it drops out regardless of the module. Keep the engine running while
winching whenever possible.
