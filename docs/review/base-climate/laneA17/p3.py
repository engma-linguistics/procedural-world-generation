"""Stage-3 probe, Earth L6: summer heat boxes, SH coastal range, continentality, summer rain in dry regions.
usage: p3.py 'k=v,k=v' ...   (WT=<tree> to probe another tree)"""
import sys, io, contextlib, time, os
WT = os.environ.get("WT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")))
sys.path.insert(0, WT)
from planet import climate, vegetation  # planet before numpy (BLAS caps)
import numpy as np
from planet.grid import build_grid
from tools import earth_data, earth_check, climate_bias
from tools.earth_data import cell_areas

grid = build_grid(6)
d = earth_data.earth_on_grid(grid)
w = cell_areas(grid)
lat, lon = grid.lat, grid.lon
land = earth_data.land_of(d)
bare = land & (d["ice"] <= 0) & np.isfinite(d["obs_temp"])
north = lat >= 0
HUMID = {"SE USA": (30, 37, -95, -77), "SE China": (22, 32, 108, 122), "NE USA": (38, 45, -80, -70),
         "Great Lakes": (40, 50, -95, -75), "Labrador": (52, 62, -80, -56), "HB lowlands": (50, 60, -95, -80),
         "Pampas": (-38, -30, -64, -56), "E Australia": (-35, -25, 145, 154), "W Europe": (45, 55, -5, 10),
         "E Europe": (48, 58, 25, 45)}
DRY = {"Great Plains": (35, 48, -105, -95), "Sahara": (18, 30, -10, 30), "Arabia": (18, 30, 40, 55),
       "C Asia": (40, 50, 55, 80), "Aus interior": (-30, -20, 120, 140), "Mongolia": (42, 50, 95, 115)}
SMALL = {"Patagonia": (-55, -40, -76, -65), "NZ": (-47, -34, 166, 179), "Tasmania": (-44, -40, 144, 149),
         "S Africa cape": (-35, -30, 17, 27), "Chile mid": (-40, -30, -73, -70)}
MOUNT = {"Canadian Rockies": (50, 60, -125, -114), "Tibet": (30, 36, 80, 95), "Alps": (44, 48, 5, 15),
         "Andes 20-35S": (-35, -20, -71, -66)}


def box(b):
    a0, a1, l0, l1 = b
    return bare & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)


def wm(f, m):
    return float((f[m] * w[m]).sum() / max(w[m].sum(), 1e-12))


