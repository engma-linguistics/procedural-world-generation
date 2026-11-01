"""Life stages of a people (PW-917, PW-1148): stage ages from canon, annual mortality per stage by way of life, and what follows.

Built like dragon_ages.py (the dragons' stage-structured mortality): a schedule of annual mortality per stage gives the survivorship;
with a fecundity over the fertile window it gives the generation time T (mean age of mothers) and the growth rate r (Euler-Lotka).

Stages: infancy, childhood, adulthood, elder. Infancy is its own stage because infant mortality dominates pre-modern demography
(~23% die in the first year among foragers, below). Human stage ends: 1, 18, 45, 80 yr.

Mortality (annual, per stage) comes from Gurven & Kaplan 2007, "Longevity among hunter-gatherers", Population and Development Review
33:321, Table 2 (Siler fits h(x) = a1 e^(-b1 x) + a2 + a3 e^(b3 x)), integrated over each human stage (lane 78,
scratchpad l78/siler.py; the integration reproduces the table's l15: 0.56 / 0.64 / 0.61 against 0.57 / 0.64 / 0.60):
- forager: the average hunter-gatherer row;
- horticulturalist: the average forager-horticulturalist row (a people that has taken up a crop);
- agrarian: Sweden 1751-59 (a people that farms mainly, with the plough).
Which schedule a people lives under at a step is a condition of the history, not a date (owner 10-30): history.growth.life_era.

A people of other ages: the childhood stages stretch by adult_yr / 18, the adult ones by (lifespan - adult) / (80 - 18); each stage's
annual rate is divided by its stretch, so survival through every stage is the human one (lane 76's method,
docs/review/peoples-demography/report.md section 3). 'harsh' survival (kobolds, goblins: canon "rarely do so"): the childhood rates
raised until HARSH[0] reach adulthood, HARSH[1] more adult deaths a year (lane 76's judgement numbers).

Fecundity is flat over the fertile window (default: from 1.5 childhood-years after adulthood to 22 adult-years after it, humans
19.5-40: first birth 19.5 yr, Robson & Wood 2008 J Anat 212:394 Table 2; the last birth at 40 is lane 76's assumption). Its level is
closed so that the people's net reproduction under its own forager schedule is Rmax of its breeding class (Ginzburg, Burger & Damuth
2010, Biol Lett 6:850: Rmax per generation is ~3.5 in mammals whatever their size, ~7.8 in birds; 'slow' 2 and 'brood' 7 are lane 76's
classes). A gentler schedule (fewer children die) then raises the net reproduction and so r; a harsher one lowers it.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

STAGES = ("infancy", "childhood", "adulthood", "elder")
HUMAN_END = (1.0, 18.0, 45.0, 80.0)  # the human stage ends, yr
SCHEDULES = {  # annual mortality per stage (infancy, childhood, adulthood, elder), Gurven & Kaplan 2007 Table 2 (above)
    "forager": (0.2346, 0.0203, 0.0156, 0.0565),
    "horticulturalist": (0.1961, 0.0155, 0.0163, 0.0587),
    "agrarian": (0.2249, 0.0159, 0.0113, 0.0564),
}
ERAS = tuple(SCHEDULES)
BREEDING = {"slow": 2.0, "mammal": 3.5, "brood": 7.0}  # Rmax per generation (Ginzburg et al. 2010; slow and brood: lane 76)
SURVIVAL = ("normal", "harsh")
HARSH = (0.25, 0.05)  # harsh survival: share reaching adulthood, extra adult mortality a year (lane 76's kobold numbers, a judgement)
FIRST_BIRTH, LAST_BIRTH = 1.5, 22.0  # the default fertile window: childhood-years after adulthood, adult-years after adulthood
HUMAN = (18.0, 80.0)  # (adult_yr, lifespan_yr) of the human reference: x = r / r of it under the forager schedule
DX = 0.05  # yr, the life table's step


def _stage_ends(adult: float, life: float) -> tuple[float, float, float, float]:
    cp, ap = adult / HUMAN_END[1], (life - adult) / (HUMAN_END[3] - HUMAN_END[1])
    return (HUMAN_END[0] * cp, adult, adult + (HUMAN_END[2] - HUMAN_END[1]) * ap, life)


def _rates(adult, life, era, survival, mortality):
    """The annual mortality per stage of a people under a schedule (stretched, harsh applied, or the given override)."""
    if mortality is not None:
        return np.array(mortality, float)
    cp, ap = adult / HUMAN_END[1], (life - adult) / (HUMAN_END[3] - HUMAN_END[1])
    m = np.array(SCHEDULES[era], float) / np.array([cp, cp, ap, ap])
    if survival == "harsh":
        e = _stage_ends(adult, life)
        hz = m[0] * e[0] + m[1] * (e[1] - e[0])  # (the cumulative hazard to adulthood)
        m[:2] *= -np.log(HARSH[0]) / hz
        m[2:] += HARSH[1]
    return m


@lru_cache(maxsize=None)
def table(adult_yr: float, lifespan_yr: float, breeding: str = "mammal", fertile: tuple | None = None, survival: str = "normal",
          mortality: tuple | None = None) -> dict:
    """What a people's life history gives, per schedule: stage ends (yr), annual mortality per stage, survival to adulthood, net
    reproduction R0, generation time T (yr), growth rate r (/yr), x = r / the human forager r, and the sustainable loss (r / 2: the
    steady extra mortality at which it keeps half its numbers, N* = K (1 - h / r))."""
    if breeding not in BREEDING:
        raise ValueError(f"breeding must be one of {list(BREEDING)}")
    a, life = float(adult_yr), float(lifespan_yr)
    ends = _stage_ends(a, life)
    cp, ap = a / HUMAN_END[1], (life - a) / (HUMAN_END[3] - HUMAN_END[1])
    f0, f1 = fertile if fertile else (a + FIRST_BIRTH * cp, a + LAST_BIRTH * ap)
    x = np.arange(0.0, life + DX / 2, DX)
    st = np.searchsorted(np.array(ends[:3]), x, side="right")
    births = ((x >= f0) & (x <= f1)).astype(float)

    def surv(m):
        return np.exp(-np.concatenate([[0.0], np.cumsum(m[st][:-1] * DX)]))

    l_ref = surv(_rates(a, life, "forager", survival, mortality))
    fec = BREEDING[breeding] / max(float((l_ref * births).sum() * DX), 1e-12)
    out = {"stage_end": [round(e, 2) for e in ends], "fertile": [round(f0, 2), round(f1, 2)], "breeding": breeding,
           "survival": survival, "by_era": {}}
    for era in ERAS:
        m = _rates(a, life, era, survival, mortality)
        w = surv(m) * births * fec * DX
        R0 = float(w.sum())
        lo, hi = -0.5, 3.0
        for _ in range(80):
            r = 0.5 * (lo + hi)
            if (w * np.exp(-r * x)).sum() > 1.0:
                lo = r
            else:
                hi = r
        ew = w * np.exp(-r * x)
        out["by_era"][era] = {"mortality": [round(float(v), 5) for v in m], "adult_share": round(float(np.interp(a, x, surv(m))), 3),
                              "R0": round(R0, 3), "T": float((x * ew).sum() / max(ew.sum(), 1e-12)), "r": float(r)}
    return out


@lru_cache(maxsize=None)
def r_human() -> float:
    return table(*HUMAN)["by_era"]["forager"]["r"]


def of_line(l) -> dict | None:
    """A line's life table (table above), or None where it has no canon ages (adult_yr and lifespan_yr)."""
    if l.adult_yr is None or l.lifespan_yr is None:
        return None
    return table(float(l.adult_yr), float(l.lifespan_yr), l.breeding, tuple(l.fertile_yr) if l.fertile_yr else None, l.survival,
                 tuple(l.mortality) if l.mortality else None)


