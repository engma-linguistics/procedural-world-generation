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
from . import regional as RG

RAMP_KM = 80.0  # the blend's width inside the section's own ground (the tiling's least margin is ~97 km)
VALID_PX = 3  # a neighbour's pixels this near its own edge aren't used (its bilinear sampling needs a pixel round)
ACCEPT_M3S = 10.0  # the least stream of the neighbour's coming in from this section's ground that this one's water may join
FADE_KM = 20.0  # ... and its weight fades to 0 over this much before them, so a ramp never ends in a step


def sources(refs) -> list[dict]:
    """The saved zooms to match, as {id, frame, res, nx, ny, h (the ground: the bed under a glacier), ice (m), land, section,
    center, layers (categorical, 2D)}."""
    out = []
    for ref in refs:
        d = S.find_zoom(ref)
        meta = json.loads((d / "zoom.json").read_text())
        want = [k for k in ("elevation", "water", "ice", "lake_depth", "discharge", "receiver", *CATEGORICAL)
                if k in meta["layers"]]
        raw = S.read_layers(d, meta["layers"], want)
        h = S.decode(np.asarray(raw["elevation"]), meta["layers"]["elevation"]).astype(np.float32)
        if "lake_depth" in raw:
            h = _lake_surface(h, np.asarray(raw["water"]),
                              S.decode(np.asarray(raw["lake_depth"]), meta["layers"]["lake_depth"]))
        ice = (S.decode(np.asarray(raw["ice"]), meta["layers"]["ice"]).astype(np.float32) if "ice" in raw
               else np.zeros_like(h))
        out.append(dict(id=meta["id"], frame=RG.frame_of(meta["center"]), res=float(meta["res_km"]), nx=int(meta["nx"]),
                        ny=int(meta["ny"]), h=h, ice=ice, land=np.asarray(raw["water"]) != 1, lake=np.asarray(raw["water"]) == 2, section=meta.get("section"),
                        size_km=float(meta["size_km"]), center=meta["center"],
                        layers={k: np.asarray(raw[k]) for k in want if k in CATEGORICAL},
                        **_network(raw.get("discharge"), raw.get("receiver"), meta["layers"].get("discharge"))))
    return out


def source_of(z: dict, zid: str = "mem", section: str | None = None) -> dict:
    """A built (unsaved) zoom, regional.build's result, as a source to match (tests, diagnostics); its height is the
    ground (the bed under a glacier) and the ice's thickness apart."""
    L = z["layers"]
    h = np.asarray(L["elevation"], np.float32)
    if "lake_depth" in L:
        h = _lake_surface(h, np.asarray(L["water"]), np.asarray(L["lake_depth"]))
    return dict(id=zid, frame=z["frame"], res=float(z["res"]), nx=int(z["nx"]), ny=int(z["ny"]),
                h=h,
                ice=np.asarray(L["ice"], np.float32) if "ice" in L else np.zeros(np.shape(L["elevation"]), np.float32), land=np.asarray(L["water"]) != 1, lake=np.asarray(L["water"]) == 2, section=section,
                size_km=float(z["nx"] * z["res"]), center=None,
                layers={k: np.asarray(L[k]) for k in CATEGORICAL if k in L},
                **_network(L.get("discharge"), L.get("receiver"), None))


