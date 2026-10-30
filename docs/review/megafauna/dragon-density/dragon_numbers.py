"""dragon_numbers.py R2_DIR OUT.json: every model number on the dragon-density page (index.html), from the review's round-2 sweep.

R2_DIR (persistent: /home/daniel/personal/repos/procedural-world-generation/data/review-inputs/dragon-r2/, written by its run.sh) holds
docs/review/megafauna/probe.py outputs run from a snapshot of git 8c7ce305 (main b36c9581 plus this review's probe.py; planet/ as on main,
prey.FORAGE_REF 2.85, GRAZE_REF 279), all with --eras 31,29,25,10,0 --cells:
  on/WORLD_ROLL.json      6 worlds x rolls 7000-7003, the default model (food budget on, the peoples' pressure on)
  off/WORLD_ROLL.json     the same 24 worlds and rolls, --no-press (PRESS_N0 = 1e12: neither overkill nor persecution)
  noper/WORLD_7000.json   the same 6 worlds at roll 7000, --no-persecute (overkill on, dragons not pressed toward meta.dragon_km2)
  ARM/cells/WORLD_ROLL.npz  per-cell fields at each era (budget, peoples by way of life, dragons, presence, biome tags; suitability now)
Constants come from planet.lineages (prey, dragon_ages, history.megafauna) at this checkout. Nothing is tuned here.

Run: PYTHONPATH=. uv run python docs/review/megafauna/dragon-density/dragon_numbers.py R2_DIR docs/review/megafauna/dragon-density/numbers.json
"""
import glob
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import sensitivity as SE  # noqa: E402

from planet.geo import R_KM  # noqa: E402
from planet.lineages import dragon_ages as DA  # noqa: E402
from planet.lineages import prey as PR  # noqa: E402
from planet.lineages.history import megafauna as MG  # noqa: E402

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
CELL_KM2 = 4 * math.pi * R_KM ** 2 / 163842  # an L7 cell (all runs are L7: 163,842 cells; the model treats every cell as this size)
CLASSES = ("none", "others", "foragers", "herders", "farmers", "all")
PEOPLED = ("others", "foragers", "herders", "farmers")
ERAS = ("31", "29", "25", "10", "5", "0")
WORLDS = ("2a7385", "1df1c3", "e71172", "6909cb", "a12762", "067778")
out: dict = {"cell_km2": CELL_KM2}

# ---- the chain's constants -----------------------------------------------------------------------------------------------
ds = DA.structure(DA.DEFAULT)
g = MG.guild_ratio()
food_t = ds["cattle_yr"] * PR.HEAD_T  # t of prey a dragon kills a year (survivorship mean over all ages)
coef = MG.OFFTAKE / (1.0 + g) / food_t  # dragons per km2 per t/km2 of prey where nobody else eats (megafauna.natural_coef, "food")
mean_mass = float(np.dot(ds["share"], ds["stage_mass_kg"]))
m = ds["eco_mass_kg"]
out["chain"] = {
    "schedule": ds["name"], "eco_mass_kg": m, "mean_mass_all_stages_kg": mean_mass, "kcal_day": ds["kcal_day"],
    "cattle_yr": ds["cattle_yr"], "generation_yr": ds["generation_yr"], "head_t": PR.HEAD_T, "food_t_yr": food_t, "offtake": MG.OFFTAKE, "stock_tolerable": MG.STOCK_TOLERABLE,
    "guild_ratio": g, "dragon_share": 1.0 / (1.0 + g), "per_km2_per_t": coef, "one_per_km2_at_1t": 1.0 / coef,
    "prey_dragon_biomass_ratio_eco": 1.0 / (coef * m / 1000.0), "prey_dragon_biomass_ratio_mean": 1.0 / (coef * mean_mass / 1000.0),
    "person_kcal_day": MG.PERSON_KCAL_YR / 365.0, "wild_meat": list(MG.WILD_MEAT), "head_kcal": MG.HEAD_KCAL,
    "forager_game_t_yr": MG.WILD_MEAT[0] * MG.PERSON_KCAL_YR / MG.HEAD_KCAL * PR.HEAD_T,
    "other_game_t_yr": MG.WILD_MEAT[1] * MG.PERSON_KCAL_YR / MG.HEAD_KCAL * PR.HEAD_T,
    "guild_classes": [list(c) for c in MG.GUILD_CLASSES],
    "guild_food_weights": [n * mm ** MG.GUILD_KLEIBER for mm, n in MG.GUILD_CLASSES],
    "press_n0": MG.PRESS_N0, "overkill": PR.OVERKILL, "kill_q": MG.KILL_Q, "breed_x": MG.BREED_X, "motive0": MG.MOTIVE0, "forager_org": MG.FORAGER_ORG, "vulnerability": MG.VULNERABILITY, "ancient_x": MG.ANCIENT_X,
    "era_level": MG.ERA_LEVEL, "era_kyr": MG.ERA_KYR, "people_exp": PR.PEOPLE_EXP, "forage_ref": PR.FORAGE_REF, "graze_ref": PR.GRAZE_REF, "npp_ref": PR.NPP_REF,
    "stage_share": ds["share"], "stage_food_share": ds["food_share"], "stage_mass_kg": ds["stage_mass_kg"],
    "kill_t_at_eco_mass": float(DA.cattle_per_yr(DA.fmr_kcal(m))) * PR.HEAD_T,
    "single_reptile_mass_for_mean_intake_kg": float((ds["kcal_day"] * DA.KJ_PER_KCAL / 0.196) ** (1 / 0.889) / 1000.0),
}
out["prey_anchor"] = {str(n): float(PR.wild(np.array([float(n)]))[0]) for n in (90, 200, 279, 470)}
nsp = {}
for n in (90, 200, 470):  # McNaughton et al. 1989's NSP fit against their biomass fit at the same NAP (two fits, different data)
    nap = n * PR.KJ_PER_G_C
    b = 10 ** (1.52 * math.log10(nap) - 4.79)
    p = 10 ** (1.10 * math.log10(nap) - 3.27)
    nsp[str(n)] = {"nap_kj": nap, "B_kj": b, "NSP_kj": p, "NSP_over_B": p / b}
