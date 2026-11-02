"""Neighbouring land-zoom sections agree at their edges (PW-1301, epic PW-1299; notes in
docs/review/land-zoom/seams-round1.md).

A regional zoom's landscape pass (stream-power grading on the zoom's own D8 drainage) is not local: the height of a
hillside depends on where its water leaves the square, so two overlapping zooms built alone differ by tens of metres on
plains and hundreds in mountains, even though their noise and coarse fields are keyed by place. Rather than a
planet-wide pass, a section is built *matched* to neighbours already built (the sweep's order decides who matches whom):

- **owner**: every place belongs to one section: the tiling's cell (tiling.locate) when both are tiling sections,
  else the nearer centre (the Voronoi bisector). The mosaic shows each place from its owner.
- **pinned**: the new section's pixels the neighbour owns (and covers) take the neighbour's land/sea before the
  terrain detail and its finished heights before the landscape pass; there they are held (outlets at the neighbour's
  height, as the region's edge is held at the target), so the new section's valleys run down to the neighbour's
  ground at the neighbour's levels.
- **ramp**: inside the new section's own ground, within RAMP_KM of the owner line, the finished heights are blended
  from the neighbour's (at the line) to its own (RAMP_KM in), before the final drainage, so rivers, lakes and the
  rest are found on the blended ground; categorical layers (biome, vegetation, landform...) switch at a ragged line
  across the ramp (place-keyed noise), not at a straight seam.

    sources(refs) -> [neighbour dicts]  (saved zooms)
    prepare(ctx)   frame_and_grid: ownership, weights, the neighbours' fields on this zoom's pixels
"""
from __future__ import annotations

import json

import numpy as np

from .. import store as S
from ..geo import smoothstep
from . import kernels as ZK

RAMP_KM = 80.0  # the blend's width inside the section's own ground (the tiling's least margin is ~97 km)
VALID_PX = 3  # a neighbour's pixels this near its own edge aren't used (its bilinear sampling needs a pixel round)
FADE_KM = 20.0  # ... and its weight fades to 0 over this much before them, so a ramp never ends in a step


def sources(refs) -> list[dict]:
    """The saved zooms to match, as {id, frame, res, nx, ny, h (the ground: the bed under a glacier), ice (m), land, section,
    center, layers (categorical, 2D)}."""
    from . import regional as RG
    out = []
    for ref in refs:
        d = S.find_zoom(ref)
        meta = json.loads((d / "zoom.json").read_text())
        want = [k for k in ("elevation", "water", "ice", *CATEGORICAL) if k in meta["layers"]]
        raw = S.read_layers(d, meta["layers"], want)
        h = S.decode(np.asarray(raw["elevation"]), meta["layers"]["elevation"]).astype(np.float32)
        ice = (S.decode(np.asarray(raw["ice"]), meta["layers"]["ice"]).astype(np.float32) if "ice" in raw
               else np.zeros_like(h))
        out.append(dict(id=meta["id"], frame=RG.frame_of(meta["center"]), res=float(meta["res_km"]), nx=int(meta["nx"]),
                        ny=int(meta["ny"]), h=h, ice=ice, land=np.asarray(raw["water"]) != 1, section=meta.get("section"),
                        size_km=float(meta["size_km"]), center=meta["center"],
                        layers={k: np.asarray(raw[k]) for k in want if k in CATEGORICAL}))
    return out


def source_of(z: dict, zid: str = "mem", section: str | None = None) -> dict:
    """A built (unsaved) zoom, regional.build's result, as a source to match (tests, diagnostics); its height is the
    ground (the bed under a glacier) and the ice's thickness apart."""
    L = z["layers"]
    return dict(id=zid, frame=z["frame"], res=float(z["res"]), nx=int(z["nx"]), ny=int(z["ny"]),
                h=np.asarray(L["elevation"], np.float32),
                ice=np.asarray(L["ice"], np.float32) if "ice" in L else np.zeros(np.shape(L["elevation"]), np.float32), land=np.asarray(L["water"]) != 1, section=section,
                size_km=float(z["nx"] * z["res"]), center=None,
                layers={k: np.asarray(L[k]) for k in CATEGORICAL if k in L})


# the layers that switch (not blend) across the ramp: classes, not quantities
CATEGORICAL = ("biome", "landform", "vegetation", "land_cover", "surface_rock", "soil")


