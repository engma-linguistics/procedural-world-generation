"""people_density.py DIR [DIR ...] [--fit]: the 6 x 4 dnd sweep's tables (probe.py OUT.json files, one DIR per arm), for PW-974 and PW-977.

Per arm: the per-people pass (>= 300 cells), the remnants (< 100 cells, counting peoples absent at the present), the present dragons
and giants per run, the mean density by way of life (people per km2 of held country, presence-weighted) and, where probe ran with
--eras, the food budget's shares at each era. --fit (on an arm run with --no-people-prod) prints the two references of
lineages.prey.people_fields: the presence-weighted means of the foraging layer and the grazing NPP over the country held by the peoples
that read them, each weighted by its share of the people's living, so each way's mean density over the sweep stays at its number.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

DRAGONS = ("red", "blue", "green", "black", "white", "gold", "silver", "bronze", "copper", "brass")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
FIT = "--fit" in sys.argv


def load(d):
    return {p.stem: json.loads(p.read_text()) for p in sorted(Path(d).glob("*.json"))}


def way(lm):
    tot = lm["herd"] + lm["forage"] + lm["farm"]
    if tot <= 0:
        return "other"
    return max((("herders", lm["herd"]), ("foragers", lm["forage"]), ("farmers", lm["farm"])), key=lambda x: x[1])[0]


for d in args:
    R = load(d)
    if not R:
        continue
    cells = [(k, lid, c) for k, r in R.items() for lid, c in r["peoples"].items()]
    npass = sum(c >= 300 for _, _, c in cells)
    rem = [(k, lid, c) for k, lid, c in cells if c < 100]
    drag = [sum(v for lid, v in r["mf_count"].items() if lid.split("_")[0] in DRAGONS and lid.endswith("dragon")) for r in R.values()]
    giants = [sum(v for lid, v in r["mf_count"].items() if lid.endswith("giant")) for r in R.values()]
    print(f"== {d}: {len(R)} runs")
    print(f"  per-people pass {npass}/{len(cells)} = {npass / max(len(cells), 1):.1%}; remnants (<100 cells) {len(rem)}"
          f" (of them absent: {sum(c == 0 for *_, c in rem)})")
    print(f"  dragons per run {np.mean(drag):,.0f} (min {min(drag):,}, max {max(drag):,}); giants per run {np.mean(giants):,.0f}")
    pw = defaultdict(lambda: [0.0, 0.0])  # way -> [people, presence x km2]
    for r in R.values():
        for lid, lm in r.get("lmean", {}).items():
            pop = r["pop"].get(lid, 0) or 0
            md = r["meand"].get(lid)
            if not md or pop <= 0:
                continue
            pw[way(lm)][0] += pop
            pw[way(lm)][1] += pop / md
    print("  mean density by way (people/km2 of held country): " + ", ".join(f"{w} {a / b:.3f}" for w, (a, b) in sorted(pw.items()) if b > 0))
    rems = defaultdict(int)
    for k, lid, c in rem:
        rems[lid] += 1
    print("  remnants by people: " + ", ".join(f"{lid} {n}" for lid, n in sorted(rems.items(), key=lambda x: -x[1])))
    eras = defaultdict(lambda: defaultdict(list))
    for r in R.values():
        for e, row in (r.get("eras") or {}).items():
            for cn in ("all", "none", "foragers", "herders", "farmers"):
                if cn in row and row[cn]["supply_t"] > 0:
                    eras[e][cn].append(row[cn])
            eras[e]["_dragons"].append(row["dragons"])
            eras[e]["_unc"].append(row["dragons_uncapped"])
    for e in sorted(eras, key=float, reverse=True):
        print(f"  era {e} kyr ago: dragons {np.mean(eras[e]['_dragons']):,.0f} (uncapped {np.mean(eras[e]['_unc']):,.0f}) per run;"
              " shares of the supply (peoples / giants / guild / left for dragons / dragons' need), mean over runs:")
        for cn in ("all", "none", "foragers", "herders", "farmers"):
            rows = eras[e].get(cn)
            if not rows:
                continue
            m = lambda k: np.mean([x[k] for x in rows])
            print(f"    {cn:9s} cells {np.mean([x['cells'] for x in rows]):8,.0f}  stock {m('stock'):6.1%}  peoples {m('peoples'):6.1%}"
                  f"  giants {m('giants'):6.1%}  guild {m('guild'):6.1%}  left {m('food'):6.1%}  need {m('dragons_need'):6.2%}")
    if FIT:
        acc = {"forage": [0.0, 0.0], "graze": [0.0, 0.0]}
        for r in R.values():
            for lid, lm in r.get("lmean", {}).items():
                pop, md = r["pop"].get(lid, 0) or 0, r["meand"].get(lid)
                tot = lm["herd"] + lm["forage"] + lm["farm"]
                if not md or pop <= 0 or tot <= 0:
                    continue
                held = pop / md  # (presence x km2 held)
                for key, sh in (("forage", lm["forage"]), ("graze", lm["herd"])):
                    acc[key][0] += held * sh / tot * lm[key]
                    acc[key][1] += held * sh / tot
        print(f"  FIT: FORAGE_REF {acc['forage'][0] / acc['forage'][1]:.3f}  GRAZE_REF {acc['graze'][0] / acc['graze'][1]:.1f}")
