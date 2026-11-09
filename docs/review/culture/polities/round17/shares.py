"""Lane 245: peoples' shares (track pop) at given times for runs; argv: label=run_dir ... (relative dirs read under the scratchpad)."""
import json
import sys
from pathlib import Path

S = Path("/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad")
TIMES = (5.0, 3.0, 2.0, 1.0, 0.0)
rows = {}
for a in sys.argv[1:]:
    lab, d = a.split("=")
    r = json.loads((S / d / "run.json").read_text())
    L = r["meta"]["lineages"]
    sh = {}
    for t in TIMES:
        pops = {}
        for l in L:
            v = [x for x in (l.get("track") or []) if abs(x[0] - t) < 1e-6]
            if v:
                pops[l["id"]] = v[0][4]
        tot = sum(pops.values()) or 1
        sh[t] = {p: 100 * v / tot for p, v in pops.items()}
        sh[t]["TOTAL(M)"] = tot / 1e6
    rows[lab] = sh
peoples = sorted({p for s in rows.values() for p in s[0.0] if p != "TOTAL(M)"}, key=lambda p: -max(s[0.0].get(p, 0) for s in rows.values()))[:9]
peoples.append("TOTAL(M)")
for t in TIMES:
    print(f"--- {t * 1000:,.0f} ya")
    print(f"{'run':14s}" + "".join(f"{p[:9]:>10s}" for p in peoples))
    for lab, sh in rows.items():
        print(f"{lab:14s}" + "".join(f"{sh[t].get(p, 0):10.1f}" for p in peoples))
