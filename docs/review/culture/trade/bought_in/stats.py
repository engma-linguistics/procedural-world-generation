"""Bought-in food statistics on stored runs (read-only; scratch PLANET_DATA). usage: stats.py run [run ...] > out"""
import json, sys, time
import numpy as np
from planet import server, store as S
from planet.lineages import brief as BR, bought_in as BI


def wq(v, w, q):
    v, w = np.asarray(v, float), np.asarray(w, float)
    if not len(v):
        return None
    o = np.argsort(v)
    c = np.cumsum(w[o]) / w.sum()
    return int(v[o][np.searchsorted(c, q)])


out = {}
for run in sys.argv[1:]:
    t = time.time()
    ctx = BR.Ctx(run)
    doc = ctx.trade_flows()
    led = server.trade_doc(S.find_run(run))
    res = {}
    for era in (0.0, 5.0):
        lf = min(led["frames"], key=lambda f: abs(f["ago_kyr"] - era))
        rows = {int(c): r for c, r in lf["cultures"].items() if r.get("mode", "trade") == "trade"}
        per = {g: {"km": [], "w": [], "road": {}, "takers": 0} for g in BI.FOOD_GOODS}
        wine = {"km": [], "w": []}
        any_food, herders, tribute, flown, samples = 0, [], 0, 0, []
        for c, r in rows.items():
            b = BI.of_culture(ctx, doc, c, era)
            if b is None:
                continue
            ppl = float(r.get("people") or 0)
            if b["foods"]:
                any_food += 1
            if b["flown_in"]:
                flown += 1
            if any(g["road"] == "tribute" for fd in b["foods"] for g in fd["givers"]):
                tribute += 1
            for fd in b["foods"]:
                p = per[fd["good"]]
                p["takers"] += 1
                for g in fd["givers"]:
                    p["km"].append(g["km"]); p["w"].append(g["share"] * ppl)
                    p["road"][g["road"]] = p["road"].get(g["road"], 0) + g["share"] * ppl
                    if "wine" in (g.get("what") or []):
                        wine["km"].append(g["km"]); wine["w"].append(g["share"] * ppl)
            w = r.get("ways") or {}
            if (w.get("herd") or 0) >= 0.25:
                gr = next((fd for fd in b["foods"] if fd["good"] == "grain"), None)
                herders.append((ppl, gr["share"] if gr else 0.0, (r.get("lack") or {}).get("grain", 0.0)))
            if b["foods"]:
                samples.append((c, ppl, b["text"]))
        H = np.array(herders) if herders else np.zeros((0, 3))
        res[era] = {
            "trading_cultures": len(rows), "with_bought_food": any_food, "tribute_takers": tribute, "flown_in": flown,
            "foods": {g: {"takers": p["takers"], "km_median": wq(p["km"], p["w"], 0.5), "km_p90": wq(p["km"], p["w"], 0.9),
                          "roads": {k: round(v / max(1e-9, sum(p["road"].values())), 2) for k, v in sorted(p["road"].items(), key=lambda kv: -kv[1])}}
                      for g, p in per.items() if p["takers"]},
            "wine": {"givers": len(wine["km"]), "km_median": wq(wine["km"], wine["w"], 0.5), "km_p90": wq(wine["km"], wine["w"], 0.9)},
            "herders": {"n": len(H), "grain_bought_people_weighted": round(float((H[:, 0] * H[:, 1]).sum() / max(1e-9, H[:, 0].sum())), 3) if len(H) else None,
                        "grain_lack_people_weighted": round(float((H[:, 0] * H[:, 2]).sum() / max(1e-9, H[:, 0].sum())), 3) if len(H) else None,
                        "with_any_bought_grain": int((H[:, 1] > 0).sum()) if len(H) else 0},
            "samples": [s for s in sorted(samples, key=lambda s: -s[1])[:40]],
        }
    out[run] = res
    print(run, round(time.time() - t), "s", file=sys.stderr, flush=True)
json.dump(out, sys.stdout, indent=1, default=str)