out["mcnaughton_nsp"] = nsp
out["sensitivity"] = SE.run()

# ---- literature lines at the dragons' ecological mass ----------------------------------------------------------------------
lit = {
    "carbone_per_km2_per_t": 89.1 * m ** -1.05 / 10.0,  # Carbone & Gittleman 2002, p. 2274 (per 10,000 kg of prey; M kg)
    "carbone_biomass_kg_per_10t": 89.1 * m ** -0.05,  # the same fit as carnivore biomass per 10,000 kg of prey at mass m
    "jetz_carn_km2_each": 34.43 * m ** 0.86 / 100.0,  # Jetz et al. 2004, Table 1, p. 268 (ha; M kg)
    "jetz_carn_home_range_km2": 52.07 * m ** 1.20 / 100.0,
    "farlow_reptile_per_km2": 66.07 * m ** -1.01,  # Farlow 1993, p. 187
    "farlow_ratio_per_km2_per_t_100": 1.0 / (100.0 * m / 1000.0),  # Farlow 1993, p. 176
    "farlow_ratio_per_km2_per_t_200": 1.0 / (200.0 * m / 1000.0),
    "farlow_turnover": {str(k): 0.94 * k ** -0.28 for k in (100, 500, 1000, 2000)},  # Farlow 1993, eq. 6, p. 172
    "farlow_ecto_intake_t_yr": 3.81 * m ** -0.16 * m / 1000.0,  # Farlow 1993, eq. 8, p. 187 (kg/kg/yr)
    "farlow_endo_intake_t_yr": 48.87 * m ** -0.30 * m / 1000.0,  # Farlow 1993, eq. 7, p. 172
    # Marshall et al. 2021, Table 1, p. 284: Damuth's law rho = a M^-0.75, M in g, log10 a = 1.80 / 2.99 / 4.18 (2.5% / mean / 97.5%)
    "marshall_per_km2": {k: 10 ** (la - 0.75 * math.log10(m * 1000.0)) for k, la in (("lo", 1.80), ("mid", 2.99), ("hi", 4.18))},
    # Burness et al. 2001, p. 14520: top species' mass (kg) against land area (km2)
    "burness": {"endo_carn": lambda A: 0.05 * A ** 0.47, "ecto_carn": lambda A: 0.25 * A ** 0.47},
}
lit["carbone_one_per_km2_at_1t"] = 1.0 / lit["carbone_per_km2_per_t"]
lit["farlow_reptile_one_per_km2"] = 1.0 / lit["farlow_reptile_per_km2"]
lit["marshall_one_per_km2"] = {k: 1.0 / v for k, v in lit["marshall_per_km2"].items()}
lit["marshall_prey_match_t_km2"] = lit["marshall_per_km2"]["mid"] / coef
lit["jetz_crossing_t_km2"] = 1.0 / (lit["jetz_carn_km2_each"] * coef)
lit["farlow_reptile_crossing_t_km2"] = lit["farlow_reptile_per_km2"] / coef
lit["model_biomass_kg_per_10t_eco"] = coef * 10.0 * m
lit["model_biomass_kg_per_10t_mean"] = coef * 10.0 * mean_mass
gm = np.array([n * mm for mm, n in MG.GUILD_CLASSES])
top = np.array([mm >= MG.GUILD_APEX_KG for mm, _ in MG.GUILD_CLASSES])
lit["guild_biomass_small_over_apex"] = float(gm[~top].sum() / gm[top].sum())
lit["whole_guild_ratio_mean"] = out["chain"]["prey_dragon_biomass_ratio_mean"] / (1 + lit["guild_biomass_small_over_apex"])
lit["whole_guild_ratio_eco"] = out["chain"]["prey_dragon_biomass_ratio_eco"] / (1 + lit["guild_biomass_small_over_apex"])
# Hamilton et al. 2007 (Table 1 C0 4.44, Fig. 1 label 4.14; ln km2, beta 0.70) and 2009 (Fig. 2 top: log10 A = 0.72 log10(N M) + 0.61)
lit["hamilton"] = {f"{c0}": {str(n): n / (math.exp(c0) * n ** 0.70) for n in (25, 1000)} for c0 in (4.44, 4.14)}
lit["hamilton2009"] = {str(n): {str(mm): n / 10 ** (0.72 * math.log10(n * mm) + 0.61) for mm in (45, 55)} for n in (25, 1000)}
lit["pressure_at"] = {str(n): 1 - math.exp(-n / MG.PRESS_N0) for n in (0.02, 0.03, 0.05, 0.09, 0.1, 0.25)}
# the persecution kill (PW-1068, by age class): the model's own functions (megafauna.dragon_kept, vulnerability), by people and era
class _H:  # (the two attributes dragon_kept reads)
    dragon_struct = ds


