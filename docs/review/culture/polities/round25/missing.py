"""Round 25 (lane 281b, PW-1596): on one switch-on run, the states the after-run read-out seats (derive, live map hidden) that the
live polities do not, at a few dates: what the live map has on that capital's cell instead (a chiefdom, a province of another
polity, nothing), and the read-out seat's ledger site (kind, size, holder). Read-only. argv: run_dir [ago ...] (default 2 1 0)."""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from planet.lineages import polities as PO


def maps(D):
    return {round(float(s["ago"]), 3): m for s, m in zip(D["steps"], D["maps"])}


def main(argv):
    d = Path(argv[0])
    dates = [float(a) for a in argv[1:]] or [2.0, 1.0, 0.0]
    live = PO.derive(d)
    PO._from_live = None
    _ex = Path.exists
    Path.exists = lambda p: False if p.name == "polities_live.json" else _ex(p)
    ro = PO.derive(d)
    Path.exists = _ex
    R = PO._Run(d)
    sites = {s["id"]: s for s in R.S["sites"]}
    lm, rm = maps(live), maps(ro)
    lrec, rrec = {r["id"]: r for r in live["polities"]}, {r["id"]: r for r in ro["polities"]}
    for t in dates:
        a = min(lm, key=lambda x: abs(x - t))
        g_n = R.g.n
        own_t, own_r = np.full(g_n, -1), np.full(g_n, -1)  # (live: tier index of the polity ruling each cell; its record)
        cap_tier = {}
        for e in lm[a]:
            cells = PO._unpack(e[2])
            own_t[cells], own_r[cells] = e[1], e[0]
            cap_tier[int(lrec[e[0]]["capital"]["cell"])] = PO.TIERS[e[1]]
        ro_states = [(rrec[e[0]], PO.TIERS[e[1]]) for e in rm[a] if e[1] in (1, 2)]
        li_states = {int(lrec[e[0]]["capital"]["cell"]) for e in lm[a] if e[1] in (1, 2)}
        what = Counter()
        kinds = Counter()
        pops = []
        for r, tier in ro_states:
            c = int(r["capital"]["cell"])
            if c in li_states:
                what["live: a state seated here too"] += 1
                continue
            if c in cap_tier:
                what[f"live: a {cap_tier[c]} seated here"] += 1
            elif own_t[c] >= 0:
                what[f"live: inside another's {PO.TIERS[own_t[c]]}"] += 1
            else:
                what["live: unruled"] += 1
            s = sites.get(r["capital"].get("site"))
            if s is not None:
                kinds[s["kind"]] += 1
        print(f"== {d.name} at {a * 1000:,.0f} ya: read-out states {len(ro_states)}, live states {len(li_states)}")
        for k, v in what.most_common():
            print(f"   {v:4d}  {k}")
        print("   read-out-only capitals' site kinds: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()))
        lo = Counter(PO.TIERS[e[1]] for e in lm[a])
        ro_c = Counter(PO.TIERS[e[1]] for e in rm[a])
        print(f"   tiers live {dict(lo)} | read-out {dict(ro_c)}")
        print(f"   confederations standing: live {sum(1 for e in lm[a] if e[1] in (1, 2) and lrec[e[0]].get('confed'))}, "
              f"read-out {sum(1 for e in rm[a] if e[1] in (1, 2) and rrec[e[0]].get('confed'))}")


if __name__ == "__main__":
    main(sys.argv[1:])
