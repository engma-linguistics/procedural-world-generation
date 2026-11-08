"""Round 4 (lane 208, D60 B "towns or chiefdoms", D62 A): who holds writing and kingship at 0.5 kyr ago, from round3/lag.py's JSONs,
baseline against the chiefdom variant (a people holding chiefdoms may TAKE UP a state tech without a town; inventing still needs one).
python chiefs.py RUN BASE.json OTHER.json   (RUN: the run id, for the peoples' ways of life in run.json; PLANET_DATA: the data root)

Per draw (median and range over draws): the share of peoples with hands holding writing / kingship / chiefdoms at 0.5 kyr ago, and,
among the peoples with no town of their own by then (towns_first None or later than 0.5 kyr ago, not hosted), the share holding
writing, split by whether they hold chiefdoms then and by a mobile way of life (techtree.MOBILE_WAYS)."""
import json, os, sys
from pathlib import Path

import numpy as np

AT = 0.5
MOBILE = ("forager", "fisher_forager", "hunter", "pastoral_nomad", "nomadic", "sea_nomad", "transhumant")


def held(v, t):
    d = v["dates"].get(t)
    return d is not None and d >= AT - 1e-9


def stats(D, way):
    rows = []
    for d in D["draws"]:
        P = d["people"]
        n = len(P) or 1
        r = {t: sum(held(v, t) for v in P.values()) / n for t in ("writing", "kingship", "chiefdoms")}
        nt = {p: v for p, v in P.items() if not v.get("hosted") and (v.get("towns_first") is None or v["towns_first"] < AT)}
        for lab, sel in (("no town", lambda p, v: True),
                         ("no town, chiefdoms", lambda p, v: held(v, "chiefdoms")),
                         ("no town, no chiefdoms", lambda p, v: not held(v, "chiefdoms")),
                         ("no town, mobile way", lambda p, v: way.get(p) in MOBILE),
                         ("no town, mobile, chiefdoms", lambda p, v: way.get(p) in MOBILE and held(v, "chiefdoms"))):
            S = [p for p, v in nt.items() if sel(p, v)]
            r[lab + " n"] = len(S)
            r[lab + " writing"] = (sum(held(nt[p], "writing") for p in S) / len(S)) if S else float("nan")
        rows.append(r)
    return rows


def fmt(rows, k):
    x = np.array([r[k] for r in rows], float)
    x = x[~np.isnan(x)]
    if not len(x):
        return "-"
    if k.endswith(" n"):
        return f"{np.median(x):.0f} [{x.min():.0f}-{x.max():.0f}]"
    return f"{100 * np.median(x):.0f}% [{100 * x.min():.0f}-{100 * x.max():.0f}]"


def main(rid, files):
    meta = json.loads((Path(os.environ["PLANET_DATA"]) / "runs" / rid / "run.json").read_text())["meta"]
    way = {ln["id"]: ln.get("way") for ln in meta.get("lineages") or []}
    S = {Path(f).stem: stats(json.loads(Path(f).read_text()), way) for f in files}
    keys = list(next(iter(S.values()))[0].keys())
    print(f"=== {rid}  (median of draws [min-max]; shares of peoples with hands at {AT} kyr ago)")
    print(f"{'':32s}" + "".join(f"{k:>26s}" for k in S))
    for k in keys:
        print(f"{k:32s}" + "".join(f"{fmt(r, k):>26s}" for r in S.values()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
