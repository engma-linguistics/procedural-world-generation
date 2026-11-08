"""PW-1446 (b) scout 190: split a stored world's high cells into Airy + sediment lift + rest (swell, flexure/sag, sea level,
minus the ice's load). usage: scout3_world.py WORLD_JSON"""
import sys
import numpy as np
from planet import world as W
from planet.tectonics import isostasy as I

w = W.load(sys.argv[1])
L, m = w['layers'], w['meta']
print('layers:', sorted(L))
E = np.asarray(L['elevation'], float)
th = np.asarray(L['crust_thickness'], float)
cov = np.asarray(L['sediment_cover'], float)
ice = np.asarray(L.get('ice', np.zeros_like(E)), float)
cont = th > 20
airy = 250 + I.ISO_LAND * (th - I.CONT_KM)
lift = I.sediment_lift(cont, np.zeros(len(E), np.int64), cov)  # (cover incl. any lava: an upper bound on the lift)
rest = E - airy - lift
print(f"world {m.get('id', '')} t {m.get('t_myr')} sea level {m.get('sea_level_m')}")
for k in (5000, 6000, 7000):
    print(f"cells > {k} m: {(E > k).sum()}")
s = E > 6000
print(f"highest {E.max():.0f}; cells > 6 km {s.sum()}: crust med {np.median(th[s]):.1f}, at cap {(th[s] >= 79.5).mean():.0%}")
for name, v in (("cover km", cov), ("sed lift m", lift), ("rest m", rest), ("ice m", ice), ("excess m", E - airy)):
    print(f"  {name:10s} p10 {np.percentile(v[s],10):7.1f} med {np.median(v[s]):7.1f} p90 {np.percentile(v[s],90):7.1f} max {v[s].max():7.1f}")
print("top 10: cell elev crust cover lift rest ice")
for c in np.argsort(-E)[:10]:
    print(f"  {c:6d} {E[c]:6.0f} {th[c]:5.1f} {cov[c]:5.1f} {lift[c]:6.0f} {rest[c]:6.0f} {ice[c]:5.0f}")
cap = cont & (th >= 79.5)
print(f"cap cells {cap.sum()}: cover med {np.median(cov[cap]):.1f} km p90 {np.percentile(cov[cap],90):.1f}; "
      f"lift med {np.median(lift[cap]):.0f}; rest med {np.median(rest[cap]):.0f}")
print(f"all continent: cover med {np.median(cov[cont]):.1f} p90 {np.percentile(cov[cont],90):.1f} km")

# static before/after with isostasy.max_km (the world's crust thinned to the new cap, nothing else re-run). The world
# stores no swell, so two bounds: sediment lift only, and sediment lift plus the positive part of the rest
print("static re-cap (lower bound: lift only | upper bound: lift + max(rest, 0)):")
for name, over in (("lift only", lift), ("lift+rest", lift + np.maximum(rest, 0))):
    cap = np.maximum(I.MAX_KM - over / I.ISO_LAND, cov)
    E2 = E - np.where(cont, I.ISO_LAND * np.maximum(th - cap, 0), 0)
    print(f"  {name:9s}: cells > 5/6/7 km {(E2 > 5000).sum()} / {(E2 > 6000).sum()} / {(E2 > 7000).sum()}, highest {E2.max():.0f} m; "
          f"land > 4 km {100 * ((E2 > 4000) & (E2 > 0)).sum() / (E2 > 0).sum():.2f}% (was {100 * (E > 4000).sum() / (E > 0).sum():.2f}%)")
