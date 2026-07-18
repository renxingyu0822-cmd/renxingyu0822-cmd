#!/usr/bin/env python3
"""Generate a contribution-style cat SVG where every cell is a cat-head icon."""

# GitHub dark-theme contribution palette
# 0 = no icon, 1-4 = darkest→brightest green, 9 = very dark (pupils)
COLORS = {
    0: None,
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
    9: "#0d1117",
}

# Pixel-art cat face — 18 cols × 16 rows
# Each filled cell will be rendered as a cat-head icon
CAT = [
    [0,0,2,2,2,0,0,0,0,0,0,0,0,2,2,2,0,0],
    [0,2,3,3,3,2,0,0,0,0,0,0,2,3,3,3,2,0],
    [0,3,3,4,3,3,0,0,0,0,0,0,3,3,4,3,3,0],
    [0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0],
    [0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0],
    [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
    [3,3,3,4,4,4,3,3,3,3,3,3,4,4,4,3,3,3],
    [3,3,3,4,9,4,3,3,3,3,3,3,4,9,4,3,3,3],
    [3,3,3,4,4,4,3,3,3,3,3,3,4,4,4,3,3,3],
    [3,4,4,3,3,3,3,3,3,3,3,3,3,3,3,4,4,3],
    [3,3,4,4,3,3,3,3,3,3,3,3,3,3,4,4,3,3],
    [3,3,3,3,3,3,3,4,4,4,3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3,4,3,3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,4,3,3,4,3,3,3,3,3,3,3],
    [0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0],
    [0,0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,0],
]

CELL = 14   # icon size in px
GAP  = 3    # gap between icons
PAD  = 10   # outer padding

cols = len(CAT[0])
rows = len(CAT)
step = CELL + GAP
W = PAD * 2 + cols * step - GAP
H = PAD * 2 + rows * step - GAP

# Cat-head path in a 14×14 viewBox:
#   - Circle face:   cx=7, cy=9, r=5.5
#   - Left ear:      outer base on circle at ~(1.8, 7.5), tip at (3.5, 1), inner at (7, 6.2)
#   - Right ear:     mirror of left
#   All shapes use fill="currentColor" so <use color="..."> drives the tint.
CAT_SYMBOL = """\
  <defs>
    <symbol id="ch" viewBox="0 0 14 14">
      <circle cx="7" cy="9" r="5.5" fill="currentColor"/>
      <polygon points="1.8,7.5 3.5,1 7,6.2" fill="currentColor"/>
      <polygon points="7,6.2 10.5,1 12.2,7.5" fill="currentColor"/>
    </symbol>
  </defs>"""

lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'  <rect width="{W}" height="{H}" rx="8" fill="#0d1117"/>',
    CAT_SYMBOL,
]

count = 0
for r, row in enumerate(CAT):
    for c, val in enumerate(row):
        color = COLORS.get(val)
        if color is None:
            continue
        x = PAD + c * step
        y = PAD + r * step
        lines.append(
            f'  <use href="#ch" x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" color="{color}"/>'
        )
        count += 1

lines.append("</svg>")

svg = "\n".join(lines)
with open("cat_contributions.svg", "w") as f:
    f.write(svg)

print(f"Generated cat_contributions.svg  {W}x{H}px  {count} cat heads")
