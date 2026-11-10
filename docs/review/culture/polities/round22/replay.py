"""Lane 265 (PW-1597 R, round22.md): the after-run tree of a switch-on run, on the footprint its live tree read, with the live tree's
habits added one at a time (round19/replay.py's, on today's build: regions per frame), to find which one parts it from the live
tree. Read-only. argv: run_dir live_dump.json variant [variant ...]; a variant is habits joined by '+':
  batch     techtree.build as rebuild does (one advance)
  steps     advance(ago) at every history step (every stored frame and every 0.1 kyr of the last 30), then advance()
  starts    + each step, the lines' starts and ends as known then (not started yet: -1e9)
  forced    + each step, the tamings dated at or before it only
  have      + the goods each people holds on its range at the stored frame at or before each step (else: today's range)
  hold      + population, density and range read at the stored frame at or before a time (else: drawn toward the next frame)
Prints the 12 largest peoples' writing median and how many (people, tech) records differ from the stored live tree, and the oldest."""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.lineages import land as LD
from planet.lineages import techtree as TT
from planet.lineages.output import read_presence

d, dump = Path(sys.argv[1]), Path(sys.argv[2])
run = json.loads((d / "run.json").read_text())
m = run["meta"]
pp = m.get("presence_present")
present = np.frombuffer((d / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0
goods = LD.goods(m.get("world")) if m.get("world") else None
lines = TT.with_generations(m["lineages"], m.get("tree"))
fp = json.loads(dump.read_text())
towns = {k: (v if k == "_cell_km2" else (np.array(v[0]), np.array(v[1]))) for k, v in fp.items()}
landmass = TT.landmass_of(d, m)
frames = TT.frames_of(d, run)
pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
live = m["techtree"]["known"]
top = sorted([p for p in live if p in pops], key=lambda p: -pops[p])[:12]
fa = np.array([-float(f["t"]) for f in run["frames"]])
agos = sorted(set(fa.tolist()) | set(np.round(np.arange(30.0, 0, -0.1), 3).tolist()), reverse=True)
_at0, _area0 = TT._at, TT._area_at


def _j(a, ago):
    k = np.flatnonzero(np.asarray(a) >= ago - 1e-9)
    return int(k[-1]) if len(k) else 0


def held(on):
    if on:
        TT._at = lambda ser, ago: (float(ser[1][_j(ser[0], ago)]), float(ser[2][_j(ser[0], ago)]))
        TT._area_at = lambda ser, ago: None if ser is None else (lambda v: v if v > 0 else None)(float(ser[3][_j(ser[0], ago)]))
    else:
        TT._at, TT._area_at = _at0, _area0


_pt = None


def presence_at(a):
    global _pt
    if _pt is None:
        _pt = read_presence(d, m)
    j = int(np.flatnonzero(fa >= a - 1e-9)[-1]) if (fa >= a - 1e-9).any() else 0
    nl, n = _pt["offsets"].shape[1] - 1, present.shape[1]
    P = np.zeros((nl, n), np.float32)
    off = _pt["offsets"][j]
    for k in range(nl):
        x, y = int(off[k]), int(off[k + 1])
        P[k, _pt["cells"][x:y].astype(np.int64)] = _pt["share"][x:y] / 100.0
    return j, P


def report(name, known):
    w = [x for x in ((known.get(p) or {}).get("writing", [None])[0] for p in top) if x is not None]
    rows = []
    for p in set(live) | set(known):
        a, b = live.get(p) or {}, known.get(p) or {}
        for t in set(a) | set(b):
            x, y = a.get(t), b.get(t)
            if x is None or y is None or abs(x[0] - y[0]) > 1e-6:
                rows.append((max(x[0] if x else -1, y[0] if y else -1), p, t, x and x[0], y and y[0]))
    rows.sort(key=lambda r: -r[0])
    print(f"{name:28s} writing {(st.median(w) * 1000 if w else -1):,.0f} ya ({len(w)}); {len(rows)} dates differ from live; oldest: "
          + "; ".join(f"{r[1]} {r[2]} live {r[3]} here {r[4]}" for r in rows[:3]), flush=True)


for v in sys.argv[3:]:
    hs = set(v.split("+"))
    held("hold" in hs)
    c = TT.Calendar(lines, m.get("mode", "fantasy"), m.get("era"), int(m.get("try_seed") or 0), None, m.get("gods_mode", "faith_made"),
                    towns)
    have = {l["id"]: TT.goods_held(c.T, present, goods, c.idx[l["id"]]) for l in c.people}
    c.feed(lines, TT.links_of(m.get("contacts"), c.kind), TT.forced_of(m.get("present"), c.techs, c.L), have,
           (m.get("present") or {}).get("lines") or {}, c.region_shares(present, landmass), c.regions_through(frames, landmass))
    if hs != {"batch"}:
        f_all = c.forced
        s_all, e_all = dict(c.start), dict(c.end)
        st0 = {l["id"]: l.get("started_kyr") for l in lines if l["id"] in c.kind}
        en0 = {l["id"]: l.get("ended_kyr") for l in lines if l["id"] in c.kind}
        last = None
        for a in agos:
            if "starts" in hs:
                for lid in c.start:
                    c.start[lid] = float(st0[lid]) if st0[lid] is not None and float(st0[lid]) >= a else -1e9
                    c.end[lid] = float(en0[lid]) if en0[lid] is not None and float(en0[lid]) >= a else -1.0
            if "forced" in hs:
                c.forced = {lid: [x for x in xs if x[0] >= a] for lid, xs in f_all.items()}
            if "have" in hs:
                j, P = presence_at(a)
                if j != last:
                    last = j
                    c.have = {l["id"]: TT.goods_held(c.T, P, goods, c.idx[l["id"]]) for l in c.people}
            c.advance(a)
        c.start.update(s_all)
        c.end.update(e_all)
        c.forced = f_all
        c.have = have
    c.advance()
    report(v, c.result()["known"])
held(False)
