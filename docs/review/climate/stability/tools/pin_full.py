"""Lane 160 (round2.md): option A's full check read out. Per draw (36 = paired.sh's 18 x rolls 0.0005, 0.001): the yardstick-pinned
continuations P (pin.py) and P2 (pin.py + 1e-5 C after the fork), against lane 140's unpinned main runs of the same
draws (l140/judge/main_*, code 4abc1707) and, on lane 144's six cold draws, its forked fm / fn / fn2."""
import glob, gzip, json, sys
from collections import defaultdict
import numpy as np
S = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad"
L, M, F = f"{S}/l160/judge", f"{S}/l140/judge", f"{S}/l144/judge"


def load(p):
    try:
        d = json.load(gzip.open(p))
    except FileNotFoundError:
        return None
    st = d["steps"]
    x = [s for s in st if s["t"] > 400][0]
    y = float(np.log(x["source_raw"] / x["src"]) - np.log(x["sink_raw"] / x["sink"]))
    late = [s for s in st if 600 < s["t"] <= 1000]
    win = [s for s in st if 884 <= s["t"] <= 1000]
    return dict(y=y, late=float(np.mean([s["dT"] for s in late])), lmed=float(np.median([s["dT"] for s in late])),
                lmax=float(max(s["dT"] for s in late)), pk=float(max(s["iced_land_pct"] for s in win)),
                end_ice=float(st[-1]["iced_land_pct"]), end_dT=float(st[-1]["dT"]),
                t40=float(100 * np.mean([s["iced_land_pct"] >= 40 for s in late])))


draws = []
for R in ("0.0005", "0.001"):
    for line in open(f"{S}/l160/draws.txt"):
        tag, seed, _ = line.split()
        draws.append((R, tag, seed))
arms = {"main": lambda R, t, s: f"{M}/main_r{R}_{t}/seed{s}_L6.json.gz",
        "P": lambda R, t, s: f"{L}/P_r{R}_{t}/seed{s}_L6.json.gz",
        "P2": lambda R, t, s: f"{L}/P2_r{R}_{t}/seed{s}_L6.json.gz",
        "fm": lambda R, t, s: f"{F}/m_r{R}_{t}/seed{s}_L6.json.gz",
        "fn": lambda R, t, s: f"{F}/n_r{R}_{t}/seed{s}_L6.json.gz",
        "fn2": lambda R, t, s: f"{F}/n2_r{R}_{t}/seed{s}_L6.json.gz"}
D = {(R, t, s): {a: load(f(R, t, s)) for a, f in arms.items()} for R, t, s in draws}
print(f"{'draw':>24} {'y0':>6} {'main':>6} {'P':>6} {'P2':>6} {'P-main':>6} {'fcst':>5} | pk ice main P P2 | end ice main P P2 | late max P P2")
for k, v in D.items():
    m, p, q = v["main"], v["P"], v["P2"]
    f = lambda r, key, fmt="+6.2f": format(r[key], fmt) if r else "   -  "
    yy = p["y"] if p else m["y"]
    print(f"{' '.join(k):>24} {m['y']:6.3f} {f(m,'late')} {f(p,'late')} {f(q,'late')} "
          f"{(p['late'] - m['late']) if p else float('nan'):+6.2f} {10.7 * (m['y'] - 1.316):+5.1f} | "
          f"{f(m,'pk','5.1f')} {f(p,'pk','5.1f')} {f(q,'pk','5.1f')} | {f(m,'end_ice','5.1f')} {f(p,'end_ice','5.1f')} {f(q,'end_ice','5.1f')} | "
          f"{f(p,'lmax')} {f(q,'lmax')}")


def within(arm, key="late"):
    by = defaultdict(list)
    for (R, t, s), v in D.items():
        if v[arm]:
            by[s].append(v[arm][key])
    g = [x for x in by.values() if len(x) > 1]
    return float(np.sqrt(np.mean([np.var(x, ddof=1) for x in g]))), sum(len(x) for x in by.values())


def allsd(arm, key="late"):
    x = np.array([v[arm][key] for v in D.values() if v[arm]])
    return x.mean(), x.std(ddof=1), x.min(), x.max(), len(x)


print()
for arm in ("main", "P", "P2"):
    w, n = within(arm)
    mu, sd, lo, hi, n2 = allsd(arm)
    wp, _ = within(arm, "pk")
    mp, sp, lp, hp, _ = allsd(arm, "pk")
    print(f"{arm:>4} n={n}: late dT within-seed sd {w:.2f} C; all-run mean {mu:+.2f} sd {sd:.2f} range {lo:+.2f}..{hi:+.2f}; "
          f"peak ice within-seed sd {wp:.1f}, all sd {sp:.1f}, max {hp:.1f}")
# twins: the same 300 Myr state, two continuations
pairs = [(v["P"]["late"], v["P2"]["late"]) for v in D.values() if v["P"] and v["P2"]]
if pairs:
    d = np.array([a - b for a, b in pairs])
    print(f"pinned twins P vs P2 ({len(d)} draws): sd of one history about the pair mean {np.sqrt(np.mean(d ** 2) / 2):.2f} C, "
          f"median |diff| {np.median(np.abs(d)):.2f}")
up = [(v["fm"]["late"], v["fn"]["late"], v["fn2"]["late"]) for v in D.values() if v["fm"] and v["fn"] and v["fn2"]]
if up:
    print(f"unpinned forked twins fm/fn/fn2 ({len(up)} draws): sd within draw {np.sqrt(np.mean([np.var(x, ddof=1) for x in up])):.2f} C")
    pp = [(v["P"]["late"], v["P2"]["late"]) for v in D.values() if v["fm"] and v["fn"] and v["P"] and v["P2"]]
    if pp:
        print(f"  same six, pinned P/P2: sd within draw {np.sqrt(np.mean([np.var(x, ddof=1) for x in pp])):.2f} C")
# within-seed with both pinned histories pooled (up to 12 histories per seed: 4-6 draws x 2)
by = defaultdict(list)
for (R, t, s), v in D.items():
    for a in ("P", "P2"):
        if v[a]:
            by[s].append(v[a]["late"])
g = [x for x in by.values() if len(x) > 1]
if g:
    print(f"P+P2 pooled within-seed sd {np.sqrt(np.mean([np.var(x, ddof=1) for x in g])):.2f} C")
json.dump({" ".join(k): v for k, v in D.items()}, open(f"{S}/l160/ana.json", "w"), indent=1)
