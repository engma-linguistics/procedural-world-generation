"""Slow calibration scores, tracked over time (not pass/fail).

    uv run python tools/scorecard.py [--myr 1000] [--seeds 1 2] [--jobs J]

Runs (1) the climate on real Earth geography (needs data/earth, see
earth_check.py) and (2) level-6 simulations for --myr, then appends one JSON
line to docs/scorecard.jsonl tagged with the git commit, so you can see
whether model changes moved things toward or away from Earth. The Earth
climate and each seed run at once in worker processes (planet/parallel.py;
--jobs 1: one after the other), so it takes about as long as one seed
(the `seconds` field of each line).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import planet  # noqa: E402,F401  (first: its thread caps must precede numpy, planet/parallel.py)
import numpy as np  # noqa: E402
from planet import climate, parallel, vegetation  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools.earth_data import koppen_agreement  # noqa: E402
from planet.provenance import code_version  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

GROUP = np.array([k[1][0] for k in climate.KOPPEN])


def earth_scores() -> dict | None:
    path = ROOT / "data" / "earth" / "L6.npz"
    if not path.exists():
        return None
    e = np.load(path)
    g = build_grid(6)
    elev, ice, obs = e["elev"].astype(float), e["ice"].astype(float), e["obs_koppen"]
    c, _ = vegetation.coupled_climate(g, elev, 0.0, 23.4, ice)
    land = (elev > 0) & (g.lat > -60) & (obs >= 0) & (obs != climate.SEA_CLASS)
    mg = GROUP[c["koppen"]]
    shares = {k: round(100 * float((mg[land] == k).mean()), 1) for k in "ABCDE"}
    p, po = c["precip"][land], e["obs_precip"][land]
    ok = np.isfinite(po) & (po > 0)
    ka = koppen_agreement(g, c["koppen"], obs, elev)  # area-weighted, the one Earth Koppen score
    return {"group_agree": round(ka["group"], 1), "exact_agree": round(ka["exact"], 1),
            "shares": shares,
            "land_rain_mean": round(float(p.mean())),
            "log_rain_corr": round(float(np.corrcoef(np.log(p[ok] + 10), np.log(po[ok] + 10))[0, 1]), 3)}


def world_scores(seed: int, myr: float) -> dict:
    sim = Simulation(build_grid(6), seed, Params(flora_end=myr), 2.0)  # (plant groups scaled as simulate does)
    v0 = float((sim.w_thick * sim.w_cont).sum())
    track = []
    while sim.t < myr - 1e-9:
        sim.run(min(myr, sim.t + 100))
        land = sim.w_elev > 0
        st = sim.stats()
        track.append({"t": sim.t, "land": st["land_pct"], "cont": st["continental_pct"],
                      "largest": st["largest_landmass_pct"], "masses": st["landmasses"],
                      "dry": round(100 * float((GROUP[sim.snapshot().koppen[land]] == "B").mean()), 1),
                      "ice": st["ice_pct"], "speed": st["mean_speed_cmyr"],
                      "npp": round(float(sim.npp[land].mean())), "trees": round(100 * float(sim.tree_cover[land].mean()), 1)})
    last = track[-1]
    return {"seed": seed, "myr": myr, "final": last,
            "volume_ratio": round(float((sim.w_thick * sim.w_cont).sum()) / v0, 3),
            "land_min": min(r["land"] for r in track), "land_max": max(r["land"] for r in track),
            "largest_max": max(r["largest"] for r in track),
            "ocean_age": round(float(sim.w_age[~sim.w_cont].mean()), 1),
            "plant_groups": [None if not np.isfinite(t) else t for t in sim.flora], "track": track}


def _job(job: tuple, progress) -> dict | None:
    """One scorecard part, in a worker process: ("earth",) or ("world", seed, myr)."""
    return earth_scores() if job[0] == "earth" else world_scores(*job[1:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--myr", type=float, default=1000)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--jobs", type=int, help="parts run at once (default: all of them, up to a quarter of the cores)")
    ap.add_argument("--threads", type=int, help="numba threads per worker (default: the cores shared out, at most 8)")
    a = ap.parse_args()
    t0 = time.time()
    code = code_version()
    jobs = [("earth",)] + [("world", s, a.myr) for s in a.seeds]
    earth, *worlds = parallel.run(_job, jobs, a.jobs, a.threads)
    rec = {"commit": f"{code['commit']}{'+dirty' if code['dirty'] else ''}", "src": code["planet_src_sha"],
           "date": time.strftime("%Y-%m-%d %H:%M"), "earth": earth, "worlds": worlds}
    rec["seconds"] = round(time.time() - t0)
    out = ROOT / "docs" / "scorecard.jsonl"
    out.parent.mkdir(exist_ok=True)
    with open(out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    e = rec["earth"]
    if e:
        print(f"Earth: group agreement {e['group_agree']}% (exact {e['exact_agree']}%), shares {e['shares']}, "
              f"log-rain corr {e['log_rain_corr']}")
    for w in rec["worlds"]:
        f = w["final"]
        print(f"seed {w['seed']} @ {w['myr']:g} Myr: land {f['land']}% (range {w['land_min']}-{w['land_max']}), "
              f"crust {f['cont']}%, volume x{w['volume_ratio']}, dry {f['dry']}%, ice {f['ice']}%, "
              f"largest landmass max {w['largest_max']}%, ocean age {w['ocean_age']} Myr, "
              f"land NPP {f['npp']} g C/m2/yr, tree cover {f['trees']}%, plant groups at {w['plant_groups']} Myr")
    print(f"appended to {out.relative_to(ROOT)}  [{rec['seconds']}s]")


if __name__ == "__main__":
    main()
