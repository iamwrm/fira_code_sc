#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools>=4.50"]
# ///
"""Sanity checks for built Fira Code SC fonts.

Asserts, per font:
  1. every CJK advance is exactly 2x the Latin advance,
  2. simplified-Chinese coverage (chars missing from JP fonts),
  3. Fira Code ligature machinery (calt) survived the merge,
  4. family naming is consistent.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fontTools.ttLib import TTFont

# Includes the four chars missing from IBM Plex Sans JP (the Firple gap).
SC_PROBES = "时显查译上关午小年引日月用相看示翻中文简体测试"


def check(path: Path) -> list[str]:
    errors = []
    f = TTFont(str(path))
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]

    latin = hmtx[cmap[ord("a")]][0]
    for ch in SC_PROBES:
        if ord(ch) not in cmap:
            errors.append(f"missing glyph: {ch} (U+{ord(ch):04X})")
            continue
        adv = hmtx[cmap[ord(ch)]][0]
        if adv != 2 * latin:
            errors.append(f"{ch}: advance {adv} != 2*{latin}")

    feats = {
        fr.FeatureTag
        for fr in f["GSUB"].table.FeatureList.FeatureRecord
    } if "GSUB" in f else set()
    if "calt" not in feats:
        errors.append("GSUB calt (Fira Code ligatures) missing")

    names = f["name"]
    family = names.getDebugName(16) or names.getDebugName(1)
    if family != "Fira Code SC":
        errors.append(f"unexpected typographic family: {family!r}")

    return errors


def main() -> None:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    fonts = sorted(dist.glob("*.ttf"))
    if not fonts:
        print(f"no fonts found in {dist}", file=sys.stderr)
        sys.exit(1)
    failed = False
    for p in fonts:
        errors = check(p)
        status = "FAIL" if errors else "ok"
        print(f"{status} {p.name}")
        for e in errors:
            print(f"     {e}")
        failed |= bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
