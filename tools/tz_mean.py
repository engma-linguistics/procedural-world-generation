"""The time zoom's time-mean ice against the run's (PW-467; PW-555 stage 0).

    uv run python tools/tz_mean.py MOMENT ... [--kyr 400] [--skip 100] [--set k=v ...] [--json OUT]

MOMENT: a pickled source from tools/ice_diag.py --moments (DIR/seed11_L6_at400.pkl), `earth` (L6),
`fixture` (the consistency test's L5 seed 1 @ 300 Myr, 4 C colder, the run's own ice for that climate;
tests/test_timezoom_consistency.py), or `suite` (MOMENTS below, from SUITE_DIR). Nothing is written to
the store.

PW-462's framing: a time zoom is a window on the run's ice-age cycles, so its time-mean ice should match
the run's ice; its start and end needn't. For each moment this runs the default forced zoom (the glacial
index on) for --kyr and prints: the run's sea level from ice; the zoom's mean change of sea level (all,
and after --skip kyr), its min and max and swing; where the start sits in the zoom's range (percentile:
0 = the start is the zoom's highest sea level, i.e. its interglacial; 100 = its glacial); the mean iced
area against the start's; cycles, endings and backstops. The bar (PW-467): the mean after --skip within
max(15 m, 0.25 x swing) of the start, and the iced area within 25%.
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import timezoom as Z  # noqa: E402
from planet.grid import build_grid  # noqa: E402

# The fixed moment suite (docs/review/ice-v2/checkpoint-0.md lists the seeds and times): pickles made by
#   tools/ice_diag.py --seed S --myr M --moments T ... --out $ICE_MOMENTS (deterministic, ~4 MB each at L6,
# so they're regenerated rather than committed; a run-physics change re-picks the moments by their state)
import os  # noqa: E402
SUITE_DIR = Path(os.environ.get("ICE_MOMENTS", ROOT / "ice_v2_moments"))
MOMENTS = ["fixture", "earth"]  # + every *.pkl in SUITE_DIR


def fixture():
    sys.path.insert(0, str(ROOT / "tests"))
    from helpers import run_sim
    from planet import vegetation
    from planet.tectonics import earth
    from planet.tectonics.isostasy import ice_load, land_view
    src = Z.source_from_sim(run_sim(level=5, seed=1, myr=300))
    g = src["grid"]
    dT = src["dT"] - 4.0
    bed0 = src["elev"] + ice_load(g, src["ice"])
    sim = SimpleNamespace(grid=g, params=SimpleNamespace(tilt=src["tilt"]), cell_area=4 * np.pi / g.n,
                          precip=None, p_jul=None, p_jan=None)
    ice = np.zeros(g.n)
    for _ in range(6):
        bed = bed0 - ice_load(g, ice)
        e, ice0, _ = land_view(bed, np.where(bed0 > 0, ice, 0.0))
        land = e > 0
        v = src["veg"]
        c, _ = vegetation.coupled_climate(g, e, dT, src["tilt"], np.where(land, ice0, 0.0), nu0=v["nu0"],
                                          pco2=v["pco2"], unlocked=v["unlocked"])
        sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
        ice = earth.ice_sheets(sim, land, e, c["ground"], ice0, ice_load(g, ice), marine=earth.marine_view(bed, c))
    e, ice0, _ = land_view(bed0 - ice_load(g, ice), np.where(bed0 > 0, ice, 0.0))
    return dict(src, elev=e, ice=ice0, dT=dT, source_name="fixture L5 s1 @ 300 Myr, -4 C")


def sea_ice_of(src) -> float:
    """The run's sea level from ice at the moment (m): the pickle's own, else from its ice as
    earth.update_climate counts it (-0.9 x volume / ocean area)."""
    if "sea_ice_run" in src:
        return float(src["sea_ice_run"])
    land = src["elev"] > 0
    ice = np.where(land, src["ice"], 0.0)
    return float(-0.9 * ice.sum() / max(int((~land).sum()), 1))


def load(m: str) -> tuple[str, dict]:
    if m == "earth":
        return "earth", Z.source_earth(6)
    if m == "fixture":
        return "fixture", fixture()
    src = pickle.loads(Path(m).read_bytes())
    src["grid"] = build_grid(src["level"])
    return Path(m).stem, src


def measure(name, src, kyr, skip, sets) -> dict:
    res = Z.simulate(src, kyr, 0.5, 2.0, Z.TZParams(**sets))
    fr = res["frames"]
    t = np.array([f["t"] for f in fr])
    sl = np.array([f["stats"]["sea_level_change_m"] for f in fr])
    area = np.array([f["stats"]["ice_pct"] for f in fr])
    late = t >= skip
    swing = float(sl.max() - sl.min())
    mean_late = float(sl[late].mean()) if late.any() else float("nan")
    tol = max(15.0, 0.25 * swing)
    a0 = max(area[0], 1e-6)
    cyc = res["cycle"]
    out = {"moment": name, "source": src.get("source_name"), "run_sea_ice": round(sea_ice_of(src), 1),
           "start_ice_pct": round(float(area[0]), 2), "mean_all": round(float(sl.mean()), 1),
           "mean_late": round(mean_late, 1), "min": round(float(sl.min()), 1), "max": round(float(sl.max()), 1),
           "swing": round(swing, 1), "start_pct": round(100 * float((sl > 0).mean()), 0),
           "area_ratio": round(float(area[late].mean()) / a0, 2), "tol": round(tol, 1),
           "cycles": cyc.get("cycle_kyr"), "endings": len(cyc.get("endings", [])),
           "backstops": cyc.get("backstops"), "runtime_s": res["runtime_s"]}
    out["pass_mean"] = bool(abs(mean_late) <= tol)
    out["pass_area"] = bool(abs(out["area_ratio"] - 1) <= 0.25)
    return out


def row(r) -> str:
    return (f"{r['moment']:<24} run ice {r['run_sea_ice']:7.1f} m ({r['start_ice_pct']:5.2f}% iced) | zoom mean "
            f"{r['mean_all']:+6.1f} / after skip {r['mean_late']:+6.1f} (tol {r['tol']:.0f}) "
            f"{'ok' if r['pass_mean'] else 'F'} | range {r['min']:+.0f}..{r['max']:+.0f} (swing {r['swing']:.0f}),"
            f" start at {r['start_pct']:.0f}th pct | area x{r['area_ratio']} {'ok' if r['pass_area'] else 'F'} |"
            f" endings {r['endings']}, backstops {r['backstops']}, cycles {r['cycles']} | {r['runtime_s']:.0f} s")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("moments", nargs="+")
    ap.add_argument("--kyr", type=float, default=400.0)
    ap.add_argument("--skip", type=float, default=100.0)
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--json")
    a = ap.parse_args()
    sets = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        f = Z.TZParams.__dataclass_fields__[k]
        sets[k] = v if f.type == "str" else (int(v) if f.type == "int" else float(v))
    ms = []
    for m in a.moments:
        ms += (MOMENTS + sorted(str(p) for p in SUITE_DIR.glob("*.pkl"))) if m == "suite" else [m]
    rows = []
    for m in ms:
        name, src = load(m)
        r = measure(name, src, a.kyr, a.skip, sets)
        print(row(r), flush=True)
        rows.append(r)
    n = len(rows)
    print(f"mean within tol: {sum(r['pass_mean'] for r in rows)}/{n}; area within 25%: "
          f"{sum(r['pass_area'] for r in rows)}/{n}")
    if a.json:
        Path(a.json).write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
