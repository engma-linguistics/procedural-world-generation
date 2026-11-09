"""Lane 244 harness: derive the exchange of one run with switches set, save stats (and the doc). usage: h.py run tag [KEY=VAL ...]
KEY=VAL sets planet.lineages.trade / trade_flow module constants (TR.X / TF.X), evaluated with eval()."""
import json, sys, time
import numpy as np
from planet import server, store as S
from planet.lineages import brief as BR, bought_in as BI, trade as TR, trade_flow as TF

run, tag = sys.argv[1], sys.argv[2]
for kv in sys.argv[3:]:
    k, v = kv.split("=", 1)
    mod, name = k.split(".")
    setattr({"TR": TR, "TF": TF}[mod], name, eval(v))
OUT = sys.argv[0].rsplit("/", 1)[0] + "/out"


def wq(v, w, q):
    v, w = np.asarray(v, float), np.asarray(w, float)
    if not len(v):
        return None
    o = np.argsort(v)
    c = np.cumsum(w[o]) / w.sum()
    return int(v[o][min(len(v) - 1, np.searchsorted(c, q))])


t = time.time()
d = S.find_run(run)
pol = server.polities_doc(d)
att = server.gods_doc(d).get("attitudes")
ctx = BR.Ctx(run)
doc = TF.derive(d, ctx=None, pol=pol, att=att)
print(run, tag, "derive", round(time.time() - t), "s", file=sys.stderr, flush=True)
json.dump(doc, open(f"{OUT}/doc-{tag}-{run}.json", "w"))
ctx._trade_flows = doc
led = TR.derive(d)
res = {}
for era in (0.0, 5.0):
    lf = min(led["frames"], key=lambda f: abs(f["ago_kyr"] - era))
    rows = {int(c): r for c, r in lf["cultures"].items() if r.get("mode", "trade") == "trade"}
    per = {g: {"km": [], "w": [], "road": {}, "takers": 0, "max": 0} for g in BI.FOOD_GOODS}
    any_food, herders, samples = 0, [], []
    for c, r in rows.items():
        b = BI.of_culture(ctx, doc, c, era)
        if b is None:
            continue
        ppl = float(r.get("people") or 0)
        any_food += bool(b["foods"])
        for fd in b["foods"]:
            p = per[fd["good"]]
            p["takers"] += 1
            for g in fd["givers"]:
                p["km"].append(g["km"]); p["w"].append(g["share"] * ppl)
                p["max"] = max(p["max"], g["km"])
                p["road"][g["road"]] = p["road"].get(g["road"], 0) + g["share"] * ppl
        w = r.get("ways") or {}
        if (w.get("herd") or 0) >= 0.25:
            gr = next((fd for fd in b["foods"] if fd["good"] == "grain"), None)
            herders.append((ppl, gr["share"] if gr else 0.0, (r.get("lack") or {}).get("grain", 0.0)))
        fish = next((fd for fd in b["foods"] if fd["good"] == "dried_fish"), None)
        far = [g for fd in b["foods"] if fd["good"] == "grain" for g in fd["givers"] if g["km"] >= 3000]
        if fish or far:
            samples.append((c, ppl, b["text"], fish is not None, len(far)))
    H = np.array(herders) if herders else np.zeros((0, 3))
    res[era] = {
        "trading": len(rows), "with_food": any_food,
        "foods": {g: {"takers": p["takers"], "med": wq(p["km"], p["w"], 0.5), "p90": wq(p["km"], p["w"], 0.9), "max": p["max"],
                      "roads": {k: round(v / max(1e-9, sum(p["road"].values())), 2) for k, v in sorted(p["road"].items(), key=lambda kv: -kv[1])}}
                  for g, p in per.items() if p["takers"]},
        "kmw": {g: [[int(k), round(float(w), 1)] for k, w in zip(per[g]["km"], per[g]["w"])] for g in ("grain", "dried_fish")},
        "herders": {"n": len(H), "grain_bought": round(float((H[:, 0] * H[:, 1]).sum() / max(1e-9, H[:, 0].sum())), 4) if len(H) else None},
        "samples": sorted(samples, key=lambda s: -s[1])[:60],
    }
# every good's flows (all eras): count and people-weighted km (the walk is shared)
allg = {}
for f in doc["frames"]:
    for x in f["flows"]:
        allg.setdefault(x[2], [0, 0.0])
        allg[x[2]][0] += 1
        allg[x[2]][1] += x[3]
res["all_flows"] = {g: [n, round(s, 2)] for g, (n, s) in sorted(allg.items())}
json.dump(res, open(f"{OUT}/st-{tag}-{run}.json", "w"), indent=1, default=str)
print(run, tag, "done", round(time.time() - t), "s", file=sys.stderr, flush=True)
