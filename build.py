#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools>=4.50"]
# ///
"""Build Fira Code SC.

Merges IBM Plex Sans SC CJK glyphs into Fira Code, scaling them so that
one CJK glyph advances exactly 2x one Fira Code cell. Result: a coding
font where mixed Latin/CJK ASCII art aligns on a character grid.

Sources are pinned release artifacts:
  - Fira Code 6.2            (OFL 1.1, no Reserved Font Name)
  - IBM Plex Sans SC 1.1.0   (OFL 1.1, Reserved Font Name "Plex")

Usage:
  uv run build.py [--out dist] [--styles Regular,Bold,...]
"""

from __future__ import annotations

import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

FONT_VERSION = "0.1.0"
FAMILY = "Fira Code SC"
PS_FAMILY = "FiraCodeSC"

FIRA_URL = "https://github.com/tonsky/FiraCode/releases/download/6.2/Fira_Code_v6.2.zip"
PLEX_URL = (
    "https://github.com/IBM/plex/releases/download/"
    "%40ibm/plex-sans-sc%401.1.0/ibm-plex-sans-sc.zip"
)

# (style name, fira ttf, plex ttf)
STYLES = [
    ("Regular", "FiraCode-Regular.ttf", "IBMPlexSansSC-Regular.ttf"),
    ("Bold", "FiraCode-Bold.ttf", "IBMPlexSansSC-Bold.ttf"),
    ("Light", "FiraCode-Light.ttf", "IBMPlexSansSC-Light.ttf"),
    ("Medium", "FiraCode-Medium.ttf", "IBMPlexSansSC-Medium.ttf"),
    ("SemiBold", "FiraCode-SemiBold.ttf", "IBMPlexSansSC-SemiBold.ttf"),
    # Fira Code Retina (~450) pairs best with Plex Text (~450).
    ("Retina", "FiraCode-Retina.ttf", "IBMPlexSansSC-Text.ttf"),
]

# Codepoint ranges taken from Plex (everything else stays Fira Code).
WIDE_RANGES = [
    (0x2E80, 0x303F),   # CJK radicals, Kangxi radicals, CJK punctuation
    (0x3040, 0x30FF),   # kana (Plex SC carries some)
    (0x31C0, 0x9FFF),   # strokes, enclosed, compat, CJK unified
    (0xF900, 0xFAFF),   # CJK compatibility ideographs
    (0xFE30, 0xFE4F),   # CJK vertical forms
    (0xFF00, 0xFF60),   # fullwidth forms
    (0xFFE0, 0xFFE6),   # fullwidth signs
    (0x20000, 0x3FFFF), # CJK extensions B+
]

COPYRIGHT = (
    "Fira Code SC: Copyright (c) 2026, iamwrm "
    "(https://github.com/iamwrm/fira_code_sc). "
    "Fira Code: Copyright (c) 2014, The Fira Code Project Authors "
    "(https://github.com/tonsky/FiraCode). "
    "IBM Plex Sans SC: Copyright (c) 2017 IBM Corp. "
    'with Reserved Font Name "Plex".'
)


def is_wide(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in WIDE_RANGES)


def fetch(url: str, dest: Path) -> None:
    if dest.exists():
        return
    print(f"fetch {url}")
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    tmp.rename(dest)


def prepare_sources(work: Path) -> tuple[Path, Path]:
    work.mkdir(parents=True, exist_ok=True)
    fira_zip, plex_zip = work / "fira.zip", work / "plex.zip"
    fetch(FIRA_URL, fira_zip)
    fetch(PLEX_URL, plex_zip)
    for z, d in ((fira_zip, work / "fira"), (plex_zip, work / "plex")):
        if not d.exists():
            with zipfile.ZipFile(z) as zf:
                zf.extractall(d)
    fira_dir = work / "fira" / "ttf"
    plex_candidates = list((work / "plex").rglob("ttf/hinted"))
    assert plex_candidates, "Plex hinted ttf dir not found"
    return fira_dir, plex_candidates[0]


def set_name(name_table, string: str, name_id: int) -> None:
    name_table.setName(string, name_id, 3, 1, 0x409)  # Windows
    name_table.setName(string, name_id, 1, 0, 0)      # Mac


