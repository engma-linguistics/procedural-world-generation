"""usage: quick.py [--level L] [k=v ...] -> lane 26's Earth summary (PW-998 / PW-026): the coasts' rain by half-year
against GPCC, Koppen B / BWh, the log-rain correlation, land rain and winter temperatures (coldest month) against
NCEP. k=v: climate.TUNE overrides. Harness only."""
import sys
from pathlib import Path
W = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, W)
import planet  # noqa
import numpy as np
from planet import climate
level = 6
args = sys.argv[1:]
if args and args[0] == "--level":
    level = int(args[1]); args = args[2:]
for kv in args:
    k, v = kv.split("=")
    climate.TUNE[k] = float(v)
from tools import earth_check as E, earth_data
from tools.earth_data import cell_areas
grid, d, c, _, rec = E.run(level)
R = E.analyse(grid, d, c)
lat, lon = grid.lat, grid.lon
w = cell_areas(grid)
land = earth_data.land_of(d)
dr = E.dryness(R)
ag = R["cell_agreement_excl_ant"]
lp = R["land_precip_excl_ant"]
print(f"{' '.join(args) or 'default'} (L{level})")
print(f"B {dr['B']['model']:.1f} ({dr['B']['kottek']:.1f})  BWh {dr['BWh']['model']:.1f} ({dr['BWh']['kottek']:.1f})  "
      f"BSh {dr['BSh']['model']:.1f} ({dr['BSh']['kottek']:.1f})")
print(f"exact {ag['exact']:.1f} group {ag['group']:.1f}  log-rain corr {R['log_rain_corr']:.3f}  "
      f"land P {lp['model']['mean']:.0f} (GPCC {lp['gpcc']['mean']:.0f})")
REG = {r[0]: r[1:] for r in E.REGIONS}
REG.update({"Scandinavia": (58, 70, 5, 30), "Quebec": (47, 58, -80, -65), "NE China": (40, 50, 120, 132)})
oj, on = d["obs_p_jul"].astype(float), d["obs_p_jan"].astype(float)
pj, pn = np.asarray(c["p_jul"]), np.asarray(c["p_jan"])
lonw = (lon + 180) % 360 - 180


def mask(a0, a1, o0, o1):
    return land & (lat >= a0) & (lat < a1) & (lonw >= o0) & (lonw < o1)


print(f"{'region':>18} {'P':>6} {'GPCC':>6} {'%':>4} | {'Pjul':>5} {'obs':>5} | {'Pjan':>5} {'obs':>5}")
for nm in ("SE USA", "Pampas", "Japan", "E Australia", "Mediterranean", "India", "Mexico N", "SE China", "SE Brazil",
           "Sahara", "Arabia", "Sahel", "Australia interior", "US Southwest", "Central Asia", "Gobi/Mongolia",
           "Great Plains", "NE USA", "W Europe", "Southern Africa", "Amazon"):
    m = mask(*REG[nm]) & np.isfinite(oj) & np.isfinite(on)
    f = lambda x: E.wmean(x, w, m)  # noqa: E731
    P, Po = f(0.5 * (pj + pn)), f(0.5 * (oj + on))
    print(f"{nm:>18} {P:6.0f} {Po:6.0f} {100*P/Po:4.0f} | {f(pj):5.0f} {f(oj):5.0f} | {f(pn):5.0f} {f(on):5.0f}")
print(f"{'region':>18} {'Tc':>6} {'obs':>6} {'Tw':>6} {'obs':>6}")
for nm in ("W Europe", "Scandinavia", "European Russia", "W Siberia", "E Siberia", "Alaska", "Quebec", "N Canada",
           "NE China", "Japan", "SE USA", "Pampas"):
    m = mask(*REG[nm])
    f = lambda x: E.wmean(np.asarray(x, float), w, m)  # noqa: E731
    print(f"{nm:>18} {f(c['t_cold']):6.1f} {f(d['obs_t_cold']):6.1f} {f(c['t_warm']):6.1f} {f(d['obs_t_warm']):6.1f}")
