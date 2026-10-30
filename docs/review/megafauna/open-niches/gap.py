"""gap.py DIAG.npz WORLD: rich land (prey >= 3 t/km2) at the present that no dragon kind's habitat reaches (K < EST for all), whoever lives
there: its climate (env temperature and rain, the world's rain under the prey), Koppen, tags; and the 'mismatch' share (world rain > 3x env)."""
import sys
import numpy as np
from planet.lineages import recent as R
EST = 0.12
z = np.load(sys.argv[1])
tz, now0, wid = R.resolve(sys.argv[2])
ps = R.Pass(tz, now0, R.RecentParams(kyr=30.0, climate_every=2.0), world_ref=wid)
ids = [str(x) for x in z['mf_ids']]
drag = [i for i, x in enumerate(ids) if x.endswith('_dragon') and x not in ('chromatic_dragon', 'metallic_dragon')]
e = 'final'
land, prey, T, Rn = z['land@' + e], z['prey@' + e], z['T@' + e], z['R@' + e]
K = z['K@' + e][drag]; P = z['P@' + e][drag]
KO = ["Af", "Am", "Aw", "BWh", "BWk", "BSh", "BSk", "Csa", "Csb", "Csc", "Cwa", "Cwb", "Cwc", "Cfa", "Cfb", "Cfc", "Dsa", "Dsb", "Dsc", "Dsd", "Dwa", "Dwb", "Dwc", "Dwd", "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF"]
rich = land & (prey >= 3)
gap = rich & (K.max(0) < EST)
held = rich & (P >= EST).any(0)
mism = land & (ps.rain0 > 3 * np.maximum(Rn, 1))
print(f'{sys.argv[2]}: rich land {rich.sum()} cells; dragon-held {held.mean() if False else held.sum() / rich.sum():.2f}; no kind can live there {gap.sum() / rich.sum():.2f}; '
      f'peopled share of the gap {(z["allp@"+e][gap] >= 0.02).mean():.2f}; rain mismatch (world > 3x env) on the gap {mism[gap].mean():.2f}, on all land {mism[land].mean():.3f}')
for nm, m in (('gap', gap), ('held', held)):
    if m.any():
        print(f'  {nm}: T pct {np.percentile(T[m], [10, 50, 90]).round(1)}, env rain pct {np.percentile(Rn[m], [10, 50, 90]).round(0)}, world rain pct {np.percentile(ps.rain0[m], [10, 50, 90]).round(0)}')
        u, c = np.unique(z['cl@' + e][m], return_counts=True)
        print('     Koppen', sorted(((KO[a], int(b)) for a, b in zip(u, c) if 0 <= a < 30), key=lambda x: -x[1])[:8])
        print('     tags', {t[4:-6]: round(float(z[t][m].mean()), 2) for t in z.files if t.startswith('tag_') and t.endswith('@final')})
g5 = gap & (T >= 5) & (T <= 15) & (Rn >= 400) & (Rn <= 900)
print(f'  cool continental plains (5-15 C, 400-900 mm) in the gap: {g5.sum()} cells = {g5.sum() / max(gap.sum(), 1):.2f} of the gap; '
      f'all such rich land: {(rich & (T >= 5) & (T <= 15) & (Rn >= 400) & (Rn <= 900)).sum()}')
