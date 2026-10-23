"""The endings test's numbers on a pickled source (lane A18's xzoom.py), with TZParams overrides, and where the
glacial's extra ice is at the ending and 15 kyr later. usage (from a tree's root):
  PYTHONPATH=.:tests uv run python scan.py SRC.pkl [k=v ...]
Prints one 'ending' line (as A18's seedscan) and a few diagnostic lines."""
import pickle
import sys

from planet import timezoom as Z  # planet before numpy (lane A16)
from planet.timezoom.geometry import geometry
import numpy as np

src = pickle.load(open(sys.argv[1], "rb"))
over = {}
for a in sys.argv[2:]:
    k, v = a.split("=", 1)
    ty = type(getattr(Z.TZParams(), k))
    over[k] = (v.lower() in ("1", "true")) if ty is bool else ty(v)
src["dT"] = src["dT"] - 4.0
kw = dict(veg="local", phases="0,90,0,90", **over)
on, off = [Z.simulate(src, kyr=200, step=0.5, every=2.0, params=Z.TZParams(index=i, glacial_dt=6.0, **kw))
           for i in ("on", "off")]
t = np.array([f["t"] for f in on["frames"]])
so = np.array([f["stats"]["sea_level_change_m"] for f in on["frames"]])
sf = np.array([f["stats"]["sea_level_change_m"] for f in off["frames"]])
e = on["cycle"]["endings"][0]
i, j = np.searchsorted(t, e["t"]), np.searchsorted(t, e["t"] + 15.0)
ex, left = sf[i] - so[i], sf[j] - so[j]
print(f"{sys.argv[1].split('/')[-1]} {' '.join(sys.argv[2:])}: ending at {e['t']} kyr; extra {ex:.1f} m, "
      f"left {left:.1f} m; sl_off {sf[i]:.1f} -> {sf[j]:.1f}, sl_on {so[i]:.1f} -> {so[j]:.1f}; "
      f"pass={ex > 10 and left < 0.5 * ex}")
print("  sl_on  every 10 kyr:", np.round(so[::5], 1).tolist())
print("  sl_off every 10 kyr:", np.round(sf[::5], 1).tolist())
g = src["grid"]
area = geometry(g)["area"]
oa = on["budget"]["ocean_area"]
bands = [(-90, -60), (-60, -40), (-40, 0), (0, 40), (40, 60), (60, 75), (75, 90)]
for nm, k in (("ending", i), ("+15 kyr", j)):
    d = (on["data"]["ice"][k].astype(float) - off["data"]["ice"][k].astype(float)) * area * 0.917 / oa  # m sl, crude
    s = " ".join(f"{a}..{b}:{d[(g.lat >= a) & (g.lat < b)].sum():6.1f}" for a, b in bands)
    print(f"  extra ice (m sl, on - off, by lat) at {nm}: {s}")
fo = np.asarray(on["flows"])
tt = 0.5 * (np.arange(len(fo)) + 1)
for a in range(-10, 20, 5):
    m = (tt > e["t"] + a) & (tt <= e["t"] + a + 5)
    print(f"  on flows {a:+3d}..{a + 5:+3d} kyr (acc abl calv NHnet Gt/yr): " + " ".join(f"{x:7.0f}" for x in fo[m].mean(0)))