_h = _H()
r_dragon = math.log(MG.BREED_X) / ds["generation_yr"]
r_giant = math.log(MG.BREED_X) / 65.0
CASES = (("forager band", 0.3, 1.0, 0.0), ("dense foragers", 6.0, 1.0, 0.0), ("nomads", 0.8, 0.0, 1.0), ("transhumant herders", 3.0, 0.0, 0.9),
         ("farmers", 3.0, 0.0, 0.5), ("dense farmers", 10.0, 0.0, 0.5))
kt = {"r_dragon": r_dragon, "r_giant": r_giant, "rows": [], "vulnerability": {}}
for ago in (25.0, 10.0, 5.0, 3.0, 2.0, 1.0, 0.5, 0.0):
    lev = MG.tech_level("renaissance", ago)
    kt["vulnerability"][str(ago)] = {"level": lev, "stages": [float(x) for x in MG.vulnerability(lev)]}
    for nm, n_, f_, st in CASES:
        mn = (MG.MOTIVE0 + (1 - MG.MOTIVE0) * st) * (f_ * MG.FORAGER_ORG + (1 - f_))
        e_ = MG.KILL_Q * n_ * mn
        kt["rows"].append({"ago": ago, "level": lev, "case": nm, "people_km2": n_, "means": mn, "effort_yr": e_,
                           "dragons_kept": float(MG.dragon_kept(_h, e_, lev)), "giants_kept": 1 / (1 + e_ * MG.vulnerability(lev)[2] / r_giant)})
# elasticity of R0 to each stage's survival, summed over the stage's years, on the dragons' schedule
mort = np.asarray(DA.SCHEDULES[ds["name"]], float)[DA.STAGE_OF]
breed = DA.AGES >= DA.BREED_FROM
l0 = np.concatenate([[1.0], np.cumprod(1 - mort)[:-1]])
el = {}
for si, nm in enumerate(DA.STAGES):
    p2 = (1 - mort) * np.where(DA.STAGE_OF == si, 1 + 1e-5, 1.0)
    l2 = np.concatenate([[1.0], np.cumprod(p2)[:-1]])
    el[nm] = float((np.log((l2 * breed).sum()) - np.log((l0 * breed).sum())) / 1e-5)
kt["elasticity_R0"] = el
kt["one_stage_0p2pct"] = {nm: float(MG.dragon_kept(_h, 0.002, 0.0) if False else 0.0) for nm in DA.STAGES}
for si, nm in enumerate(DA.STAGES):
    ks = np.where(DA.STAGE_OF == si, 0.002, 0.0)
    lk = np.concatenate([[1.0], np.cumprod((1 - mort) * np.exp(-ks))[:-1]])
    F = (l0 * breed).sum() / (lk * breed).sum()
    kt["one_stage_0p2pct"][nm] = 1 / (1 + (F - 1) / (MG.BREED_X - 1))
