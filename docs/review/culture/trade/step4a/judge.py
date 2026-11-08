"""Trade step 4a judge (lane 224; PW-1522 craft goods, PW-1529 handling cost, PW-1530 trading towns): step3d/judge.py plus trading
towns per era (all route towns, and those on the long-haul network), how far each good travels (people-weighted km of its flows between
cultures: median, p90, max) and who exports it, and NOCOST=1 to skip the two cost nudges (the land nudge is the bar). --base also takes
trade.py from $JUDGE_BASE (the goods list changed).

Trade step 3d judge (lane 222; PW-1515 long-haul layer, PW-1519 unmet per good): step3b/judge.py plus each good's unmet share and
rounds, the long-haul layer's size and shape per era, and its steadiness (the nudged runs derived on every frame only, "full").

Step 3b judge (lanes 216 and 216b; PW-1515, PW-1514): routes by group per era, trading-town kinds, caravan-rule inputs, grain
met and unmet, allocation rounds, and the route set's steadiness under the land nudge and the cost nudges.

usage: PLANET_DATA=<data root> uv run python judge.py RUN [--base] [--quick]
  JUDGE_OUT: folder for judge-<TAG>-<RUN>.json (default: the current folder); TAG: the file's tag (default base / new)
  --base: trade_flow.py and trade_routes.py from the folder $JUDGE_BASE (the baseline commit's two files), the rest of planet/ from the
          checkout
  --quick: no nudges (routes, towns, grain, time only)
The land nudge multiplies every land value and every cell's people by U(0.9, 1.1) (seed 1); the cost nudges every mode factor, L and the
toll by U(0.9, 1.1) (seeds 2 and 3). The nudged runs are derived on every frame (last era's routes hold) and judged on every third frame
("full"); "sub" derives every third frame only, as lane 214 did. Rebuilt by lane 216 from lane 213's judge2.py (lane 214's was not kept)."""
import sys, time, json, collections, importlib.util, os
import numpy as np

SP = os.environ.get("JUDGE_OUT", ".")
run = sys.argv[1]
base = '--base' in sys.argv
quick = '--quick' in sys.argv
import planet.lineages as PL
if base:
    for name in ('trade', 'trade_routes', 'trade_flow'):
        spec = importlib.util.spec_from_file_location(f'planet.lineages.{name}', f'{os.environ["JUDGE_BASE"]}/{name}.py')
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f'planet.lineages.{name}'] = mod
        setattr(PL, name, mod)
        spec.loader.exec_module(mod)
from planet import store as S, server
from planet.lineages import brief as B, trade as TR, trade_flow as TF, trade_routes as RT
import os
if os.environ.get('RKEY'): RT.KEY = os.environ['RKEY']
if os.environ.get('RSHARE'): RT.ROUTE_SHARE = float(os.environ['RSHARE'])
if os.environ.get('RHOLD'): RT.ROUTE_HOLD = float(os.environ['RHOLD'])
if os.environ.get('RSPAN'): RT.SPAN = os.environ['RSPAN'] == '1'
if os.environ.get('RROUNDS'): TF.ROUNDS = int(os.environ['RROUNDS'])
for _k, _v in os.environ.items():
    if _k.startswith('TF_'):
        _o = getattr(TF, _k[3:]); setattr(TF, _k[3:], (_v == '1') if isinstance(_o, bool) else type(_o)(_v))
TAG = os.environ.get('TAG') or ('base' if base else 'new')

d = S.find_run(run)
pol = server.polities_doc(d)
att = server.gods_doc(d).get("attitudes")
ctx = B.Ctx(run)
n = ctx.g.n
t0 = time.time()
doc = TF.derive(run, ctx, pol, att)
out = {"run": run, "base": base, "derive_s": round(time.time() - t0, 1)}
eq = ctx.meta["eraq"]
sub = eq["frames"][::3]


