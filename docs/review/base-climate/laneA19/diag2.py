"""What keeps the endings test's leftover ice cold: 15 kyr after the first ending, the index-on run's year on its
own surface (A), with the index-off run's climate fields at that moment (B: the full climate's response to the
glacial's sheets taken out; the on-run's surface height still lapsed from the off-run's), and with its own fields
but without the ice surface's local terms (C: ice_cool, the summer damping), over the cells holding the leftover
extra ice (weighted by it). usage (from a tree's root): PYTHONPATH=.:tests uv run python diag2.py SRC.pkl [k=v ...]"""
import pickle
import sys

from planet import timezoom as Z  # planet before numpy (lane A16)
from planet import climate
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
# a first on-run finds the ending
on0 = Z.simulate(src, kyr=200, step=0.5, every=2.0, params=Z.TZParams(index="on", glacial_dt=6.0, **kw))
e = on0["cycle"]["endings"][0]["t"]
T = float(np.ceil((e + 15.0) / 2.0) * 2.0)  # the test's frame (searchsorted on 2 kyr frames)
keep = {}
orig = SIM._Sim.record


def record(self, t_kyr, orb, dq65, dTg):
    orig(self, t_kyr, orb, dq65, dTg)
    if abs(t_kyr - T) > 1e-6:
        return
    surf, gr = self.grounded_surface()
    st = dict(H=self.H.copy(), gr=gr, surf=surf, bed=self.bed.copy(), sl=self.sl, f={k: (np.copy(v) if isinstance(v, np.ndarray) else v) for k, v in self.fields.f.items() if isinstance(v, (np.ndarray, float))})
    if self.p.index == "off":
        keep["off"] = st
        return
    keep["on"] = st
    out = {}
    s_save = [a.copy() for a in (self.smb, self.t_ann, self.t_warm, self.t_cold, self.p_scale, self.f_snow)]
    dq = SIM.insolation(*orb) - self.q_ref
    out["A"] = (self.t_warm.copy(), self.smb.copy())
    F = self.fields.f
    mine = {k: F[k] for k in ("t_mean", "half", "p_jul", "p_jan", "s0", "dTg0")}
    F.update({k: keep["off"]["f"][k] for k in mine})
    self.prepare_surface(dTg)
    self.year(self.dt_base, dq)
    out["B"] = (self.t_warm.copy(), self.smb.copy())
    F.update(mine)
    self.prepare_surface(dTg)
    cool, damp = self.p.ice_cool, self.damp
    self.p.ice_cool, self.damp = 0.0, np.zeros(self.n)
    self.year(self.dt_base, dq)
    out["C"] = (self.t_warm.copy(), self.smb.copy())
    self.p.ice_cool = cool
    for a, b in zip((self.smb, self.t_ann, self.t_warm, self.t_cold, self.p_scale, self.f_snow), s_save):
        a[:] = b
    keep["out"] = out


SIM._Sim.record = record
for ix in ("off", "on"):
    Z.simulate(src, kyr=200, step=0.5, every=2.0, params=Z.TZParams(index=ix, glacial_dt=6.0, **kw))
g = src["grid"]
area = SIM.geometry(g)["area"]
a, b = keep["on"], keep["off"]
ex = np.maximum(np.where(a["gr"], a["H"], 0) - np.where(b["gr"], b["H"], 0), 0) * area
print(f"{sys.argv[1].split('/')[-1]} {' '.join(sys.argv[2:])}: ending {e}, frame {T}")
for nm, m in (("land", a["gr"] & (a["bed"] >= a["sl"])), ("marine", a["gr"] & (a["bed"] < a["sl"]))):
    w = ex * m
    if w.sum() <= 0:
        continue
    avg = lambda x: (x * w).sum() / w.sum()
    dz = avg(a["surf"] - np.maximum(b["surf"], 0))
    s = "  ".join(f"{k}: t_warm {avg(tw):+5.1f} smb {avg(sm):+.3f}" for k, (tw, sm) in keep["out"].items())
    print(f"  {nm:6s} (extra weight {w.sum() / 1e15:.2f} Mkm3, on - off surface {dz:+.0f} m = {-dz * climate.LAPSE:+.1f} C): {s}")
    fo, ff = a["f"], b["f"]
    print(f"     fields on - off at these cells: t_mean {avg(fo['t_mean'] - ff['t_mean']):+.1f} (of it the lapse over s0 "
          f"{-avg(fo['s0'] - ff['s0']) * climate.LAPSE:+.1f}), half {avg(fo['half'] - ff['half']):+.1f}, "
          f"p_jan+p_jul ratio {avg(fo['p_jul'] + fo['p_jan']) / avg(ff['p_jul'] + ff['p_jan']):.2f}")
