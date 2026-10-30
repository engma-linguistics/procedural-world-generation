"""probe.py WORLD ROLL OUT.json [--ages NAME] [--gen MODE] [--gen-yr YR] [--no-cap] [--no-budget] [--no-people-prod] [--no-press] [--no-persecute] [--natural NAME] [--eras 25,10,0] [--save DIR]: one dnd history run of a world at a roll.

Writes OUT.json: the peoples' cells, the megafauna's coverage and counts (present, and the deep-time peak), blue dragons in deserts,
frost giants in tundra, the dragons' food use (PW-977 stage 1) and the counts over time. For the sweep (6 worlds x rolls 7000-7003):
    for w in 2a7385 1df1c3 e71172 6909cb a12762 067778; do for r in 7000 7001 7002 7003; do echo $w $r; done; done |
      xargs -P 8 -n 2 sh -c 'NUMBA_NUM_THREADS=2 uv run python docs/review/megafauna/probe.py $0 $1 OUT/$0_$1.json'
and `table.py`-style comparisons read the OUT.json files.

The overrides measure a setting without editing the tree: --ages (meta.dragon_ages), --gen (meta.dragon_generation: schedule | line |
schedule_mass), --gen-yr (the dragon lines' generation_yr), --no-cap (megafauna.FOOD_CAP off: the dragons are not held to their food),
--no-budget (megafauna.BUDGET off: the dragons get all the wild offtake and the stock, PW-977 stage 1), --no-people-prod (PW-974 off: a people's
density is its way-of-life number everywhere), --no-press (a diagnostic, not a model setting: the peoples press the megafauna not at all, so the
dragons stand at their natural density wherever the food budget lets them; it shows what the budget alone does through time).
--no-persecute (a diagnostic: the dragons are not pressed toward meta.dragon_km2, but the peoples' overkill still cuts the wild herds; with
the default and --no-press it splits the pressure's two channels). --cells DIR writes DIR/WORLD_ROLL.npz, float32 per-cell fields at each
--eras step (the budget, the peoples by way of life, the dragons, their presence, biome tag bits) and the dragons' suitability now (review r2).
PROBE_REV in the environment is recorded in OUT.json as "rev".
--natural NAME (meta.megafauna_natural: food, the default since PW-990 B | prey | mesotherm | mammal).
--eras 25,10,0 adds the budget sums at those eras to OUT.json; with --save it also writes DIR/ERAS.npz: the budget, presences and dragons at the steps nearest those kyr ago.

--save DIR also writes DIR/RUN.npz and DIR/SERIES.json, the inputs of age_of_dragons.py (the PW-967 review): presences, the megafauna's
suitability, the peoples' pressure, the prey field (wild before and after overkill, livestock), the dragons' food and the present summary.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

from planet.lineages import land as LD
from planet.lineages import landuse as LU
from planet.lineages import prey as PR
from planet.lineages import recent as R
from planet.lineages import run as LR
from planet.lineages.history import megafauna as MG
from planet.lineages.history.model import History
from planet.lineages.history.summary import present_summary
from planet.lineages.spread import EST

ap = argparse.ArgumentParser()
ap.add_argument("world")
ap.add_argument("roll", type=int)
ap.add_argument("out")
ap.add_argument("--ages")
ap.add_argument("--gen")
ap.add_argument("--gen-yr", type=float)
ap.add_argument("--no-cap", action="store_true")
ap.add_argument("--no-budget", action="store_true")
ap.add_argument("--no-people-prod", action="store_true")
ap.add_argument("--no-press", action="store_true")
ap.add_argument("--no-persecute", action="store_true")
ap.add_argument("--cells")
ap.add_argument("--natural")
ap.add_argument("--eras")
ap.add_argument("--tree", default="dnd")
ap.add_argument("--save")
a = ap.parse_args()

if a.no_cap:
    MG.FOOD_CAP = False
if a.no_budget and hasattr(MG, "BUDGET"):
    MG.BUDGET = False
if a.no_press:
    MG.PRESS_N0 = 1e12
if a.no_persecute:  # (the dragons are not pressed toward meta.dragon_km2, but the overkill still cuts the wild herds: the third arm)
    _pressed0 = MG._pressed

    def _pressed_np(h, k, s, prey, food=None, _o=_pressed0):
        return _o(h, k, 0.0 * s if "flies" in h.lines[k].traits else s, prey, food)
    MG._pressed = _pressed_np
if a.no_people_prod:
    import planet.lineages.history.model as _model
    _model.PEOPLE_PROD = False
BIOME_TAGS = ("mountain", "tundra", "desert", "wetland", "forest", "jungle", "steppe", "open", "farmland", "hills", "coast", "island", "lowland")
tree = LR.load_tree(a.tree)
if a.natural:
    tree.megafauna_natural = a.natural
if a.ages:
    tree.dragon_ages = a.ages
if a.gen:
    tree.dragon_generation = a.gen
if a.gen_yr:
    for l in tree.lines.values():
        if l.megafauna and "flies" in l.traits:
            l.generation_yr = a.gen_yr
tz, now0, wid = R.resolve(a.world)
ps = R.Pass(tz, now0, R.RecentParams(kyr=30.0, climate_every=2.0), world_ref=wid)
goods = LD.goods(wid) if (wid and tree.uses) else None
t0 = time.time()
h = History(tree, ps, a.roll, goods=goods)
eras = {}
if a.eras:
    targets = [float(x) for x in a.eras.split(",")]
    _orig = h._start_due

    def _start(step, env, tags, Ks, _o=_orig):
        if step.epoch != "deep" and h._press is not None:
            for e in targets:
                if e not in eras or abs(step.ago - e) < abs(eras[e]["ago"] - e):
                    b = MG.budget(h, h.p, h._press, tags)
                    fl = [k for k, l in enumerate(h.lines) if l.megafauna and "flies" in l.traits]
                    nd = sum((np.where(h.p[k] >= EST, h.p[k], 0.0) * MG.local_density(h, k, h._press, b["prey"], b["food"], h.p) for k in fl), np.zeros(h.grid.n))
                    gd = sum((np.where(h.p[k] >= EST, h.p[k], 0.0) * MG.local_density(h, k, h._press, b["prey"]) for k in fl), np.zeros(h.grid.n))
                    cls = {"foragers": np.zeros(h.grid.n), "herders": np.zeros(h.grid.n), "farmers": np.zeros(h.grid.n), "others": np.zeros(h.grid.n)}
                    dm = h.dens_cells()
                    for k, l in enumerate(h.lines):  # (the peoples' density per cell by how the people lives: its larger share of use)
                        if l.megafauna or l.overlay:
                            continue
                        sh = LU.shares(tree, l)
                        c = "herders" if sh["herd"] >= 0.5 else "farmers" if sh["farm"] >= 0.5 else "foragers" if (sh["forage"] > 0 or l.way in ("fisher_forager", "sea_nomad")) else "others"
                        cls[c] += np.where(h.p[k] >= EST, h.p[k], 0.0) * dm[k]
                    pres_any = np.max([np.where(h.p[k] >= EST, 1.0, 0.0) for k in fl], axis=0) if fl else np.zeros(h.grid.n)
                    bits = np.zeros(h.grid.n, np.uint16)
                    for bi, tg in enumerate(BIOME_TAGS):
                        if tg in tags:
                            bits |= (np.asarray(tags[tg], bool).astype(np.uint16) << bi)
                    eras[e] = {"ago": step.ago, "dragon_present": pres_any, "biome_bits": bits, "press": h._press.copy(), "land": np.asarray(env["land"]), "dragons": nd, "dragons_uncapped": gd,
                               **{"people_" + c: v for c, v in cls.items()}, **{k: np.asarray(v, float) for k, v in b.items()}}
        return _o(step, env, tags, Ks)
    h._start_due = _start
res = h.run()
P = res["present"]
pres = present_summary(h, P)
peoples = {}
for l in tree.leaves():
    if l.overlay or l.megafauna or l.group_of or l.marine:
        continue
    k = h.idx[l.id]
    peoples[l.id] = int((h.whole(l.id, P) >= EST).sum()) if h.active.get(l.id) or (P[k] >= EST).any() else 0
pl = pres["lines"]
pop = {lid: pl[lid]["population"] for lid in peoples if lid in pl}  # (PW-974: people, and their patches; the density a people holds per occupied cell)
patches = {lid: pl[lid]["patches"] for lid in peoples if lid in pl}
meand = {}
for lid in peoples:
    k = h.idx[lid]
    occ = P[k] >= EST
    if occ.any():
        d = h.dens_at(k, P)
        meand[lid] = float((np.broadcast_to(d, occ.shape)[occ] * P[k][occ]).sum() / P[k][occ].sum())
lmean = {}  # (PW-974 calibration: per people, its presence-weighted mean of the foraging layer and the grazing NPP over the cells it holds)
for lid in peoples:
    k = h.idx[lid]
    occ = P[k] >= EST
    if occ.any() and ps.forage is not None and ps.graze_npp is not None:
        w = P[k][occ]
        lmean[lid] = {"L_forage": float((ps.forage[occ] * w).sum() / w.sum()), "L_graze": float((ps.graze_npp[occ] * w).sum() / w.sum()),
                      "dens": float(h.dens[k]), **{s: float(v) for s, v in LU.shares(tree, h.lines[k]).items() if s in ("herd", "forage", "farm")}}
mf = pres.get("megafauna", {})
cov = {lid: r.get("suitable_reached") for lid, r in mf.items()}
cnt = {lid: r["count"] for lid, r in mf.items()}
by_t: dict = {}  # counts over time: the frames' populations (tracks)
for l in h.lines:
    if l.megafauna:
        kind = "dragons" if "flies" in l.traits else "giants"
        for row in h.tracks[l.id]:
            d = by_t.setdefault(row[0], {"dragons": 0, "giants": 0})
            d[kind] += row[4]
ts = sorted(by_t, reverse=True)
peak = {}
for kind in ("dragons", "giants"):
    if ts:
        t_ = max(ts, key=lambda t: by_t[t][kind])
        peak[kind] = {"count": by_t[t_][kind], "ago_kyr": t_}
present = {kind: sum(c for lid, c in cnt.items() if ("flies" in tree.lines[lid].traits) == (kind == "dragons")) for kind in ("dragons", "giants")}
stages = [sum(r["stages"][i] for r in mf.values() if r.get("stages")) for i in range(4)]


def in_country(lid, country):
    return sum(p["count"] for p in mf.get(lid, {}).get("pocket_list", []) if p["country"] == country)


# the dragons' food (PW-977): the worst pocket's share of its food (expected need over what the land supplies), of the herders' stock
# (pockets holding >= 20 head), and section 5's old figure, an ancient's yearly kill over the stock in its range as if it ate only stock
pockets = [p for r in mf.values() for p in r["pocket_list"] if "food_use" in p]
fu = [p["food_use"] for p in pockets if p["food_use"] is not None]
st = [p["stock_take"] for p in pockets if p["stock_take"] is not None and p.get("livestock_head", 0) >= 20]
old = [p["ancient_cattle_yr"] / (p["livestock_head"] / max(p["km2"], 1) * p["ancient_range_km2"]) for p in pockets
       if p["stages"][3] and p.get("livestock_head", 0) >= 20 and p.get("ancient_range_km2")]
food = {"worst_food_use": max(fu, default=None), "worst_stock_take": max(st, default=None), "worst_ancient_vs_stock": max(old, default=None),
        "pockets_over_food": sum(x > 1.0 + 1e-9 for x in fu), "pockets_over_stock": sum(x > MG.STOCK_TOLERABLE + 1e-9 for x in st),
        "pockets": len(fu)}
# cell level: every cell where dragons are expected
press = MG.pressure(h, P, h._land_now)
bud = MG.budget(h, P, press, h._tags_now)
prey, supply, live = bud["prey"], bud["food"], bud["live"]
dens = {k: MG.local_density(h, k, press, prey, supply, P) for k, l in enumerate(h.lines) if l.megafauna}
fs = MG.food_state(h, P, dens, supply, live, bud["pool"])
if fs is not None:
    use = fs["demand"] / np.maximum(fs["supply"], 1e-12)
    food["worst_cell_food_use"] = float(use.max())
    food["cells_over_food"] = int((use > 1.0 + 1e-9).sum())
eras_sum = {}  # (PW-977 stage 2: per era, the budget summed over the land, t/yr, and the dragons' share of the supply, all and by who lives there)
area_km2 = h.cell_mkm2 * 1e6
for e, r in eras.items():
    lnd = r["land"]
    tot = lambda x, m=lnd: float((np.asarray(x)[m]).sum() * area_km2)
    need = r["dragons"] * h.dragon_struct["cattle_yr"] * PR.HEAD_T
    pp = {c: r["people_" + c] for c in ("foragers", "herders", "farmers", "others")}
    allp = sum(pp.values())
    cls = {"none": lnd & (allp < 0.02)}
    for c in ("foragers", "herders", "farmers"):
        cls[c] = lnd & (allp >= 0.02) & np.all([pp[c] >= pp[o] for o in pp if o != c], axis=0)
    row = {"ago": float(r["ago"]), "dragons": tot(r["dragons"]), "dragons_uncapped": tot(r["dragons_uncapped"])}
    for cn, m in [("all", lnd)] + list(cls.items()):
        sup = tot(r["wild"] + r["stock"], m)
        occ = m & (r["dragon_present"] > 0)
        row[cn] = {"cells": int(m.sum()), "supply_t": sup, "dragons": tot(r["dragons"], m),
                   "occupied_cells": int(occ.sum()), "food_t": tot(r["food"], m), "food_t_occupied": tot(r["food"], occ),
                   **{k: (tot(r[k], m) / sup if sup > 0 else 0.0) for k in ("stock", "peoples", "giants", "guild", "food")},
                   "dragons_need": tot(need, m) / sup if sup > 0 else 0.0}
    eras_sum[f"{e:g}"] = row
extra = {lid: {k: r.get(k) for k in ("count", "one_per_km2", "pressed_one_per_km2", "natural_one_per_km2", "peopled_one_per_km2",
                                     "wild_one_per_km2", "peopled_share", "stages")} for lid, r in mf.items()}
import os
json.dump({"world": a.world, "roll": a.roll, "rev": os.environ.get("PROBE_REV"), "secs": round(time.time() - t0), "args": vars(a), "peoples": peoples, "pop": pop, "patches": patches, "meand": meand, "lmean": lmean, "eras": eras_sum, "mf_cov": cov, "mf_count": cnt,
           "present": present, "stages": stages, "blue_desert": in_country("blue_dragon", "desert"), "blue": cnt.get("blue_dragon", 0),
           "frost_tundra": in_country("frost_giant", "tundra"), "frost": cnt.get("frost_giant", 0), "food": food, "peak": peak,
           "series": {str(t): by_t[t] for t in ts}, "mf_extra": extra, "lost": pres.get("lost"),
           "gen_yr": {lid: round(h.gen_yr(l)) for lid, l in ((l.id, l) for l in h.lines) if l.megafauna and "flies" in l.traits}},
          open(a.out, "w"), indent=1)
print(a.world, a.roll, "done", round(time.time() - t0), "s")

if a.save:
    d = Path(a.save)
    d.mkdir(parents=True, exist_ok=True)
    ids = [l.id for l in h.lines]
    mf_idx = [k for k, l in enumerate(h.lines) if l.megafauna]
    S = h._suit() if getattr(h, "_K_now", None) else np.zeros((len(h.lines), h.grid.n))
    ref = np.asarray(h.prey_wild, float)
    from planet.lineages import prey as PR
    refuge = PR.refuge(h._tags_now)
    f = PR.field(h.prey_wild, press, refuge, PR.stocked(P, h._herd, EST))
    dem = fs["demand"] if fs is not None else np.zeros(h.grid.n)
    np.savez_compressed(d / "RUN.npz", pres=json.dumps(pres, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x)),
                        ids=np.array(ids), mf_ids=np.array([ids[k] for k in mf_idx]), P=P.astype(np.float32), S=S[mf_idx].astype(np.float32),
                        level=h.grid.level if hasattr(h.grid, "level") else 7, land=np.asarray(h._tags_now["land"]), prey=prey, wild0=ref,
                        wild=f["wild"], livestock=f["livestock"], press=press, supply=supply, live=live, demand=dem,
                        stock_take=fs["stock_take"] if fs is not None else np.zeros(h.grid.n),
                        dens=np.array([dens[k] for k in mf_idx], np.float32))
    if eras:
        np.savez_compressed(d / "ERAS.npz", targets=np.array(sorted(eras)), **{f"{k}_{e:g}": v for e, r in eras.items() for k, v in r.items()})
    (d / "SERIES.json").write_text(json.dumps({"series": {str(t): by_t[t] for t in ts}}))
    print("saved", d)

if a.cells:  # (review r2: compact per-cell fields at each era, float32, for the dragon-density page's per-cell tables)
    d = Path(a.cells)
    d.mkdir(parents=True, exist_ok=True)
    fl = [k for k, l in enumerate(h.lines) if l.megafauna and "flies" in l.traits]
    S = h._suit() if getattr(h, "_K_now", None) else np.zeros((len(h.lines), h.grid.n))
    out = {"targets": np.array(sorted(eras)), "biome_tags": np.array(BIOME_TAGS), "lat": np.asarray(h.grid.lat, np.float32),
           "lon": np.asarray(h.grid.lon, np.float32), "dragon_ids": np.array([h.lines[k].id for k in fl]),
           "S_dragons_now": S[fl].astype(np.float16), "P_dragons_now": P[fl].astype(np.float16), "food_t_per_dragon": np.array(h.dragon_struct["cattle_yr"] * PR.HEAD_T)}
    for e, r in eras.items():
        for k, v in r.items():
            if k in ("ago",):
                out[f"{k}_{e:g}"] = np.array(v)
            elif k in ("land",):
                out[f"{k}_{e:g}"] = np.asarray(v, bool)
            elif k == "biome_bits":
                out[f"{k}_{e:g}"] = v
            else:
                out[f"{k}_{e:g}"] = np.asarray(v, np.float32)
    np.savez_compressed(d / f"{a.world}_{a.roll}.npz", **out)
    print("cells", d)
