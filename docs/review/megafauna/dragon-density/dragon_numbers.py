"""dragon_numbers.py L45B_DIR OUT.json: every model number on the dragon-density page (index.html), from fun lane 45b's sweep outputs.

L45B_DIR holds the probe outputs (docs/review/megafauna/probe.py, run by the lane's sweep.sh / one.sh at git c32e89f8):
  new2/WORLD_ROLL.json     6 worlds x rolls 7000-7003, the default model (food budget on, peoples' pressure on), --eras 25,10,0
  nopress/WORLD_7000.json  the same 6 worlds, roll 7000, --no-press (megafauna.PRESS_N0 = 1e12: peoples press dragons not at all)
  save2/run/ERAS.npz       world 2a7385 roll 7000, the default model, per-cell budget fields at the eras nearest 25, 10 and 0 kyr ago
Constants come from planet.lineages (prey, dragon_ages, history.megafauna) at this checkout. Nothing is tuned here.

Run: uv run python docs/review/megafauna/dragon-density/dragon_numbers.py L45B_DIR docs/review/megafauna/dragon-density/numbers.json
"""
import glob
import json
import math
import sys
from pathlib import Path

import numpy as np

from planet.geo import R_KM
from planet.lineages import dragon_ages as DA
from planet.lineages import prey as PR
from planet.lineages.history import megafauna as MG

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
CELL_KM2 = 4 * math.pi * R_KM ** 2 / 163842  # an L7 cell (all sweep runs are L7: 163,842 cells)
CLASSES = ("none", "foragers", "herders", "farmers", "all")
ERAS = ("25", "10", "0")
out: dict = {"cell_km2": CELL_KM2}

# ---- the chain's constants -----------------------------------------------------------------------------------------------
ds = DA.structure(DA.DEFAULT)
g = MG.guild_ratio()
food_t = ds["cattle_yr"] * PR.HEAD_T  # t of prey a dragon eats a year
coef = MG.OFFTAKE / (1.0 + g) / food_t  # dragons per km2 per t/km2 of prey where nobody else eats (megafauna.natural_coef, "food")
mean_mass = float(np.dot(ds["share"], ds["stage_mass_kg"]))  # mean mass over all four stages (wyrmlings included)
m = ds["eco_mass_kg"]
out["chain"] = {
    "schedule": ds["name"], "eco_mass_kg": m, "mean_mass_all_stages_kg": mean_mass, "kcal_day": ds["kcal_day"],
    "cattle_yr": ds["cattle_yr"], "head_t": PR.HEAD_T, "food_t_yr": food_t, "offtake": MG.OFFTAKE, "stock_tolerable": MG.STOCK_TOLERABLE,
    "guild_ratio": g, "dragon_share": 1.0 / (1.0 + g), "per_km2_per_t": coef, "one_per_km2_at_1t": 1.0 / coef,
    "prey_dragon_biomass_ratio_eco": 1.0 / (coef * m / 1000.0), "prey_dragon_biomass_ratio_mean": 1.0 / (coef * mean_mass / 1000.0),
    "person_kcal_day": MG.PERSON_KCAL_YR / 365.0, "wild_meat": list(MG.WILD_MEAT), "head_kcal": MG.HEAD_KCAL,
    "forager_game_t_yr": MG.WILD_MEAT[0] * MG.PERSON_KCAL_YR / MG.HEAD_KCAL * PR.HEAD_T,
    "other_game_t_yr": MG.WILD_MEAT[1] * MG.PERSON_KCAL_YR / MG.HEAD_KCAL * PR.HEAD_T,
    "guild_classes": [list(c) for c in MG.GUILD_CLASSES],
    "guild_food_weights": [n * mm ** MG.GUILD_KLEIBER for mm, n in MG.GUILD_CLASSES],
    "press_n0": MG.PRESS_N0, "overkill": PR.OVERKILL, "dragon_km2_pressed": None,
}
# the prey fit at three grazing NPPs (prey.wild: McNaughton et al. 1989's fit with this module's unit factors)
out["prey_anchor"] = {str(n): float(PR.wild(np.array([float(n)]))[0]) for n in (90, 200, 279, 470)}
# McNaughton et al. 1989's own net secondary production fit, log NSP = 1.10 log NAP - 3.27 (kJ/m2/yr), against their biomass fit at
# the same NAP: herbivore production per unit standing biomass a year (a cross-check on OFFTAKE; the page's own arithmetic)
nsp = {}
for n in (90, 200, 470):
    nap = n * PR.KJ_PER_G_C
    b = 10 ** (1.52 * math.log10(nap) - 4.79)
    p = 10 ** (1.10 * math.log10(nap) - 3.27)
    nsp[str(n)] = {"nap_kj": nap, "B_kj": b, "NSP_kj": p, "NSP_over_B": p / b}
out["mcnaughton_nsp"] = nsp

