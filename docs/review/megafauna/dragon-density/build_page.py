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


E = {k: v for k, v in globals().items() if k in ("sig", "f0", "f1", "f2", "pct", "per", "rng", "math", "S", "X", "era", "P", "sc", "cells")}
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
