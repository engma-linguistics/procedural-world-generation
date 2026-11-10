"""PW-1629: the tide-dominated delta's mouth count against the river's size (and the zoom seed).
usage: delta_sweep.py OUT.json P1 P2 ... [--seeds 1,2,3] [--seas tide,wave]"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, "tests")  # (run from the repo root with PYTHONPATH=.)
from planet import hydrology  # noqa: E402
from planet.zoom import regional as zoom  # noqa: E402
from planet.geo import smoothstep  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from test_zoom_water import LAKE_AT, _dist_km  # noqa: E402
from test_coast import SEAS, _measures  # noqa: E402


def world(P):
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    x = 2500 - d0
    s = smoothstep(150.0, 450.0, x)
    elev = np.where(d0 < 2500, (1 - s) * (8 + 0.05 * x) + s * (60 + 0.3 * x), -3000.0)
    elev = elev - np.where(d0 < 2300, 500 * np.exp(-(_dist_km(g, *LAKE_AT) / 500) ** 2), 0)
    precip = np.full(g.n, float(P))
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c, channel=0.0)
    land = elev > 0
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": lk["wet"].astype(int),
        "lake_level": np.maximum(np.round(lk["level"]), np.round(elev)), "lake_kind": lk["kind"].astype(int),
        "runoff": c["runoff"],
        "rock": np.zeros(g.n, int), "surface_rock": np.zeros(g.n, int), "climate": np.full(g.n, 2),
        "ice": np.zeros(g.n), "sediment_cover": np.where(land, 0.5, 6.0),
    }
    return {"grid": g, "layers": layers, "meta": {"level": 5}}


CAP = {}
_orig_count = zoom._count_mouths


def _count(dl, px, py, land, rec, discharge, nx, ny, splits=()):
    n = _orig_count(dl, px, py, land, rec, discharge, nx, ny, splits)
    # every sea-draining land pixel reached from the apex, any discharge: their shares of q
    dl2 = dict(dl)
    dl2["q"] = 1e-9
    mouth = land & (rec >= 0) & ~land[np.maximum(rec, 0)]
    shares = []
    if dl.get("apex", -1) >= 0:
        kids = {s: k for s, k, _ in splits}
        seen = np.zeros(len(rec), bool)
        stack = [int(dl["apex"])]
        while stack:
            p = stack.pop()
            while p >= 0 and land[p] and not seen[p]:
                seen[p] = True
                stack += [c for c in kids.get(p, []) if c != rec[p]]
                p = int(rec[p])
        sh = np.sort(discharge[mouth & seen] / dl["q"])[::-1]
        shares = [round(float(v), 3) for v in sh[:12]]
    CAP.setdefault("d", []).append({"nb": dl.get("nb"), "q": dl["q"], "form": dl.get("form"),
                                    "goals": len(dl.get("goals") or []), "shares": shares, "n": n,
                                    "why": str(dl.get("_why")), "wT": dl.get("wT"), "wR": dl.get("wR"), "wW": dl.get("wW"), "sf": dl.get("sf")})
    return n


zoom._count_mouths = _count


def main():
    args = sys.argv[1:]
    out = args.pop(0)
    seeds, seas = [1], ["tide"]
    if "--seeds" in args:
        i = args.index("--seeds"); seeds = [int(v) for v in args[i + 1].split(",")]; del args[i:i + 2]
    if "--seas" in args:
        i = args.index("--seas"); seas = args[i + 1].split(","); del args[i:i + 2]
    rows = []
    for P in map(float, args):
        W = world(P)
        g, L = W["grid"], W["layers"]
        down, flow, elev = L["downstream"], L["flow"], L["elevation"]
        mouths = np.flatnonzero((elev > 0) & (down >= 0))
        mouths = mouths[elev[down[mouths]] <= 0]
        i = mouths[np.argmax(flow[mouths])]
        p = g.centers[i] + g.centers[down[i]]
        lat, lon = np.degrees(np.arcsin(p[2] / np.linalg.norm(p))), np.degrees(np.arctan2(p[1], p[0]))
        for name in seas:
            wave, tide = SEAS[name]
            Lw = {**L, "wave_power": np.where(elev > 0, 0.0, wave), "tide_range": np.where(elev > 0, 0.0, tide)}
            for sd in seeds:
                t0 = time.time()
                CAP.clear()
                z = zoom.build({**W, "layers": Lw}, float(lat), float(lon), size_km=800, res_km=5, seed=sd,
                               iterations=8, log=lambda *a: None)
                m = _measures(z)
                cap = CAP.get("d", [{}])[0]
                d = z["stats"]["deltas"][0]
                row = {"P": P, "sea": name, "seed": sd, "q": d["discharge_m3s"],
                       "mouths": m["mouths"], "rough": round(m["rough"], 3), "sea_near": round(float(m["sea_near"]), 3),
                       "sea_inland": round(float(m["sea_inland"]), 3), "type": m["type"],
                       "keys": sorted(d.keys()), "sec": round(time.time() - t0)}
                row.update({k: cap.get(k) for k in ("why", "nb", "form", "goals", "shares", "wT", "wR", "wW", "sf")})
                row["weights"] = m["weights"]
                print(json.dumps({k: v for k, v in row.items() if k != "keys"}), flush=True)
                rows.append(row)
    json.dump(rows, open(out, "w"), indent=1, default=float)


main()
