"""sensitivity.py [OUT.json]: how the dragon-density page's headline number moves with each key constant, worked out analytically (no runs).

The headline is the model's density where nobody else eats: dragons per km2 per t/km2 of prey = OFFTAKE x s / F, with s the apex size
class's share of the guild's food (megafauna.guild_ratio) and F a dragon's yearly kill, t of live prey (dragon_ages: survivorship-averaged
field metabolic rate x 365 / (836 Mcal per 0.5 t carcass x assimilation)). Each row changes one constant and gives the factor on the
density and the resulting "1 dragon per X km2 at 1 t/km2". A last group changes the prey itself (the above-ground fraction of the NPP fed
to McNaughton's fit), which scales density through prey, not through the coefficient.

Sources are the PDFs in docs/references/megafauna/ (page numbers as printed). Imported by dragon_numbers.py; runs standalone too:
    uv run python docs/review/megafauna/dragon-density/sensitivity.py
"""
import json
import sys

import numpy as np

from planet.lineages import dragon_ages as DA
from planet.lineages import prey as PR
from planet.lineages.history import megafauna as MG

KJ = DA.KJ_PER_KCAL
DS = DA.structure(DA.DEFAULT)
_m = np.array(DA.SCHEDULES[DA.DEFAULT])[DA.STAGE_OF]
SURV = np.concatenate([[1.0], np.cumprod(1.0 - _m[:-1])])  # the default ("younger") schedule's survivorship, as dragon_ages.structure
G = DA.MASS_KG * 1000.0  # mass at each age, g


def mean_kcal(a: float, b: float, scale: float = 1.0) -> float:
    """A field metabolic rate law a M^b kJ/day (M in g), x scale, averaged over the age schedule as the model does: kcal/day."""
    return float((SURV * scale * a * G ** b).sum() / SURV.sum()) / KJ


def apex_share(b: float) -> float:
    """The apex classes' (>= 1 t) share of the guild's food when each class's individuals are weighted by M^b."""
    f = np.array([n * m ** b for m, n in MG.GUILD_CLASSES])
    top = np.array([m >= MG.GUILD_APEX_KG for m, _ in MG.GUILD_CLASSES])
    return float(f[top].sum() / f.sum())


BASE = {"kcal_day": DS["kcal_day"], "assim": DA.ASSIMILATED, "carcass": 1.0, "share": apex_share(MG.GUILD_KLEIBER), "offtake": MG.OFFTAKE}


def coef(kcal_day=None, assim=None, carcass=None, share=None, offtake=None) -> float:
    """Dragons per km2 per t/km2 of prey where nobody else eats."""
    p = dict(BASE)
    p.update({k: v for k, v in dict(kcal_day=kcal_day, assim=assim, carcass=carcass, share=share, offtake=offtake).items() if v is not None})
    kill_t = p["kcal_day"] * 365.0 / (DA.CATTLE_MCAL * 1000.0 * p["assim"] * p["carcass"]) * PR.HEAD_T
    return p["offtake"] * p["share"] / kill_t


C0 = coef()
assert abs(C0 - MG.OFFTAKE / (1.0 + MG.guild_ratio()) / (DS["cattle_yr"] * PR.HEAD_T)) < 1e-12  # the model's own number

# Coe, Cumming & Phillipson 1976, Table 1 (pp. 344-345), the 24 wildlife areas: large-herbivore biomass and production, kg/km2 (/yr), live
# weight. (Transcribed from the PDF; production there comes from assumed size-class P/B ratios of 0.05 / 0.20 / 0.35, p. 343-344.)
COE_B = [17448, 19928, 13261, 19189, 7561, 6688, 4348, 7568, 405, 2018, 4824, 4033, 4388, 1731, 5423, 8352, 3909, 3980, 4315, 2869, 984,
         3783, 3344, 4385]
COE_P = [1936, 2554, 1145, 2405, 1503, 1409, 934, 1983, 87, 402, 1008, 351, 438, 147, 1134, 1743, 364, 871, 722, 684, 162, 884, 765, 605]
COE_PB = [p / b for p, b in zip(COE_P, COE_B)]


