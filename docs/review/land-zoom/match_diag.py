"""Matched-pair check: A alone, B alone, B matched to A (in memory); seam numbers at the owner line (the bisector).

  uv run python diag2.py WORLD LATA LONA LATB LONB SIZE RES
"""
import json
import sys
import time

import numpy as np

from planet import world as W
from planet.geo import R_KM
from planet.zoom import match as ZM
from planet.zoom import regional as RG

q = lambda *a: None  # noqa: E731


def samp(z, P):
    fr, res, nx, ny = z["frame"], z["res"], z["nx"], z["ny"]
    x, y = fr.to_plane(P)
    r = ny / 2 - y / res - 0.5
    c = x / res + nx / 2 - 0.5
    ok = (r >= 1) & (r <= ny - 2) & (c >= 1) & (c <= nx - 2)
    r0 = np.clip(np.floor(r).astype(int), 0, ny - 2)
    c0 = np.clip(np.floor(c).astype(int), 0, nx - 2)
    a, b = np.clip(r - r0, 0, 1), np.clip(c - c0, 0, 1)
    h = np.asarray(z["layers"]["elevation"], float)
    hv = h[r0, c0] * (1 - a) * (1 - b) + h[r0, c0 + 1] * (1 - a) * b + h[r0 + 1, c0] * a * (1 - b) + h[r0 + 1, c0 + 1] * a * b
    ri, ci = np.clip(np.rint(r).astype(int), 0, ny - 1), np.clip(np.rint(c).astype(int), 0, nx - 1)
    gy, gx = np.gradient(h, res * 1000.0)
    sl = np.degrees(np.arctan(np.hypot(gx, gy)))[ri, ci]
    L = z["layers"]
    return dict(ok=ok, h=hv, land=np.asarray(L["water"])[ri, ci] == 0, slope=sl, biome=np.asarray(L["biome"])[ri, ci])


def main():
    wref, la, loa, lb, lob, size, res = sys.argv[1], *map(float, sys.argv[2:8])
    world = W.load(RG.find_world(wref))
    t = time.time()
    za = RG.build(world, la, loa, size, res, 1, 15, log=q)
    zb = RG.build(world, lb, lob, size, res, 1, 15, log=q)
    zm = RG.build(world, lb, lob, size, res, 1, 15, log=print, match=[ZM.source_of(za, "A")])
    print(f"built in {time.time() - t:.0f}s", file=sys.stderr)
    a, b = za["frame"].c, zb["frame"].c
    u = (b - a) / np.linalg.norm(b - a)
    half = size / 2
    xs = np.arange(-half, half, res * 0.5)
    X, Y = np.meshgrid(xs, xs)
    P = zb["frame"].to_sphere(X.ravel(), Y.ravel())
    d = np.arcsin(np.clip(P @ u, -1, 1)) * R_KM  # + into B's ground
    A, B, M = samp(za, P), samp(zb, P), samp(zm, P)
    out = {}

    def stat(S1, S2, sel):
        k = sel & S1["ok"] & S2["ok"]
        both = k & S1["land"] & S2["land"]
        dh = np.abs(S1["h"] - S2["h"])[both]
        return dict(n=int(k.sum()), dh_med=round(float(np.median(dh)), 1) if len(dh) else None,
                    dh_p95=round(float(np.percentile(dh, 95)), 1) if len(dh) else None,
                    coast=round(float((S1["land"] != S2["land"])[k].mean()), 4) if k.any() else None,
                    biome=round(float((S1["biome"] != S2["biome"])[both].mean()), 3) if len(dh) else None)
    line = np.abs(d) < 2.5
    out["alone@line"] = stat(A, B, line)
    out["matched@line"] = stat(A, M, line)
    out["matched@-50"] = stat(A, M, np.abs(d + 50) < 2.5)
    out["matched@+40"] = stat(A, M, np.abs(d - 40) < 2.5)
    out["B moved, d 100-300"] = stat(B, M, (d > 100) & (d < 300))
    out["B moved, d > 600"] = stat(B, M, d > 600)
    for nm, S1 in (("alone", B), ("matched", M)):
        for lab, sel in (("ramp 0-80", (d > 0) & (d < 80)), ("inside 120-400", (d > 120) & (d < 400))):
            k = sel & S1["ok"] & S1["land"]
            out[f"slope p95 {nm} {lab}"] = round(float(np.percentile(S1["slope"][k], 95)), 2) if k.any() else None
    for k, v in out.items():
        print(f"{k:32s} {json.dumps(v)}")


if __name__ == "__main__":
    main()
