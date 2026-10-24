"""Whole-history ice-age criteria for a run (PW-555, docs/review/ice-v2-criteria.md).

    uv run python tools/ice_criteria.py DIR/seed11.json[.gz] ...   (tools/ice_diag.py or tools/sealevel.py output)

Judges a run's history the way docs/review/ice-v2-criteria.md section 3 lays out, on the climate updates
(every 4 Myr) after a 300 Myr spin-up (SPINUP: the coupled systems settle into each other: the CO2
baselines learn fast at first, the climate drift needs ~40 Myr to reach its spread, the first ice starts
from none, the plants spread, the ocean basins start from a made-up floor), and the old bar beside it:

- old (PW-434/449/514): the worst sea level from ice >= -450 m and <= 2% of the time below -430 m (from
  t = 0, as tools/sealevel.py measured it);
- new, per run (section 3): N1 every cold era ends (deep, below DEEP m, within DEEP_MAX Myr; very deep,
  below VDEEP m, within VDEEP_MAX Myr; eras still on at the end are censored, not failed, if they started
  less than that before it); N2 the ice's sea level stays above FLOOR; N3 the planet spends between
  ICEHOUSE_SHARE of its time in an icehouse and no icehouse lasts longer than ICEHOUSE_MAX Myr (the share's floor
  only on runs of at least FLOOR_RUN Myr: a shorter window, e.g. health --quick's 300-500 Myr, can't hold the
  gap between two ice ages, Earth's Mesozoic was ~200 Myr without one; PW-709. The cap is judged on every
  window); N4 a hot
  era (dT above HOT C) ends within HOT_MAX Myr. Gaps between icehouses and their lengths are reported,
  not barred (Earth's range is 80 Myr to ~1.5 Gyr).

An icehouse is land ice holding at least -ICEHOUSE_SL m of sea level (20 m: about three Greenlands; Earth today ~65 m,
the Mesozoic ~0). Not an iced share of the land: the model keeps ice on its high tropical plateaus and polar
mountains at any dT it reaches (1-4% of the land; checkpoint 0), which is mountain ice, not an icehouse;
icehouse spells closer than JOIN Myr are one icehouse (a 4 Myr ice-free flicker inside an era isn't an
interglacial era of its own).
"""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np

SPINUP = 300.0  # Myr (owner, 2026-10-21: the first 300 Myr are a warm-up)
EVERY = 4.0  # Myr: the climate updates
ICEHOUSE_SL = -20.0  # m of sea level from ice
ICEHOUSE_LAND = 0.01  # (reported only: share of the land under ice)
JOIN = 8.0  # Myr
DEEP, DEEP_MAX = -150.0, 150.0  # m, Myr
VDEEP, VDEEP_MAX = -430.0, 60.0  # m, Myr
FLOOR = -1000.0  # m
ICEHOUSE_SHARE = (0.05, 0.70)
ICEHOUSE_MAX = 300.0  # Myr
FLOOR_RUN = 1000.0  # Myr: the run's end from which ICEHOUSE_SHARE's floor is judged (PW-709)
HOT, HOT_MAX = 8.0, 150.0  # C, Myr


def load(path) -> dict:
    p = Path(path)
    raw = gzip.open(p, "rt").read() if p.suffix == ".gz" else p.read_text()
    return json.loads(raw)


def series(d: dict) -> dict:
    """t, sea_ice, sea_tect, iced_land, dT on the climate updates, from ice_diag's steps or sealevel's track."""
    rows = d.get("steps") or d.get("track")
    rows = [r for r in rows if abs(r["t"] / EVERY - round(r["t"] / EVERY)) < 1e-6 and r["t"] > 0]
    get = lambda k, alt=None: np.array([r.get(k, r.get(alt)) if alt else r.get(k) for r in rows], dtype=float)
    out = {"t": get("t"), "sea_ice": get("sea_ice", "ice"), "sea_tect": get("sea_tect", "tect"),
           "dT": get("dT_end", "dT")}
    if "iced_land" in rows[0]:
        out["iced_land"] = get("iced_land")
    else:  # (sealevel.py's track: the iced share of the surface over the land's share)
        out["iced_land"] = get("ice_frac") / 100.0 / np.maximum(get("land") / 100.0, 1e-6)
    return out


def spells(t, mask, join: float = 0.0) -> list[list[float]]:
    """[t0, t1] of the runs of True in mask (t on EVERY samples); spells less than `join` Myr apart merge."""
    out = []
    for ti, m in zip(t, mask):
        if not m:
            continue
        if out and ti - out[-1][1] <= max(join, EVERY) + 1e-6:
            out[-1][1] = ti
        else:
            out.append([ti, ti])
    return out


def length(s) -> float:
    return s[1] - s[0] + EVERY


