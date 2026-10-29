"""usage: diag_b.py [k=v ...] -> where Earth L6 misses Koppen B (lane 25, PW-015): the B share with the land rain
scaled, with GPCC rain on the model temperatures, and the obs-B land the model misses by box (rain ratio per half-year,
which group it went to). k=v: climate.TUNE overrides. Harness only."""
import sys
from pathlib import Path
W = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, W)
import planet  # noqa
import numpy as np
from planet import climate
for kv in sys.argv[1:]:
    k, v = kv.split("="); climate.TUNE[k] = float(v)
from tools import earth_check as E, earth_data
from tools.earth_data import cell_areas
grid, d, c, _, rec = E.run(6)
lat = grid.lat; lon = grid.lon
w = cell_areas(grid); land = earth_data.land_of(d); ant = lat < -60
m = land & ~ant
ok = d["obs_koppen"].astype(int); both = m & (ok >= 0)
GB = np.array([cc.startswith("B") for _, cc, _, _ in climate.KOPPEN])
def Bsh(k, mask=m): return 100 * w[mask & GB[k]].sum() / w[mask].sum()
k = np.asarray(c["koppen"])
el = np.where(land, np.maximum(d["elev"], 1.0), d["elev"])
def kop(pj, pn):
    return climate.koppen(el, c["temp"], c["t_warm"], c["t_cold"], 0.5 * (pj + pn), pj, pn, lat, d["ice"])
print(f"B model {Bsh(k):.1f}  obs {Bsh(np.maximum(ok,0), both):.1f}  (recomputed model {Bsh(kop(np.asarray(c['p_jul']), np.asarray(c['p_jan']))):.1f})")
pj, pn = np.asarray(c["p_jul"]), np.asarray(c["p_jan"])
for f in (0.85, 0.7, 0.6):
    print(f"  land P x{f}: B {Bsh(kop(np.where(land, f*pj, pj), np.where(land, f*pn, pn))):.1f}")
oj, on = d["obs_p_jul"].astype(float), d["obs_p_jan"].astype(float)
good = np.isfinite(oj) & np.isfinite(on)
kk = kop(np.where(good, oj, pj), np.where(good, on, pn))
print(f"  model T + GPCC half-year rain: B {Bsh(kk):.1f}")
# attribution: obs-B cells the model calls non-B, by box
miss = both & GB[np.maximum(ok, 0)] & ~GB[k]
extra = both & ~GB[np.maximum(ok, 0)] & GB[k]
tot = w[m].sum()
P = 0.5 * (pj + pn); Po = 0.5 * (oj + on)
boxes = {"Sahel/W Afr 8-20N": (8, 20, -20, 40), "Sahara/Arabia 20-35N": (20, 35, -20, 60), "E Afr/Horn": (-5, 12, 33, 52),
         "S Africa": (-35, -10, 10, 40), "Australia": (-40, -10, 110, 155), "C Asia/Iran": (30, 50, 45, 90),
         "Mongolia/N China": (35, 52, 90, 125), "N Am West": (25, 50, -125, -95), "Mexico": (15, 32, -118, -95),
         "NE Brazil": (-15, 0, -45, -34), "Pampas/Patag/Atacama": (-55, -15, -76, -55), "India/Pak": (5, 35, 60, 90),
         "Mediterranean/Iberia": (30, 45, -10, 45)}
lonw = (lon + 180) % 360 - 180
print(f"\nobs-B land the model misses: {100*w[miss].sum()/tot:.1f}% of land; model B where obs isn't: {100*w[extra].sum()/tot:.1f}%")
print(f"{'box':>28} {'miss%':>6} {'extra%':>6} {'P/Pobs':>7} {'jul':>5} {'jan':>5}  to A/C/D/E (% of miss)")
G = np.array(["ABCDE".index(cc[0]) if cc[0] in "ABCDE" else -1 for _, cc, _, _ in climate.KOPPEN])
seen = np.zeros(grid.n, bool)
def gm(a, b, mm):
    ws = w[mm]
    return np.exp(np.sum(ws * np.log(np.maximum(a[mm], 1) / np.maximum(b[mm], 1))) / max(ws.sum(), 1e-12))
for name, (a, b, lo, hi) in boxes.items():
    bx = (lat >= a) & (lat < b) & (lonw >= lo) & (lonw < hi) & ~seen
    seen |= bx
    mm = miss & bx
    if w[mm].sum() == 0 and w[extra & bx].sum() == 0:
        continue
    to = [100 * w[mm & (G[k] == g)].sum() / max(w[mm].sum(), 1e-12) for g in (0, 2, 3, 4)]
    print(f"{name:>28} {100*w[mm].sum()/tot:6.2f} {100*w[extra&bx].sum()/tot:6.2f} {gm(P,Po,mm):7.2f} {gm(pj,oj,mm):5.2f} "
          f"{gm(pn,on,mm):5.2f}  " + " ".join(f"{x:4.0f}" for x in to))
rest = miss & ~seen
print(f"{'rest':>28} {100*w[rest].sum()/tot:6.2f} {100*w[extra & ~seen].sum()/tot:6.2f}")
