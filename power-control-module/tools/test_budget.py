"""Sanity checks that keep the design margins in budget.py from drifting."""

from budget import (
    CLASSES,
    SLEEP_ITEMS,
    TJ_MAX_C,
    TJ_MARGIN_C,
    build_thermal,
    ipc2221_width_mm,
    wire_drop_v,
)

SLEEP_LIMIT_UA = 250  # requirement EL-7


def test_jk_default_has_margin():
    # D-12 / D-13: MMSS in the cab, printed shell on an aluminium base plate.
    t = build_thermal("MMSS", "cab", "plate")
    assert t["ok"], t["tj_hottest_c"]


def test_original_engine_bay_build_still_has_margin_in_aluminium():
    t = build_thermal("LMSS", "engine_bay", "alu")
    assert t["ok"], t["tj_hottest_c"]


def test_printed_only_enclosure_is_rejected_for_the_engine_bay():
    # Documents why the engine-bay option needs metal to sink the heat.
    t = build_thermal("MMSS", "engine_bay", "printed")
    assert t["tj_hottest_c"] > TJ_MAX_C - TJ_MARGIN_C


def test_base_plate_beats_printed_only():
    for location in ("cab", "engine_bay"):
        plate = build_thermal("MMSS", location, "plate")["tj_hottest_c"]
        printed = build_thermal("MMSS", location, "printed")["tj_hottest_c"]
        assert plate < printed


def test_hardware_trip_is_well_above_rating():
    for c in CLASSES.values():
        assert c.i_trip_a >= 3 * c.i_cont_a, c.name


def test_sleep_budget_meets_requirement():
    assert sum(qty * ua for _item, qty, ua in SLEEP_ITEMS) <= SLEEP_LIMIT_UA


def test_trace_width_grows_with_current_and_shrinks_with_copper():
    assert ipc2221_width_mm(40, 20, 2, True) > ipc2221_width_mm(20, 20, 2, True)
    assert ipc2221_width_mm(40, 20, 3, True) < ipc2221_width_mm(40, 20, 2, True)
    assert ipc2221_width_mm(40, 20, 2, False) > ipc2221_width_mm(40, 20, 2, True)


def test_wire_drop_round_trip_doubles():
    one_way = wire_drop_v(20, 10, 3.0, round_trip=False)
    assert abs(wire_drop_v(20, 10, 3.0, round_trip=True) - 2 * one_way) < 1e-12
