"""Replays the tree of a stored switch-on run step by step, each input either the whole run's (as the after-run tree) or as the
history knew it at the step (as the live tree): km = each pair's border median so far (meta's thinned series), ser = the tracks
so far (held at the last frame), have = the goods held as the live tree was fed them (l195_log.pkl feeds). Read-only on the run.
argv: run_dir variant[,variant...]  (variants: none, km, ser, have, and + joins, e.g. km+ser+have)"""
import json, pickle, sys
from pathlib import Path
import numpy as np
from planet.lineages import techtree as TT
from planet.lineages import land as LD

d = Path(sys.argv[1])
run = json.loads((d / "run.json").read_text())
m = run["meta"]
pp = m.get("presence_present")
present = np.frombuffer((d / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0
goods = LD.goods(m.get("world"))
lines = TT.with_generations(m["lineages"], m.get("tree"))
seed = int(sys.argv[3]) if len(sys.argv) > 3 else int(m.get("try_seed") or 0)
log = pickle.loads((d / "l195_log.pkl").read_bytes()) if (d / "l195_log.pkl").exists() else {"feeds": []}
feeds = sorted(log["feeds"], key=lambda f: f["step"])
live = m["techtree"]["known"]
WATCH = ["villages", "towns", "tokens", "proto_writing", "writing", "cities", "kingship", "law"]


def make():
    c = TT.Calendar(lines, m.get("mode", "fantasy"), m.get("era"), seed, None, m.get("gods_mode", "faith_made"), None, None)
    have = {l["id"]: TT.goods_held(c.T, present, goods, c.idx[l["id"]]) for l in c.people}
    c.feed(lines, TT.links_of(m.get("contacts"), c.kind), TT.forced_of(m.get("present"), c.techs, c.L), have,
           (m.get("present") or {}).get("lines") or {})
    return c


def retime(c, ago):
    """A live front fixed earlier is re-timed (never later) from the pair's border now known: its delay at today's rate."""
    D = c.D
    lk = {}
    for a, b, fr, to, km in c.links:
        if fr >= ago >= to:
            lk[(a, b)] = lk[(b, a)] = (fr, min(km / D["contact_full_km"], 1.0))
    for k3, at in list(c.arrive.items()):
        x, y, tid = k3
        if (at is None and (c.techs[tid].get("modern_contact") and c.node[y] is None)) or (at is not None and at >= ago) or tid in c.known[y] or (x, y) not in lk or tid not in c.known[x]:
            continue
        fr, w = lk[(x, y)]
        t = c.techs[tid]
        op = 1 - 0.7 * float((c.L[y].get("demography") or {}).get("insularity", 0.3))
        r = TT.contact_rate(TT._area_at(c.series[y], ago), D) * w * op * t.get("spread", D["spread"]) * TT.domain_x(c.culture[y][1], t)
        if r > 0:
            new = min(c.known[x][tid][0], fr) - c.unit[(x, y)] / r
            if at is None or new > at:
                c.arrive[k3] = new


def run_variant(v):
    on = set(v.split("+")) - {"none"}
    c = make()
    full_links = list(c.links)
    full_series = dict(c.series)
    pairs = {(p["a"], p["b"]): p.get("series") or [] for p in m["contacts"]["pairs"]}
    c.advance(1e12)  # (fix the grid; no step runs)
    fi = 0
    while c.step < len(c.grid):
        g = c.grid[c.step]
        if "km" in on or "now" in on or "peak" in on:
            links = []
            for a, b, fr, to, km in full_links:
                so = [q[1] for q in pairs[(a, b)] if q[0] >= g - 1e-9]
                links.append((a, b, fr, to, (float(so[-1]) if "now" in on else float(max(so)) if "peak" in on else float(np.median(so))) if so else km))
            c.links = links
            if "retime" in on:
                retime(c, g)
        if "ser" in on:
            ser = {}
            for lid, s in full_series.items():
                if s is None:
                    ser[lid] = None
                    continue
                k = s[0] >= g - 1e-9
                ser[lid] = tuple(x[k] for x in s) if k.any() else None
            c.series = ser
        if "have" in on:
            while fi < len(feeds) and feeds[fi]["step"] <= c.step:
                c.have = {k: (set(x) if x is not None else None) for k, x in feeds[fi]["have"].items()}
                fi += 1
        c.advance(g)
    return c.known


_c = make(); _c.advance(); after = _c.known
pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
big = sorted([p for p in live if p in pops], key=lambda p: -pops[p])[:12]


def score(K, ref):
    """(median |move| over the big peoples' watched dates, dates known in one only)"""
    mv, one = [], 0
    for p in big:
        for t in WATCH:
            a, b = (K.get(p, {}).get(t) or [None])[0], (ref.get(p, {}).get(t) or [None])[0]
            if (a is None) != (b is None):
                one += 1
            elif a is not None:
                mv.append(abs(a - b) * 1000)
    return round(float(np.median(mv)), 0), round(float(np.mean(mv)), 0), one


def wr(K, p):
    v = K.get(p, {}).get("writing")
    return "-" if not v else str(int(round(v[0] * 1000)))


OUT = {}
for v in sys.argv[2].split(","):
    K = run_variant(v)
    OUT[v] = {p: {t: (K.get(p, {}).get(t) or [None])[0] for t in WATCH} for p in K}
    print(f"{v:14s} vs after {score(K, after)}  vs live {score(K, live)}  writing:",
          " ".join(f"{p}={wr(K, p)}" for p in ["human", "hobgoblin", "leonin", "bugbear", "orc", "elf", "tabaxi", "gnome"]), flush=True)
print("live           writing:", " ".join(f"{p}={wr(live, p)}" for p in ["human", "hobgoblin", "leonin", "bugbear", "orc", "elf", "tabaxi", "gnome"]))
print("after          writing:", " ".join(f"{p}={wr(after, p)}" for p in ["human", "hobgoblin", "leonin", "bugbear", "orc", "elf", "tabaxi", "gnome"]))

OUT["after"] = {p: {t: (after.get(p, {}).get(t) or [None])[0] for t in WATCH} for p in after}
if len(sys.argv) > 4:
    json.dump(OUT, open(sys.argv[4], "w"))
