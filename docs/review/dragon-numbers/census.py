"""census.py WORLD ROLL OUTDIR [probe.py flags...]: one dnd history run (docs/review/megafauna/probe.py, unchanged, with --eras and
--cells) plus a dragon census at the present, written to OUTDIR/WORLD_ROLL.census.npz and OUTDIR/WORLD_ROLL.census.json.

Run from the repository root (the code in the current directory is the code measured). The census, per dragon kind:
- `now`: the expected dragons per cell at the present, as the model's summary counts them (presence x density per km2 x cell area).
- `nopeople`: the same history's dragons on the same cells with every people taken out of the food budget and the kill (no overkill
  of the wild herds, no hunters' take, no livestock, no persecution, the smaller predators not pressed): the land before people.
- `nopeople_country`: the same, over the kind's whole own country (its habitat without ecological release at least
  megafauna.SUITABLE), as if it held all of it: the most the land would carry before people.
- the people per cell (all small folk), the biome tags, the land, the persecution `kill` per cell, and each kind's count over time.
- `by_people`: the persecution's weight by people (people x means; the kill is KILL_Q x their sum).
`tables.py` reads these. `run_all.sh` runs the six worlds.
"""
import json
import os
import runpy
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
import numpy as np  # noqa: E402

world, roll, outdir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
outdir.mkdir(parents=True, exist_ok=True)
key = f"{world}_{roll}"
extra = sys.argv[4:]
from planet.lineages.history import megafauna as MG  # noqa: E402
from planet.lineages.spread import EST  # noqa: E402

if "--no-sea" in extra:  # (D28 B off: the sea hunters live on the land's food alone, to measure what the sea food does)
    extra.remove("--no-sea")
    MG.SEA_FOOD = False
sys.argv = ["probe.py", world, roll, str(outdir / f"{key}.json"), "--eras", "31,29,25,10,5,0", "--cells", str(outdir / "cells")] + extra
g = runpy.run_path("docs/review/megafauna/probe.py", run_name="__main__")

h, P = g["h"], g["P"]
tags, land = h._tags_now, np.asarray(h._land_now, bool)
area = h.cell_mkm2 * 1e6
fl = [k for k, l in enumerate(h.lines) if l.megafauna and "flies" in l.traits]
ids = [h.lines[k].id for k in fl]
small = MG._small_w(h)


def census(PP, people_on: bool):
    """Expected dragons per cell for each kind under presences PP (people rows as given)."""
    press = MG.pressure(h, PP, land)
    kl = MG.kill(h, PP, land)
    if not people_on:
        kl = np.zeros_like(kl)
    b = MG.budget(h, PP, press, tags, kl)
    out = []
    for k in fl:
        d = MG.local_density(h, k, kl, b["prey"], b["food"], PP)
        out.append(np.where(PP[k] >= EST, PP[k], 0.0) * d * area)
    return np.array(out, np.float32), b


now, b_now = census(P, True)
P0 = P.copy()
P0[small > 0] = 0.0  # (every people out)
nop, b0 = census(P0, False)
S = h._suit()
Pc = P0.copy()
own = getattr(h, "_K_own", {})
from planet.lineages import compose as CP  # noqa: E402

for k in fl:
    K = own.get(k)
    s = np.where(K >= EST, np.clip(K / CP.SUIT_K, 0.0, 1.0), 0.0) if K is not None else S[k]
    Pc[k] = np.where(s >= MG.SUITABLE, 1.0, 0.0)
nopc, _ = census(Pc, False)
people = (np.where(P >= EST, P, 0.0) * h.dens_cells() * small[:, None]).sum(0) * area  # (people per cell)
bits = np.zeros(h.grid.n, np.uint16)
for bi, tg in enumerate(g["BIOME_TAGS"]):
    if tg in tags:
        bits |= (np.asarray(tags[tg], bool).astype(np.uint16) << bi)
m = MG.means(h)
occ = np.where(P >= EST, P, 0.0)
dm = h.dens_cells()
by_people = {}
for k, l in enumerate(h.lines):
    if small[k] > 0:
        ppl = float((occ[k] * dm[k]).sum() * area)
        if ppl > 0:
            by_people[l.id] = {"people": ppl, "means": float(m[k]), "kill_w": ppl * float(m[k]), "cells": int((P[k] >= EST).sum())}
tracks = {h.lines[k].id: [[r[0], r[4]] for r in h.tracks[h.lines[k].id]] for k in fl}
np.savez_compressed(outdir / f"{key}.census.npz", ids=np.array(ids), now=now, nopeople=nop, nopeople_country=nopc,
                    people=people.astype(np.float32), biome_bits=bits, biome_tags=np.array(g["BIOME_TAGS"]), land=land,
                    kill=np.asarray(MG.kill(h, P, land), np.float32), food=np.asarray(b_now["food"], np.float32),
                    food0=np.asarray(b0["food"], np.float32), sea_food=np.asarray(getattr(h, "sea_food", np.zeros(h.grid.n)), np.float32),
                    cell_km2=np.array(area), lat=np.asarray(h.grid.lat, np.float32))
json.dump({"world": world, "roll": int(roll), "by_people": by_people, "kill_w_sum": sum(r["kill_w"] for r in by_people.values()),
           "tracks": tracks, "count_now": {i: float(now[j].sum()) for j, i in enumerate(ids)},
           "count_nopeople": {i: float(nop[j].sum()) for j, i in enumerate(ids)},
           "count_nopeople_country": {i: float(nopc[j].sum()) for j, i in enumerate(ids)}},
          open(outdir / f"{key}.census.json", "w"), indent=1)
print("census", key, round(float(now.sum())), "now,", round(float(nop.sum())), "without people")