lit["kill_table"] = kt
SC_KM2 = (1500 * 1.609344) * (1000 * 1.609344)
lit["burness_sc"] = {k: f(SC_KM2) for k, f in lit.pop("burness").items()}
lit["burness_sc"]["dino_offset_x12"] = 12 * lit["burness_sc"]["ecto_carn"]
out["literature"] = lit

# ---- the sweep: per run, per era, per class ---------------------------------------------------------------------------------


ADD = ("cells", "supply_t", "dragons", "occupied_cells", "food_t", "food_t_occupied")
SHR = ("stock", "peoples", "giants", "guild", "food", "dragons_need")


def load(arm):
    """The arm's runs. probe.py sums four classes (none, foragers, herders, farmers) and all land; "others" (peopled land where another way
    of life leads) is all land minus the four: every summed quantity is additive, and the shares are weighted back by supply."""
    R = {Path(f).stem: json.load(open(f)) for f in sorted(glob.glob(str(SRC / arm / "*.json")))}
    for r in R.values():
        for x in r["eras"].values():
            four = [x[c] for c in ("none", "foragers", "herders", "farmers")]
            o = {k: x["all"][k] - sum(f[k] for f in four) for k in ADD}
            for k in SHR:
                o[k] = (x["all"][k] * x["all"]["supply_t"] - sum(f[k] * f["supply_t"] for f in four)) / o["supply_t"] if o["supply_t"] > 0 else 0.0
            x["others"] = o
    return R


def era_table(runs):
    tab = {}
    for e in ERAS:
        if not all(e in r["eras"] for r in runs.values()):
            continue
        tab[e] = {"ago": [r["eras"][e]["ago"] for r in runs.values()]}
        for c in CLASSES:
            R = [r["eras"][e][c] for r in runs.values()]
            cells = sum(x["cells"] for x in R)
            drag = sum(x["dragons"] for x in R)
            sup = sum(x["supply_t"] for x in R)
            per = [1000.0 * x["dragons"] / (x["cells"] * CELL_KM2) for x in R if x["cells"] > 0]
            shares = {k: (sum(x[k] * x["supply_t"] for x in R) / sup if sup > 0 else 0.0) for k in ("stock", "peoples", "giants", "guild", "food", "dragons_need")}
            area = cells * CELL_KM2
            food = sum(x["food_t"] for x in R)
            tab[e][c] = {"cells": cells, "km2": area, "dragons": drag, "per_1000km2": 1000.0 * drag / area if area else None,
                         "per_1000km2_runs": per, "per_1000km2_runs_min": min(per, default=None), "per_1000km2_runs_max": max(per, default=None),
                         "per_1000km2_runs_median": float(np.median(per)) if per else None,
                         "supply_t_km2_yr": sup / area if area else None, "prey_t_km2": sup / area / MG.OFFTAKE if area else None, "shares": shares,
                         "occupied_share": sum(x["occupied_cells"] for x in R) / cells if cells else None,
                         "food_fed_per_1000km2": 1000.0 * food / food_t / area if area else None,
                         "food_in_occupied_share": sum(x["food_t_occupied"] for x in R) / food if food > 0 else None,
                         "food_fed_occupied_per_1000km2": 1000.0 * sum(x["food_t_occupied"] for x in R) / food_t / (sum(x["occupied_cells"] for x in R) * CELL_KM2)
                         if sum(x["occupied_cells"] for x in R) else None}
        land = tab[e]["all"]["cells"]
        for c in CLASSES:
            tab[e][c]["land_share"] = tab[e][c]["cells"] / land if land else None
    return tab


ON, OFF, NOPER = load("on"), load("off"), load("noper")
out["runs"] = {"on": sorted(ON), "off": sorted(OFF), "noper": sorted(NOPER), "rev": sorted({r.get("rev") for r in [*ON.values(), *OFF.values(), *NOPER.values()]}, key=str),
               "secs_median": float(np.median([r["secs"] for r in ON.values()]))}
for arm, R in (("on", ON), ("off", OFF), ("noper", NOPER)):
    out[arm] = {"eras": era_table(R), "present_dragons_per_run": {k: r["present"]["dragons"] for k, r in R.items()},
                "present_giants_per_run": {k: r["present"]["giants"] for k, r in R.items()}}
    v = list(out[arm]["present_dragons_per_run"].values())
    out[arm]["present_dragons_mean"] = float(np.mean(v)) if v else None
