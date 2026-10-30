"""usage: judge.py ARM_A ARM_B [ROLL ...] -> paired table of two arms of paired.sh (judge/<ARM>_r<ROLL>_<tag>/).
Pass = good finish moment (highlights.finish_moment) and no hellhouse or frozen-over world (passrate4.judge). Also per-draw
end T, moment T, land %, and the carbon-cycle terms over 600-1000 Myr (means) for diagnosis."""
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

W = Path("/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a593a386fec489ab4")
sys.path.insert(0, str(W))
from planet import highlights as H  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

with redirect_stdout(io.StringIO()):
    _argv, sys.argv = sys.argv, [sys.argv[0]]
    sys.path.insert(0, str(W / "docs/review/base-climate/v1-finish-12"))
    import passrate4 as P  # noqa: E402
    sys.argv = _argv

J = Path(__file__).resolve().parent / "judge"
A, B = sys.argv[1], sys.argv[2]
ROLLS = sys.argv[3:] or ["0.0005", "0.001"]
TERMS = ["co2", "co2_term", "albedo_term", "drift", "src", "sink", "w_area", "w_supply", "w_temp", "w_plant",
         "w_rate", "w_T", "land", "ghg"]


def one(p):
    raw = C.load(p)
    s = C.series(raw)
    bar = P.judge(s["t"], s["sea_ice"], s["dT"], 300, 1e9, s["iced_land"])
    steps = [r for r in raw["steps"] if r["t"] > 0]
    fm = H.finish_moment([{"t": r["t"], "stats": r} for r in steps], float(raw["params"].get("finish_window", 10.0)))
    at = next(r for r in steps if abs(r["t"] - fm["t"]) < 1e-9)
    late = [r for r in steps if r["t"] >= 600]
    d = {k: float(np.mean([r[k] for r in late if r.get(k) is not None] or [np.nan])) for k in TERMS}
    early = [r for r in steps if 250 <= r["t"] < 300]
    d.update({k + "@300": float(np.mean([r[k] for r in early if r.get(k) is not None] or [np.nan])) for k in TERMS})
    return dict(ok=bool(bar["ok"] and fm["passes"]), frozen=bool(bar["frozen"]), hell=bool(bar["hell"]),
                mT=at["true_temp_c"] - H.PREIND_T, eT=steps[-1]["true_temp_c"] - H.PREIND_T, fails=H.habitable(at),
                dTend=steps[-1]["dT_end"], **d)


def arm(a):
    out = {}
    for r in ROLLS:
        for d in sorted(J.glob(f"{a}_r{r}_*")):
            for p in d.glob("seed*_L6.json.gz"):
                out[(r, d.name.split("_", 2)[2], p.name.split("_")[0])] = one(p)
    return out


ra, rb = arm(A), arm(B)
keys = sorted(set(ra) & set(rb))
print(f"{'roll':>6} {'tag':>6} {'seed':>11} | {A:>6} mT eT land co2 | {B:>6} mT eT land co2")
for k in keys:
    x, y = ra[k], rb[k]
    f = lambda z: f"{'PASS' if z['ok'] else 'fail':>6} {z['mT']:+5.1f} {z['eT']:+5.1f} {100*z['land']:4.1f} {z['co2']:+5.2f}" + (" F" if z["frozen"] else "  ") + (" H" if z["hell"] else "")
    print(f"{k[0]:>6} {k[1]:>6} {k[2]:>11} | {f(x)} | {f(y)}")
print(f"\npaired draws: {len(keys)} (A has {len(ra)}, B has {len(rb)})")
for name, R in [(A, ra), (B, rb)]:
    for r in ROLLS:
        ks = [k for k in keys if k[0] == r]
        print(f"  {name:>8} r{r}: pass {sum(R[k]['ok'] for k in ks)}/{len(ks)}, frozen over {sum(R[k]['frozen'] for k in ks)}, "
              f"hellhouse {sum(R[k]['hell'] for k in ks)}")
    print(f"  {name:>8} pooled: pass {sum(R[k]['ok'] for k in keys)}/{len(keys)}, frozen over {sum(R[k]['frozen'] for k in keys)}, "
          f"hellhouse {sum(R[k]['hell'] for k in keys)}, median end T {np.median([R[k]['eT'] for k in keys]):+.2f}, "
          f"median moment T {np.median([R[k]['mT'] for k in keys]):+.2f}, warm fails "
          f"{sum((not R[k]['ok']) and R[k]['mT'] > 3 for k in keys)}, cold fails {sum((not R[k]['ok']) and R[k]['mT'] < -6 for k in keys)}")
both = sum(ra[k]["ok"] and rb[k]["ok"] for k in keys)
ao = sum(ra[k]["ok"] and not rb[k]["ok"] for k in keys)
bo = sum(rb[k]["ok"] and not ra[k]["ok"] for k in keys)
print(f"  both {both}, {A} only {ao}, {B} only {bo}, neither {len(keys) - both - ao - bo}")
print("\n600-1000 Myr means (median over draws) and at 250-300 Myr:")
for t in TERMS:
    print(f"  {t:>12}: {A} {np.nanmedian([ra[k][t] for k in keys]):9.4f} ({np.nanmedian([ra[k][t + '@300'] for k in keys]):9.4f})"
          f"   {B} {np.nanmedian([rb[k][t] for k in keys]):9.4f} ({np.nanmedian([rb[k][t + '@300'] for k in keys]):9.4f})")
