"""usage: tally.py DIR_ROOT LEVEL (6|7) -> lane 92's hard-bar tally over DIR_ROOT/m_r<roll>_<tag>/seed*_L<LEVEL>.json.gz
(paired.sh output). Per draw: the pass (passrate4.judge bar + finish_moment, as pjudge), and the four hard failures:
- frozen: passrate4.judge frozen (40%+ of the land under ice inside ice_criteria.hard_window); frozen_any is also shown
- boiled: passrate4.judge hell (dT median > +10.5 or max > +15.5 C)
- ocean loss (operational definition, no owner-set number exists): sea-ice-free ocean share lost, i.e. the ocean's share
  of the surface (1 - land) after 300 Myr below 40% at any step (Earth 71%; the sim has no sink for ocean water, so this
  is the only way it can show) or the mean sea level beyond +-1000 m of the start
- CO2 crash: pCO2 below 100 ppm at any step after 300 Myr (passrate4's diagnostic band is 180-600 at the end); the
  end pCO2 outside 180-600 is reported separately
Harness only; no threshold of tools/ is changed."""
import io, sys
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from planet import climate, highlights as H  # noqa
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
    ocean = 100 * (1 - np.array([r["land"] for r in late]))
    sl = np.array([r["sea_level"] for r in late])
    ups = [u for u in raw["updates"] if 50 <= u["t"] <= 1000 and "arid_pct" in u]
    d = p.parent.name.split("_")
    rows.append(dict(roll=d[1][1:], tag="_".join(d[2:]), seed=p.name.split("_")[0][4:], ok=bool(bar["ok"] and fm["passes"]),
                     bar=bool(bar["ok"]), fm=bool(fm["passes"]), frozen=bool(bar["frozen"]), frozen_any=bool(bar["frozen_any"]),
                     boiled=bool(bar["hell"]), ocean_min=float(ocean.min()), slmax=float(np.abs(sl).max()),
                     ocean_loss=bool(ocean.min() < 40 or np.abs(sl).max() > 1000), pco2_min=float(pc.min()),
                     co2_crash=bool(pc.min() < 100), pco2_end=float(pc[-1]), pco2_end_out=bool(not 180 <= pc[-1] <= 600),
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
print(f"\nL{lvl}: {n} draws")
for k, lab in [("ok", "soft pass (bar + finish moment)"), ("frozen", "HARD frozen over in window"), ("boiled", "HARD boiled/hellhouse"),
               ("ocean_loss", "HARD ocean loss"), ("co2_crash", "HARD CO2 crash (<100 ppm)"), ("frozen_any", "(frozen any time after 300, reported)"),
               ("pco2_end_out", "(end pCO2 outside 180-600, reported)"), ("icehouse", "(icehouse, reported)")]:
    print(f"  {lab}: {sum(r[k] for r in rows)}/{n}")
for roll in sorted({r['roll'] for r in rows}):
    rs = [r for r in rows if r['roll'] == roll]
    print(f"  roll {roll}: pass {sum(r['ok'] for r in rs)}/{len(rs)}, frozen {sum(r['frozen'] for r in rs)}, boiled {sum(r['boiled'] for r in rs)}")
