"""Read a diag npz: on a FIXED mask (rich empty land at the present, and at 25 kyr), per era: dragon occupancy (any dragon kind
P >= EST), whether any kind's habitat K >= EST there (could hold), the best kind K, mean temperature and rain, and per-kind shares."""
import sys
import numpy as np
EST = 0.12
z = np.load(sys.argv[1])
ids = [str(x) for x in z['mf_ids']]
drag = [i for i, x in enumerate(ids) if x.endswith('_dragon') and x not in ('chromatic_dragon', 'metallic_dragon')]
eras = sorted({k.split('@')[1] for k in z.files if '@' in k and k.split('@')[1] != 'final'}, key=lambda e: -float(e))
eras = eras + ['final']
def rich_empty(e):
    return z['land@' + e] & (z['allp@' + e] < 0.02) & (z['prey@' + e] >= 3)
for me in ('final', '25'):
    m = rich_empty(me)
    print(f'== fixed mask: rich empty land at {me} ({m.sum()} cells); T {z["T@"+me][m].mean():.1f} C, rain median {np.median(z["R@"+me][m]):.0f} mm')
    for e in eras:
        P, K = z['P@' + e][drag], z['K@' + e][drag]
        occ = (P[:, m] >= EST).any(0)
        could = (K[:, m] >= EST).any(0)
        print(f'  {e:>5} ago={float(z["ago@"+e]) if e!="final" else 0:5.1f}: occupied {occ.mean():.2f}  K>=EST for some kind {could.mean():.2f}  '
              f'occupied|could {occ[could].mean() if could.any() else 0:.2f}  bestK {K[:, m].max(0).mean():.2f}  T {z["T@"+e][m].mean():5.1f}  '
              f'rain {np.median(z["R@"+e][m]):5.0f}  peoples here {(z["allp@"+e][m] >= 0.02).mean():.2f}  press {z["press@"+e][m].mean():.2f}')
    # which kinds held it at 25 and what happened to their K
    for j, k in enumerate(drag):
        a25 = (z['P@25'][k][m] >= EST).mean(); a0 = (z['P@final'][k][m] >= EST).mean()
        k25 = (z['K@25'][k][m] >= EST).mean(); k0 = (z['K@final'][k][m] >= EST).mean()
        if max(a25, a0, k25, k0) > 0.02:
            print(f'     {ids[k]:>14}: held {a25:.2f} -> {a0:.2f}; K>=EST {k25:.2f} -> {k0:.2f}; meanK {z["K@25"][k][m].mean():.2f} -> {z["K@final"][k][m].mean():.2f}')
    # tags at the present over the mask
    tg = [t.split('@')[0][4:] for t in z.files if t.startswith('tag_') and t.endswith('@final')]
    print('   tags at present:', {t: round(float(z[f'tag_{t}@final'][m].mean()), 2) for t in tg})
    cl = z['cl@final'][m]
    K_ = ["Af", "Am", "Aw", "BWh", "BWk", "BSh", "BSk", "Csa", "Csb", "Csc", "Cwa", "Cwb", "Cwc", "Cfa", "Cfb", "Cfc", "Dsa", "Dsb", "Dsc", "Dsd", "Dwa", "Dwb", "Dwc", "Dwd", "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF"]
    u, c = np.unique(cl, return_counts=True)
    print('   Koppen:', sorted(((K_[a] if 0 <= a < 30 else a, int(b)) for a, b in zip(u, c)), key=lambda x: -x[1])[:8])
# all rich land (prey >= 3), whoever lives there: the same
for e in ('25', 'final'):
    m = z['land@' + e] & (z['prey@' + e] >= 3)
    P = z['P@' + e][drag]
    print(f'all rich land at {e}: {m.sum()} cells, occupied {(P[:, m] >= EST).any(0).mean():.2f}, peopled {(z["allp@"+e][m] >= 0.02).mean():.2f}')
