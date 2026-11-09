"""samples from a saved doc: fish buyers and far grain. usage: samp.py tag run [era]"""
import json, sys
from planet.lineages import brief as BR, bought_in as BI
D = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l244/out"
tag, run = sys.argv[1], sys.argv[2]
era = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
ctx = BR.Ctx(run)
doc = json.load(open(f"{D}/doc-{tag}-{run}.json"))
C = ctx.cultures()["cultures"]
f = BI.frame_of(doc, era)
takers = sorted({x[1] for x in f["flows"]})
fish, far, roads = [], [], {}
for c in takers:
    b = BI.of_culture(ctx, doc, c, era)
    if not b:
        continue
    for fd in b["foods"]:
        if fd["good"] == "dried_fish":
            fish.append((c, fd))
            for g in fd["givers"]:
                roads[g["road"]] = roads.get(g["road"], 0) + 1
        if fd["good"] == "grain":
            for g in fd["givers"]:
                if g["km"] >= 4000:
                    far.append((c, g))
print(run, tag, era, "fish buyers", len(fish), "non-tribute", sum(1 for _, fd in fish if any(g["road"] != "tribute" for g in fd["givers"])), roads)
for c, fd in sorted(fish, key=lambda x: -max((g["km"] for g in x[1]["givers"]), default=0))[:8]:
    print(f"  FISH [{c}] {C[c]['name']}: " + "; ".join(f"{g['share']:.0%} from {g.get('name') or g.get('giver')} {g['km']} km {g['road']}" for g in fd["givers"]))
for c, g in sorted(far, key=lambda x: -x[1]["km"])[:8]:
    print(f"  FAR GRAIN [{c}] {C[c]['name']}: {g['share']:.1%} from {g.get('name') or g.get('giver')} {g['km']} km {g['road']}")
