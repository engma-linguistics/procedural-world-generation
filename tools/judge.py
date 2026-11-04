"""tools/judge.py -- the climate judge, one module (PW-1393): the v1 icehouse bar (was docs/review/base-climate/v1-finish-12/passrate4.py)
and the paired merge judge (was docs/review/base-climate/v1-finish-16/pjudge.py). Moved, not changed: every verdict, number
and threshold is the old scripts'. The old paths are thin shims onto this module.

Library: judge / flags / line (the bar on one draw), the finish constants, load (one paired.sh draw, as pjudge judges it), arm.
Command lines:
  uv run python tools/judge.py bar DIAG_DIR [...]          # passrate4.py's
  uv run python tools/judge.py paired OUT_ROOT ARM_A ARM_B [...]   # pjudge.py's
(each old script's docstring follows, for the rules.)

--- passrate4 ---
usage: passrate4.py DIAG_DIR [...] -- the v1 icehouse bar as ruled on PW-865 (owner, option C, 2026-10-25).

The bar, judged on 300 Myr to the run's end (and per forward window 300-1000, 1000-1500, 1500-2000 Myr):
- FAIL on frozen over (owner 2026-10-30, PW-1091, replacing the old icebox rule; owner 11-03, D47, PW-1425): the world
  ENDS frozen: 40% or more of the LAND under ice (`iced_land`, the run's saved stat) at the last climate update, so
  also a world that stays frozen to the end, and (paired judge, judge_draw) no finish-window moment passes the finish's
  land-ice check. The peak in the hard window is reported (frozen_peak), not a failure;
- FAIL on hellhole: dT median > +10.5 C or max > +15.5 C;
- never-ice (icehouse share < 5%) and the old icebox rule (icehouse >= 90% of the time or deep ice < -150 m for 30%)
  are reported, not failures (owner 2026-10-27);
- no cap on the icehouse share (the old <= 40% is gone; the share is reported only).
The three ice terms (tools/ice_criteria.py ice_terms): icehouse (permanent polar sheets), glacial maximum (land ice
>= 25%, Earth's coldest) and frozen over (>= 40%); judge / flags / line report all three.

The finish checks, per run at its end:
- true area mean temperature (the climate's mean, PW-822) within -6..+5 C of pre-industrial 13.8 C;
- interglacial land ice near Earth's ~10% of land: the least over the last 12 Myr is not none (< 1%) and not
  LGM-like (>= 25%); the share inside 5-20% is also tallied as "near Earth";
- wet equatorial lowland (> 2000 mm) trees >= 20% (PW-806, hard check);
- end pCO2 in 180-600 ppm (diagnostic).
A seed-draw "passes all" when it passes the bar and the three hard finish checks (temperature, land ice, trees).
Harness only: no thresholds of tools/ice_criteria are changed.
--- pjudge ---
usage: pjudge.py OUT_ROOT ARM_A ARM_B [--rolls R ...] [--late T0 T1] [--json FILE]
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
hellhouse and not frozen over (passrate4.judge; frozen over = the world ends frozen, 40%+ of the land under ice at the
end with no finish-window moment passing the land-ice check, owner 11-03, D47, PW-1425; the 40% line is PW-1091's.
The old rule, 40%+ at any moment of ice_criteria.hard_window, is reported as "frozen peak"; frozen spells under the dim
young star are reported only).
The three ice terms (icehouse, glacial maximum, frozen over) are counted per arm. The set-level check: at >= 80%
frozen-over worlds or hellhouses in an arm, the sim is suspect. The pass table gives both / A only / B only / neither and an exact McNemar p on the discordant
draws. Use 2 rolls (72 runs for two arms); use 4 rolls only when the pass count decides the merge (README).
Harness only."""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from planet import climate  # noqa: E402
from planet import highlights as H  # noqa: E402
from planet.highlights import HUMAN_RANGE, PREIND_T  # noqa: E402  (one definition of the finish band: -6..+5 C, owner D19, PW-1164)
from tools import ice_criteria as C  # noqa: E402

LAND_ICE_NONE, LAND_ICE_LGM = 1.0, 25.0  # % of land: none / LGM-like (Earth pre-industrial ~10, LGM ~25)
LAND_ICE_NEAR = (5.0, 20.0)  # % of land: "near Earth's ~10%" (reported)
WET_TREES = 20.0  # % trees on the wet equatorial lowland (PW-806)
PCO2_DIAG = (180.0, 600.0)  # ppm at the end (diagnostic)


