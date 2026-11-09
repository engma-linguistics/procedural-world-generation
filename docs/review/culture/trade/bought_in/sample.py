"""Sample bought-in food lines on a stored run (read-only; scratch PLANET_DATA). usage: sample.py run [era] [n]"""
import sys, time
from planet.lineages import brief as BR, bought_in as BI
run = sys.argv[1]
era = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
t = time.time()
ctx = BR.Ctx(run)
doc = ctx.trade_flows()
f = BI.frame_of(doc, era)
C = ctx.cultures()["cultures"]
tot = {}
for x in f["flows"]:
    if x[2] in BI.FOOD_GOODS:
        tot[x[1]] = tot.get(x[1], 0) + x[3]
print("frame", f["frame"], f["ago_kyr"], "takers of food", len(tot), round(time.time() - t), "s")
# a spread of peoples: the biggest food taker of each people
best = {}
for c, v in sorted(tot.items(), key=lambda kv: -kv[1]):
    best.setdefault(C[c]["people"], c)
for pid, c in list(best.items())[:n]:
    r = BI.of_culture(ctx, doc, c, era)
    print(f"\n[{c}] {C[c]['name']} ({pid}): {r['text']}")
b = BR.build(run, culture=int(sys.argv[4]) if len(sys.argv) > 4 else list(best.values())[0], era_kyr=era, ctx=ctx)
md = BR.markdown(b)
s = md if isinstance(md, str) else "\n".join(md)
for ln in s.splitlines():
    if ln.startswith(("- Staple", "- Drink", "- Fuel", "- Bought in", "## Bought-in")) or "of the people get it" in ln:
        print(ln[:400])
print(round(time.time() - t), "s")
