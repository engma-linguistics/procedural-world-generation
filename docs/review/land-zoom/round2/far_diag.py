"""Why does test_zoom_match's matched B differ from B alone far inside? Build the test's synthetic pair, snapshot the
height after every stage of B alone and B matched (same frame: compare pixel by pixel), report median |dh| on land by
distance from the owner line. Also: the share of far pixels whose final drainage ends in held ground."""
import sys

import numpy as np

sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-ab77e24b7280d80be")
sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-ab77e24b7280d80be/docs/review/land-zoom")
import stage_diag as SD  # noqa: E402  (hooks every stage, snapshots into SD.SNAP)

from planet import world as W  # noqa: E402
from planet.geo import R_KM, xyz  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.zoom import match as ZM  # noqa: E402
from planet.zoom import regional as RG  # noqa: E402

level = int(sys.argv[1]) if len(sys.argv) > 1 else 5
size = float(sys.argv[2]) if len(sys.argv) > 2 else 700.0
res = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
dlon = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
g = build_grid(level)
c = xyz(np.radians(38.0), np.radians(10.0))
d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
ridge = np.arccos(np.clip(g.centers @ xyz(np.radians(39.0), np.radians(10.0)), -1, 1)) * R_KM
elev = np.where(d < 2200, 250 + 0.3 * (2200 - d) + 2500 * np.exp(-(ridge / 300) ** 2), -3000.0)
extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(elev > 0, 0.2, 6.0)}
world = W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": level}, erosion=0.0)
q = dict(size_km=size, res_km=res, iterations=6, log=lambda *a: None)
A_C, B_C = (38.0, 10.0 - dlon / 2), (38.0, 10.0 + dlon / 2)
za = RG.build(world, *A_C, **q)
SD.SNAP.clear()
zb = RG.build(world, *B_C, **q)
sb = {k: v for k, v in SD.SNAP.items()}
SD.SNAP.clear()
zm = RG.build(world, *B_C, **q, match=[ZM.source_of(za, "A")])
sm = {k: v for k, v in SD.SNAP.items()}
a, b = za["frame"].c, zb["frame"].c
u = (b - a) / np.linalg.norm(b - a)


def dist_of(nx, ny, r):
    xs = (np.arange(nx) + 0.5 - nx / 2) * r
    ys = (ny / 2 - np.arange(ny) - 0.5) * r
    X, Y = np.meshgrid(xs, ys)
    P = zb["frame"].to_sphere(X.ravel(), Y.ravel())
    return (np.arcsin(np.clip(P @ u, -1, 1)) * R_KM).reshape(ny, nx)


bands = [(0, 80), (80, 160), (160, 240), (240, 320), (320, 400), (400, 600)]
print("level", level, "size", size, "res", res, "centres", A_C, B_C)
print(f"{'stage':28s}" + "".join(f"{f'{lo}-{hi}':>12s}" for lo, hi in bands))
for name in sb:
    if name not in sm:
        continue
    h1, h2 = sb[name]["h"], sm[name]["h"]
    if h1.shape != h2.shape:
        continue
    dd = dist_of(sb[name]["nx"], sb[name]["ny"], sb[name]["res"])
    land = sb[name].get("land", h1 > 0) & sm[name].get("land", h2 > 0)
    row = []
    for lo, hi in bands:
        k = land & (dd >= lo) & (dd < hi)
        row.append(f"{np.median(np.abs(h1 - h2)[k]):12.2f}" if k.sum() > 20 else f"{'-':>12s}")
    print(f"{name:28s}" + "".join(row))
e1, e2 = np.asarray(zb["layers"]["elevation"]), np.asarray(zm["layers"]["elevation"])
dd = dist_of(zb["nx"], zb["ny"], zb["res"])
land = (np.asarray(zb["layers"]["water"]) != 1) & (np.asarray(zm["layers"]["water"]) != 1)
print("final elevation layer:", "".join(f"{np.median(np.abs(e1 - e2)[land & (dd >= lo) & (dd < hi)]):10.2f}"
                                        if (land & (dd >= lo) & (dd < hi)).sum() > 20 else "    -" for lo, hi in bands))
print("land fraction 0-600:", round(float(land[(dd > 0) & (dd < 600)].mean()), 3), "B half-width", size / 2,
      "B centre at d =", round(float(np.arcsin(b @ u) * R_KM), 1))
