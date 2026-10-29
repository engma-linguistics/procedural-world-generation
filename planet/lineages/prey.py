"""Static prey: wild herbivore biomass from absolute NPP, livestock included (PW-966).

One field per cell, made once from the world's grazing NPP (gameattrs `grazing_npp`: the herb layer's NPP plus browse,
season-weighted, g C/m2/yr; forests hold less than savanna because forest NPP is mostly wood). There are no predator-prey cycles
(owner, 10-28: "just fit to what should work"). It feeds:
- the megafauna's natural density (history.megafauna: dragons on Carbone & Gittleman 2002's carnivores per prey biomass; checked: PDF p. 2);
- people density (PW-833, PW-974: density = way-of-life factor x f(absolute productivity); `people_fields` is that f).

**The fit.** McNaughton, Oesterheld, Frank & Williams 1989 (Nature 341:142-144, doi:10.1038/341142a0; PDF p. 142-143, checked): across
51 ecosystems, log10 B = 1.52 log10 NAP - 4.79 (r2 = 0.579, d.f. 49), B the herbivore biomass in kJ/m2 and NAP the net above-ground
primary productivity in kJ/m2/yr. The slope is above 1 (t = 2.80, per the coordinator's reading; not rechecked), so poor country holds
proportionally fewer herbivores than rich. The paper gives no conversion to mass or carbon: it says only that fluxes in mass were
turned to energy "using standard conversion factors" (its refs 41-43: Golley 1961, Schroeder 1977, Whitfield 1977; not on file). So the
three factors below are this module's own, each marked: carbon to dry matter (C_FRAC), dry plant to kJ (KJ_PER_G_DRY) and live animal
to kJ (KJ_PER_G_LIVE). With them 470 g C/m2/yr (a rich savanna, PW-966's anchor) gives ~7 t/km2, against PW-966's ~10: the paper's fit
and the old anchor agree to within the factors' uncertainty, so the paper's intercept is used outright. The scatter is wide (r2 0.58:
a factor of a few either way), and the fit is across ecosystems, not for one grazer guild. The model's grazing NPP (herb layer plus
browse, season-weighted) is not exactly McNaughton's NAP (above-ground, all plant parts, annual), a stated approximation. Coe, Cumming &
Phillipson 1976 (Oecologia 22:341, on file, read 2026-10-29) is not used but agrees: for twelve semi-arid African wildlife areas
(rain < 700 mm) it fits log10 B = 1.094 log10 NAAP + 0.389 (B kg/km2 live weight, NAAP g dry matter/m2/yr predicted from rainfall
by Rosenzweig 1968; r = 0.966; Fig. 3, p. 349), which at this module's C_FRAC gives ~0.8 / ~1.9 / ~4.9 t/km2 for the three anchors
below: a shallower slope (1.09 against 1.52) on a narrower range. With the fit, grazing NPP of 90 / 200 / 470 g C/m2/yr
(a hot desert's median / a steppe / a rich savanna) holds ~0.6 / ~1.9 / ~7 t/km2 of wild herbivores.

**Overkill.** Where small folk press the land (the megafauna pressure, history.megafauna.pressure) the wild big herbivores fall
to (1 - OVERKILL x pressure) of their potential, the late-Pleistocene pattern after people arrive (Sandom et al. 2014, Proc R Soc B
281:20133254; on file, read 2026-10-29: it counts the share of large-mammal SPECIES (>= 10 kg) lost per country, not biomass, and the
loss depends on how long the fauna lived beside hominins: median ~0.46 where modern humans were the first to arrive, ~0.23 where
archaic hominins were there before, near 0 in Africa (max 13%); Fig. 3, p. 5, and p. 6). Country hostile to small folk keeps them: tundra, high mountains and the sea (REFUGE), where frost,
cloud and storm giants herd or tend them (PW-724). Overkill never zeroes the prey (and never the dragons: livestock below).

**Livestock** counts as prey where peoples herd or farm (owner, 10-28: dragons take cattle-sized prey readily, later tribute and
kobold thralls). A people's way of life sets the share of its country stocked (LIVESTOCK), at the pasture's wild potential
(LIVESTOCK_X): a model assumption, not a fitted number.
"""

from __future__ import annotations

import numpy as np

# McNaughton et al. 1989, Nature 341:142 (PDF p. 142-143): log10 B = 1.52 log10 NAP - 4.79, B in kJ/m2, NAP in kJ/m2/yr. Checked.
PREY_EXP = 1.52  # the slope (log-log), checked against the PDF
PREY_LOG_A = -4.79  # the intercept, checked against the PDF
# Unit conversions, none from the paper (it cites "standard factors" without giving them). The first two are typical textbook values, unverified:
C_FRAC = 0.45  # g C per g dry plant matter (assumption: ~0.45-0.5 for plant tissue; unverified)
KJ_PER_G_DRY = 17.5  # kJ per g dry plant matter (assumption: ~17-20 for plant tissue; unverified, cf. Golley 1961, not on file)
KJ_PER_G_LIVE = 7.0  # kJ per g live weight of an animal: Farlow 1993, Am J Sci 293:167, p. 172 ("the energy content of animal tissue
# approximates 7 x 10^6 joules/kg live mass", citing Peters 1983, p. 33). Checked.
KJ_PER_G_C = KJ_PER_G_DRY / C_FRAC  # kJ of NAP per g C (~39)
OVERKILL = 0.6  # the share of the wild big herbivores lost where small folk press the land fully (a judgement, after Sandom et al. 2014,
# whose figure is species lost, not biomass, and varies with how long the fauna knew hominins: see the module docstring)
REFUGE = ("tundra", "mountain")  # places (history.tags) hostile to small folk, where the wild herds persist (and the sea)
LIVESTOCK = {"pastoral_nomad": 1.0, "transhumant": 0.9, "agro_pastoral": 0.8, "farmer": 0.5, "horticulturalist": 0.2}
# the share of a people's country stocked, by way of life (herders all of it; farmers keep draught, dairy and meat stock on part)
LIVESTOCK_X = 1.0  # stocked country carries livestock at the pasture's wild herbivore potential (t/km2)
HEAD_T = 0.5  # t live weight per head of cattle (PW-967: an ancient's ~100 head a year is ~50 t)