def edges(f):
    return {(min(a, b), max(a, b)) for a, b, *_ in f["routes"]}


def pieces(es):
    par = {}
    def find(x):
        while par.setdefault(x, x) != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b in es:
        par[find(a)] = find(b)
    return len({find(x) for x in par})


# --- per era
eras = []
for f in doc["frames"]:
    rs = f["routes"]
    eras.append({"ago": f["ago_kyr"], "stretches": len(rs), "pieces": pieces(edges(f)),
                 "groups": dict(collections.Counter(RT.GROUPS[r[3]] for r in rs)), "modes": dict(collections.Counter(RT.MODES[r[4]] for r in rs)),
                 "hubs": dict(collections.Counter(h["kind"] for h in f["hubs"])), "n_hubs": len(f["hubs"])})
out["eras"] = eras
with_towns = [e for e in eras if e["n_hubs"] > 0 or e["ago"] <= 6.0]
out["eras_with_towns"] = len([e for e in eras if e["n_hubs"] > 0])
out["eras_food_and_other"] = len([e for e in eras if e["n_hubs"] > 0 and e["groups"].get("food") and any(e["groups"].get(g) for g in ("metal", "precious", "raw"))])
out["eras_nonsalt_two_kinds"] = len([e for e in eras if e["n_hubs"] > 0 and sum(1 for g in ("food", "metal", "precious", "raw") if e["groups"].get(g)) >= 2])
out["eras_group_present"] = {g: len([e for e in eras if e["n_hubs"] > 0 and e["groups"].get(g)]) for g in RT.GROUPS}
out["hubs_total"] = dict(sum((collections.Counter(e["hubs"]) for e in eras), collections.Counter()))
out["mean_stretches"] = round(float(np.mean([e["stretches"] for e in eras])), 1)
out["mean_pieces"] = round(float(np.mean([e["pieces"] for e in eras])), 1)
out["max_pieces"] = max(e["pieces"] for e in eras)
# goods on the routes (by the route's leading good is not kept; count hub goods instead)
out["hub_goods"] = dict(collections.Counter(g for f in doc["frames"] for h in f["hubs"] for g in h["goods"][:2]).most_common(12))

# --- caravan inputs (land-mode route stretches into unfarmed Koppen B cells beside farmed ones)
cv = collections.Counter()
for f in doc["frames"]:
    if not f["routes"]:
        continue
    i = f["frame"]
    X = TR.cells_at(ctx, i)
    farm = X["farm"]
    clim = np.asarray(ctx.f("climate", i)).astype(int)
    arid = np.isin(clim, RT.ARID) & X["land"]
    towns = RT.towns_at(ctx, -float(ctx.ts[i]))
    for a, b, s, g, m, *_ in f["routes"]:
        cv["stretches"] += 1
        if m != 0:
            continue
        cv["land"] += 1
        for x, y in ((a, b), (b, a)):
            if arid[y]:
                cv["land_into_arid"] += 1
                if farm[y] <= 0:
                    cv[".. unfarmed"] += 1
                    if farm[x] > 0:
                        cv[".. .. from farmed"] += 1
                        if x in towns:
                            cv[".. .. .. town on farmed end"] += 1
    arid_any = arid.sum()
    cv["arid_cells_frames"] += int(arid_any)
    cv["arid_unfarmed_cells_frames"] += int((arid & (farm <= 0)).sum())
    for k in ("trade_cells", "trade_ledger", "trade_pairs"):
        ctx._frame_cache.pop((k, i), None)
out["caravan_inputs"] = dict(cv)