def merge(fira_path: Path, plex_path: Path, out_path: Path, style: str) -> dict:
    fira = TTFont(str(fira_path))
    plex = TTFont(str(plex_path))

    fira_cmap = fira.getBestCmap()
    plex_cmap = plex.getBestCmap()
    fira_adv = fira["hmtx"][fira_cmap[0x0020]][0]
    plex_han_adv = plex["hmtx"][plex_cmap[0x4E00]][0]
    target_adv = 2 * fira_adv
    scale = target_adv / plex_han_adv

    todo = sorted(
        cp for cp in plex_cmap if is_wide(cp) and cp not in fira_cmap
    )

    glyf = fira["glyf"]
    hmtx = fira["hmtx"]
    plex_glyphs = plex.getGlyphSet()
    plex_hmtx = plex["hmtx"]
    order = fira.getGlyphOrder()
    existing = set(order)

    added: dict[int, str] = {}
    src_done: dict[str, str] = {}
    y_min, y_max = 0, 0
    for cp in todo:
        src = plex_cmap[cp]
        if src in src_done:
            added[cp] = src_done[src]
            continue
        new_name = f"cjk{cp:05X}"
        if new_name in existing:
            new_name += ".sc"
        rec = DecomposingRecordingPen(plex_glyphs)
        plex_glyphs[src].draw(rec)
        pen = TTGlyphPen(None)
        rec.replay(TransformPen(RoundingPen(pen), (scale, 0, 0, scale, 0, 0)))
        glyph = pen.glyph()
        glyf[new_name] = glyph
        adv, lsb = plex_hmtx[src]
        hmtx[new_name] = (round(adv * scale), round(lsb * scale))
        # note: glyf.__setitem__ already appended new_name to the shared
        # glyph order list; do not append again.
        existing.add(new_name)
        added[cp] = new_name
        src_done[src] = new_name
        glyph.recalcBounds(glyf)
        if glyph.numberOfContours:
            y_min = min(y_min, glyph.yMin)
            y_max = max(y_max, glyph.yMax)

    fira.setGlyphOrder(fira.getGlyphOrder())
    fira["maxp"].numGlyphs = len(fira.getGlyphOrder())

    # cmap: BMP into every unicode subtable; full repertoire into format 12,
    # creating one if Fira lacks it.
    cmap_table = fira["cmap"]
    has12 = any(t.format == 12 for t in cmap_table.tables)
    if not has12:
        full = {}
        for t in cmap_table.tables:
            if t.isUnicode():
                full.update(t.cmap)
        sub12 = CmapSubtable.newSubtableClass(12)()
        sub12.format, sub12.reserved, sub12.length, sub12.language = 12, 0, 0, 0
        sub12.platID, sub12.platEncID = 3, 10
        sub12.cmap = full
        cmap_table.tables.append(sub12)
    for t in cmap_table.tables:
        if not t.isUnicode():
            continue
        for cp, name in added.items():
            if t.format == 12 or cp <= 0xFFFF:
                t.cmap[cp] = name

    # Widen clipping metrics if scaled CJK glyphs poke out; keep line
    # height (typo/hhea) identical to Fira Code.
    os2 = fira["OS/2"]
    os2.usWinAscent = max(os2.usWinAscent, y_max)
    os2.usWinDescent = max(os2.usWinDescent, -y_min)

    # Names.
    name_table = fira["name"]
    if style in ("Regular", "Bold"):
        family, subfamily = FAMILY, style
    else:
        family, subfamily = f"{FAMILY} {style}", "Regular"
    ps_name = f"{PS_FAMILY}-{style}"
    set_name(name_table, COPYRIGHT, 0)
    set_name(name_table, family, 1)
    set_name(name_table, subfamily, 2)
    set_name(name_table, f"{FONT_VERSION};{PS_FAMILY};{ps_name}", 3)
    set_name(name_table, f"{FAMILY} {style}", 4)
    set_name(name_table, f"Version {FONT_VERSION}", 5)
    set_name(name_table, ps_name, 6)
    set_name(name_table, FAMILY, 16)
    set_name(name_table, style, 17)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fira.save(str(out_path))
    return {
        "style": style,
        "added": len(added),
        "latin_adv": fira_adv,
        "cjk_adv": target_adv,
        "scale": round(scale, 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--work", default=".work")
    ap.add_argument("--styles", default=",".join(s for s, _, _ in STYLES))
    args = ap.parse_args()

    wanted = set(args.styles.split(","))
    fira_dir, plex_dir = prepare_sources(Path(args.work))
    out_dir = Path(args.out)

    results = []
    for style, fira_ttf, plex_ttf in STYLES:
        if style not in wanted:
            continue
        out = out_dir / f"{PS_FAMILY}-{style}.ttf"
        info = merge(fira_dir / fira_ttf, plex_dir / plex_ttf, out, style)
        print(f"built {out}  (+{info['added']} CJK glyphs, "
              f"latin {info['latin_adv']} / cjk {info['cjk_adv']})")
        results.append(out)

    zip_path = out_dir / "FiraCodeSC.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in results:
            zf.write(p, p.name)
        zf.write("LICENSE", "LICENSE")
    print(f"built {zip_path}")


if __name__ == "__main__":
    main()
