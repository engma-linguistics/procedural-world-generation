"""Round 27 (lane 281d, PW-1687): per dragon people, at a few stored frames of a switch-on peoples run: the regions of its range by
the live rule (polity_live.dragon_regions on the stored presence), the read-out's dragon cultures (polities._dragon_cultures), and the
dragon realms standing in the live map and in the read-out on the same history (derive with the live map hidden, as
round26/measure.py). Read-only. argv: run_dir [agos kyr, default 2,1,0]."""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO
from planet.lineages.history import polity_live as PL
from planet.lineages.history.megafauna import LINK_KM
from planet.lineages import demes as DE
from planet.lineages.seafood import cells_for, rings_for


def realms(D, ago):
    """people -> dragon realms standing at the step nearest ago."""
    j = min(range(len(D["steps"])), key=lambda i: abs(float(D["steps"][i]["ago"]) - ago))
    by_id = {r["id"]: r for r in D["polities"]}
    return Counter(by_id[e[0]]["people"] for e in D["maps"][j] if e[1] == 3)


def main(argv):
    d = Path(argv[0])
    agos = [float(a) for a in argv[1:]] or [2.0, 1.0, 0.0]
    R = PO._Run(d)
    g = R.g
    rl, mc = rings_for(g, LINK_KM / 2), cells_for(g, DE.MIN_KM2)
    live = PO.derive(d)
    _f, _ex = PO._from_live, Path.exists
    PO._from_live = None
    Path.exists = lambda p: False if p.name == "polities_live.json" else _ex(p)
    try:
        ro = PO.derive(d)
    finally:
        Path.exists, PO._from_live = _ex, _f
    dl = [i for i, l in enumerate(R.lines) if l["id"] in R.dragons]
    for ago in agos:
        j = R.frame_of(ago)
        F = R.frame(j)
        cu = Counter()
        for c, cells in PO._dragon_cultures(R, F):
            cu[R.C["cultures"][c]["people"]] += 1
        lv, rv = realms(live, ago), realms(ro, ago)
        print(f"--- {ago:.1f} kyr ago (frame {R.agos[j]:.2f}): people regions cultures live-realms readout-realms")
        tot = np.zeros(4, int)
        for k in dl:
            p = R.lines[k]["id"]
            held = np.zeros(g.n, bool)
            held[F["cells"][F["line"] == k]] = True
            _lab, n = PL.dragon_regions(g, held, rl, mc)
            row = np.array([n, cu[p], lv[p], rv[p]])
            tot += row
            print(f"  {p:18s} {row[0]:4d} {row[1]:4d} {row[2]:4d} {row[3]:4d}   cells {int(held.sum())}")
        print(f"  {'total':18s} {tot[0]:4d} {tot[1]:4d} {tot[2]:4d} {tot[3]:4d}")


if __name__ == "__main__":
    main(sys.argv[1:])
