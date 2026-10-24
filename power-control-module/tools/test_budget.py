"""Sanity checks that keep the design margins in budget.py from drifting."""

from budget import (
    CLASSES,
    SLEEP_ITEMS,
    TJ_MARGIN_C,
    TJ_MAX_C,
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


def test_engine_bay_expected_loads_fit_a_printed_shell_on_the_plate():
    t = build_thermal("MMSS", "engine_bay", "plate", "jk_expected")
    assert t["ok"], (t["tj_hottest_c"], t["t_base_c"])


def test_hot_engine_bay_needs_the_low_loss_light_bar_part():
    plain = build_thermal("MMSS", "engine_bay_hot", "plate", "jk_expected")
    low_loss = build_thermal("M+MSS", "engine_bay_hot", "plate", "jk_expected")
    assert not plain["ok"]
    assert low_loss["ok"], (low_loss["tj_hottest_c"], low_loss["t_base_c"])


def test_printed_only_is_rejected_in_the_hot_engine_bay_even_at_expected_loads():
    t = build_thermal("M+MSS", "engine_bay_hot", "printed", "jk_expected")
    assert not t["base_ok"]


ASA_HDT_C = 100  # Bambu ASA heat deflection temperature at 0.45 MPa


def test_front_module_in_a_closed_glovebox_fits_asa_at_expected_loads():
    t = build_thermal("MMSS", "glovebox", "plate", "jk_front_expected")
    assert t["ok"] and t["t_base_c"] < ASA_HDT_C, (t["tj_hottest_c"], t["t_base_c"])


def test_closed_glovebox_at_full_rating_runs_an_asa_shell_too_hot():
    # Documents why the glovebox needs venting or a metal mount for full-rating use.
    assert build_thermal("MMSS", "glovebox", "plate", "rated")["t_base_c"] > ASA_HDT_C


def test_rear_module_has_margin_even_without_the_plate():
    t = build_thermal("SSSS", "rear_cargo", "printed", "rated", aux="rear")
    assert t["ok"] and t["t_base_c"] < ASA_HDT_C


def test_rear_module_inside_the_tuffy_on_the_plate_has_margin():
    t = build_thermal("SSSS", "tuffy", "plate", "rated", aux="rear")
    assert t["ok"] and t["t_base_c"] < ASA_HDT_C


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
