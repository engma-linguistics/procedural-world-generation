"""Dragon age structure (PW-958): growth by age, candidate mortality schedules, and what follows from each.

From docs/proposals/megafauna-scaling.md and docs/review/megafauna/scaling.py (the owner-approved sums). A dragon grows all its life,
reptile-style: snout-to-tail length through 0.8 m at hatching, 3 m at 5 yr, 8 m at 100, 16 m at 800, 22 m at 1,500 and 28 m at
3,000 (the oldest); mass is a Komodo build (70 kg at 2.6 m, ~ L^3), x0.6 for flight. Food is reptile field metabolic rate (Nagy,
Girard & Brown 1999, Annu Rev Nutr 19:247: 0.196 M^0.889 kJ/day, M in g; the slope is from the abstract, the intercept unverified,
docs/references/megafauna/README.md), eaten as whole cattle (836 Mcal each, 85% assimilated).

Owner 10-28: younger is the default schedule; the others stay as options. meta.dragon_ages picks one:
- base: the proposal's approved base case (ancients ~7% of dragons, ~1/3 of their biomass);
- younger (default): annual mortality 20% wyrmling, 3% young, 0.5% adult, 0.1% ancient: young-heavy, ancients are the very best survivors;
- harsher: every rate up (PW-958's 'harsher' column of the review);
- gentler: every rate down (scaling.py's third case).
Each gives the stage shares, the ecological mass (survivorship-weighted mean mass past the wyrmling years, which sets the
natural density: Marshall et al. 2021), the generation time (PW-959: mean age of mothers, breeding from 100, flat fecundity or
fecundity ~ mass) and the food per dragon.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

STAGES = ("wyrmling", "young", "adult", "ancient")
STAGE_END = (5, 100, 800)  # the last year of each stage but the ancients'
OLDEST = 3000
BREED_FROM = 100  # years: adults breed
SCHEDULES = {  # annual mortality per stage (wyrmling, young, adult, ancient)
    "base": (0.20, 0.015, 0.0025, 0.004),
    "younger": (0.20, 0.03, 0.005, 0.001),
    "harsher": (0.30, 0.03, 0.005, 0.008),
    "gentler": (0.10, 0.01, 0.001, 0.002),
}
DEFAULT = "younger"  # (owner 10-28, PW-958)
GENERATION = ("schedule", "schedule_mass", "line")  # meta.dragon_generation: from the schedule (flat fecundity), with fecundity ~ mass, or each line's generation_yr
GENERATION_DEFAULT = "schedule"
CATTLE_MCAL = 836.0  # a whole carcass
ASSIMILATED = 0.85
KJ_PER_KCAL = 4.184

AGES = np.arange(OLDEST + 1)
LENGTH_M = np.interp(AGES, [0, 5, 100, 800, 1500, 3000], [0.8, 3, 8, 16, 22, 28])
MASS_KG = 0.6 * 70.0 * (LENGTH_M / 2.6) ** 3
STAGE_OF = np.select([AGES <= STAGE_END[0], AGES <= STAGE_END[1], AGES <= STAGE_END[2]], [0, 1, 2], 3)


def fmr_kcal(mass_kg):
    """Reptile field metabolic rate, kcal/day (Nagy et al. 1999)."""
    return 0.196 * (np.asarray(mass_kg, float) * 1000.0) ** 0.889 / KJ_PER_KCAL


def cattle_per_yr(kcal_day):
    return np.asarray(kcal_day, float) * 365.0 / (CATTLE_MCAL * 1000.0 * ASSIMILATED)


@lru_cache(maxsize=None)
def structure(name: str = DEFAULT) -> dict:
    """What a schedule gives: shares of individuals, biomass and food by stage; the ecological mass (kg); the all-ages factor
    (Damuth's density at the ecological mass counts the dragons past their first years; the same food spread over every age, the
    young eating less, holds this many times more); generation times (yr); food per dragon (kcal/day, cattle/yr), overall and by
    stage."""
    if name not in SCHEDULES:
        raise ValueError(f"meta.dragon_ages must be one of {list(SCHEDULES)}")
    m = np.array(SCHEDULES[name])[STAGE_OF]
    surv = np.concatenate([[1.0], np.cumprod(1.0 - m[:-1])])
    E = fmr_kcal(MASS_KG)
    post = AGES > STAGE_END[0]
    eco = float((surv * MASS_KG)[post].sum() / surv[post].sum())
    per_all = float((surv * E).sum() / surv.sum())
    breed = (AGES >= BREED_FROM).astype(float)
    st = lambda w: [float(w[STAGE_OF == s].sum() / w.sum()) for s in range(4)]
    n_st = [float(surv[STAGE_OF == s].sum()) for s in range(4)]
    return {"name": name, "mortality": SCHEDULES[name], "share": st(surv), "biomass_share": st(surv * MASS_KG),
            "food_share": st(surv * E), "eco_mass_kg": eco, "all_ages": float(fmr_kcal(eco)) / per_all,
            "generation_yr": float((AGES * surv * breed).sum() / (surv * breed).sum()),
            "generation_mass_yr": float((AGES * surv * breed * MASS_KG).sum() / (surv * breed * MASS_KG).sum()),
            "kcal_day": per_all, "cattle_yr": float(cattle_per_yr(per_all)),
            "stage_cattle_yr": [float(cattle_per_yr((surv * E)[STAGE_OF == s].sum() / n_st[s])) for s in range(4)],
            "stage_mass_kg": [float((surv * MASS_KG)[STAGE_OF == s].sum() / n_st[s]) for s in range(4)]}


def generation_yr(name: str, mode: str, line_yr: float) -> float:
    """A dragon line's generation time under meta.dragon_generation (PW-959)."""
    if mode == "line":
        return line_yr
    s = structure(name)
    return s["generation_mass_yr"] if mode == "schedule_mass" else s["generation_yr"]


def split(count: int, name: str, rng: np.random.Generator) -> list[int]:
    """A pocket's count drawn into stages (wyrmling, young, adult, ancient) by the schedule's shares."""
    if count <= 0:
        return [0, 0, 0, 0]
    return [int(x) for x in rng.multinomial(count, structure(name)["share"])]


def stages_text(st: list[int]) -> str:
    """'1 ancient, 6 adults, 4 young, 1 wyrmling' (largest stages first in age order: ancients first)."""
    nm = (("wyrmling", "wyrmlings"), ("young", "young"), ("adult", "adults"), ("ancient", "ancients"))
    return ", ".join(f"{int(st[s])} {nm[s][int(st[s]) != 1]}" for s in (3, 2, 1, 0) if st[s])
