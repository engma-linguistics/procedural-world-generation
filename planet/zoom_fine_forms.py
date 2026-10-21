"""Forms a fine zoom draws at its own scale (PW-392): glaciers, landform
overlays (karst, dunes) and coastal life with the reefs as terrain. Each reuses the regional
zoom's code (zoom.glaciers, zoom_landforms.Landforms.finish,
zoom_coastal.place) on the fine pixels, with the parent's say kept:

  glaciers   zoom.glaciers() on the fine ground (its drainage, the fine
             climate's lapse), the parent's ice as the "coarse ice" (the
             accumulation zones and the sheet it feeds), so the outline
             follows the fine valleys and agrees with the parent's.
  overlays   the planet-fixed forms (dolines, poljes, towers, dunes) drawn
             at the fine scale with the regional zoom's seed (the root of
             the lineage, so every level draws the same dune and doline),
             but only their sub-parent-pixel part: each parent pixel's mean
             change is taken off again, so the parent's own (resolved at its
             scale) isn't drawn twice and the pixel means stay.
  reefs      the volcanoes' reefs (atoll rims and their islets, fringing flats)
             by zoom_volcanoes.fields on the fine pixels, same seed.
  coastal    zoom_coastal.place on the fine sea floor and shore, each
             habitat kept to where the parent has it; reef pixels raised to
             their flats, the lagoons around deepened to keep each parent
             pixel's mean.
"""

from __future__ import annotations

import numpy as np

from . import icemass
from . import zoom as Z
from . import zoom_coastal as ZCL
from . import zoom_kernels as ZK
from . import zoom_landforms as ZL
from . import zoom_volcanoes as ZV
from . import zoom_vegetation as ZVG
from .geo import R_KM, latlon

OVERLAY_CLASSES = (8, 9)  # landform.KARST, landform.DUNES: the classes with overlays (Synth.overlay)
HABITAT_KEEP = 0.25  # a fine habitat pixel stands where the parent's habitat (bilinear) is at least this
LAGOON_MAX_M = 40.0  # m: the lagoons deepened by at most this to keep a parent pixel's mean
SUBPIXEL_PASSES = 4  # subpixel(): passes taking each parent pixel's mean off a change
ICE_NEAR = 0.1  # new glacier ice only where the parent's ice (bilinear) is at least this


def root_seed(pmeta: dict, seed: int) -> int:
    """The noise seed the lineage's first (regional) zoom drew with: planet-fixed forms (dunes, dolines, reef
    and kelp patches) agree at every level."""
    return int((pmeta.get("params") or {}).get("root_seed", pmeta.get("seed", seed)))


def subpixel(dz: np.ndarray, mask: np.ndarray, pa, own: np.ndarray, pr, pc) -> np.ndarray:
    """dz on `mask` less each parent pixel's mean of it (smoothly interpolated, no steps at the parent's pixel
    edges): the part of a change the parent's pixels can't hold."""
    nown = pa.nx * pa.ny
    cnt = np.bincount(own, mask, minlength=nown)
    out = np.where(mask, dz, 0.0)
    for _ in range(SUBPIXEL_PASSES):  # (the interpolation of the means isn't the means: take what is left off again)
        m = np.bincount(own, out, minlength=nown) / np.maximum(cnt, 1)
        out = np.where(mask, out - pa.bicubic(m.reshape(pa.ny, pa.nx), pr, pc), 0.0)
    return out


