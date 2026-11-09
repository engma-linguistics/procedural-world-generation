"""Round 14's measures (lane 234, PW-1466, PW-1456, PW-1460): the polities of a peoples run, live (polities_live.json, when the switch
was on) and read out after the run (polities.derive, always). Read-only. argv: run_dir [run_dir ...] [--pair BASE NUDGE ...].

Per run and source (live / readout):
- when states first form: the oldest step with a state or empire, and the states 2,000 / 1,000 / 0 years ago;
- the largest state or empire per century over the last 3,000 years against Taagepera 1997's 2.3 Mkm2 floor (PW-1456): median,
  the share of centuries at or over it, the peak, and the most polities over 1 Mkm2 in one century;
- first writing (the 12 largest peoples' median and earliest), from the run's own calendar.
--pair BASE NUDGE: PW-1460's measures between two runs (round6.md section 2, re-made here): "top 10 kept" (the 10 largest states and
empires of one run with a state or empire of the same ruling people within 300 km of its capital in the other, read both ways),
"same ruler" (the share of cells ruled by a state, empire or dragon realm in either run with the same ruling people in both).
"""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.grid import shared_grid
from planet.lineages import polities as PO

RULED = (1, 2, 3)  # (state, empire, dragon realm: the tiers "same ruler" reads)
STATES = (1, 2)
FLOOR = 2.3  # Taagepera 1997 (via proposal.md 2.1.2): the largest polity never under 2.3 Mkm2 after ~650 BC
_doc_cache: dict = {}


def docs(d: Path) -> dict:
    """{source: (steps [(ago, [(rec, tier, cells)])], people_of(rec, ago), capital_cell(rec), cell_km2)}."""
    if d in _doc_cache:
        return _doc_cache[d]
    run = json.loads((d / "run.json").read_text())
    g = shared_grid(run["meta"]["level"])
    km2 = 4 * np.pi * PO.R_EARTH_KM ** 2 / g.n
    out = {}
    lp = d / "polities_live.json"
    if lp.exists():
        L = json.loads(lp.read_text())
        recs = L["polities"]
        steps = [(s["ago"], [(e[0], e[1], PO._unpack(e[2])) for e in m]) for s, m in zip(L["steps"], L["maps"])]
        out["live"] = (steps, lambda r, a, recs=recs: recs[r]["people"], lambda r, recs=recs: recs[r]["cell"], km2)
    D = PO.derive(d)
    recs = D["polities"]
    steps = [(s["ago"], [(e[0], e[1], PO._unpack(e[2])) for e in m]) for s, m in zip(D["steps"], D["maps"])]
    out["readout"] = (steps, lambda r, a, recs=recs: PO._at([[x[0], x[1]] for x in recs[r]["peoples"]], a)[1],
                      lambda r, recs=recs: recs[r]["capital"]["cell"], km2)
    _doc_cache[d] = (out, run, g)
    return _doc_cache[d]


def at(steps, ago):
    return min(steps, key=lambda s: abs(s[0] - ago))[1]


def one(d: Path):
    out, run, g = docs(d)
    m = run["meta"]
    print(f"=== {d.name} ({run.get('name')})  live: {'polities_live.json' if 'live' in out else 'off'}")
    for src, (steps, people, cap, km2) in out.items():
        first = max((a for a, mp in steps if any(t in STATES for _, t, _ in mp)), default=None)
        n = lambda a: sum(t in STATES for _, t, _ in at(steps, a))  # noqa: E731
        big = [(a, max((len(c) * km2 / 1e6 for _, t, c in mp if t in STATES), default=0.0),
                sum(len(c) * km2 / 1e6 > 1 for _, t, c in mp if t in STATES)) for a, mp in steps if a <= 3.0 + 1e-9]
        sz = [b for _, b, _ in big]
        print(f"  {src:8s} first state {('never' if first is None else f'{first * 1000:,.0f} ya'):>9s} | states 2,000/1,000/0 ya "
              f"{n(2.0)}/{n(1.0)}/{n(0.0)} | largest last 3 kyr: median {st.median(sz):.2f}, >= {FLOOR} in "
              f"{sum(b >= FLOOR for b in sz)}/{len(sz)}, peak {max(sz):.2f} Mkm2, now {sz[-1]:.2f} | most > 1 Mkm2 {max(o for *_, o in big)}")
    k = m["techtree"]["known"]
    pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
    top = sorted([p for p in k if p in pops], key=lambda p: -pops[p])[:12]
    w = [(k[p].get("writing") or [None])[0] for p in top]
    ww = [x for x in w if x is not None]
    print(f"  writing (12 largest): {len(ww)}/12 write; median {st.median(ww) * 1000:,.0f} ya, earliest {max(ww) * 1000:,.0f} ya"
          if ww else "  writing: none of the 12 largest")
    tot = sum(pops.values()) or 1
    print("  shares now: " + ", ".join(f"{p} {100 * pops[p] / tot:.1f}" for p in sorted(pops, key=lambda p: -pops[p])[:6]))


def pair(a: Path, b: Path):
    A, _, g = docs(a)
    B, _, _ = docs(b)
    c = np.asarray(g.centers, float)
    for src in ("live", "readout"):
        if src not in A or src not in B:
            continue
        sa, pa, ca, km2 = A[src]
        sb, pb, cb, _ = B[src]
        row = []
        for ago in (1.0, 0.0):
            ma, mb = at(sa, ago), at(sb, ago)
            ra, rb = np.full(g.n, "", object), np.full(g.n, "", object)
            for r, t, cells in ma:
                if t in RULED:
                    ra[cells] = pa(r, ago)
            for r, t, cells in mb:
                if t in RULED:
                    rb[cells] = pb(r, ago)
            either = (ra != "") | (rb != "")
            same = float(((ra == rb) & either).sum() / max(either.sum(), 1))

            def kept(m1, p1, c1, m2, p2, c2):
                top = sorted([e for e in m1 if e[1] in STATES], key=lambda e: -len(e[2]))[:10]
                oth = [(p2(r, ago), c2(r)) for r, t, _ in m2 if t in STATES]
                hit = 0
                for r, _, _ in top:
                    p, x = p1(r, ago), c[c1(r)]
                    hit += any(q == p and np.arccos(np.clip(np.dot(x, c[y]), -1, 1)) * PO.R_EARTH_KM <= 300 for q, y in oth)
                return hit, len(top)
            k1, k2 = kept(ma, pa, ca, mb, pb, cb), kept(mb, pb, cb, ma, pa, ca)
            row.append(f"{ago * 1000:,.0f} ya: top 10 kept {k1[0]}/{k1[1]}, {k2[0]}/{k2[1]}; same ruler {100 * same:.0f}%")
        print(f"  {a.name} vs {b.name} [{src}]  " + " | ".join(row))


def main(argv):
    if "--pair" in argv:
        i = argv.index("--pair")
        runs, prs = argv[:i], argv[i + 1:]
    else:
        runs, prs = argv, []
    for d in runs:
        one(Path(d))
    for x, y in zip(prs[::2], prs[1::2]):
        pair(Path(x), Path(y))


if __name__ == "__main__":
    main(sys.argv[1:])