# ---- literature lines at the dragons' ecological mass ----------------------------------------------------------------------
lit = {
    # Carbone & Gittleman 2002, p. 2274: carnivores per 10,000 kg of prey = 89.1 M^-1.05 (M kg)
    "carbone_per_km2_per_t": 89.1 * m ** -1.05 / 10.0,
    # Jetz et al. 2004, Table 1 p. 268, carnivores, N^-1: 34.43 ha x M^0.86 (area per individual)
    "jetz_carn_km2_each": 34.43 * m ** 0.86 / 100.0,
    # Jetz et al. 2004, Table 1, carnivores, home range H: 52.07 ha x M^1.20
    "jetz_carn_home_range_km2": 52.07 * m ** 1.20 / 100.0,
    # Farlow 1993, p. 187: reptile density = 66.07 M^-1.01 per km2 (M kg)
    "farlow_reptile_per_km2": 66.07 * m ** -1.01,
    # Farlow 1993, p. 176: prey:predator biomass 200:1 to 100:1 in modern large-mammal communities (as low as 45:1)
    "farlow_ratio_per_km2_per_t_100": 1.0 / (100.0 * m / 1000.0),
    "farlow_ratio_per_km2_per_t_200": 1.0 / (200.0 * m / 1000.0),
    # Farlow 1993, p. 172, eq. 6: prey turnover 0.94 M^-0.28 per yr
    "farlow_turnover": {str(k): 0.94 * k ** -0.28 for k in (100, 500, 1000)},
}
lit["carbone_one_per_km2_at_1t"] = 1.0 / lit["carbone_per_km2_per_t"]
lit["farlow_reptile_one_per_km2"] = 1.0 / lit["farlow_reptile_per_km2"]
out["literature"] = lit

# ---- the sweep: density by who lives there, per era ------------------------------------------------------------------------


def load(tag):
    return {Path(f).stem: json.load(open(f)) for f in sorted(glob.glob(str(SRC / tag / "*.json")))}


def era_table(runs):
    tab = {}
    for e in ERAS:
        tab[e] = {}
        for c in CLASSES:
            cells = sum(r["eras"][e][c]["cells"] for r in runs.values())
            drag = sum(r["eras"][e][c]["dragons"] for r in runs.values())
            sup = sum(r["eras"][e][c]["supply_t"] for r in runs.values())
            per = [1000.0 * r["eras"][e][c]["dragons"] / (r["eras"][e][c]["cells"] * CELL_KM2)
                   for r in runs.values() if r["eras"][e][c]["cells"] > 0]
            shares = {k: (sum(r["eras"][e][c][k] * r["eras"][e][c]["supply_t"] for r in runs.values()) / sup if sup > 0 else 0.0)
                      for k in ("stock", "peoples", "giants", "guild", "food", "dragons_need")}
            area = cells * CELL_KM2
            tab[e][c] = {"cells": cells, "km2": area, "dragons": drag, "per_1000km2": 1000.0 * drag / area if area else None,
                         "per_1000km2_runs_min": min(per, default=None), "per_1000km2_runs_max": max(per, default=None),
                         "supply_t_km2_yr": sup / area if area else None, "shares": shares,
                         "land_share": None}
        land = tab[e]["all"]["cells"]
        for c in CLASSES:
            tab[e][c]["land_share"] = tab[e][c]["cells"] / land if land else None
    return tab


new2, nop = load("new2"), load("nopress")
out["sweep"] = {"runs": sorted(new2), "eras": era_table(new2),
                "present_dragons_per_run": {k: r["present"]["dragons"] for k, r in new2.items()}}
out["sweep"]["present_dragons_mean"] = float(np.mean(list(out["sweep"]["present_dragons_per_run"].values())))
new2_7000 = {k: v for k, v in new2.items() if k.endswith("_7000")}
out["sweep_7000"] = {"runs": sorted(new2_7000), "eras": era_table(new2_7000)}
out["nopress"] = {"runs": sorted(nop), "eras": era_table(nop), "present_dragons_per_run": {k: r["present"]["dragons"] for k, r in nop.items()}}
# pressure's toll: with-pressure density over no-pressure density, same worlds and roll (7000)
toll = {}
for e in ERAS:
    toll[e] = {c: (out["sweep_7000"]["eras"][e][c]["per_1000km2"] / out["nopress"]["eras"][e][c]["per_1000km2"]
                   if out["nopress"]["eras"][e][c]["per_1000km2"] else None) for c in CLASSES}
out["pressure_keeps"] = toll

