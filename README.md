# Fira Code SC

[Fira Code](https://github.com/tonsky/FiraCode) for Latin/code, with
Simplified Chinese glyphs merged in from
[IBM Plex Sans SC](https://github.com/IBM/plex), scaled so that **one CJK
character advances exactly 2× one Fira Code cell**.

The same recipe as [Firple](https://github.com/negset/Firple)
(Fira Code + IBM Plex Sans **JP**), but for Simplified Chinese — including
the simplified-only codepoints a JP font lacks (时, 显, 查, 译, …).

```text
| 显示翻译                             |      ← flush,
| It's not x, it's ...                 |      ← because CJK = exactly 2 cells
+--------------------------------------+
```

## Why

Mixed Latin/CJK ASCII art, box diagrams, and tables only align when the
font guarantees an integer width ratio. Generic fallback (e.g. Fira Code →
PingFang SC) renders CJK at ≈1.67× a Fira cell, so nothing lines up.
Fira Code advances 0.615 em; here Plex SC han glyphs are scaled to 1.231 em
— exactly 2:1, the same figure Firple uses.

**See it:** [demo/FiraCodeSC-demo.pdf](demo/FiraCodeSC-demo.pdf) — the same
46-column box rendered with naive fallback (ragged) vs Fira Code SC (flush),
plus ligature and SC-coverage samples. Regenerate with
[typst](https://typst.app): the command is at the top of
[demo/demo.typ](demo/demo.typ).

## Install

Grab TTFs from [Releases](../../releases), or build locally:

```bash
uv run build.py            # downloads pinned sources, writes dist/
uv run verify.py dist      # 2:1 metrics + SC coverage + ligature checks
```

VS Code:

```jsonc
"editor.fontFamily": "Fira Code SC",
"editor.fontLigatures": true
```

## Styles

| Fira Code | IBM Plex Sans SC |
|---|---|
| Regular | Regular |
| Bold | Bold |
| Light | Light |
| Medium | Medium |
| SemiBold | SemiBold |
| Retina (~450) | Text (~450) |

Italics are not built (Plex Sans SC has no italic).

## What the build does

`build.py` (pure [fontTools](https://github.com/fonttools/fonttools), no
FontForge):

1. downloads pinned releases — Fira Code 6.2, IBM Plex Sans SC 1.1.0;
2. copies CJK-range glyphs (`U+2E80…U+9FFF`, compat, fullwidth forms,
   extensions B+) that Fira Code doesn't cover, decomposing composites and
   scaling outlines by `2 × fira_advance / plex_advance`;
3. adds a format-12 cmap subtable for non-BMP ideographs;
4. keeps Fira Code's line metrics (line height unchanged for pure code) and
   only widens Win clip metrics for the taller CJK glyphs;
5. leaves Fira Code's GSUB untouched — all ligatures (`calt`) keep working.

CJK OpenType features from Plex (e.g. vertical forms) are not carried over.

## License

[SIL Open Font License 1.1](LICENSE).

- Fira Code — OFL 1.1, no Reserved Font Name
- IBM Plex Sans SC — OFL 1.1, Reserved Font Name **"Plex"** (this font's
  name intentionally does not contain it)
- "Fira Code SC" declares no additional Reserved Font Name

Not affiliated with tonsky, IBM, or the Firple project.
