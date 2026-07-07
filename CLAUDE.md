# CLAUDE.md

Guidance for AI coding agents working in this repo.

## What this project is

Fira Code SC is a merged font: Fira Code (Latin) + IBM Plex Sans SC (CJK),
with CJK glyphs advancing **exactly 2× one Fira Code cell** so mixed
Latin/CJK ASCII art and box diagrams align on a character grid.

## Invariants — do not break

1. **The 2:1 metric is exact, not approximate.** Every CJK advance is
   `2 × fira_advance` (2400 units at upm 1950). Never scale, round, or
   "improve" advances. `verify.py` asserts this per char.
2. **Ink size ≠ advance.** Outlines are drawn at `INK_RATIO` (5/6) of the
   metric scale (≈1.03 em, hanzi's natural optical size — Firple's exact
   choice), centered in the advance box. Full-metric ink (~1.11 em) was
   v0.1.0 and looked oversized (国/H caps ratio 1.54 vs Sarasa's 1.19).
   `verify.py` asserts 1.1 ≤ ratio ≤ 1.4.
3. **Fira Code's tables stay untouched** except: glyf/hmtx/cmap additions,
   name, OS/2 usWin{As,De}scent widening, maxp. GSUB is never modified —
   Fira ligatures (`calt`) must keep working. No `fi`/`fl` ligature exists
   in this font; if one appears in rendering, the *editor* is falling back
   to Menlo (see README VS Code notes).
4. **Line metrics (hhea/typo) are Fira Code's.** Don't "fix" line height
   for CJK; only Win clip metrics may grow.
5. **Sources are pinned releases** (Fira Code 6.2, Plex Sans SC 1.1.0),
   downloaded by `build.py`. Never vendor fonts into git; never build from
   floating "latest".
6. **Naming/license:** the font name must never contain "Plex" (IBM's OFL
   Reserved Font Name) or "Firple" (negset's RFN). Output stays OFL 1.1
   with all three copyright lines in LICENSE and nameID 0.

## Commands

```bash
uv run build.py --out dist     # download pinned sources into .work/, build 6 styles + zip
uv run verify.py dist          # metrics/coverage/ligature/naming/ink assertions — must pass
```

Demo PDF (requires typst; run after build.py so .work/ and dist/ exist):

```bash
typst compile --ignore-system-fonts \
  --font-path dist \
  --font-path .work/fira/ttf \
  --font-path .work/plex/ibm-plex-sans-sc/fonts/complete/ttf/hinted \
  demo/demo.typ demo/FiraCodeSC-demo.pdf
```

`demo/box.txt` lines are exactly 46 display columns (CJK counted as 2);
if you edit its content, regenerate the padding with east_asian_width
arithmetic — never eyeball it.

## Workflow

- Python is fontTools-only (no FontForge). Scripts use PEP 723 inline
  deps; run everything through `uv run`.
- After any change to build.py: rebuild, run `verify.py`, and eyeball the
  demo (compile to PNG and inspect — e.g. `typst compile --format png`).
  Metrics bugs that pass verify.py can still be visible (that's how the
  ink-size issue was found).
- Releases: bump `FONT_VERSION` in build.py, commit, tag `vX.Y.Z`, push
  the tag. CI (.github/workflows/build.yml) builds, verifies, and attaches
  TTFs + zip to the GitHub release. Never hand-upload artifacts.
- Testing a candidate font in VS Code on macOS requires a **full quit**
  (Cmd+Q), not Reload Window — Electron snapshots the font list at app
  start.

## Gotchas learned the hard way

- fontTools `glyf.__setitem__` appends to the shared glyph-order list;
  appending manually again corrupts maxp/glyf (assertion on save).
- `TTGlyphSet.draw()` does NOT decompose composites — wrap with
  `DecomposingRecordingPen` before transforming outlines.
- typst: `raw` sets its own font internally; outer `text(font: ...)` is
  silently ignored — restyle raw only via `show raw: set text(...)`.
- Plex Sans SC ships TTF (glyf) in `fonts/complete/ttf/hinted/`; no CFF
  conversion is needed. Copied glyphs lose hinting — acceptable.
- Fira Code has no format-12 cmap; build.py creates one for non-BMP
  ideographs (extensions B+). Keep BMP entries in format 4 too.