def evaluate(d: dict, spinup: float = SPINUP) -> dict:
    s = series(d)
    t_all, si_all = s["t"], s["sea_ice"]
    old_worst = float(si_all.min())
    old_430 = float((si_all < VDEEP).mean())
    late = t_all >= spinup
    t, si, dT, il = t_all[late], si_all[late], s["dT"][late], s["iced_land"][late]
    end = float(t.max())
    res = {"old": {"worst": round(old_worst), "below430_pct": round(100 * old_430, 1),
                   "pass": old_worst >= -450 and old_430 <= 0.02}}
    fails = []

    def ends(mask, limit, name):
        sp = spells(t, mask)
        longest = max((length(x) for x in sp), default=0.0)
        bad = [x for x in sp if length(x) > limit and not (x[1] >= end - 1e-6 and x[1] - x[0] < limit)]
        censored = [x for x in sp if x[1] >= end - 1e-6]
        if bad:
            fails.append(f"{name} {bad[0][0]:g}-{bad[0][1]:g} Myr lasts {length(bad[0]):g} > {limit:g}")
        return {"spells": len(sp), "longest": longest, "share_pct": round(100 * float(mask.mean()), 1),
                "on_at_end": bool(censored)}

    res["deep"] = ends(si < DEEP, DEEP_MAX, "deep era")
    res["vdeep"] = ends(si < VDEEP, VDEEP_MAX, "very deep era")
    res["hot"] = ends(dT > HOT, HOT_MAX, "hot era")
    res["worst"] = round(float(si.min()))
    if si.min() < FLOOR:
        fails.append(f"ice sea level {si.min():.0f} m below {FLOOR:g}")
    ice = si <= ICEHOUSE_SL
    sp = spells(t, ice, JOIN)
    lens = [length(x) for x in sp]
    gaps = [b[0] - a[1] - EVERY for a, b in zip(sp, sp[1:])]
    share = float(ice.mean())
    res["icehouse"] = {"share_pct": round(100 * share, 1), "eras": len(sp), "longest": max(lens, default=0.0),
                       "median_len": float(np.median(lens)) if lens else 0.0,
                       "gaps": gaps, "median_gap": float(np.median(gaps)) if gaps else None,
                       "first": sp[0][0] if sp else None,
                       "flicker_eras": sum(x <= EVERY + 1e-6 for x in lens)}
    floor = end >= FLOOR_RUN - EVERY  # (a 1 Gyr run's last climate update may fall a step short of its end)
    res["icehouse"]["floor_judged"] = floor
    if share > ICEHOUSE_SHARE[1] or (floor and share < ICEHOUSE_SHARE[0]):
        fails.append(f"icehouse {100 * share:.0f}% of the time, outside {100 * ICEHOUSE_SHARE[0]:g}-"
                     f"{100 * ICEHOUSE_SHARE[1]:g}%")
    if lens and max(lens) > ICEHOUSE_MAX:
        fails.append(f"an icehouse lasts {max(lens):g} > {ICEHOUSE_MAX:g} Myr")
    res["dT"] = {"min": round(float(dT.min()), 1), "max": round(float(dT.max()), 1)}
    res["tect"] = {"min": round(float(np.nanmin(s["sea_tect"][late]))), "max": round(float(np.nanmax(s["sea_tect"][late]))),
                   "end": round(float(s["sea_tect"][-1]))}
    # N5 (reported): ice reaches low latitudes only after high-latitude ice exists (Chandler & Sohl 2000)
    ups = [u for u in d.get("updates", []) if u["t"] >= spinup]
    if ups:
        bad = [u["t"] for prev, u in zip(ups, ups[1:]) if (u.get("iced_lat_min") is not None and u["iced_lat_min"] < 30)
               and not (prev.get("iced_lat_max") is not None and prev["iced_lat_max"] >= 60)]
        res["onset_low_first"] = bad
        res["lat_min"] = min((u["iced_lat_min"] for u in ups if u.get("iced_lat_min") is not None), default=None)
    res["fails"] = fails
    res["pass"] = not fails
    return res


def line(name: str, r: dict) -> str:
    ih, dp = r["icehouse"], r["deep"]
    return (f"{name}: old {'ok' if r['old']['pass'] else 'F'} ({r['old']['worst']} m, {r['old']['below430_pct']}% <-430) | "
            f"new {'ok' if r['pass'] else 'F'}: icehouse {ih['share_pct']}% in {ih['eras']} eras (longest {ih['longest']:g},"
            f" median gap {ih['median_gap']}), deep {dp['share_pct']}% longest {dp['longest']:g} Myr"
            f"{' (on at end)' if dp['on_at_end'] else ''}, <-430 longest {r['vdeep']['longest']:g}, worst {r['worst']} m,"
            f" dT {r['dT']['min']}..{r['dT']['max']}, basins {r['tect']['min']}..{r['tect']['max']} (end {r['tect']['end']})"
            + (f" -- {'; '.join(r['fails'])}" if r["fails"] else ""))


def main():
    for p in sys.argv[1:]:
        print(line(Path(p).name.split(".")[0], evaluate(load(p))))


if __name__ == "__main__":
    main()
