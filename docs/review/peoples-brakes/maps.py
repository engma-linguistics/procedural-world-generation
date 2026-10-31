"""Map pictures for lane 97's report (docs/review/peoples-brakes/report.md): who leads each land cell today in one dnd try, side by side
for the stages. Not viewer screenshots: a plain equirectangular plot of the same numbers the viewer's peoples layer shows.

    uv run python docs/review/peoples-brakes/maps.py shot OUT.npz WORLD SEED ['{"raiders": 4}']   (from the code checkout to picture)
    uv run --with matplotlib python docs/review/peoples-brakes/maps.py plot OUT.png TITLE=A.npz TITLE=B.npz ...
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def shot(out, world, seed, meta=None):
    sys.path.insert(0, ".")
    import tools.peoples_robust as PR
    from planet.lineages import land as LD
    from planet.lineages import recent as R
    from planet.lineages import spec as SP
    from planet.lineages.history import model as M

    raw = PR.with_seed(PR._load("dnd"), int(seed), **(json.loads(meta) if meta else {}))
    tree = SP.parse(raw)
    tz, now0, wref = R.resolve(world)
    ps = R.Pass(tz, now0, R.RecentParams(kyr=30.0, climate_every=2.0), world_ref=wref)
    goods = LD.goods(wref) if wref and tree.uses else None
    h = M.History(tree, ps, tree.seed * 1000, goods=goods)
    res = h.run()
    P = res["present"]
    peoples = [l for l in tree.leaves() if not l.group_of and not l.megafauna and not l.overlay]
    pid = {l.id: i for i, l in enumerate(peoples)}
    pop = np.zeros((len(peoples), h.grid.n))
    for k, l in enumerate(h.lines):
        if l.overlay or l.megafauna:
            continue
        who = tree.people_of(l.id)
        if who in pid:
            pop[pid[who]] += h.population(k, P)
    ev = [e for e in h.events if e["kind"] in ("cull", "hunt") and e.get("lat") is not None]
    np.savez_compressed(out, pop=pop.astype(np.float32), names=np.array([l.id for l in peoples]), lat=h.grid.lat, lon=h.grid.lon,
                        land=h.steps[-1].get()["land"], ev=json.dumps(ev))
    print({l.id: round(100 * pop[i].sum() / pop.sum(), 2) for i, l in enumerate(peoples) if pop[i].sum() / pop.sum() > 0.005})


def plot(out, panels):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from charts import INK, INK2, OTHER, PAL, PEOPLE_ORDER, SURF

    data = [(t, np.load(p)) for t, p in panels]
    # one hue per people for the peoples that lead anywhere in any panel, in the charts' fixed order; the rest grey
    lead = set()
    for _, d in data:
        pop = d["pop"]
        on = pop.sum(0) > 0
        lead |= {str(d["names"][i]) for i in np.unique(pop.argmax(0)[on])}
    ordered = sorted(lead, key=lambda p: PEOPLE_ORDER.index(p) if p in PEOPLE_ORDER else 99)
    col = {p: (PAL[PEOPLE_ORDER.index(p)] if p in PEOPLE_ORDER[:8] else OTHER) for p in ordered}
    fig, axs = plt.subplots(1, len(data), figsize=(6.2 * len(data), 3.9), facecolor=SURF)
    axs = np.atleast_1d(axs)
    for ax, (t, d) in zip(axs, data):
        ax.set_facecolor("#dfe8ef")
        lat, lon, land, pop, names = d["lat"], d["lon"], d["land"].astype(bool), d["pop"], [str(x) for x in d["names"]]
        ax.scatter(lon[land], lat[land], s=1.6, color="#e9e6dc", lw=0)
        on = land & (pop.sum(0) > 0)
        who = pop.argmax(0)
        for i, nm in enumerate(names):
            m = on & (who == i)
            if m.any():
                ax.scatter(lon[m], lat[m], s=1.8, color=col.get(nm, OTHER), lw=0)
        ev = json.loads(str(d["ev"]))
        cu = [e for e in ev if e["kind"] == "cull" and e["ago_kyr"] <= 5]
        if cu:
            ax.scatter([e["lon"] for e in cu], [e["lat"] for e in cu], s=26, marker="x", color=INK, lw=1.2, label="cull, last 5 kyr")
        tot = pop.sum()
        top = sorted(((pop[i].sum() / tot, nm) for i, nm in enumerate(names)), reverse=True)[:4]
        ax.set_title(f"{t}\n" + ", ".join(f"{nm.replace('_', ' ')} {100 * s:.0f}%" for s, nm in top), fontsize=9, color=INK, loc="left")
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#cfd6dc")
    hs = [plt.Line2D([], [], ls="", marker="s", ms=7, color=c) for p, c in col.items() if c != OTHER]
    ls = [p.replace("_", " ") for p, c in col.items() if c != OTHER]
    hs += [plt.Line2D([], [], ls="", marker="s", ms=7, color=OTHER), plt.Line2D([], [], ls="", marker="x", ms=7, color=INK)]
    ls += ["another people", "cull (last 5 kyr)"]
    fig.legend(hs, ls, loc="lower center", ncol=len(ls), fontsize=8, frameon=False, labelcolor=INK2)
    fig.suptitle("Who leads each land cell today (people count), one try of the full dnd tree", fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    fig.savefig(out, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    if sys.argv[1] == "shot":
        shot(*sys.argv[2:])
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        plot(sys.argv[2], [a.split("=", 1) for a in sys.argv[3:]])