# ---------------------------------------------------------------------------
# Glaciers
# ---------------------------------------------------------------------------
def glaciers(world: dict, pa, pr, pc, Pk, P, h, land, sea, ring, nb: int, res: float, fields: dict, S: int,
             precip: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(mask, thickness m) of the zoom's glaciers on the finished ground h (all flat, nb x nb): zoom.glaciers()
    with the fine climate (fields: zoom_vegetation.fine_fields) and the parent's ice as its coarse ice."""
    g = world["grid"]
    sp = g.spacing * R_KM
    ice_c = np.maximum(pa.bilinear("ice", pr, pc), 0.0) if "ice" in pa.L else np.zeros(len(h))
    jul = fields["p_jul"] / np.maximum(fields["p_jul"] + fields["p_jan"], 1e-9)
    jul = np.where(fields["p_jul"] + fields["p_jan"] > 0, jul, 0.5)
    noise = ZK.fbm(Pk, 0.4 * sp, Z._octaves(0.4 * sp, 2 * res), 0.6, S + 5) / 0.17
    lat = latlon(P)[0]
    tilt = float(world["meta"].get("params", {}).get("tectonics", {}).get("tilt", 23.4))
    jitter = Z.tie_jitter(Pk, res, S + 63)
    _, rec, order = ZK.flood_d8(h, ring | sea, nb, nb, 1e-3, jitter)
    glacier, th = Z.glaciers(h, rec, order, land, sea, nb, nb, res, fields["warm_sl"], fields["cold_sl"],
                             np.full(len(h), icemass.LOCAL), precip, jul, ice_c, lat, noise, tilt)
    # kept to the parent's ice: new ice only within a parent pixel of it (the fine crests alone would seed
    # specks the parent's pixels never held), the parent's ice inside (> 1/2 a pixel in) stays, and where the
    # parent has ice its surface is the least the fine ice stands to (the fine valleys filled to it)
    if "ice" in pa.L:
        ice_p = np.asarray(pa.L["ice"], float)
        has = pa.bilinear((ice_p > 0).astype(float), pr, pc)
        glacier = ((glacier & (has > ICE_NEAR)) | (has > 0.5)) & land
        surf = pa.bilinear(np.where(ice_p > 0, np.asarray(pa.L["elevation"], float) + ice_p, 0.0), pr, pc) / np.maximum(has, 1e-9)
        fill = np.where(has > ICE_NEAR, surf - h, 0.0)
        th = np.where(glacier, np.where(has > 0.5, np.maximum(fill, 1.0), th), 0.0)
    return glacier, np.where(glacier, np.maximum(th, 1.0), 0.0)


# ---------------------------------------------------------------------------
# Landform overlays
# ---------------------------------------------------------------------------
def landform_overlay(world: dict, fr, pa, pr, pc, own, Pk, px, py, nb: int, res: float, S: int, h, land, rec, order,
                     discharge, water, ice, active, region):
    """The karst and dune overlays on the finished fine ground (zoom_landforms.Landforms.finish), as sub-parent-
    pixel detail. All arrays flat on the nb x nb pixels (the halo included; region: the part the stats count).
    Returns None where no such class is near, else {"h", "q", "pond", "pond_depth", "stats"}."""
    g, L = world["grid"], world["layers"]
    if "landform" not in L:
        return None
    size_km = nb * res
    sel = ZVG._sel(g, fr, size_km)
    cx, cy = fr.to_plane(g.centers[sel])
    e_c = np.asarray(L["elevation"], float)[sel]
    land_c = e_c > 0
    form = np.asarray(L["landform"])[sel]
    if not np.any(np.isin(form[land_c], OVERLAY_CLASSES)):
        return None
    sp = g.spacing * R_KM

    def interp(v, w, s):
        return ZK.gauss_interp(px, py, cx, cy, v, w, s)

    base, _ = interp(np.maximum(e_c, 1.0)[:, None], land_c[:, None].astype(float), 0.5 * sp)
    base = np.nan_to_num(base[:, 0], nan=1.0)
    lf = ZL.Landforms.build(L, sel, cx, cy, land_c, px, py, Pk, sp, res, nb, nb, S, land, base, interp, g,
                            fr.to_plane)
    if lf is None:
        return None
    lf.set_region(region)
    fz = lf.finish(h, {"rec": rec, "order": order, "q": discharge, "water": water, "ice": ice, "active": active})
    free = active & ~water & ~ice
    h2 = fz["h"]
    for _ in range(3):  # (the floor at 0.5 m keeps low ground from going under: its change's mean taken off again)
        dz = subpixel(h2 - h, free, pa, own, pr, pc)
        h2 = np.where(free, np.maximum(h + dz, 0.5), h)
    return {"h": h2, "q": fz["q"], "pond": fz["pond"] & free, "pond_depth": fz["pond_depth"], "stats": fz["stats"]}


# ---------------------------------------------------------------------------
# Coastal life and the reefs as terrain
# ---------------------------------------------------------------------------
def coastal(world: dict, fr, pa, pr, pc, own, Pk, px, py, n: int, res: float, rseed: int, h, water, glacier,
            surf_rock, volcano_reef=None) -> dict:
    """The fine zoom's coastal life (zoom_coastal.place on the fine shore and sea floor, with the lineage's seed) kept
    to where the parent has each habitat, and its reef flats as terrain. All arrays flat on the n x n pixels.
    Returns {"layer", "h" (reef flats raised, the lagoons deepened to keep each parent pixel's mean), "stats",
    "reef_forms"}."""
    land = water == 0
    d_sea = ZK.inside_distance(land, n, n, False) * res
    cz = ZCL.place(world, fr, Pk, px, py, n, n, res, n * res, rseed, h, water, glacier, d_sea, surf_rock, volcano_reef)
    layer = cz["layer"].copy()
    p_cl = np.asarray(pa.L["coastal_life"]) if "coastal_life" in pa.L else None
    if p_cl is None:
        return {"layer": layer, "h": h, "stats": cz["stats"], "reef_forms": cz["reef_forms"]}
    keep = np.zeros(len(h), bool)
    for k in (ZCL.REEF, ZCL.KELP, ZCL.SEAGRASS, ZCL.MANGROVE, ZCL.SALT_MARSH):
        pk = pa.bilinear((p_cl == k).astype(float), pr, pc) >= HABITAT_KEEP
        keep |= (layer == k) & pk
    if volcano_reef is not None:  # (a volcano's own reef: zoom_volcanoes' rim, drawn here at the fine scale)
        keep |= (layer == ZCL.REEF) & volcano_reef
    layer = np.where(keep, layer, 0).astype(np.uint8)
    on = keep & (layer == ZCL.REEF) & np.isfinite(cz["reef_top"])
    out = h.copy()
    if on.any():
        out = np.where(on, np.maximum(h, np.nan_to_num(cz["reef_top"], nan=-1e9)), h)
        gain = out - h
        mov = (water == 1) & ~on & cz["shelf"] & (layer != ZCL.REEF)
        nown = pa.nx * pa.ny
        cnt = np.bincount(own, mov, minlength=nown)
        per = np.bincount(own, gain, minlength=nown) / np.maximum(cnt, 1)
        corr = pa.bicubic(np.where(cnt > 0, per, 0.0).reshape(pa.ny, pa.nx), pr, pc)
        out = np.where(mov, out - np.clip(corr, 0.0, LAGOON_MAX_M), out)
        out = np.where(water == 1, np.minimum(out, -0.5), out)
    cell = res * res
    stats = {ZCL.LIFE[k][0]: round(float((layer == k).sum() * cell)) for k in ZCL.LIFE if k}
    return {"layer": layer, "h": out, "stats": stats, "reef_forms": cz["reef_forms"]}


def volcano_reefs(world: dict, fr, px, py, n: int, res: float, Pk, rseed: int):
    """The volcanoes' reefs (fringing flats, barrier reefs, atoll rims with their islets) at the fine scale:
    zoom_volcanoes.fields on the fine pixels with the lineage's seed draws the same planet-fixed forms the regional
    zoom did, now at the pixel size. Returns {"reef": mask, "h": their heights (m)} or None."""
    g = world["grid"]
    vf = ZV.fields(world, fr, px, py, res, g.spacing * R_KM, Pk, rseed, n * res)
    if vf is None or not vf["reef"].any():
        return None
    z = np.maximum(vf["z"], vf["bump"])
    on = vf["reef"] & np.isfinite(z)
    return {"reef": on, "h": np.where(on, z, 0.0)} if on.any() else None
