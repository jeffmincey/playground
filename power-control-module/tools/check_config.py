"""Check the module configuration files against the rule grammar in docs/07.

Every rule expression (condition, force_off, max_on_defer, dip_check_while
and flash conditions) must be at most four terms joined by AND/OR, each
`source op [value] [for <ms>]` with a source the firmware knows. A remote
source must come from a configured peer, a rule must not read a DISABLED
input, numeric fields must be numbers, and on_host_loss must be one of
OFF/HOLD/RELEASE — which also catches a bare OFF that YAML parsed as false.

Usage:
    python3 tools/check_config.py                     # every config/*.yaml
    python3 tools/check_config.py config/jk-rear.yaml

Needs PyYAML (the repository's pixi environment has it).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

_N = r"[1-8]"
LOCAL = (
    rf"IN{_N}|IGN|VIN{_N}|VS{_N}|VBAT|IN{_N}_TURN|IN{_N}_BRAKE|OUT[1-4]|AUX[1-4]|KA[12]|"
    r"(?:OUT|AUX)[1-4]_I|(?:OUT|AUX)[1-4]_FAULT|ENGINE_RUNNING|VBAT_SAG|VBAT_EST"
)
REMOTE = rf"M[0-3]\.(?:IN{_N}|IGN|VS{_N}|VBAT|OUT[1-4]|AUX[1-4]|(?:OUT|AUX)[1-4]_I)"
_NUM = r"-?\d+(?:\.\d+)?"
VALUE = rf"{_NUM}|hysteresis\(\s*{_NUM}\s*,\s*{_NUM}\s*\)"
TERM = re.compile(
    rf"^(?P<src>{REMOTE}|{LOCAL})\s+(?:is_on|is_off|rising|falling|[<>]\s+(?:{VALUE}))"
    r"(?:\s+for\s+\d+)?$"
)
MAX_TERMS = 4
EXPR_KEYS = ("condition", "force_off", "max_on_defer", "dip_check_while")
NUMERIC_KEYS = ("rating_a", "open_load_a", "max_supply_v", "level_v", "current_limit_a",
                "soft_start_ms", "inrush_ms", "hold_s")
HOST_LOSS = {"OFF", "HOLD", "RELEASE"}


def terms(expr: str) -> list[str]:
    return [t.strip() for t in re.split(r"\s+(?:AND|OR)\s+", expr.strip())]


def _expressions(name: str, out: dict) -> list[tuple[str, object]]:
    found = [(f"{name}.{k}", out[k]) for k in EXPR_KEYS if k in out]
    rule = out.get("rule") or {}
    found += [(f"{name}.rule.{k}", rule[k]) for k in EXPR_KEYS if k in rule]
    found += [(f"{name}.rule.flash[{i}].when", f.get("when"))
              for i, f in enumerate(rule.get("flash") or [])]
    return found


def check(cfg: dict) -> list[str]:
    """One message per problem in a parsed configuration; empty when it is clean."""
    errors = []
    address = cfg["module"]["address"]
    peers = set(cfg["module"].get("peers", []))
    disabled = {k for k, v in (cfg.get("inputs") or {}).items() if v.get("mode") == "DISABLED"}

    expressions = []
    for group in ("outputs", "aux", "keep_alive"):
        for name, out in (cfg.get(group) or {}).items():
            for key in NUMERIC_KEYS:
                # type() rather than isinstance(): YAML's true/false are ints to isinstance.
                if key in out and type(out[key]) not in (int, float):
                    errors.append(f"{name}.{key} = {out[key]!r} is not a number")
            if "on_host_loss" in out and out["on_host_loss"] not in HOST_LOSS:
                errors.append(f"{name}.on_host_loss = {out['on_host_loss']!r} (quote it)")
            expressions += _expressions(name, out)

    for where, expr in expressions:
        if not isinstance(expr, str):
            errors.append(f"{where} = {expr!r} is not an expression")
            continue
        parts = terms(expr)
        if len(parts) > MAX_TERMS:
            errors.append(f"{where}: {len(parts)} terms, at most {MAX_TERMS}")
        for term in parts:
            m = TERM.match(term)
            if not m:
                errors.append(f"{where}: cannot parse {term!r}")
                continue
            src = m.group("src")
            if src.startswith("M"):
                if int(src[1]) == address or int(src[1]) not in peers:
                    errors.append(f"{where}: {src} is not from a configured peer")
            elif src.split("_")[0] in disabled:
                errors.append(f"{where}: {src} reads a DISABLED input")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args()
    files = args.files or sorted(CONFIG_DIR.glob("*.yaml"))
    failed = False
    for path in files:
        errors = check(yaml.safe_load(path.read_text()))
        print(f"{path}: {len(errors)} problems")
        for e in errors:
            print(f"  {e}")
        failed |= bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
