"""Back-of-envelope budgets for the power control module.

Every number the design docs quote for dissipation, junction temperature,
enclosure temperature, copper width, harness voltage drop and sleep current
comes from this script, so changing an assumption here and re-running it
keeps the docs honest.

Usage:
    python3 tools/budget.py                                  # JK default: MMSS, cab, printed + plate
    python3 tools/budget.py --build LMSS --location engine_bay --enclosure alu
    python3 tools/budget.py --build M+MSS --location engine_bay_hot --scenario jk_expected
    python3 tools/budget.py --build SSSS --location tuffy --scenario jk_rear_expected --aux rear

Standard library only. Device figures are typical datasheet values and are
marked "verify" in the docs until the parts are locked in the BOM. Thermal
resistances are assumptions until validation test TH-1 measures them.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

TJ_MAX_C = 150  # PROFET+2 and automotive MOSFET junction limit
TJ_MARGIN_C = 15  # design margin below TJ_MAX_C
# The enclosure base stands in for the logic-board temperature. AEC-Q100
# Grade 1 parts are rated to 125 C ambient; keep 10 C of margin.
T_BASE_MAX_C = 115

# --- Output channel classes -------------------------------------------------


@dataclass(frozen=True)
class ChannelClass:
    name: str
    device: str
    i_cont_a: float  # rated continuous current
    i_trip_a: float  # hardware short-circuit trip (approximate)
    rds_25c_mohm: float  # per switch, typical at 25 C
    n_parallel: int  # switches sharing the current
    n_series: int  # 2 for back-to-back (reverse-blocking) pairs
    hot_factor: float  # Rds(on) multiplier at hot junction
    shunt_mohm: float  # external shunt, 0 when sensing is integrated
    rth_j_base_k_per_w: float  # junction to enclosure base, per switch (assumed)

    def r_path_mohm(self) -> float:
        """Hot on-resistance of the switch network, excluding the shunt."""
        r_one = self.rds_25c_mohm * self.hot_factor
        return r_one * self.n_series / self.n_parallel


CLASSES = {
    "S": ChannelClass(
        name="S (small)",
        device="BTS7004-1EPP PROFET+2",
        i_cont_a=10,
        i_trip_a=45,
        rds_25c_mohm=4.4,
        n_parallel=1,
        n_series=1,
        hot_factor=2.0,
        shunt_mohm=0.0,
        rth_j_base_k_per_w=15,
    ),
    "M": ChannelClass(
        name="M (medium)",
        device="BTS7002-1EPP PROFET+2",
        i_cont_a=20,
        i_trip_a=75,
        rds_25c_mohm=2.6,
        n_parallel=1,
        n_series=1,
        hot_factor=2.0,
        shunt_mohm=0.0,
        rth_j_base_k_per_w=12,
    ),
    "M+": ChannelClass(
        name="M+ (medium, low-loss part)",
        device="BTS50015-1TAD PROFET, TO-263-7",
        i_cont_a=25,
        i_trip_a=100,
        rds_25c_mohm=1.5,
        n_parallel=1,
        n_series=1,
        hot_factor=2.0,
        shunt_mohm=0.0,
        rth_j_base_k_per_w=8,
    ),
    "L": ChannelClass(
        name="L (large)",
        device="2x2 60 V N-FET back-to-back + smart gate driver",
        i_cont_a=40,
        i_trip_a=150,
        rds_25c_mohm=1.2,
        n_parallel=2,
        n_series=2,
        hot_factor=1.8,
        shunt_mohm=0.25,
        rth_j_base_k_per_w=20,
    ),
    "A": ChannelClass(
        name="AUX (coil driver)",
        device="BTS7008-2EPA PROFET+2 dual, per channel",
        i_cont_a=5,
        i_trip_a=30,
        rds_25c_mohm=8.0,
        n_parallel=1,
        n_series=1,
        hot_factor=2.0,
        shunt_mohm=0.0,
        rth_j_base_k_per_w=30,
    ),
}


def channel_loss(c: ChannelClass, current_a: float) -> dict:
    r_one_hot = c.rds_25c_mohm * c.hot_factor
    i_per_switch = current_a / c.n_parallel
    p_per_switch = i_per_switch**2 * r_one_hot / 1000
    p_switches = p_per_switch * c.n_parallel * c.n_series
    p_shunt = current_a**2 * c.shunt_mohm / 1000
    return {
        "p_per_switch_w": p_per_switch,
        "p_switches_w": p_switches,
        "p_shunt_w": p_shunt,
        "p_total_w": p_switches + p_shunt,
        "drop_mv": current_a * (c.r_path_mohm() + c.shunt_mohm),
    }


# --- Builds, enclosures, locations -------------------------------------------

BUILDS = {
    "MMSS": ["M", "M", "S", "S"],  # JK front module: lighting on the main outputs
    "M+MSS": ["M+", "M", "S", "S"],  # engine-bay JK: low-loss part on the light-bar slot
    "LMSS": ["L", "M", "S", "S"],  # single-motor compressor on the L slot
    "SSSS": ["S", "S", "S", "S"],  # JK rear module
}

# Per-slot load currents (A). None = every slot at its class rating.
SCENARIOS = {
    "rated": None,
    # Single-module JK: light bar, front pods, rear floods, rock lights.
    "jk_expected": [20, 12, 8, 4],
    # Two-module JK, front: light bar, bumper pods, ditch lights, front rock lights.
    "jk_front_expected": [20, 12, 6, 3],
    # Two-module JK, rear: rear flood, rear rock lights, RIGID Chase courtesy
    # (green wire), camp lights. No fridge on this JK.
    "jk_rear_expected": [8, 4, 0.3, 4],
}

# Steady AUX loads (A). Front: ARB relay coil, winch contactor hold
# (economised coil), rocker indicator LED, spare. Rear: the RIGID Chase's
# trail, brake, strobe and reverse wires, all on, at RIGID's 14 V figures.
AUX_LOADS_A = {
    "front": [0.2, 0.13, 0.05, 0.0],
    "rear": [0.3, 1.3, 1.3, 0.7],
}

LOGIC_W = 0.5  # buck, LDO, MCU, transceivers, input pull-ups


@dataclass(frozen=True)
class Enclosure:
    name: str
    rth_k_per_w: float  # enclosure base to ambient, whole module (assumed)


ENCLOSURES = {
    "alu": Enclosure("Die-cast aluminium box on vehicle metal", 1.5),
    "plate": Enclosure("Printed shell + 6 mm aluminium base plate", 2.5),
    "printed": Enclosure("Printed shell only", 6.0),
}

@dataclass(frozen=True)
class Location:
    name: str
    ambient_c: float  # design ambient (assumed until the vehicle is logged)
    extra_rth_k_per_w: float = 0.0  # a second box around the module, e.g. a closed glovebox


# Engine-bay figures: front of the bay while moving, and a hot spot / slow
# crawl on a summer day. The closed glovebox adds the bin's own resistance to
# the cab (assumed 4 K/W for a small closed plastic bin).
LOCATIONS = {
    "cab": Location("Cab, open air (under dash, or plate on dash metal)", 65.0),
    "glovebox": Location("Inside a closed glovebox", 65.0, 4.0),
    "rear_cargo": Location("Rear cargo area", 65.0),
    "tuffy": Location("Inside the Tuffy cargo enclosure (closed steel box)", 65.0, 2.0),
    "engine_bay": Location("Engine bay", 85.0),
    "engine_bay_hot": Location("Engine-bay hot spot", 105.0),
}


def build_thermal(build: str, location: str, enclosure: str, scenario: str = "rated",
                  aux: str = "front") -> dict:
    """Module-level heat: Tj = ambient + P_total * Rth_enc + P_switch * Rth_j_base."""
    cells = [CLASSES[k] for k in BUILDS[build]]
    currents = SCENARIOS[scenario] or [c.i_cont_a for c in cells]
    for c, i in zip(cells, currents):
        if i > c.i_cont_a:
            raise ValueError(f"{i} A exceeds the {c.name} rating in {build}")
    losses = [channel_loss(c, i) for c, i in zip(cells, currents)]
    aux_cls = CLASSES["A"]
    aux_losses = [channel_loss(aux_cls, i) for i in AUX_LOADS_A[aux]]
    p_total = (sum(x["p_total_w"] for x in losses)
               + sum(x["p_total_w"] for x in aux_losses) + LOGIC_W)
    loc = LOCATIONS[location]
    t_base = loc.ambient_c + p_total * (ENCLOSURES[enclosure].rth_k_per_w + loc.extra_rth_k_per_w)
    tj = [t_base + x["p_per_switch_w"] * c.rth_j_base_k_per_w for c, x in zip(cells, losses)]
    return {
        "currents_a": currents,
        "losses_w": [x["p_total_w"] for x in losses],
        "p_total_w": p_total,
        "i_total_a": sum(currents),
        "t_base_c": t_base,
        "tj_c": tj,
        "tj_hottest_c": max(tj),
        "tj_ok": max(tj) <= TJ_MAX_C - TJ_MARGIN_C,
        "base_ok": t_base <= T_BASE_MAX_C,
        "ok": max(tj) <= TJ_MAX_C - TJ_MARGIN_C and t_base <= T_BASE_MAX_C,
    }


# --- PCB copper (IPC-2221 approximation) -------------------------------------

OZ_TO_MIL = 1.378  # 1 oz/ft^2 copper is ~35 um / 1.378 mil thick


def ipc2221_width_mm(current_a: float, rise_c: float, oz: float, external: bool) -> float:
    """Trace width for a given current and temperature rise.

    IPC-2221 is conservative for planes and pours with good heat spreading;
    IPC-2152 charts give narrower results. Treat this as an upper bound.
    """
    k = 0.048 if external else 0.024
    area_mil2 = (current_a / (k * rise_c**0.44)) ** (1 / 0.725)
    width_mil = area_mil2 / (oz * OZ_TO_MIL)
    return width_mil * 0.0254


# --- Harness -----------------------------------------------------------------

# Copper resistance at 20 C, milliohm per metre.
AWG_MOHM_PER_M = {
    4: 0.815,
    6: 1.296,
    8: 2.061,
    10: 3.277,
    12: 5.211,
    14: 8.286,
    16: 13.17,
    18: 20.95,
}


def wire_drop_v(current_a: float, awg: int, length_m: float, round_trip: bool) -> float:
    metres = length_m * (2 if round_trip else 1)
    return current_a * AWG_MOHM_PER_M[awg] * metres / 1000


# Two-module JK (2016 two-door): (module, label, current A, AWG, one-way metres,
# return wired back to the module's ground point rather than to a chassis
# ground at the load). The rear feed is ~4 m on a two-door, ~5 m on a four-door.
EXAMPLE_LOADS = [
    ("Front", "Battery feed to the glovebox module", 60, 6, 3.0, False),
    ("Front", "Light bar (OUT1, M)", 20, 10, 3.5, True),
    ("Front", "Bumper pods (OUT2, M)", 12, 12, 3.0, True),
    ("Front", "Ditch lights (OUT3, S)", 6, 16, 2.0, True),
    ("Front", "Front rock lights (OUT4, S)", 3, 16, 2.5, True),
    ("Front", "ARB relay coil (AUX1)", 0.2, 18, 3.0, False),
    ("Front", "Winch contactor coil, pull-in (AUX2)", 3.8, 18, 3.0, False),
    ("Rear", "Battery feed to the rear module, 10 AWG, at the 30 A fuse", 30, 10, 4.0, False),
    ("Rear", "Same 10 AWG feed at the expected 20 A", 20, 10, 4.0, False),
    ("Rear", "Rear flood (OUT1, S)", 8, 14, 1.5, True),
    ("Rear", "Rear rock lights (OUT2, S)", 4, 16, 2.0, True),
    ("Rear", "Camp lights (OUT4, S)", 4, 16, 3.0, True),
    # All five Chase functions on: 0.3 + 1.3 + 1.3 + 0.7 + 0.3 A. Conservative:
    # only the shared ground carries the sum; each feed carries its own function.
    ("Rear", "RIGID Chase, all five functions on (AUX1-4, OUT3)", 3.9, 18, 2.5, True),
]

# Two-module JK system cases: (case, build, location, scenario, AUX loads)
SYSTEM_CASES = [
    ("Front, closed glovebox", "MMSS", "glovebox", "rated", "front"),
    ("Front, closed glovebox", "MMSS", "glovebox", "jk_front_expected", "front"),
    ("Front, vented glovebox or plate on dash metal", "MMSS", "cab", "jk_front_expected", "front"),
    ("Rear, inside the Tuffy enclosure", "SSSS", "tuffy", "rated", "rear"),
    ("Rear, inside the Tuffy enclosure", "SSSS", "tuffy", "jk_rear_expected", "rear"),
]


# --- Sleep current -----------------------------------------------------------

# (item, quantity, microamps each) -- typical datasheet values, assumed.
SLEEP_ITEMS = [
    ("Buck regulator, no-load Iq", 1, 25),
    ("5 V -> 3.3 V LDO Iq", 1, 15),
    ("MCU (STM32G474) in Stop 1 with RTC -- assumed, measure", 1, 90),
    ("Accessory CAN transceiver in standby (remote wake)", 1, 15),
    ("Vehicle CAN transceivers, power-gated off", 2, 0),
    ("PROFET+2 devices off (4 single + 2 dual)", 6, 1),
    # Ground-switched inputs need a pull-up to wake the module, but the ADC
    # divider loads a weak pull-up below the threshold, so in sleep the 2.2 k
    # wetting pull-up is pulsed for 1 ms every 200 ms (0.5 % duty) instead.
    ("Pulsed input scan, switch open (0.35 mA x 0.5 %)", 8, 2),
    ("MCU wake-ups for the scan (~4 mA x 0.5 %)", 1, 20),
    ("VBAT sense divider, gated off", 1, 1),
    ("Keep-alive buck and eFuses, disabled", 1, 2),
    ("Reverse-polarity / TVS leakage", 1, 5),
]


# --- Report ------------------------------------------------------------------


def cell(build: str, location: str, enclosure: str, scenario: str, aux: str = "front") -> str:
    """'Tj / base' with the value that breaks a limit in bold."""
    t = build_thermal(build, location, enclosure, scenario, aux)
    tj = f"{t['tj_hottest_c']:.0f}"
    base = f"{t['t_base_c']:.0f}"
    return f"{tj if t['tj_ok'] else f'**{tj}**'} / {base if t['base_ok'] else f'**{base}**'}"


def matrix(scenario: str, builds: list[str],
           locations: tuple[str, ...] = ("cab", "engine_bay", "engine_bay_hot")) -> list[str]:
    """Hottest junction / base temperature for each build, location and enclosure."""
    out = ["| Build | Location | " + " | ".join(e.name for e in ENCLOSURES.values()) + " |",
           "|---|---|" + "---:|" * len(ENCLOSURES)]
    for b in builds:
        for loc in locations:
            cells = [cell(b, loc, enc, scenario) for enc in ENCLOSURES]
            out.append(f"| {b} | {loc} | " + " | ".join(cells) + " |")
    return out


def system_table() -> list[str]:
    out = ["| Case | Build | Loads | " + " | ".join(e.name for e in ENCLOSURES.values()) + " |",
           "|---|---|---|" + "---:|" * len(ENCLOSURES)]
    for case, build, loc, scenario, aux in SYSTEM_CASES:
        loads = "rated" if SCENARIOS[scenario] is None else str(SCENARIOS[scenario])
        cells = [cell(build, loc, enc, scenario, aux) for enc in ENCLOSURES]
        out.append(f"| {case} | {build} | {loads} | " + " | ".join(cells) + " |")
    return out


def report(build: str, location: str, enclosure: str, scenario: str, aux: str = "front") -> str:
    out: list[str] = []
    sel = build_thermal(build, location, enclosure, scenario, aux)

    out.append(f"## Cells: {build}, {location}, {ENCLOSURES[enclosure].name}, "
               f"loads '{scenario}', AUX loads '{aux}' {AUX_LOADS_A[aux]} A\n")
    out.append(f"Ambient {LOCATIONS[location].ambient_c:.0f} C, enclosure base "
               f"{sel['t_base_c']:.0f} C ({sel['p_total_w']:.1f} W in the module).\n")
    out.append("| Slot | Class | Device | Load (A) | Path R hot (mOhm) | Drop (mV) | "
               "Loss (W) | Tj est (C) |")
    out.append("|---|---|---|---:|---:|---:|---:|---:|")
    for n, (k, i, tj) in enumerate(zip(BUILDS[build], sel["currents_a"], sel["tj_c"]), start=1):
        c = CLASSES[k]
        x = channel_loss(c, i)
        out.append(
            f"| OUT{n} | {c.name} | {c.device} | {i:g} | {c.r_path_mohm():.2f} | "
            f"{x['drop_mv']:.0f} | {x['p_total_w']:.2f} | {tj:.0f} |"
        )

    limit = TJ_MAX_C - TJ_MARGIN_C
    out.append("\n## Hottest junction / enclosure base (C), every slot at its rating\n")
    out.append(f"Bold = hottest junction above {limit} C ({TJ_MARGIN_C} C below the "
               f"{TJ_MAX_C} C limit), or base above {T_BASE_MAX_C} C (logic-board "
               f"parts are rated to 125 C).\n")
    out.extend(matrix("rated", list(BUILDS)))
    out.append("\n## Hottest junction / enclosure base (C), expected JK loads "
               f"{SCENARIOS['jk_expected']} A\n")
    out.extend(matrix("jk_expected", ["MMSS", "M+MSS"]))
    out.append("\n## Two-module JK system: hottest junction / enclosure base (C)\n")
    out.extend(system_table())

    out.append("\n## Copper width (IPC-2221, 20 C rise, upper bound)\n")
    out.append("| Current (A) | 2 oz outer (mm) | 3 oz outer (mm) | 2 oz inner (mm) |")
    out.append("|---:|---:|---:|---:|")
    for amps in (10, 20, 40, 60, 80):
        out.append(
            f"| {amps} | {ipc2221_width_mm(amps, 20, 2, True):.1f} | "
            f"{ipc2221_width_mm(amps, 20, 3, True):.1f} | "
            f"{ipc2221_width_mm(amps, 20, 2, False):.1f} |"
        )

    out.append("\n## Harness voltage drop (20 C copper)\n")
    out.append("| Module | Run | Current (A) | AWG | One-way (m) | Drop (V) | Drop at 13.5 V (%) |")
    out.append("|---|---|---:|---:|---:|---:|---:|")
    for module, label, amps, awg, metres, rt in EXAMPLE_LOADS:
        v = wire_drop_v(amps, awg, metres, rt)
        out.append(f"| {module} | {label} | {amps} | {awg} | {metres} | {v:.2f} | "
                   f"{100 * v / 13.5:.1f} |")

    out.append("\n## Sleep current (ignition off, all outputs off)\n")
    out.append("| Item | Qty | uA each | uA total |")
    out.append("|---|---:|---:|---:|")
    total_ua = 0
    for item, qty, ua in SLEEP_ITEMS:
        total_ua += qty * ua
        out.append(f"| {item} | {qty} | {ua} | {qty * ua} |")
    out.append(f"| **Total** | | | **{total_ua}** |")
    days = 0.5 * 60 / (total_ua / 1e6) / 24  # 50 % of a 60 Ah battery
    out.append(f"\n{total_ua} uA would take {days:.0f} days to drain half of a 60 Ah "
               f"battery; lead-acid self-discharge gets there first.")

    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--build", choices=BUILDS, default="MMSS")
    parser.add_argument("--location", choices=LOCATIONS, default="cab")
    parser.add_argument("--enclosure", choices=ENCLOSURES, default="plate")
    parser.add_argument("--scenario", choices=SCENARIOS, default="rated")
    parser.add_argument("--aux", choices=AUX_LOADS_A, default="front")
    args = parser.parse_args()
    print(report(args.build, args.location, args.enclosure, args.scenario, args.aux))


if __name__ == "__main__":
    main()
