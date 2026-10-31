"""usage: pairs290.py L6_ROOT L7_ROOT -> PW-290 pairs: for each seed-draw (seed x climate offset) run at both levels, the
median over the climate updates in 50-1000 Myr of Koppen B share of land (arid_pct), BWh share (bwh_pct), tree cover
(trees, only updates with trees > 0, i.e. after the plants spread) and land rain (land_precip), L6 | L7 and L7 - L6.
Harness only."""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import ice_criteria as C  # noqa


def med(raw, k, pos=False):
    v = [u[k] for u in raw["updates"] if 50 <= u["t"] <= 1000 and u.get(k) is not None and (not pos or u[k] > 0)]
    return float(np.median(v))


l6, l7 = Path(sys.argv[1]), Path(sys.argv[2])
rows = []
print(f"{'draw':>22} | {'arid L6':>7} {'L7':>5} {'d':>5} | {'BWh L6':>6} {'L7':>5} {'d':>5} | {'trees L6':>8} {'L7':>5} {'d':>5} | {'rain L6':>7} {'L7':>5} {'d':>5}")
for p7 in sorted(l7.glob("m_r*_*/seed*_L7.json.gz")):
    p6 = l6 / p7.parent.name / p7.name.replace("_L7", "_L6")
    if not p6.exists():
        continue
    a, b = C.load(str(p6)), C.load(str(p7))
    r = []
    for k, pos in [("arid_pct", False), ("bwh_pct", False), ("trees", True), ("land_precip", False)]:
        x, y = med(a, k, pos), med(b, k, pos)
        r += [x, y, y - x]
    rows.append(r)
    print(f"{p7.parent.name[2:] + ' ' + p7.name.split('_')[0][4:]:>22} | {r[0]:7.1f} {r[1]:5.1f} {r[2]:+5.1f} | {r[3]:6.1f} {r[4]:5.1f} {r[5]:+5.1f} | {r[6]:8.1f} {r[7]:5.1f} {r[8]:+5.1f} | {r[9]:7.0f} {r[10]:5.0f} {r[11]:+5.0f}")
m = np.array(rows)
print(f"\n{len(rows)} pairs; median differences L7 - L6: arid {np.median(m[:,2]):+.1f}, BWh {np.median(m[:,5]):+.1f}, trees {np.median(m[:,8]):+.1f}, land rain {np.median(m[:,11]):+.0f} mm/yr; "
      f"L7 drier (arid higher) in {int((m[:,2] > 0).sum())}/{len(rows)} pairs; mean arid L6 {m[:,0].mean():.1f}, L7 {m[:,1].mean():.1f}")