# ---- one run per cell (2a7385 roll 7000): rich and poor land ---------------------------------------------------------------
z = np.load(SRC / "save2" / "run" / "ERAS.npz")
cell = {}
bins = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 100.0]
for e in ("25", "0"):
    land = z[f"land_{e}"]
    pp = {c: z[f"people_{c}_{e}"] for c in ("foragers", "herders", "farmers", "others")}
    allp = sum(pp.values())
    masks = {"none": land & (allp < 0.02)}
    for c in ("foragers", "herders", "farmers"):
        masks[c] = land & (allp >= 0.02) & np.all([pp[c] >= pp[o] for o in pp if o != c], axis=0)
    prey = z[f"prey_{e}"]  # wild (after overkill) + livestock, t/km2, over a dragon's reach
    d = z[f"dragons_{e}"]  # expected dragons per km2 (every kind; presence x local density)
    fd = z[f"food_{e}"] / food_t  # what the dragons' share of the food would feed, per km2 (pressure off, same prey)
    rows = {}
    for c, mk in masks.items():
        r = {}
        for lo, hi, name in ((0.0, 1.0, "poor"), (1.0, 3.0, "middling"), (3.0, 100.0, "rich")):
            s = mk & (prey >= lo) & (prey < hi)
            if s.sum() < 20:
                r[name] = None
                continue
            r[name] = {"cells": int(s.sum()), "prey_t_km2": float(prey[s].mean()), "per_1000km2": 1000.0 * float(d[s].mean()),
                       "food_allows_per_1000km2": 1000.0 * float(fd[s].mean())}
        rows[c] = r
    binned = {}
    for c in ("none", "peopled"):
        mk = masks["none"] if c == "none" else land & (allp >= 0.02)
        bl = []
        for lo, hi in zip(bins[:-1], bins[1:]):
            s = mk & (prey >= lo) & (prey < hi)
            if s.sum() >= 20:
                bl.append({"lo": lo, "hi": hi, "cells": int(s.sum()), "prey": float(prey[s].mean()),
                           "per_km2": float(d[s].mean()), "food_allows_per_km2": float(fd[s].mean())})
        binned[c] = bl
    cell[e] = {"ago_kyr": float(z[f"ago_{e}"]), "by_class": rows, "binned": binned}
out["cells_2a7385"] = cell

# ---- dragons over time, 2a7385 roll 7000, with and without the peoples' pressure ---------------------------------------------
out["series"] = {"with_pressure": new2["2a7385_7000"]["series"], "no_pressure": nop["2a7385_7000"]["series"]}

# ---- the Sword Coast referent ---------------------------------------------------------------------------------------------
MI = 1.609344
ns, ew = 1500 * MI, 1000 * MI
sc = {"ns_km": ns, "ew_km": ew, "km2": ns * ew}
# a box of the same size centred on 47 N, 0.5 E (western Europe), drawn on the sphere
lat_c, lon_c = 47.0, 0.5
dlat = ns / (math.pi * R_KM / 180.0)
dlon = ew / (math.pi * R_KM / 180.0 * math.cos(math.radians(lat_c)))
la1, la2 = lat_c - dlat / 2, lat_c + dlat / 2
box_km2 = R_KM ** 2 * math.radians(dlon) * (math.sin(math.radians(la2)) - math.sin(math.radians(la1)))
sc["box"] = {"lat_s": la1, "lat_n": la2, "lon_w": lon_c - dlon / 2, "lon_e": lon_c + dlon / 2, "km2": box_km2}
E = out["sweep"]["eras"]
NP = out["nopress"]["eras"]
counts = {}
for e in ERAS:
    counts[e] = {}
    for c in CLASSES:
        counts[e][c] = {"with_pressure": E[e][c]["per_1000km2"] * sc["km2"] / 1000.0,
                        "no_pressure": NP[e][c]["per_1000km2"] * sc["km2"] / 1000.0 if NP[e][c]["per_1000km2"] else None}
sc["counts"] = counts
# rich and poor: one run's cells (2a7385 roll 7000), present and 25 kyr
rp = {}
for e in ("25", "0"):
    rp[e] = {}
    for c, r in cell[e]["by_class"].items():
        rp[e][c] = {k: (None if v is None else {"with_pressure": v["per_1000km2"] * sc["km2"] / 1000.0,
                                                "food_allows": v["food_allows_per_1000km2"] * sc["km2"] / 1000.0,
                                                "prey_t_km2": v["prey_t_km2"]}) for k, v in r.items()}
sc["rich_poor"] = rp
# the formula alone (no people anywhere): dragons in the area at a uniform prey biomass
sc["formula"] = {str(p): coef * p * sc["km2"] for p in (0.6, 1.0, 3.0, 7.0)}
out["sword_coast"] = sc

OUT.write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("chain", "literature", "pressure_keeps")}, indent=1))
for e in ERAS:
    print(e, {c: (round(E[e][c]["per_1000km2"], 3), round(NP[e][c]["per_1000km2"] or 0, 2), round(E[e][c]["land_share"], 2)) for c in CLASSES})
print(json.dumps(sc, indent=1)[:4000])
print(json.dumps(cell, indent=1)[:5000])
