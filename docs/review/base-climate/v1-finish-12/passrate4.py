"""usage: passrate4.py DIAG_DIR [...] -- the v1 icehouse bar as ruled on PW-865 (owner, option C, 2026-10-25).

The bar, judged on 300 Myr to the run's end (and per forward window 300-1000, 1000-1500, 1500-2000 Myr):
- FAIL on frozen over (owner 2026-10-30, PW-1091, replacing the old icebox rule): 40% or more of the LAND under ice
  at any climate update (`iced_land`, the run's saved stat);
- FAIL on hellhole: dT median > +10.5 C or max > +15.5 C;
- never-ice (icehouse share < 5%) and the old icebox rule (icehouse >= 90% of the time or deep ice < -150 m for 30%)
  are reported, not failures (owner 2026-10-27);
- no cap on the icehouse share (the old <= 40% is gone; the share is reported only).
The three ice terms (tools/ice_criteria.py ice_terms): icehouse (permanent polar sheets), glacial maximum (land ice
>= 25%, Earth's coldest) and frozen over (>= 40%); judge / flags / line report all three.

The finish checks, per run at its end:
- true area mean temperature (the climate's mean, PW-822) within -6..+3 C of pre-industrial 13.8 C;
- interglacial land ice near Earth's ~10% of land: the least over the last 12 Myr is not none (< 1%) and not
  LGM-like (>= 25%); the share inside 5-20% is also tallied as "near Earth";
- wet equatorial lowland (> 2000 mm) trees >= 20% (PW-806, hard check);
- end pCO2 in 180-600 ppm (diagnostic).
A seed-draw "passes all" when it passes the bar and the three hard finish checks (temperature, land ice, trees).
Harness only: no thresholds of tools/ice_criteria are changed."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import climate  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

PREIND_T = 13.8  # C: Earth's pre-industrial (1850-1900) area mean (Berkeley Earth / HadCRUT ~13.7-13.9)
HUMAN_RANGE = (-6.0, 3.0)  # C against it (LGM to Pliocene-ish; owner via coordinator 2026-10-25)
LAND_ICE_NONE, LAND_ICE_LGM = 1.0, 25.0  # % of land: none / LGM-like (Earth pre-industrial ~10, LGM ~25)
LAND_ICE_NEAR = (5.0, 20.0)  # % of land: "near Earth's ~10%" (reported)
WET_TREES = 20.0  # % trees on the wet equatorial lowland (PW-806)
PCO2_DIAG = (180.0, 600.0)  # ppm at the end (diagnostic)


def judge(t, si, dT, a, b, il=None):
    """il: the share of land under ice (0..1) on the same samples (C.series(raw)["iced_land"]). Without it the
    land terms are None and nothing is frozen over."""
    w = (t >= a) & (t < b)
    if not w.any():
        return None
    ice = C.ice_terms(si[w], None if il is None else il[w])
    share, deep = ice["icehouse_pct"], ice["deep_pct"]
    med, mx = float(np.median(dT[w])), float(dT[w].max())
    hell = med > 10.5 or mx > 15.5
    frozen = bool(ice["frozen_over"])
    # owner 2026-10-30 (PW-1091): a world fails on hellhouse or on frozen over (>= 40% of the land under ice).
    # Never-ice and the old icebox rule (icehouse >= 90% or deep >= 30%) are reported only. The set-level check
    # (fmtally, pjudge) flags the sim as wrong if nearly all worlds are frozen over or nearly all hellhouses.
    return dict(share=share, deep=deep, med=med, mx=mx, hell=hell, never=ice["never_ice"], frozen=frozen,
                glacial_max=bool(ice["glacial_max"]), land_ice_peak=ice["land_ice_peak"],
                icehouse=ice["icehouse"], always_icy=bool(share >= 90 or deep >= 30), ok=not hell and not frozen)


def flags(j):
    return ((" HELL" if j["hell"] else "") + (" FROZEN-OVER" if j["frozen"] else "") + (" GLACIAL-MAX" if j["glacial_max"] else "")
            + (" ICEHOUSE" if j["icehouse"] else "") + (" NEVER-ICE" if j["never"] else ""))


def line(j):
    pk = "n/a" if j["land_ice_peak"] is None else f"{j['land_ice_peak']:.0f}%"
    return (f"icehouse {j['share']:4.1f}% deep {j['deep']:4.1f}% land ice peak {pk} dT med {j['med']:+.1f} max {j['mx']:+.1f}"
            f"{flags(j)} -> {'ok' if j['ok'] else 'F'}")


def queue(d: Path, level: str, end: int) -> str:
    return f"L{level[1:]} {end / 1000:g} Gyr" if level.startswith("L") else f"{level} {end}"


tally = {}
rows = []


def add(k, v):
    tally.setdefault(k, []).append(bool(v))


for d in map(Path, sys.argv[1:]):
    for p in sorted(d.glob("seed*_L*.json.gz")):
        raw = C.load(p)
        s = C.series(raw)
        t, si, dT, il_s = s["t"], s["sea_ice"], s["dT"], s["iced_land"]
        end = float(t.max())
        steps = [r for r in raw["steps"] if r["t"] > 0]
        st = np.array([r["t"] for r in steps])
        co2 = np.array([r["co2"] for r in steps])
        sdT = np.array([r["dT"] for r in steps])
        pc = climate.PCO2_BALANCE * np.exp(co2)
        late = st >= 300
        last = raw["updates"][-1]
        q = queue(d, p.name.split("_")[1].split(".")[0], int(round(end / 100.0) * 100))
        seed = p.name.split("_")[0]
        allj = judge(t, si, dT, 300, 1e9, il_s)
        add((q, "bar 300-end"), allj["ok"])
        print(f"{d.name:>14} {seed:>11} 300-{end:.0f}: {line(allj)}")
        for a, b in [(300, 1000), (1000, 1500), (1500, 2000.1)]:
            j = judge(t, si, dT, a, b, il_s)
            if j is not None and b <= end + 1:
                print(f"{'':>27}{a:>4}-{min(b, 2000):.0f}: {line(j)}")
                add((q, f"bar {a}-{min(b, 2000):.0f}"), j["ok"])
        e540 = judge(t, si, dT, end - 540, 1e9, il_s)
        print(f"{'':>27}last 540 ({end - 540:.0f}-{end:.0f}, diagnostic): {line(e540)}")
        corr = float(np.corrcoef(sdT[late], co2[late])[0, 1]) if late.sum() > 3 else float("nan")
        print(f"{'':>27}pCO2 after 300: median {np.median(pc[late]):.0f} (10-90% {np.percentile(pc[late], 10):.0f}-"
              f"{np.percentile(pc[late], 90):.0f}), <180 ppm {100 * (pc[late] < 180).mean():.0f}%, at the end "
              f"{pc[-1]:.0f}; corr(dT, ln pCO2) {corr:+.2f}")
        rel = last["temp"] - PREIND_T
        t_ok = HUMAN_RANGE[0] <= rel <= HUMAN_RANGE[1]
        il = 100 * np.array([r["iced_land"] for r in steps if r["t"] >= end - 12 and "iced_land" in r])
        ice_end, ice_min = (float(il[-1]), float(il.min())) if len(il) else (float("nan"), float("nan"))
        ice_ok = LAND_ICE_NONE <= ice_min < LAND_ICE_LGM
        ice_near = LAND_ICE_NEAR[0] <= ice_min <= LAND_ICE_NEAR[1]
        iflag = " NO-ICE" if ice_min < LAND_ICE_NONE else (" LGM-LIKE" if ice_min >= LAND_ICE_LGM else "")
        wet = last.get("wet_eq_trees")
        tree_ok = wet is not None and wet >= WET_TREES
        co2_ok = PCO2_DIAG[0] <= pc[-1] <= PCO2_DIAG[1]
        all_ok = allj["ok"] and t_ok and ice_ok and tree_ok
        for k, v in [("finish T -6..+3", t_ok), ("finish land ice 1-25%", ice_ok), ("finish land ice 5-20%", ice_near),
                     ("finish wet-eq trees >= 20%", tree_ok), ("end pCO2 180-600 (diag.)", co2_ok),
                     ("bar + hard finish checks", all_ok)]:
            add((q, k), v)
        print(f"{'':>27}end: dT {last['dT']:+.1f}, true mean T {last['temp']:.1f} C, trees {last.get('trees')}% of land, "
              f"wet-eq lowland trees {'none' if wet is None else f'{wet:.0f}%'} ({last.get('wet_eq_cells')} cells)")
        print(f"{'':>27}finish: true mean {rel:+.1f} C vs pre-industrial ({'inside' if t_ok else 'OUTSIDE'} -6..+3); "
              f"land ice {ice_end:.1f}% at the end, {ice_min:.1f}% least in the last 12 Myr{iflag}; "
              f"trees {'ok' if tree_ok else 'LOW'}; -> {'PASSES ALL' if all_ok else 'fails'}")
        rows.append((q, d.name, seed, allj, rel, ice_min, wet, pc[-1], all_ok))

print("\nper draw (bar on 300-end; finish at the end):")
print(f"{'queue':>10} {'dir':>14} {'seed':>11} {'ice%':>5} {'deep%':>5} {'dTmed':>6} {'bar':>4} {'T-PI':>5} "
      f"{'landice':>7} {'wetTr':>5} {'pCO2':>5} all")
for q, dn, seed, j, rel, imin, wet, pe, ok in sorted(rows, key=lambda r: (r[0], r[1], r[2])):
    print(f"{q:>10} {dn:>14} {seed:>11} {j['share']:5.1f} {j['deep']:5.1f} {j['med']:+6.1f} "
          f"{'ok' if j['ok'] else flags(j).strip()[:4]:>4} {rel:+5.1f} {imin:7.1f} "
          f"{'-' if wet is None else f'{wet:.0f}':>5} {pe:5.0f} {'yes' if ok else 'no'}")
print("\npass tallies (PW-865 bar, no icehouse cap; frozen over fails, PW-1091):")
for k, v in sorted(tally.items()):
    print(f"  {k[0]:>10} {k[1]}: {sum(v)}/{len(v)}")
