# 04 — Inputs

Four general inputs (`IN1`–`IN4`) plus a dedicated ignition/wake input
(`IGN`). Every input is read by the ADC, so "active-high", "active-low" and
"analog" are firmware modes over identical hardware — any input can be
re-purposed by configuration, with no rework.

## Input circuit (per channel, identical ×4)

```
                     VBAT_PROT
                         │
                    [P-FET, MCU controlled]   ← wetting pull-up enable
                         │
                       2.2 kΩ                 (~6 mA at 13.5 V)
                         │
 pin ──[ 1 kΩ, 0.25 W ]──┼──────┬────────────[ 47 kΩ ]──┬──── ADC_INn
         series          │      │                       │
                     TVS 24 V  100 kΩ                 10 kΩ ── 10 nF
                     (bidir)  pull-down                 │
                         │      │                      GND
                        GND   [N-FET]  ← pull-down enable
                                │
                               GND
```

- Divider 47 k / 10 k gives 0–3.0 V for 0–17.1 V at the pin; values above
  that are clamped by the MCU pin's protection through the 47 k (≤ 0.5 mA at
  40 V, inside the injection limit — verify against the MCU datasheet).
- 1 kΩ series + bidirectional TVS survive ISO 7637-2 pulses on harness wiring
  and a ±16 V miswire indefinitely.
- **Wetting pull-up:** toggle switches in an off-road vehicle get wet and
  oxidise. A ground-switched input runs ~6 mA through the switch contacts,
  which keeps them clean. The pull-up is MCU-switched so it can be disabled
  for 12 V-driven inputs.
- **Sleep scanning:** a weak always-on pull-up cannot replace it in sleep,
  because the 57 kΩ divider and 100 kΩ pull-down load it below the
  active-low threshold. Instead, in sleep the MCU wakes every 100 ms, turns
  the 2.2 kΩ pull-up on for 1 ms and samples. Cost ≈ 4 µA per open switch
  plus ≈ 20 µA of MCU wake-ups ([budget](../tools/budget.py)); a switch left
  *closed* with the module asleep costs ≈ 60 µA. Worst-case wake latency is
  100 ms + debounce.
- **Pull-down:** switchable so a 12 V-driven input (trailer harness, factory
  switch) has a defined level when its source is open.
- RC (~0.4 ms) removes RF; real debounce is in firmware.
- Active-high inputs are caught by the same 100 ms sleep scan (a 12 V input
  only reaches ~1.9–2.4 V at the divider, too marginal for a digital EXTI
  threshold); `IGN` has its own digital wake path. See
  [05-logic-power-can.md](05-logic-power-can.md#sleep-and-wake).

## Input modes

| Mode | Hardware setting | Active when | Typical source |
|---|---|---|---|
| `ACTIVE_LOW` | Pull-up on, pull-down off | V < 2.0 V | Dash toggle to ground, pressure switch, door switch |
| `ACTIVE_HIGH` | Pull-up off, pull-down on | V > 7.0 V (hysteresis to 5.0 V) | Trailer harness circuits, factory 12 V switches, ignition-switched feeds |
| `ANALOG` | Both off (or pull-up on for resistive senders) | — reports voltage | 0.5–4.5 V pressure transducer (with module `+5V_SENS`), resistor-ladder multi-position switch |
| `FREQUENCY` | As `ACTIVE_*` | — reports Hz and duty | Turn-signal decode, wheel-speed pulses (≤ 1 kHz) |

Thresholds, debounce (default 20 ms on, 50 ms off) and inversion are
per-input configuration parameters.

### `+5V_SENS` sensor supply

A 5 V, 50 mA protected supply (short-to-ground and short-to-battery
tolerant, e.g. a protected LDO or a high-side switch from the 5 V rail) on
the signal connector powers a ratiometric pressure transducer. That lets the
module run the compressor on measured tank pressure with its own cut-in and
cut-out thresholds instead of a mechanical pressure switch.

## Trailer harness as an input source

The JK's factory/Mopar trailer harness and aftermarket 7-way plugs carry
lighting circuits that are useful triggers.

| Circuit | Usual connector | Useful for | Decode |
|---|---|---|---|
| Reverse / back-up | 7-way RV blade (centre pin on most US harnesses — varies; probe it) | Rear floods on when reversing | Steady high |
| Tail / running lights | 4-flat and 7-way | "Lights on" interlock, rock-light enable | Steady high |
| Left / right turn + stop (combined) | 4-flat and 7-way | Brake input, turn-signal side lights | Steady = brake; 1–2 Hz square wave = turn signal |
| 12 V aux (battery) | 7-way | Not an input — do not use as a trigger | — |
| Electric brake controller output | 7-way | Brake-controller activity (rarely useful) | PWM/analog |

Notes from typical vehicles (verify on the target vehicle):

- **Combined stop/turn circuits** need the `FREQUENCY` mode: firmware treats
  a steady signal for > 700 ms as brake, a 1–2 Hz toggle as turn, and
  turn + brake as both.
- **Lamp-out / trailer-detect pulses:** many vehicles and trailer-tow modules
  pulse the outputs for a few ms to check for a connected trailer. A 20 ms
  debounce rejects these; increase it if the module sees ghost triggers.
- **Loading:** an input draws ≤ 0.3 mA from a 12 V circuit — far below what
  a bulb-out detector would flag — but some LED-trailer converters need a
  minimum load to switch. If the module is the only "trailer", add a
  load resistor at the plug, not in the module.

## Ignition / wake input

`IGN` uses the same front end with fixed `ACTIVE_HIGH` settings and a
stronger filter (10 ms). On a JK, take it from an ignition-switched fuse in
the TIPM with an add-a-fuse tap, fused at 2 A. `IGN` gates:

- whether the module may sleep,
- the default "ignition-only" rules (e.g. light bar allowed only with
  ignition on),
- the CAN-timeout failsafe (with ignition off, a missing host is normal).

## Example JK input allocation

| Input | Mode | Wired to | Used by |
|---|---|---|---|
| IN1 | `ACTIVE_LOW` | Dash toggle "BAR" | OUT2 light bar |
| IN2 | `ACTIVE_HIGH` | Trailer harness reverse circuit | OUT3 rear floods |
| IN3 | `ACTIVE_LOW` | Dash toggle "AIR" | OUT1 compressor enable |
| IN4 | `ANALOG` | Tank pressure transducer on `+5V_SENS` | OUT1 cut-in / cut-out |
| IGN | fixed | TIPM ignition fuse tap | Sleep, interlocks |

The matching configuration is [`config/jk-example.yaml`](../config/jk-example.yaml).
