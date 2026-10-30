"""build_page.py: write index.html from page.tmpl.html, filling each {{ expression }} from numbers.json (so every model number on the page is
computed, not typed). Expressions are Python, evaluated with N (numbers.json) and the format helpers below.

Run: uv run python docs/review/megafauna/dragon-density/build_page.py
"""
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).parent
N = json.loads((HERE / "numbers.json").read_text())


def sig(x, n=2):
    """x to n significant figures, with thousands separators."""
    if x is None:
        return "n/a"
    if x == 0:
        return "0"
    d = n - 1 - int(math.floor(math.log10(abs(x))))
    v = round(x, d)
    if d <= 0:
        return f"{int(v):,}"
    return f"{v:,.{d}f}"


def f0(x):
    return f"{x:,.0f}"


def f1(x):
    return f"{x:,.1f}"


def f2(x):
    return f"{x:,.2f}"


def pct(x, n=2):
    return sig(100 * x, n) + "%"


def per(x_per_km2):
    """'1 per X km²' from a density per km2."""
    return f"1 per {sig(1.0 / x_per_km2, 2)} km²"


def rng(a, b, n=2, f=None):
    f = f or (lambda v: sig(v, n))
    return f"{f(a)} to {f(b)}"


def S(start):
    """The sensitivity row whose label starts with `start`."""
    return next(r for r in N["sensitivity"]["rows"] if r["label"].startswith(start))


def X(x):
    """A factor as '×0.43'."""
    return f"×{sig(x, 2)}"


def era(arm, e, c, k="per_1000km2"):
    return N[arm]["eras"][e][c][k]


def P(e, c, k):
    return N["paired"][e][c][k]


def sc(e, c, k):
    return N["sword_coast"]["counts"][e][c][k]


def cells(arm, e, *path):
    x = N["cells"][arm][e]
    for p in path:
        x = x[p]
    return x


def rp(arm, c, band, k, n=2, scale=1.0, e="0"):
    """A rich/poor cell (pooled cells), or an en dash where the band has too few cells."""
    r = N["cells"][arm][e]["rich_poor"][c][band]
    if r is None or r.get(k) is None:
        return "–"
    return sig(r[k] * scale, n)


def bs(arm, biome, sit, k, n=2):
    """A biome x situation cell of the game-present table, or an en dash."""
    t = N["cells"].get(arm, {}).get("0", {}).get("biome_situation", {}).get("table", {}).get(biome, {}).get(sit)
    if t is None or t.get(k) is None:
        return "–"
    return sig(t[k], n)


def chk(e, c, nm, k="median"):
    """A channel's share kept (median over the six worlds at roll 7000) as a percentage, or an en dash where the class is empty."""
    r = N["channels_7000"].get(e, {}).get(c, {}).get(nm + "_runs", {})
    v = r.get(k) if r.get("n") else None
    return "–" if v is None else pct(min(v, 9.99), 2)


def chall(e, c):
    """The three channels together (the product of the medians: persecution x overkill x offtake), or an en dash."""
    r = N["channels_7000"].get(e, {}).get(c, {})
    v = [r.get(nm + "_runs", {}).get("median") if r.get(nm + "_runs", {}).get("n") else None for nm in ("persecution", "overkill", "offtake")]
    return "–" if None in v else pct(v[0] * v[1] * v[2], 2)


def gpv(biome, sit):
    """The game-present best guess, dragons per 10,000 km2 (Section 6): the model's own value (round 3: the persecution rule now follows
    the owner's ruling, so the round-2 half-way adjustment toward the persecution-off arm is retired). None where a cell is empty or thin."""
    t = N["cells"]["on"]["0"]["biome_situation"]["table"][biome][sit]
    if t is None or thin(biome, sit):
        return None
    return t["per_10000km2"]


def ser(arm, ago):
    """World 2a7385 roll 7000's planet-wide dragons at `ago` kyr from its series (arm: with_pressure / no_pressure / no_persecution)."""
    s = {float(k): v["dragons"] for k, v in N["series"][arm].items()}
    return s[min(s, key=lambda x: abs(x - ago))]


def wr(which, arm="off", step="300"):
    """The (min, max) step ratio over the rolls of the world whose median roll is lowest ('lo') or highest ('hi')."""
    by = {}
    for k, v in N["steps"][arm][step].items():
        if v and v.get("ratio"):
            by.setdefault(k.split("_")[0], []).append(v["ratio"])
    w = (min if which == "lo" else max)(by, key=lambda w: sorted(by[w])[len(by[w]) // 2])
    return min(by[w]), max(by[w])


def thin(biome, sit):
    """True where fewer than half the runs have 30 cells of this biome and situation (the pooled value rests on a few worlds)."""
    t = N["cells"]["on"]["0"]["biome_situation"]["table"][biome][sit]
    return t is None or t["runs_30"] < t["runs_n"] / 2


def gp(biome, sit):
    v = gpv(biome, sit)
    return "–" if v is None else sig(v, 2)


B = json.loads((HERE / "charts" / "boxes.json").read_text()) if (HERE / "charts" / "boxes.json").exists() else []

E = {k: v for k, v in globals().items() if k in ("sig", "f0", "f1", "f2", "pct", "per", "rng", "math", "S", "X", "era", "P", "sc", "cells", "rp", "bs", "B", "gp", "gpv", "thin", "ser", "wr")}
E["N"] = N
src = (HERE / "page.tmpl.html").read_text()
SEC = HERE / "sections"  # page fragments: plain.html, abstract.html, and the body's numbered NN-name.html in order
src = src.replace("@@PLAIN@@", (SEC / "plain.html").read_text()).replace("@@ABSTRACT@@", (SEC / "abstract.html").read_text())
src = src.replace("@@BODY@@", "\n".join(p.read_text() for p in sorted(SEC.glob("[0-9]*.html"))))
bad = []


def sub(m):
    try:
        return str(eval(m.group(1), E))
    except Exception as ex:  # noqa: BLE001
        bad.append((m.group(1), repr(ex)))
        return "??"


out = re.sub(r"\{\{(.+?)\}\}", sub, src, flags=re.S)
(HERE / "index.html").write_text(out)
for b in bad:
    print("FAILED:", b)
print("wrote index.html", len(out), "bytes;", len(bad), "failures")
