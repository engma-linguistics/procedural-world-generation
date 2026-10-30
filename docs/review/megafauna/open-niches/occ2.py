import sys, numpy as np
z = np.load(sys.argv[1])
E = ('25', '10', '0')
def mask(e):
    land = z['land_' + e]; allp = sum(z[f'people_{c}_{e}'] for c in ('foragers', 'herders', 'farmers', 'others'))
    return land & (allp < 0.02) & (z['prey_' + e] >= 3)
M = {e: mask(e) for e in E}
for me in E:
    m = M[me]
    row = [f'mask@{me} ({m.sum()} cells):']
    for e in E:
        d = z['dragons_' + e]
        row.append(f'occ@{e}={(d[m] > 1e-9).mean():.2f} prey@{e}={z["prey_"+e][m].mean():.2f} empty@{e}={(M[e][m]).mean():.2f}')
    print(' '.join(row))
# overlap of masks
print('mask25 & mask0', (M['25'] & M['0']).sum(), 'mask10 & mask0', (M['10'] & M['0']).sum())
# wild prey vs live
for e in E:
    m = M[e]
    print(e, 'wild offtake mean', z['wild_' + e][m].mean() / 0.1, 'live mean', z['live_' + e][m].mean())
