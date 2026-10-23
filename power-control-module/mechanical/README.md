# Mechanical

Enclosure, bracket and panel CAD for printing on the Bambu Lab X1C. Nothing
is modelled yet: the shell is generated from the KiCad board outlines
(exported as STEP) once the PCBs are laid out, so it fits the real boards and
connector positions. Design rules, materials and the parts list are in
[`../docs/08-mechanical-and-wiring.md`](../docs/08-mechanical-and-wiring.md).

## Planned layout

```
mechanical/
├── enclosure/   # shell, service cap, gasket; base-plate drawing (6 mm 6061)
├── brackets/    # under-dash bracket, ARB relay and winch contactor brackets
├── panel/       # switch-panel bezel for the JK dash
└── mockups/     # PLA fit-check models: module and panel envelopes
```

Commit for each part: the parametric source, a STEP export, and the
Bambu Studio `.3mf` with the print profile that was validated, so a reprint
matches the tested part.

## First prints (phase 0.5)

| Part | Material | Purpose |
|---|---|---|
| Module envelope 160 × 120 × 50 mm with connector stubs | PLA | Check the glovebox and the rear cargo-area spot, including connector and harness clearance |
| Panel envelope | PLA | Find a dash location and reach |

## Print profiles (starting points)

| Part | Material | Nozzle | Walls | Infill | Notes |
|---|---|---|---|---|---|
| Shell, cap | ASA | 0.4 mm | 4–6 | 40 %, 100 % within 10 mm of sealing faces and inserts | Sealing rim printed flat, facing up; seam away from the gasket path |
| Gasket (cab build) | TPU 95A | 0.4 mm | — | 100 % | External spool, not through the AMS; engine-bay builds use silicone instead |
| Engine-bay brackets | PET-CF or PAHT-CF | 0.4–0.6 mm hardened steel | 6 | 60 % | Dry the filament first; metal inserts at every bolt |
| Engine-bay shell (alternative build) | PAHT-CF | 0.6 mm hardened steel | ≥ 6, walls ≥ 3 mm | 100 % | Metal compression limiters at every bolt, silicone gasket, bolts into tapped holes in the plate; see the engine-bay build in doc 08 |
| Panel bezel | ASA | 0.4 mm | 3 | 20 % | Light pipes or a thin diffuser layer over LEDs |
| Keep-alive injector housings | PAHT-CF | 0.4–0.6 mm hardened steel | ≥ 4 | 100 % | Grille area: warm and wet; pot the diodes in silicone, sealed connectors both ends |
