"""PW-831 scout 261: the overbank loss along a river on Earth (earth_capture.py's pickle): per cell the slope, the
equilibrium slope of its flood flow, the flood ratio, the spill's evaporation cap and the loss, from a start point
downstream. Usage: diag_ob.py PKL LAT LON [--obsrain] [--n=40] [Hy.ATTR=value ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "docs/review/wetlands/scout261"))
import numpy as np
from planet import hydrology as Hy
import earth_wet as EWt

for a in sys.argv:
    if a.startswith("Hy."):
        k, v = a[3:].split("=")
        setattr(Hy, k, eval(v))
rec = {}
orig = Hy._overbank_k


def spy(*a):
    out = orig(*a)
    rec.update(args=a, out=out)
    return out


Hy._overbank_k = spy
lat, lon = float(sys.argv[2]), float(sys.argv[3])
nn = int(next((a[4:] for a in sys.argv if a.startswith("--n=")), 40))
_, d = EWt.run(sys.argv[1], label="ob", hook=EWt.obs_rain if "--obsrain" in sys.argv else None)
g, land = d["grid"], d["land"]
down, order, src, wet, ok, shape, slope, cap, qu, k_eq, e_eq = rec["args"]
lost = rec["out"]
q = Hy.discharge(g, d["flow"])
i = int(np.argmin(np.where(land, (g.lat - lat) ** 2 + ((g.lon - lon) * np.cos(np.radians(lat))) ** 2, np.inf)))
print(f"k_eq {k_eq:.3g} e_eq {e_eq:.3f}")
for t in range(nn):
    pk = shape[:, i].max()
    qf = (q[i] + lost[i] * qu) * pk
    seq = k_eq * max(qf, 1e-9) ** e_eq
    print(f"{t:2d} {g.lat[i]:6.1f} {g.lon[i]:6.1f} Q {q[i]:7.0f} wet {int(wet[i])} S {slope[i]:.1e} Seq {seq:.1e} "
          f"peak {pk:4.2f} cap {cap[i]*qu:6.0f} lost {lost[i]*qu:6.0f} P {d['c']['precip'][i]:5.0f}")
    if down[i] < 0 or not land[down[i]]:
        break
    i = int(down[i])
