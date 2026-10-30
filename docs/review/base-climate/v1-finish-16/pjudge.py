"""usage: pjudge.py OUT_ROOT ARM_A ARM_B [--rolls R ...] [--late T0 T1] [--json FILE]
-> the paired merge judge (PW-994) of two arms of paired.sh (OUT_ROOT/<ARM>_r<ROLL>_<tag>/seed*_L6.json.gz).

The merge is judged on paired continuous measures; the pass count is a check. For every draw present in both arms
(same seed-draw, same roll) it takes B - A of each measure and reports the median difference with a bootstrap 95%
interval (resampling draws, 4000 times, fixed seed) and a two-sided sign test. A measure moved when its interval
excludes 0 ("*"); a near-null change moves 15 of 36 draws' passes and the median end T by +-0.8 C (lane 24), so the
per-draw spread is large and only the paired interval says whether a shift is more than chaos.

Measures (late = the window --late, default 600-1000 Myr, on the 2 Myr steps / the climate updates):
  end T        true global mean at the run's end minus 13.8 C (pre-industrial)
  moment T     the same at the finish moment (highlights.finish_moment)
  late dT      mean dT over the late window
  late CO2     mean CO2 index (e-folds against the balance) over the late window
  land %       mean land share over the late window
  sink ref     ln of the weathering sink's reference: mean sink_raw / mean sink over the late window
  src ref      ln of the volcanic source's reference, likewise
  arid %       Koppen B share of land, late-window mean of the climate updates (diag arid_pct, PW-015)
  hot desert % BWh share of land, likewise (diag bwh_pct)
  land rain    mean rain on land, mm/yr, likewise (diag land_precip)
  trees %      tree cover of land, likewise
Add a measure: put a (name, function of the loaded record) pair in MEASURES.

The pass definition is v1-finish-16's plus frozen over (PW-1091): a good finish moment (highlights.finish_moment passes) and no
hellhouse and not frozen over (passrate4.judge; frozen over = 40%+ of the land under ice, owner 2026-10-30, PW-1091,
counted only in ice_criteria.hard_window: the star within 2 C of its final forcing and the run's last 300 Myr,
whichever is narrower, owner 2026-10-30, PW-1142; frozen spells under the dim young star are reported only).
The three ice terms (icehouse, glacial maximum, frozen over) are counted per arm. The set-level check: at >= 80%
frozen-over worlds or hellhouses in an arm, the sim is suspect. The pass table gives both / A only / B only / neither and an exact McNemar p on the discordant
draws. Use 2 rolls (72 runs for two arms); use 4 rolls only when the pass count decides the merge (README).
Harness only."""
import argparse
import io
import json
import math
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from planet import highlights as H  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

with redirect_stdout(io.StringIO()):  # (passrate4 runs on import; with no dirs it prints only empty tallies)
    _argv, sys.argv = sys.argv, [sys.argv[0]]
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v1-finish-12"))
    import passrate4 as P  # noqa: E402
    sys.argv = _argv

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--rolls", nargs="*", help="default: every roll both arms have")
ap.add_argument("--late", nargs=2, type=float, default=(600.0, 1000.0))
ap.add_argument("--json")
ap.add_argument("--level", type=int, default=6, help="the draws' grid level (paired.sh LEVEL)")
ap.add_argument("--table", action="store_true", help="print the per-draw table")
args = ap.parse_args()
T0, T1 = args.late


def _mean(rows, k):
    v = [r[k] for r in rows if r.get(k) is not None]
    return float(np.mean(v)) if v else float("nan")


