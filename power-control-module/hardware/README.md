# Hardware

KiCad 9 projects will live here. Nothing is drawn yet; this page fixes the
structure and layout rules so the schematics start from the design in
[`../docs`](../docs).

## Planned layout

```
hardware/
├── lib/                     # project symbol + footprint library, 3D models
├── blocks/                  # channel cells as reusable hierarchical sheets
│   ├── cell-s/              #   BTS7004-1EPP cell
│   ├── cell-m/              #   BTS7002-1EPP cell
│   └── cell-l/              #   TPS48111-Q1 + 4 FETs + shunt cell
├── logic-board/             # common to all variants
└── power-board-lmss/        # default variant; other variants copy this and swap cells
```

Each cell sheet exposes exactly the
[slot interface](../docs/02-architecture.md#slot-interface) as hierarchical
pins. A cell that needs anything else is a slot-interface change and is
reviewed as one.

## Logic board schematic sheets

1. Supply: ideal diode, hold-up, buck, LDO, `+5V_SENS`, VREF
2. MCU: STM32G0B1, SWD, USB-C, address strap, status LED, board NTC
3. Inputs ×4 + IGN (one sheet instantiated 5 times)
4. CAN 1 (TX/RX) and CAN 2 (listen-only, `TXD` link DNP)
5. Slot header and connectors J5/J6

## Power board schematic sheets

1. Battery input: J1/J2, TVS, bulk capacitance, VBAT sense divider (gated)
2. Slots 1–4: one cell sheet each
3. EEPROM, ID resistors, slot header

## Stack-ups

| Board | Layers | Copper | Thickness | Notes |
|---|---|---|---|---|
| Power | 4 | 2 oz all layers (3 oz outer if the fab allows at a sane price) | 1.6 mm | VBAT spine poured on all layers and stitched; optional solder-on copper bus bar for the 80 A spine |
| Logic | 4 | 1 oz | 1.6 mm | Signal / GND / power / signal |

## Layout rules

- **Current paths.** IPC-2221 (`python3 ../tools/budget.py`) gives an upper
  bound of 16 mm of 2 oz outer copper for 40 A and 42 mm for 80 A at a 20 °C
  rise. Use pours on all four layers in parallel with via arrays (≥ 1 via
  per amp, 0.3 mm drill), and a soldered bus bar on the VBAT spine. Check the
  result in IPC-2152 or a thermal simulation before release.
- **Thermal vias** under every PROFET exposed pad and FET drain tab,
  through to a bottom-side pad that meets the enclosure gap pad. No solder
  mask on that bottom pad.
- **Kelvin sense** for the L-cell shunt: sense traces leave from the inner
  edges of the shunt pads as a tight pair, routed away from the power pour.
- **Grounds.** Power ground (TVS, freewheel diode, PROFET `GND` resistors)
  and signal ground (ADC, inputs, CAN) meet at one point beside J2.
- **CAN** pairs routed as 120 Ω differential, ESD diodes at the connector
  pins, choke footprint between ESD and transceiver.
- **Creepage.** Not a high-voltage design, but keep VBAT ≥ 0.5 mm from
  signal copper on both boards for coating and contamination margin.
- **Heavy parts.** Bulk capacitors, shunts and any through-hole part
  > 5 g get adhesive staking (EN-3).
- **Test points** for every slot-interface signal on the power board, so a
  cell can be exercised with no logic board fitted.

## Candidate key parts

Candidates, not a frozen BOM — confirm every rating against the current
datasheet before ordering.

| Function | Part | Notes |
|---|---|---|
| S switch | Infineon BTS7004-1EPP | Alt: BTS7006-1EPP, TI TPS1HB08-Q1 |
| M switch | Infineon BTS7002-1EPP | Alt: BTS50015-1TAD for a 25–30 A M+ cell |
| L driver | TI TPS48111-Q1 | Alt: Infineon 2ED2410-EM (dual) |
| L FETs | 60 V AEC-Q101, ≤ 1.3 mΩ, TOLL/sTOLL/LFPAK88 | 4 per L cell |
| L shunt | 0.25 mΩ 4-terminal, ≥ 3 W | |
| Input TVS | SM8S24A-class load-dump TVS | 24 V stand-off |
| Ideal diode | TI LM74700-Q1 | Logic supply |
| Buck | TI LMR3600x-Q1 class, 60 V | Low Iq |
| MCU | ST STM32G0B1 (64-pin) | Alt: STM32G474 |
| CAN PHY | TI TCAN1042-Q1 / NXP TJA1042 | ×2 |
| EEPROM | 24AA02 / 24C02 class, I²C | Power-board calibration |
| Connectors | Deutsch DT / DTP / DTHD PCB headers, M6 + M5 studs | See [08](../docs/08-mechanical-and-wiring.md#connectors) |
