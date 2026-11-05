"""A switch-on run's live calendar against the after-run tree of the same history (techtree.rebuild), its own seed and 12 seeds
(the run's own and the next 11) for the spread; the live states. argv: run_dir [arms]. Read-only."""
import json, sys
from pathlib import Path
import numpy as np
from planet.lineages import techtree as TT
d = Path(sys.argv[1]); arms = sys.argv[2] if len(sys.argv) > 2 else None
m = json.loads((d / "run.json").read_text())["meta"]
live = m["techtree"]["known"]; seed = int(m.get("try_seed") or 0)
print("run", d.name, "try_seed", seed, "inside_history", m["techtree"].get("inside_history"))
own = TT.rebuild(d, arms=arms)["known"]
S = [TT.rebuild(d, arms=arms, seed=s)["known"] for s in range(seed, seed + 12)]
pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
big = sorted([p for p in live if p in pops], key=lambda p: -pops[p])[:12]
W = ["villages", "towns", "chiefdoms", "tokens", "proto_writing", "writing", "cities", "kingship", "law"]
f = lambda K, p, t: (K.get(p, {}).get(t) or [None])[0]
yr = lambda x: "never" if x is None else f"{int(round(x * 1000)):,}"
out = {"run": d.name, "seed": seed, "rows": {}}
for t in ["writing", "kingship", "law", "cities"]:
    print(f"\n{t}: people | live | after-run (same seed) | 12 seeds: known in, min-median-max | live in the spread")
    inn = 0
    for p in big:
        xs = [f(K, p, t) for K in S]
        k = sorted(x for x in xs if x is not None)
        lv = f(live, p, t)
        ok = (lv is None and len(k) < 12) or (lv is not None and k and k[0] - 1e-9 <= lv <= k[-1] + 1e-9)
        inn += ok
        out["rows"].setdefault(t, {})[p] = {"live": lv, "after": f(own, p, t), "seeds": xs}
        print(f"  {p} | {yr(lv)} | {yr(f(own, p, t))} | {len(k)}/12, {yr(k[0]) if k else '-'}-{yr(float(np.median(k))) if k else '-'}-{yr(k[-1]) if k else '-'} | {'yes' if ok else 'NO'}")
    print(f"  in the spread: {inn}/{len(big)}")
mv = [(f(live, p, t) - f(own, p, t)) * 1000 for p in big for t in W if f(live, p, t) is not None and f(own, p, t) is not None]
one = sum((f(live, p, t) is None) != (f(own, p, t) is None) for p in big for t in W)
print(f"\nall {len(W)} watched techs x {len(big)} peoples, live - after-run (same seed), yr (+ = live earlier): median {np.median(mv):.0f}, "
      f"mean {np.mean(mv):.0f}, |move| mean {np.mean(np.abs(mv)):.0f}; known in both {len(mv)}, in one only {one}")
pl = d / "polities_live.json"
if pl.exists():
    P = json.loads(pl.read_text())
    st = P["steps"]
    first_state = next((s["ago"] for s in st if s["counts"].get("state", 0) + s["counts"].get("empire", 0) > 0), None)
    print("live polities now:", st[-1]["counts"], "states", st[-1]["states"], "largest", st[-1]["largest_mkm2"], st[-1]["largest_people"],
          "| first state kyr", first_state, "| tech_s", P.get("tech_s"))
json.dump(out, open(d.parent.parent.parent.parent / f"check_{d.name}.json", "w") if False else open(sys.argv[3] if len(sys.argv) > 3 else "/dev/null", "w"))
