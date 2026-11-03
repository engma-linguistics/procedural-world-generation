"""Lane 142 (PW-1381): fetch an observed SST climatology to compare the model's sea with (scratch only, never
data/earth). NOAA OISST v2 (Reynolds et al. 2002), 1 deg, 1991-2020 long-term monthly means, NOAA PSL OPeNDAP.
Usage: get_sst.py OUT.npz"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import numpy as np
from tools import earth_data as ed

URL = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2/sst.mon.ltm.1991-2020.nc"
raw = ed._get(URL + ".dods?sst[0:1:11][0:1:179][0:1:359]", timeout=300)
arrs = ed.parse_dods(raw)
print([(n, a.shape) for n, a in arrs])
d = dict(arrs)
v = arrs[0][1].astype(float)
v[(v < -5) | (v > 45)] = np.nan
np.savez(sys.argv[1], val=v, lat=d["lat"], lon=d["lon"])
print(np.nanmin(v), np.nanmax(v), d["lat"][:2], d["lon"][:2])
