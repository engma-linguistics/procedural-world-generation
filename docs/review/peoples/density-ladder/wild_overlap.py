"""Lane 139, PW-1385 sizing: of each kind's farmed and herded people, the share on cells where its wild rung (forager or fisher)
gives at least half the farm (herd) density there; and by biome. Reads `wild_overlap` from peoples_robust snapshot folders
(tools/peoples_robust.py::wild_overlap). Pooled over the runs. usage: python wild_overlap.py DIR_BEFORE DIR_AFTER"""
import json
import sys
from pathlib import Path


def pool(d):
    P, B, n = {}, {}, 0
    for f in sorted(Path(d).glob("*.json")):
        if f.name.endswith(".spec.json"):
            continue
        r = json.loads(f.read_text()).get("wild_overlap") or {}
        if "peoples" not in r:
            continue
        n += 1
        for src, dst in ((r["peoples"], P), (r["biomes"], B)):
            for a, ways in src.items():
                for w, (tot, near) in ways.items():
                    v = dst.setdefault(a, {}).setdefault(w, [0.0, 0.0])
                    v[0] += tot
                    v[1] += near
    return P, B, n


A, Bf = pool(sys.argv[1]), pool(sys.argv[2])
f = lambda d, a, w: (f"{100 * d[a][w][1] / d[a][w][0]:.0f}%" if a in d and w in d[a] and d[a][w][0] > 0 else "-")  # noqa: E731
m = lambda d, a, w: (f"{d[a][w][0] / 1e6:.0f}" if a in d and w in d[a] else "-")  # noqa: E731
print(f"runs: before {A[2]}, after {Bf[2]}\n")
for title, i in (("kind", 0), ("biome", 1)):
    a, b = A[i], Bf[i]
    keys = sorted(set(a) | set(b), key=lambda k: -sum(v[0] for v in b.get(k, a.get(k, {})).values()))
    print(f"| {title} | farmed M (b / a) | farmed, wild >= 1/2 (b / a) | herded M (b / a) | herded, wild >= 1/2 (b / a) |")
    print("|---|---|---|---|---|")
    for k in keys:
        print(f"| {k} | {m(a, k, 'farm')} / {m(b, k, 'farm')} | {f(a, k, 'farm')} / {f(b, k, 'farm')} | "
              f"{m(a, k, 'herd')} / {m(b, k, 'herd')} | {f(a, k, 'herd')} / {f(b, k, 'herd')} |")
    def tot(d, w):
        return sum(v.get(w, [0, 0])[0] for v in d.values()), sum(v.get(w, [0, 0])[1] for v in d.values())
    if i == 0:
        for w in ("farm", "herd"):
            print(f"\nall kinds, {w}: before {100 * tot(a, w)[1] / max(tot(a, w)[0], 1):.0f}%, after {100 * tot(b, w)[1] / max(tot(b, w)[0], 1):.0f}%")
    print()
