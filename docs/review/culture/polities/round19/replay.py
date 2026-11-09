"""Lane 254 (PW-1597): the after-run tree of a stored run (techtree.rebuild's inputs), run in one go and run in the history's own
steps (advance(to) per history step, as history.tech_live does), the inputs whole either way; then with one live habit at a time
(variants below). Read-only. argv: run_dir variant [variant ...]. Variants:
  batch      one advance() (techtree.build)
  steps      advance(ago) at every history step (polities_live.json's steps, else every 0.1 kyr), then advance()
  starts     steps + each step sets start/end as the live tree does (a line not started yet: -1e9)
  forced     steps + the tamings known by then only (cal.forced refreshed each step from tamings dated at or before it)"""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.lineages import land as LD
from planet.lineages import techtree as TT
from planet.lineages.techspread import town_footprint

d = Path(sys.argv[1])
run = json.loads((d / "run.json").read_text())
m = run["meta"]
pp = m.get("presence_present")
present = np.frombuffer((d / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0 if pp else None
goods = LD.goods(m.get("world")) if m.get("world") else None
lines = TT.with_generations(m["lineages"], m.get("tree"))
towns = town_footprint(d) if m.get("settlements") else None
landmass = TT.landmass_of(d, m)
pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
lp = d / "polities_live.json"
agos = sorted({float(s["ago"]) if isinstance(s, dict) else float(s[0]) for s in json.loads(lp.read_text())["steps"]}, reverse=True) if lp.exists() else []
fr = sorted({float(t[0]) for l in m["lineages"] for t in (l.get("track") or [])}, reverse=True)
agos = sorted(set(agos) | set(fr) | set(np.round(np.arange(30.0, 0, -0.1), 3)), reverse=True)


def calendar():
    c = TT.Calendar(lines, m.get("mode", "fantasy"), m.get("era"), int(m.get("try_seed") or 0), None, m.get("gods_mode", "faith_made"), towns)
    have = {l["id"]: TT.goods_held(c.T, present, goods, c.idx[l["id"]]) for l in c.people}
    c.feed(lines, TT.links_of(m.get("contacts"), c.kind), TT.forced_of(m.get("present"), c.techs, c.L), have,
           (m.get("present") or {}).get("lines") or {}, c.region_shares(present, landmass))
    return c


def report(name, known):
    top = sorted([p for p in known if p in pops], key=lambda p: -pops[p])[:12]
    w = [x for x in ((known.get(p) or {}).get("writing", [None])[0] for p in top) if x is not None]
    t = [x for x in ((known.get(p) or {}).get("towns", [None])[0] for p in top) if x is not None]
    print(f"{name:8s} writing median {st.median(w) * 1000:,.0f} ya ({len(w)}/12); towns median {st.median(t) * 1000:,.0f} ya", flush=True)


_pt, _fa = None, None


def presence_at(a):
    """The presence (lines x cells, 0..1) at the last stored frame at or before `a` kyr ago (the run's presence table)."""
    global _pt, _fa
    from planet.lineages.output import read_presence
    if _pt is None:
        _pt = read_presence(d, m)
        _fa = np.array([-float(f["t"]) for f in run["frames"]])
    j = int(np.flatnonzero(_fa >= a - 1e-9)[-1]) if (_fa >= a - 1e-9).any() else 0
    nl, n = _pt["offsets"].shape[1] - 1, present.shape[1]
    P = np.zeros((nl, n), np.float32)
    off = _pt["offsets"][j]
    for k in range(nl):
        x, y = int(off[k]), int(off[k + 1])
        P[k, _pt["cells"][x:y].astype(np.int64)] = _pt["share"][x:y] / 100.0
    return j, P


for v in sys.argv[2:]:
    c = calendar()
    if v in ("regions", "have", "both"):
        last = None
        have0, reg0 = c.have, c.regions
        for a in agos:
            j, P = presence_at(a)
            if j != last:
                last = j
                if v in ("have", "both"):
                    c.have = {l["id"]: TT.goods_held(c.T, P, goods, c.idx[l["id"]]) for l in c.people}
                if v in ("regions", "both"):
                    c.regions = c.region_shares(P, landmass)
            c.advance(a)
        c.have, c.regions = have0, reg0
        v = v + "_t"
    if v != "batch":
        f_all = c.forced
        st0 = {l["id"]: (l.get("started_kyr") if l.get("started_kyr") is not None else l.get("ago_kyr", 0.0)) for l in lines if l["id"] in c.kind}
        en0 = {l["id"]: l.get("ended_kyr") for l in lines if l["id"] in c.kind}
        for a in agos:
            if v == "starts":
                for lid in c.start:
                    c.start[lid] = float(st0[lid]) if st0[lid] is not None and float(st0[lid]) >= a else -1e9
                    c.end[lid] = float(en0[lid]) if en0[lid] is not None and float(en0[lid]) >= a else -1.0
            if v == "forced":
                c.forced = {lid: [x for x in xs if x[0] >= a] for lid, xs in f_all.items()}
            c.advance(a)
        if v == "starts":
            c.start = {lid: float(st0[lid]) for lid in c.start}
            c.end = {lid: float(en0[lid]) if en0[lid] is not None else -1.0 for lid in c.end}
        c.forced = f_all
    c.advance()
    report(v, c.result()["known"])
