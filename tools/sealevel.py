"""Sea-level diagnostics (PW-053): how far and how fast the sea moves, and why.

    PYTHONPATH=. uv run python tools/sealevel.py --seed 1 2 [--myr 1000] [--level 6] [--out DIR] [--set k=v ...]
    PYTHONPATH=. uv run python tools/sealevel.py --run <run id> [...]     (a stored run's keyframes)
    PYTHONPATH=. uv run python tools/sealevel.py --summary DIR/seed1.json [...]

A simulation records every step: land and crust %, sea level and its parts
(sea_ice from land ice, sea_tect from the ocean basins), the mean ocean depth
and its slow baseline (earth.global_temperature), the mean ocean-floor age,
the share of young (< 10 Myr) and capped-old floor, the ocean's share of the
surface, the number of plates, and the step's events. Writes DIR/seed<N>.json.

Summary, on 4 Myr samples after --skip Myr (default 0): sea level mean, sd,
min, max; steps at the +-250 m clamp of sea_tect; the largest change of sea
level within 20 Myr; and 'land drops': episodes where land falls by 4 or more
points of the surface within 20 Myr (consecutive flagged samples count once).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402
from planet.tectonics.isostasy import ocean_depth  # noqa: E402

CLAMP = 250.0


def sample(sim) -> dict:
    ocean = ~sim.w_cont
    age = sim.w_age[ocean]
    return {
        "t": sim.t,
        "land": round(100 * float((sim.w_elev > 0).mean()), 2),
        "cont": round(100 * float(sim.w_cont.mean()), 2),
        "sl": round(float(sim.sea_level), 1),
        "ice": round(float(sim.sea_ice), 1),
        "tect": round(float(sim.sea_tect), 1),
        "depth": round(float(ocean_depth(age).mean()), 1) if age.size else 0.0,
        "depth_ref": round(float(sim.depth_ref), 1) if sim.depth_ref is not None else 0.0,
        "age": round(float(age.mean()), 1) if age.size else 0.0,
        "young": round(100 * float((age < 10).mean()), 2) if age.size else 0.0,
        "old": round(100 * float((age > 117).mean()), 2) if age.size else 0.0,
        "ocean": round(100 * float(ocean.mean()), 2),
        "plates": int(sim.plates.alive.sum()),
    }


def run(seed, myr, level, sets) -> dict:
    sim = Simulation(build_grid(level), seed, Params(**sets), 2.0)
    track, evs, seen = [sample(sim)], [], 0
    t0 = time.time()

    def on_step(s):
        nonlocal seen
        for e in s.events[seen:]:
            if e.kind in ("rift", "subduction", "suture"):
                evs.append({"t": e.t, "kind": e.kind, "text": e.text})
        seen = len(s.events)
        track.append(sample(s))

    sim.run(myr, on_step)
    return {"seed": seed, "myr": myr, "level": level, "params": sets, "seconds": round(time.time() - t0),
            "track": track, "events": evs}


def from_run(run_id: str) -> dict:
    d = json.loads((ROOT / "runs" / run_id / "run.json").read_text())
    tr = [{"t": f["t"], "land": f["stats"]["land_pct"], "sl": f["stats"]["sea_level_m"],
           "plates": f["stats"]["plates"]} for f in d["frames"]]
    return {"seed": d["meta"].get("seed"), "run": run_id, "level": d["meta"].get("level"), "track": tr, "events": []}


def stats(d, skip: float = 0.0, every: float = 4.0, window: float = 20.0, drop: float = 4.0) -> dict:
    tr = [r for r in d["track"] if r["t"] >= skip - 1e-9 and abs(r["t"] / every - round(r["t"] / every)) < 1e-6]
    t = np.array([r["t"] for r in tr])
    L = np.array([r["land"] for r in tr])
    s = np.array([r["sl"] for r in tr])
    k = int(round(window / every))
    flag = np.array([i + 1 < len(L) and L[i + 1:i + k + 1].min() <= L[i] - drop for i in range(len(L))])
    drops = int(flag[0]) + int((flag[1:] & ~flag[:-1]).sum()) if len(flag) else 0
    swing = max((np.abs(s[i + 1:i + k + 1] - s[i]).max() for i in range(len(s) - 1)), default=0.0)
    out = {"n": len(tr), "sl_mean": round(float(s.mean())), "sl_sd": round(float(s.std())),
           "sl_min": round(float(s.min())), "sl_max": round(float(s.max())),
           "swing20": round(float(swing)), "land_drops": drops,
           "drop_times": [float(x) for x in t[flag & np.concatenate([[True], ~flag[:-1]])]],
           "land_min": float(L.min()), "land_max": float(L.max())}
    if "tect" in tr[0]:
        te = np.array([r["tect"] for r in tr])
        out["clamp"] = int((np.abs(te) >= CLAMP - 0.5).sum())
        out["tect_sd"] = round(float(te.std()))
        out["ice_mean"] = round(float(np.mean([r["ice"] for r in tr])))
        out["ice_min"] = round(float(np.min([r["ice"] for r in tr])))
        ages = np.array([r["age"] for r in tr])
        out["age_mean"], out["age_sd"] = round(float(ages.mean()), 1), round(float(ages.std()), 1)
    if "plates" in tr[0]:
        p = np.array([r["plates"] for r in tr])
        out["plates_median"], out["plates_min"] = float(np.median(p)), int(p.min())
    return out


def line(d, skip=0.0) -> str:
    st = stats(d, skip)
    name = f"run {d['run']}" if d.get("run") else f"seed {d['seed']}"
    extra = (f"; clamp {st['clamp']} samples, tect sd {st['tect_sd']}, ice mean {st['ice_mean']} (min {st['ice_min']}),"
             f" ocean age {st['age_mean']}+-{st['age_sd']}") if "clamp" in st else ""
    return (f"{name} L{d['level']} (>= {skip:g} Myr): sea level {st['sl_mean']}+-{st['sl_sd']} m"
            f" [{st['sl_min']}, {st['sl_max']}], 20-Myr swing max {st['swing20']} m, land {st['land_min']}-{st['land_max']}%,"
            f" 4-pt land drops {st['land_drops']} {st['drop_times']}{extra}; plates median {st.get('plates_median')}"
            f" min {st.get('plates_min')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, nargs="*", default=[])
    ap.add_argument("--myr", type=float, default=1000)
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--out", default="/tmp/sealevel")
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--run", nargs="*", default=[])
    ap.add_argument("--summary", nargs="*")
    ap.add_argument("--skip", type=float, default=0.0)
    a = ap.parse_args()
    if a.summary is not None:
        for p in a.summary:
            print(line(json.loads(Path(p).read_text()), a.skip))
        return
    for r in a.run:
        print(line(from_run(r), a.skip))
    sets = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        f = Params.__dataclass_fields__[k]
        sets[k] = v if f.type == "str" else (int(v) if f.type == "int" else float(v))
    out = Path(a.out)
    for s in a.seed:
        out.mkdir(parents=True, exist_ok=True)
        d = run(s, a.myr, a.level, sets)
        (out / f"seed{s}.json").write_text(json.dumps(d))
        print(line(d, a.skip), flush=True)


if __name__ == "__main__":
    main()
