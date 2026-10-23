"""The endings test's ice budget around the first ending: accumulation, ablation, calving (Gt/yr; sim.flows) of the
index-on run minus the index-off run, in 5 kyr windows from 20 kyr before the ending to 20 kyr after, and the cells
under ice. usage (from a tree's root): PYTHONPATH=.:tests uv run python xflows.py SRC.pkl"""
import pickle
import sys

from planet import timezoom as Z  # planet before numpy
import numpy as np

src = pickle.load(open(sys.argv[1], "rb"))
src["dT"] = src["dT"] - 4.0
kw = dict(veg="local", phases="0,90,0,90")
on, off = [Z.simulate(src, kyr=200, step=0.5, every=2.0, params=Z.TZParams(index=i, glacial_dt=6.0, **kw))
           for i in ("on", "off")]
e = on["cycle"]["endings"][0]["t"]
fo, ff = np.asarray(on["flows"]), np.asarray(off["flows"])
t = 0.5 * (np.arange(len(fo)) + 1)
print(f"{sys.argv[1]}: source dT {src['dT'] + 4:.2f} (zoom start {src['dT']:.2f}), ending at {e} kyr; flows cols "
      f"{fo.shape[1]} (accumulation, ablation, calving, NH net ...), Gt/yr: on | off")
for a in range(-20, 20, 5):
    m = (t > e + a) & (t <= e + a + 5)
    print(f"  {a:+3d}..{a + 5:+3d} kyr: on " + " ".join(f"{x:8.0f}" for x in fo[m].mean(0)) +
          " | off " + " ".join(f"{x:8.0f}" for x in ff[m].mean(0)))
for nm, r in (("on", on), ("off", off)):
    fr = r["frames"]
    tt = np.array([f["t"] for f in fr])
    for k in (e, e + 15.0):
        i = int(np.searchsorted(tt, k))
        st = fr[i]["stats"]
        print(f"  {nm} t={tt[i]:.0f}: " + ", ".join(f"{q}={st[q]:.3g}" for q in sorted(st) if "ice" in q or "sea_level" in q))
