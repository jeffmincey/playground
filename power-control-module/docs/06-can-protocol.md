# 06 — CAN protocol (accessory bus)

Protocol version 0.1. The machine-readable definition is
[`can/pcm.dbc`](../can/pcm.dbc) (validated with `cantools`, strict mode);
this page explains intent. If the two disagree, the DBC wins and this page
is a bug.

## Bus parameters

| Parameter | Value |
|---|---|
| Physical layer | ISO 11898-2, 120 Ω at both ends |
| Bitrate | 500 kbit/s default (250 k / 1 M configurable) |
| Frames | Classic CAN, 11-bit IDs, DLC 8 |
| Byte order | Little-endian (Intel) for all multi-byte signals |
| Base ID | `0x6A0` default, configurable (param `0x0101`) |
| Module ID | `base + 0x10 × address`, address 0–3 from the strap |

**ID choice:** `0x6A0–0x6DF` sits in the CANopen SDO-request range for node
IDs 0x20–0x5F. CANopen keypads typically default to low node IDs (e.g.
0x15), so there is no clash on a typical bus; if a keypad is moved into that
range, move the base ID.

## Message map (module address 0)

| ID | Name | Dir | Period | Content |
|---|---|---|---|---|
| `0x6A0` | `Command` | host → PCM | 100 ms while controlling | Output requests, duty, fault reset, virtual inputs, alive counter |
| `0x6A1` | `Status` | PCM → host | 100 ms + on change (≥ 10 ms apart) | Output state and source, inputs, IGN, VBAT, board temp, flags, module current |
| `0x6A2` | `Currents` | PCM → host | 100 ms | 4 × output current, 0.01 A/bit |
| `0x6A3` | `Diag` | PCM → host | 1 s + on change | 4 × fault code, 4 × channel temperature |
| `0x6A4` | `Inputs` | PCM → host | 100 ms | 4 × input pin voltage, 1 mV/bit |
| `0x6A5` | `Info` | PCM → host | 1 s | Slot classes, address, protocol/firmware/hardware version, config CRC |
| `0x6A6` | `ConfigReq` | host → PCM | on demand | Read/write/commit a configuration parameter |
| `0x6A7` | `ConfigResp` | PCM → host | reply | Status + value |
| `0x6AE` | `BootReq` | host → PCM | on demand | Reserved for the CAN bootloader |
| `0x6AF` | `BootResp` | PCM → host | reply | Reserved for the CAN bootloader |

### `Command` (`0x6A0`)

| Bits | Signal | Values |
|---|---|---|
| 0–7 | `OUT1_Req` … `OUT4_Req` (2 bits each) | 0 `RELEASE` (give control back to rules), 1 `OFF`, 2 `ON`, 3 reserved |
| 8–11 | `OUT1_FaultReset` … `OUT4_FaultReset` | Rising edge clears a latched fault |
| 12–15 | `Cmd_AliveCounter` | +1 per frame, wraps at 15 |
| 16–47 | `OUT1_Duty` … `OUT4_Duty` (8 bits each) | 0.5 %/bit, 200 = 100 %; 255 = configured default |
| 48–55 | `VIN1` … `VIN8` | Virtual inputs consumed by the rule engine |
| 56–63 | — | Reserved, send 0 |

Example: OUT1 ON at 50 %, OUT2 released, OUT3 OFF, OUT4 ON at 25 % with a
fault reset, counter 7, VIN3 set → `92 78 C8 00 00 64 04 00`.

