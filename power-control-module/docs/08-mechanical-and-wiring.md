# 08 — Mechanical, connectors and wiring

## Enclosure

| Item | Choice |
|---|---|
| Body | Die-cast or extruded aluminium, gasketed lid, IP67 (EN-2). Target 130 × 110 × 45 mm. |
| Heat path | Power board on the enclosure floor through a 1 mm gap pad; the floor is the heat sink for the 7.7 W worst case. |
| Board stack | Power board (bottom) → 2 × 20 board-to-board header + 2 × M3 standoffs → logic board (top). |
| Venting | Pressure-equalising membrane vent. A sealed box that heats and cools pumps moist air past its gaskets; a membrane vent stops that and is the usual cause of "IP67" electronics failing in engine bays. |
| Coating | Acrylic or silicone conformal coat on both boards (EN-4), masked at connectors, test points, USB. |
| Mounting | 4 × M6 through-holes on external flanges, isolated from the PCB ground. |
| Service | USB-C and address strap under a gasketed screw cap, not through the harness side. |

## Connectors

All harness connectors are sealed when mated and are PCB-mount headers in
the enclosure wall. Contact ratings are the series' nominal values — check
the specific contact part and wire gauge.

| Ref | Function | Connector | Contacts |
|---|---|---|---|
| J1 | Battery + | M6 brass stud, insulating boot | 4 AWG ring |
| J2 | Module ground | **M5** stud (deliberately different size from J1 to prevent swapping the ring terminals) | 12 AWG ring |
| J3 | OUT1 (L slot) | Deutsch DTHD 1-way, size 8 contact (~60 A) | 8 AWG |
| J4 | OUT2–OUT4 (M/S slots) + spare | Deutsch DTP 4-way, size 12 contacts (~25 A) | 10–14 AWG |
| J5 | Signals + accessory CAN | Deutsch DT 12-way, size 16 contacts | 18–20 AWG; CAN as twisted pair |
| J6 | Vehicle CAN (listen-only) | Deutsch DT 4-way | 20 AWG twisted pair |

On other variants, every L slot gets its own DTHD connector and every S/M
slot takes a DTP position, so the enclosure is punched per variant but the
connector families do not change.

### J4 — outputs

| Pin | Signal |
|---|---|
| 1 | OUT2 |
| 2 | OUT3 |
| 3 | OUT4 |
| 4 | Spare / not connected |

### J5 — signals

| Pin | Signal | Notes |
|---|---|---|
| 1 | IN1 | |
| 2 | IN2 | |
| 3 | IN3 | |
| 4 | IN4 | |
| 5 | IGN | Ignition-switched, 2 A fuse at the tap |
| 6 | +5V_SENS | 50 mA protected sensor supply |
| 7 | SIG_GND | Sensor / switch reference |
| 8 | SIG_GND | |
| 9 | CAN1_H | Bus in |
| 10 | CAN1_L | |
| 11 | CAN1_H | Bus out (daisy chain) — internally connected to 9 |
| 12 | CAN1_L | Bus out — internally connected to 10 |

### J6 — vehicle CAN

| Pin | Signal |
|---|---|
| 1 | CAN2_H (OBD-II pin 6) |
| 2 | CAN2_L (OBD-II pin 14) |
| 3 | GND (OBD-II pin 5, signal ground) |
| 4 | Not connected |

CAN keypads/displays need their own 12 V feed: take it from an
ignition-switched source or from an S output with the rule `IGN is_on`.

## Harness

From `python3 tools/budget.py` (20 °C copper; hot copper is ~15–20 % worse).
"One-way" is the module-to-load distance; the drop includes a wired return
to a chassis ground point near the module.

| Run | Current (A) | AWG | One-way (m) | Drop (V) | Drop at 13.5 V (%) |
|---|---:|---:|---:|---:|---:|
| Battery feed to module | 80 | 4 | 1.0 | 0.07 | 0.5 |
| Compressor (OUT1, L) | 40 | 8 | 1.5 | 0.25 | 1.8 |
| 50 in light bar (OUT2, M) | 20 | 10 | 3.0 | 0.39 | 2.9 |
| Rear floods (OUT3, S) | 10 | 14 | 4.5 | 0.75 | 5.5 |
| Rock lights (OUT4, S) | 6 | 16 | 3.0 | 0.47 | 3.5 |

Rules:

- **Fuse the battery feed at the battery** (100 A MIDI/MEGA fuse or a
  type-1 auto-reset breaker, within ~300 mm of the post). The module
  protects its outputs; only that fuse protects the 4 AWG feed.
- Size output wire for the channel's **hardware** trip, not its firmware
  setting ([03](03-output-channels.md#protection-layers)).
- Return each load to a clean chassis point near the load; do not bring load
  returns back to J2.
- Keep the rear-flood run at 12 AWG if it exceeds ~5 m: the 14 AWG drop
  above is already 5.5 %.
- Use cross-linked (GXL/TXL) wire in the engine bay, convoluted loom over
  everything, and a drip loop below each connector.

## Mounting on a JK

Two sensible locations; choose before the harness is drawn.

| Location | For | Against |
|---|---|---|
| **Engine bay, inner fender/firewall near the battery** (default) | 4 AWG feed under 1 m; lighting runs to the bar and front pods are short; most JK accessory wiring already lives here | Hot (design is rated to 85 °C ambient; keep it away from the exhaust manifold) and wet — the IP67/vent design is for this case |
| In cab, under dash or behind the centre console | Cool and dry; easy access to dash toggles | Battery feed needs a firewall grommet and is longer; every output crosses the firewall |

Mount with connectors facing down or sideways, never up, and above the
expected fording depth.