def rows() -> list[dict]:
    """The sensitivity table: group, label, source, the factor on density, and 1 per X km2 at 1 t/km2."""
    out = []

    def add(group, label, source, c=None, factor=None, note=""):
        f = factor if factor is not None else c / C0
        out.append({"group": group, "label": label, "source": source, "factor": f, "one_per_km2_at_1t": 1.0 / (C0 * f), "note": note})

    # 1. intake: which field metabolic rate law, averaged over the same age schedule (Nagy et al. 1999, Table 2: all reptiles eq. 32,
    # lizards eq. 33, Varanidae eq. 36 on p. 261; mammals and birds on p. 260; McNab 2009: varanids p. 12185, dinosaurs at 31% of mammals p. 12187)
    laws = [
        ("All reptiles, 0.196 M^0.889 (the model)", "Nagy et al. 1999, Table 2, eq. 32, p. 261", 0.196, 0.889, 1.0),
        ("Varanid lizards, McNab's fit, 1.07 M^0.735", "McNab 2009, p. 12185", 1.07, 0.735, 1.0),
        ("All lizards, 0.190 M^0.916", "Nagy et al. 1999, Table 2, eq. 33, p. 261", 0.190, 0.916, 1.0),
        ("Varanidae, 0.208 M^0.915", "Nagy et al. 1999, Table 2, eq. 36, p. 261", 0.208, 0.915, 1.0),
        ("Dinosaur-like mesotherm, 31% of a mammal", "McNab 2009, p. 12187 (on Nagy's mammal line)", 4.82, 0.734, 0.31),
        ("Mammal, 4.82 M^0.734", "Nagy et al. 1999, Table 2, p. 260", 4.82, 0.734, 1.0),
        ("Bird (flying endotherms), 10.5 M^0.681", "Nagy et al. 1999, Table 2, p. 260", 10.5, 0.681, 1.0),
    ]
    for lab, src, a, b, sc in laws:
        k = mean_kcal(a, b, sc)
        add("Intake: field metabolic rate law", lab, src, coef(kcal_day=k), note=f"{k:,.0f} kcal/day averaged over all ages")
    for x in (1.7, 0.3):  # a species' true rate about its class-and-mass prediction (Nagy 2005, p. 1622)
        add("Intake: field metabolic rate law", f"The model's law, a species at {100 * x:.0f}% of it", "Nagy 2005, p. 1622: as low as 30%, as high as 170%",
            factor=1.0 / x)
    # 2. the guild's food weighting exponent b
    for b, src in ((0.6, "Carbone et al. 2007, p. 364: intake within large-prey hunters, 0.6 +/- 0.09"),
                   (0.66, "Carbone & Gittleman 2002, p. 2274: fitted, -0.66 (CI -0.48 to -0.85)"),
                   (0.75, "Kleiber; the model's value"),
                   (0.79, "Carbone et al. 2007, Table 1: intake across carnivores, 0.79 +/- 0.09"),
                   (0.85, "Carbone & Gittleman 2002, p. 2274: lower confidence limit"),
                   (0.889, "Nagy et al. 1999, eq. 32: the reptile exponent the dragons' own intake uses")):
        add("Guild weighting exponent", f"b = {b:g} (apex share {100 * apex_share(b):.1f}%)", src, coef(share=apex_share(b)))
    # 3. assimilation
    add("Assimilation", "85% (the model; unsourced)", "dragon_ages.ASSIMILATED", coef())
    add("Assimilation", "Nagy's conversion: 16.8 kJ/g dry matter at 30% dry matter", "Nagy et al. 1999, pp. 263-264",
        factor=(16.8 * 0.30) / (7.0 * DA.ASSIMILATED), note="5.04 kJ metabolised per g of fresh meat against the model's 5.95")
    add("Assimilation", "66%", "Carbone et al. 2007, p. 364", coef(assim=0.66))
    # 4. carcass use
    for u in (0.91, 0.78, 0.65):
        add("Share of a large carcass eaten", f"{100 * u:.0f}%", "Carbone et al. 2007, p. 367: 65% to 91% by prey mass", coef(carcass=u))
    # 5. offtake: the share of standing wild biomass the whole guild (peoples included) can take a year
    pb = sorted(COE_PB)
    for v, lab, src in ((0.05, "5% a year", "illustrative"), (0.10, "10% a year (the model; unsourced)", "megafauna.OFFTAKE"),
                        (0.136, "13.6%: Farlow's turnover at 1,000 kg", "Farlow 1993, eq. 6, p. 172"),
                        (0.165, "16.5%: Farlow's turnover at 500 kg", "Farlow 1993, eq. 6, p. 172"),
                        (float(np.median(pb)), f"{100 * np.median(pb):.1f}%: Coe's median production/biomass, 24 areas",
                         "Coe et al. 1976, Table 1, pp. 344-345"),
                        (pb[-1], f"{100 * pb[-1]:.1f}%: Coe's highest", "Coe et al. 1976, Table 1"),
                        (0.259, "25.9%: Farlow's turnover at 100 kg", "Farlow 1993, eq. 6, p. 172")):
        add("Yearly offtake", lab, src, coef(offtake=v), note="all of the production, the predators' best case" if v > 0.11 else "")
    # 6. the prey itself: McNaughton's NAP is above-ground; the model feeds whole-plant herb NPP (roots in). If the true above-ground
    # share is f, the prey is f^1.52 of the model's (slope 1.52, McNaughton et al. 1989, p. 143). f has no source on file.
    for f in (0.7, 0.5, 0.4):
        add("Prey: above-ground share of the NPP fed to the fit", f"f = {f:g} (prey x f^1.52)", "McNaughton et al. 1989, pp. 142-143; f itself unsourced",
            factor=f ** PR.PREY_EXP, note="scales prey, so density in every cell")
    return out