def load(p):
    raw = C.load(p)
    s = C.series(raw)
    bar = P.judge(s["t"], s["sea_ice"], s["dT"], 300, 1e9, s["iced_land"], s["star"])
    steps = [r for r in raw["steps"] if r["t"] > 0]
    fm = H.finish_moment([{"t": r["t"], "stats": r} for r in steps], float(raw["params"].get("finish_window", 10.0)))
    at = next(r for r in steps if abs(r["t"] - fm["t"]) < 1e-9)
    late = [r for r in steps if T0 <= r["t"] < T1 and abs(r["t"] - round(r["t"])) < 1e-9]
    ups = [u for u in raw["updates"] if T0 <= u["t"] <= T1]
    return dict(ok=bool(bar["ok"] and fm["passes"]), frozen=bool(bar["frozen"]), frozen_any=bool(bar["frozen_any"]), gmax=bool(bar["glacial_max"]), ihouse=bool(bar["icehouse"]), hell=bool(bar["hell"]),
                steps=steps, late=late, ups=ups, at=at, fm=fm)


def _ln_ref(r, raw_k, rel_k):
    a, b = _mean(r["late"], raw_k), _mean(r["late"], rel_k)
    return math.log(a / b) if a > 0 and b > 0 else float("nan")


MEASURES = [
    ("end T", lambda r: r["steps"][-1]["true_temp_c"] - H.PREIND_T),
    ("moment T", lambda r: r["at"]["true_temp_c"] - H.PREIND_T),
    ("late dT", lambda r: _mean(r["late"], "dT")),
    ("late CO2", lambda r: _mean(r["late"], "co2")),
    ("land %", lambda r: 100 * _mean(r["late"], "land")),
    ("sink ref", lambda r: _ln_ref(r, "sink_raw", "sink")),
    ("src ref", lambda r: _ln_ref(r, "source_raw", "src")),
    ("arid %", lambda r: _mean(r["ups"], "arid_pct")),
    ("hot desert %", lambda r: _mean(r["ups"], "bwh_pct")),
    ("land rain", lambda r: _mean(r["ups"], "land_precip")),
    ("trees %", lambda r: _mean(r["ups"], "trees")),
]


def arm(name):
    out = {}
    for d in sorted(Path(args.root).glob(f"{name}_r*_*")):
        roll, tag = d.name[len(name) + 2:].split("_", 1)
        if args.rolls and roll not in args.rolls:
            continue
        for p in d.glob(f"seed*_L{args.level}.json.gz"):
            r = load(p)
            r["m"] = {k: f(r) for k, f in MEASURES}
            out[(roll, tag, p.name.split("_")[0])] = r
    return out


def sign_p(d):
    """Two-sided exact sign test on the nonzero differences."""
    d = [x for x in d if x != 0 and not math.isnan(x)]
    n, k = len(d), sum(x > 0 for x in d)
    if n == 0:
        return 1.0
    k = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def boot_ci(d, n=4000, seed=0):
    d = np.asarray([x for x in d if not math.isnan(x)])
    if len(d) < 3:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    med = np.median(d[rng.integers(0, len(d), (n, len(d)))], axis=1)
    return float(np.percentile(med, 2.5)), float(np.percentile(med, 97.5))


ra, rb = arm(args.a), arm(args.b)
keys = sorted(set(ra) & set(rb))
if not keys:
    sys.exit(f"no paired draws (A {len(ra)}, B {len(rb)})")
rolls = sorted({k[0] for k in keys})
A, B = args.a, args.b
print(f"# paired judge: {A} (A) vs {B} (B), {len(keys)} paired draws (A has {len(ra)}, B {len(rb)}), rolls "
      f"{' '.join(rolls)}, late window {T0:g}-{T1:g} Myr")

if args.table:
    print(f"\n{'roll':>6} {'tag':>6} {'seed':>11} | {'A':>4} {'endT':>5} {'arid':>5} {'land':>5} {'co2':>5} | "
          f"{'B':>4} {'endT':>5} {'arid':>5} {'land':>5} {'co2':>5}")
    for k in keys:
        f = lambda z: (f"{'PASS' if z['ok'] else 'fail':>4} {z['m']['end T']:+5.1f} {z['m']['arid %']:5.1f} "
                       f"{z['m']['land %']:5.1f} {z['m']['late CO2']:+5.2f}" + (" F" if z["frozen"] else "  ") +
                       (" H" if z["hell"] else "  "))
        print(f"{k[0]:>6} {k[1]:>6} {k[2]:>11} | {f(ra[k])} | {f(rb[k])}")

