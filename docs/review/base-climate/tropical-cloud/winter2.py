"""Lane 131: offline breakdown of the warm land's coldest-month miss (PW-1335) from a screen2.py --save file:
by observed rain band, elevation, latitude; a regression on elevation, the model's rain error and its winter
sunshine error.  uv run python docs/review/base-climate/tropical-cloud/winter2.py SAVE.npz"""
import sys

import numpy as np

z = np.load(sys.argv[1])
g = {k: z[k] for k in z.files}
lat, w, land = g["lat"], g["w"], g["land"].astype(bool)


def wm(x, m):
    m = m & np.isfinite(x)
    return float((x * w)[m].sum() / w[m].sum()) if m.sum() else np.nan


warm = land & (g["oT"] > 18) & (np.abs(lat) < 35)
dc, dm, dw = g["tc"] - g["otc"], g["temp"] - g["oT"], g["tw"] - g["otw"]
print("warm land by obs rain band (all cells): n, dTc, dMAT, dTw, elev, winter sun model/CRU")
for p0, p1 in ((0, 250), (250, 400), (400, 900), (900, 1500), (1500, 9e9)):
    m = warm & (g["oP"] >= p0) & (g["oP"] < p1)
    print(f"  {p0}-{p1}: {m.sum():5d} {wm(dc, m):+5.2f} {wm(dm, m):+5.2f} {wm(dw, m):+5.2f} {wm(g['elev'], m):6.0f}"
          f"  {wm(g['m_ws'], m):.2f}/{wm(g['o_ws'], m):.2f}")
s = warm & (g["oP"] >= 250) & (g["oP"] < 1500)
print("warm semi-arid (obs 250-1500 mm) by elevation: n dTc dMAT dTw")
for e0, e1 in ((-99, 300), (300, 700), (700, 1200), (1200, 9e9)):
    m = s & (g["elev"] >= e0) & (g["elev"] < e1)
    print(f"  {e0}-{e1}: {m.sum():5d} {wm(dc, m):+5.2f} {wm(dm, m):+5.2f} {wm(dw, m):+5.2f}")
print("warm semi-arid by |lat|: n dTc dMAT dTw   obs Tw-Tc  model Tw-Tc")
for a, b in ((0, 10), (10, 20), (20, 30), (30, 35)):
    m = s & (np.abs(lat) >= a) & (np.abs(lat) < b)
    print(f"  {a}-{b}: {m.sum():5d} {wm(dc, m):+5.2f} {wm(dm, m):+5.2f} {wm(dw, m):+5.2f}   "
          f"{wm(g['otw'] - g['otc'], m):5.1f} {wm(g['tw'] - g['tc'], m):5.1f}")
x1 = g["elev"] / 1000
x2 = np.log(np.maximum(g["P"], 50) / np.maximum(g["oP"], 50))
x3 = g["m_ws"] - g["o_ws"]
m = s & np.isfinite(x3) & np.isfinite(dc)
X = np.vstack([x1[m], x2[m], x3[m], np.ones(m.sum())]).T
sw = np.sqrt(w[m])
for name, y in (("dTc", dc), ("dMAT", dm)):
    co = np.linalg.lstsq(X * sw[:, None], y[m] * sw, rcond=None)[0]
    res = y[m] - X @ co
    print(f"  {name} = {co[0]:+.2f} x elev_km {co[1]:+.2f} x ln(P/GPCC) {co[2]:+.2f} x (winter sun m-CRU) "
          f"{co[3]:+.2f}   (resid sd {res.std():.2f}, raw sd {y[m].std():.2f})")
for p0, p1 in ((250, 900), (900, 1500), (1500, 9e9)):
    mm = warm & (np.abs(x2) < 0.3) & (g["elev"] < 300) & (g["oP"] >= p0) & (g["oP"] < p1)
    print(f"  rain right, ground < 300 m, obs {p0}-{p1}: n {mm.sum()} dTc {wm(dc, mm):+.2f} dMAT {wm(dm, mm):+.2f}"
          f" dTw {wm(dw, mm):+.2f}")
print("all ice-free land by |lat| band and elevation: dTc / dMAT / dTw (n)")
for a, b in ((0, 20), (20, 35), (35, 50), (50, 70)):
    row = []
    for e0, e1 in ((-99, 300), (300, 700), (700, 1200), (1200, 2000), (2000, 9e9)):
        m = land & (np.abs(lat) >= a) & (np.abs(lat) < b) & (g["elev"] >= e0) & (g["elev"] < e1)
        row.append(f"{wm(dc, m):+5.1f}/{wm(dm, m):+5.1f}/{wm(dw, m):+5.1f} ({m.sum()})")
    print(f"  {a}-{b}: " + "  ".join(row))
print("PW-1348: summer sunshine excess (model - CRU) on ice-free land 20-40 deg, by the model's annual rain error")
b = land & (np.abs(lat) >= 20) & (np.abs(lat) < 40) & np.isfinite(g["o_ss"])
ex = g["m_ss"] - g["o_ss"]
tot = (w * b).sum()
for lo_, hi_, nm in ((-9, -0.5, "rain < 0.6x GPCC"), (-0.5, -0.2, "0.6-0.8x"), (-0.2, 0.2, "within 20%"),
                     (0.2, 9, "> 1.2x")):
    m = b & (x2 >= lo_) & (x2 < hi_)
    print(f"  {nm:18} area {100 * (w * m).sum() / tot:4.1f}%  excess {wm(ex, m):+.3f}  share of band excess "
          f"{100 * (w * ex)[m].sum() / (w * ex)[b].sum():5.1f}%")
print(f"  band: model {wm(g['m_ss'], b):.3f} CRU {wm(g['o_ss'], b):.3f}")
