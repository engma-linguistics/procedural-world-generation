"""Trade step 3b judge (lanes 216 and 216b; PW-1515, PW-1514): routes by group per era, trading-town kinds, caravan-rule inputs, grain
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
    for name in ('trade_routes', 'trade_flow'):
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
    for a, b, s, g, m in f["routes"]:
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
out["eras_food_routes"] = [e["ago"] for e in eras if e["groups"].get("food")]
out["herders_grain"] = {"n": len(a), "mean_ratio": round(float((a[:, 1] / a[:, 0]).mean()), 4) if len(a) else None,
                        "sum_ratio": round(float(a[:, 1].sum() / a[:, 0].sum()), 4) if len(a) else None,
                        "any": round(float((a[:, 1] > 0).mean()), 3) if len(a) else None}

# --- grain route km: where food routes run, how long are their pieces
if quick:
    print(json.dumps(out, indent=1))
    json.dump(out, open(f"{SP}/judge-{TAG}-{run}.json", "w"), indent=1)
    sys.exit()

# --- steadiness
R0 = {f["frame"]: f for f in doc["frames"]}


def jac(dB, frames):
    rb = {f["frame"]: f for f in dB["frames"]}
    v, w, h = [], [], []
    for i in frames:
        if i not in R0 or i not in rb:
            continue
        a, b = edges(R0[i]), edges(rb[i])
        if a or b:
            v.append(len(a & b) / len(a | b))
            la = {(min(x[0], x[1]), max(x[0], x[1])): x[2] for x in R0[i]["routes"]}
            lb = {(min(x[0], x[1]), max(x[0], x[1])): x[2] for x in rb[i]["routes"]}
            ks = set(la) | set(lb)
            w.append(sum(min(la.get(k, 0), lb.get(k, 0)) for k in ks) / max(sum(max(la.get(k, 0), lb.get(k, 0)) for k in ks), 1e-12))
        ha = {(x["cell"], x["kind"]) for x in R0[i]["hubs"]}
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
out["land_nudge_sub"] = jac(nudge_land(sub), sub)  # (as lane 214: the nudged run derived on every third frame only)
out["land_nudge_full"] = jac(nudge_land(None), sub)  # (the nudged run derived on every frame, judged on every third)
res = []
for seed in (2, 3):
    r2 = np.random.default_rng(seed)
    scale = {"L": float(r2.uniform(0.9, 1.1)), "toll": float(r2.uniform(0.9, 1.1)),
             "modes": {k: float(r2.uniform(0.9, 1.1)) for k in ("porter", "pack", "cart", "sea", "canoe", "down", "up")}}
    res.append({"seed": seed, "sub": jac(TF.derive(run, ctx, pol, att, scale=scale, frames=sub), sub),
                "full": jac(TF.derive(run, ctx, pol, att, scale=scale), sub)})
out["cost_nudge"] = res
json.dump(out, open(f"{SP}/judge-{TAG}-{run}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