`OUT_Req = ON` with a duty below 100 % on an L cell is treated as 100 % —
the L cell does not PWM (see [03](03-output-channels.md#class-summary)).

### `Status` (`0x6A1`)

| Bits | Signal | Notes |
|---|---|---|
| 0–7 | `OUTn_State` (2 bits each) | 0 OFF, 1 ON, 2 PWM, 3 FAULT |
| 8–11 | `INn_Active` | After mode, threshold, inversion and debounce |
| 12 | `IGN_Active` | |
| 13 | `SleepPending` | Module will sleep when the sleep timer expires |
| 14 | `HostPresent` | A `Command` with a changing counter arrived within the timeout |
| 15 | `ConfigDirty` | RAM config differs from flash |
| 16–23 | `VBAT` | 0.1 V/bit |
| 24–31 | `BoardTemp` | 1 °C/bit, offset −40 |
| 32–39 | `OUTn_Source` (2 bits each) | Who owns the output: 0 DEFAULT, 1 RULE, 2 CAN, 3 OVERRIDE |
| 40–44 | Flags | `LoadShedActive`, `ModuleBudgetLimit`, `ThermalDerating`, `VehicleBusActive`, `VehicleSignalStale` |
| 48–55 | `ModuleCurrent` | 0.5 A/bit |
| 56–59 | `Sts_AliveCounter` | |

`OUTn_Source` makes arbitration observable: a display can show *why* an
output is on (a rule, the host, or a local override switch).

## Timeouts and failsafe

The host is **present** while `Command` frames arrive with a changing
`Cmd_AliveCounter`. A frozen counter counts as absent, which catches a host
whose CAN driver keeps retransmitting a stale buffer.

| Parameter | Default | Meaning |
|---|---|---|
| `host_timeout_ms` | 500 | No fresh `Command` for this long → host lost |
| per-output `on_host_loss` | `HOLD` | `HOLD`: keep the last CAN request for `hold_s`, then `RELEASE`. `RELEASE`: rules take over now. `OFF`: force off. |
| per-output `hold_s` | 10 | Used by `HOLD` |

Recommended: `OFF` for the compressor, `HOLD` for lights (a keypad reboot
on the trail should not black out the light bar), `RELEASE` for outputs that
have good autonomous rules.

With `IGN` off, host loss is expected and is not logged as a fault.

## Fault codes

Used in `Diag.OUTn_Fault`.

| Code | Name | Latching | Cleared by |
|---|---|---|---|
| 0 | `NONE` | — | — |
| 1 | `OVERCURRENT` | After retries | Retry timer / fault reset |
| 2 | `SHORT` | After retries | Retry timer / fault reset |
| 3 | `OVERTEMP` | No | Cooling below hysteresis |
| 4 | `OPEN_LOAD` | No (warning) | Load current returns |
| 5 | `EXT_VOLTAGE` | No (warning) | Output voltage falls while off |
| 6 | `LATCHED` | Yes | `FaultReset` edge, local input re-toggle, or IGN cycle |
| 7 | `LOAD_SHED` | No | VBAT recovery or IGN on |
| 8 | `UNDERVOLTAGE` | No | VBAT recovery |
| 9 | `SLOT_MISMATCH` | Yes | Slot class differs from configuration; fix config or hardware |
| 10 | `RETRY_WAIT` | No | Retry timer |

## Configuration access

`ConfigReq` / `ConfigResp` carry one parameter per frame.

| Field | Bits | Notes |
|---|---|---|
| `Op` | 0–7 | 1 READ, 2 WRITE, 3 COMMIT (RAM → flash), 4 REVERT (flash → RAM), 5 FACTORY_RESET |
| `Param` | 8–23 | Parameter ID, `group << 8 \| index` |
| `Value` | 24–55 | Signed 32-bit |
| `Seq` | 56–63 | Echoed in the response |

Response `Status`: 0 OK, 1 UNKNOWN_PARAM, 2 OUT_OF_RANGE, 3 READ_ONLY,
4 BUSY, 5 LOCKED (a write that would change an output's class or protection
while that output is on).

Parameter groups:

| Group | Range | Content |
|---|---|---|
| `0x01` | `0x0100–0x01FF` | Module: base ID, bitrate, termination, sleep timer, module current budget, host timeout |
| `0x10–0x13` | per output | Rating, I²t time constant, inrush blanking, soft-start, PWM frequency/default duty, retries, back-off, `on_host_loss`, `hold_s`, load-shed threshold |
| `0x20–0x23` | per input | Mode, thresholds, debounce, inversion, pull-up/down |
| `0x30–0x3F` | rules | Rule slots (see [07](07-firmware.md#rule-engine)) |
| `0x40–0x4F` | vehicle signals | Vehicle CAN signal map entries |

Bulk configuration (a whole rules file) goes over USB; CAN access is for
tuning a value from a display or laptop in the field. The host-side tool
compiles [`config/jk-example.yaml`](../config/jk-example.yaml)-style files
into parameter writes.
