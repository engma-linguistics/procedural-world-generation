"""Lane 131: Earth L7 screen for round 2 (PW-1347 Congo low cloud, PW-1348 summer subtropical sunshine, PW-1335 cool
coldest month of warm semi-arid land). Lane 126's screen.py measures plus the coldest month by band, the winter
decomposition and the candidates' code hooks (--cand, applied by monkeypatch; the same code is in round2.patch).

    PYTHONPATH=. uv run python docs/review/base-climate/tropical-cloud/screen2.py [--cand NAME] [--tune k=v,...]
        [--recall "k=v,..;k=v"] [--save F]

Runs vegetation.coupled_climate on the worktree's private data/earth copy (data/earth itself is only read).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, vegetation  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools import earth_data  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--tune", default="")
ap.add_argument("--cand", default="", help="comma list of candidate hooks (see CANDS)")
ap.add_argument("--recall", default="")
ap.add_argument("--save", default="")
A = ap.parse_args()
for kv in A.tune.split(","):
    if kv:
        k, v = kv.split("=")
        assert k in climate.TUNE, k
        climate.TUNE[k] = tuple(float(x) for x in v.split(":")) if ":" in v else float(v)
        print("TUNE", k, "=", climate.TUNE[k], flush=True)

# ---------------------------------------------------------------- candidate hooks
_gate0 = climate._layer_gate


def gate_floor(f):
    """PW-1348/1347 a: keep a share f of the layer cloud in unstable air (lane 126's untried floor)."""
    def g(si, tune):
        x = _gate0(si, tune)
        return f + (1 - f) * x if not np.isscalar(x) else x
    climate._layer_gate = g


def gate_rhfloor(f, rh0):
    """PW-1347 b: a floor only in near-saturated air (rh above rh0, full at 1): the humid tropics' air mass."""
    def g(si, tune, q=None):
        return _gate0(si, tune)
    climate._layer_gate = g
    _clouds0 = climate.clouds

    def clouds(grid, elev, seasons_in, vap, p_mm, tune, ocean=None):
        sis = []
        for si, q in zip(seasons_in, vap):
            rh = np.clip(q / np.maximum(si["qs"], 1e-12), 0, 1)
            si = dict(si)
            si["_rhfloor"] = f * np.clip((rh - rh0) / (1 - rh0), 0, 1)
            sis.append(si)
        return _clouds0(grid, elev, sis, vap, p_mm, tune, ocean)

    def g2(si, tune):
        x = _gate0(si, tune)
        fl = si.get("_rhfloor", 0.0)
        return fl + (1 - fl) * x
    climate._layer_gate = g2
    climate.clouds = clouds


CANDS = {}
for f in (0.2, 0.3, 0.4):
    CANDS[f"floor{int(f * 100)}"] = (lambda f=f: gate_floor(f))
for f, r in ((0.5, 0.7), (0.6, 0.75), (0.7, 0.7), (0.8, 0.7)):
    CANDS[f"rhf{int(f * 100)}_{int(r * 100)}"] = (lambda f=f, r=r: gate_rhfloor(f, r))
for c in A.cand.split(","):
    if c:
        print("CAND", c, flush=True)
        CANDS[c]()

# ---------------------------------------------------------------- spies
rec = {}
_clouds_now = climate.clouds


def spy(*a, **k):
    rec["args"] = a
    return _clouds_now(*a, **k)


climate.clouds = spy
_wa = climate._winter_air


def spy_wa(grid, ocean, sst, t_land, half_l, *a, **k):
    out = _wa(grid, ocean, sst, t_land, half_l, *a, **k)
    rec["wa"] = (t_land, half_l, out[0], a[-1] if a else k.get("lift"))
    return out


climate._winter_air = spy_wa
_alb = climate.albedo_warming


def spy_alb(*a, **k):
    out = _alb(*a, **k)
    rec["alb"] = out
    return out


climate.albedo_warming = spy_alb

g = build_grid(7)
d = earth_data.earth_on_grid(g)
cl = earth_data.earth_clouds(g)
elev, ice = d["elev"].astype(float), d["ice"].astype(float)
c, _ = vegetation.coupled_climate(g, elev, 0.0, 23.4, ice)
lat, lon, w = g.lat, g.lon, earth_data.cell_areas(g)
land = earth_data.land_of(d) & (ice <= 0)
dh = climate.day_hours(lat, 23.4)
m_sun = 0.5 * (c["sun_jul"] / np.maximum(dh[0], 1e-6) + c["sun_jan"] / np.maximum(dh[1], 1e-6))
m_sky = 0.5 * (c["cloud_jul"] + c["cloud_jan"])
m_sh = 0.5 * (c["shade_jul"] + c["shade_jan"])
o_sun = 0.5 * (cl["obs_sun_jul"] + cl["obs_sun_jan"])
o_sh = 0.5 * (climate.shade(cl["obs_sun_jul"]) + climate.shade(cl["obs_sun_jan"]))
P, oP, oT = c["precip"], d["obs_precip"], d["obs_temp"]
nth = lat >= 0


def wm(x, m):
    m = m & np.isfinite(x)
    return float((x * w)[m].sum() / w[m].sum()) if m.sum() else float("nan")


def box(a, b, lo, hi):
    return (lat >= a) & (lat <= b) & (lon >= lo) & (lon <= hi)


warm = land & (oT > 18) & (np.abs(lat) < 35)
BANDS = ((400, 900), (900, 1500), (1500, 6000))
print("\n== warm land, same cells: sky / sun / shade  model | obs(CRU) ;  Tc / MAT / Tw model | NCEP")
for p0, p1 in BANDS:
    m = warm & (P >= p0) & (P < p1) & (oP >= p0) & (oP < p1)
    print(f"  {p0}-{p1}: n={int(m.sum()):5d}  {wm(m_sky, m):.2f}/{wm(m_sun, m):.2f}/{wm(m_sh, m):.2f}"
          f"  | {wm(o_sun, m):.2f}/{wm(o_sh, m):.2f} ;  {wm(c['t_cold'], m):5.1f}/{wm(c['temp'], m):5.1f}/"
          f"{wm(c['t_warm'], m):5.1f} | {wm(d['obs_t_cold'], m):5.1f}/{wm(oT, m):5.1f}/{wm(d['obs_t_warm'], m):5.1f}")

print("\n== land cloud regions: sky % (target), jul/jan, sun model / CRU")
from tools.earth_check import CLOUD_REGIONS  # noqa: E402
regs = [r for r in CLOUD_REGIONS if r[5] == "land"] + [("Pacific NW", 42, 50, -125, -120, "land", (60, 75))]
for name, a, b, lo, hi, surf, tgt in regs:
    m = land & box(a, b, lo, hi)
    print(f"  {name:20} sky {100 * wm(m_sky, m):5.1f} ({tgt[0]}-{tgt[1]})  jul {100 * wm(c['cloud_jul'], m):4.0f}"
          f" jan {100 * wm(c['cloud_jan'], m):4.0f}  sun {wm(m_sun, m):.2f} / {wm(o_sun, m):.2f}")

print("\n== warmest / coldest month vs NCEP (ice-free land north of 60S)")
tw, otw, tc, otc = c["t_warm"], d["obs_t_warm"], c["t_cold"], d["obs_t_cold"]
L = land & (lat > -60)
for a, b in ((0, 20), (20, 40), (40, 60)):
    m = L & (np.abs(lat) >= a) & (np.abs(lat) < b)
    print(f"  {a}-{b}: warm {wm(tw, m):5.1f} vs {wm(otw, m):5.1f} ({wm(tw - otw, m):+.1f})   cold {wm(tc, m):5.1f} vs "
          f"{wm(otc, m):5.1f} ({wm(tc - otc, m):+.1f})")
m_ss = np.where(nth, c["sun_jul"] / np.maximum(dh[0], 1e-6), c["sun_jan"] / np.maximum(dh[1], 1e-6))
o_ss = np.where(nth, cl["obs_sun_jul"], cl["obs_sun_jan"])
m_ws = np.where(nth, c["sun_jan"] / np.maximum(dh[1], 1e-6), c["sun_jul"] / np.maximum(dh[0], 1e-6))
o_ws = np.where(nth, cl["obs_sun_jan"], cl["obs_sun_jul"])
for a_, b_ in ((0, 10), (10, 20), (20, 40), (40, 60), (20, 60)):
    m = L & (np.abs(lat) >= a_) & (np.abs(lat) < b_)
    print(f"  sunshine share {a_}-{b_}: summer model {wm(m_ss, m):.3f} CRU {wm(o_ss, m):.3f}   winter model "
          f"{wm(m_ws, m):.3f} CRU {wm(o_ws, m):.3f}")
for thr in (30, 35):
    print(f"  land >= {thr} C: {100 * wm((tw >= thr).astype(float), L):.1f}%  NCEP {100 * wm((otw >= thr).astype(float), L):.1f}%")
REG = [("Sahara", 18, 30, -10, 30), ("Arabia", 17, 28, 40, 55), ("India", 10, 28, 72, 88),
       ("US Southwest", 31, 37, -115, -105), ("Mexico N", 24, 31, -110, -100), ("Sahel", 10, 16, -15, 30),
       ("W Africa coast", 4, 9, -10, 5), ("SE USA", 29, 36, -92, -78), ("Pacific NW", 42, 50, -125, -120),
       ("W Europe", 43, 55, -5, 15), ("Siberia", 55, 70, 65, 140), ("Amazon", -10, 2, -70, -50),
       ("Congo", -5, 5, 12, 30), ("S Africa sav", -25, -10, 15, 35), ("N Australia", -20, -11, 125, 145),
       ("E China", 25, 35, 105, 120)]
print("  region warm month model / NCEP (bias)  cold month model / NCEP (bias)  summer sun / CRU  rain / GPCC")
for name, a, b, lo, hi in REG:
    m = L & box(a, b, lo, hi)
    print(f"  {name:15} {wm(tw, m):5.1f} / {wm(otw, m):5.1f} ({wm(tw - otw, m):+.1f})  {wm(tc, m):5.1f} / "
          f"{wm(otc, m):5.1f} ({wm(tc - otc, m):+.1f})  {wm(m_ss, m):.2f} / {wm(o_ss, m):.2f}  {wm(P, m):5.0f} / "
          f"{wm(oP, m):5.0f}")

# ---- winter decomposition (PW-1335): land left to itself vs the carried air vs albedo; rain error regression
t_land, half_l, tcold_sl, lift = rec["wa"]
t_lw = t_land - half_l - lift  # land left to itself, at the ground
d_win = np.where(nth, rec["alb"][1], rec["alb"][0]) if "alb" in rec else np.zeros(g.n)
print("\n== coldest month decomposition, warm semi-arid same cells and regions: land-left-to-itself (t_land-half_l) |"
      " carried air at ground | albedo d_win | final Tc | NCEP Tc")
semi = warm & (P >= 400) & (P < 900) & (oP >= 400) & (oP < 900)
for name, m in [("warm 400-900 same", semi), ("warm 900-1500 same", warm & (P >= 900) & (P < 1500) & (oP >= 900)
                                                                         & (oP < 1500))] + \
        [(nm, L & box(a, b, lo, hi)) for nm, a, b, lo, hi in REG if nm in ("Sahel", "S Africa sav", "India",
                                                                            "N Australia", "Sahara", "Mexico N")]:
    print(f"  {name:20} {wm(t_lw, m):5.1f} | {wm(tcold_sl - lift, m):5.1f} | {wm(d_win, m):+5.2f} | {wm(tc, m):5.1f}"
          f" | {wm(otc, m):5.1f}   half_l {wm(half_l, m):4.1f}  MAT {wm(c['temp'], m):5.1f}/{wm(oT, m):5.1f}")
wsa = warm & (oP >= 250) & (oP < 1500)
x = np.log(np.maximum(P, 50) / np.maximum(oP, 50))
y = tc - otc
mm = wsa & np.isfinite(x) & np.isfinite(y)
A_ = np.vstack([x[mm], np.ones(mm.sum())]).T
coef = np.linalg.lstsq(A_ * np.sqrt(w[mm])[:, None], y[mm] * np.sqrt(w[mm]), rcond=None)[0]
r = np.corrcoef(x[mm], y[mm])[0, 1]
print(f"  regression, warm land obs 250-1500 mm (n={int(mm.sum())}): Tc miss = {coef[0]:+.2f} x ln(P/GPCC) "
      f"{coef[1]:+.2f}  (r {r:+.2f}); miss where |ln| < 0.3: {wm(y, mm & (np.abs(x) < 0.3)):+.2f}")
y2 = c["temp"] - oT
print(f"  annual mean miss same set {wm(y2, mm):+.2f}; where |ln| < 0.3: {wm(y2, mm & (np.abs(x) < 0.3)):+.2f};"
      f" Tw miss {wm(tw - otw, mm):+.2f}; winter sunshine model {wm(m_ws, mm):.2f} CRU {wm(o_ws, mm):.2f}")

if A.save:
    np.savez_compressed(A.save, tw=tw, tc=tc, temp=c["temp"], sky=m_sky, sun=m_sun, koppen=c["koppen"], P=P,
                        oP=oP, oT=oT, otc=otc, otw=otw, elev=elev, lat=lat, lon=lon, w=w, land=land, t_lw=t_lw,
                        m_ws=m_ws, o_ws=o_ws, m_ss=m_ss, o_ss=o_ss, aet=c["aet"], pet=c["pet"],
                        cloud_jul=c["cloud_jul"], cloud_jan=c["cloud_jan"], sun_jul=c["sun_jul"] / np.maximum(dh[0], 1e-6),
                        sun_jan=c["sun_jan"] / np.maximum(dh[1], 1e-6), osun_jul=cl["obs_sun_jul"],
                        osun_jan=cl["obs_sun_jan"], ncep_jul=cl["obs_cloud_ncep_jul"], ncep_jan=cl["obs_cloud_ncep_jan"])

if A.recall:
    a = rec["args"]
    print("\n== re-call clouds (no re-solve). shade 400-900/900-1500/>1500 same cells (obs 0.27/0.41/0.53) | summer sun"
          " 0-10,10-20,20-40,40-60 (CRU .46 .57 .67 .55) | annual sky % WEur PNW Sib Amaz Congo (60-75,-,60-70,65-80,70-80)"
          " | summer sun WEur PNW India MexN SEUSA Congo (CRU .45 .62 .49 .61 .64; Congo see regions)")
    for spec in [""] + A.recall.split(";"):
        t = dict(a[5])
        keep = (climate._layer_gate, climate.clouds)
        for kv in spec.split(","):
            if kv:
                k, v = kv.split("=")
                if k == "cand":
                    CANDS[v]()
                    continue
                t[k] = tuple(float(x) for x in v.split(":")) if ":" in v else float(v)
        fn = climate.clouds if climate.clouds is not spy else _clouds_now
        out = fn(*a[:5], t, *a[6:])
        climate._layer_gate, climate.clouds = keep
        sky = 0.5 * (out[0][0] + out[1][0])
        sh = 0.5 * (climate.shade(out[0][1]) + climate.shade(out[1][1]))
        ss = np.where(nth, out[0][1], out[1][1])
        bands = [f"{wm(sh, warm & (P >= p0) & (P < p1) & (oP >= p0) & (oP < p1)):.2f}" for p0, p1 in BANDS]
        sb = [wm(ss, L & (np.abs(lat) >= a_) & (np.abs(lat) < b_)) for a_, b_ in ((0, 10), (10, 20), (20, 40), (40, 60))]
        rs = [100 * wm(sky, land & box(*r)) for r in ((43, 55, -5, 15), (42, 50, -125, -120), (55, 70, 65, 140),
                                                       (-10, 2, -70, -50), (-5, 5, 12, 30))]
        sr = [wm(ss, land & box(*r)) for r in ((43, 55, -5, 15), (42, 50, -125, -120), (10, 28, 72, 88),
                                               (24, 31, -110, -100), (29, 36, -92, -78), (-5, 5, 12, 30))]
        print(f"  {spec or 'as run':34} {'/'.join(bands)} | " + " ".join(f"{x:.2f}" for x in sb) + " | "
              + " ".join(f"{x:3.0f}" for x in rs) + " | " + " ".join(f"{x:.2f}" for x in sr)
              + f" | Gabon-W jul sky {wm(out[0][0], land & box(-5, 2, 9, 16)):.2f} sun {wm(out[0][1], land & box(-5, 2, 9, 16)):.2f}", flush=True)

# ---- cloud components by region and half-year (re-derived from clouds()' inputs as run)
a = rec["args"]
grid_, elev_, s_in, vap, p_mm, tn = a[:6]
oc_ = a[6] if len(a) > 6 else None
print("\n== components (land, as run): lts | gate | rh | layer=cloud_rh*rh^1.5*gate | deep | cu | storm | clear |"
      " sky | sun ; CRU sun, NCEP sky")
CR = [("Congo", -5, 5, 12, 30), ("Congo S (5S-0)", -5, 0, 12, 30), ("Gabon/Congo W", -5, 2, 9, 16),
      ("Amazon", -10, 2, -70, -50), ("India", 10, 28, 72, 88), ("Mexico N", 24, 31, -110, -100),
      ("W Europe", 43, 55, -5, 15), ("SE USA", 29, 36, -92, -78), ("Sahel", 10, 16, -15, 30),
      ("S Africa sav", -25, -10, 15, 35)]
for hi, (si, q, p, tag) in enumerate(zip(s_in, vap, p_mm, ("jul", "jan"))):
    rh = np.clip(q / np.maximum(si["qs"], 1e-12), 0, 1)
    lts = si["t_ref"] - si["mse_t"]
    gt = climate._layer_gate(si, tn) * np.ones(g.n)
    p_s = climate.smooth(g, p, tn["cloud_rain_km"])
    deep = tn["cloud_deep"] * (1 - np.exp(-np.maximum(p_s - tn["cloud_deep_mm0"], 0) / tn["cloud_deep_mm"]))
    inst = si["mse_t"] + climate.LQ * q - si["mse_thr"]
    c0, c1 = tn["cloud_cu_c"]
    cu = tn["cloud_cu"] * np.clip((inst + c0) / c1, 0, 1) * np.sqrt(rh)
    storm = tn["cloud_storm"] * np.clip(si["B"], 0, 1.2) * np.clip(1 - si["sink"], 0, 1) * rh
    clear = tn["cloud_clear"] * si["sink"] * np.exp(-p / tn["cloud_clear_mm"])
    sky_ = c["cloud_jul"] if hi == 0 else c["cloud_jan"]
    sun_ = (c["sun_jul"] / np.maximum(dh[0], 1e-6)) if hi == 0 else (c["sun_jan"] / np.maximum(dh[1], 1e-6))
    osun = cl["obs_sun_jul"] if hi == 0 else cl["obs_sun_jan"]
    ncep = cl["obs_cloud_ncep_jul"] if hi == 0 else cl["obs_cloud_ncep_jan"]
    for name, a_, b_, lo, hi_ in CR:
        m = land & box(a_, b_, lo, hi_)
        print(f"  {tag} {name:15} {wm(lts, m):5.1f} | {wm(gt, m):.2f} | {wm(rh, m):.2f} | "
              f"{wm(tn['cloud_rh'] * rh ** 1.5 * gt, m):.2f} | {wm(deep, m):.2f} | {wm(cu, m):.2f} | {wm(storm, m):.2f} |"
              f" {wm(clear, m):.2f} | {wm(sky_, m):.2f} | {wm(sun_, m):.2f} ; {wm(osun, m):.2f}, {wm(ncep, m):.2f}"
              f"   inst {wm(inst, m):+5.1f}  P {wm(p, m):5.0f}")
print("\n== the sea's Sc deck and stability next to W Central Africa (sea cells): deck | t_ref - sst | sst | sink")
ocm = ~earth_data.land_of(d)
for hi, (si, q, tag) in enumerate(zip(s_in, vap, ("jul", "jan"))):
    inst = si["mse_t"] + climate.LQ * q - si["mse_thr"]
    s0, s1 = tn["cloud_sc_c"]
    deck = tn["cloud_sc"] * np.clip((-inst - s0) / s1, 0, 1) * si["sink"]
    for name, a_, b_, lo, hi_ in (("off Gabon", -5, 2, 4, 9), ("off Angola", -17, -5, 6, 12),
                                  ("Gulf of Guinea N", 0, 5, -5, 5)):
        m = ocm & box(a_, b_, lo, hi_)
        print(f"  {tag} {name:16} {wm(deck, m):.2f} | {wm(si['t_ref'] - si['t_sl'], m):+5.1f} | {wm(si['t_sl'], m):5.1f}"
              f" | {wm(si['sink'], m):.2f}")
print("  sea surface vs NCEP 2 m air over the same sea (rough: air, not water): model sst annual / sst_jul | NCEP annual / coldest")
for name, a_, b_, lo, hi_ in (("off Gabon", -5, 2, 4, 9), ("off Angola", -17, -5, 6, 12), ("Gulf of Guinea N", 0, 5, -5, 5),
                              ("E eq Atlantic", -3, 3, -15, 5)):
    m = ocm & box(a_, b_, lo, hi_)
    print(f"  {name:16} {wm(c['sst'], m):5.1f} / {wm(c['sst_jul'], m):5.1f} | {wm(oT, m):5.1f} / {wm(otc, m):5.1f}")
