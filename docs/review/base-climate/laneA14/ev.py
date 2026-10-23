"""Offline: what a wind-set summer layer would do to the sea's summer air, from out/base.npz (main's fields).
own(h) = Q / hypot(rho c omega h, ice_b); land part scales with c(h) = open_b / (open_b + rho c omega h)."""
import numpy as np, sys
D = np.load(sys.argv[1] if len(sys.argv) > 1 else "out/base.npz")
g = {k: D[k] for k in D.files}
RC, W, ICE_B, OPEN_B = 4.1e6, 2 * np.pi / (365.25 * 86400), 3.5, 30.0
def own(h): return g["Q"] / np.hypot(RC * W * h, ICE_B)
def cfac(h): return OPEN_B / (OPEN_B + RC * W * h)
own50 = own(50.0); land50 = g["sea_half"] - own50
def alpha(T): T = np.clip(T, -2, 32); return 1e-4 * (0.55 + 0.13 * T - 0.0012 * T * T)
def mo(u, T, m=1 / 0.4):
    ust3 = (1.2 * 1.3e-3 / 1025.0 * u * u) ** 1.5
    B = 9.81 * alpha(T) * g["Q"] / RC
    return m * ust3 / np.maximum(B, 1e-12)
sea, lat, lon, w = g["sea"], g["lat"], g["lon"], g["w"]
def wm(f, m): return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12)) if m.any() else float("nan")
B = {"NE Atl": (45, 55, -25, -6), "Biscay-N Sea": (43, 58, -6, 8), "Norw Sea": (60, 70, -5, 15),
     "G Alaska": (52, 60, -160, -135), "NE Pac": (40, 50, -150, -125), "NW Pac": (35, 45, 145, 175),
     "N Pac 30-40": (30, 40, -170, -140), "Pat": (-52, -40, -64, -56), "Tasman": (-45, -35, 150, 165),
     "Chile": (-52, -38, -85, -76), "Agulhas": (-40, -30, 15, 35), "S Ind 40-50": (-50, -40, 40, 100),
     "S Oc 50-60": (-60, -50, -180, 180), "S Pac 30-40": (-40, -30, -140, -100)}
def variant(name, h):
    half = own(h) + land50 * cfac(h) / cfac(50.0)
    tw = g["tw"] + (half - g["sea_half"])
    hs = (tw - g["tc"]) / 2; ho = (g["otw"] - g["otc"]) / 2
    row = [f"{name:>22}"]
    for k, (a0, a1, l0, l1) in B.items():
        m = sea & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
        row.append(f"{k} h{wm(h, m):3.0f} sw{wm(hs, m):4.1f}/{wm(ho, m):3.1f} Tw{wm(tw - g['otw'], m):+4.1f}")
    ratio = np.where(sea & (np.abs(lat) > 20) & (np.abs(lat) < 65), hs / np.maximum(ho, 0.3), np.nan)
    ok = np.isfinite(ratio)
    inb = ((ratio[ok] <= 1.5) & (ratio[ok] >= 1 / 1.5))
    row.append(f"| sea 20-65 swing within 1.5x: {100 * (w[ok] * inb).sum() / w[ok].sum():.0f}%")
    print("\n   ".join(row))
variant("main (50 m)", np.full(len(lat), 50.0))
T = g["sst"] + g["sea_half"]
for hmin in (10.0, 20.0):
    variant(f"MO vec hmin{hmin:.0f}", np.clip(mo(g["us"], T), hmin, 50.0))
    variant(f"MO vec 2x hmin{hmin:.0f}", np.clip(mo(g["us"], T, 2.0), hmin, 50.0))
for h in (20.0, 30.0, 40.0):
    variant(f"flat {h:.0f} m", np.full(len(lat), h))