def generation_yr(l) -> float:
    """A line's generation time, yr: T under the forager schedule where it has canon ages, else its own generation_yr."""
    t = of_line(l)
    return l.generation_yr if t is None else t["by_era"]["forager"]["T"]


def x_of(l, era: str = "forager") -> float:
    """r of the line under a schedule over the human forager r (1 for a line without canon ages)."""
    t = of_line(l)
    return 1.0 if t is None else t["by_era"][era]["r"] / r_human()


def summary(l) -> dict | None:
    """The line's life history for the run output and the workbench (rounded)."""
    t = of_line(l)
    if t is None:
        return None
    rh = r_human()
    return {"adult_yr": l.adult_yr, "lifespan_yr": l.lifespan_yr, "stage_end": t["stage_end"], "fertile": t["fertile"],
            "breeding": t["breeding"], "survival": t["survival"],
            "by_era": {e: {**v, "T": round(v["T"], 1), "r_pct": round(100 * v["r"], 2), "x": round(v["r"] / rh, 2),
                           "sustain_pct": round(50 * v["r"], 2)} for e, v in t["by_era"].items()}}


@lru_cache(maxsize=None)
def _harsh_r(adult_yr: float, lifespan_yr: float, breeding: str, fertile: tuple | None, era: str, R: float) -> float:
    """r (/yr) of a harsh-survival people under a schedule whose harsh excess (the harsh rates less the normal ones) is scaled by R, with
    the fecundity closed as in table(): on the harsh forager schedule at R = 1 (lane 97, raid losses and in-fighting, history.counter)."""
    a, life = float(adult_yr), float(lifespan_yr)
    ends = _stage_ends(a, life)
    cp, ap = a / HUMAN_END[1], (life - a) / (HUMAN_END[3] - HUMAN_END[1])
    f0, f1 = fertile if fertile else (a + FIRST_BIRTH * cp, a + LAST_BIRTH * ap)
    x = np.arange(0.0, life + DX / 2, DX)
    st = np.searchsorted(np.array(ends[:3]), x, side="right")
    births = ((x >= f0) & (x <= f1)).astype(float)

    def surv(m):
        return np.exp(-np.concatenate([[0.0], np.cumsum(m[st][:-1] * DX)]))

    fec = BREEDING[breeding] / max(float((surv(_rates(a, life, "forager", "harsh", None)) * births).sum() * DX), 1e-12)
    mn, mh = _rates(a, life, era, "normal", None), _rates(a, life, era, "harsh", None)
    w = surv(mn + R * (mh - mn)) * births * fec * DX
    lo, hi = -0.5, 3.0
    for _ in range(80):
        r = 0.5 * (lo + hi)
        if (w * np.exp(-r * x)).sum() > 1.0:
            lo = r
        else:
            hi = r
    return float(r)


def harsh_kept(l, era: str, R: float) -> float:
    """The share of its numbers a harsh-survival line keeps (r' / r, lane 82's sustainable-loss form N* = K (1 - h / r)) when its harsh
    excess is R x the canon one (R 1: as its life table; lane 85's raid factor). 1 for a line of normal survival, without canon ages or with
    its own mortality schedule (nothing to scale), and for R <= 1 (no line is held above its habitat)."""
    if R <= 1.0 or l.survival != "harsh" or l.adult_yr is None or l.mortality:
        return 1.0
    fert = tuple(l.fertile_yr) if l.fertile_yr else None
    r1 = _harsh_r(float(l.adult_yr), float(l.lifespan_yr), l.breeding, fert, era, 1.0)
    if r1 <= 0:
        return 1.0
    return float(np.clip(_harsh_r(float(l.adult_yr), float(l.lifespan_yr), l.breeding, fert, era, round(R, 3)) / r1, 0.0, 1.0))
