"""Lane 123: per-PFT GPP, NPP, LAI and water ratio on Earth's observed climate, in chosen climate boxes."""
import sys

sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6")
import planet  # noqa: F401
import numpy as np
from planet import store as S, world as W, vegetation as V
from tools.earth_data import earth_on_grid, earth_clouds
from tools import veg_check as VC
from tools.soil_check import geology

RL = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
V._KP[[V.IDX[c] for c in ("C4G", "C3G", "TunH", "WetH")], 9] *= RL
w = W.load(S.find_world("506694"))
g, L = w["grid"], w["layers"]
obs = {**earth_on_grid(g), **earth_clouds(g)}
v = VC.run(g, L, obs, geology(g, L))
s, pot, nu, sm = v["s"], v["pot"], v["eq"]["nu"], v["sm"]
land = v["land"]
P, T = s["precip"], s["temp"]
lat, lon = g.lat, g.lon
par = s["par"].sum(0)
boxes = {
    "wet tropics P>1800 T>24": land & (P > 1800) & (T > 24),
    "Afr savanna 550-700 T>18": land & (P >= 550) & (P < 700) & (T > 18) & (lon > -20) & (lon < 52) & (lat > -35) & (lat < 20),
    "temperate grass 300-500 T5-12": land & (P >= 300) & (P < 500) & (T > 5) & (T < 12),
    "temperate forest 800-1200 T8-14": land & (P >= 800) & (P < 1200) & (T > 8) & (T < 14),
    "boreal T-5..0 P400-700": land & (P >= 400) & (P < 700) & (T > -5) & (T < 0),
}
for name, m in boxes.items():
    print(f"== {name}: n={m.sum()} P={P[m].mean():.0f} T={T[m].mean():.1f} PAR={par[m].mean():.0f} MJ? shade={np.nanmean(s['cloud'][m]) if s.get('cloud') is not None else np.nan:.2f} "
          f"cell npp={sm['npp'][m].mean():.0f} gpp/cell={(nu * np.maximum(pot['gpp'], 0)).sum(0)[m].mean():.0f} pet={s['pet_y'][m].mean():.0f} cap={s['cap1'][m].mean():.0f}/{s['cap2'][m].mean():.0f}")
    for k, c in enumerate(V.CODES):
        share = nu[k][m].mean()
        if share < 0.05:
            continue
        print(f"   {c:5} cover {share:.2f} GPP {pot['gpp'][k][m].mean():6.0f} NPP {pot['npp'][k][m].mean():6.0f} CUE {pot['npp'][k][m].mean() / max(pot['gpp'][k][m].mean(), 1):.2f} "
              f"LAI {pot['lai'][k][m].mean():4.1f} alpha {pot['alpha'][k][m].mean():.2f}")
