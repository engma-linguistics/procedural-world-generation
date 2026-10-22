"""Endings test diagnostic: runs the icehouse fixture (on/off) and saves the sea-level series, ice maps."""
import sys, os, numpy as np
WT = "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44"
sys.path.insert(0, WT); sys.path.insert(0, WT + "/tests")
from helpers import run_sim
from planet import timezoom as Z, store as S
from planet.timezoom.sim import LAYERS
tag = sys.argv[1]
sim = run_sim()
src = Z.source_from_sim(sim)
src["dT"] = src["dT"] - float(os.environ.get("DT4", "4.0"))
kw = dict(veg="local", phases="0,90,0,90")
for kv in filter(None, os.environ.get("TZSET", "").split(",")):
    k, v = kv.split("=")
    kw[k] = type(getattr(Z.TZParams(), k))(v)
res = [Z.simulate(src, kyr=200, step=0.5, every=2.0, params=Z.TZParams(index=i, glacial_dt=6.0, **kw)) for i in ("on", "off")]
on, off = res
t = np.array([f["t"] for f in on["frames"]])
sl_on = np.array([f["stats"]["sea_level_change_m"] for f in on["frames"]])
sl_off = np.array([f["stats"]["sea_level_change_m"] for f in off["frames"]])
I = np.array([f["stats"]["glacial_index"] for f in on["frames"]])
e = on["cycle"]["endings"][0]
i, j = np.searchsorted(t, e["t"]), np.searchsorted(t, e["t"] + 15.0)
print(tag, "ending t", e["t"], "extra", round(sl_off[i] - sl_on[i], 1), "left", round(sl_off[j] - sl_on[j], 1))
for k in range(0, len(t), 5):
    print(f"  t {t[k]:6.1f} I {I[k]:.2f} sl_on {sl_on[k]:7.1f} sl_off {sl_off[k]:7.1f}")
ice_on = np.stack([S.decode(v, LAYERS["ice"]) for v in on["data"]["ice"]]) if False else on["data"]["ice"]
np.savez(f"{os.path.dirname(__file__)}/out/end_{tag}.npz", t=t, sl_on=sl_on, sl_off=sl_off, I=I, ice_on=on["data"]["ice"],
         ice_off=off["data"]["ice"], elev_on=on["data"]["elevation"], temp_on=on["data"]["temperature"],
         lat=sim.grid.lat if hasattr(sim, "grid") else 0, tw_on=on["state"]["t_warm"], tw_off=off["state"]["t_warm"],
         H_on=on["state"]["H"], H_off=off["state"]["H"], smb_on=on["state"]["smb"], smb_off=off["state"]["smb"], i=i, j=j)
