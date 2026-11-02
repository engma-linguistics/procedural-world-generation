"""python pw252_ab.py LEVEL DIR : mean (min..max) per stage and for the ported functions, A (base) vs B (new), from the
interleaved timed runs DIR/t{LEVEL}_{A,B}_{i}.json that run_sim.py wrote (part 2 of docs/review/speed/pw252.md)."""
import glob, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gpu", "scripts"))
from stages import load, stage_of

level, d = sys.argv[1], sys.argv[2]
FUNCS = ["climate._erf", "climate.months", "climate.koppen", "vegetation.site", "isostasy.sediment_lift",
         "isostasy.elevation", "geo.is_land", "climate.face_winds", "climate.open_water_evap", "ocean.ice_growth",
         "tectonics.motion.forces", "tectonics.mantle.gradient"]
out = {}
for v in "AB":
    runs = []
    for fn in sorted(glob.glob(f"{d}/t{level}_{v}_*.json")):
        dd, rows, excl = load(fn)
        st, fx, pyside = defaultdict(float), defaultdict(float), 0.0
        for p, e in excl.items():
            if "CheckpointWriter.submit" in p[-1] or p == ("timeline.simulate",):
                continue
            st[stage_of(p)] += e
            if not p[-1].startswith("K:"):
                fx[p[-1]] += e
                pyside += e
        runs.append((dd["wall"], dd.get("load_before", [0])[0], st, fx, pyside))
    out[v] = runs


def fmt(xs):
    return f"{sum(xs) / len(xs):7.2f} ({min(xs):.1f}..{max(xs):.1f})"


print(f"L{level}: runs A {len(out['A'])} B {len(out['B'])}; load at start A {[round(r[1]) for r in out['A']]} B {[round(r[1]) for r in out['B']]}")
print("wall           A", fmt([r[0] for r in out["A"]]), " B", fmt([r[0] for r in out["B"]]))
print("python-side    A", fmt([r[4] for r in out["A"]]), " B", fmt([r[4] for r in out["B"]]))
for k in sorted({k for v in "AB" for r in out[v] for k in r[2]}):
    print(f"{k:34s}A", fmt([r[2].get(k, 0) for r in out["A"]]), " B", fmt([r[2].get(k, 0) for r in out["B"]]))
print("-- exclusive python-side seconds of the ported functions")
for f in FUNCS:
    print(f"{f:34s}A", fmt([r[3].get(f, 0) for r in out["A"]]), " B", fmt([r[3].get(f, 0) for r in out["B"]]))
