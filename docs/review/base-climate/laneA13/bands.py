"""Zonal-band SST budget, Earth L6: per hemisphere and band, ocean cells: model annual sea air (temp) vs NCEP,
split near land (land share within 600 km > 0.15) / open; and the SST's parts: t_eq, gyre+upwelling anomaly, moc heat.
usage: bands.py 'k=v,...'"""
import sys, os
WT = os.environ.get("WT", "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a759d4eade75b5dcd"); sys.path.insert(0, WT)
import numpy as np
from planet import climate, vegetation
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas
grid = build_grid(int(os.environ.get("LV", "6"))); d = earth_data.earth_on_grid(grid); w = cell_areas(grid)
lat, lon = grid.lat, grid.lon; land = earth_data.land_of(d)
cap = {}
orig = climate.sea_surface
def spy(*a, **kw):
    r = orig(*a, **kw)
    if kw.get("share") is None and a[0].n == grid.n:
        cap["raw0"] = r[0]; cap["t_eq"] = a[2]
    return r
climate.sea_surface = spy
_osh = climate._sea_half
def _spy_sh(lat_, *a):
    r = _osh(lat_, *a)
    if len(lat_) == grid.n: cap["sea_half"] = r
    return r
climate._sea_half = _spy_sh
arg = sys.argv[1] if len(sys.argv) > 1 else ""
tune = {k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))}
climate.TUNE.update(tune)
c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
sea = ~land & np.isfinite(d["obs_temp"])
ls = climate.smooth(grid, land.astype(float), 600.0)
near = sea & (ls > 0.15)
def wm(f, m): return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12)) if m.any() else float("nan")
gy = cap["raw0"] - cap["t_eq"]
SH = cap["sea_half"]
T, O = c["temp"], d["obs_temp"]
print(f"{'band':>9} | all: mod obs bias | near: mod obs bias | open bias | t_eq gyre  moc  sst | near: gyre moc | warm near: mod obs bias")
for h in (1, -1):
    for a0 in (range(75, 15, -5) if h > 0 else range(-15, -75, -5)):
        lo, hi = a0 - 5, a0
        m = sea & (lat >= lo) & (lat < hi)
        mn, mo = m & near, m & ~near
        print(f"{lo:>4}..{hi:<4} | {wm(T, m):5.1f}{wm(O, m):5.1f}{wm(T, m) - wm(O, m):+5.1f}  |"
              f" {wm(T, mn):5.1f}{wm(O, mn):5.1f}{wm(T, mn) - wm(O, mn):+5.1f}   | {wm(T, mo) - wm(O, mo):+5.1f}    |"
              f" {wm(cap['t_eq'], m):5.1f}{wm(gy, m):+5.1f}{wm(c['moc_heat'], m):+5.1f}{wm(c['sst'], m):5.1f} |"
              f" {wm(gy, mn):+5.1f}{wm(c['moc_heat'], mn):+5.1f}  |"
              f" {wm(c['t_warm'], mn):5.1f}{wm(d['obs_t_warm'], mn):5.1f}{wm(c['t_warm'], mn) - wm(d['obs_t_warm'], mn):+5.1f}  n={mn.sum()}/{m.sum()}")
B = {"NE Atl 45-55N": (45, 55, -25, -6), "Bay Biscay-N Sea": (43, 58, -6, 8), "Norw Sea 60-70": (60, 70, -5, 15),
     "Baltic": (54, 66, 12, 30), "G Alaska": (52, 60, -160, -135), "NE Pac 40-50": (40, 50, -150, -125),
     "W Atl 35-45N": (35, 45, -72, -55), "Labrador Sea": (52, 62, -60, -45), "Okhotsk": (45, 60, 140, 160),
     "S Atl off Pat": (-52, -40, -64, -56), "Tasman": (-45, -35, 150, 165), "SE Pac off Chile": (-52, -38, -85, -76),
     "Agulhas": (-40, -30, 15, 35), "S Indian 40-50": (-50, -40, 40, 100), "Barents": (70, 78, 20, 55), "Barents mouth": (70, 74, 15, 30)}
print("box: t_eq gyre moc sst | air mod obs bias | Tw mod obs bias | half mod obs | Tc mod obs | sea_half")
for k, (a0, a1, l0, l1) in B.items():
    m = sea & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
    print(f"{k:>17}: {wm(cap['t_eq'], m):5.1f}{wm(gy, m):+5.1f}{wm(c['moc_heat'], m):+5.1f}{wm(c['sst'], m):5.1f} |"
          f" {wm(T, m):5.1f}{wm(O, m):5.1f}{wm(T - O, m):+5.1f} | {wm(c['t_warm'], m):5.1f}{wm(d['obs_t_warm'], m):5.1f}{wm(c['t_warm'] - d['obs_t_warm'], m):+5.1f} | {wm(c['t_warm'] - c['t_cold'], m) / 2:5.1f}{wm(d['obs_t_warm'] - d['obs_t_cold'], m) / 2:5.1f} | {wm(c['t_cold'], m):5.1f}{wm(d['obs_t_cold'], m):5.1f} | {wm(SH, m):4.1f}")
print("global ocean mean: model temp", round(wm(T, sea), 2), "obs", round(wm(O, sea), 2),
      "| NH", round(wm(T, sea & (lat > 0)) - wm(O, sea & (lat > 0)), 2), "SH", round(wm(T, sea & (lat < 0)) - wm(O, sea & (lat < 0)), 2))
