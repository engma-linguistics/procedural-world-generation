"""Lane 148 (PW-1365): a finished world's seasonal extremes and biome shares (read-only).

    PYTHONPATH=. uv run python docs/review/climate/eccentricity/measure.py TAG worlds/<id>.json [TAG2 world2 ...]

Per world, one JSON line: land under ice (% of land), and on open (ice-free) land, area-weighted: warmest month
>= 35 / >= 30 C, warmest month < 0 C (no thaw: 'frozen' ground), coldest month < -20 C, the same two heat shares
per hemisphere, mean warmest / coldest month and the annual swing; global temperature; the biome shares (% of land).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, world  # noqa: E402
from tools.earth_data import cell_areas  # noqa: E402

args = sys.argv[1:]
for tag, path in zip(args[::2], args[1::2]):
    w = world.load(path)
    L, g, m = w["layers"], w["grid"], w["meta"]
    area = cell_areas(g)
    elev = L["elevation"].astype(float)
    ice = L.get("ice", np.zeros(g.n)).astype(float)
    land = (elev > 0) | (ice > 0)
    open_land = land & (ice <= 0)
    tw, tc = L["warm_month"].astype(float), L["cold_month"].astype(float)

    def pct(x, mask):
        return round(100 * float(area[mask & x].sum() / area[mask].sum()), 1) if mask.any() else None

    def mean(x, mask):
        return round(float((x * area)[mask].sum() / area[mask].sum()), 1)

    nh, sh = open_land & (g.lat >= 0), open_land & (g.lat < 0)
    names = {b[0]: b[1] for b in climate.BIOMES}
    bio = {}
    for b in np.unique(L["biome"][land]):
        bio[names.get(int(b), str(b))] = round(100 * float(area[land & (L["biome"] == b)].sum() / area[land].sum()), 1)
    out = dict(tag=tag, world=Path(path).stem, global_temp_c=m.get("global_temp_c"),
               land_pct=round(100 * float(area[land].sum() / area.sum()), 1),
               ice_pct_land=pct(ice > 0, land),
               hot35=pct(tw >= 35, open_land), hot30=pct(tw >= 30, open_land),
               hot35_nh=pct(tw >= 35, nh), hot35_sh=pct(tw >= 35, sh),
               no_thaw=pct(tw < 0, open_land), cold_lt_m20=pct(tc < -20, open_land),
               warm_mean=mean(tw, open_land), cold_mean=mean(tc, open_land),
               swing=mean(tw - tc, open_land), nh_land_share=pct(g.lat >= 0, open_land),
               orbit={k: m.get(k) for k in ("eccentricity", "perihelion", "obliquity")} | dict(m.get("orbit", {})),
               biome=dict(sorted(bio.items(), key=lambda kv: -kv[1])))
    print(json.dumps(out))
