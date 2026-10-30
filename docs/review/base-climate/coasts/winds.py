"""usage: winds.py [k=v ...] -> the rain's wind (east, north; m/s) and the vapour (PW mm, q/qs) by box and half-year on
Earth L6, with the wind's parts: the zonal belts (wind()) and the land-sea part (monsoon_wind - wind). Harness only."""
import sys
from pathlib import Path
W = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, W)
import planet  # noqa
import numpy as np
from planet import climate
for kv in sys.argv[1:]:
    k, v = kv.split("=")
    climate.TUNE[k] = float(v)
from tools import earth_check as E, earth_data, moisture_budget as MB
from tools.earth_data import cell_areas
grid, d, c, _, rec = E.run(6)
G = climate._geom(grid)
lat, lon = grid.lat, grid.lon
lonw = (lon + 180) % 360 - 180
w = cell_areas(grid)
land = earth_data.land_of(d)
P1 = MB.probe(rec, np.zeros(grid.n, np.int64), 1)
q_b = P1["q_before"]
BOX = {"SE USA": (30, 37, -95, -77, "land"), "Gulf of Mexico": (22, 29, -96, -82, "sea"),
       "W Atlantic 30-37N": (30, 37, -77, -65, "sea"), "Japan": (32, 42, 130, 142, "land"),
       "Sea of Japan": (36, 44, 131, 140, "sea"), "Kuroshio 25-32N": (25, 32, 125, 140, "sea"),
       "Pampas": (-38, -30, -65, -58, "land"), "S Atlantic 30-38S": (-38, -30, -55, -45, "sea"),
       "S Brazil/Paraguay": (-30, -20, -62, -50, "land"),
       "E Australia": (-35, -25, 148, 154, "land"), "Tasman 25-35S": (-35, -25, 155, 165, "sea"),
       "SE China": (22, 32, 105, 122, "land"), "NE USA": (38, 45, -85, -72, "land"),
       "Mediterranean": (35, 42, -5, 25, "land"), "India": (10, 28, 72, 88, "land")}
pw = MB.mm_scale  # noqa
fit = ~land & (np.abs(lat) < 60)
obs = MB.observations(grid)
qcol = q_b.mean(0)
ok = fit & np.isfinite(obs["pw"])
k_pw = float((qcol[ok] * obs["pw"][ok] * w[ok]).sum() / (qcol[ok] ** 2 * w[ok]).sum())
NC = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l26/dl/"


def obs_wind(level_hpa):
    """NCEP 1991-2020 half-year mean wind (u east, v north; m/s) at a pressure level, nearest 2.5 deg point."""
    out = []
    zu, zv = np.load(NC + "uwnd_ltm.npz"), np.load(NC + "vwnd_ltm.npz")
    li = int(np.where(zu["level"] == level_hpa)[0][0])
    ia = np.clip(np.round((90 - lat) / 2.5).astype(int), 0, 72)
    io = np.round((lon % 360) / 2.5).astype(int) % 144
    for months in ((3, 4, 5, 6, 7, 8), (9, 10, 11, 0, 1, 2)):
        u = zu["val"][list(months), li].mean(0)[ia, io]
        v = zv["val"][list(months), li].mean(0)[ia, io]
        out.append((u, v))
    return out


O850, O925 = obs_wind(850), obs_wind(925)
print(f"{'box':>20} {'half':>4} {'u_e':>5} {'u_n':>5} | {'850u':>5} {'850v':>5} | {'925u':>5} {'925v':>5} | "
      f"{'PW':>5} {'obs':>5} {'q/qs':>5}")
for nm, (a0, a1, o0, o1, kind) in BOX.items():
    m = (lat >= a0) & (lat < a1) & (lonw >= o0) & (lonw < o1) & (land if kind == "land" else ~land)
    for k, half in enumerate(("jul", "jan")):
        v = rec["s_in"][k]["v"] * climate.U_REF
        ue = (v * G["east"]).sum(1); un = (v * G["north"]).sum(1)
        f = lambda x: E.wmean(x, w, m)  # noqa: E731
        po = obs["pw_jul"] if k == 0 else obs["pw_jan"]
        print(f"{nm:>20} {half:>4} {f(ue):5.1f} {f(un):5.1f} | {f(O850[k][0]):5.1f} {f(O850[k][1]):5.1f} | "
              f"{f(O925[k][0]):5.1f} {f(O925[k][1]):5.1f} | {f(q_b[k] * k_pw):5.1f} {f(np.nan_to_num(po)):5.1f} "
              f"{f(q_b[k] / rec['s_in'][k]['qs']):5.2f}")
