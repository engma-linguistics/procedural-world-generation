"""Lane 158: option A's check read out. Per draw: the yardstick-pinned continuation against fm (same planet, same
300 Myr state, its own yardstick) and the forked nulls fn, fn2 (the do-nothing spread)."""
import gzip, json
import numpy as np
S = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad"
J = f"{S}/l144/judge"
draws = [("r0.001_l6c_p", "957317"), ("r0.001_l6c_0", "819014"), ("r0.0005_l6c_0", "819014")]


def rec(p):
    d = json.load(gzip.open(p))
    return {round(x["t"], 3): x for x in d["steps"] if abs(x["t"] - round(x["t"])) < 1e-9}, d


def stats(R):
    late = [R[t] for t in R if 600 < t <= 1000]
    return (np.mean([x["dT"] for x in late]), max(R[t]["iced_land_pct"] for t in R if 884 <= t <= 1000),
            np.mean([x["iced_land_pct"] for x in late]), 100 * np.mean([x["iced_land_pct"] >= 40 for x in late]))


print(f"{'draw':>22} {'arm':>5} {'late dT':>7} {'pk ice 884-1000':>15} {'mean ice':>8} {'%t>=40':>6}")
for dr, s in draws:
    out = {}
    for arm, p in [("fm", f"{J}/m_{dr}"), ("fn", f"{J}/n_{dr}"), ("fn2", f"{J}/n2_{dr}"), ("PIN", f"{S}/l158/pin/{dr}")]:
        try:
            R, d = rec(f"{p}/seed{s}_L6.json.gz")
        except FileNotFoundError:
            continue
        out[arm] = stats(R)
        extra = f"  (y {d['pin']['y_from']:.3f} -> {d['pin']['y_to']:.3f}; forecast late dT shift {10.7 * (d['pin']['y_from'] - d['pin']['y_to']):+.1f} C, " \
                f"peak ice {-25.8 * (d['pin']['y_from'] - d['pin']['y_to']):+.0f} pts)" if "pin" in d else ""
        print(f"{dr + ' ' + s:>22} {arm:>5} {out[arm][0]:+7.2f} {out[arm][1]:15.1f} {out[arm][2]:8.1f} {out[arm][3]:6.1f}{extra}")
    if "PIN" in out:
        base = np.mean([out[a][0] for a in ("fm", "fn", "fn2")])
        print(f"{'':>22}  PIN late dT minus the three unpinned histories' mean: {out['PIN'][0] - base:+.2f} C")
