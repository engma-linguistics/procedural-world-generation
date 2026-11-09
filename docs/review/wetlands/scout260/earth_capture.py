"""PW-831 scout 260: build the Earth world (terrain + the model's climate) once and pickle what
hydrology.rivers_and_lakes is given (elev, the climate dict's per-cell fields, ice, outlet / closed / valley),
so the wetland checks can rerun the hydrology alone. Writes only OUT. Usage: earth_capture.py LEVEL OUT.pkl"""
import pickle
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import numpy as np  # noqa
import planet  # noqa
from planet import hydrology as Hy
import planet.world as W
from tools import earth_world as EW

lvl, out = int(sys.argv[1]), sys.argv[2]
cap = {}
orig = Hy.rivers_and_lakes


def spy(*a, **k):
    cap.setdefault("args", (a, k))
    return orig(*a, **k)


Hy.rivers_and_lakes = spy
W.hydrology.rivers_and_lakes = spy
world = EW.build(lvl)
(a, k) = cap["args"]
n = a[1].shape[0]
c = {kk: v for kk, v in a[2].items() if isinstance(v, np.ndarray) and v.ndim >= 1 and v.shape[-1] == n}
pickle.dump(dict(level=lvl, elev=a[1], c=c, ice=a[3] if len(a) > 3 else k.get("ice"), kw=dict(k)), open(out, "wb"))
print("saved", out, sorted(c), list(k))
