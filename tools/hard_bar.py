"""usage: tools/hard_bar.py DIR_ROOT LEVEL (6|7) -> lane 92's hard-bar tally over DIR_ROOT/m_r<roll>_<tag>/seed*_L<LEVEL>.json.gz
(paired.sh output). Per draw: the pass (passrate4.judge bar + finish_moment, as pjudge), and the four hard failures:
- frozen: passrate4.judge frozen (40%+ of the land under ice inside ice_criteria.hard_window); frozen_any is also shown
- boiled: passrate4.judge hell (dT median > +10.5 or max > +15.5 C)
- ocean loss (operational definition, no owner-set number exists): sea-ice-free ocean share lost, i.e. the ocean's share
  of the surface (1 - land) after 300 Myr below 40% at any step (Earth 71%; the sim has no sink for ocean water, so this
  is the only way it can show) or the mean sea level beyond +-1000 m of the start
- CO2 crash (owner ruling D32, option B): pCO2 below the plants' own compensation point at any step after 300 Myr:
  vegetation._gstar(global mean T of that step) / 0.7 (the plant code's ci = 0.7 Ca). Secondary rows: pCO2 < 100 ppm
  (lane 92's line), < 50 / < 60 ppm, and 8-fold fall in <= 50 Myr without recovery. End pCO2 outside 180-600 is reported separately
Harness only; no threshold of tools/ is changed."""
import io, sys
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from planet import climate, highlights as H, vegetation as V  # noqa
from tools import ice_criteria as C  # noqa
with redirect_stdout(io.StringIO()):
    _a, sys.argv = sys.argv, [sys.argv[0]]
    sys.path.insert(0, str(ROOT / "docs/review/base-climate/v1-finish-12"))
    import passrate4 as P  # noqa
    sys.argv = _a
root, lvl = Path(sys.argv[1]), sys.argv[2]
rows = []
for p in sorted(root.glob(f"m_r*/seed*_L{lvl}.json.gz")) + sorted(root.glob(f"m_r*_*/seed*_L{lvl}.json.gz")):
    pass
seen = set()
for p in sorted(root.glob(f"m_r*_*/seed*_L{lvl}.json.gz")):
    if p in seen: continue
    seen.add(p)
    raw = C.load(str(p)); s = C.series(raw)
    bar = P.judge(s["t"], s["sea_ice"], s["dT"], 300, 1e9, s["iced_land"], s["star"])
    steps = [r for r in raw["steps"] if r["t"] > 0]
    fm = H.finish_moment([{"t": r["t"], "stats": r} for r in steps], float(raw["params"].get("finish_window", 10.0)))
    late = [r for r in steps if r["t"] >= 300]
    pc = climate.PCO2_BALANCE * np.exp(np.array([r["co2"] for r in late]))
    tl = np.array([r["t"] for r in late]); i0 = int(pc.argmin())
    comp_t = np.array([float(V._gstar(r["true_temp_c"])) / 0.7 for r in late]); crash_b = bool((pc < comp_t).any())
    Tmin = late[i0]["true_temp_c"]; dTmin = Tmin - H.PREIND_T
    comp = float(V._gstar(Tmin)) / 0.7   # ambient pCO2 (ppm) at which C3 ci = 0.7 Ca hits G*(T): the plants' compensation point
    # 8-fold fall: some t0 and some t1 in (t0, t0+50 Myr] with pCO2(t1) <= pCO2(t0)/8, and the end value still <= pCO2(t0)/4
    ta = tl; pa = pc   # after 300 Myr only: the early spin-down from the start CO2 is not a crash
    fall8 = False; fall8s = False; worst = 1.0
    for a in range(len(ta)):
        w = (ta > ta[a]) & (ta <= ta[a] + 50)
        if w.any():
            r_ = pa[w].min() / pa[a]; worst = min(worst, r_)
            if r_ <= 1 / 8 and pa[-1] <= pa[a] / 4: fall8 = True
            if r_ <= 1 / 8 and pa[-1] <= 2 * pa[w].min(): fall8s = True   # strict: the end is still within 2x of the fall's bottom
    ocean = 100 * (1 - np.array([r["land"] for r in late]))
    sl = np.array([r["sea_level"] for r in late])
    ups = [u for u in raw["updates"] if 50 <= u["t"] <= 1000 and "arid_pct" in u]
    d = p.parent.name.split("_")
    rows.append(dict(roll=d[1][1:], tag="_".join(d[2:]), seed=p.name.split("_")[0][4:], ok=bool(bar["ok"] and fm["passes"]),
                     bar=bool(bar["ok"]), fm=bool(fm["passes"]), frozen=bool(bar["frozen"]), frozen_any=bool(bar["frozen_any"]),
                     boiled=bool(bar["hell"]), ocean_min=float(ocean.min()), slmax=float(np.abs(sl).max()),
                     ocean_loss=bool(ocean.min() < 40 or np.abs(sl).max() > 1000), pco2_min=float(pc.min()), tmin_t=float(tl[i0]), tminT=float(Tmin), tmin_dT=float(dTmin), comp=comp, below_comp=crash_b, fall8=fall8, fall8s=fall8s, worst50=worst,
                     co2_crash=crash_b, co2_100=bool(pc.min() < 100), pco2_end=float(pc[-1]), pco2_end_out=bool(not 180 <= pc[-1] <= 600),
                     endT=steps[-1]["true_temp_c"] - H.PREIND_T, peak_il=100 * max(r.get("iced_land") or 0 for r in late),
                     icehouse=bool(bar["icehouse"]), arid=float(np.median([u["arid_pct"] for u in ups])) if ups else float("nan"),
                     trees=float(np.median([u["trees"] for u in ups if u.get("trees") is not None])) if ups else float("nan"),
                     seconds=raw.get("seconds")))
