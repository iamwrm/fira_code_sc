// Fira Code SC demo sheet.
// Regenerate:
//   uv run build.py
//   typst compile --ignore-system-fonts \
//     --font-path dist \
//     --font-path .work/fira/ttf \
//     --font-path .work/plex/ibm-plex-sans-sc/fonts/complete/ttf/hinted \
//     demo/demo.typ demo/FiraCodeSC-demo.pdf

#set page(paper: "a4", margin: 2.2cm)
#set text(size: 10.5pt)
// raw sets its own font internally; only a show-set rule can restyle it.
#show raw: set text(font: "Fira Code SC", features: ("calt",))

#let box-text = read("box.txt")

#let panel(title, caption, fonts) = block(breakable: false)[
  #text(weight: "bold", size: 11pt)[#title]
  #v(2pt)
  #block(
    fill: luma(247),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
  )[
    #show raw: set text(font: fonts, size: 11pt, features: ("calt",))
    #raw(box-text, block: true)
  ]
  #v(1pt)
  #text(size: 9pt, fill: luma(90))[#caption]
  #v(10pt)
]

#text(size: 20pt, weight: "bold")[Fira Code SC]
#v(2pt)
Fira Code for Latin + IBM Plex Sans SC for CJK, scaled so one CJK glyph
advances *exactly two* Fira Code cells. Every line in the box below is 46
display columns wide (CJK counted as 2), so a correct font must render a
perfectly flush right border.
#v(12pt)

#panel(
  [1 — Naive fallback: Fira Code → IBM Plex Sans SC],
  [CJK falls back at its native width (≈ 1.67 Fira cells): the right border
   drifts on every line containing 中文.],
  ("Fira Code", "IBM Plex Sans SC"),
)

#panel(
  [2 — Fira Code SC (this project)],
  [CJK = exactly 2 cells: flush border, identical Latin glyphs, Fira Code
   ligatures (#raw("->"), #raw("=>"), #raw("!=")) intact — note line 6 renders
   them fused.],
  "Fira Code SC",
)

#block(breakable: false)[
  #text(weight: "bold", size: 11pt)[3 — Simplified-Chinese coverage]
  #v(2pt)
  The chars #text(font: "Fira Code SC")[时 显 查 译] are simplified-only
  forms absent from Japanese fonts (JP has 時 顕 査 訳) — the gap that rules
  out Firple for SC text. Sample:
  #v(4pt)
  #block(
    fill: luma(247), inset: 12pt, radius: 4pt, width: 100%,
  )[
    #show raw: set text(size: 11pt)
    #raw("显示翻译:「时间就是金钱」 // translate & display\nlet 查询结果 = db.query(\"译文\");  // 时显查译", block: true)
  ]
]

#v(1fr)
#text(size: 8.5pt, fill: luma(120))[
  Sources: Fira Code 6.2 (OFL 1.1) · IBM Plex Sans SC 1.1.0 (OFL 1.1, RFN
  "Plex") · SIL OFL 1.1 · github.com/iamwrm/fira_code_sc
]
