"""Resources (PW-155) check: per-world shares of land at each likelihood, maps, and an Earth plausibility pass.

    PYTHONPATH=. uv run python tools/resources_check.py WORLD [WORLD ...] [--earth EARTH_WORLD] [--png DIR]

For a world with resource layers (`planet resources`), prints the % of land >= 0.25 / 0.5 per resource and
writes equirectangular PNGs (DIR/<world>_<resource>.png; 'dominant' = the resource map). --earth takes the
Earth world, swaps its terrain-guessed rock for GLiM's parent rock (data/earth/glim_L6.npz, Hartmann & Moosdorf
2012) and runs the no-history rules, then reports the mean likelihood in named regions: an anchor, not a target.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from planet import resources as RS
from planet import store as S
from planet import world as W
from planet.geo import world_land
from planet.images import write_png

W_PX, H_PX = 720, 360


def _hex(c):
    c = c.lstrip("#")[:6]
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], float)


def png(path, grid, L, v=None, color="#ffffff", dominant=False):
    idx = W.nearest_cell_map(grid, W_PX, H_PX)
    land = world_land(L)
    base = np.where(land[:, None], np.array([107, 103, 95.]), np.array([28, 47, 79.]))
    if dominant:
        cols = np.array([_hex("#000000")] + [_hex(r[3]) for r in RS.RESOURCES])
        rid = np.asarray(L["resource"], int)
        val = np.array([L[f"res_{RS.KEYS[r - 1]}"][i] if r else 0 for i, r in enumerate(rid)], float)
        a = np.where(rid > 0, 0.35 + 0.65 * val, 0.0)[:, None]
        img = base * (1 - a) + cols[rid] * a
    else:
        a = np.sqrt(np.clip(np.asarray(v, float), 0, 1))[:, None]
        img = base * 0.8 * (1 - a) + _hex(color) * a
    write_png(path, img[idx].astype(np.uint8))


def shares(L):
    land = world_land(L)
    return {k: (100 * (np.asarray(L[f"res_{k}"])[land] >= 0.25).mean(), 100 * (np.asarray(L[f"res_{k}"])[land] >= 0.5).mean())
            for k in RS.KEYS if f"res_{k}" in L}


REGIONS = {  # (lat0, lat1, lon0, lon1), resource, expectation
    "Andes (porphyry)": ((-35, -5, -76, -66), "porphyry_cu", "high"),
    "N American Cordillera (porphyry)": ((32, 50, -122, -105), "porphyry_cu", "high"),
    "Canadian Shield interior (porphyry)": ((50, 60, -100, -80), "porphyry_cu", "low"),
    "Zechstein basin (salt)": ((51, 55, 6, 20), "salt", "high"),
    "Persian Gulf - Zagros (salt)": ((25, 33, 45, 56), "salt", "high"),
    "Amazon basin (salt)": ((-8, 0, -70, -55), "salt", "low"),
    "Guiana-Guinea tropics (bauxite)": ((3, 12, -15, -5), "bauxite", "high"),
    "Sahara (bauxite)": ((18, 28, -5, 20), "bauxite", "low"),
    "Himalaya (metamorphic gems)": ((26, 34, 76, 92), "gem_meta", "n/a: no history on Earth"),
}


def earth(ref, out_dir):
    path = S.find_world(ref)
    w = W.load(path)
    g, L = w["grid"], w["layers"]
    glim = np.load(S.root() / "data" / "earth" / f"glim_L{g.level}.npz")["rock"].astype(int)
    land = world_land(L)
    rock = np.where(glim >= 0, glim, np.asarray(L["rock"], int))
    L = {**L, "rock": rock, "strata_top": rock, "surface_rock": rock,
         "sediment_cover": np.where(np.isin(rock, (3, 6, 7, 8, 9, 10, 14)), 2.0, 0.02)}
    R = RS.likelihoods(g, L, w["meta"], None)
    lat, lon = g.lat, g.lon
    print(f"\nEarth ({ref}, GLiM rock, no history):")
    for name, ((a, b, c, d), k, want) in REGIONS.items():
        m = land & (lat >= a) & (lat <= b) & (lon >= c) & (lon <= d)
        v = R[k][m]
        print(f"  {name:38s} mean {v.mean():.2f}  >=0.25 {100 * (v >= 0.25).mean():5.1f}% of {m.sum():4d} cells  (expect {want})")
    if out_dir:
        for k in ("porphyry_cu", "salt", "bauxite", "coal", "orogenic_au", "sn_w"):
            png(out_dir / f"earth_{k}.png", g, L, R[k], RS.RESOURCES[RS.KEYS.index(k)][3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worlds", nargs="*")
    ap.add_argument("--earth")
    ap.add_argument("--png", type=Path)
    a = ap.parse_args()
    if a.png:
        a.png.mkdir(parents=True, exist_ok=True)
    rows = {}
    for ref in a.worlds:
        w = W.load(S.find_world(ref))
        rows[ref] = shares(w["layers"])
        if a.png:
            png(a.png / f"{ref}_dominant.png", w["grid"], w["layers"], dominant=True)
            for k in ("porphyry_cu", "orogenic_au", "bif_fe", "coal", "oil", "salt", "bauxite", "diamond"):
                png(a.png / f"{ref}_{k}.png", w["grid"], w["layers"], w["layers"][f"res_{k}"],
                    RS.RESOURCES[RS.KEYS.index(k)][3])
    if rows:
        print("% of land at >= 0.25 / >= 0.5")
        print(f"{'resource':16s}" + "".join(f"{r:>14s}" for r in rows))
        for k in RS.KEYS:
            print(f"{k:16s}" + "".join(f"{rows[r][k][0]:7.1f}/{rows[r][k][1]:5.1f} " for r in rows))
    if a.earth:
        earth(a.earth, a.png)


if __name__ == "__main__":
    main()