on7 = {k: v for k, v in ON.items() if k.endswith("_7000")}
off7 = {k: v for k, v in OFF.items() if k.endswith("_7000")}
out["on_7000"] = {"eras": era_table(on7)}
out["off_7000"] = {"eras": era_table(off7)}

# paired: on / off per world and roll (same world, same roll), per era and class; and the class areas' divergence between the arms
paired = {}
for e in ERAS:
    paired[e] = {}
    for c in CLASSES:
        rs, area_ratio = [], []
        for k in ON:
            if k not in OFF or e not in ON[k]["eras"] or e not in OFF[k]["eras"]:
                continue
            a, b = ON[k]["eras"][e][c], OFF[k]["eras"][e][c]
            if a["cells"] and b["cells"]:
                da, db = a["dragons"] / a["cells"], b["dragons"] / b["cells"]
                if db > 0:
                    rs.append({"run": k, "ratio": da / db})
                area_ratio.append(a["cells"] / b["cells"])
        r = [x["ratio"] for x in rs]
        paired[e][c] = {"n": len(r), "min": min(r, default=None), "median": float(np.median(r)) if r else None, "max": max(r, default=None),
                        "geo_mean": float(np.exp(np.mean(np.log(np.maximum(r, 1e-12))))) if r else None, "runs": rs,
                        "area_on_over_off_min": min(area_ratio, default=None), "area_on_over_off_max": max(area_ratio, default=None)}
        pon, poff = out["on"]["eras"].get(e, {}).get(c, {}), out["off"]["eras"].get(e, {}).get(c, {})
        paired[e][c]["pooled"] = (pon["per_1000km2"] / poff["per_1000km2"]) if pon and poff and poff.get("per_1000km2") else None
out["paired"] = paired
# the three channels, roll 7000: on -> noper (persecution) -> off (overkill); the peoples' hunting of the wild offtake stays in all three
# (its share: 1 - the peoples' share of the supply in the off arm)
ch = {}
for e in ERAS:
    ch[e] = {}
    for c in CLASSES:
        row = {}
        for nm, R in (("on", on7), ("noper", NOPER), ("off", off7)):
            x = era_table(R).get(e, {}).get(c) if R else None
            row[nm] = x["per_1000km2"] if x else None
            row[nm + "_peoples_share"] = x["shares"]["peoples"] if x else None
        # per world (roll 7000): persecution = on / noper, overkill = noper / off; the nobody's row is the arm's noise control
        per_ = []
        for k in sorted(NOPER):
            if k not in on7 or k not in off7 or e not in NOPER[k]["eras"]:
                continue
            a, b, d = on7[k]["eras"][e][c], NOPER[k]["eras"][e][c], off7[k]["eras"][e][c]
            if a["cells"] and b["cells"] and d["cells"] and b["dragons"] > 0 and d["dragons"] > 0:
                x, y, z = a["dragons"] / a["cells"], b["dragons"] / b["cells"], d["dragons"] / d["cells"]
                # the peoples' wild offtake (in every arm): the share of the wild herds' surplus left after the peoples' hunters take
                # theirs, in the off arm (no overkill, no kill); the dragons are held to their food, so ~ the share of their density kept
                per_.append({"run": k, "persecution": x / y, "overkill": y / z, "offtake": 1.0 - d["peoples"]})
        for nm in ("persecution", "overkill", "offtake"):
            v = [p[nm] for p in per_]
            row[nm + "_runs"] = {"n": len(v), "min": min(v, default=None), "median": float(np.median(v)) if v else None, "max": max(v, default=None),
                                 "by_run": {p["run"]: p[nm] for p in per_}}
        ch[e][c] = row
out["channels_7000"] = ch

# ---- per-cell: all runs' cells files ---------------------------------------------------------------------------------------
BIOMES = ("forest", "grassland", "desert", "tundra", "mountain", "wetland", "other")


