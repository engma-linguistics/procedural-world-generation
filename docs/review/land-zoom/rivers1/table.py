"""The river seam table (rivers-<pair>-before/after.json from rivers.py) and the owner line's height stations
(seam-<pair>-rivers.json from seams.py --owner): table.py DIR"""
import json
import sys
from pathlib import Path

D = Path(sys.argv[1])
PAIRS = ("desert", "range", "coast", "blockW", "tile")


def f(x, n=2):
    return "-" if x is None else f"{x:.{n}f}"


print("| pair | direction | build | crossings | carried on (x2) | within 25% | median abs log2 | big >= 500: n, within 25% "
      "| course offset km | total m3/s up -> down |")
print("|---|---|---|---|---|---|---|---|---|---|")
for p in PAIRS:
    for d, lab in (("A_to_B", "A->B"), ("B_to_A", "B->A")):
        for b in ("before", "after"):
            r = json.loads((D / f"rivers-{p}-{b}.json").read_text())[d]
            print(f"| {p} | {lab} | {b} | {r['n']} | {r['continued']} | "
                  f"{f(100 * r['within25'], 0) if r['within25'] is not None else '-'}% | {f(r['log2_median'])} | "
                  f"{r['n_big']}, {f(100 * r['big_within25'], 0) if r['big_within25'] is not None else '-'}% | "
                  f"{f(r['offset_km_median'], 1)} | {r['q_up_total']:,.0f} -> {r['q_down_total']:,.0f} |")
print()
print("| pair | build | line pixels | A lake | B lake | A lake / B land | A land / B lake |")
print("|---|---|---|---|---|---|---|")
for p in PAIRS:
    for b in ("before", "after"):
        r = json.loads((D / f"rivers-{p}-{b}.json").read_text())["lakes"]
        print(f"| {p} | {b} | {r['n']} | {r['lake_A']} | {r['lake_B']} | {r['A_lake_B_land']} | {r['A_land_B_lake']} |")
print()
print("| pair | station | median dh m (p95) | coast % | biome % |")
print("|---|---|---|---|---|")
for p in PAIRS:
    q = D / f"seam-{p}-rivers.json"
    if not q.exists():
        continue
    st = json.loads(q.read_text())["owner_line"]["stations"]
    for name, s in st.items():
        print(f"| {p} | {name} | {f(s['dh_median_abs'], 1)} ({f(s['dh_p95_abs'], 1)}) | "
              f"{f(100 * s['coast_mismatch_share'] if s['coast_mismatch_share'] is not None else None)} | "
              f"{f(100 * s['biome_mismatch_share'] if s['biome_mismatch_share'] is not None else None, 1)} |")