print("\n## Continuous measures (the judge): median of each arm, and of the paired B - A differences")
print(f"| measure | A median | B median | median B-A | 95% CI | B>A / B<A | sign p | moved |")
print("|---|---|---|---|---|---|---|---|")
res = {}
for name, _ in MEASURES:
    a = np.array([ra[k]["m"][name] for k in keys])
    b = np.array([rb[k]["m"][name] for k in keys])
    d = b - a
    ok = ~np.isnan(d)
    if not ok.any():
        continue
    lo, hi = boot_ci(d[ok])
    p = sign_p(list(d[ok]))
    moved = (lo > 0 or hi < 0)
    res[name] = dict(a=float(np.nanmedian(a)), b=float(np.nanmedian(b)), diff=float(np.median(d[ok])), ci=[lo, hi],
                     up=int((d[ok] > 0).sum()), down=int((d[ok] < 0).sum()), sign_p=p, moved=bool(moved))
    print(f"| {name} | {np.nanmedian(a):.3f} | {np.nanmedian(b):.3f} | {np.median(d[ok]):+.3f} | "
          f"[{lo:+.3f}, {hi:+.3f}] | {(d[ok] > 0).sum()} / {(d[ok] < 0).sum()} | {p:.3f} | {'*' if moved else ''} |")

print("\n## Pass count (the check): pass = good finish moment, no hellhouse, not frozen over")
pc = {}
for name, R in [(A, ra), (B, rb)]:
    parts = []
    for r in rolls:
        ks = [k for k in keys if k[0] == r]
        parts.append(f"r{r} {sum(R[k]['ok'] for k in ks)}/{len(ks)}")
    n_ice, n_hell = sum(R[k]["frozen"] for k in keys), sum(R[k]["hell"] for k in keys)
    n_dim = sum(R[k]["frozen_any"] and not R[k]["frozen"] for k in keys)
    n_gm, n_ih = sum(R[k]["gmax"] for k in keys), sum(R[k]["ihouse"] for k in keys)
    sus = max(n_ice, n_hell) >= 0.8 * len(keys)
    pc[name] = dict(passes=sum(R[k]["ok"] for k in keys), frozen_over=n_ice, glacial_max=n_gm, icehouse=n_ih, hellhouse=n_hell, suspect=sus)
    print(f"- {name}: {', '.join(parts)}; pooled {pc[name]['passes']}/{len(keys)}; icehouse {n_ih}, glacial maximum {n_gm}, frozen over {n_ice} (only under the dim star, reported: {n_dim}), hellhouse {n_hell}"
          + ("  << SIM SUSPECT (>= 80% frozen over or hellhouses)" if sus else ""))
both = sum(ra[k]["ok"] and rb[k]["ok"] for k in keys)
ao = sum(ra[k]["ok"] and not rb[k]["ok"] for k in keys)
bo = sum(rb[k]["ok"] and not ra[k]["ok"] for k in keys)
nd = ao + bo
mc = min(1.0, 2 * sum(math.comb(nd, i) for i in range(min(ao, bo) + 1)) / 2**nd) if nd else 1.0
print(f"- both {both}, A only {ao}, B only {bo}, neither {len(keys) - both - ao - bo}; McNemar exact p {mc:.3f} "
      f"(lane 24's null change: 7 vs 8 discordant of 36)")
if args.json:
    Path(args.json).write_text(json.dumps(dict(a=A, b=B, n=len(keys), rolls=rolls, measures=res, passes=pc,
                                               both=both, a_only=ao, b_only=bo, mcnemar_p=mc), indent=1))
