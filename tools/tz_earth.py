"""The Earth time zoom's ice-age bars (PW-555 stage 1; docs/review/ice-v2-criteria.md section 3.4).

    uv run python tools/tz_earth.py [--kyr 600] [--level 6] [--set k=v ...] [--json OUT] [--npz OUT]

Runs the default forced time zoom of today's Earth (the glacial index on, real ice with anchor=obs) in
memory (nothing is written to the store) and checks the zoom bars:
  - cycles 80-120 kyr (the gaps between endings);
  - maxima <= -80 m (each glacial's lowest sea level) at a cooling of <= 6 C (the index's cooling_c);
  - endings give back >= 60% of their glacial excess within 15 kyr: (sea level 15 kyr after the ending
    starts - the glacial's lowest) / (the interglacial level before it - the glacial's lowest), the
    interglacial level being the highest sea level in the 40 kyr after the previous ending (the start
    for the first glacial);
  - interglacial ice 9-12% of the land (the iced share of land at each interglacial's highest sea level).
Also reported: the Laurentide at the deepest frame (North American grounded ice: its area, south of 50 N,
and its southernmost latitude), the backstops and the zoom's budget. Keep PLANET_DATA unset for Earth
(its cache sits under the repository's data/earth).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import store as S  # noqa: E402
from planet import timezoom as Z  # noqa: E402
from planet.timezoom.params import LAYERS  # noqa: E402

BARS = {"cycle_kyr": (80.0, 120.0), "max_m": -80.0, "cool_c": 6.0, "give_back": 0.6, "ig_ice_pct": (9.0, 12.0)}


def evaluate(res: dict, grid) -> dict:
    fr = res["frames"]
    ft = np.array([f["t"] for f in fr])
    sl = np.array([f["stats"]["sea_level_change_m"] for f in fr])
    land = np.array([f["stats"]["land_pct"] for f in fr])
    ice_land = 100 * np.array([f["stats"]["ice_pct"] for f in fr]) / land
    c = res["cycle"]
    ends = [e["t"] for e in c["endings"]]
    # interglacial levels: the start, then the highest sea level within 40 kyr after each ending starts
    igs = [(0.0, float(sl[0]), float(ice_land[0]))]
    for e in ends:
        m = (ft >= e) & (ft <= e + 40)
        if e + 40 <= ft[-1]:  # (an interglacial cut off by the zoom's end isn't counted)
            h = np.flatnonzero(m)[np.argmax(sl[m])]
            igs.append((float(ft[h]), float(sl[h]), float(ice_land[h])))
    glacials = []
    for i, e in enumerate(ends[:len(igs)]):
        a = ends[i - 1] + 12 if i else 0.0
        m = (ft >= a) & (ft <= e + 6)
        lo_i = np.flatnonzero(m)[np.argmin(sl[m])]
        g = {"end_t": e, "max_t": float(ft[lo_i]), "max_m": round(float(sl[lo_i]), 1),
             "ig_before_m": round(igs[i][1], 1)}
        j = np.searchsorted(ft, e + 15)
        if j < len(ft):
            excess = igs[i][1] - sl[lo_i]
            g["back_15kyr_m"] = round(float(sl[j] - sl[lo_i]), 1)
            g["give_back"] = round(float((sl[j] - sl[lo_i]) / excess), 2) if excess > 1 else None
        glacials.append(g)
    imax = int(np.argmin(sl))
    ice = S.decode(res["data"]["ice"][imax], LAYERS["ice"]).astype(float)
    na = (grid.lon > -170) & (grid.lon < -50) & (grid.lat > 25) & (grid.lat < 75)
    iced = na & (ice > 1)
    cell = 4 * np.pi * 6371.0 ** 2 / grid.n
    laur = {"t": float(ft[imax]), "min_lat": round(float(grid.lat[iced].min()), 1) if iced.any() else None,
            "south_50_mkm2": round(float((iced & (grid.lat < 50)).sum() * cell / 1e6), 2),
            "area_mkm2": round(float(iced.sum() * cell / 1e6), 2)}
    cyc = c.get("cycle_kyr", [])
    full = [g for g in glacials if g.get("give_back") is not None]
    ig_pct = [round(x[2], 1) for x in igs[1:]]
    out = {"cooling_c": c.get("cooling_c"), "cycle_kyr": cyc, "backstops": c.get("backstops"),
           "glacials": glacials, "interglacial_ice_pct": ig_pct, "start_ice_pct": round(float(ice_land[0]), 1),
           "min_m": round(float(sl.min()), 1), "mean_m": round(float(sl.mean()), 1), "laurentide": laur,
           "budget_m": {k: round(res["budget"][k] / res["budget"]["ocean_area"] * 0.89, 1)
                        for k in ("smb", "calved", "shelf_melt")}, "runtime_s": res["runtime_s"]}
    lo, hi = BARS["cycle_kyr"]
    out["pass"] = {
        "cycles": bool(cyc) and all(lo <= x <= hi for x in cyc),
        "maxima": bool(glacials) and all(g["max_m"] <= BARS["max_m"] for g in glacials),
        "cooling": c.get("cooling_c", 99) <= BARS["cool_c"],
        "give_back": bool(full) and all(g["give_back"] >= BARS["give_back"] for g in full),
        "ig_ice": bool(ig_pct) and all(BARS["ig_ice_pct"][0] <= x <= BARS["ig_ice_pct"][1] for x in ig_pct)}
    return out


def summary(r: dict) -> str:
    gl = "; ".join(f"{g['max_m']:+.0f} m @ {g['max_t']:.0f} (back {g.get('give_back')})" for g in r["glacials"])
    ok = " ".join(f"{k} {'ok' if v else 'F'}" for k, v in r["pass"].items())
    L = r["laurentide"]
    return (f"cooling {r['cooling_c']} C | cycles {r['cycle_kyr']} | glacials {gl} | interglacial ice "
            f"{r['interglacial_ice_pct']}% of land (start {r['start_ice_pct']}) | Laurentide {L['area_mkm2']} Mkm2 "
            f"to {L['min_lat']} N ({L['south_50_mkm2']} south of 50 N) | backstops {r['backstops']} | "
            f"budget {r['budget_m']} | {r['runtime_s']:.0f} s\n  bars: {ok}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kyr", type=float, default=600.0)
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--json")
    ap.add_argument("--npz", help="save the frames' t, sea level, index and iced share of land")
    a = ap.parse_args()
    sets = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        f = Z.TZParams.__dataclass_fields__[k]
        sets[k] = v if f.type == "str" else (int(v) if f.type == "int" else float(v))
    src = Z.source_earth(a.level)
    res = Z.simulate(src, a.kyr, 0.5, 2.0, Z.TZParams(**sets))
    r = evaluate(res, src["grid"])
    r["params"] = sets
    print(summary(r), flush=True)
    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=1))
    if a.npz:
        fr = res["frames"]
        np.savez(a.npz, t=[f["t"] for f in fr], sl=[f["stats"]["sea_level_change_m"] for f in fr],
                 I=[f["stats"]["glacial_index"] for f in fr],
                 ice_land=[100 * f["stats"]["ice_pct"] / f["stats"]["land_pct"] for f in fr])


if __name__ == "__main__":
    main()
