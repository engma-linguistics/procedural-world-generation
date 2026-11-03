"""PW-1407 (lane 149): den peoples keep their raiding share between ladder refreshes; main against the branch on the same robust-suite runs.

    uv run python docs/review/peoples/den-raids/compare.py MAIN_DIR BRANCH_DIR

Each DIR holds the per-run JSON of `tools/peoples_robust.py run --family base --trees dnd --seeds 7,10,13 --arms now` (both worlds).
Per run and den people (goblin, kobold, troglodyte): its people, its range (area_mkm2, the cells it holds), the people it has on the
raider rung (peoples[x].ways.raider[0]), main -> branch; then the totals over all six runs and the suite's invariants.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DEN = ("goblin", "kobold", "troglodyte")
MONO_MAX = 0.85


def load(d: Path) -> dict:
    return {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json")) if not p.name.endswith(".spec.json") and p.name != "summary.json"}


def rel(a: float, b: float) -> str:
    return f"{b / a - 1:+.1%}" if a else ("0" if not b else "new")


def main(a: str, b: str):
    A, B = load(Path(a)), load(Path(b))
    tot = {p: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] for p in DEN}  # pop, area, raider pop: main then branch
    print("| run | people | main pop -> branch pop | range Mkm2 | people on the raider rung |")
    print("|---|---|---|---|---|")
    for k in sorted(B):
        for p in DEN:
            x, y = A[k]["peoples"].get(p), B[k]["peoples"].get(p)
            if not x or not y:
                continue
            rx, ry = x.get("ways", {}).get("raider", [0])[0], y.get("ways", {}).get("raider", [0])[0]
            print(f"| {k} | {p} | {x['pop']:.3g} -> {y['pop']:.3g} ({rel(x['pop'], y['pop'])}) | {x['area_mkm2']:.2f} -> {y['area_mkm2']:.2f} "
                  f"({rel(x['area_mkm2'], y['area_mkm2'])}) | {rx:.3g} -> {ry:.3g} ({rel(rx, ry)}) |")
            for i, v in enumerate((x["pop"], y["pop"], x["area_mkm2"], y["area_mkm2"], rx, ry)):
                tot[p][i] += v
    print("\nTotals over the six runs (main -> branch):\n")
    print("| people | people | range Mkm2 | people on the raider rung |")
    print("|---|---|---|---|")
    for p, t in tot.items():
        print(f"| {p} | {t[0]:.4g} -> {t[1]:.4g} ({rel(t[0], t[1])}) | {t[2]:.1f} -> {t[3]:.1f} ({rel(t[2], t[3])}) | {t[4]:.4g} -> {t[5]:.4g} ({rel(t[4], t[5])}) |")
    print("\nAll people and the top people per run (main -> branch):\n")
    for k in sorted(B):
        fa, fb = A[k]["total_pop"], B[k]["total_pop"]
        sa = max(o["share"] for o in A[k]["peoples"].values() if o.get("alive"))
        sb = max(o["share"] for o in B[k]["peoples"].values() if o.get("alive"))
        ex = [n for n in ("lost",) if A[k].get(n) or B[k].get(n)]
        print(f"- {k}: all people {fa:.4g} -> {fb:.4g} ({rel(fa, fb)}); top share {sa:.1%} -> {sb:.1%}; "
              f"crash {not A[k].get('ok', True)} -> {not B[k].get('ok', True)}; lost {A[k]['lost']} -> {B[k]['lost']}; "
              f"over {MONO_MAX:.0%}: {sa > MONO_MAX} -> {sb > MONO_MAX}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
