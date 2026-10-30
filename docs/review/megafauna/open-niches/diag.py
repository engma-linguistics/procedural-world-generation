"""diag.py WORLD ROLL OUT.npz: one dnd history run; at the steps nearest ERAS kyr ago, save per megafauna line its presence P and
habitat K (the previous step's, from h._K_now), the climate (temperature, precipitation), the peoples' pressure and density, and
the rich/empty masks. Read-only diagnosis for PW-1024 (lane 50)."""
import sys
import numpy as np
from planet.lineages import land as LD
from planet.lineages import recent as R
from planet.lineages import run as LR
from planet.lineages.history import megafauna as MG
from planet.lineages.history.model import History
from planet.lineages.spread import EST

world, roll, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
ERAS = [float(x) for x in (sys.argv[4] if len(sys.argv) > 4 else "60,30,25,20,15,10,7,5,3,2,1,0").split(",")]
tree = LR.load_tree("dnd")
tz, now0, wid = R.resolve(world)
ps = R.Pass(tz, now0, R.RecentParams(kyr=30.0, climate_every=2.0), world_ref=wid)
goods = LD.goods(wid) if (wid and tree.uses) else None
h = History(tree, ps, roll, goods=goods)
mf = [k for k, l in enumerate(h.lines) if l.megafauna]
best = {}
_orig = h._start_due


def snap(step, env, tags):
    pe = [k for k, l in enumerate(h.lines) if not (l.megafauna or l.overlay)]
    allp = (np.where(h.p[pe] >= EST, h.p[pe], 0.0) * h.dens_cells()[pe]).sum(0)
    K = np.stack([h._K_now.get(k, np.zeros(h.grid.n)) for k in mf]).astype(np.float32)
    return {"ago": step.ago, "P": h.p[mf].astype(np.float32), "K": K, "T": np.asarray(env["temperature"], np.float32),
            "R": np.asarray(env["precipitation"], np.float32), "cl": np.asarray(env.get("climate", np.zeros(1)), np.int16), "land": np.asarray(env["land"]), "allp": allp.astype(np.float32),
            "press": (h._press if h._press is not None else np.zeros(h.grid.n)).astype(np.float32),
            "prey": (h._prey if h._prey is not None else np.zeros(h.grid.n)).astype(np.float32),
            **{"tag_" + t: np.asarray(tags[t]) for t in ("steppe", "forest", "hills", "mountain", "coast", "desert", "wetland", "open", "jungle", "tundra", "volcanic", "lowland") if t in tags}}


def _start(step, env, tags, Ks, _o=_orig):
    if step.epoch != "deep":
        hit = [e for e in ERAS if e not in best or abs(step.ago - e) < abs(best[e]["ago"] - e)]
        if hit:
            s = snap(step, env, tags)
            for e in hit:
                best[e] = s
    return _o(step, env, tags, Ks)


h._start_due = _start
res = h.run()
best["final"] = snap(type("S", (), {"ago": 0.0})(), {"temperature": best[min(ERAS)]["T"], "precipitation": best[min(ERAS)]["R"],
                                                       "land": best[min(ERAS)]["land"], "climate": best[min(ERAS)]["cl"]}, h._tags_now)
best["final"]["P"] = res["present"][mf].astype(np.float32)
save = {"mf_ids": np.array([h.lines[k].id for k in mf])}
for e, d in best.items():
    for key, v in d.items():
        save[f"{key}@{e if e == 'final' else f'{e:g}'}"] = np.asarray(v)
np.savez_compressed(out, **save)
print("saved", out)