def _owner(ctx, srcs) -> np.ndarray:
    """Index of each pixel's owner: -1 this section, k the k-th neighbour."""
    P = ctx.P
    secs = [s["section"] for s in srcs]
    if getattr(ctx, "section", None) and all(secs):
        from . import tiling as ZT
        n = ZT.choose_n(ctx.size_in)
        f, i, j = ZT.locate(P, n)
        names = np.array(list(ZT.FACES))
        cell = np.char.add(np.char.add(np.char.add(names[f], "."), i.astype(str)), np.char.add(".", j.astype(str)))
        own = np.full(len(P), -1)
        for k, s in enumerate(secs):
            own[cell == s] = k
        return own
    C = np.stack([ctx.fr.c] + [s["frame"].c for s in srcs])
    k = np.argmax(P @ C.T, axis=1)
    return k - 1


def _sample(s, P, ctx_res):
    """A neighbour's height (bilinear), land and categorical layers (nearest) at points P, and how far (km) inside its
    usable square each point is (negative: outside)."""
    x, y = s["frame"].to_plane(P)
    r = s["ny"] / 2 - y / s["res"] - 0.5
    c = x / s["res"] + s["nx"] / 2 - 0.5
    lim_r, lim_c = s["ny"] - 1 - VALID_PX, s["nx"] - 1 - VALID_PX
    inside = np.minimum(np.minimum(r - VALID_PX, lim_r - r), np.minimum(c - VALID_PX, lim_c - c)) * s["res"]
    r0 = np.clip(np.floor(r).astype(int), 0, s["ny"] - 2)
    c0 = np.clip(np.floor(c).astype(int), 0, s["nx"] - 2)
    fr, fc = np.clip(r - r0, 0, 1), np.clip(c - c0, 0, 1)
    def bil(h):
        return (h[r0, c0] * (1 - fr) * (1 - fc) + h[r0, c0 + 1] * (1 - fr) * fc + h[r0 + 1, c0] * fr * (1 - fc)
                + h[r0 + 1, c0 + 1] * fr * fc)
    ri = np.clip(np.rint(r).astype(int), 0, s["ny"] - 1)
    ci = np.clip(np.rint(c).astype(int), 0, s["nx"] - 1)
    return bil(s["h"]), bil(s["ice"]), s["land"][ri, ci], {k: v[ri, ci] for k, v in s["layers"].items()}, inside


def prepare(ctx) -> None:
    """Ownership and blend weights on this zoom's pixels (ctx.match: the neighbour sources, or None). Sets ctx.m_w
    (the neighbour's weight: 1 where it owns the ground, falling to 0 across the ramp), ctx.m_pin (held: w = 1),
    ctx.m_h, ctx.m_land, ctx.m_cat (the neighbours' fields, blended where several meet) and ctx.m_dist (km into own
    ground)."""
    srcs = ctx.match
    n = ctx.npx
    own = _owner(ctx, srcs)
    mine = own < 0
    dist = ZK.inside_distance(mine, ctx.nx, ctx.ny, False) * ctx.res  # km into this section's own ground
    W = np.zeros(n)
    Hs = np.zeros(n)
    Is = np.zeros(n)
    Ls = np.zeros(n)
    cats: dict = {}
    best = np.full(n, -1.0)
    for k, s in enumerate(srcs):
        hv, iv, lv, cv, inside = _sample(s, ctx.P, ctx.res)
        fade = smoothstep(0.0, FADE_KM, inside)  # (0 outside its usable square)
        # its weight: 1 on its own ground, falling across our ramp; nothing where a third section owns the ground
        mine_or_its = mine | (own == k)
        w = np.where(own == k, 1.0, np.where(mine, 1.0 - smoothstep(0.0, RAMP_KM, dist), 0.0)) * fade * mine_or_its
        # (several neighbours: near a corner each weighs by its own ramp; the strongest's classes win)
        W += w
        Hs += w * hv
        Is += w * iv
        Ls += w * lv
        for key, v in cv.items():
            cats.setdefault(key, np.zeros(n, v.dtype))
            cats[key] = np.where(w > best, v, cats[key])
        best = np.maximum(best, w)
    ctx.m_w = np.clip(W, 0.0, 1.0)
    ctx.m_h = np.where(W > 0, Hs / np.maximum(W, 1e-9), 0.0)
    ctx.m_ice = np.where(W > 0, Is / np.maximum(W, 1e-9), 0.0)
    ctx.m_land = np.where(W > 0, Ls / np.maximum(W, 1e-9), 0.0) >= 0.5
    ctx.m_cat = cats
    ctx.m_dist = dist
    ctx.m_pin = (~mine) & (ctx.m_w > 0.999)
    ctx.log(f"  matched to {', '.join(s['id'] for s in srcs)}: {ctx.m_pin.mean():.1%} of the pixels held, "
            f"{((ctx.m_w > 0) & mine).mean():.1%} in the ramp")


