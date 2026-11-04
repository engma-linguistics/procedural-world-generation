"""Lane 158: read the pulse runs against lane 144's forked main (fm, the same run without the pulse) and the two
forked nulls (fn, fn2: the do-nothing spread at the same moments). 10 Myr means."""
import gzip, json, sys
import numpy as np
S = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad"
J = f"{S}/l144/judge"
draw, seed = "r0.001_l6c_p", "957317"


def rec(p):
    st = json.load(gzip.open(p))["steps"]
    return {round(x["t"], 3): x for x in st if abs(x["t"] - round(x["t"])) < 1e-9}


fm, fn, fn2 = (rec(f"{J}/{a}_{draw}/seed{seed}_L6.json.gz") for a in ("m", "n", "n2"))
for arm in sys.argv[1:]:
    p = rec(f"{S}/l158/pulse/{arm}/seed{seed}_L6.json.gz")
    same = all(abs(p[t]["dT"] - fm[t]["dT"]) < 1e-12 for t in p if t <= 700)
    print(f"== {arm}: equal to fm up to 700 Myr: {same}")
    print(f"{'Myr':>9} {'dT fm':>6} {'pulse':>6} {'diff':>6} {'nulls diff':>11} {'lnX diff':>8} {'ice fm':>6} {'ice p':>6} {'nulls ice':>10}")
    for a in list(range(690, 780, 10)) + list(range(780, 1000, 20)):
        ts = [t for t in p if a < t <= a + 10 and t in fm]
        m = lambda R, k: np.mean([R[t][k] for t in ts])
        nd = [m(R, "dT") - m(fm, "dT") for R in (fn, fn2)]
        ni = [m(R, "iced_land_pct") for R in (fn, fn2)]
        print(f"{a:>4}-{a + 10:<4} {m(fm, 'dT'):+6.2f} {m(p, 'dT'):+6.2f} {m(p, 'dT') - m(fm, 'dT'):+6.2f} "
              f"{nd[0]:+5.2f},{nd[1]:+5.2f} {m(p, 'co2') - m(fm, 'co2'):+8.3f} {m(fm, 'iced_land_pct'):6.1f} "
              f"{m(p, 'iced_land_pct'):6.1f} {ni[0]:5.1f},{ni[1]:4.1f}")
    ts = [t for t in p if 720 < t <= 760]
    d = np.mean([p[t]["dT"] - fm[t]["dT"] for t in ts])
    F = json.load(gzip.open(f"{S}/l158/pulse/{arm}/seed{seed}_L6.json.gz"))["pulse"]["F"]
    print(f"  720-760: dT moved {d:+.2f} C for a push of {F:+.1f} C: the thermostat cancelled {100 * (1 - d / F):.0f}%")
    pk = max(p[t]["iced_land_pct"] for t in p if 884 <= t <= 1000)
    print(f"  hard-window peak land ice {pk:.1f}% (fm {max(fm[t]['iced_land_pct'] for t in fm if 884 <= t <= 1000):.1f}, "
          f"fn {max(fn[t]['iced_land_pct'] for t in fn if 884 <= t <= 1000):.1f}, fn2 {max(fn2[t]['iced_land_pct'] for t in fn2 if 884 <= t <= 1000):.1f})")
