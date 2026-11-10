"""Lane 267: peoples runs side by side (lead people per land cell at the present, towns and cities) and town-siting numbers, every
run's sites read on the same fine world (the refined L8 world), so a coarse run's town is judged on the fine coast it would sit on.
usage: compare.py <fine_world> <out_prefix> <lon0> <lon1> <lat0> <lat1> <label=run_dir> ...   Read-only on the runs and the world."""
import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from planet import store as S, timeline as T
from planet import world as W
from planet.geo import is_land
from planet.grid import shared_grid

fw, pre = sys.argv[1], sys.argv[2]
box = [float(x) for x in sys.argv[3:7]]
runs = [a.split("=", 1) for a in sys.argv[7:]]
w = W.load(S.find_world(fw))
G = shared_grid(w["meta"]["level"])
el = w["layers"]["elevation"].astype(float)
lake = w["layers"]["lake"].astype(float) > 0 if "lake" in w["layers"] else np.zeros(G.n, bool)
iceW = w["layers"]["ice"].astype(float)
landW = is_land(el, iceW)
sea = ~landW & ~lake
nb_sea = np.zeros(G.n, bool)
src = np.repeat(np.arange(G.n), np.diff(G.nbr_off))
np.logical_or.at(nb_sea, src, sea[G.nbr_idx])
coast = landW & nb_sea
nav = w["layers"]["river_nav"].astype(float) > 0
# landmasses of the fine world
lab, k = G.components(landW)
size = np.bincount(lab[lab >= 0], minlength=k)
area_km2 = 4 * np.pi * 6371.0 ** 2 / G.n
small = np.where(lab >= 0, size[np.maximum(lab, 0)] * area_km2 < 3e5, False)  # (islands under 0.3 Mkm2)


def on_fine(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    v = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
    return G.locate(v)


stats = {}
fig, axes = plt.subplots(2, len(runs), figsize=(9 * len(runs), 9.5), dpi=110, squeeze=False)
for j, (label, d) in enumerate(runs):
    d = Path(d)
    run, arr = T.load_frames(d, ("elevation", "ice", "mix_lead"))
    m = run["meta"]
    g = shared_grid(m["level"])
    kf = len(run["frames"]) - 1
    elev, ice = T.frame(run, arr, "elevation", kf), T.frame(run, arr, "ice", kf)
    lead = np.asarray(T.frame(run, arr, "mix_lead", kf)).astype(int)
    land = is_land(elev, ice)
    nl = len(m["lineages"])
    peopled = land & (lead >= 0) & (lead < nl)
    sites = json.loads((d / "settlements.json").read_text())["sites"]
    tiers = Counter(s["tier_now"] for s in sites)
    tc = [s for s in sites if s["tier_now"] in ("town", "city")]
    lat = np.array([s["lat"] for s in tc]); lon = np.array([s["lon"] for s in tc])
    c = on_fine(lat, lon) if len(tc) else np.zeros(0, int)
    isl = np.unique(lab[c][small[c] & (lab[c] >= 0)]) if len(c) else []
    stats[label] = {"run": d.name, "level": m["level"], "cells": g.n, "generated_in_s": m.get("generated_in_s"),
                    "handover": m.get("handover"), "tiers_now": {t: tiers.get(t, 0) for t in ("village", "town", "city")},
                    "peopled_land_share": round(float(peopled.sum() / max(land.sum(), 1)), 3),
                    "towns_cities": len(tc),
                    "on_fine_coast_pct": round(100 * float(coast[c].mean()), 1) if len(c) else None,
                    "on_fine_river_pct": round(100 * float(nav[c].mean()), 1) if len(c) else None,
                    "in_fine_water_pct": round(100 * float((~landW[c]).mean()), 2) if len(c) else None,
                    "islands_with_a_town": int(len(isl)),
                    "lead_peoples": len(set(lead[peopled].tolist()))}
    lo, la = g.lon if np.abs(g.lon).max() > 7 else np.degrees(g.lon), g.lat if np.abs(g.lat).max() > 2 else np.degrees(g.lat)
    cmap = plt.get_cmap("tab20")
    col = np.where(peopled[:, None], cmap(np.mod(lead, 20))[:, :3], np.where(land[:, None], [[0.75, 0.72, 0.65]], [[0.80, 0.87, 0.95]]))
    for i, ax in enumerate(axes[:, j]):
        if i == 0:
            ax.scatter(lo, la, c=col, s=0.5 if g.n > 300000 else 1.6, marker="s", linewidths=0)
            ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
            ax.plot([box[0], box[1], box[1], box[0], box[0]], [box[2], box[2], box[3], box[3], box[2]], "k-", lw=0.8)
        else:
            sel = (lo >= box[0] - 2) & (lo <= box[1] + 2) & (la >= box[2] - 2) & (la <= box[3] + 2)
            ax.scatter(lo[sel], la[sel], c=col[sel], s=14 if g.n > 300000 else 55, marker="h", linewidths=0)
            ax.set_xlim(box[0], box[1]); ax.set_ylim(box[2], box[3])
        for tier, mk, sz in (("town", ".", 2 if i == 0 else 10), ("city", "*", 30 if i == 0 else 90)):
            xy = np.array([(s["lon"], s["lat"]) for s in tc if s["tier_now"] == tier]).reshape(-1, 2)
            ax.scatter(xy[:, 0], xy[:, 1], s=sz, marker=mk, c="k", label=f"{tier}s {len(xy)}" if i == 0 else None)
        ax.set_aspect("equal")
        if i == 0:
            ax.set_title(f"{label}: L{m['level']} ({g.n:,} cells), {m.get('generated_in_s', 0) / 60:.0f} min", fontsize=10)
            ax.legend(loc="lower left", fontsize=8)
fig.suptitle("Lead people per land cell at the present, towns (dots) and cities (stars); bottom row: the boxed region", fontsize=11)
fig.tight_layout()
fig.savefig(f"{pre}.png")
print(json.dumps(stats, indent=1))
Path(f"{pre}.json").write_text(json.dumps(stats, indent=1))
