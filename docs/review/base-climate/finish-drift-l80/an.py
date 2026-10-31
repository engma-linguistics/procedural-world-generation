"""Per-draw decomposition of the finish: endT, fm T, ln src means by era, ln sink, drift, co2/albedo/star terms."""
import gzip, json, sys
from pathlib import Path
import numpy as np
WT = Path("/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a97c27d16a20f98d6")
sys.path.insert(0, str(WT))
from planet import highlights as H
J = Path("/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l75/judge")
DRAWS = [("l6fix", s) for s in (957317, 619496, 583167, 639472)] + [("l6c_0", s) for s in (53669, 733847, 819014, 958504)] \
    + [("l6c_m", s) for s in (53669, 958504)] + [("l6c_p", s) for s in (53669, 583167, 619496, 639472, 733847, 819014, 957317, 958504)]
arm = sys.argv[1] if len(sys.argv) > 1 else "K"
rows = []


def m(st, k, a, b, f=lambda x: x):
    v = [f(r[k]) for r in st if a <= r["t"] < b and r.get(k) is not None]
    return float(np.mean(v)) if v else np.nan


print(f"{'draw':14} {'endT':>5} {'fmT':>5} fm | lnsrc 300-500 500-700 700-850 850-990 last10 | lnsink10 | drift10 co2t alb star ghg | land300 land_end | ln supply end/300")
for tag, seed in DRAWS:
    p = J / f"{arm}_r0.0005_{tag}" / f"seed{seed}_L6.json.gz"
    raw = json.load(gzip.open(p)); st = [r for r in raw["steps"] if r["t"] > 0]
    end = st[-1]["t"]
    fm = H.finish_moment([{"t": r["t"], "stats": r} for r in st], float(raw["params"].get("finish_window", 10.0)))
    fr = [r for r in st if abs(r["t"] - fm["t"]) < 1e-6][0]
    L = lambda a, b: m(st, "src", a, b, np.log)
    sup0 = m(st, "w_supply", 250, 300); sup1 = m(st, "w_supply", end - 10, end + 1)
    d = dict(draw=f"{tag} {seed}", endT=st[-1]["true_temp_c"] - H.PREIND_T, fmT=fr["true_temp_c"] - H.PREIND_T, ok=fm["passes"],
             s1=L(300, 500), s2=L(500, 700), s3=L(700, 850), s4=L(850, end - 10), s5=L(end - 10, end + 1),
             k5=m(st, "sink", end - 10, end + 1, np.log), dr=m(st, "drift", end - 10, end + 1), co2t=fr["co2_term"], alb=fr["albedo_term"],
             star=fr["star"], ghg=fr["ghg"], l0=m(st, "land", 290, 310), l1=m(st, "land", end - 10, end + 1), sup=np.log(sup1 / sup0))
    rows.append(d)
    print(f"{d['draw']:14} {d['endT']:+5.1f} {d['fmT']:+5.1f} {'ok' if d['ok'] else 'NO'} | {d['s1']:+.2f} {d['s2']:+.2f} {d['s3']:+.2f} {d['s4']:+.2f} {d['s5']:+.2f} | "
          f"{d['k5']:+.2f} | {d['dr']:+.2f} {d['co2t']:+.1f} {d['alb']:+.1f} {d['star']:+.1f} {d['ghg']:+.1f} | {d['l0']:.3f} {d['l1']:.3f} | {d['sup']:+.2f}")
A = {k: np.array([r[k] for r in rows]) for k in rows[0] if k not in ("draw", "ok")}
print("median/sd:", {k: (round(float(np.median(v)), 2), round(float(np.std(v)), 2)) for k, v in A.items()})
c = np.polyfit(A["s5"], A["endT"], 1); print("endT vs ln src last10: slope", c, "r", np.corrcoef(A["s5"], A["endT"])[0, 1])
for k in ("s4", "dr", "alb", "sup", "l1", "co2t"):
    print(k, "r with endT", round(np.corrcoef(A[k], A["endT"])[0, 1], 2))
np.save(Path(__file__).parent / f"rows_{arm}.npy", rows, allow_pickle=True)