def judge(t, si, dT, a, b, il=None, star=None, fin_ice=False):
    """il: the share of land under ice (0..1) on the same samples (C.series(raw)["iced_land"]). Without it the
    land terms are None and nothing is frozen over. Frozen over: the window's last sample is (the world ends frozen,
    PW-1425), unless fin_ice (a finish-window moment passes the finish's land-ice check: judge_draw). star: the
    star's forcing on them (C.series(raw)["star"]): frozen_peak (reported) is the old rule, 40%+ at any sample of
    C.hard_window (the star near its final brightness, the run's last 300 Myr at most; owner 2026-10-30); frozen_any
    (reported) any sample."""
    w = (t >= a) & (t < b)
    if not w.any():
        return None
    hard, h0, which = C.hard_window(t[w], None if star is None else star[w])
    ice = C.ice_terms(si[w], None if il is None else il[w], hard=hard)
    share, deep = ice["icehouse_pct"], ice["deep_pct"]
    med, mx = float(np.median(dT[w])), float(dT[w].max())
    hell = med > 10.5 or mx > 15.5
    frozen = bool(ice["frozen_over"]) and not fin_ice
    # owner 2026-10-30 (PW-1091): a world fails on hellhouse or on frozen over (>= 40% of the land under ice); owner
    # 11-03 (D47, PW-1425): frozen over at the end, not at the window's worst moment.
    # Never-ice and the old icebox rule (icehouse >= 90% or deep >= 30%) are reported only. The set-level check
    # (fmtally, pjudge) flags the sim as wrong if nearly all worlds are frozen over or nearly all hellhouses.
    return dict(share=share, deep=deep, med=med, mx=mx, hell=hell, never=ice["never_ice"], frozen=frozen,
                frozen_any=bool(ice["frozen_over_any"]), frozen_peak=bool(ice["frozen_peak"]), hard_from=h0, hard_by=which,
                glacial_max=bool(ice["glacial_max"]), land_ice_peak=ice["land_ice_peak"],
                icehouse=ice["icehouse"], always_icy=bool(share >= 90 or deep >= 30), ok=not hell and not frozen)


def flags(j):
    return ((" HELL" if j["hell"] else "") + (" FROZEN-OVER" if j["frozen"] else (" frozen-dim-star" if j.get("frozen_any") else "")) + (" GLACIAL-MAX" if j["glacial_max"] else "")
            + (" ICEHOUSE" if j["icehouse"] else "") + (" NEVER-ICE" if j["never"] else ""))


def line(j):
    pk = "n/a" if j["land_ice_peak"] is None else f"{j['land_ice_peak']:.0f}%"
    return (f"icehouse {j['share']:4.1f}% deep {j['deep']:4.1f}% land ice peak {pk} dT med {j['med']:+.1f} max {j['mx']:+.1f}"
            f"{flags(j)} -> {'ok' if j['ok'] else 'F'}")


def queue(d: Path, level: str, end: int) -> str:
    return f"L{level[1:]} {end / 1000:g} Gyr" if level.startswith("L") else f"{level} {end}"


