"""Round 28 (lane 281e, PW-1687): replay the live dragon cultures (polity_live.DragonCultures) on a finished run's stored frames from
demes.WINDOW_KYR ago, offline, and count them per dragon people against the read-out's dragon cultures (polities._dragon_cultures) at
a few frames. Diagnosis only: the history cuts on its own state at each stored frame (the same presence), with the people's era's
time apart; here the stone age's (dragons stay there on these runs). Read-only. argv: run_dir [agos kyr, default 2,1,0]."""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO
from planet.lineages import cultures as CU
from planet.lineages import demes as DE
from planet.lineages.history import polity_live as PL


def main(argv):
    R = PO._Run(Path(argv[0]))
    agos = [float(a) for a in argv[1:]] or [2.0, 1.0, 0.0]
    g = R.g
    dl = [i for i, l in enumerate(R.lines) if l["id"] in R.dragons]
    coh = R.C.get("constants", {}).get("cohesion") or {}
    dc = PL.DragonCultures(g, coh)
    js = [j for j, a in enumerate(R.agos) if a <= DE.WINDOW_KYR + 1e-9]
    js.sort(key=lambda j: -R.agos[j])
    want = {R.frame_of(a) for a in agos}
    prev = None
    tot_l, tot_r = Counter(), Counter()
    for j in js:
        a = R.agos[j]
        F = R.frame(j)
        dt = 0.0 if prev is None else prev - a
        prev = a
        live = {}
        for k in dl:
            held = np.zeros(g.n, bool)
            held[F["cells"][F["line"] == k]] = True
            live[R.lines[k]["id"]] = len(dc.step(k, R.lines[k]["id"], held, a, dt, True, CU.t_apart(None, a)))
        if j in want:
            ro = Counter(R.C["cultures"][c]["people"] for c, _ in PO._dragon_cultures(R, F))
            print(f"--- frame {a:.2f} kyr ago: people live-cultures readout-cultures")
            for p in sorted(live):
                print(f"  {p:18s} {live[p]:4d} {ro[p]:4d}")
            print(f"  {'total':18s} {sum(live.values()):4d} {sum(ro.values()):4d}")
            tot_l[a], tot_r[a] = sum(live.values()), sum(ro.values())



def dump(argv):
    """argv: run_dir people: replay to the present and print that people's labels (key, born, parent, frames, into, split off)."""
    R = PO._Run(Path(argv[0]))
    g = R.g
    k = next(i for i, l in enumerate(R.lines) if l["id"] == argv[1])
    dc = PL.DragonCultures(g, R.C.get("constants", {}).get("cohesion") or {})
    js = sorted((j for j, a in enumerate(R.agos) if a <= DE.WINDOW_KYR + 1e-9), key=lambda j: -R.agos[j])
    prev = None
    for j in js:
        a = R.agos[j]
        F = R.frame(j)
        held = np.zeros(g.n, bool)
        held[F["cells"][F["line"] == k]] = True
        out = dc.step(k, argv[1], held, a, 0.0 if prev is None else prev - a, True, CU.t_apart(None, a))
        prev = a
    alive = {x for x, _ in out}
    for i, x in enumerate(dc.info[k]):
        print(i, x, "ALIVE" if x[0] in alive else "")


if __name__ == "__main__":
    dump(sys.argv[2:]) if sys.argv[1:2] == ["dump"] else main(sys.argv[1:])
