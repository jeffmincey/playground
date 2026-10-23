"""Back-of-envelope budgets for the power control module.

Every number the design docs quote for dissipation, junction temperature,
copper width, harness voltage drop and sleep current comes from this script,
so changing an assumption here and re-running it keeps the docs honest.

Usage:
    python3 tools/budget.py              # all tables, markdown
    python3 tools/budget.py --ambient 60 # re-run thermal at a cooler ambient

Standard library only. Device figures are typical datasheet values and are
marked "verify" in the docs until the parts are locked in the BOM.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

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
    rth_k_per_w: float  # junction to ambient per switch, as mounted (assumed)

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
        rth_k_per_w=25,
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
        rth_k_per_w=20,
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
        rth_k_per_w=30,
    ),
}


def channel_thermal(c: ChannelClass, current_a: float, ambient_c: float) -> dict:
    r_one_hot = c.rds_25c_mohm * c.hot_factor
    i_per_switch = current_a / c.n_parallel
    p_per_switch = i_per_switch**2 * r_one_hot / 1000
    p_switches = p_per_switch * c.n_parallel * c.n_series
    p_shunt = current_a**2 * c.shunt_mohm / 1000
    return {
        "p_switches_w": p_switches,
        "p_shunt_w": p_shunt,
        "p_total_w": p_switches + p_shunt,
        "tj_c": ambient_c + p_per_switch * c.rth_k_per_w,
        "drop_mv": current_a * (c.r_path_mohm() + c.shunt_mohm),
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


# Example JK loads: (label, channel class, current A, AWG, one-way metres,
# return wired back to battery rather than to a local chassis ground)
EXAMPLE_LOADS = [
    ("Battery feed to module", None, 80, 4, 1.0, False),
    ("Compressor (OUT1, L)", "L", 40, 8, 1.5, True),
    ("50 in light bar (OUT2, M)", "M", 20, 10, 3.0, True),
    ("Rear floods (OUT3, S)", "S", 10, 14, 4.5, True),
    ("Rock lights (OUT4, S)", "S", 6, 16, 3.0, True),
]


# --- Sleep current -----------------------------------------------------------

# (item, quantity, microamps each) -- typical datasheet values, assumed.
SLEEP_ITEMS = [
    ("Buck regulator, no-load Iq", 1, 25),
    ("5 V -> 3.3 V LDO Iq", 1, 15),
    ("MCU in STOP with RTC + EXTI", 1, 10),
    ("CAN transceiver in standby", 2, 15),
    ("PROFET+2 channel off-state", 3, 1),
    ("L-channel gate driver, low-Iq mode", 1, 20),
    # Ground-switched inputs need a pull-up to wake the module, but the ADC
    # divider loads a weak pull-up below the threshold, so in sleep the 2.2 k
    # wetting pull-up is pulsed for 1 ms every 100 ms (1 % duty) instead.
    ("Pulsed input scan, switch open (0.35 mA x 1 %)", 4, 4),
    ("MCU wake-ups for the scan (~2 mA x 1 %)", 1, 20),
    ("VBAT sense divider, gated off", 1, 1),
    ("Reverse-polarity / TVS leakage", 1, 5),
]


# --- Report ------------------------------------------------------------------


def report(ambient_c: float) -> str:
    out: list[str] = []

    out.append(f"## Channel thermal at {ambient_c:.0f} C ambient\n")
    out.append("| Class | Device | I cont (A) | Path R hot (mOhm) | Drop (mV) | "
               "Switch loss (W) | Shunt loss (W) | Tj est (C) |")
    out.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for c in CLASSES.values():
        t = channel_thermal(c, c.i_cont_a, ambient_c)
        out.append(
            f"| {c.name} | {c.device} | {c.i_cont_a:.0f} | {c.r_path_mohm():.2f} | "
            f"{t['drop_mv']:.0f} | {t['p_switches_w']:.2f} | {t['p_shunt_w']:.2f} | "
            f"{t['tj_c']:.0f} |"
        )

    build = ["L", "M", "S", "S"]
    total_i = sum(CLASSES[k].i_cont_a for k in build)
    total_p = sum(channel_thermal(CLASSES[k], CLASSES[k].i_cont_a, ambient_c)["p_total_w"]
                  for k in build)
    out.append(f"\nDefault build {''.join(build)}: {total_i:.0f} A continuous total, "
               f"{total_p:.1f} W in the power stage with every channel at its rating.\n")

    out.append("## Copper width (IPC-2221, 20 C rise, upper bound)\n")
    out.append("| Current (A) | 2 oz outer (mm) | 3 oz outer (mm) | 2 oz inner (mm) |")
    out.append("|---:|---:|---:|---:|")
    for amps in (10, 20, 40, 80):
        out.append(
            f"| {amps} | {ipc2221_width_mm(amps, 20, 2, True):.1f} | "
            f"{ipc2221_width_mm(amps, 20, 3, True):.1f} | "
            f"{ipc2221_width_mm(amps, 20, 2, False):.1f} |"
        )

    out.append("\n## Harness voltage drop (20 C copper)\n")
    out.append("| Run | Current (A) | AWG | One-way (m) | Drop (V) | Drop at 13.5 V (%) |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for label, _cls, amps, awg, metres, rt in EXAMPLE_LOADS:
        v = wire_drop_v(amps, awg, metres, rt)
        out.append(f"| {label} | {amps} | {awg} | {metres} | {v:.2f} | {100 * v / 13.5:.1f} |")

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
    parser.add_argument("--ambient", type=float, default=85.0, help="ambient, C")
    args = parser.parse_args()
    print(report(args.ambient))


if __name__ == "__main__":
    main()