def cell_load(arm, key, e):
    f = SRC / arm / "cells" / f"{key}.npz"
    if not f.exists():
        return None
    z = np.load(f)
    if f"land_{e}" not in z:
        return None
    tags = [str(t) for t in z["biome_tags"]]
    bits = z[f"biome_bits_{e}"].astype(np.int64)
    has = {t: (bits >> i) & 1 == 1 for i, t in enumerate(tags)}
    biome = np.full(len(bits), 6)
    order = [(4, has["mountain"]), (3, has["tundra"]), (2, has["desert"]), (5, has["wetland"]), (0, has["forest"] | has["jungle"]),
             (1, has["steppe"] | has["open"])]
    for code, cond in reversed(order):  # the first in `order` wins: mountain, tundra, desert, wetland, forest, grassland
        biome = np.where(cond, code, biome)
    land = z[f"land_{e}"]
    pp = {c: z[f"people_{c}_{e}"].astype(float) for c in ("foragers", "herders", "farmers", "others")}
    allp = sum(pp.values())
    cls = np.full(len(land), -1)
    cls[land] = 0  # nobody's
    cls[land & (allp >= 0.02)] = 1  # others' unless a named way leads
    for k, c in ((2, "foragers"), (3, "herders"), (4, "farmers")):
        cls[land & (allp >= 0.02) & np.all([pp[c] >= pp[o] for o in pp if o != c], axis=0)] = k
    d = {"land": land, "cls": cls, "biome": biome, "allp": allp, "dragons": z[f"dragons_{e}"].astype(float),
         "food_fed": z[f"food_{e}"].astype(float) / float(z["food_t_per_dragon"]), "prey": z[f"prey_{e}"].astype(float),
         "press": z[f"press_{e}"].astype(float), "present": z[f"dragon_present_{e}"] > 0, "lat": z["lat"], "lon": z["lon"]}
    if e == "0":
        d["S"] = z["S_dragons_now"].astype(float).max(0)
    return d


def pooled(arm, keys, e):
    parts = [cell_load(arm, k, e) for k in keys]
    parts = [p for p in parts if p is not None]
    if not parts:
        return None
    for i, p in enumerate(parts):
        p["run"] = np.full(len(p["land"]), i)
        p["run_dragons"] = np.full(len(p["land"]), float(p["dragons"][p["land"]].sum()))
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}, len(parts)


def runstats(C, s, nrun):
    """Per-run spread of a pooled cell set: runs with 30+ cells, their densities per 10,000 km2, and the largest share of a run's dragons
    the set holds (does one place carry a run?)."""
    per, top = [], 0.0
    for i in range(nrun):
        si = s & (C["run"] == i)
        if si.sum() >= 30:
            per.append(1e4 * float(C["dragons"][si].mean()))
        tot = C["run_dragons"][C["run"] == i][:1]
        if tot.size and tot[0] > 0:
            top = max(top, float(C["dragons"][si].sum() / tot[0]))
    return {"runs_30": len(per), "runs_n": nrun, "per_10000km2_run_median": float(np.median(per)) if per else None,
            "per_10000km2_run_min": min(per, default=None), "per_10000km2_run_max": max(per, default=None), "top_run_dragon_share": top}


