import sys, io
from pathlib import Path
from contextlib import redirect_stdout
ROOT = Path("/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a89edc91613c41ab7")
sys.path.insert(0, str(ROOT))
from planet import highlights as H
from tools import ice_criteria as C
sys.path.insert(0, str(ROOT / "docs/review/base-climate/v1-finish-12"))
with redirect_stdout(io.StringIO()):
    _a, sys.argv = sys.argv, [sys.argv[0]]
    import passrate4 as P
    sys.argv = _a
J = Path("/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l75/judge")
print("with require_ice (land ice_frac proxy; sea ice not recorded in these runs: a lower bound)")
n = 0; rer = []
for d in sorted(J.glob("K_r0.0005_*")):
    for p in sorted(d.glob("seed*_L6.json.gz")):
        raw = C.load(p); s = C.series(raw)
        bar = P.judge(s["t"], s["sea_ice"], s["dT"], 300, 1e9, s["iced_land"], s["star"])
        steps = [r for r in raw["steps"] if r["t"] > 0]
        fr = [{"t": r["t"], "stats": {**r, "perm_ice_pct": 100 * r["ice_frac"]}} for r in steps]
        fm = H.finish_moment(fr, float(raw["params"].get("finish_window", 10.0)), True)
        ok = bool(bar["ok"] and fm["passes"]); n += ok
        if fm["no_permanent_ice"]:
            rer.append(d.name[11:] + " " + p.name[:10])
        print(d.name[11:], p.name[4:10], ok, fm["t"], fm["before_end_myr"], "REROLL" if fm["no_permanent_ice"] else "")
print("pass with require_ice:", n, "rerolls:", rer)
