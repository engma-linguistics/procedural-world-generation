"""Lane 158: the frozen yardstick y = ln(src ref / sink ref) of lane 140's 36 main runs (from the step records:
ref = raw / relative), its spread within a seed (re-rolls of one planet) and between seeds, and late dT (600-1000)
against it. Also the late mean dT spread itself."""
import glob, gzip, json
from collections import defaultdict
import numpy as np
L = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l140/judge"
rows = []
for f in sorted(glob.glob(f"{L}/main_r*/seed*_L6.json.gz")):
    st = json.load(gzip.open(f))["steps"]
    x = [s for s in st if s["t"] > 400][0]
    y = np.log(x["source_raw"] / x["src"]) - np.log(x["sink_raw"] / x["sink"])
    late = np.mean([s["dT"] for s in st if 600 < s["t"] <= 1000])
    pk = max(s["iced_land_pct"] for s in st if 884 <= s["t"] <= 1000)
    rows.append((f.split("/")[-1].split("_")[0], f.split("/")[-2], y, late, pk))
by = defaultdict(list)
for s, d, y, late, pk in rows:
    by[s].append((y, late, pk))
Y = np.array([r[2] for r in rows]); T = np.array([r[3] for r in rows]); P = np.array([r[4] for r in rows])
within_y = np.sqrt(np.mean([np.var([v[0] for v in g], ddof=1) for g in by.values() if len(g) > 1]))
within_T = np.sqrt(np.mean([np.var([v[1] for v in g], ddof=1) for g in by.values() if len(g) > 1]))
within_P = np.sqrt(np.mean([np.var([v[2] for v in g], ddof=1) for g in by.values() if len(g) > 1]))
print(f"{len(rows)} runs, {len(by)} seeds ({[len(g) for g in by.values()]})")
print(f"y: mean {Y.mean():.3f}, sd all {Y.std(ddof=1):.3f}, within-seed sd {within_y:.3f}")
print(f"late dT (600-1000 mean): mean {T.mean():+.2f}, sd all {T.std(ddof=1):.2f}, within-seed sd {within_T:.2f}")
print(f"hard-window peak land ice: median {np.median(P):.1f}, sd all {P.std(ddof=1):.1f}, within-seed sd {within_P:.1f}, max {P.max():.1f}")
# within-seed slope of late dT and peak ice on y (deviations from each seed's mean)
dy, dT_, dP = [], [], []
for g in by.values():
    if len(g) > 1:
        a = np.array(g)
        dy += list(a[:, 0] - a[:, 0].mean()); dT_ += list(a[:, 1] - a[:, 1].mean()); dP += list(a[:, 2] - a[:, 2].mean())
dy, dT_, dP = map(np.array, (dy, dT_, dP))
bT, bP = np.polyfit(dy, dT_, 1)[0], np.polyfit(dy, dP, 1)[0]
r2 = np.corrcoef(dy, dT_)[0, 1] ** 2
print(f"within-seed: late dT {bT:+.1f} C per unit y (r2 {r2:.2f}), peak ice {bP:+.1f} pts per unit y")
print(f"  late dT sd left after y: {np.sqrt(np.mean((dT_ - bT * dy) ** 2) * len(dy) / (len(dy) - len(by))):.2f} C")
# Option A's forecast: the same runs with every planet's yardstick at the ensemble mean (late dT + slope (y - mean y))
C = T - bT * (Y - Y.mean())
wC = np.sqrt(np.mean([np.var([C[i] for i in range(len(rows)) if rows[i][0] == s], ddof=1) for s in by]))
print(f"fixed yardstick (forecast): late dT mean {C.mean():+.2f}, sd all {C.std(ddof=1):.2f}, within-seed sd {wC:.2f}, "
      f"range {C.min():+.2f}..{C.max():+.2f} (now {T.min():+.2f}..{T.max():+.2f})")
Pc = P - bP * (Y - Y.mean())
print(f"  peak ice (forecast): sd all {Pc.std(ddof=1):.1f}, max {Pc.max():.1f} (now sd {P.std(ddof=1):.1f}, max {P.max():.1f})")