def combined() -> list[dict]:
    """A few joint cases (each a product of the rows' choices)."""
    k_meso = mean_kcal(4.82, 0.734, 0.31)
    k_var = mean_kcal(1.07, 0.735)
    k_mam = mean_kcal(4.82, 0.734)
    cases = [
        ("The model", {}),
        ("Literature-leaning mesotherm: McNab's 31%-of-mammal intake, 66% assimilation, 78% of a carcass eaten, b = 0.79, offtake at Coe's median",
         dict(kcal_day=k_meso, assim=0.66, carcass=0.78, share=apex_share(0.79), offtake=float(np.median(COE_PB)))),
        ("Lowest: mammal intake, 66% assimilation, 65% of a carcass, b = 0.6, 5% offtake",
         dict(kcal_day=k_mam, assim=0.66, carcass=0.65, share=apex_share(0.6), offtake=0.05)),
        ("Highest: varanid intake, 85% assimilation, whole carcass, b = 0.889, offtake at Farlow's 100 kg turnover",
         dict(kcal_day=k_var, share=apex_share(0.889), offtake=0.259)),
    ]
    return [{"label": lab, "factor": coef(**kw) / C0, "one_per_km2_at_1t": 1.0 / coef(**kw)} for lab, kw in cases]


def run() -> dict:
    return {"base_per_km2_per_t": C0, "base_one_per_km2_at_1t": 1.0 / C0, "base": BASE, "rows": rows(), "combined": combined(),
            "coe_pb": {"min": min(COE_PB), "median": float(np.median(COE_PB)), "max": max(COE_PB), "pooled": sum(COE_P) / sum(COE_B)},
            "mean_kcal": {"nagy_reptiles": mean_kcal(0.196, 0.889), "mcnab_varanid": mean_kcal(1.07, 0.735), "mesotherm_31": mean_kcal(4.82, 0.734, 0.31),
                          "mammal": mean_kcal(4.82, 0.734), "bird": mean_kcal(10.5, 0.681)},
            "fmr_at_eco_mass_kj": {k: a * (DS["eco_mass_kg"] * 1000) ** b for k, (a, b) in
                                   {"reptile": (0.196, 0.889), "mammal": (4.82, 0.734), "bird": (10.5, 0.681), "varanid_mcnab": (1.07, 0.735)}.items()}}


if __name__ == "__main__":
    r = run()
    for x in r["rows"]:
        print(f"{x['group'][:28]:28} {x['label'][:62]:62} x{x['factor']:6.3f}  1 per {x['one_per_km2_at_1t']:7.0f} km2  {x['note']}")
    for x in r["combined"]:
        print(f"x{x['factor']:6.3f} 1 per {x['one_per_km2_at_1t']:7.0f}  {x['label']}")
    print(json.dumps({k: r[k] for k in ("coe_pb", "mean_kcal", "fmr_at_eco_mass_kj")}, indent=1))
    if len(sys.argv) > 1:
        open(sys.argv[1], "w").write(json.dumps(r, indent=1))
