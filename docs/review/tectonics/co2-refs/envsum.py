"""Lane 135 (PW-1316): summarise envref.py's runs per arm. usage: envsum.py DIR ARM_A ARM_B
Per seed: end T; the late imbalance (lane 115's measure: mean over 300-400 Myr of ln(src/src_ref) - ln(sink/sink_ref));
the source reference's mismatch with the source the planet goes on to have (ln(src_ref / mean src over 300-400));
then per arm the correlation of end T with each, the spread, and the band count (|T - 14.5| > 10)."""
import json
import sys
from pathlib import Path

import numpy as np

d, arms = Path(sys.argv[1]), sys.argv[2:]
res = {}
for a in arms:
    rows = []
    for f in sorted(d.glob(f"{a}_*.json"), key=lambda p: int(p.stem.split("_")[1])):
        r = json.loads(f.read_text())
        tr = [x for x in r["trace"] if x["t"] > 300 and "src_ref" in x]
        imb = np.mean([np.log(x["src"] / x["src_ref"]) - np.log(x["sink"] / x["sink_ref"]) for x in tr])
        srcm = np.log(tr[-1]["src_ref"] / np.mean([x["src"] for x in tr]))
        rows.append((r["seed"], r["end"]["T"], r["end"]["pco2"], imb, srcm, tr[-1]["src_ref"], tr[-1]["sink_ref"]))
    res[a] = {r[0]: r for r in rows}
    T, imb, srcm = (np.array([r[i] for r in rows]) for i in (1, 3, 4))
    print(f"{a}: n {len(rows)}  end T median {np.median(T):.1f} sd {T.std():.2f} range {T.min():.1f}..{T.max():.1f}"
          f"  out of band {int((abs(T - 14.5) > 10).sum())}  corr(T, late imbalance) {np.corrcoef(T, imb)[0, 1]:.2f}"
          f"  sd imbalance {imb.std():.3f}  corr(T, src-ref mismatch) {np.corrcoef(T, srcm)[0, 1]:.2f}"
          f"  sd src-ref mismatch {srcm.std():.3f}")
print("seed | " + " | ".join(f"{a}: T, pCO2, imbalance, src-ref mismatch, refs" for a in arms))
for s in sorted(set.intersection(*(set(res[a]) for a in arms))):
    print(s, " | ".join(f"{res[a][s][1]:.1f}, {res[a][s][2]:.0f}, {res[a][s][3]:+.2f}, {res[a][s][4]:+.2f}, "
                        f"{res[a][s][5]:.0f}/{res[a][s][6]:.0f}" for a in arms))
