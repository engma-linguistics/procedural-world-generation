"""Stage-by-stage seam attribution: build two overlapping zooms with a snapshot of ctx.h / ctx.land after every stage,
then compare them at shared sphere points in the overlap band.

  uv run python diag.py LATA LONA LATB LONB SIZE RES [--up-a deg] [--up-b deg] [--out file.json]
"""
import argparse
import json
import sys
import time

import numpy as np

from planet import world as W
from planet.zoom import regional as RG
from planet.zoom import stage_finish as STG_F
from planet.zoom import stage_landscape as STG_L
from planet.zoom import stage_rivers as STG_R
from planet.zoom import stage_terrain as STG_T

STAGES = [(STG_T, n) for n in ("frame_and_grid", "coarse_fields", "delta_plains", "coastline", "detail",
                               "mean_correction", "volcanoes", "tides_and_flats", "landform_classes")] + \
         [(STG_R, n) for n in ("coarse_rivers", "categorical_layers")] + \
         [(STG_L, n) for n in ("first_glaciers", "lakes", "drainage_tools", "fit_setup", "landscape_loop",
                               "final_drainage", "shoreface")] + \
         [(STG_F, n) for n in ("crop_halo", "climate_on_terrain", "vegetation_layers", "coastal_life", "ice_bed")]
SNAP = {}


def hook(mod, name):
    f = getattr(mod, name)

    def g(ctx):
        t = time.time()
        f(ctx)
        h = getattr(ctx, "h", None)
        if h is not None and getattr(ctx, "nx", None):
            s = dict(h=np.array(h, np.float32).reshape(ctx.ny, ctx.nx), nx=ctx.nx, ny=ctx.ny, res=ctx.res,
                     dt=time.time() - t)
            land = getattr(ctx, "land", None)
            if land is not None and np.size(land) == ctx.nx * ctx.ny:
                s["land"] = np.asarray(land).reshape(ctx.ny, ctx.nx).copy()
            SNAP[name] = s
    setattr(mod, name, g)


for m, n in STAGES:
    hook(m, n)


def sample(fr, s, P):
    x, y = fr.to_plane(P)
    r = s["ny"] / 2 - y / s["res"] - 0.5
    c = x / s["res"] + s["nx"] / 2 - 0.5
    ok = (r >= 1) & (r <= s["ny"] - 2) & (c >= 1) & (c <= s["nx"] - 2)
    r0 = np.clip(np.floor(r).astype(int), 0, s["ny"] - 2)
    c0 = np.clip(np.floor(c).astype(int), 0, s["nx"] - 2)
    fr_, fc = np.clip(r - r0, 0, 1), np.clip(c - c0, 0, 1)
    h = s["h"]
    v = (h[r0, c0] * (1 - fr_) * (1 - fc) + h[r0, c0 + 1] * (1 - fr_) * fc + h[r0 + 1, c0] * fr_ * (1 - fc)
         + h[r0 + 1, c0 + 1] * fr_ * fc)
    land = s["land"][np.clip(np.rint(r).astype(int), 0, s["ny"] - 1), np.clip(np.rint(c).astype(int), 0, s["nx"] - 1)] \
        if "land" in s else None
    return ok, v, land


def run(world, lat, lon, size, res, up, it):
    SNAP.clear()
    z = RG.build(world, lat, lon, size, res, 1, it, log=lambda *a: None, up=RG.up_of(lat, lon, up))
    return z["frame"], dict(SNAP), z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("world")
    ap.add_argument("la", type=float); ap.add_argument("loa", type=float)
    ap.add_argument("lb", type=float); ap.add_argument("lob", type=float)
    ap.add_argument("size", type=float); ap.add_argument("res", type=float)
    ap.add_argument("--up-a", type=float, default=None); ap.add_argument("--up-b", type=float, default=None)
    ap.add_argument("--it", type=int, default=15)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    world = W.load(RG.find_world(a.world))
    t = time.time()
    fa, SA, za = run(world, a.la, a.loa, a.size, a.res, a.up_a, a.it)
    fb, SB, zb = run(world, a.lb, a.lob, a.size, a.res, a.up_b, a.it)
    print(f"built in {time.time() - t:.0f}s", file=sys.stderr)
    # points: a lattice over A's (final, cropped) square; keep those inside both final squares
    half = a.size / 2
    xs = np.arange(-half, half, a.res * 0.5)
    X, Y = np.meshgrid(xs, xs)
    P = fa.to_sphere(X.ravel(), Y.ravel())
    out = {}
    fin = SA["ice_bed"]
    okA, _, _ = sample(fa, fin, P)
    okB, _, _ = sample(fb, SB["ice_bed"], P)
    # signed distance to B's square edge (km, inside B positive) -> band position
    xb, yb = fb.to_plane(P)
    dB = half - np.maximum(np.abs(xb), np.abs(yb))
    dA = half - np.maximum(np.abs(X.ravel()), np.abs(Y.ravel()))
    band = okA & okB
    print("overlap pts", band.sum(), file=sys.stderr)
    for m, n in STAGES:
        if n not in SA or n not in SB:
            continue
        o1, v1, l1 = sample(fa, SA[n], P)
        o2, v2, l2 = sample(fb, SB[n], P)
        k = band & o1 & o2
        both = k if l1 is None or l2 is None else k & l1 & l2
        dh = np.abs(v1 - v2)[both]
        row = {"n": int(both.sum()), "dh_med": float(np.median(dh)) if len(dh) else None,
               "dh_p95": float(np.percentile(dh, 95)) if len(dh) else None,
               "dt_a": round(SA[n]["dt"], 1)}
        if l1 is not None and l2 is not None:
            row["coast_mis"] = float((l1 != l2)[k].mean())
        # by distance from the nearer own edge: < 40 km vs > 60 km
        near = np.minimum(dA, dB)
        for lab, sel in (("edge<40", near < 40), ("in>60", near > 60)):
            s2 = both & sel
            row[lab] = float(np.median(np.abs(v1 - v2)[s2])) if s2.sum() > 10 else None
        out[n] = row
        print(f"{n:20s} {json.dumps(row)}")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
