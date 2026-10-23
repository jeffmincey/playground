"""Sanity checks that keep the design margins in budget.py from drifting."""

from budget import CLASSES, channel_thermal, ipc2221_width_mm, wire_drop_v

MAX_TJ_C = 150  # PROFET+2 and automotive MOSFET absolute junction limit


def test_every_class_stays_below_tj_max_at_85c():
    for c in CLASSES.values():
        t = channel_thermal(c, c.i_cont_a, ambient_c=85)
        assert t["tj_c"] < MAX_TJ_C - 15, c.name  # keep 15 C of margin


def test_hardware_trip_is_well_above_rating():
    for c in CLASSES.values():
        assert c.i_trip_a >= 3 * c.i_cont_a, c.name


def test_trace_width_grows_with_current_and_shrinks_with_copper():
    assert ipc2221_width_mm(40, 20, 2, True) > ipc2221_width_mm(20, 20, 2, True)
    assert ipc2221_width_mm(40, 20, 3, True) < ipc2221_width_mm(40, 20, 2, True)
    assert ipc2221_width_mm(40, 20, 2, False) > ipc2221_width_mm(40, 20, 2, True)


def test_wire_drop_round_trip_doubles():
    one_way = wire_drop_v(20, 10, 3.0, round_trip=False)
    assert abs(wire_drop_v(20, 10, 3.0, round_trip=True) - 2 * one_way) < 1e-12
