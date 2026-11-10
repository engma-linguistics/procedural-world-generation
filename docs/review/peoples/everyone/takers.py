"""For each people that died out: its land before the end (frame of its peak and its last frame) and who holds that land after.
Usage: takers.py RUN_DIR"""
import json, sys
import numpy as np
from pathlib import Path

d = Path(sys.argv[1])
r = json.loads((d / "run.json").read_text())
m, ev = r["meta"], r["events"]
P = m["presence"]
nf, nl = P["frames"], P["lines"]
off = np.fromfile(d / P["files"]["offsets"], dtype=P["dtypes"]["offsets"]).astype(np.int64)
cells = np.fromfile(d / P["files"]["cells"], dtype=P["dtypes"]["cells"])
share = np.fromfile(d / P["files"]["share"], dtype=P["dtypes"]["share"])
times = [f["t"] for f in r["frames"]]
L = m["lineages"]
idx = {l["id"]: l["index"] for l in L}
name = {l["index"]: l["id"] for l in L}
off = off.reshape(-1)


def pres(f, k):
    a, b = off[f * (nl + 1) + k], off[f * (nl + 1) + k + 1]
    return cells[a:b].astype(np.int64), share[a:b]


extinct = [(e["t"], e["text"]) for e in ev if e["kind"] == "extinct"]
lab = {l["name"]: l["id"] for l in L}
for t, text in extinct:
    lid = next((i for n, i in lab.items() if text.startswith(n + " dies out")), None)
    if lid is None:
        continue
    k = idx[lid]
    fr = [f for f in range(nf) if off[f * (nl + 1) + k + 1] > off[f * (nl + 1) + k]]
    if not fr:
        print(f"{lid:16} died {-t:g} kyr ago: never held land in a stored frame (stillborn)")
        continue
    last = fr[-1]
    c, s = pres(last, k)
    nxt = min(last + 1, nf - 1)
    held = {}
    for j in range(nl):
        if j == k:
            continue
        cj, sj = pres(nxt, j)
        hit = np.isin(cj, c)
        if hit.any():
            held[name[j]] = int(hit.sum())
    top = sorted(held.items(), key=lambda x: -x[1])[:4]
    empty = len(c) - len(set(np.concatenate([pres(nxt, j)[0] for j in range(nl) if j != k])) & set(c.tolist()))
    print(f"{lid:16} died {-t:g} kyr ago; last frame {-times[last]:g} kyr: {len(c)} cells (median share {int(np.median(s))}%); "
          f"at {-times[nxt]:g} kyr held by {top}; left empty {empty}")
