"""Lane 123: the herds' inputs on stored worlds, warm land by rain band (as lane 103's table), with the climate the plants saw."""
import sys
from pathlib import Path

sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6")
import planet  # noqa: F401
import numpy as np
from planet import store as S, world as W, gameattrs as GA, climate
from planet.lineages import prey as PR
from planet.geo import is_land

for wid in sys.argv[1:]:
    w = W.load(S.find_world(wid))
    g, L = w["grid"], w["layers"]
    pco2 = w["meta"].get("vegetation", {}).get("pco2")
    a = lambda k: np.asarray(L[k], float)  # noqa: E731
    land = is_land(a("elevation"), a("ice")) & (a("ice") <= 0) & ~(np.asarray(L["lake"]) > 0)
    ga = GA.world_layers(g, L, raw=True)
    graze = ga["grazing_npp"]
    P = 0.5 * (a("precipitation_jul") + a("precipitation_jan"))
    T = a("temperature")
    herds = PR.wild(graze, P)
    warm = land & (T > 18)
    c4 = a("veg_C4G") / np.maximum(a("veg_C4G") + a("veg_C3G"), 1e-9)
    print(f"world {wid} L{g.level} pco2 {pco2} ppm; warm land cells {warm.sum()}")
    print(" rain   n   MAT  Twarm  PET   npp  graze tree% C4  above herb_anpp_dry herds(median t/km2)")
    for p0, p1 in ((150, 250), (250, 400), (400, 550), (550, 700), (700, 900), (900, 1200)):
        m = warm & (P >= p0) & (P < p1)
        if m.sum() < 5:
            continue
        ab = PR.above(P[m])
        print(f" {p0}-{p1} {m.sum():4d} {T[m].mean():5.1f} {a('warm_month')[m].mean():5.1f} {a('pet')[m].mean() if 'pet' in L else np.nan:6.0f} "
              f"{a('npp')[m].mean():5.0f} {graze[m].mean():5.0f} {a('tree_cover')[m].mean():4.0f} {c4[m].mean():.2f} {ab.mean():.2f} "
              f"{(graze[m] * ab / PR.C_FRAC).mean():5.0f} {np.median(herds[m]):.2f}")
