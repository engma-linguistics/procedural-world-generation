import json, glob, sys
import numpy as np
fs = sorted(glob.glob(sys.argv[1] + "/*.json"))
D = [json.load(open(f)) for f in fs]
vs = [v for v in D[0] if v != "none"]
P = sys.argv[3].split(",") if len(sys.argv) > 3 else ["human", "hobgoblin", "halfling", "orc", "leonin", "kenku", "tabaxi", "firbolg", "bugbear", "elf", "dragonborn", "gnome"]
for t in sys.argv[2].split(","):
    print(f"\n{t}: known in /{len(D)}, median yr ago [min-max]; first writer of any people")
    for v in vs:
        row = []
        for p in P:
            x = [d[v].get(p, {}).get(t) for d in D]
            k = [1000 * a for a in x if a is not None]
            row.append(f"{p[:5]} {len(k)} {int(np.median(k)) if k else '-'}")
        first = [max([a[t] or 0 for a in d[v].values()]) * 1000 for d in D]
        print(f"  {v:11s} first med {int(np.median(first))} | " + " | ".join(row))