def wild(graze_npp: np.ndarray | None) -> np.ndarray | None:
    """Wild herbivore biomass, t/km2, per cell, from the grazing NPP (g C/m2/yr) by McNaughton's fit; None without a world."""
    if graze_npp is None:
        return None
    nap = np.maximum(np.asarray(graze_npp, float), 0.0) * KJ_PER_G_C  # kJ/m2/yr
    b_kj = 10.0 ** PREY_LOG_A * nap ** PREY_EXP  # kJ/m2 of herbivores
    return b_kj / KJ_PER_G_LIVE  # g/m2 live weight = t/km2


def refuge(tags: dict) -> np.ndarray:
    """Cells hostile to small folk where the wild herds persist (REFUGE, and every sea cell)."""
    r = ~tags["land"]
    for t in REFUGE:
        if t in tags:
            r = r | tags[t]
    return r


def herd_share(lines) -> np.ndarray:
    """Per line, the share of its country it stocks (LIVESTOCK by its way of life; megafauna and overlays none)."""
    return np.array([0.0 if (l.megafauna or l.overlay) else LIVESTOCK.get(l.way or "", 0.0) for l in lines])


def field(wild_t: np.ndarray, press: np.ndarray, refuge_mask: np.ndarray, stocked: np.ndarray | None = None) -> dict:
    """The prey per cell, t/km2: the wild herds after overkill (press 0..1, the peoples' pressure; none in refuge country), the
    livestock (stocked 0..1, the share of the cell stocked) and their sum."""
    w = wild_t * np.where(refuge_mask, 1.0, 1.0 - OVERKILL * np.clip(press, 0, 1))
    lv = wild_t * LIVESTOCK_X * np.clip(stocked, 0, 1) if stocked is not None else np.zeros_like(wild_t)
    return {"wild": w, "livestock": lv, "total": w + lv}


def stocked(P: np.ndarray, share: np.ndarray, est: float) -> np.ndarray:
    """Per cell, the share stocked with livestock: the peoples' presences (>= est) x their way's share, at most 1."""
    return np.clip(np.where(P >= est, P, 0.0).T @ share, 0, 1)


def productivity(wild_t: np.ndarray, land: np.ndarray) -> np.ndarray:
    """The wild prey over its median on the land with any (the giants' productivity factor, PW-833)."""
    sel = land & (wild_t > 0)
    ref = float(np.median(wild_t[sel])) if sel.any() else 1.0
    return wild_t / max(ref, 1e-9)


# People density reads the land's productivity (PW-974, PW-833: density = way-of-life factor x f(absolute NPP)). Each people's density
# is its way-of-life number (the spec's `density`) times f per cell, f = the layer / a fixed reference: absolute, so a poor planet holds
# fewer people than a rich one, not the same number spread differently. Herders read the grazing NPP (what their stock eats); foragers
# read the foraging layer (gameattrs `foraging`, 0-5: mast and fruit trees, game, wetlands, river fish), not the grazing, which
# undercounts a forest forager's food; farmers' soil is already in their habitat K, so their share reads nothing. f is linear in the
# layer: an assumption (Binford's forager densities rise with productivity over orders of magnitude, per the owner's PW-833 ruling;
# Binford 2001 is not on file, and the linear form is not from it). The two references are not physical constants: they are the
# layers' presence-weighted means over the country the peoples held on the 6 x 4 dnd sweep (rolls 7000-7003) with the factor off, so
# each way's mean density over that sweep stays at its number (docs/review/megafauna/people_density.py fits them).
FORAGE_REF = 2.6  # foraging score (0-5) at which a forager holds its way-of-life density
GRAZE_REF = 150.0  # grazing NPP, g C/m2/yr, at which a herder holds its way-of-life density


def people_fields(lines, shares_of, graze_npp: np.ndarray | None, forage: np.ndarray | None) -> np.ndarray | None:
    """Per line (L x cells), the productivity factor f of its density: its herding share reads the grazing NPP over GRAZE_REF, its
    wild-food share the foraging layer over FORAGE_REF, its farming share 1 (weighted by the shares). 1 for megafauna, overlays, marine
    peoples, fishers and lines whose way uses none of these goods. `shares_of(line)` is landuse.shares. None without a world."""
    if graze_npp is None or forage is None:
        return None
    fg = np.maximum(np.asarray(graze_npp, float), 0.0) / GRAZE_REF
    ff = np.maximum(np.asarray(forage, float), 0.0) / FORAGE_REF
    out = np.ones((len(lines), len(fg)))
    for k, l in enumerate(lines):
        if l.megafauna or l.overlay or l.marine or l.way in ("fisher_forager", "sea_nomad"):
            continue
        sh = shares_of(l)
        tot = sh["herd"] + sh["forage"] + sh["farm"]
        if tot > 0:
            out[k] = (sh["herd"] * fg + sh["forage"] * ff + sh["farm"]) / tot
    return out
