"""probe.py WORLD ROLL OUT.json [--ages NAME] [--gen MODE] [--gen-yr YR] [--no-cap] [--no-budget] [--no-people-prod] [--no-press] [--eras 25,10,0] [--save DIR]: one dnd history run of a world at a roll.

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
--eras 25,10,0 (with --save) also writes DIR/ERAS.npz: the budget, presences and dragons at the steps nearest those kyr ago.

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
if a.no_people_prod:
    import planet.lineages.history.model as _model
    _model.PEOPLE_PROD = False
tree = LR.load_tree(a.tree)
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
                    eras[e] = {"ago": step.ago, "press": h._press.copy(), "land": np.asarray(env["land"]), "dragons": nd, "dragons_uncapped": gd,
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
extra = {lid: {k: r.get(k) for k in ("count", "one_per_km2", "pressed_one_per_km2", "natural_one_per_km2", "peopled_one_per_km2",
                                     "wild_one_per_km2", "peopled_share", "stages")} for lid, r in mf.items()}
json.dump({"world": a.world, "roll": a.roll, "secs": round(time.time() - t0), "args": vars(a), "peoples": peoples, "pop": pop, "patches": patches, "meand": meand, "mf_cov": cov, "mf_count": cnt,
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