CL = {0: "none", 1: "others", 2: "foragers", 3: "herders", 4: "farmers"}
cells_out = {}
for arm in ("on", "off", "noper"):
    keys = sorted({"on": ON, "off": OFF, "noper": NOPER}[arm])
    cells_out[arm] = {}
    for e in ("25", "0"):
        P = pooled(arm, keys, e)
        if P is None:
            continue
        C, nrun = P
        land = C["land"]
        res = {"runs": nrun}
        # rich and poor by class (prey bands), pooled over runs: dragons, the food-fed density, occupancy, food-fed where occupied, pressure, S
        rp = {}
        for code, cn in CL.items():
            r = {}
            for lo, hi, name in ((0.0, 1.0, "poor"), (1.0, 3.0, "middling"), (3.0, 1e9, "rich")):
                s = land & (C["cls"] == code) & (C["prey"] >= lo) & (C["prey"] < hi)
                n = int(s.sum())
                if n < 20:
                    r[name] = None
                    continue
                occ = s & C["present"]
                r[name] = {"cells": n, "km2": n * CELL_KM2, "prey_t_km2": float(C["prey"][s].mean()), "per_1000km2": 1000 * float(C["dragons"][s].mean()),
                           "food_fed_per_1000km2": 1000 * float(C["food_fed"][s].mean()), "occupied_share": float(occ.sum() / n),
                           "food_in_occupied_share": float(C["food_fed"][occ].sum() / max(C["food_fed"][s].sum(), 1e-12)),
                           "per_1000km2_occupied": 1000 * float(C["dragons"][occ].mean()) if occ.any() else None,
                           "food_fed_occupied_per_1000km2": 1000 * float(C["food_fed"][occ].mean()) if occ.any() else None,
                           "press_mean": float(C["press"][s].mean()), "people_mean": float(C["allp"][s].mean()),
                           "lat_abs_median": float(np.median(np.abs(C["lat"][s]))),
                           **({"suitable_share": float((C["S"][s] >= MG.SUITABLE).mean()), "S_mean": float(C["S"][s].mean())} if "S" in C else {})}
            rp[cn] = r
        res["rich_poor"] = rp
        # binned (Figure 3)
        bins = [0.0, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 1e9]
        bl = {}
        for cn, mk in (("none", land & (C["cls"] == 0)), ("peopled", land & (C["cls"] >= 1))):
            rows_ = []
            for lo, hi in zip(bins[:-1], bins[1:]):
                s = mk & (C["prey"] >= lo) & (C["prey"] < hi)
                if s.sum() >= 50:
                    occ = s & C["present"]
                    rows_.append({"lo": lo, "hi": hi, "cells": int(s.sum()), "prey": float(C["prey"][s].mean()), "per_km2": float(C["dragons"][s].mean()),
                                  "food_fed_per_km2": float(C["food_fed"][s].mean()), "occupied_share": float(occ.sum() / s.sum()),
                                  "per_km2_occupied": float(C["dragons"][occ].mean()) if occ.any() else None,
                                  "food_fed_occupied_per_km2": float(C["food_fed"][occ].mean()) if occ.any() else None})
            bl[cn] = rows_
        res["binned"] = bl
        # biome x situation (the game-present table): situations by who holds the cell and how many people per km2
        if e == "0":
            pe = C["allp"]
            peopled = land & (C["cls"] >= 1)
            q = np.quantile(pe[peopled], [0.5, 0.9]) if peopled.any() else [1, 10]
            sit = np.full(len(land), -1)
            sit[land & (C["cls"] == 0)] = 0  # wild
            sit[peopled & np.isin(C["cls"], (2, 3)) & (pe < q[1])] = 1  # frontier: foragers' or herders' country
            sit[peopled & np.isin(C["cls"], (1, 4)) & (pe < q[1])] = 2  # farmed (and others' settled land)
            sit[peopled & (pe >= q[1])] = 3  # city hinterland: the densest tenth of peopled land
            SIT = ("wild", "frontier", "farmed", "city hinterland")
            bs = {}
            for bi, bn in enumerate(BIOMES):
                bs[bn] = {}
                for si, sn in enumerate(SIT):
                    s = land & (C["biome"] == bi) & (sit == si)
                    n = int(s.sum())
                    bs[bn][sn] = None if n < 30 else {
                        "cells": n, "km2": n * CELL_KM2, "per_10000km2": 1e4 * float(C["dragons"][s].mean()),
                        "food_fed_per_10000km2": 1e4 * float(C["food_fed"][s].mean()), "occupied_share": float((s & C["present"]).sum() / n),
                        "people_km2_median": float(np.median(pe[s])), "prey_t_km2": float(C["prey"][s].mean()),
                        "lat_abs_median": float(np.median(np.abs(C["lat"][s]))), "press_mean": float(C["press"][s].mean()),
                        "share_under_025_people": float((pe[s] < 0.25).mean()), **runstats(C, s, nrun)}
            land_n = int(land.sum())
            res["biome_situation"] = {"table": bs, "people_quantiles_peopled": [float(x) for x in q], "situations": SIT,
                                      "biome_land_share": {bn: float((land & (C["biome"] == bi)).sum() / land_n) for bi, bn in enumerate(BIOMES)},
                                      "situation_land_share": {sn: float((land & (sit == si)).sum() / land_n) for si, sn in enumerate(SIT)},
                                      "people_median": {sn: float(np.median(pe[land & (sit == si)])) if (land & (sit == si)).any() else None for si, sn in enumerate(SIT)}}
            # occupancy and suitability where nobody lives (S1), every run
            s = land & (C["cls"] == 0)
            res["none_now"] = {"suitable_share": float((C["S"][s] >= MG.SUITABLE).mean()), "occupied_share": float(C["present"][s].mean()),
                               "press_mean": float(C["press"][s].mean()), "press_max": float(C["press"][s].max()),
                               "food_in_unoccupied_share": float(C["food_fed"][s & ~C["present"]].sum() / C["food_fed"][s].sum())}
        cells_out[arm][e] = res
out["cells"] = cells_out

# ---- dragons over time: one world both arms, and the two steps (30 kyr, 300 kyr) over every run --------------------------------


def series(r):
    return sorted((float(t), v["dragons"]) for t, v in r["series"].items())


out["series"] = {"with_pressure": ON.get("2a7385_7000", {}).get("series"), "no_pressure": OFF.get("2a7385_7000", {}).get("series"),
                 "no_persecution": NOPER.get("2a7385_7000", {}).get("series")}


