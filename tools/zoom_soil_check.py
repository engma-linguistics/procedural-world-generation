"""Zoom soils against their world cells (PW-331; docs/proposals/soils.md step 6).

Builds regional zooms of a world in memory (nothing is saved) and reports,
for the coarse land cells wholly inside each zoom:
- the slope conversion (soils.PX_SLOPE): each cell's slope (m/km to its
  steepest neighbour, the world's measure) against its pixels' RMS slope
  (tan x 1000), and the cells' erosion against their pixels' mean;
- agreement: the share of a cell's pixels whose soil is in the cell's
  group (soil_check's ten), on uniform cells (gentle, inland), steep ones
  and those by the sea (the world's slope counts the drop to the sea floor);
- the soil mix by terrain: steep pixels, hollows, floodplains;
- the soils' seconds per zoom.
With --png, a small image per zoom: the cells' soil types (nearest cell)
beside the pixels', hill-shaded (docs/review/soils/zoom_*.png).

    uv run python tools/zoom_soil_check.py <world> --at LAT,LON [--at ...] [--size 400] [--res 2] [--png DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps must precede numpy, planet/parallel.py)
import numpy as np  # noqa: E402
from planet import soils as SO  # noqa: E402
from planet import world as W  # noqa: E402
from planet.zoom import regional as Z  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.images import write_png  # noqa: E402
from tools.soil_check import TYPE_GROUP  # noqa: E402


def _rgb(hexs):
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in hexs], float)


SOIL_RGB = _rgb([t[5] for t in SO.TYPES])
# soil_check's ten groups (an oxisol next to an ultisol is the same story); "none" apart
GROUP = np.array([{0: "none", **{k: v for k, v in TYPE_GROUP.items()}}[t[0]] for t in SO.TYPES])
UNIFORM = 3.0  # m/km: a cell this gentle, away from the sea, has uniform terrain (no hill or sea next to it)


def check(world: dict, lat: float, lon: float, size_km: float, res_km: float, png: Path | None = None) -> dict:
    g, L = world["grid"], world["layers"]
    z = Z.build(world, lat, lon, size_km, res_km, log=lambda *a: None)
    zl = {k: np.asarray(v).ravel() for k, v in z["layers"].items()}
    nx, ny, res, fr = z["nx"], z["ny"], z["res"], z["frame"]
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    cell = g.locate(fr.to_sphere(X.ravel(), Y.ravel()))
    soil, depth = zl["soil"].astype(int), zl["soil_depth"]
    bare = (zl["water"] == 0) & (zl["ice"] <= 0)
    w_soil = np.asarray(L["soil"], int)
    w_depth = np.asarray(L["soil_depth"], float)
    elev = np.asarray(L["elevation"], float)
    s_cell = SO.cell_slope(g, elev)  # (the soils' own: the sea at sea level)
    P_cell = np.asarray(L["precipitation"], float)
    # the pixels' terrain (as zoom_vegetation computes it)
    from planet.zoom import terrain as ZT
    from planet.geo import latlon
    lat_px = latlon(fr.to_sphere(X.ravel(), Y.ravel()))[0]
    h = zl["elevation"].astype(float)
    tr = ZT.indices(np.where(zl["water"] == 1, 0.0, h), zl["water"] == 0, zl["water"] == 1,
                    zl["discharge"].astype(float),
                    zl["drainage_area"].astype(float), lat_px, nx, ny, res)
    tan = tr["slope"]
    full_px = 4 * np.pi * R_KM ** 2 / g.n / res ** 2
    cells, cnt = np.unique(cell[bare], return_counts=True)
    keep = cells[(cnt > 0.8 * full_px) & (w_soil[cells] > 0)]
    rows = []
    for c in keep:
        m = bare & (cell == c)
        rows.append((c, s_cell[c], 1000 * np.sqrt(np.mean(tan[m] ** 2)), np.mean(GROUP[soil[m]] == GROUP[w_soil[c]]),
                     depth[m].mean(), w_depth[c],
                     np.mean(SO.erosion_rate(SO.zoom_slope(tan[m], res), zl["precipitation"][m])),
                     SO.erosion_rate(s_cell[c], P_cell[c])))
    r = np.array(rows) if rows else np.zeros((0, 8))
    # (cells next to the sea: the world's slope counts the drop to the sea floor, so they read steeper)
    coastal = np.array([(elev[g.nbr_idx[g.nbr_off[c]:g.nbr_off[c + 1]]] <= 0).any() for c in keep], bool)
    gentle = (r[:, 1] < UNIFORM) & ~coastal if len(r) else np.zeros(0, bool)
    steep = (r[:, 1] >= SO.STEEP) & ~coastal if len(r) else np.zeros(0, bool)
    out = {"lat": lat, "lon": lon, "res_km": res, "cells": len(r),
           "soil_seconds": z["stats"]["vegetation"].get("soils", {}).get("seconds"),
           "zoom_seconds": z["seconds"],
           "slope_ratio_median": float(np.median(r[:, 2] / np.maximum(r[:, 1], 0.1))) if len(r) else None,
           "erosion_px_over_cell_median": float(np.median(r[:, 6] / r[:, 7])) if len(r) else None,
           "agree_uniform": float(r[gentle, 3].mean()) if gentle.any() else None,
           "agree_steep": float(r[steep, 3].mean()) if steep.any() else None,
           "agree_coastal": float(r[coastal, 3].mean()) if coastal.any() else None,
           "depth_px_mean": float(r[:, 4].mean()) if len(r) else None,
           "depth_cell_mean": float(r[:, 5].mean()) if len(r) else None}
    # the soil mix by terrain
    s_eq = SO.zoom_slope(tan, res)
    names = {t[0]: t[2] for t in SO.TYPES}

    def mix(mask):
        if not mask.any():
            return {}
        b = np.bincount(soil[mask], minlength=len(SO.TYPES)) / mask.sum()
        return {names[k]: round(100 * float(b[k])) for k in np.argsort(-b)[:4] if b[k] >= 0.03}
    out["mix_all"] = mix(bare)
    out["mix_steep"] = mix(bare & (s_eq > 2 * SO.STEEP))
    out["mix_flat"] = mix(bare & (s_eq < 0.5 * SO.STEEP))
    out["mix_big_river_plain"] = mix(bare & (tr["river_q"] >= 300) & (tr["river_dist"] <= 1)
                                     & (h - tr["river_h"] < 5))
    for k, sel in (("depth_steep_m", bare & (s_eq > 2 * SO.STEEP)), ("depth_flat_m", bare & (s_eq < 0.5 * SO.STEEP))):
        out[k] = float(depth[sel].mean()) if sel.any() else None
    if png is not None:
        f = (0.55 + 0.5 * Z.hillshade(h.reshape(ny, nx), res).ravel())[:, None]
        sea_rgb = np.array([40.0, 70, 120])
        ice_rgb = np.array([230.0, 240, 250])
        lake_rgb = np.array([70.0, 130, 196])

        def paint(types):
            img = SOIL_RGB[types] * f
            img = np.where((zl["water"] == 1)[:, None], sea_rgb, img)
            img = np.where((zl["water"] == 2)[:, None], lake_rgb, img)
            img = np.where(((zl["water"] == 0) & (zl["ice"] > 0))[:, None], ice_rgb * f, img)
            return np.clip(img, 0, 255).reshape(ny, nx, 3)
        a, b = paint(np.where(zl["water"] == 0, w_soil[cell], 0)), paint(soil)
        step = max(1, nx // 300)
        a, b = a[::step, ::step], b[::step, ::step]
        gap = np.full((a.shape[0], 6, 3), 255.0)
        png.parent.mkdir(parents=True, exist_ok=True)
        write_png(png, np.concatenate([a, gap, b], 1).astype(np.uint8))
        out["png"] = str(png)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("world")
    ap.add_argument("--at", action="append", required=True, help="LAT,LON (repeatable)")
    ap.add_argument("--size", type=float, default=400.0)
    ap.add_argument("--res", type=float, default=2.0)
    ap.add_argument("--png", type=Path, default=None, help="directory for zoom_<lat>_<lon>.png")
    a = ap.parse_args()
    world = W.load(Z.find_world(a.world))
    for at in a.at:
        lat, lon = (float(v) for v in at.split(","))
        png = a.png / f"zoom_{lat:g}_{lon:g}_{a.res:g}km.png" if a.png else None
        out = check(world, lat, lon, a.size, a.res, png)
        for k, v in out.items():
            print(f"{k:28s} {round(v, 3) if isinstance(v, float) else v}")
        print()


if __name__ == "__main__":
    main()
