"""Lane 265 (PW-1597 R, round22.md): one people's region learners at a stored frame, from the presence table, on the after-run
tree's landmass map (techtree.landmass_of: demes.landmass_rank, sea cells take the nearest landmass) and on the same map with
today's sea left out (-1, as crossing.Crossings.label, which the live tree reads). Read-only. argv: run_dir people frame_ago."""
import json
import sys
from pathlib import Path

import numpy as np

from planet import timeline as TL
from planet.geo import is_land
from planet.lineages import techtree as TT
from planet.lineages.output import read_presence

d, who, at = Path(sys.argv[1]), sys.argv[2], float(sys.argv[3])
run = json.loads((d / "run.json").read_text())
m = run["meta"]
lm = TT.landmass_of(d, m)
r, arr = TL.load_frames(d, ("elevation", "ice"))
j = len(r["frames"]) - 1
land = is_land(TL.frame(r, arr, "elevation", j), TL.frame(r, arr, "ice", j))
pt = read_presence(d, m)
fa = np.array([-float(f["t"]) for f in run["frames"]])
f = int(np.flatnonzero(np.abs(fa - at) < 1e-6)[0])
k = [x["id"] for x in m["lineages"]].index(who)
off = pt["offsets"][f]
P = np.zeros((len(m["lineages"]), lm.shape[0]), np.float32)
P[k, pt["cells"][int(off[k]):int(off[k + 1])].astype(np.int64)] = pt["share"][int(off[k]):int(off[k + 1])] / 100.0
c = TT.Calendar(TT.with_generations(m["lineages"], m.get("tree")), m.get("mode", "fantasy"), m.get("era"), 0)
on_sea = float(P[k][~land].sum() / max(P[k].sum(), 1e-9))
print(f"{who} at {at} kyr: {(P[k] > 0).sum()} cells, {on_sea:.0%} of its weight on cells that are sea today")
print("  after-run map (sea filled):", c.region_shares(P, lm).get(who))
print("  today's sea left out:      ", c.region_shares(P, np.where(land, lm, -1)).get(who))
