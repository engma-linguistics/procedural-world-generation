"""Alone vs matched at the owner line, from seams.py --owner jsons: table4.py DIR"""
import json
import sys
from pathlib import Path

D = Path(sys.argv[1])


def f(x, n=1):
    return "-" if x is None else f"{x:.{n}f}"


print("| pair | build | station | n land | median dh m | p95 dh m | median dslope | p95 dslope | coast % | biome % |")
print("|---|---|---|---|---|---|---|---|---|---|")
for name in ("desert", "range", "coast", "blockW", "tile"):
    for kind in ("alone", "matched"):
        p = D / f"seam-{name}-{kind}.json"
        if not p.exists():
            continue
        r = json.loads(p.read_text())["owner_line"]
        for st, s in r["stations"].items():
            print(f"| {name} | {kind} | {st} | {s['n_land']} | {f(s['dh_median_abs'])} | {f(s['dh_p95_abs'])} | "
                  f"{f(s['dslope_median_deg'], 2)} | {f(s['dslope_p95_deg'], 2)} | {f(100 * s['coast_mismatch_share'] if s['coast_mismatch_share'] is not None else None, 2)} | "
                  f"{f(100 * s['biome_mismatch_share'] if s['biome_mismatch_share'] is not None else None, 1)} |"
                  + (f" {s['coast_pairs']}" if "-v" in sys.argv and s.get("coast_mismatch_share") else ""))
print()
print("| pair | slope p95 ramp 0-80 (matched / alone) | slope p95 inside 120-400 (matched / alone) | B moved: " +
      " | ".join(["0-80", "80-160", "160-300", "300-600", "600-end"]) + " (median dh m, p95; coast changed %) |")
print("|---|---|---|---|---|---|---|---|")
for name in ("desert", "range", "coast", "blockW", "tile"):
    p = D / f"seam-{name}-matched.json"
    if not p.exists():
        continue
    r = json.loads(p.read_text())["owner_line"]
    mv = r.get("b_moved", {})
    cells = [f"{f(v['dh_median_abs'])} ({f(v['dh_p95_abs'])}; {f(100 * v['coast_changed_share'] if v['coast_changed_share'] is not None else None, 2)})"
             for v in mv.values()]
    print(f"| {name} | {f(r['slope_p95_ramp_0_80'], 2)} / {f(r.get('slope_p95_ramp_0_80_alone'), 2)} | "
          f"{f(r['slope_p95_inside_120_400'], 2)} / {f(r.get('slope_p95_inside_120_400_alone'), 2)} | " + " | ".join(cells) + " |")
