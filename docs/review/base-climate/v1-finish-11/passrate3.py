"""usage: passrate3.py DIAG_DIR [...] -- the strict v1 bar (unchanged from v1-signoff: icehouse share <= 40%, no
always-icebox, no hellhole, and never-ice (< 5% icehouse) is a FAIL), judged on 300 Myr to the run's end, plus
per window: the forward windows (300-1000, 1000-1500, 1500-2000 Myr) and, as a reported diagnostic only (PW-812),
the end-counted last 540 Myr (the Phanerozoic analogue under the end-anchored star). Also per run: pCO2 (median,
10-90%, share < 180 ppm, at the end), the true area mean temperature (PW-822: the climate's mean, not 14.5 + dT)
at the end, tree cover over land and over the wet equatorial lowland at the end (%), and corr(dT, ln pCO2)
after 300 Myr (PW-819). Harness only: the thresholds are tools/ice_criteria's and v1-signoff's."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import climate  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

OWNER_BAR = 40.0
from planet.highlights import HUMAN_RANGE, PREIND_T  # noqa: E402  (the finish band's one definition, PW-1164: now -6..+5 C)
# (LGM to Pliocene-ish; coordinator 2026-10-25, owner feedback). Diagnostic only
EARTH_LAND_ICE = (10.0, 25.0)  # % of land under ice: Earth pre-industrial ~10, LGM ~25. Diagnostic only


def judge(t, si, dT, a, b):
    w = (t >= a) & (t < b)
    if not w.any():
        return None
    share = 100 * float((si[w] <= C.ICEHOUSE_SL).mean())
    deep = 100 * float((si[w] < -150).mean())
    med, mx = float(np.median(dT[w])), float(dT[w].max())
    hell = med > 10.5 or mx > 15.5
    icebox = share >= 90 or deep >= 30
    never = share < 5
    return dict(share=share, deep=deep, med=med, mx=mx, hell=hell, icebox=icebox, never=never,
                ok=share <= OWNER_BAR and not hell and not icebox and not never)


def flags(j):
    return (" HELL" if j["hell"] else "") + (" ICEBOX" if j["icebox"] else "") + (" NEVER-ICE" if j["never"] else "")


def line(j):
    return (f"icehouse {j['share']:4.1f}% deep {j['deep']:4.1f}% dT med {j['med']:+.1f} max {j['mx']:+.1f}"
            f"{flags(j)} -> {'ok' if j['ok'] else 'F'}")


tally = {}
for d in sys.argv[1:]:
    for p in sorted(Path(d).glob("seed*_L*.json.gz")):
        raw = C.load(p)
        s = C.series(raw)
        t, si, dT = s["t"], s["sea_ice"], s["dT"]
        end = float(t.max())
        steps = [r for r in raw["steps"] if r["t"] > 0]
        st = np.array([r["t"] for r in steps])
        co2 = np.array([r["co2"] for r in steps])
        sdT = np.array([r["dT"] for r in steps])
        pc = np.array([climate.PCO2_BALANCE * np.exp(c) for c in co2])
        late = st >= 300
        ups = raw["updates"]
        last = ups[-1]
        allj = judge(t, si, dT, 300, 1e9)
        key = (Path(d).name.split("_")[0], p.name.split("_")[1].split(".")[0], int(round(end)))
        tally.setdefault(key, []).append(allj["ok"])
        e540 = judge(t, si, dT, end - 540, 1e9)
        tally.setdefault(key + ("last540",), []).append(e540["ok"])
        corr = float(np.corrcoef(sdT[late], co2[late])[0, 1]) if late.sum() > 3 else float("nan")
        print(f"{Path(d).name:>14} {p.name.split('_')[0]:>11} 300-{end:.0f}: {line(allj)}")
        for a, b in [(300, 1000), (1000, 1500), (1500, 2000.1)]:
            j = judge(t, si, dT, a, b)
            if j is not None and b <= end + 1:
                print(f"{'':>27}{a:>4}-{min(b, 2000):.0f}: {line(j)}")
                tally.setdefault(key + (f"{a}-{min(b, 2000):.0f}",), []).append(j["ok"])
        print(f"{'':>27}last 540 ({end - 540:.0f}-{end:.0f}, diagnostic): {line(e540)}")
        print(f"{'':>27}pCO2 after 300: median {np.median(pc[late]):.0f} (10-90% {np.percentile(pc[late], 10):.0f}-"
              f"{np.percentile(pc[late], 90):.0f}), <180 ppm {100 * (pc[late] < 180).mean():.0f}%, at the end "
              f"{pc[-1]:.0f}; corr(dT, ln pCO2) {corr:+.2f}")
        wet = last.get("wet_eq_trees")
        rel = last["temp"] - PREIND_T
        inside = HUMAN_RANGE[0] <= rel <= HUMAN_RANGE[1]
        tally.setdefault(key + ("end T in human range",), []).append(inside)
        il = 100 * np.array([r["iced_land"] for r in steps if r["t"] >= end - 12 and "iced_land" in r])
        ice_end, ice_min = (float(il[-1]), float(il.min())) if len(il) else (float("nan"), float("nan"))
        iflag = " NO-ICE" if ice_min < 1.0 else (" LGM-LIKE" if ice_min >= EARTH_LAND_ICE[1] else "")
        tally.setdefault(key + ("end land ice 1-25%",), []).append(iflag == "")
        print(f"{'':>27}end: dT {last['dT']:+.1f}, true mean T {last['temp']:.1f} C (14.5 + dT = {14.5 + last['dT']:.1f}), "
              f"trees {last.get('trees')}% of land, wet-eq lowland trees "
              f"{'none' if wet is None else f'{wet:.0f}%'} ({last.get('wet_eq_cells')} cells)")
        print(f"{'':>27}finish: true mean {rel:+.1f} C vs pre-industrial ({'inside' if inside else 'OUTSIDE'} -6..+5); "
              f"land ice {ice_end:.1f}% at the end, {ice_min:.1f}% least in the last 12 Myr (Earth ~10, LGM ~25){iflag}")
print("\npass tallies (strict bar):")
for k, v in sorted(tally.items(), key=lambda kv: str(kv[0])):
    print(f"  {' '.join(map(str, k))}: {sum(v)}/{len(v)}")