def coast(ctx) -> None:
    """In the coastline, before land is read off the indicator: the neighbour's land and sea where its weight is over a
    half (held ground and the outer half of the ramp): one coastline, the neighbour's, up to the middle of the ramp.
    A pixel that disagrees gets a just-land or just-sea indicator (a low shore: the base surface follows it)."""
    flip = (ctx.m_w >= 0.5) & (ctx.m_land != (ctx.ind_n > 0))
    ctx.ind_n = np.where(flip, np.where(ctx.m_land, 0.05, -0.05), ctx.ind_n)


def hold(ctx) -> None:
    """Before the landscape pass: the held ground at the neighbour's heights (the target there), and an outlet of
    the pass, as the region's edge."""
    pin = ctx.m_pin & ctx.land
    ctx.h = np.where(pin, ctx.m_h, ctx.h)


def hold_edge(ctx) -> None:
    """The held ground joins the region's edge: an outlet, not graded (first_glaciers, after the edge is drawn)."""
    ctx.edge = ctx.edge | (ctx.m_pin & ctx.land)
    ctx.outlet = ctx.sea | ctx.edge


def blend(ctx) -> None:
    """After the landscape pass: the ramp's heights from the neighbour's to this section's own, on land both call
    land (the coast was matched already)."""
    w = np.where(ctx.land & ctx.m_land & (ctx.m_w > 0), ctx.m_w, 0.0)  # (not towards the neighbour's sea floor)
    ctx.h = np.where(w > 0, np.maximum(w * ctx.m_h + (1 - w) * ctx.h, 0.5), ctx.h)  # (land stays above the sea)


def final(ctx) -> None:
    """After the ice's bed (the last change to the ground, on the region's pixels): the ground and the ice blended
    once more, to the neighbour's outright where it owns the ground: the landscape pass ran on the neighbour's ground,
    but the falls, the glaciers redrawn on the finished valleys and the bed sunk under them are this section's own."""
    reg = ctx.region
    w = np.where(ctx.land & ctx.m_land[reg], ctx.m_w[reg], 0.0)
    on = w > 0
    ctx.h = np.where(on, w * ctx.m_h[reg] + (1 - w) * ctx.h, ctx.h)
    ctx.h = np.where(on & ~ctx.glacier & (ctx.h < 0.5), 0.5, ctx.h)  # (bare land above the sea; a bed under ice may not be)
    ice = w * ctx.m_ice[reg] + (1 - w) * np.where(ctx.glacier, ctx.ice_th, 0.0)
    ctx.glacier = np.where(on, ice >= 1.0, ctx.glacier)
    ctx.ice_th = np.where(on, ice, ctx.ice_th)


def categorical(ctx, layers: dict) -> None:
    """The class layers switch from the neighbour's to this section's at a ragged line across the ramp: a place takes
    the neighbour's class where its weight beats place-keyed noise (no straight seam, no speckle)."""
    if not ctx.m_cat:
        return
    reg = ctx.region
    nz = ZK.fbm(ctx.Pk, 25.0, 3, 0.5, ctx.S + 1301) / 0.17  # (ctx.Pk is cropped to the region by now)
    thr = np.clip(0.5 + 0.18 * nz, 0.05, 0.95)
    take = ctx.m_w[reg] > thr
    for k, v in ctx.m_cat.items():
        if k in layers:
            a = np.asarray(layers[k])
            flat = a.reshape(-1).copy()
            flat[take] = v[reg][take].astype(a.dtype)
            layers[k] = flat.reshape(a.shape)
