"""Earth L6 sea boxes: summer/winter wind speed (m/s, model), summer sunshine half-amplitude Q, sea_half,
Monin-Obukhov depth u*^3/(kappa B), and model/NCEP half-swing.  usage: wind.py 'k=v,...'"""
import sys, os
WT = os.environ.get("WT", "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a9ddfdb109da6508a"); sys.path.insert(0, WT)
import numpy as np
from planet import climate, vegetation
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas
grid = build_grid(int(os.environ.get("LV", "6"))); d = earth_data.earth_on_grid(grid); w = cell_areas(grid)
lat, lon = grid.lat, grid.lon; land = earth_data.land_of(d)
cap = {}
_oa = climate._air_temps
def spy_air(*a, **kw):
    if kw["grid"].n == grid.n:
        cap["v_sum"] = kw["v_sum"]; cap["v_win"] = kw["v_win"]; cap["sea_half"] = kw["sea_half"]
        cap["half_w"] = kw.get("half_w")
    return _oa(*a, **kw)
climate._air_temps = spy_air
_ost = climate.storm_track
cap["tr"] = []
def spy_tr(g, *a, **kw):
    r = _ost(g, *a, **kw)
    if g.n == grid.n: cap["tr"].append(r)
    return r
climate.storm_track = spy_tr
arg = sys.argv[1] if len(sys.argv) > 1 else ""
climate.TUNE.update({k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))})
c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
sea = ~land & np.isfinite(d["obs_temp"])
U = climate.U_REF
us, uw = climate.speed(cap["v_sum"]) * U, climate.speed(cap["v_win"]) * U
ra = climate.insolation(lat, 23.4) * (1e6 / 86400.0)
Q = (1 - climate.SEA_ALBEDO) * climate.SUN_SURFACE * 0.5 * (ra.max(0) - ra.min(0))
def mo(u):
    tau = 1.2 * 1.3e-3 * u ** 2; ust = np.sqrt(tau / 1025.0)
    Bf = 9.81 * 2e-4 * Q / climate.RHO_C_SEA
    return ust ** 3 / (0.4 * np.maximum(Bf, 1e-12))
def wm(f, m): return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12)) if m.any() else float("nan")
B = {"NE Atl 45-55N": (45, 55, -25, -6), "Bay Biscay-N Sea": (43, 58, -6, 8), "Norw Sea 60-70": (60, 70, -5, 15),
     "Baltic": (54, 66, 12, 30), "G Alaska": (52, 60, -160, -135), "NE Pac 40-50": (40, 50, -150, -125),
     "W Atl 35-45N": (35, 45, -72, -55), "Labrador Sea": (52, 62, -60, -45), "Okhotsk": (45, 60, 140, 160),
     "NW Pac 35-45": (35, 45, 145, 175), "Med": (35, 43, 0, 30),
     "S Atl off Pat": (-52, -40, -64, -56), "Tasman": (-45, -35, 150, 165), "SE Pac off Chile": (-52, -38, -85, -76),
     "Agulhas": (-40, -30, 15, 35), "S Indian 40-50": (-50, -40, 40, 100), "S Ocean 50-60": (-60, -50, -180, 180),
     "S Pac 30-40 open": (-40, -30, -140, -100), "N Pac 30-40 open": (30, 40, -170, -140), "trop Pac": (-10, 10, -170, -100)}
print("box: Usum Uwin(m/s) | track sum win | Q W/m2 | MO_sum m | sea_half | half mod obs | Tw mod obs | Tc mod obs")
mo_s = mo(us)
north = lat >= 0
trs = np.where(north, cap["tr"][0], cap["tr"][1]); trw = np.where(north, cap["tr"][1], cap["tr"][0])
print("storm track calls:", len(cap["tr"]))
for k, (a0, a1, l0, l1) in B.items():
    m = sea & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
    print(f"{k:>17}: {wm(us, m):4.1f} {wm(uw, m):4.1f} | {wm(trs, m):4.2f} {wm(trw, m):4.2f} | {wm(Q, m):5.0f} | {wm(mo_s, m):6.1f} |"
          f" {wm(cap['sea_half'], m):4.1f} | {wm(c['t_warm'] - c['t_cold'], m) / 2:4.1f} {wm(d['obs_t_warm'] - d['obs_t_cold'], m) / 2:4.1f} |"
          f" {wm(c['t_warm'], m):5.1f}{wm(d['obs_t_warm'], m):5.1f} | {wm(c['t_cold'], m):5.1f}{wm(d['obs_t_cold'], m):5.1f} | sst {wm(c['sst'], m):5.1f} Tw-sst {wm(c['t_warm'] - c['sst'], m):+4.1f} sst-Tc {wm(c['sst'] - c['t_cold'], m):+4.1f} obsmid {wm(d['obs_t_warm'] + d['obs_t_cold'], m) / 2:5.1f}")
tn = climate.TUNE; sh = tn["hk"] * tn["belt_shift"] * 23.4 / 23.4
zb = np.where(north, climate.speed(climate.wind(grid, sh)), climate.speed(climate.wind(grid, -sh))) * U
print("belts-only summer speed (no land-sea part, no front): " + " ".join(
    f"{k} {wm(zb, sea & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)):.1f}" for k, (a0, a1, l0, l1) in B.items()))
if os.environ.get("DUMP"):
    np.savez(os.environ["DUMP"], us=us, uw=uw, trs=trs, trw=trw, Q=Q, sst=c["sst"], sea_half=cap["sea_half"],
             tw=c["t_warm"], tc=c["t_cold"], otw=d["obs_t_warm"], otc=d["obs_t_cold"], sea=sea, lat=lat, lon=lon, w=w,
             half_w=cap["half_w"] if cap["half_w"] is not None else cap["sea_half"], land=land)
print("band (sea): Usum Uwin | MO_sum | sea_half | half mod obs | Tw bias Tc bias")
for a0 in range(-70, 75, 10):
    m = sea & (lat >= a0) & (lat < a0 + 10)
    print(f"{a0:>4}..{a0+10:<4}: {wm(us, m):4.1f} {wm(uw, m):4.1f} | {wm(trs, m):4.2f} {wm(trw, m):4.2f} | {wm(mo_s, m):6.1f} | {wm(cap['sea_half'], m):4.1f} |"
          f" {wm(c['t_warm'] - c['t_cold'], m) / 2:4.1f} {wm(d['obs_t_warm'] - d['obs_t_cold'], m) / 2:4.1f} |"
          f" {wm(c['t_warm'] - d['obs_t_warm'], m):+5.1f} {wm(c['t_cold'] - d['obs_t_cold'], m):+5.1f}")