def step_ratio(r, lo_after, hi_before):
    """dragons just after (younger) over just before (older) a hand-over, from the run's series (kyr ago)."""
    s = series(r)
    before = [v for t, v in s if t >= hi_before]
    after = [v for t, v in s if t <= lo_after]
    if not before or not after:
        return None
    tb = min(t for t, v in s if t >= hi_before)
    ta = max(t for t, v in s if t <= lo_after)
    vb = dict(s)[tb]
    va = dict(s)[ta]
    return {"t_before": tb, "t_after": ta, "before": vb, "after": va, "ratio": va / vb if vb else None}


steps = {}
for arm, R in (("on", ON), ("off", OFF)):
    steps[arm] = {"30": {k: step_ratio(r, 29.9, 30.0) for k, r in R.items()}, "300": {k: step_ratio(r, 299.0, 300.0) for k, r in R.items()},
                  "peak": {k: r["peak"]["dragons"] for k, r in R.items()}}
    for st in ("30", "300"):
        v = [x["ratio"] for x in steps[arm][st].values() if x and x["ratio"]]
        steps[arm][st + "_summary"] = {"min": min(v, default=None), "median": float(np.median(v)) if v else None, "max": max(v, default=None), "n": len(v)}
out["steps"] = steps
# the 30 kyr step's cause: the eras at 31 and 29 kyr (the glacial pass's last step and the recent pass's first), every run
out["step30_eras"] = {arm: {e: {c: {k: out[arm]["eras"][e][c][k] for k in ("land_share", "per_1000km2", "food_fed_per_1000km2", "occupied_share")}
                                for c in CLASSES} for e in ("31", "29") if e in out[arm]["eras"]} for arm in ("on", "off")}

# ---- the Sword Coast referent ---------------------------------------------------------------------------------------------
MI = 1.609344
ns, ew = 1500 * MI, 1000 * MI
sc = {"ns_km": ns, "ew_km": ew, "km2": ns * ew}
lat_c, lon_c = 47.0, 0.5
dlat = ns / (math.pi * R_KM / 180.0)
dlon = ew / (math.pi * R_KM / 180.0 * math.cos(math.radians(lat_c)))
la1, la2 = lat_c - dlat / 2, lat_c + dlat / 2
box_km2 = R_KM ** 2 * math.radians(dlon) * (math.sin(math.radians(la2)) - math.sin(math.radians(la1)))
sc["box"] = {"lat_s": la1, "lat_n": la2, "lon_w": lon_c - dlon / 2, "lon_e": lon_c + dlon / 2, "km2": box_km2}
counts = {}
for e in ("25", "10", "5", "0"):
    counts[e] = {}
    for c in CLASSES:
        a, b = out["on"]["eras"].get(e, {}).get(c), out["off"]["eras"].get(e, {}).get(c)
        if not a:
            continue
        counts[e][c] = {"on": a["per_1000km2"] * sc["km2"] / 1000.0, "on_min": a["per_1000km2_runs_min"] * sc["km2"] / 1000.0,
                        "on_max": a["per_1000km2_runs_max"] * sc["km2"] / 1000.0, "on_median": a["per_1000km2_runs_median"] * sc["km2"] / 1000.0,
                        "off": b["per_1000km2"] * sc["km2"] / 1000.0 if b and b["per_1000km2"] is not None else None,
                        "off_min": b["per_1000km2_runs_min"] * sc["km2"] / 1000.0 if b and b["per_1000km2_runs_min"] is not None else None,
                        "off_max": b["per_1000km2_runs_max"] * sc["km2"] / 1000.0 if b and b["per_1000km2_runs_max"] is not None else None}
sc["counts"] = counts
sc["formula"] = {str(p): coef * p * sc["km2"] for p in (0.6, 1.0, 3.0, 7.0)}
# per kind: the largest single kind's share of all dragons, present, every run (for the viability point)
kind_share = []
for r in ON.values():
    dr = {lid: c for lid, c in r["mf_count"].items() if lid in r.get("gen_yr", {})}
    tot = sum(dr.values())
    if tot:
        kind_share.append(max(dr.values()) / tot)
sc["largest_kind_share"] = {"min": min(kind_share, default=None), "median": float(np.median(kind_share)) if kind_share else None,
                            "max": max(kind_share, default=None)}
out["sword_coast"] = sc

OUT.write_text(json.dumps(out, indent=1, default=float))
for arm in ("on", "off"):
    for e in ("25", "10", "5", "0"):
        E = out[arm]["eras"].get(e)
        if E:
            print(arm, e, {c: (round(E[c]["per_1000km2"] or 0, 3), round(E[c]["land_share"], 3)) for c in CLASSES})
print("paired 0", {c: (paired["0"][c]["min"], paired["0"][c]["median"], paired["0"][c]["max"]) for c in CLASSES})