def _network(q, slots, spec) -> dict:
    """A neighbour's drainage: discharge (m3/s) and receivers (pixel index, -1 none) from its D8 slot layer."""
    if q is None or slots is None:
        return dict(q=None, rec=None)
    q = np.asarray(q)
    q = (S.decode(q, spec) if spec is not None else q).astype(np.float32).ravel()
    sl = np.asarray(slots).ravel().astype(np.int64)
    nx = np.asarray(slots).shape[1]
    t = sl + (sl >= 4)  # (slot 3 * (dr + 1) + (dc + 1), the centre skipped: regional.d8_slots)
    rec = np.where(sl == RG.D8_NONE, -1, np.arange(len(sl)) + (t // 3 - 1) * nx + (t % 3 - 1))
    return dict(q=q, rec=rec)


def _lake_surface(h, water, depth) -> np.ndarray:
    """The neighbour's ground with its lakes at their surface (the elevation layer is a lake's bed): held ground is
    land here (lakes count as land), and a lake's bed held as bare ground was a pit, below the sea at times (a bare
    pixel below the sea broke the vegetation's land test)."""
    return np.where(water == 2, h + np.nan_to_num(np.asarray(depth, np.float32)), h).astype(np.float32)


# the layers that switch (not blend) across the ramp: classes, not quantities
CATEGORICAL = ("biome", "landform", "vegetation", "land_cover", "surface_rock", "soil")


def _owner(ctx, srcs, P=None) -> np.ndarray:
    """Index of the owner of each pixel (or of points P): -1 this section, k the k-th neighbour."""
    P = ctx.P if P is None else P
    secs = [s["section"] for s in srcs]
    if getattr(ctx, "section", None) and all(secs):
        from . import tiling as ZT
        n = ZT.choose_n(ctx.size_in, 190.0)  # (as tiling.section builds them: its default least overlap)
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
    return bil(s["h"]), bil(s["ice"]), s["land"][ri, ci], s["lake"][ri, ci], {k: v[ri, ci] for k, v in s["layers"].items()}, inside


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
    Ks = np.zeros(n)
    cats: dict = {}
    best = np.full(n, -1.0)
    for k, s in enumerate(srcs):
        hv, iv, lv, kv, cv, inside = _sample(s, ctx.P, ctx.res)
        fade = smoothstep(0.0, FADE_KM, inside)  # (0 outside its usable square)
        # its weight: 1 on its own ground, falling across our ramp; nothing where a third section owns the ground
        mine_or_its = mine | (own == k)
        w = np.where(own == k, 1.0, np.where(mine, 1.0 - smoothstep(0.0, RAMP_KM, dist), 0.0)) * fade * mine_or_its
        # (several neighbours: near a corner each weighs by its own ramp; the strongest's classes win)
        W += w
        Hs += w * hv
        Is += w * iv
        Ls += w * lv
        Ks += w * kv
        for key, v in cv.items():
            cats.setdefault(key, np.zeros(n, v.dtype))
            cats[key] = np.where(w > best, v, cats[key])
        best = np.maximum(best, w)
    ctx.m_w = np.clip(W, 0.0, 1.0)
    ctx.m_h = np.where(W > 0, Hs / np.maximum(W, 1e-9), 0.0)
    ctx.m_ice = np.where(W > 0, Is / np.maximum(W, 1e-9), 0.0)
    ctx.m_land = np.where(W > 0, Ls / np.maximum(W, 1e-9), 0.0) >= 0.5
    ctx.m_lake = np.where(W > 0, Ks / np.maximum(W, 1e-9), 0.0) >= 0.5  # (its lakes: land in m_land)
    ctx.m_cat = cats
    ctx.m_dist = dist
    ctx.m_mine = mine
    ctx.m_pin = (~mine) & (ctx.m_w > 0.999)
    ctx.log(f"  matched to {', '.join(s['id'] for s in srcs)}: {ctx.m_pin.mean():.1%} of the pixels held, "
            f"{((ctx.m_w > 0) & mine).mean():.1%} in the ramp")


def coast(ctx) -> None:
    """In the coastline, before land is read off the indicator: the neighbour's land and sea where its weight is over a
    half (held ground and the outer half of the ramp): one coastline, the neighbour's, up to the middle of the ramp.
    A pixel that disagrees gets a just-land or just-sea indicator (a low shore: the base surface follows it)."""
    flip = (ctx.m_w >= 0.5) & (ctx.m_land != (ctx.ind_n > 0))
    ctx.ind_n = np.where(flip, np.where(ctx.m_land, 0.05, -0.05), ctx.ind_n)


def lakes(ctx, cand: np.ndarray) -> np.ndarray:
    """The lake outlines: the neighbour's where its weight is over a half, as the coastline (coast()). Its lakes were
    land to this section's coastline and held ground isn't a lake candidate (an outlet, as the region's edge), so the
    neighbour's lakes there and near the line were dry ground in this section, the only coast mismatch left at the
    owner line on lane 128's practice pairs. Same coarse lakes, same levels: the held surface is the lake's."""
    z = ctx.m_w >= 0.5
    frame = ctx.edge & ~ctx.m_pin  # (the square's own edge stays no lake)
    # (this section's first glacier outline gives way to the neighbour's lake: the ice there is the neighbour's, final())
    ctx.glacier = ctx.glacier & ~(z & ctx.m_lake & ~frame)
    return np.where(z, ctx.m_lake & ctx.land & ~frame, cand)


def inflows(ctx) -> None:
    """After the coarse rivers' inflow: the water the neighbour's rivers carry across the owner line into this
    section's ground, handed on (PW-1302). The held ground is an outlet, so without it a river flowing from the
    neighbour's ground into this one started dry at the line (lane 128's pairs: 0 of 53 crossings carried on, e.g.
    a 95,000 m3/s river arriving at 0). From the neighbour's own network (its `receiver` layer): every pixel it owns
    whose receiver this section owns passes its discharge to this section's pixel where that receiver lies (the
    nearest of its own land pixels round it, if the lattices' offset puts it on held ground or the sea). The
    river's course from there is this section's own routing, on ground that at the line is the neighbour's.
    Also ctx.m_accept: the held pixels where the neighbour's rivers enter its ground from this section's (walls()
    keeps those, and only those, open to this section's water)."""
    n_in, q_in = 0, 0.0
    nx, ny, res = ctx.nx, ctx.ny, ctx.res
    ok = ctx.m_mine & ~ctx.m_pin & ctx.land
    ctx.m_accept = np.zeros(ctx.npx, bool)
    for k, s in enumerate(ctx.match):
        if s["q"] is None:
            continue
        nxs, nys = s["nx"], s["ny"]
        cand = np.flatnonzero((s["rec"] >= 0) & (s["q"] > 0) & s["land"].ravel())
        if not len(cand):
            continue
        rr, cc = np.divmod(cand, nxs)
        X = (cc + 0.5 - nxs / 2) * s["res"]
        Y = (nys / 2 - rr - 0.5) * s["res"]
        own_p = _owner(ctx, ctx.match, s["frame"].to_sphere(X, Y))
        # its pixels on this section's ground whose receiver it owns: where its rivers (a stream at least) enter its
        # ground from ours
        back = cand[(own_p == -1) & (s["q"][cand] >= ACCEPT_M3S)]
        rr, cc = np.divmod(s["rec"][back], nxs)
        Pb = s["frame"].to_sphere((cc + 0.5 - nxs / 2) * s["res"], (nys / 2 - rr - 0.5) * s["res"])
        Pb = Pb[_owner(ctx, ctx.match, Pb) == k]
        x, y = ctx.fr.to_plane(Pb)
        col = np.floor(x / res + nx / 2).astype(int)
        row = np.floor(ny / 2 - y / res).astype(int)
        on = (col >= 0) & (col < nx) & (row >= 0) & (row < ny)
        ctx.m_accept[row[on] * nx + col[on]] = True
        cand = cand[own_p == k]  # (the pixels it owns)
        r = s["rec"][cand]
        rr, cc = np.divmod(r, nxs)
        Pr = s["frame"].to_sphere((cc + 0.5 - nxs / 2) * s["res"], (nys / 2 - rr - 0.5) * s["res"])
        cross = _owner(ctx, ctx.match, Pr) == -1  # (whose receiver this section owns)
        p, Pr = cand[cross], Pr[cross]
        x, y = ctx.fr.to_plane(Pr)
        col = np.floor(x / res + nx / 2).astype(int)
        row = np.floor(ny / 2 - y / res).astype(int)
        on = (col >= 3) & (col < nx - 3) & (row >= 3) & (row < ny - 3)
        for pk, r0, c0 in zip(p[on], row[on], col[on]):
            b = r0 * nx + c0
            if not ok[b]:  # (onto the nearest of this section's own land pixels, within 2)
                dr, dc = np.mgrid[-2:3, -2:3]
                rr_, cc_ = r0 + dr.ravel(), c0 + dc.ravel()
                bb = rr_ * nx + cc_
                good = ok[bb]
                if not good.any():
                    continue
                b = int(bb[good][np.argmin((dr.ravel() ** 2 + dc.ravel() ** 2)[good])])
            ctx.inflow[b] += float(s["q"][pk]) / RG.KM2_M_PER_YR_TO_M3S
            n_in += 1
            q_in += float(s["q"][pk])
    ctx.log(f"  {n_in} crossings of the owner line hand on {q_in:,.0f} m3/s from the neighbours' rivers")


def basin_lakes(ctx) -> None:
    """The landform lakes and ponds (final drainage) keep to the neighbour's lake outline where its weight is over a
    half, as the lakes do (lakes()): a basin on the ramp that fills to the brim with a river handed on (inflows())
    made a lake at the line where the neighbour has land (lane 129, ice range pair: 6 of 402 line pixels). Where one
    goes, the ground stands at its surface."""
    drop = ctx.lf_lake & (ctx.m_w >= 0.5) & ~ctx.m_lake
    if drop.any():
        ctx.h = np.where(drop, ctx.h + ctx.lake_depth, ctx.h)
        ctx.lake_depth = np.where(drop, 0.0, ctx.lake_depth)
        ctx.lf_lake = ctx.lf_lake & ~drop


def walls(ctx) -> np.ndarray:
    """The held pixels next to this section's own ground that its water may not enter (PW-1302): all but where the
    neighbour's own network has a river coming in from this side (ctx.m_accept). Held ground is an outlet of the
    landscape pass (the valleys are graded down to the neighbour's levels), but in the final drainage an outlet all
    along the line let a river handed on by inflows() run straight back into held ground beside where it came in
    (lane 129's first try: a 95,000 m3/s river handed on, 104,000 m3/s run back out at the next pixels): water
    crosses the line only where the neighbour, whose ground the mosaic shows there, has it cross."""
    held = ctx.m_pin & ctx.land & ~ctx.lake & ~ctx.sea
    own = (ctx.m_mine & ~ctx.m_pin).reshape(ctx.ny, ctx.nx)
    near = RG._dilate(own, 1).ravel()
    return held & near & ~ctx.m_accept


def hold(ctx) -> None:
    """Before the landscape pass: the held ground at the neighbour's heights (the target there), and an outlet of
    the pass, as the region's edge."""
    pin = ctx.m_pin & ctx.land
    # (bare held ground above the sea: where the neighbour has no ice its ground is above it, but for a closed
    # basin's lake below sea level; under its ice the bed may lie below, and is held as it is)
    ctx.h = np.where(pin, np.where(ctx.m_ice >= 1.0, ctx.m_h, np.maximum(ctx.m_h, 0.5)), ctx.h)


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
    ice = w * ctx.m_ice[reg] + (1 - w) * np.where(ctx.glacier, ctx.ice_th, 0.0)
    ctx.glacier = np.where(on, ice >= 1.0, ctx.glacier)
    ctx.ice_th = np.where(on, ice, ctx.ice_th)
    # (bare land above the sea, on the blended glacier outline: a bed under ice may not be)
    ctx.h = np.where(on & ~ctx.glacier & (ctx.h < 0.5), 0.5, ctx.h)


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