# --- herders' grain (herder culture-frames with grain lack >= 0.05, herding the biggest way; share of the lack met by other cultures)
led = TR.derive(run, ctx)
rows = {f["frame"]: f["cultures"] for f in led["frames"]}
way = lambda r: max(("farm", "herd", "forage"), key=lambda k: r["ways"][k])  # noqa: E731
hs = []
for f in doc["frames"]:
    R = rows.get(f["frame"], {})
    gin = collections.defaultdict(float)
    for x in f["flows"]:
        if x[2] == "grain" and x[8] != "tribute" and x[0] != x[1]:
            gin[x[1]] += x[3]
    for c, r in R.items():
        if r.get("mode", "trade") == "trade" and way(r) == "herd" and r["lack"].get("grain", 0) >= 0.05:
            hs.append((r["lack"]["grain"], gin[int(c)]))
a = np.array(hs) if hs else np.zeros((0, 2))
ug = []
for f in doc["frames"]:
    R = rows.get(f["frame"], {})
    ug.append(sum(v.get("grain", 0) * (R.get(c) or {}).get("people", 0) for c, v in f["unmet"].items()))
need = [sum(r["lack"].get("grain", 0) * r.get("people", 0) for r in rows.get(f["frame"], {}).values()) for f in doc["frames"]]
out["grain_unmet_share_last6"] = [round(u / max(nd, 1), 3) for u, nd in zip(ug[-6:], need[-6:])]
out["grain_unmet_share_all"] = round(sum(ug) / max(sum(need), 1), 3)
rds = [f.get("rounds") or {} for f in doc["frames"]]
out["grain_rounds"] = {"mean": round(float(np.mean([r.get("grain", 0) for r in rds])), 1), "max": max(r.get("grain", 0) for r in rds)} if rds and rds[0] else None
out["rounds_max_any_good"] = max((max(r.values(), default=0) for r in rds), default=None)
gneed, gun = collections.defaultdict(float), collections.defaultdict(float)
for f in doc["frames"]:  # (each good's lack in the units of the doc's "unmet": per pair lack x w / wsum of its culture, x the culture's people)
    R = rows.get(f["frame"], {})
    P = TR.pairs_at(ctx, f["frame"])
    ppl = np.array([float((R.get(str(c)) or R.get(c) or {}).get("people", 0)) if (R.get(str(c)) or R.get(c) or {}).get("mode", "trade") == "trade"
                    else 0.0 for c in P["culture"].tolist()])
    ws = np.array([P["wsum"].get(int(c), 1.0) for c in P["culture"].tolist()])
    for g, lk in P["lack"].items():
        gneed[g] += float((np.maximum(lk, 0) * P["w"] / ws * ppl).sum())
    for c, v in f["unmet"].items():
        for g, x in v.items():
            gun[g] += x * (R.get(c) or {}).get("people", 0)
    for k in ("trade_cells", "trade_ledger", "trade_pairs"):
        ctx._frame_cache.pop((k, f["frame"]), None)
out["unmet_by_good"] = {g: round(gun[g] / gneed[g], 3) for g in sorted(gneed) if gneed[g] > 0}
out["capped_by_good"] = dict(sum((collections.Counter(f.get("capped") or {}) for f in doc["frames"]), collections.Counter()))
out["rounds_by_good_max"] = {g: max(r.get(g, 0) for r in rds) for g in sorted({g for r in rds for g in r})}


def degree_stats(es):
    deg = collections.Counter()
    for a, b in es:
        deg[a] += 1
        deg[b] += 1
    nodes = len(deg)
    return {"stretches": len(es), "pieces": pieces(es) if es else 0, "junctions": sum(1 for v in deg.values() if v >= 3),
            "ends": sum(1 for v in deg.values() if v == 1), "loops": len(es) - nodes + (pieces(es) if es else 0)}


lh = []
for f in doc["frames"]:
    rs = f["routes"]
    if rs and len(rs[0]) > 5:
        L = {(min(r[0], r[1]), max(r[0], r[1])) for r in rs if r[5] & 1}
        lh.append({"ago": f["ago_kyr"], **degree_stats(L), "groups": dict(collections.Counter(RT.GROUPS[r[7]] for r in rs if r[5] & 1)),
                   "modes": dict(collections.Counter(RT.MODES[r[4]] for r in rs if r[5] & 1)), "local": sum(1 for r in rs if r[5] & 2),
                   "local_groups": dict(collections.Counter(RT.GROUPS[r[9]] for r in rs if r[5] & 2)), "both": sum(1 for r in rs if r[5] == 3),
                   "all": len(rs)})
