"""Markdown table of every seam-*.json here (run seams.py first): python docs/review/land-zoom/table.py"""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
f = lambda v, n=1: "-" if v is None else f"{v:.{n}f}"  # noqa: E731
print("| seam | station | line km | median dh m | p95 dh m | bias m | median dslope deg | p95 dslope deg | coast breaks/100km | river breaks/100km (A/B crossings, unmatched A/B) | matched offset km (median/max) | landform mismatch % | biome mismatch % |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for p in sorted(here.glob("seam-*.json")):
    r = json.loads(p.read_text())
    for k, s in r["stations"].items():
        if "dh_median_abs" not in s:
            continue
        print(f"| {p.stem[5:]} (gap {r['centres_km_apart']:.0f} km, overlap {r['overlap_km']:.0f}) | {k} | {s['line_km']:.0f} | {f(s['dh_median_abs'])} | {f(s['dh_p95_abs'])} | {f(s['dh_bias'])} | {f(s['dslope_median_deg'],2)} | {f(s['dslope_p95_deg'],2)} | {f(s['coast_breaks_per_100km'],2)} | {f(s['river_breaks_per_100km'],2)} ({s['river_crossings_A']}/{s['river_crossings_B']}, {s['river_unmatched_A']}/{s['river_unmatched_B']}) | {f(s['river_offset_km_median'])}/{f(s['river_offset_km_max'])} | {f(100*s['landform_mismatch_share'] if s['landform_mismatch_share'] is not None else None)} | {f(100*s['biome_mismatch_share'] if s['biome_mismatch_share'] is not None else None)} |")