for arg in sys.argv[1:] or [""]:
    tune = {k: float(v) for k, v in (kv.split("=") for kv in filter(None, arg.split(",")))}
    for k in tune:
        assert k in climate.TUNE, k
    old = dict(climate.TUNE); climate.TUNE.update(tune)
    t0 = time.time()
    try:
        c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
    finally:
        climate.TUNE.clear(); climate.TUNE.update(old)
    with contextlib.redirect_stdout(io.StringIO()):
        R = earth_check.analyse(grid, d, c)
    B = climate_bias.analyse(grid, d, c)
    a = R["cell_agreement_excl_ant"]
    print(f"### {arg or 'default'} ({time.time()-t0:.0f}s) logr {R['log_rain_corr']:.3f} group {a['group']:.1f} "
          f"exact {a['exact']:.1f} summer-share {R['summer_rain_share_land']['model']:.3f}", flush=True)
    psum = np.where(north, c["p_jul"], c["p_jan"])
    psum_o = np.where(north, d["obs_p_jul"], d["obs_p_jan"])
    for nm, G in (("humid", HUMID), ("dry", DRY), ("small", SMALL)):
        s = []
        for k, b in G.items():
            m = box(b)
            s.append(f"{k} {wm(c['t_warm'], m):.1f}({wm(c['t_warm'] - d['obs_t_warm'], m):+.1f})"
                     f" rng {wm(c['t_warm'] - c['t_cold'], m):.1f}/{wm(d['obs_t_warm'] - d['obs_t_cold'], m):.1f}"
                     f" Ps {wm(psum, m & np.isfinite(psum_o)):.0f}/{wm(psum_o, m & np.isfinite(psum_o)):.0f}")
        print(f"  {nm}: " + " | ".join(s))
    print("  mount Tc: " + " | ".join(f"{k} {wm(c['t_cold'], box(b)):.1f}({wm(c['t_cold'] - d['obs_t_cold'], box(b)):+.1f})"
                                      f" Tw({wm(c['t_warm'] - d['obs_t_warm'], box(b)):+.1f})" for k, b in MOUNT.items()))
    print("  contin:", [(r['hemi'], r['km'], round(r['range'], 1), round(r['range_obs'], 1), round(r['Tw_bias'], 1))
                        for r in B['continentality'] if r['cells']])
    print("  summer:", [(r['hemi'], r['mm'], round(r['Tw_bias'], 1), round(r['P_sum']), round(r['P_sum_obs']))
                        for r in B['summer'] if r['cells']])
    seab = {"NE Atl 45-55N": (45, 55, -25, -6), "Bay Biscay-N Sea": (43, 58, -6, 8), "Gulf Mex": (22, 29, -95, -82),
            "W Atl 35-45N": (35, 45, -72, -55), "S Atl off Pat": (-52, -40, -64, -56), "SE Pac off Chile": (-52, -38, -85, -76),
            "Tasman": (-45, -35, 150, 165), "E China Sea": (25, 33, 122, 130), "Labrador Sea": (52, 62, -60, -45)}
    seam = ~land & np.isfinite(d["obs_t_warm"])
    print("  sea Tw: " + " | ".join(f"{k} {wm(c['t_warm'], seam & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)):.1f}"
                                    f"({wm(c['t_warm'] - d['obs_t_warm'], seam & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)):+.1f})"
                                    for k, (a0, a1, l0, l1) in seab.items()))
    rows = {r["name"]: r for r in B["regions"]}
    print("  rows:", {k: (round(rows[k]['Tw'] - rows[k]['Tw_obs'], 1), round(rows[k]['Tc'] - rows[k]['Tc_obs'], 1))
                      for k in ("Labrador / Quebec N", "Hudson Bay lowlands", "Fennoscandia", "Great Lakes / Midwest",
                                "Canadian Rockies", "Alaska / Yukon", "Patagonia", "Keewatin / Nunavut", "Iceland")},
          flush=True)
    hs = (c["t_warm"] - c["t_cold"]) / 2; ho = (d["obs_t_warm"] - d["obs_t_cold"]) / 2
    ls = climate.smooth(grid, land.astype(float), 600.0)
    out = []
    for nm, mm in (("near", seam & (ls > 0.15)), ("open", seam & (ls <= 0.15))):
        for hn, hm in (("N", lat > 20), ("S", lat < -20)):
            m = mm & hm & (np.abs(lat) < 65)
            r = hs[m] / np.maximum(ho[m], 0.3); ok = (r <= 1.5) & (r >= 1 / 1.5)
            out.append(f"{nm}{hn} {100 * (w[m] * ok).sum() / w[m].sum():.0f}% (mean ratio {wm(hs, m) / wm(ho, m):.2f})")
    print("  sea swing within 1.5x (20-65): " + " | ".join(out))
    sb = {"NE Atl": (45, 55, -25, -6), "Norw": (60, 70, -5, 15), "NE Pac": (40, 50, -150, -125),
          "G Alaska": (52, 60, -160, -135), "N Pac 30-40": (30, 40, -170, -140), "Pat": (-52, -40, -64, -56),
          "Tasman": (-45, -35, 150, 165), "Agulhas": (-40, -30, 15, 35), "S Oc 50-60": (-60, -50, -180, 180),
          "S Pac 30-40": (-40, -30, -140, -100)}
    def bx(a0, a1, l0, l1): return seam & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
    print("  sea half-swing mod/obs: " + " | ".join(f"{k} {wm(hs, bx(*b)):.1f}/{wm(ho, bx(*b)):.1f}"
                                                   for k, b in sb.items()), flush=True)