out["long_haul"] = lh
out["eras_food_routes"] = [e["ago"] for e in eras if e["groups"].get("food")]
out["herders_grain"] = {"n": len(a), "mean_ratio": round(float((a[:, 1] / a[:, 0]).mean()), 4) if len(a) else None,
                        "sum_ratio": round(float(a[:, 1].sum() / a[:, 0].sum()), 4) if len(a) else None,
                        "any": round(float((a[:, 1] > 0).mean()), 3) if len(a) else None}

# --- trading towns per era (PW-1530) and how far each good goes, who exports it (PW-1522)
out["towns_per_era"] = [{"ago": f["ago_kyr"], "route_towns": len(f["hubs"]), "long": sum(1 for h in f["hubs"] if h.get("long")),
                         "trading": sum(1 for h in f["hubs"] if h.get("trading", h.get("long"))),
                         "kinds_trading": dict(collections.Counter(h["kind"] for h in f["hubs"] if h.get("trading", h.get("long")))),
                         "quarters": len(f.get("quarters") or [])} for f in doc["frames"]]
names = [c["name"] for c in doc["cultures"]]
gk = collections.defaultdict(list)
gx = collections.defaultdict(collections.Counter)
gm = collections.defaultdict(collections.Counter)
for f in doc["frames"]:
    for x in f["flows"]:
        gv, tk, g, sh, ppl, km, cw, mode, kind, via = x
        if gv == tk or kind == "tribute" or ppl <= 0:
            continue
        gk[g].append((km, ppl))
        gx[g][gv] += ppl
        gm[g][mode] += ppl
def wq(v, q):
    v = sorted(v)
    tot = sum(w for _, w in v)
    acc = 0
    for k, w in v:
        acc += w
        if acc >= q * tot:
            return k
    return v[-1][0] if v else None
out["goods_reach"] = {g: {"flows": len(v), "people": int(sum(w for _, w in v)), "km_median": wq(v, 0.5), "km_p90": wq(v, 0.9),
                          "km_max": max(k for k, _ in v), "share_over_500km": round(sum(w for k, w in v if k >= 500) / max(sum(w for _, w in v), 1), 3),
                          "modes": {m: round(c / max(sum(gm[g].values()), 1), 2) for m, c in gm[g].most_common()},
                          "exporters": [[names[c] if 0 <= c < len(names) else c, round(p / max(sum(gx[g].values()), 1), 3)] for c, p in gx[g].most_common(4)],
                          "n_exporters": len(gx[g])} for g, v in sorted(gk.items())}
out["n_cultures"] = len(names)

# --- grain route km: where food routes run, how long are their pieces
if quick:
    print(json.dumps(out, indent=1))
    json.dump(out, open(f"{SP}/judge-{TAG}-{run}.json", "w"), indent=1)
    sys.exit()

# --- steadiness
R0 = {f["frame"]: f for f in doc["frames"]}


