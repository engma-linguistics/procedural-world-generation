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
from planet import climate, parallel  # noqa: E402
from planet.geo import is_land  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools import earth_data, moisture_budget  # noqa: E402
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
    c, rec = moisture_budget.capture(g, elev, ice)  # (the same climate, its rain kernel's inputs kept)
    land = is_land(elev, ice) & (g.lat > -60) & (obs >= 0) & (obs != climate.SEA_CLASS)
    mg = GROUP[c["koppen"]]
    shares = {k: round(100 * float((mg[land] == k).mean()), 1) for k in "ABCDE"}
    p, po = c["precip"][land], e["obs_precip"][land]
    ok = np.isfinite(po) & (po > 0)
    ka = koppen_agreement(g, c["koppen"], obs, elev, ice)  # area-weighted, the one Earth Koppen score
    return {"group_agree": round(ka["group"], 1), "exact_agree": round(ka["exact"], 1),
            "shares": shares,
            "land_rain_mean": round(float(p.mean())),
            "log_rain_corr": round(float(np.corrcoef(np.log(p[ok] + 10), np.log(po[ok] + 10))[0, 1]), 3),
            "moisture": moisture_budget.headlines(moisture_budget.analyse(g, earth_data.earth_on_grid(g), c, rec))}


LATE_FRACTION = 0.4  # the late window: the run's last 40% (600-1000 Myr of 1 Gyr)
LATE_STEP = 20.0  # Myr between samples inside it


def late_window(myr: float) -> tuple[float, list[float]]:
    """The late window's start and its sample times (every LATE_STEP Myr from its start to myr). PW-1684: high ground,
    ice and plant growth come and go in 50-100 Myr pulses, so the run's last moment alone can sit on a peak or a
    trough (lane 286, docs/review/tectonics/andes-late.md); medians over the window read the run's late state."""
    t0 = (1.0 - LATE_FRACTION) * myr
    n = int(np.floor((myr - t0) / LATE_STEP + 1e-9))
    return t0, sorted({round(myr - k * LATE_STEP, 9) for k in range(n + 1)})


def late_summary(samples: list[dict], t0: float) -> dict:
    """Median and mean of every numeric field over the samples at t >= t0 (the late window)."""
    a = [r for r in samples if r["t"] >= t0 - 1e-9]
    keys = [k for k, v in a[0].items() if k != "t" and isinstance(v, (int, float))] if a else []
    return {"t0": t0, "t1": a[-1]["t"] if a else None, "n": len(a),
            "median": {k: round(float(np.median([r[k] for r in a])), 2) for k in keys},
            "mean": {k: round(float(np.mean([r[k] for r in a])), 2) for k in keys}}


def sample(sim) -> dict:
    """One moment's scores (a `track` row)."""
    land = is_land(sim.w_elev, grid=sim.grid)  # (the sea by connection, PW-1229)
    st = sim.stats()
    sea, sub = ~land, ~land & sim.w_cont
    return {"t": sim.t, "land": st["land_pct"], "cont": st["continental_pct"],
            "largest": st["largest_landmass_pct"], "masses": st["landmasses"],
            "dry": round(100 * float((GROUP[sim.snapshot().koppen[land]] == "B").mean()), 1),
            "ice": st["ice_pct"], "speed": st["mean_speed_cmyr"],
            "plate_max": st["largest_plate_pct"], "plates2": st["plates_over_2pct"],
            # hypsometry (PW-818, PW-846; Earth at L6: shelf 0..-200 m ~5.8% of the ocean, submerged
            # continent's median -184 m, land above 3 km ~2.4%, above 4 km ~1.5%: ETOPO1 on the L6 grid)
            "shelf": round(100 * float((sim.w_elev[sea] > -200).mean()), 1),
            "sub_cont_med": int(np.median(sim.w_elev[sub])) if sub.any() else 0,
            "gt3km": round(100 * float((sim.w_elev[land] > 3000).mean()), 2),
            "gt4km": round(100 * float((sim.w_elev[land] > 4000).mean()), 2), "peak": st["max_elev_m"],
            "npp": round(float(sim.npp[land].mean())), "trees": round(100 * float(sim.tree_cover[land].mean()), 1)}


def world_scores(seed: int, myr: float) -> dict:
    sim = Simulation(build_grid(6), seed, Params(run_end=myr), 2.0)  # (the run's end is now, as simulate sets it)
    v0 = float((sim.w_thick * sim.w_cont).sum())
    t0, late_t = late_window(myr)
    # `track` every 100 Myr as before (its min/max columns compare with older lines); `late_track` every LATE_STEP
    # Myr over the late window. Sampling only reads the state, so the run is the same however it is cut.
    hundreds = [min(myr, 100.0 * k) for k in range(1, int(np.ceil(myr / 100 - 1e-9)) + 1)]
    track, late_track = [], []
    for t in sorted(set(hundreds) | set(late_t)):
        sim.run(t)
        r = sample(sim)
        if t in late_t:
            late_track.append(r)
        if t in hundreds:
            track.append(r)
    last = track[-1]
    return {"seed": seed, "myr": myr, "final": last, "late": late_summary(late_track, t0),
            "volume_ratio": round(float((sim.w_thick * sim.w_cont).sum()) / v0, 3),
            "land_min": min(r["land"] for r in track), "land_max": max(r["land"] for r in track),
            "largest_max": max(r["largest"] for r in track),
            "plate_max_max": max(r["plate_max"] for r in track),
            "ocean_age": round(float(sim.w_age[~sim.w_cont].mean()), 1),
            "plant_groups": [None if not np.isfinite(t) else t for t in sim.flora], "track": track,
            "late_track": late_track}


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
        f, late = w["final"], w["late"]
        lm, la = late["median"], late["mean"]
        print(f"seed {w['seed']} late {late['t0']:g}-{late['t1']:g} Myr (median of {late['n']} moments; compare these, "
              f"not the one {w['myr']:g}-Myr moment below): land {lm['land']}%, dry {lm['dry']}%, ice {lm['ice']}%, "
              f"land >3 km {lm['gt3km']}%, >4 km {lm['gt4km']}% (mean {la['gt4km']}%), "
              f"land NPP {lm['npp']} (mean {la['npp']}) g C/m2/yr, tree cover {lm['trees']}%")
        print(f"seed {w['seed']} @ {w['myr']:g} Myr: land {f['land']}% (range {w['land_min']}-{w['land_max']}), "
              f"crust {f['cont']}%, volume x{w['volume_ratio']}, dry {f['dry']}%, ice {f['ice']}%, "
              f"largest landmass max {w['largest_max']}%, largest plate {f['plate_max']}% (max {w['plate_max_max']}%, "
              f"{f['plates2']} plates >2%), shelf {f['shelf']}% of ocean (submerged continent median {f['sub_cont_med']} m), "
              f"land >4 km {f['gt4km']}%, peak {f['peak']} m, ocean age {w['ocean_age']} Myr, "
              f"land NPP {f['npp']} g C/m2/yr, tree cover {f['trees']}%, plant groups at {w['plant_groups']} Myr")
    print(f"appended to {out.relative_to(ROOT)}  [{rec['seconds']}s]")


if __name__ == "__main__":
    main()
