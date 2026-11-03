"""PW-1386 (lane 146): forager trade, main against the branch on the same robust-suite runs.

    uv run python docs/review/peoples/forager-trade/compare.py MAIN_DIR BRANCH_DIR

Each DIR holds the per-run JSON of `tools/peoples_robust.py run --family base --trees dnd --seeds 7,10,13 --arms now` (both worlds).
Per run: all people, the forager peoples' people (ladder.barters: no crops, not den peoples or holds) and the share of their food
that is traded farm food (forage_land traded_pop / forager_pop), people on a wild rung, and the suite's invariants per run (crash,
extinct, a people over 85%). The baseline (main) has no trade, so its traded share is 0 by construction.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MONO_MAX = 0.85


def load(d: Path) -> dict:
    out = {}
    for p in sorted(d.glob("*.json")):
        if p.name.endswith(".spec.json") or p.name == "summary.json":
            continue
        out[p.stem] = json.loads(p.read_text())
    return out


def row(m: dict) -> dict:
    if "error" in m or "forage_land" not in m:
        return {"crash": True}
    fl = m["forage_land"].get("peoples", {})
    pop = sum(o["pop"] for o in fl.values())
    fpop = sum(o.get("forager_pop", 0.0) for o in fl.values())
    tpop = sum(o.get("traded_pop", 0.0) for o in fl.values())
    wild = sum(o["wild_pop"] for o in fl.values())
    shares = {a: o["pop"] / pop for a, o in fl.items()} if pop else {}
    foragers = {a: o["forager_pop"] for a, o in fl.items() if o.get("forager_pop", 0) > 0}
    return {"crash": False, "pop": pop, "forager_pop": fpop, "traded": tpop / fpop if fpop else 0.0, "wild": wild,
            "top": max(shares.values()) if shares else 0.0, "foragers": foragers, "traded_by": {a: o.get("traded_pop", 0.0) / o["forager_pop"]
            for a, o in fl.items() if o.get("forager_pop", 0) > 0}, "extinct": m.get("extinct") or m.get("dead") or []}


def main(a: str, b: str):
    A, B = load(Path(a)), load(Path(b))
    print("| run | all people (main -> branch) | forager peoples' people | traded share of their food | people on a wild rung | top people's share |")
    print("|---|---|---|---|---|---|")
    for k in sorted(set(A) | set(B)):
        ra, rb = row(A.get(k, {"error": 1})), row(B.get(k, {"error": 1}))
        if ra["crash"] or rb["crash"]:
            print(f"| {k} | crash main={ra['crash']} branch={rb['crash']} |")
            continue
        f = lambda x: f"{x:.3g}"  # noqa: E731
        print(f"| {k} | {f(ra['pop'])} -> {f(rb['pop'])} ({rb['pop'] / ra['pop']:.3f}) | {f(ra['forager_pop'])} -> {f(rb['forager_pop'])} "
              f"({rb['forager_pop'] / max(ra['forager_pop'], 1):.2f}) | {ra['traded']:.1%} -> {rb['traded']:.1%} | {f(ra['wild'])} -> "
              f"{f(rb['wild'])} ({rb['wild'] / max(ra['wild'], 1):.2f}) | {ra['top']:.1%} -> {rb['top']:.1%} |")
    print()
    for k in sorted(B):
        rb = row(B[k])
        if not rb["crash"]:
            ra = row(A.get(k, {"error": 1}))
            fa = ra.get("foragers", {}) if not ra["crash"] else {}
            print(k, {p: (f"{fa.get(p, 0):.3g}", f"{x:.3g}", f"{rb['traded_by'][p]:.1%}") for p, x in sorted(rb["foragers"].items(), key=lambda t: -t[1])})


if __name__ == "__main__":
    main(*sys.argv[1:3])
