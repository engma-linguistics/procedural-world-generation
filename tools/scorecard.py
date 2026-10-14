"""Slow calibration scores, tracked over time (not pass/fail).

    uv run python tools/scorecard.py [--myr 1000] [--seeds 1 2]

Runs (1) the climate on real Earth geography (needs data/earth, see
earth_check.py) and (2) level-6 simulations for --myr, then appends one JSON
line to docs/scorecard.jsonl tagged with the git commit, so you can see
whether model changes moved things toward or away from Earth. ~2-4 min.
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

from planet import climate  # noqa: E402
from planet.grid import build_grid  # noqa: E402
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
    c = climate.compute(g, elev, 0.0, 23.4, ice)
    land = (elev > 0) & (g.lat > -60) & (obs >= 0) & (obs != climate.SEA_CLASS)
    og = np.array([climate.KOPPEN[int(k)][1][0] if 0 <= k < len(climate.KOPPEN) else "?" for k in obs])
    mg = GROUP[c["koppen"]]
    shares = {k: round(100 * float((mg[land] == k).mean()), 1) for k in "ABCDE"}
    p, po = c["precip"][land], e["obs_precip"][land]
    ok = np.isfinite(po) & (po > 0)
    return {"group_agree": round(100 * float((mg[land] == og[land]).mean()), 1),
            "exact_agree": round(100 * float((c["koppen"][land] == obs[land]).mean()), 1),
            "shares": shares,
            "land_rain_mean": round(float(p.mean())),
            "log_rain_corr": round(float(np.corrcoef(np.log(p[ok] + 10), np.log(po[ok] + 10))[0, 1]), 3)}


def world_scores(seed: int, myr: float) -> dict:
    sim = Simulation(build_grid(6), seed, Params(), 2.0)
    v0 = float((sim.w_thick * sim.w_cont).sum())
    track = []
    while sim.t < myr - 1e-9:
        sim.run(min(myr, sim.t + 100))
        land = sim.w_elev > 0
        st = sim.stats()
        track.append({"t": sim.t, "land": st["land_pct"], "cont": st["continental_pct"],
                      "largest": st["largest_landmass_pct"], "masses": st["landmasses"],
                      "dry": round(100 * float((GROUP[sim.snapshot().koppen[land]] == "B").mean()), 1),
                      "ice": st["ice_pct"], "speed": st["mean_speed_cmyr"]})
    last = track[-1]
    return {"seed": seed, "myr": myr, "final": last,
            "volume_ratio": round(float((sim.w_thick * sim.w_cont).sum()) / v0, 3),
            "land_min": min(r["land"] for r in track), "land_max": max(r["land"] for r in track),
            "largest_max": max(r["largest"] for r in track),
            "ocean_age": round(float(sim.w_age[~sim.w_cont].mean()), 1), "track": track}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--myr", type=float, default=1000)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    a = ap.parse_args()
    t0 = time.time()
    code = code_version()
    rec = {"commit": f"{code['commit']}{'+dirty' if code['dirty'] else ''}", "src": code["planet_src_sha"],
           "date": time.strftime("%Y-%m-%d %H:%M"),
           "earth": earth_scores(), "worlds": [world_scores(s, a.myr) for s in a.seeds]}
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
              f"largest landmass max {w['largest_max']}%, ocean age {w['ocean_age']} Myr")
    print(f"appended to {out.relative_to(ROOT)}  [{rec['seconds']}s]")


if __name__ == "__main__":
    main()
