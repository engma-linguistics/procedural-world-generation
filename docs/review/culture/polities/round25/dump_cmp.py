"""Round 25 (lane 281b): the states the read-out seats on a switch-on history where the live polities seat only a chiefdom on the
same cell: the live seat's place (seat_dump.py's dump) against the read-out seat's ledger site at that step. Read-only.
argv: run_dir dump.json [ago ...] (default 2 1 0)."""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO


def main(argv):
    d, dump = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    dates = [float(a) for a in argv[2:]] or [2.0, 1.0, 0.0]
    lines = dump[0]["lines"]
    PO._from_live = None
    _ex = Path.exists
    Path.exists = lambda p: False if p.name == "polities_live.json" else _ex(p)
    ro = PO.derive(d)
    Path.exists = _ex
    R = PO._Run(d)
    city_min = float(R.S["tiers"]["city_min"])
    rrec = {r["id"]: r for r in ro["polities"]}
    rm = {round(float(s["ago"]), 3): m for s, m in zip(ro["steps"], ro["maps"])}
    dm = {e["ago"]: e["seats"] for e in dump}
    agos = sorted(rm, reverse=True)
    pop, holder, _ = PO._site_tables(R, agos)
    for t in dates:
        a = min(dm, key=lambda x: abs(x - t))
        k = agos.index(min(agos, key=lambda x: abs(x - a)))
        live = {c: (tier, p, w, hem) for c, tier, p, w, hem in dm[a]}
        rows = []
        for e in rm[agos[k]]:
            if e[1] not in (1, 2):
                continue
            r = rrec[e[0]]
            c = int(r["capital"]["cell"])
            if c not in live or live[c][0] != "chiefdom":
                continue
            tier, p, w, hem = live[c]
            sid = r["capital"].get("site")
            lp = float(pop[sid, k]) if sid is not None else float("nan")
            rows.append((c, lines[w] if w >= 0 else None, r["people"] if "people" in r else None, p, lp, hem, bool(r.get("confed"))))
        print(f"== {d.name} at {a * 1000:,.0f} ya: {len(rows)} read-out states that are live chiefdoms (city_min {city_min:,.0f})")
        if not rows:
            continue
        lp_ = np.array([x[4] for x in rows])
        p_ = np.array([x[3] for x in rows], float)
        hem_ = [x[5] for x in rows]
        print(f"   live seat place: median {np.median(p_):,.0f}, under city_min {int((p_ < city_min).sum())}, under city_min x 0.5 {int((p_ < city_min / 2).sum())}")
        print(f"   ledger site:     median {np.nanmedian(lp_):,.0f}; live / ledger median {np.nanmedian(p_ / lp_):.2f}; "
              f"live under ledger in {int((p_ < lp_).sum())}/{len(rows)}")
        print(f"   hemmed read live: {sum(h is not None for h in hem_)} of {len(rows)} (None: the state gate's techs or cool failed first)")
        print(f"   read-out confederations among them: {sum(x[6] for x in rows)}")
        print("   same holder people: " + str(Counter((x[1] == x[2]) for x in rows)))
        for x in sorted(rows, key=lambda x: x[4] - x[3], reverse=True)[:6]:
            print(f"     cell {x[0]} live {x[1]} {x[3]:,.0f} (hem {x[5]}) | read-out {x[2]} site {x[4]:,.0f} confed {x[6]}")


if __name__ == "__main__":
    main(sys.argv[1:])
