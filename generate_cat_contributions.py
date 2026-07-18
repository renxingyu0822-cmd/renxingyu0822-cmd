#!/usr/bin/env python3
"""
Fetch real GitHub contribution data and render every cell as a cat-head icon.
Requires env var: GH_TOKEN (PAT with read:user scope)
Optional env var: GITHUB_USERNAME (defaults to renxingyu0822)
"""

import os, json, sys, urllib.request

USERNAME = os.environ.get("GITHUB_USERNAME", "renxingyu0822-cmd")
TOKEN    = os.environ.get("GH_TOKEN", "")

# Light-theme GitHub contribution palette (matches the UI screenshot)
COLORS = {
    "NONE":            "#ebedf0",
    "FIRST_QUARTILE":  "#9be9a8",
    "SECOND_QUARTILE": "#40c463",
    "THIRD_QUARTILE":  "#30a14e",
    "FOURTH_QUARTILE": "#216e39",
}

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        months { name firstDay totalWeeks }
        weeks {
          contributionDays {
            contributionLevel
            date
            weekday
          }
        }
      }
    }
  }
}"""


def fetch_calendar(token, username):
    body = json.dumps({"query": QUERY, "variables": {"login": username}}).encode()
    req  = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


# Cat-head symbol: fits a 11×11 viewBox.
# Circle = face, two polygons = pointy ears.
CAT_SYMBOL = """\
  <defs>
    <symbol id="ch" viewBox="0 0 11 11">
      <circle cx="5.5" cy="7.2" r="4.1" fill="currentColor"/>
      <polygon points="1.3,6.1 3.1,0.8 5.5,4.9" fill="currentColor"/>
      <polygon points="5.5,4.9 7.9,0.8 9.7,6.1" fill="currentColor"/>
    </symbol>
  </defs>"""


def make_svg(calendar):
    CELL = 11
    GAP  = 3
    STEP = CELL + GAP
    PL   = 6    # left pad
    PT   = 22   # top pad  (month labels)
    PR   = 8    # right pad
    PB   = 28   # bottom pad (legend)

    weeks  = calendar["weeks"]
    months = calendar["months"]
    nw     = len(weeks)

    W = PL + nw * STEP - GAP + PR
    H = PT + 7 * STEP - GAP + PB

    # date → week-index, for placing month labels
    date_to_wi = {
        day["date"]: wi
        for wi, week in enumerate(weeks)
        for day in week["contributionDays"]
    }

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    out.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')
    out.append(CAT_SYMBOL)

    # Month labels
    seen_labels = set()
    for month in months:
        wi = date_to_wi.get(month["firstDay"])
        if wi is None:
            continue
        label = month["name"][:3]
        if label in seen_labels:
            continue          # skip duplicate (year wrap)
        seen_labels.add(label)
        x = PL + wi * STEP
        out.append(f'  <text x="{x}" y="14" font-size="10" fill="#57606a" '
                   f'font-family="ui-sans-serif,sans-serif">{label}</text>')

    # Cat-head cells
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            color = COLORS[day["contributionLevel"]]
            x = PL + wi * STEP
            y = PT + day["weekday"] * STEP
            out.append(f'  <use href="#ch" x="{x}" y="{y}" width="{CELL}" height="{CELL}" color="{color}"/>')

    # Legend  (Less □□□□□ More)
    levels = list(COLORS.keys())
    legend_w = 32 + len(levels) * STEP + 28
    lx = (W - legend_w) // 2
    ly = H - PB + 9
    out.append(f'  <text x="{lx}" y="{ly + CELL - 1}" font-size="10" fill="#57606a" '
               f'font-family="ui-sans-serif,sans-serif">Less</text>')
    lx += 30
    for level in levels:
        out.append(f'  <use href="#ch" x="{lx}" y="{ly}" width="{CELL}" height="{CELL}" color="{COLORS[level]}"/>')
        lx += STEP
    out.append(f'  <text x="{lx + 3}" y="{ly + CELL - 1}" font-size="10" fill="#57606a" '
               f'font-family="ui-sans-serif,sans-serif">More</text>')

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: set GH_TOKEN env var (PAT with read:user scope)", file=sys.stderr)
        sys.exit(1)
    print(f"Fetching contributions for @{USERNAME}…")
    cal = fetch_calendar(TOKEN, USERNAME)
    svg = make_svg(cal)
    path = "cat_contributions.svg"
    with open(path, "w") as f:
        f.write(svg)
    print(f"Saved {path}")
