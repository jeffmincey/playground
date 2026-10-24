"""Check the relative links and #anchors in the design documents.

Every relative link in a Markdown file in this folder must point at a file
that exists, and a #fragment into a Markdown file must match one of its
headings, slugged the way GitHub does it (lower case, punctuation dropped,
spaces to hyphens). Fenced code blocks are skipped. Repeated headings, which
GitHub suffixes with -1, -2, are not modelled.

Usage:
    python3 tools/check_links.py

Standard library only.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)\s]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:")  # http:, https:, mailto:


def _outside_code(text: str) -> Iterator[str]:
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield line


def slug(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(text: str) -> set[str]:
    return {slug(m.group(1)) for line in _outside_code(text) if (m := HEADING.match(line))}


def broken_links(root: Path = ROOT) -> list[str]:
    problems = []
    for md in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in md.relative_to(root).parts):
            continue  # caches and other tool folders
        for line in _outside_code(md.read_text()):
            for link in LINK.findall(line):
                if SCHEME.match(link):
                    continue
                path, _, fragment = link.partition("#")
                target = (md.parent / path).resolve() if path else md
                where = f"{md.relative_to(root)}: {link}"
                if not target.exists():
                    problems.append(f"{where} (no such file)")
                elif fragment and target.suffix == ".md" and fragment not in anchors(target.read_text()):
                    problems.append(f"{where} (no such heading)")
    return problems


def main() -> None:
    problems = broken_links()
    for p in problems:
        print(p)
    print(f"{len(problems)} broken links")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
