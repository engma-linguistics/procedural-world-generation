"""Round 25 (lane 281b): every live seat's place (seat_dump.py's dump) against the ledger's biggest settled place on that cell
(settlements.json read back as the read-out reads it, _site_tables), at the same step and at the step before (the live seats read
the places as at the end of the last step). Read-only. argv: run_dir dump.json."""
import json
import sys
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO


def main(argv):
    d, dump = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    R = PO._Run(d)
    sites = R.S["sites"]
    settled = np.array([s["kind"] in PO.SETTLED_KINDS for s in sites], bool)
    cell = np.array([s["cell"] for s in sites], np.int64)
    agos = sorted({e["ago"] for e in dump} | {round(e["ago"] + 0.1, 3) for e in dump}, reverse=True)
    pop, _, _ = PO._site_tables(R, agos)
    pop = np.where(settled[:, None], pop, 0.0)
    for e in dump:
        if round(e["ago"] * 10) % 5:
            continue
        rows = []
        for when in (e["ago"], round(e["ago"] + 0.1, 3)):
            k = agos.index(when)
            best = np.zeros(R.g.n)
            np.maximum.at(best, cell, pop[:, k])
            live = np.array([s[2] for s in e["seats"]], float)
            led = best[np.array([s[0] for s in e["seats"]], np.int64)]
            ok = led > 0
            r = live[ok] / led[ok]
            rows.append(f"ledger at {when * 1000:,.0f} ya: live/ledger median {np.median(r):.2f}, p25 {np.percentile(r, 25):.2f}, "
                        f"p75 {np.percentile(r, 75):.2f}; no ledger place {int((~ok).sum())}")
        big = [s for s in e["seats"] if s[2] >= 8000]
        print(f"{e['ago'] * 1000:5,.0f} ya: {len(e['seats'])} live seats ({len(big)} of 8,000+) | " + " | ".join(rows))


if __name__ == "__main__":
    main(sys.argv[1:])