def jac(dB, frames, layer=None):
    rb = {f["frame"]: f for f in dB["frames"]}
    if layer is not None:  # (one layer of the routes only: 1 long-haul, 2 local)
        sel = lambda f: {**f, "routes": [r for r in f["routes"] if len(r) > 5 and r[5] & layer]}  # noqa: E731
        rb = {k: sel(v) for k, v in rb.items()}
        r0 = {k: sel(v) for k, v in R0.items()}
    else:
        r0 = R0
    v, w, h = [], [], []
    for i in frames:
        if i not in r0 or i not in rb:
            continue
        a, b = edges(r0[i]), edges(rb[i])
        if a or b:
            v.append(len(a & b) / len(a | b))
            la = {(min(x[0], x[1]), max(x[0], x[1])): x[2] for x in r0[i]["routes"]}
            lb = {(min(x[0], x[1]), max(x[0], x[1])): x[2] for x in rb[i]["routes"]}
            ks = set(la) | set(lb)
            w.append(sum(min(la.get(k, 0), lb.get(k, 0)) for k in ks) / max(sum(max(la.get(k, 0), lb.get(k, 0)) for k in ks), 1e-12))
        ha = {(x["cell"], x["kind"]) for x in r0[i]["hubs"]}
        hb = {(x["cell"], x["kind"]) for x in rb[i]["hubs"]}
        if ha or hb:
            h.append(len(ha & hb) / len(ha | hb))
    return {"routes": round(float(np.mean(v)), 3) if v else None, "routes_min": round(float(np.min(v)), 3) if v else None,
            "routes_loadw": round(float(np.mean(w)), 3) if w else None, "by_frame": [round(float(x), 3) for x in v], "towns": round(float(np.mean(h)), 3) if h else None, "frames": len(v)}


orig = TR.cells_at


def nudge_land(frames):
    rng = np.random.default_rng(1)

    def nudged(c, i):
        X = orig(c, i)
        if X is None or X.get("_nudged"):
            return X
        Y = dict(X)
        what = os.environ.get("RNUDGE", "both")  # (both, or only "val" or only "heads": which part of the land nudge moves the routes)
        nv = {g: np.clip(v * (1 + rng.uniform(-0.1, 0.1, v.shape)), 0, 1) for g, v in X["val"].items()}
        nh = X["heads"] * (1 + rng.uniform(-0.1, 0.1, X["heads"].shape))
        Y["val"] = nv if what in ("both", "val") else X["val"]
        Y["heads"] = nh if what in ("both", "heads") else X["heads"]
        Y["_nudged"] = True
        c._frame_cache[("trade_cells", i)] = Y
        return Y
    for k in list(ctx._frame_cache):
        if k[0] in ("trade_cells", "trade_ledger", "trade_pairs"):
            ctx._frame_cache.pop(k)
    TR.cells_at = nudged
    try:
        return TF.derive(run, ctx, pol, att, frames=frames)
    finally:
        TR.cells_at = orig
        for k in list(ctx._frame_cache):
            if k[0] in ("trade_cells", "trade_ledger", "trade_pairs"):
                ctx._frame_cache.pop(k)


if os.environ.get("RNUDGE"):  # (the land nudge's parts only)
    out["land_nudge_full"] = jac(nudge_land(None), sub)
    out["land_nudge_sub"] = out["land_nudge_full"]
    out["cost_nudge"] = []
    json.dump(out, open(f"{SP}/judge-{TAG}-{run}.json", "w"), indent=1)
    sys.exit()
dl = nudge_land(None)
out["land_nudge_full"] = jac(dl, sub)
out["land_nudge_long"] = jac(dl, sub, 1)
out["land_nudge_local"] = jac(dl, sub, 2)
res = []
for seed in (() if os.environ.get("NOCOST") else (2, 3)):
    r2 = np.random.default_rng(seed)
    scale = {"L": float(r2.uniform(0.9, 1.1)), "toll": float(r2.uniform(0.9, 1.1)),
             "modes": {k: float(r2.uniform(0.9, 1.1)) for k in ("porter", "pack", "cart", "sea", "canoe", "down", "up")}}
    dc = TF.derive(run, ctx, pol, att, scale=scale)
    res.append({"seed": seed, "full": jac(dc, sub), "long": jac(dc, sub, 1), "local": jac(dc, sub, 2)})
out["cost_nudge"] = res
json.dump(out, open(f"{SP}/judge-{TAG}-{run}.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("eras", "long_haul")}, indent=1))
