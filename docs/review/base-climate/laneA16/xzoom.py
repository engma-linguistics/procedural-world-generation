"""Cross-check: the icehouse test's zoom on a pickled source (so main's world can be zoomed with the branch's
climate and vice versa). usage (from a tree's root):
  PYTHONPATH=.:tests uv run python xzoom.py dump OUT.pkl          # sim4's source (L4 s1 300 Myr) of this tree
  PYTHONPATH=.:tests uv run python xzoom.py zoom SRC.pkl [belt1] [col1]   # the icehouse test's numbers on it
belt1 / col1: westerly_belt / low_column forced to 1 (A15's steps off) if this tree has them."""
import pickle
import sys

import numpy as np

from planet import climate, timezoom as Z

if sys.argv[1] == "dump":
    from helpers import run_sim
    src = Z.source_from_sim(run_sim())
    pickle.dump(src, open(sys.argv[2], "wb"))
    print("dumped; ice cells>1m %.2f%%" % (100 * (src["ice"] > 1).mean()), "dT", src["dT"])
    sys.exit()
src = pickle.load(open(sys.argv[2], "rb"))
if "belt1" in sys.argv and hasattr(climate, "westerly_belt"):
    climate.westerly_belt = lambda g, a, b: (np.ones(g.n), np.ones(g.n))
if "col1" in sys.argv and hasattr(climate, "low_column"):
    climate.low_column = lambda g, land, tune: np.ones(g.n)
src["dT"] = src["dT"] - 4.0
kw = dict(veg="local", phases="0,90,0,90")
on, off = [Z.simulate(src, kyr=200, step=0.5, every=2.0, params=Z.TZParams(index=i, glacial_dt=6.0, **kw))
           for i in ("on", "off")]
t = np.array([f["t"] for f in on["frames"]])
so = np.array([f["stats"]["sea_level_change_m"] for f in on["frames"]])
sf = np.array([f["stats"]["sea_level_change_m"] for f in off["frames"]])
e = on["cycle"]["endings"][0]
i, j = np.searchsorted(t, e["t"]), np.searchsorted(t, e["t"] + 15.0)
ex, left = sf[i] - so[i], sf[j] - so[j]
print(f"{sys.argv[2:]}: ending at {e['t']} kyr; extra {ex:.1f} m, left {left:.1f} m; "
      f"sl_off {sf[i]:.1f} -> {sf[j]:.1f}, sl_on {so[i]:.1f} -> {so[j]:.1f}; pass={ex > 10 and left < 0.5 * ex}")
print("  sl_on series every 10 kyr:", np.round(so[::5], 1).tolist())
print("  sl_off series every 10 kyr:", np.round(sf[::5], 1).tolist())
