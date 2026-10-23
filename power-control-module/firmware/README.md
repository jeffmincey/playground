# Firmware

Not started. The design is in [`../docs/07-firmware.md`](../docs/07-firmware.md)
and the wire protocol in [`../docs/06-can-protocol.md`](../docs/06-can-protocol.md)
/ [`../can/pcm.dbc`](../can/pcm.dbc).

## Planned layout

```
firmware/
├── app/
│   ├── protection/     # e-fuse, I²t, retry state machine  (1 kHz)
│   ├── io/             # input conditioning and decode
│   ├── rules/          # rule engine and arbitration        (100 Hz)
│   ├── canproto/       # Command/Status/... per pcm.dbc, config access
│   ├── vehicle/        # vehicle signal map, FDCAN2/3 filters, OBD-II polling client
│   └── config/         # A/B flash storage, defaults, CRC
├── drivers/
│   ├── cell_profet/    # S/M cells: EN, DEN, IS scaling, calibration
│   ├── cell_l/         # L cell: TPS48111-Q1 control, NTC
│   ├── aux_bank/       # BTS7008-2EPA pair: IN, DEN, DSEL-multiplexed sense
│   ├── adc/            # DMA scan, oversampling
│   └── can/            # FDCAN1-3 setup, bus-monitoring mode on FDCAN2/3
├── board/              # pin map, clocks, slot ID read
├── test/               # host-run unit tests for protection/ and rules/
└── tools/              # host-side config compiler (YAML → parameters), CAN log decoding
```

`protection/` and `rules/` are written without hardware dependencies so they
run as host unit tests — the trip-time table in the firmware doc and the
behaviour of `config/jk-example.yaml` are checked on a PC before they run
on a vehicle.
