# 07 — Firmware

Target: STM32G474, C with STM32 LL drivers (or Rust/Embassy — decision
D-6 in [10-decisions-and-open-questions.md](10-decisions-and-open-questions.md)).
No RTOS is needed; three fixed-rate loops cover the work.

## Execution model

| Loop | Rate | Context | Work |
|---|---|---|---|
| ADC | continuous | DMA | Scan ISENSE ×4, AUX IS ×2, inputs ×8, IGN, VBAT, multiplexed slow channels; oversample ×8 |
| Protection | 1 kHz | Timer ISR, highest priority | E-fuse, I²t, soft-start ramps, retry timers, `force_off` interlocks, apply final output state |
| Logic | 100 Hz | Main loop | Input decode, vehicle signals, rule engine, arbitration, feedback supervision, load shed, derating |
| Telemetry | 10 Hz | Main loop | `Status`, `Currents`, `Inputs`, `Inputs2`, `Aux`, `VehicleA/B`; `Diag`/`Info`/`Health` at 1 Hz |
| CAN RX | event | FDCAN ISR → queue | FDCAN1: `Command`, `ConfigReq`. FDCAN2/3: vehicle-signal extraction |
| OBD client | 10 Hz max | Main loop | Only when enabled and the `TXD` jumper is fitted ([below](#obd-ii-polling)) |

The protection loop never waits on the logic loop: it reads the latest
arbitrated request and applies it, so a slow or stuck rule never delays a
trip. The independent watchdog is fed only when both loops have checked in.

## Start-up and reset behaviour (FN-14)

1. Hardware pull-downs hold every `CHn_EN` and `AUXn_IN` low through reset,
   bootloader and any period the pins are high-impedance.
2. Firmware loads configuration (A/B pages, CRC-checked), reads slot ID
   resistors and the power-board EEPROM, and compares fitted classes with
   the configuration. Mismatch → that output stays off with
   `SLOT_MISMATCH`.
3. 500 ms start-up inhibit: no output turns on until VBAT has been stable
   above 9 V for 500 ms. This also stops outputs flickering on during cranking.
4. Outputs then follow arbitration. State is not restored across a reset:
   rules re-evaluate from current inputs, and a CAN host has to re-command.
   (A winch isolator therefore opens if the module resets; the hardwired
   override is the path that does not depend on the module.)

## Output protection state machine (per channel)

```mermaid
stateDiagram-v2
    [*] --> OFF
    OFF --> SOFT_START: request ON
    SOFT_START --> ON: ramp done
    SOFT_START --> TRIPPED: trip
    ON --> OFF: request OFF
    SOFT_START --> OFF: request OFF
    ON --> TRIPPED: hardware fault / instantaneous / I2t
    TRIPPED --> RETRY_WAIT: retries left
    TRIPPED --> LATCHED: retries exhausted
    RETRY_WAIT --> SOFT_START: back-off elapsed and still requested
    RETRY_WAIT --> OFF: request OFF
    LATCHED --> OFF: fault reset / input re-toggle / IGN cycle
```

AUX outputs use the same machine with a zero-length soft start.

### Electronic fuse

Two checks run every 1 ms on the calibrated current `I`, against the
configured rating `In`:

1. **Instantaneous:** `I > k_inst × In` (default 4×) → trip. For the first
   `inrush_ms` after turn-on (default 0 ms for S/M, 300 ms for L, 150 ms for
   AUX so a contactor's pull-in current passes) the instantaneous limit is
   raised to the hardware trip level.
2. **I²t thermal model:** a first-order model of conductor heating,
   `θ += (dt/τ) × ((I/In)² − θ)`, trips when `θ > 1.21` (i.e. it never trips
   at ≤ 110 % of rating). Time to trip from cold at `k × In` is
   `−τ ln(1 − 1.21/k²)`:

   | Overload | τ = 10 s (default) |
   |---|---|
   | 1.5 × | 7.7 s |
   | 2 × | 3.6 s |
   | 3 × | 1.4 s |
   | 5 × | 0.5 s |

   θ keeps cooling while the channel is off, so rapid retries cannot ratchet
   a harness hotter than one long overload would.

Retry policy (per output): default 3 retries with back-off 1 s, 5 s, 30 s,
then `LATCHED`. The retry counter clears after 60 s without a trip. Coil
outputs default to 1 retry: a shorted coil wire is not a transient.

### System-level limits

| Function | Default | Action |
|---|---|---|
| Module current budget | 60 A for `MMSS`, 80 A for `LMSS` (EL-8) | Fold back PWM-capable outputs, then shed by priority |
| Thermal derating | Estimated junction > 125 °C, per channel (board NTC + that channel's loss × its R<sub>th</sub>, calibrated in TH-1) | PWM-capable outputs fold back duty, others shed by priority, until the estimate is back under 120 °C; board > 115 °C → everything except `critical` outputs off. Working on estimated junction temperature rather than fixed board thresholds lets the same firmware run the cab and engine-bay builds. |
| Low-voltage shed, IGN off | VBAT < 12.0 V for 60 s | Shed outputs with `shed_ign_off: true`; restore at IGN on |
| Low-voltage shed, IGN on | VBAT < 11.5 V for 10 s | Shed by priority (charging system not keeping up) |
| Cranking / winching | VBAT 6–9 V | Hold outputs; no shed; protection thresholds unchanged |

## Rule engine

Autonomous behaviour is **configuration, not code**: a small, fixed set of
function blocks that can be verified once and reused, instead of a scripting
language that would need its own test effort.

Each output (main or AUX) has one rule:

```
condition  = expr                       drives the behaviour
force_off  = expr                       optional interlock: while true the output is off
expr       = term [AND|OR term]...      (up to 4 terms, evaluated left to right)
term       = source op [value] [for <ms>]
op         = is_on | is_off | > | < | rising | falling
value      = number | hysteresis(low, high)   ("< hysteresis(110, 150)": true
             below 110, false above 150, unchanged in between)
for <ms>   = the comparison must have held for <ms> (long press, persistence)
source     = IN1..IN8, IGN, VIN1..VIN8, VS1..VS8 (vehicle signals), VBAT,
             OUT1..OUT4 / AUX1..AUX4 (state), OUT1_I..AUX4_I (current, A),
             OUT1_FAULT..AUX4_FAULT (a fault is present),
             ENGINE_RUNNING, VBAT_SAG (derived)
behaviour  = follow | toggle | pulse
modifiers  = on_delay, off_delay, min_off (cooldown),
             max_on (auto-off) + max_on_defer (expr) + max_on_warning_s,
             max_load_on_s + load_on_threshold_a (continuous-run limit),
             flash: [{when: expr, pattern: slow|fast}]  (first match wins),
             duty, soft_start_ms
```

- `follow`: output on while the condition is true (after delays).
- `toggle`: each rising edge of the condition flips the output — momentary
  buttons and panel keys. With `for`, a toggle becomes a long-press action.
- `pulse`: a rising edge turns the output on for `max_on`.
- `max_on_defer` holds the `max_on` timer at its limit while the expression
  is true (the winch isolator does not time out while the winch is pulling);
  `max_on_warning_s` raises a warning flag for the panel before it expires.
- A vehicle signal that is stale or unverified makes every comparison on it
  false — so put vehicle signals in `force_off` (a missing signal then
  removes the interlock) or in optional extras, never as a requirement for
  turning something on.
- `force_off` is evaluated in the protection layer, above CAN commands and
  local overrides: it is how interlocks such as "compressor only with the
  engine running" or "winch isolator opens when driving" cannot be bypassed
  from the panel. It cannot touch hardware outside the module (the winch
  override switch).
- `max_load_on_s` trips `RUN_LIMIT` when the output's *current* has stayed
  above `load_on_threshold_a` continuously for that long — the compressor's
  continuous-run limit ([12](12-compressor-and-winch.md#run-detection-without-a-pressure-sensor)).
- `ENGINE_RUNNING` is derived: an RPM vehicle signal > 500, or VBAT > 13.2 V
  for 5 s when no RPM signal is configured or it is stale.
- `VBAT_SAG` is derived: VBAT more than 1 V below its 10 s average — a large
  load such as a winch is pulling.
- **Local override** inputs: an input can be marked `override` for an output,
  which places it above CAN commands in arbitration
  ([02](02-architecture.md#data-flow-inside-the-mcu)). This is how a physical
  dash switch keeps working when a CAN panel is present.

Worked example: [`config/jk-example.yaml`](../config/jk-example.yaml).

## Feedback supervision

Any output may name inputs that must follow its real-world state (FN-16):

| Field | Meaning |
|---|---|
| `sense` | Input that is high when the load side is live (e.g. winch-side contactor stud) |
| `command_sense` | Optional input on the coil side; high when *anything* — this output or a hardwired override — energises the coil |
| `close_timeout_ms` | `sense` must go high within this time after the coil is energised |
| `open_timeout_ms` | `sense` must go low within this time after the coil is released |

Expected state = this output on, **or** `command_sense` high. A mismatch past
the timeout raises `FEEDBACK_MISMATCH` on that output. The winch isolator
uses this to detect a contactor that failed to close, welded contacts, and
an override switch left on ([12](12-compressor-and-winch.md#state-and-feedback)).

## Vehicle signal map

Up to 8 vehicle signals `VS1..VS8`, each defined in configuration:

| Field | Example |
|---|---|
| `name` | `high_beam` |
| `bus` | `CAN3` (CAN-IHS) or `CAN2` (OBD port) |
| `type` | `broadcast` (decode a frame on the bus) or `obd_pid` (poll, CAN2 only) |
| `can_id`, `start_bit`, `length`, `byte_order`, `signed` | DBC-style, for `broadcast` |
| `pid` | e.g. `0x0D`, for `obd_pid`; the standard SAE J1979 formula is applied |
| `factor`, `offset`, `scale` | Engineering units, and the unit reported in `VehicleA/B` |
| `timeout_ms` | Value becomes *stale* after this; rules treat stale as false and `Status.VehicleSignalStale` is set |

FDCAN2/FDCAN3 hardware filters are programmed from the map, so the MCU only
sees the frames it needs.

### OBD-II polling

Runs only when all of these hold: the CAN2 `TXD` jumper is fitted, polling
is enabled in configuration, at least one `obd_pid` signal is configured,
and IGN is on.

- Transmits only ID `0x7DF`, mode `0x01`, configured PIDs; ≤ 10 requests/s
  in total.
- Automatic retransmission is disabled; any transmit error or bus-off stops
  polling until the next ignition cycle.
- Pauses for 30 s whenever another tester's requests appear on the bus
  (`Health.OtherTesterSeen`).
- Never runs on FDCAN3; there is no transmit path to CAN-IHS in hardware.

## Configuration storage

- Two flash pages (A/B), each holding the full configuration, a sequence
  number and a CRC-32.
- `COMMIT` writes the inactive page, verifies it, then bumps its sequence —
  power loss during a commit leaves the previous configuration valid.
- Boot loads the valid page with the highest sequence. Neither valid →
  factory defaults: all outputs OFF, no rules, inputs inert, vehicle buses
  listen-only, CAN1 on at 500 kbit/s so the module can be configured.
- `Info.ConfigCrc16` lets a host detect which configuration a module runs.

## Firmware update

- **USB (rev A):** USB-C service port → ROM DFU bootloader, entered by a
  `ConfigReq` command or by a button on the logic board. Outputs are off
  throughout (pins high-impedance + pull-downs).
- **CAN (later):** custom bootloader on `BootReq`/`BootResp`, A/B image slots,
  image CRC + version check before switching. Lets every module on a bus be
  updated through one connector.

## Source layout (planned)

See [`../firmware/README.md`](../firmware/README.md).
