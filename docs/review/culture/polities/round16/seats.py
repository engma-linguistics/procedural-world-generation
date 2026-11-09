"""Round 16 (lane 241, PW-1583): what the ledger's seats are, on one run, at a few times. Read-only. argv: run_dir.
The read-out (polities.derive step 1) seats a chiefdom at each cell's biggest settled place (chief or minority) of town size for its
stage (TOWN_MIN by stage: 1,000, or 2,000 with roads); the history's seats (polity_live._step 1) are central places of 2,000 or more
(TOWN_MIN[-1]) at a cell that is the best of its ring. Splits the ledger's seats by kind, by size band and by whether a town or city
of the ledger stands within one ring (so the cell is not the best of its ring)."""
import sys
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO

R = PO._Run(Path(sys.argv[1]))
agos = [2.0, 1.0, 0.5, 0.0]
pop, holder, town_min = PO._site_tables(R, agos)
sites = R.S["sites"]
cell = np.array([s["cell"] for s in sites])
off, idx = np.asarray(R.g.nbr_off), np.asarray(R.g.nbr_idx)
for k, ago in enumerate(agos):
    best: dict = {}
    for i in np.flatnonzero(pop[:, k] > 0):
        s = sites[i]
        if s["kind"] not in PO.SETTLED_KINDS or pop[i, k] < town_min(s, ago):
            continue
        c = int(cell[i])
        if c not in best or pop[i, k] > pop[best[c], k]:
            best[c] = i
    ps = np.array([pop[i, k] for i in best.values()])
    kinds: dict = {}
    for i in best.values():
        kinds[sites[i]["kind"]] = kinds.get(sites[i]["kind"], 0) + 1
    seat_cells = set(best)
    bigger_near = sum(any(int(b) in seat_cells and pop[best[int(b)], k] > pop[i, k] for b in idx[off[c]:off[c + 1]]) for c, i in best.items())
    print(f"{ago:.1f} kyr ago: {len(best)} town-size seat cells; kinds {kinds}; < 2,000: {(ps < 2000).sum()}, 2,000-10,000: "
          f"{((ps >= 2000) & (ps < 10000)).sum()}, >= 10,000: {(ps >= 10000).sum()}; with a bigger seat in its ring: {bigger_near}")
