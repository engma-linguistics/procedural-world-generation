"""Round 26 (lane 281c): how many dragon realms each way of cutting a dragon people's range into realms gives, on a run's stored
frames (the presence table). Read-only. argv: run_dir.
- pieces: each connected piece of the range (the live polities' rule on c489e2ca);
- flight: pieces within DRAGON_KM of each other joined (dilate by half of DRAGON_KM, then components);
- cultures: the read-out's rule (one realm per dragon culture on the map)."""
import sys
from pathlib import Path

import numpy as np

from planet.lineages.gridops import nbr_reduce
from planet.lineages import polities as PO
from planet.lineages.seafood import rings_for


def main(argv):
    R = PO._Run(Path(argv[0]))
    g = R.g
    idx = np.asarray(g.nbr_idx, np.int64)
    r = rings_for(g, PO.DRAGON_KM / 2)
    print(f"level rings for DRAGON_KM/2: {r}")
    dl = [i for i, l in enumerate(R.lines) if l["id"] in R.dragons]
    for j in range(0, len(R.agos), max(1, len(R.agos) // 8)):
        F = R.frame(j)
        pieces = flight = 0
        for k in dl:
            held = np.zeros(g.n, bool)
            held[F["cells"][F["line"] == k]] = True
            if not held.any():
                continue
            pieces += g.components(held)[1]
            d = held.copy()
            for _ in range(r):
                d = d | (nbr_reduce(g, np.maximum, d[idx].astype(np.int8)) > 0)
            lab, _ = g.components(d)
            flight += len(np.unique(lab[held]))
        cultures = len(PO._dragon_cultures(R, F))
        print(f"{R.agos[j] * 1000:7,.0f} ya: pieces {pieces:4d} flight {flight:4d} cultures {cultures:4d}")


if __name__ == "__main__":
    main(sys.argv[1:])
