"""python stages.py prof.json [more.json ...]: stage shares (exclusive time attributed to the
innermost stage root on the call path), top kernels and top exclusive Python functions."""
import json, sys
from collections import defaultdict

ROOTS = {
    "tectonics.earth.ice_sheets": "ice", "icemass.balance": "ice",
    "tectonics.earth.update_vegetation": "vegetation",
    "ocean.solve": "ocean", "ocean.freshwater": "ocean",
    "tectonics.earth.update_climate": "climate (atmosphere)", "climate.compute": "climate (atmosphere)",
    "tectonics.earth.global_temperature": "climate (atmosphere)",
    "hydrology.lakes": "lakes / priority flood",
    "tectonics.earth.erode": "erosion / flow routing", "surface.erode": "erosion / flow routing",
    "hydrology.route": "erosion / flow routing",
    "tectonics.earth.sediments": "sediment, burial, reefs", "tectonics.earth.bury": "sediment, burial, reefs",
    "tectonics.earth.reefs": "sediment, burial, reefs",
    "tectonics.simulation.Simulation.step": "tectonics (plates, crust, events, mantle)",
    "tectonics.simulation.Simulation.snapshot": "output (snapshot, keyframes, checkpoints)",
    "timeline.jet_of": "output (snapshot, keyframes, checkpoints)",
    "timeline.frame_values": "output (snapshot, keyframes, checkpoints)",
    "store.encode": "output (snapshot, keyframes, checkpoints)",
    "store.save_checkpoint": "output (snapshot, keyframes, checkpoints)",
    "store.write_layers": "output (snapshot, keyframes, checkpoints)",
    "timeline.report": "output (snapshot, keyframes, checkpoints)",
    "tectonics.simulation.Simulation.__post_init__": "setup (grid, initial state)",
    "grid.build_grid": "setup (grid, initial state)",
}
PREFIX = {"tectonics.isostasy.": "isostasy"}


def stage_of(path):
    for lab in reversed(path):
        if lab in ROOTS:
            # build_grid inside the ocean's coarse grid is the ocean's work
            if lab == "grid.build_grid" and len(path) > 1 and "ocean._coarse" in path:
                continue
            return ROOTS[lab]
        for p, s in PREFIX.items():
            if lab.startswith(p):
                return s
    return "other / python glue"


def load(fn):
    d = json.load(open(fn))
    rows = {tuple(r["path"]): (r["s"], r["n"]) for r in d["rows"]}
    kids = defaultdict(float)
    for p, (s, n) in rows.items():
        if len(p) > 1:
            kids[p[:-1]] += s
    excl = {p: s - kids[p] for p, (s, n) in rows.items()}
    return d, rows, excl


if __name__ == '__main__':
  for fn in sys.argv[1:]:
        d, rows, excl = load(fn)
        wall = d["wall"]
        st = defaultdict(float)
        for p, e in excl.items():
            st[stage_of(p)] += e
        st["unwrapped (outside timers)"] = wall - sum(r[0] for p, r in rows.items() if len(p) == 1)
        print(f"\n== {fn}: wall {wall:.1f}s threads {d.get('threads')} load {d.get('load_before', [0])[0]:.0f}->"
              f"{d.get('load_after', [0])[0]:.0f}")
        for k, v in sorted(st.items(), key=lambda x: -x[1]):
            print(f"  {k:<45s} {v:8.2f}s {100 * v / wall:5.1f}%")
        kern = defaultdict(lambda: [0.0, 0])
        for p, (s, n) in rows.items():
            if p[-1].startswith("K:"):
                kern[p[-1]][0] += s
                kern[p[-1]][1] += n
        print("  -- top kernels (inclusive, all call sites)")
        for k, (s, n) in sorted(kern.items(), key=lambda x: -x[1][0])[:15]:
            print(f"  {k:<50s} {s:8.2f}s {100 * s / wall:5.1f}%  n={n}  {1000 * s / n:.2f} ms/call")
        pe = defaultdict(lambda: [0.0, 0])
        for p, e in excl.items():
            if not p[-1].startswith("K:"):
                pe[p[-1]][0] += e
                pe[p[-1]][1] += rows[p][1]
        print("  -- top exclusive python functions (numpy glue and unwrapped nested kernels)")
        for k, (s, n) in sorted(pe.items(), key=lambda x: -x[1][0])[:15]:
            print(f"  {k:<50s} {s:8.2f}s {100 * s / wall:5.1f}%  n={n}")
