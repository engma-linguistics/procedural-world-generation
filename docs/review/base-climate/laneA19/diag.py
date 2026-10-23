"""Where the endings test's leftover ice is and what holds it: the index-on and -off runs' states at the first
ending and 15 kyr later, the on - off extra ice split by what the cell is (land above / below its equilibrium line,
marine, shelf), its latitude, surface height, bed depression. usage (from a tree's root):
  PYTHONPATH=.:tests uv run python diag.py SRC.pkl [k=v ...]"""
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

snaps = {}
orig = SIM._Sim.record


def record(self, t_kyr, orb, dq65, dTg):
    orig(self, t_kyr, orb, dq65, dTg)
    surf, gr = self.grounded_surface()
    snaps[self.p.index][round(t_kyr, 3)] = dict(
        H=self.H.copy(), bed=self.bed.copy(), sl=self.sl, smb=self.smb.copy(), surf=surf, gr=gr, t_warm=self.t_warm.copy(),
        dep=(self.bed_rest - self.bed).copy(), dTg=dTg, f_snow=self.f_snow.copy())


SIM._Sim.record = record
res = {}
for ix in ("on", "off"):
    snaps[ix] = {}
    res[ix] = Z.simulate(src, kyr=200, step=0.5, every=2.0, params=Z.TZParams(index=ix, glacial_dt=6.0, **kw))
on = res["on"]
e = on["cycle"]["endings"][0]["t"]
ts = sorted(snaps["on"])
g = src["grid"]
area = SIM.geometry(g)["area"]
oa = on["budget"]["ocean_area"]
k_e = ts[int(np.searchsorted(ts, e))]
k_j = ts[int(np.searchsorted(ts, e + 15.0))]
print(f"{sys.argv[1].split('/')[-1]} {' '.join(sys.argv[2:])}: ending {e}, frames {k_e} / {k_j}")
for k in (k_e, k_j):
    a, b = snaps["on"][k], snaps["off"][k]
    ex = (np.where(a["gr"], a["H"], 0) - np.where(b["gr"], b["H"], 0)) * area * 0.917 / oa  # m sl (crude)
    land_a = a["surf"] > 0
    cls = {
        "land, on smb>0": a["gr"] & (a["bed"] >= a["sl"]) & (a["smb"] > 0),
        "land, on smb<=0": a["gr"] & (a["bed"] >= a["sl"]) & (a["smb"] <= 0),
        "marine grounded": a["gr"] & (a["bed"] < a["sl"]),
        "not grounded on": ~a["gr"],
    }
    print(f" t={k}: dTg {a['dTg']:+.2f}; extra (m sl) total {ex.sum():.1f}, positive {ex[ex > 0].sum():.1f}")
    for nm, m in cls.items():
        mm = m & (ex > 0)
        w = ex * mm
        if w.sum() <= 0:
            continue
        lat = (np.abs(g.lat) * w).sum() / w.sum()
        print(f"   {nm:18s}: {w.sum():6.1f} m  |lat| {lat:4.1f}  surf on {(a['surf'] * w).sum() / w.sum():5.0f} m"
              f" off {(b['surf'] * w).sum() / w.sum():5.0f}  H on {(a['H'] * w).sum() / w.sum():5.0f} off "
              f"{(b['H'] * w).sum() / w.sum():5.0f}  smb on {(a['smb'] * w).sum() / w.sum():+.3f} off "
              f"{(b['smb'] * w).sum() / w.sum():+.3f} m/yr  t_warm on {(a['t_warm'] * w).sum() / w.sum():+5.1f} off "
              f"{(b['t_warm'] * w).sum() / w.sum():+5.1f}  bed dep on {(a['dep'] * w).sum() / w.sum():5.0f} off "
              f"{(b['dep'] * w).sum() / w.sum():5.0f}  off iced {((b['H'] > 1) * w).sum() / w.sum():.2f}")
    # the marine ice: how much of it faces the sea (calves), behind a shelf, or lies inland of other ice
    from planet.timezoom.ice import shelf_cover
    p = Z.TZParams(index="on", glacial_dt=6.0, **kw)
    for nm, s in (("on", a), ("off", b)):
        H, bed, sl = s["H"], s["bed"], s["sl"]
        depth = sl - bed
        fl = (H > 0) & ~s["gr"]
        mar = s["gr"] & (depth > 0)
        sea = (depth > 0) & ~s["gr"]
        nb = np.add.reduceat(sea[g.nbr_idx], g.nbr_off[:-1]) > 0
        fr = mar & nb
        cov = shelf_cover(g, fr, sea, np.where(sea, H, 0.0), p)
        v = lambda m: (H * area * m).sum() * 0.917 / oa
        print(f"   {nm} marine ice {v(mar):6.1f} m: at fronts {v(fr):5.1f} (cells {fr.sum()}, depth "
              f"{(depth * fr).sum() / max(fr.sum(), 1):4.0f} m, shelf-covered share {(cov * fr).sum() / max(fr.sum(), 1):.2f}),"
              f" inland {v(mar & ~nb):5.1f}; floating {v(fl):5.1f}; land-ice cells beside sea "
              f"{(s['gr'] & (depth <= 0) & nb).sum()}")
# the on run's mean smb on its ice over the ending, and its ELA proxy
for k in ts:
    if e - 10 <= k <= e + 20 and int(k) % 4 == 0:
        a = snaps["on"][k]
        ice = a["gr"] & (a["H"] > 1) & (a["bed"] >= a["sl"])
        neg = ice & (a["smb"] < 0)
        print(f"  t={k:5.1f} dTg {a['dTg']:+.2f}: land ice cells {ice.sum()}, smb<0 share {neg.sum() / max(ice.sum(), 1):.2f},"
              f" mean smb {(a['smb'] * area)[ice].sum() / area[ice].sum():+.3f} m/yr, sl {a['sl']:.1f}")
