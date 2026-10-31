"""usage: screen.py DIR [...] -> the human-habitable screen at every step of a run's last 5, 10 and 20 Myr
(diagnostic only, coordinator's question: take the finished world at the latest passing moment, not the end).
A moment passes if
- the true mean temperature is within -6..+5 C of pre-industrial (passrate4's PREIND_T): the climate's true mean
  (updates, every climate_every Myr) carried to the 2-Myr steps through the run's dT (its offset to dT interpolated);
- the land ice at that moment is 1-25% of land (passrate4's LAND_ICE_NONE..LAND_ICE_LGM, at the moment);
- pCO2 >= 180 ppm (a proxy for C3 forests);
- and, for the "+trees" column, the wet equatorial lowland trees >= 20% at the nearest climate update.
Per draw: the latest passing moment's age before the end (Myr; '-' none in 20 Myr), without and with trees.
Harness only."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import climate  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

from planet.highlights import HUMAN_RANGE, PREIND_T  # noqa: E402  (the finish band's one definition, PW-1164: now -6..+5 C)
LAND_ICE_NONE, LAND_ICE_LGM, WET_TREES = 1.0, 25.0, 20.0

WINDOWS = (5, 10, 20)
rows = []
for d in map(Path, sys.argv[1:]):
    for p in sorted(d.glob("seed*_L*.json.gz")):
        raw = C.load(p)
        steps = [r for r in raw["steps"] if r["t"] > 0 and "iced_land" in r]
        ups = [u for u in raw["updates"] if u.get("temp") is not None]
        st = np.array([r["t"] for r in steps])
        end = float(st.max())
        sdT = np.array([r["dT"] for r in steps])
        ice = 100 * np.array([r["iced_land"] for r in steps])
        pc = climate.PCO2_BALANCE * np.exp(np.array([r["co2"] for r in steps]))
        ut = np.array([u["t"] for u in ups])
        off = np.array([u["temp"] - u["dT"] for u in ups])
        temp = sdT + np.interp(st, ut, off)
        wet = np.array([u.get("wet_eq_trees") if u.get("wet_eq_trees") is not None else -1.0 for u in ups])
        near = np.abs(st[:, None] - ut[None, :]).argmin(1)
        rel = temp - PREIND_T
        ok = ((HUMAN_RANGE[0] <= rel) & (rel <= HUMAN_RANGE[1]) & (LAND_ICE_NONE <= ice) & (ice < LAND_ICE_LGM)
              & (pc >= 180.0))
        okt = ok & (wet[near] >= WET_TREES)
        res = []
        for m in (ok, okt):
            w = st >= end - max(WINDOWS)
            hit = st[w & m]
            res.append(end - hit.max() if len(hit) else None)
        rows.append((d.name, p.name.split("_")[0], res, ok[-1], okt[-1]))

print(f"{'dir':>14} {'seed':>11}  latest pass, Myr before the end (screen / +trees)  end passes")
for dn, seed, (a, b), e, et in rows:
    f = lambda x: "-" if x is None else f"{x:.0f}"  # noqa: E731
    print(f"{dn:>14} {seed:>11}  {f(a):>5} / {f(b):>5}  {'yes' if e else 'no'} / {'yes' if et else 'no'}")
n = len(rows)
for w in WINDOWS:
    a = sum(r[2][0] is not None and r[2][0] <= w for r in rows)
    b = sum(r[2][1] is not None and r[2][1] <= w for r in rows)
    print(f"a passing moment in the last {w:>2} Myr: screen {a}/{n}, +trees {b}/{n}")
print(f"the end itself passes: screen {sum(r[3] for r in rows)}/{n}, +trees {sum(r[4] for r in rows)}/{n}")
