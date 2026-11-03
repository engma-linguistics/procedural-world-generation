import sys, io
from pathlib import Path
from contextlib import redirect_stdout
ROOT = Path("/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a89edc91613c41ab7")
sys.path.insert(0, str(ROOT))
from planet import highlights as H
from tools import ice_criteria as C
from tools import judge as P
assert P.HUMAN_RANGE is H.HUMAN_RANGE
J = Path("/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l75/judge")
tot = {3.0: 0, 5.0: 0}; noice = []; rows = []
for d in sorted(J.glob("K_r0.0005_*")):
    for p in sorted(d.glob("seed*_L6.json.gz")):
        raw = C.load(p); s = C.series(raw)
        bar = P.judge(s["t"], s["sea_ice"], s["dT"], 300, 1e9, s["iced_land"], s["star"])
        steps = [r for r in raw["steps"] if r["t"] > 0]
        fr = [{"t": r["t"], "stats": r} for r in steps]
        w = float(raw["params"].get("finish_window", 10.0))
        res = {}
        for edge in (3.0, 5.0):
            H.HUMAN_RANGE = (-6.0, edge)
            fm = H.finish_moment(fr, w)
            res[edge] = (bool(bar["ok"] and fm["passes"]), fm)
        H.HUMAN_RANGE = (-6.0, 5.0)
        fm = res[5.0][1]
        at = next(r for r in steps if abs(r["t"] - fm["t"]) < 1e-9)
        win = [r for r in steps if r["t"] >= steps[-1]["t"] - w - 1e-9]
        land_ice_surf = 100 * at["ice_frac"]
        best = max(100 * r["ice_frac"] for r in win)
        has = best >= H.PERM_ICE_MIN_PCT
        for e in (3.0, 5.0): tot[e] += res[e][0]
        if not has: noice.append(f"{d.name[11:]} {p.name[:10]}")
        rows.append((d.name[11:], p.name[4:10], res[3.0][0], res[5.0][0], at["true_temp_c"] - H.PREIND_T, bar["ok"], fm["passes"], fm["fails_at_end"], land_ice_surf, best))
for r in rows:
    print(f"{r[0]:6} {r[1]} +3:{'P' if r[2] else '-'} +5:{'P' if r[3] else '-'} momT {r[4]:+5.1f} bar {r[5]} fm {r[6]} endfails {r[7]} landice% of surface at moment {r[8]:.2f} best-in-window {r[9]:.2f}")
print("pass +3", tot[3.0], "pass +5", tot[5.0], "of", len(rows))
print("no land-ice >=0.5% surface anywhere in the finish window:", len(noice), noice)
print("at the picked moment <0.5%:", sum(r[8] < 0.5 for r in rows))