print(f"{'roll':>6} {'tag':>6} {'seed':>7} {'pass':>4} {'bar':>3} {'fm':>3} {'FRZ':>3} {'frzAny':>6} {'BOIL':>4} {'OCN':>3} {'CO2x':>4} "
      f"{'oceanMin':>8} {'|sl|max':>7} {'pCO2min':>7} {'pCO2end':>7} {'endT':>5} {'pkIce':>5} {'arid':>5} {'trees':>5} {'min':>5}")
for r in sorted(rows, key=lambda r: (r['roll'], r['tag'], r['seed'])):
    yn = lambda b: "Y" if b else "-"
    print(f"{r['roll']:>6} {r['tag']:>6} {r['seed']:>7} {yn(r['ok']):>4} {yn(r['bar']):>3} {yn(r['fm']):>3} {yn(r['frozen']):>3} {yn(r['frozen_any']):>6} "
          f"{yn(r['boiled']):>4} {yn(r['ocean_loss']):>3} {yn(r['co2_crash']):>4} {r['ocean_min']:8.1f} {r['slmax']:7.0f} {r['pco2_min']:7.0f} "
          f"{r['pco2_end']:7.0f} {r['endT']:+5.1f} {r['peak_il']:5.1f} {r['arid']:5.1f} {r['trees']:5.1f} {(r['seconds'] or 0)/60:5.1f}")
n = len(rows)
print("\nmin pCO2 per draw, ascending (t at min Myr; global mean T at min C; dT vs pre-industrial; compensation point ppm = G*(T)/0.7; below it?; worst 50-Myr fall ratio; 8-fold-no-recovery):")
for r in sorted(rows, key=lambda r: r['pco2_min']):
    print(f"  {r['pco2_min']:6.1f} ppm  L{lvl} r{r['roll']} {r['tag']} {r['seed']}  t={r['tmin_t']:5.0f}  T={r['tminT']:5.1f}  dT={r['tmin_dT']:+5.1f}  comp={r['comp']:5.1f}  below_comp={'Y' if r['below_comp'] else '-'}  worst50={r['worst50']:.2f}  fall8={'Y' if r['fall8'] else '-'}  fall8strict={'Y' if r['fall8s'] else '-'}")
for lim in (50, 60, 100):
    print(f"  min pCO2 < {lim} ppm: {sum(r['pco2_min'] < lim for r in rows)}/{n}")
print(f"  CRASH (B): pCO2 below the compensation point of a step: {sum(r['below_comp'] for r in rows)}/{n}")
print(f"  falls 8-fold strict (end <= 2x fall bottom): {sum(r['fall8s'] for r in rows)}/{n}")
print(f"  falls 8-fold in <=50 Myr and end <= 1/4 of the pre-fall value: {sum(r['fall8'] for r in rows)}/{n}")
print(f"\nL{lvl}: {n} draws")
for k, lab in [("ok", "soft pass (bar + finish moment)"), ("frozen", "HARD frozen over in window"), ("boiled", "HARD boiled/hellhouse"),
               ("ocean_loss", "HARD ocean loss"), ("co2_crash", "HARD CO2 crash (below plants' compensation point)"), ("co2_100", "(secondary: CO2 under 100 ppm)"), ("fall8", "(secondary: 8-fold fall in <=50 Myr, end <= 1/4 of pre-fall)"), ("fall8s", "(secondary: 8-fold fall in <=50 Myr, end <= 2x the fall bottom)"), ("frozen_any", "(frozen any time after 300, reported)"),
               ("pco2_end_out", "(end pCO2 outside 180-600, reported)"), ("icehouse", "(icehouse, reported)")]:
    print(f"  {lab}: {sum(r[k] for r in rows)}/{n}")
for roll in sorted({r['roll'] for r in rows}):
    rs = [r for r in rows if r['roll'] == roll]
    print(f"  roll {roll}: pass {sum(r['ok'] for r in rs)}/{len(rs)}, frozen {sum(r['frozen'] for r in rs)}, boiled {sum(r['boiled'] for r in rs)}")
