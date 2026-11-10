"""Lane 262 (PW-1612): how far the settlement ledger's dates moved between two runs of the same world and seed (switch off, the
code before / after the ledger stopped reading the next frame). Read-only. argv: run_A run_B (A the baseline).
Prints, for the 12 largest peoples (run A's populations now): each one's first town cell (techspread.town_footprint) and first
writing (the run's calendar), A / B / B - A in years; then over all chief places and second peoples' places: the count founded,
the median founding date and the oldest, A / B."""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.lineages import techspread as TS


def load(d: Path):
    m = json.loads((d / "run.json").read_text())["meta"]
    fp = TS.town_footprint(d)
    first = {p: float(v[0][np.flatnonzero(v[1] > 0)[0]]) for p, v in fp.items() if p != "_cell_km2" and (v[1] > 0).any()}
    S = json.loads((d / m["settlements"]["file"]).read_text())
    founded = [float(s["founded_kyr"]) for s in S["sites"] if s["kind"] in TS.SETTLED_KINDS]
    return m, first, founded


def main(a: Path, b: Path):
    ma, fa, sa = load(a)
    mb, fb, sb = load(b)
    pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in ma["lineages"]}
    top = sorted([p for p in ma["techtree"]["known"] if p in pops], key=lambda p: -pops[p])[:12]
    ka, kb = ma["techtree"]["known"], mb["techtree"]["known"]
    yr = lambda x: "-" if x is None else f"{x * 1000:,.0f}"  # noqa: E731
    dif = lambda x, y: "-" if x is None or y is None else f"{(x - y) * 1000:+,.0f}"  # noqa: E731 (A - B: positive = B later)
    print(f"=== {a.name} (A) / {b.name} (B): years ago; A-B > 0 means B is later")
    print(f"{'people':14s} {'first town A / B':>18s} {'A-B':>6s} | {'writing A / B':>16s} {'A-B':>6s}")
    for p in top:
        wa = ((ka.get(p) or {}).get("writing") or [None])[0]
        wb = ((kb.get(p) or {}).get("writing") or [None])[0]
        print(f"{p:14s} {yr(fa.get(p)):>8s} / {yr(fb.get(p)):>7s} {dif(fa.get(p), fb.get(p)):>6s} | {yr(wa):>7s} / {yr(wb):>6s} {dif(wa, wb):>6s}")
    for name, s in (("A", sa), ("B", sb)):
        print(f"  sites {name}: {len(s):,} founded; median founding {st.median(s) * 1000:,.0f} ya, oldest {max(s) * 1000:,.0f} ya")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
