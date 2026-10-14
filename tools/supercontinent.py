"""Supercontinent-cycle diagnostics: does a world gather its continents
together and break them up again? (docs/proposals/supercontinent_cycle.md)

    uv run python tools/supercontinent.py --seed 1 [--myr 2000] [--level 6] [--out DIR] [--set k=v ...]
    uv run --with matplotlib python tools/supercontinent.py --plot DIR/seed1.json [...]

Every --every Myr it records: the largest landmass (% of the surface, land =
above sea level), the largest connected continental-crust mass, the number of
landmasses bigger than 0.5% of the surface, land and crust %, mean plate
speed, ocean-floor age, the mean mantle temperature anomaly under the largest
continent (if the model has a mantle field), and every rift with its cause and
the continental area of its two pieces. Writes DIR/seed<N>.json; --plot draws
the time series (one PNG per JSON, next to it).

Assemblies: spells where the largest landmass is above --assembled (25%) of the
surface; their start times and spacing are printed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402
from planet.tectonics.plates import CMYR  # noqa: E402


def rift_cause(e, mantle: bool) -> str:
    """margin (new subduction), or for rifts: without a mantle field the old
    rules heat / stress; with it, a continental rift over warm / cold /
    neutral mantle (cont-warm, cont-cold, cont) or an oceanic plate split
    (plate)."""
    if e.kind == "subduction":
        return "margin"
    if not mantle:
        return "heat" if "rifts apart" in e.text else "stress"
    kind = "cont" if e.text.startswith("continent") else "plate"
    if "warm mantle" in e.text:
        return kind + "-warm"
    if "cold mantle" in e.text:
        return kind + "-cold"
    return kind


def sample(sim, v0) -> dict:
    g = sim.grid
    land = sim.w_elev > 0
    lab, nl = g.components(land)
    sizes = np.bincount(lab[lab >= 0]) if nl else np.zeros(1, int)
    clab, ncl = g.components(sim.w_cont)
    csizes = np.bincount(clab[clab >= 0]) if ncl else np.zeros(1, int)
    big = clab == int(csizes.argmax()) if ncl else np.zeros(g.n, bool)
    v = np.linalg.norm(sim.velocity(), axis=1) * CMYR
    rec = {
        "t": sim.t,
        "largest": round(100 * sizes.max() / g.n, 2),
        "largest_cont": round(100 * csizes.max() / g.n, 2),
        "masses": int((sizes > 0.005 * g.n).sum()),
        "land": round(100 * land.mean(), 2),
        "cont": round(100 * sim.w_cont.mean(), 2),
        "speed": round(float(v.mean()), 2),
        "ocean_age": round(float(sim.w_age[~sim.w_cont].mean()), 1),
        "plates": int(sim.plates.alive.sum()),
        "volume": round(float((sim.w_thick * sim.w_cont).sum()) / v0, 4),
        "max_elev": int(sim.w_elev.max()),
        "cover_max": round(float(sim.w_cover.max()), 2),
        "cover_cap": int((sim.w_cover >= sim.params.metamorphic_depth - 0.01).sum()),
        "elev_p99": int(np.percentile(sim.w_elev[land], 99)) if land.any() else 0,
    }
    m = getattr(sim, "mantle", None)
    if m is not None:
        rec["mantle_under"] = round(float(m[big].mean()), 3) if big.any() else 0.0
        rec["mantle_cont"] = round(float(m[sim.w_cont].mean()), 3)
        rec["mantle_min"] = round(float(m.min()), 3)
        rec["mantle_max"] = round(float(m.max()), 3)
    return rec


def run(seed, myr, level, every, sets) -> dict:
    p = Params(**sets)
    sim = Simulation(build_grid(level), seed, p, 2.0)
    v0 = float((sim.w_thick * sim.w_cont).sum())
    track, rifts, seen = [], [], 0
    has_mantle = hasattr(sim, "mantle")
    t0 = time.time()

    def on_step(s):
        nonlocal seen
        for e in s.events[seen:]:
            if e.kind in ("rift", "subduction", "suture"):
                slots = {int(s.plates.label[k]): k for k in np.flatnonzero(s.plates.alive)}
                pieces = []
                for lb in e.plates:
                    k = slots.get(lb)
                    pieces.append(round(100 * float((s.w_cont & (s.owner == k)).mean()), 2) if k is not None else 0)
                rifts.append({"t": e.t, "kind": e.kind, "cause": rift_cause(e, has_mantle) if e.kind != "suture" else "suture",
                              "pieces": pieces})
        seen = len(s.events)
        if abs(s.t / every - round(s.t / every)) < 1e-6:
            track.append(sample(s, v0))

    track.append(sample(sim, v0))
    sim.run(myr, on_step)
    return {"seed": seed, "myr": myr, "level": level, "params": sets, "seconds": round(time.time() - t0),
            "track": track, "events": rifts}


def assemblies(track, thr=25.0, gap=100.0):
    """(start, end, peak) of spells with largest landmass >= thr; spells less
    than `gap` Myr apart count as one."""
    out = []
    for r in track:
        if r["largest"] >= thr:
            if out and r["t"] - out[-1][1] <= gap:
                out[-1][1] = r["t"]
                out[-1][2] = max(out[-1][2], r["largest"])
            else:
                out.append([r["t"], r["t"], r["largest"]])
    return out


def summary(d, thr=25.0) -> str:
    tr = d["track"]
    late = [r for r in tr if r["t"] >= 200] or tr
    asm = assemblies(tr, thr)
    starts = [a[0] for a in asm]
    gaps = np.diff(starts).tolist() if len(starts) > 1 else []
    masses = [r["masses"] for r in late]
    between = [r["masses"] for r in late if r["largest"] < 20] or [0]
    rifts = [e for e in d["events"] if e["kind"] != "suture"]
    causes = {}
    for e in rifts:
        causes[e["cause"]] = causes.get(e["cause"], 0) + 1
    small = sum(1 for e in rifts if e["kind"] == "rift" and any(0.3 < x < 3.0 for x in e["pieces"]))
    last = tr[-1]
    return (f"seed {d['seed']} ({d['seconds']}s): assemblies>{thr:g}% at {[f'{a:g}-{b:g} ({c:.0f}%)' for a, b, c in asm]}"
            f" gaps {gaps}; largest max {max(r['largest'] for r in tr):.1f}% median {np.median([r['largest'] for r in late]):.1f}%;"
            f" masses>0.5% median {np.median(masses):.0f} (range {min(masses)}-{max(masses)}; dispersed, largest<20%: {np.median(between):.0f});"
            f" land {min(r['land'] for r in late):.1f}-{max(r['land'] for r in late):.1f}% (median {np.median([r['land'] for r in late]):.1f});"
            f" volume x{last['volume']}; ocean age median {np.median([r['ocean_age'] for r in late]):.0f};"
            f" speed median {np.median([r['speed'] for r in late]):.2f}; rifts {causes}"
            f" (continental pieces <3%: {small}); sutures {sum(1 for e in d['events'] if e['kind'] == 'suture')}")


def plot(path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = json.loads(path.read_text())
    tr = d["track"]
    t = np.array([r["t"] for r in tr])
    has_m = "mantle_under" in tr[0]
    fig, ax = plt.subplots(4 if has_m else 3, 1, figsize=(10, 11 if has_m else 8.5), sharex=True)
    a = ax[0]
    a.plot(t, [r["largest"] for r in tr], color="#1f6f8b", label="largest landmass (% surface)")
    a.plot(t, [r["largest_cont"] for r in tr], color="#99c1b9", lw=1, label="largest continental-crust mass")
    a.axhline(25, color="#c44", lw=0.8, ls="--")
    a.set_ylabel("% of surface")
    a.legend(loc="upper right", fontsize=8)
    a.set_title(f"seed {d['seed']}, level {d['level']}  {d.get('params') or ''}")
    a = ax[1]
    a.plot(t, [r["masses"] for r in tr], color="#444", label="landmasses > 0.5%")
    a.axhspan(5, 15, color="#9c9", alpha=0.2)
    a.set_ylabel("count")
    a.legend(loc="upper right", fontsize=8)
    a = ax[2]
    a.plot(t, [r["land"] for r in tr], label="land %")
    a.plot(t, [r["speed"] * 5 for r in tr], label="mean speed x5 (cm/yr)")
    a.plot(t, [r["ocean_age"] / 2 for r in tr], label="ocean age / 2 (Myr)")
    a.plot(t, [r["plates"] for r in tr], label="plates")
    colors = {"heat": "#d62728", "stress": "#ff7f0e", "margin": "#2ca02c", "suture": "#8c564b",
              "cont-warm": "#d62728", "cont": "#ff7f0e", "cont-cold": "#1f77b4", "plate": "#7f7f7f",
              "plate-warm": "#7f7f7f", "plate-cold": "#7f7f7f"}
    for e in d["events"]:
        a.axvline(e["t"], ymin=0.93 if e["kind"] == "suture" else 0.0, ymax=1.0 if e["kind"] == "suture" else 0.07,
                  color=colors.get(e["cause"], "k"), lw=1)
    a.legend(loc="upper right", fontsize=8, ncol=2)
    a.set_ylabel("rifts (bottom ticks) / sutures (top)")
    if has_m:
        a = ax[3]
        a.plot(t, [r["mantle_under"] for r in tr], color="#b22", label="mantle under largest continent")
        a.plot(t, [r["mantle_cont"] for r in tr], color="#e88", lw=1, label="mantle under all continent")
        a.fill_between(t, [r["mantle_min"] for r in tr], [r["mantle_max"] for r in tr], color="#ccc", alpha=0.4,
                       label="mantle min..max")
        a.axhline(0, color="k", lw=0.5)
        a.set_ylabel("mantle T anomaly")
        a.legend(loc="upper right", fontsize=8)
    ax[-1].set_xlabel("Myr")
    fig.tight_layout()
    out = path.with_suffix(".png")
    fig.savefig(out, dpi=90)
    print(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, nargs="*", default=[1])
    ap.add_argument("--myr", type=float, default=2000)
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--every", type=float, default=10)
    ap.add_argument("--out", default="/tmp/supercontinent")
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--plot", nargs="*")
    ap.add_argument("--summary", nargs="*")
    a = ap.parse_args()
    if a.plot is not None:
        for p in a.plot:
            plot(Path(p))
        return
    if a.summary is not None:
        for p in a.summary:
            print(summary(json.loads(Path(p).read_text())))
        return
    sets = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        f = Params.__dataclass_fields__[k]
        sets[k] = f.type == "str" and v or (int(v) if f.type == "int" else float(v))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for s in a.seed:
        d = run(s, a.myr, a.level, a.every, sets)
        path = out / f"seed{s}.json"
        path.write_text(json.dumps(d))
        print(summary(d), flush=True)


if __name__ == "__main__":
    main()