def passrate_main(dirs):
    """passrate4.py DIAG_DIR [...]: the bar and finish tally, printed."""
    tally = {}
    rows = []

    def add(k, v):
        tally.setdefault(k, []).append(bool(v))

    for d in map(Path, dirs):
        for p in sorted(d.glob("seed*_L*.json.gz")):
            raw = C.load(p)
            s = C.series(raw)
            t, si, dT, il_s = s["t"], s["sea_ice"], s["dT"], s["iced_land"]
            end = float(t.max())
            steps = [r for r in raw["steps"] if r["t"] > 0]
            st = np.array([r["t"] for r in steps])
            co2 = np.array([r["co2"] for r in steps])
            sdT = np.array([r["dT"] for r in steps])
            pc = climate.PCO2_BALANCE * np.exp(co2)
            late = st >= 300
            last = raw["updates"][-1]
            q = queue(d, p.name.split("_")[1].split(".")[0], int(round(end / 100.0) * 100))
            seed = p.name.split("_")[0]
            allj = judge(t, si, dT, 300, 1e9, il_s)
            add((q, "bar 300-end"), allj["ok"])
            print(f"{d.name:>14} {seed:>11} 300-{end:.0f}: {line(allj)}")
            for a, b in [(300, 1000), (1000, 1500), (1500, 2000.1)]:
                j = judge(t, si, dT, a, b, il_s)
                if j is not None and b <= end + 1:
                    print(f"{'':>27}{a:>4}-{min(b, 2000):.0f}: {line(j)}")
                    add((q, f"bar {a}-{min(b, 2000):.0f}"), j["ok"])
            e540 = judge(t, si, dT, end - 540, 1e9, il_s)
            print(f"{'':>27}last 540 ({end - 540:.0f}-{end:.0f}, diagnostic): {line(e540)}")
            corr = float(np.corrcoef(sdT[late], co2[late])[0, 1]) if late.sum() > 3 else float("nan")
            print(f"{'':>27}pCO2 after 300: median {np.median(pc[late]):.0f} (10-90% {np.percentile(pc[late], 10):.0f}-"
                  f"{np.percentile(pc[late], 90):.0f}), <180 ppm {100 * (pc[late] < 180).mean():.0f}%, at the end "
                  f"{pc[-1]:.0f}; corr(dT, ln pCO2) {corr:+.2f}")
            rel = last["temp"] - PREIND_T
            t_ok = HUMAN_RANGE[0] <= rel <= HUMAN_RANGE[1]
            il = 100 * np.array([r["iced_land"] for r in steps if r["t"] >= end - 12 and "iced_land" in r])
            ice_end, ice_min = (float(il[-1]), float(il.min())) if len(il) else (float("nan"), float("nan"))
            ice_ok = LAND_ICE_NONE <= ice_min < LAND_ICE_LGM
            ice_near = LAND_ICE_NEAR[0] <= ice_min <= LAND_ICE_NEAR[1]
            iflag = " NO-ICE" if ice_min < LAND_ICE_NONE else (" LGM-LIKE" if ice_min >= LAND_ICE_LGM else "")
            wet = last.get("wet_eq_trees")
            tree_ok = wet is not None and wet >= WET_TREES
            co2_ok = PCO2_DIAG[0] <= pc[-1] <= PCO2_DIAG[1]
            all_ok = allj["ok"] and t_ok and ice_ok and tree_ok
            for k, v in [("finish T -6..+5", t_ok), ("finish land ice 1-25%", ice_ok), ("finish land ice 5-20%", ice_near),
                         ("finish wet-eq trees >= 20%", tree_ok), ("end pCO2 180-600 (diag.)", co2_ok),
                         ("bar + hard finish checks", all_ok)]:
                add((q, k), v)
            print(f"{'':>27}end: dT {last['dT']:+.1f}, true mean T {last['temp']:.1f} C, trees {last.get('trees')}% of land, "
                  f"wet-eq lowland trees {'none' if wet is None else f'{wet:.0f}%'} ({last.get('wet_eq_cells')} cells)")
            print(f"{'':>27}finish: true mean {rel:+.1f} C vs pre-industrial ({'inside' if t_ok else 'OUTSIDE'} -6..+5); "
                  f"land ice {ice_end:.1f}% at the end, {ice_min:.1f}% least in the last 12 Myr{iflag}; "
                  f"trees {'ok' if tree_ok else 'LOW'}; -> {'PASSES ALL' if all_ok else 'fails'}")
            rows.append((q, d.name, seed, allj, rel, ice_min, wet, pc[-1], all_ok))

    print("\nper draw (bar on 300-end; finish at the end):")
    print(f"{'queue':>10} {'dir':>14} {'seed':>11} {'ice%':>5} {'deep%':>5} {'dTmed':>6} {'bar':>4} {'T-PI':>5} "
          f"{'landice':>7} {'wetTr':>5} {'pCO2':>5} all")
    for q, dn, seed, j, rel, imin, wet, pe, ok in sorted(rows, key=lambda r: (r[0], r[1], r[2])):
        print(f"{q:>10} {dn:>14} {seed:>11} {j['share']:5.1f} {j['deep']:5.1f} {j['med']:+6.1f} "
              f"{'ok' if j['ok'] else flags(j).strip()[:4]:>4} {rel:+5.1f} {imin:7.1f} "
              f"{'-' if wet is None else f'{wet:.0f}':>5} {pe:5.0f} {'yes' if ok else 'no'}")
    print("\npass tallies (PW-865 bar, no icehouse cap; frozen over fails, PW-1091):")
    for k, v in sorted(tally.items()):
        print(f"  {k[0]:>10} {k[1]}: {sum(v)}/{len(v)}")


