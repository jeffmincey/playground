"""Generate a multi-module CAN database from the single-module can/pcm.dbc.

can/pcm.dbc describes module address 0 and is the source of truth. Module n
uses the same frames at base + 0x10 * n with node PCMn; this script writes one
database covering addresses 0..N-1, so a log of the whole system decodes in
one pass.

Usage:
    python3 tools/gen_dbc.py --modules 2 --out can/pcm-jk.dbc

Standard library only.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

STRIDE = 0x10  # ID offset between module addresses
SOURCE = Path(__file__).resolve().parent.parent / "can" / "pcm.dbc"

# Trailer lines that belong to one frame and must be repeated per module.
PER_FRAME = re.compile(r"^(CM_ (?:BO_|SG_) |BA_ \"[^\"]+\" BO_ |VAL_ )(\d+)(.*)$")


def _shift(line: str, n: int) -> str:
    return line.replace("PCM0", f"PCM{n}")


def generate(src: str, modules: int) -> str:
    if not 1 <= modules <= 4:
        raise ValueError("the address strap allows 1-4 modules")
    lines = src.splitlines()
    first_bo = next(i for i, line in enumerate(lines) if line.startswith("BO_ "))
    first_cm = next(i for i, line in enumerate(lines) if line.startswith("CM_ "))
    header, body, trailer = lines[:first_bo], lines[first_bo:first_cm], lines[first_cm:]

    nodes = " ".join(f"PCM{n}" for n in range(modules))
    out = [re.sub(r"^BU_: HOST PCM0$", f"BU_: HOST {nodes}", line) for line in header]

    for n in range(modules):
        for line in body:
            m = re.match(r"^BO_ (\d+) (.*)$", line)
            if m:
                line = f"BO_ {int(m.group(1)) + STRIDE * n} {m.group(2)}"
            out.append(_shift(line, n))

    for line in trailer:
        if line.startswith('CM_ "'):
            out.append(
                f'CM_ "Power control modules, addresses 0-{modules - 1}, default base ID '
                f'0x6A0; module n uses base + 0x10*n. Generated from pcm.dbc by '
                f'tools/gen_dbc.py - edit pcm.dbc, not this file.";'
            )
            continue
        m = PER_FRAME.match(line)
        if m:
            prefix, frame_id, rest = m.group(1), int(m.group(2)), m.group(3)
            for n in range(modules):
                out.append(_shift(f"{prefix}{frame_id + STRIDE * n}{rest}", n))
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--modules", type=int, default=2)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.write_text(generate(SOURCE.read_text(), args.modules))


if __name__ == "__main__":
    main()
