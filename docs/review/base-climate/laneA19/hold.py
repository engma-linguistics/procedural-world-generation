"""Is the endings test's leftover ice slow or held? The index-on run with I kept at 0 from the end of its first
ending (e + end_kyr) to 200 kyr, against the index-off run: the glacial's extra ice (sea level, off - on) every
10 kyr after the ending, and its e-folding time. usage (from a tree's root):
  PYTHONPATH=.:tests uv run python hold.py SRC.pkl [k=v ...]"""
import pickle
import sys

from planet import timezoom as Z  # planet before numpy (lane A16)
from planet.timezoom import sim as SIM
import numpy as np

src = pickle.load(open(sys.argv[1], "rb"))
over = {}
for a in sys.argv[2:]:
    k, v = a.split("=", 1)
    ty = type(getattr(Z.TZParams(), k))
    over[k] = (v.lower() in ("1", "true")) if ty is bool else ty(v)
src["dT"] = src["dT"] - 4.0
kw = dict(veg="local", phases="0,90,0,90", **over)
P = lambda ix: Z.TZParams(index=ix, glacial_dt=6.0, **kw)
on, off = [Z.simulate(src, kyr=200, step=0.5, every=2.0, params=P(i)) for i in ("on", "off")]
e = on["cycle"]["endings"][0]["t"]
cut = e + P("on").end_kyr
orig = SIM._Sim.setup_index


def setup_index(self):
    orig(self)
    self.index.I[int(round(cut / self.step)):] = 0.0


SIM._Sim.setup_index = setup_index
held = Z.simulate(src, kyr=200, step=0.5, every=2.0, params=P("on"))
t = np.array([f["t"] for f in held["frames"]])
sh = np.array([f["stats"]["sea_level_change_m"] for f in held["frames"]])
sf = np.array([f["stats"]["sea_level_change_m"] for f in off["frames"]])
ex = sf - sh
i0 = int(np.searchsorted(t, e))
row = [(t[k] - e, ex[k]) for k in range(i0, len(t), 5)]
tail = ex[t >= t[-1] - 40].mean()
tau = [dt / np.log(ex[i0] / x) if 0 < x < ex[i0] else np.inf for dt, x in row[1:]]
print(f"{sys.argv[1].split('/')[-1]} {' '.join(sys.argv[2:])}: ending {e}, I = 0 from {cut}; extra after the ending "
      f"(kyr: m): " + " ".join(f"{dt:.0f}:{x:.0f}" for dt, x in row) + f" | last 40 kyr mean {tail:.1f} m "
      f"({tail / ex[i0]:.2f} of the glacial's); off mean {sf.mean():.1f} m")