def judge_draw(raw):
    """One draw's bar and finish moment as pjudge and tools/hard_bar.py judge it: (series, bar, steps, finish_moment).
    pass = bar["ok"] and fm["passes"]."""
    s = C.series(raw)
    steps = [r for r in raw["steps"] if r["t"] > 0]
    window = float(raw["params"].get("finish_window", 10.0))
    fm = H.finish_moment([{"t": r["t"], "stats": r} for r in steps], window)
    end = steps[-1]["t"]  # (PW-1425: a world whose finish window has a moment that passes for ice is not frozen over)
    fin_ice = any("land ice" not in H.habitable(r) for r in steps if r["t"] >= end - window - 1e-9)
    bar = judge(s["t"], s["sea_ice"], s["dT"], 300, 1e9, s["iced_land"], s["star"], fin_ice)
    return s, bar, steps, fm


def _mean(rows, k):
    v = [r[k] for r in rows if r.get(k) is not None]
    return float(np.mean(v)) if v else float("nan")


def load(p, t0=600.0, t1=1000.0):
    raw = C.load(p)
    s, bar, steps, fm = judge_draw(raw)
    at = next(r for r in steps if abs(r["t"] - fm["t"]) < 1e-9)
    late = [r for r in steps if t0 <= r["t"] < t1 and abs(r["t"] - round(r["t"])) < 1e-9]
    ups = [u for u in raw["updates"] if t0 <= u["t"] <= t1]
    return dict(ok=bool(bar["ok"] and fm["passes"]), frozen=bool(bar["frozen"]), frozen_any=bool(bar["frozen_any"]),
                frozen_peak=bool(bar["frozen_peak"]), gmax=bool(bar["glacial_max"]), ihouse=bool(bar["icehouse"]), hell=bool(bar["hell"]),
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


def arm(root, name, rolls=None, level=6, t0=600.0, t1=1000.0):
    out = {}
    for d in sorted(Path(root).glob(f"{name}_r*_*")):
        roll, tag = d.name[len(name) + 2:].split("_", 1)
        if rolls and roll not in rolls:
            continue
        for p in d.glob(f"seed*_L{level}.json.gz"):
            r = load(p, t0, t1)
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


def paired_main(argv=None):
    """pjudge.py OUT_ROOT ARM_A ARM_B [...]: the paired merge judge, printed."""
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--rolls", nargs="*", help="default: every roll both arms have")
    ap.add_argument("--late", nargs=2, type=float, default=(600.0, 1000.0))
    ap.add_argument("--json")
    ap.add_argument("--level", type=int, default=6, help="the draws' grid level (paired.sh LEVEL)")
    ap.add_argument("--table", action="store_true", help="print the per-draw table")
    args = ap.parse_args(argv)
    T0, T1 = args.late
    ra, rb = arm(args.root, args.a, args.rolls, args.level, T0, T1), arm(args.root, args.b, args.rolls, args.level, T0, T1)
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
        n_pk = sum(R[k]["frozen_peak"] for k in keys)
        n_gm, n_ih = sum(R[k]["gmax"] for k in keys), sum(R[k]["ihouse"] for k in keys)
        sus = max(n_ice, n_hell) >= 0.8 * len(keys)
        pc[name] = dict(passes=sum(R[k]["ok"] for k in keys), frozen_over=n_ice, frozen_peak=n_pk, glacial_max=n_gm, icehouse=n_ih, hellhouse=n_hell, suspect=sus)
        print(f"- {name}: {', '.join(parts)}; pooled {pc[name]['passes']}/{len(keys)}; icehouse {n_ih}, glacial maximum {n_gm}, frozen over at the end {n_ice} (reported: 40%+ at some moment of the hard window {n_pk}, at some moment after 300 Myr but not at the end {n_dim}), hellhouse {n_hell}"
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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "bar":
        passrate_main(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == "paired":
        paired_main(sys.argv[2:])
    else:
        sys.exit(__doc__.split("--- passrate4")[0])
