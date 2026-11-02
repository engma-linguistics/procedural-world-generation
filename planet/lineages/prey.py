"""Static prey: wild herbivore biomass from absolute NPP, livestock included (PW-966).

One field per cell, made once from the world's grazing NPP (gameattrs `grazing_npp`: the herb layer's NPP plus browse,
season-weighted, g C/m2/yr; forests hold less than savanna because forest NPP is mostly wood). There are no predator-prey cycles
(owner, 10-28: "just fit to what should work"). It feeds:
- the megafauna's natural density (history.megafauna: dragons on Carbone & Gittleman 2002's carnivores per prey biomass; checked: PDF p. 2);
- (people density read it until PW-1275; the density ladder, lineages.ladder, reads the world's NPP layers itself).

**The fit.** McNaughton, Oesterheld, Frank & Williams 1989 (Nature 341:142-144, doi:10.1038/341142a0; PDF p. 142-143, checked): across
51 ecosystems, log10 B = 1.52 log10 NAP - 4.79 (r2 = 0.579, d.f. 49), B the herbivore biomass in kJ/m2 and NAP the net above-ground
primary productivity in kJ/m2/yr. The slope is above 1 (t = 2.80, per the coordinator's reading; not rechecked), so poor country holds
proportionally fewer herbivores than rich. The paper gives no conversion to mass or carbon: it says only that fluxes in mass were
turned to energy "using standard conversion factors" (its refs 41-43: Golley 1961, Schroeder 1977, Whitfield 1977; not on file). So the
three factors below are this module's own, each marked: carbon to dry matter (C_FRAC), dry plant to kJ (KJ_PER_G_DRY) and live animal
to kJ (KJ_PER_G_LIVE). With them 470 g C/m2/yr (a rich savanna, PW-966's anchor) gives ~7 t/km2, against PW-966's ~10: the paper's fit
and the old anchor agree to within the factors' uncertainty, so the paper's intercept is used outright. The scatter is wide (r2 0.58:
a factor of a few either way), and the fit is across ecosystems, not for one grazer guild. The fit is above-ground only ("Only processes
occurring above ground were included", p. 142), while the model's NPP is whole-plant (vegetation's net includes the fine roots), so
the grazing NPP is cut to its above-ground part first (ABOVE, PW-1073, lane 90): the share of NPP below ground from Gherardi & Sala
2020 (PNAS 117:20038, PMC7443884; read 2026-10-31 on the PMC page): F-BNPP = 146 - 13.95 log(MAP) (Fig. 3 legend), "ranging from ~70%
in arid ecosystems to ~35% in humid ecosystems" (Results); grasslands average 64% (Table 1). The legend names neither the log's base
nor MAP's unit; the natural log with MAP in mm is the reading that reproduces their 70% and 35%, so that is the one used (a reading,
marked). With the fit's slope 1.52, a herd on open grassland is ~x0.25-0.4 of what the whole-plant input gave. Coe, Cumming &
Phillipson 1976 (Oecologia 22:341, on file, read 2026-10-29) is not used but agrees: for twelve semi-arid African wildlife areas
(rain < 700 mm) it fits log10 B = 1.094 log10 NAAP + 0.389 (B kg/km2 live weight, NAAP g dry matter/m2/yr predicted from rainfall
by Rosenzweig 1968; r = 0.966; Fig. 3, p. 349), which at this module's C_FRAC gives ~0.8 / ~1.9 / ~4.9 t/km2 for the three anchors
below: a shallower slope (1.09 against 1.52) on a narrower range. With the fit, grazing NPP of 90 / 200 / 470 g C/m2/yr
(a hot desert's median / a steppe / a rich savanna) holds ~0.6 / ~1.9 / ~7 t/km2 of wild herbivores.

**Overkill by how long the fauna knew people (PW-1000 B, owner 10-30; lane 90).** The loss is no longer one OVERKILL everywhere: it
follows how long the land's herds have lived beside small folk (`coevolved`), after Sandom et al.'s three classes of hominin history
(medians read off Fig. 3, p. 5: ~0.02 where hominins evolved, ~0.23 where archaic hominins came first, ~0.46 where modern humans were
the first; "universally low extinctions in sub-Saharan Africa (maximum 13%)", p. 6). They count species, not biomass: the largest go
first, so the biomass lost is more than the species share; meta.overkill (OVERKILL, 0.6, a judgement) stays the biomass loss where the
fauna is naive, and the other classes keep Sandom's ratios to it (x 0.23/0.46, x 0.02/0.46). The years that mark the classes are
judgements (COEVOL_KYR): Sandom et al. date the archaic arrival only as "possibly as early as the Late Pliocene or Early Pleistocene"
(p. 2), and the modern arrivals in the Americas and Australia are recent.

**Overkill (the old flat rule's text, still the form).** Where small folk press the land (the megafauna pressure, history.megafauna.pressure) the wild big herbivores fall
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
BNPP_A, BNPP_B = 146.0, 13.95  # Gherardi & Sala 2020, Fig. 3 legend: F-BNPP (%) = 146 - 13.95 log(MAP); read as ln, MAP in mm (docstring)
MAP_CLIP = (50.0, 5000.0)  # mm: the rainfall the fit is read over (its F stays within ~27%-91%); a guard, not from the paper
# Sandom et al. 2014 Fig. 3 p. 5, medians: the share of large-mammal species lost by how long hominins and the fauna lived together
SANDOM_LOSS = (0.46, 0.23, 0.02)  # (modern humans first: naive fauna; archaic hominins first; where hominins evolved)
COEVOL_KYR = (50.0, 1000.0, 3000.0)  # the years beside small folk that stand for those three classes (judgements; log-interpolated between)
OVERKILL = 0.6  # the share of the wild big herbivores lost where small folk press the land fully (a judgement, after Sandom et al. 2014,
# whose figure is species lost, not biomass, and varies with how long the fauna knew hominins: see the module docstring)
REFUGE = ("tundra", "mountain")  # places (history.tags) hostile to small folk, where the wild herds persist (and the sea)
LIVESTOCK = {"pastoral_nomad": 1.0, "transhumant": 0.9, "agro_pastoral": 0.8, "farmer": 0.5, "horticulturalist": 0.2}
# the share of a people's country stocked, by way of life (herders all of it; farmers keep draught, dairy and meat stock on part)
LIVESTOCK_X = 1.0  # stocked country carries livestock at the pasture's wild herbivore potential (t/km2)
HEAD_T = 0.5  # t live weight per head of cattle (PW-967: an ancient's ~100 head a year is ~50 t)


# Sea prey (D28 B, owner 10-31; lane 99): the coast and ice dragons' food from the sea, the seals and other marine mammals, from the
# ocean's primary production up the food chain. Read 2026-10-31 (docs/review/dragon-numbers/report.md, "Sea food"):
# - primary production by province, g C/m2/yr: open ocean 50, coastal waters to 180 m 100, upwelling 300 (Ryther 1969, Science 166:72,
#   Table 1, as quoted by Pauly 1996, Fish Res 25:25, sec. 5; the original not read). Later estimates run 1.4-2.6x higher (Martin et al.
#   1987, via a NOAA-SWFSC 1988 review): a low reading, marked.
# - transfer efficiency between trophic levels 10% (Pauly & Christensen 1995, Nature 374:255, as summarised by FishBase; Chassot et al.
#   2010, Ecol Lett 13:495, p. 497 use 10% for temperate systems, 5% upwelling, 14% tropical); one figure, a simplification.
# - the prey's trophic level 4.0: harbour, larga and grey seals (Pauly, Trites, Capuli & Christensen 1998, ICES J Mar Sci 55:467,
#   Table 2; the pinnipeds run 3.8-4.4).
# - the marine mammals' share of the primary production: they need 20-30 g C/m2/yr of it in every FAO area of the Pacific (Trites,
#   Christensen & Pauly 1997, J Northw Atl Fish Sci 22:173, text and Fig. 4: "a very narrow range of 20 to 30 g C per m2 per year"), of a Pacific mean 135 (Table 1): 25 / 135.
# - wet weight 9 g per g C (Chassot et al. 2010 and Stock et al. 2017, PNAS 114:1441, both after Strathmann 1967).
# So the marine mammals' production, t wet/km2/yr = MM_SHARE x NPP x TE^(TL - 1) x WET_PER_C: ~0.17 over a shelf at 100 g C.
SEA_NPP = (50.0, 100.0, 300.0)  # g C/m2/yr: open ocean, shelf, upwelling (Ryther 1969 Table 1, via Pauly 1996)
SEA_SHELF_M = (1500.0, 300.0)  # a sea cell's mean depth, m: deep sea from the first, shelf under the second (as seafood.SHELF_M: a 60 km cell)
SEA_UPWELL = (0.5, 3.0)  # C of upwelling cooling at which a sea is an upwelling province, from none to full (as coastform.PROD_UPWELL)
SEA_TE = 0.10  # transfer efficiency per trophic level (Pauly & Christensen 1995)
SEA_TL = 4.0  # the prey's trophic level (seals: Pauly et al. 1998)
MM_SHARE = 25.0 / 135.0  # the marine mammals' share of the primary production (Trites et al. 1997)
WET_PER_C = 9.0  # g wet weight per g C (Strathmann 1967, via Chassot et al. 2010)


def sea_npp(layers: dict, grid=None) -> np.ndarray | None:
    """Ocean net primary production, g C/m2/yr, per sea cell (0 on land), from a world's layers: Ryther's open-ocean figure, his coastal
    one over the shelf (the cell's mean depth, SEA_SHELF_M) and his upwelling one where the sea upwells (SEA_UPWELL); under perennial
    sea ice x (1 - 0.8 x ramp(the year's ice share, 0.6, 0.98)), coastform's own cut for its sea production (with the grid and the
    month layers; a judgement: the ice-edge blooms and the seals' ice are kept, the closed pack is not). None without elevation."""
    if "elevation" not in layers:
        return None
    from ..geo import is_land
    elev = np.asarray(layers["elevation"], float)
    sea = ~is_land(elev, layers.get("ice"), grid)  # (the sea that reaches the ocean: not inland pits below 0 m, PW-1229)
    depth = np.where(sea, -elev, 0.0)
    a, b = SEA_SHELF_M
    shelf = np.clip((a - depth) / (a - b), 0.0, 1.0)
    up = np.asarray(layers["upwelling"], float) if "upwelling" in layers else np.zeros_like(elev)
    u = np.clip((up - SEA_UPWELL[0]) / (SEA_UPWELL[1] - SEA_UPWELL[0]), 0.0, 1.0)
    base = SEA_NPP[0] + (SEA_NPP[1] - SEA_NPP[0]) * shelf
    npp = np.where(sea, base + (SEA_NPP[2] - base) * u, 0.0)
    if grid is not None and "warm_month" in layers and "cold_month" in layers:
        from .. import coast as CO
        from ..geo import ramp
        ice_y = CO.sea_ice_share(grid, elev, {"t_warm": np.asarray(layers["warm_month"], float),
                                                   "t_cold": np.asarray(layers["cold_month"], float)}, layers.get("ice")).mean(0)
        npp = npp * (1.0 - 0.8 * ramp(ice_y, 0.6, 0.98))
    return npp


def sea_prey(npp: np.ndarray | None) -> np.ndarray | None:
    """The marine mammals' production, t wet/km2/yr, per cell, from the ocean's NPP (g C/m2/yr): MM_SHARE x NPP x SEA_TE^(SEA_TL - 1)
    x WET_PER_C (g/m2 = t/km2)."""
    if npp is None:
        return None
    return MM_SHARE * np.asarray(npp, float) * SEA_TE ** (SEA_TL - 1.0) * WET_PER_C


def above(rain_mm) -> np.ndarray:
    """The above-ground share of NPP at an annual rainfall (mm): 1 - F-BNPP (Gherardi & Sala 2020, PW-1073)."""
    r = np.clip(np.asarray(rain_mm, float), *MAP_CLIP)
    return 1.0 - np.clip(BNPP_A - BNPP_B * np.log(r), 0.0, 100.0) / 100.0


def wild(graze_npp: np.ndarray | None, rain_mm: np.ndarray | None = None) -> np.ndarray | None:
    """Wild herbivore biomass, t/km2, per cell, from the grazing NPP (g C/m2/yr, whole-plant) by McNaughton's fit, its above-ground
    part only (`above`, at the annual rain; without rain, the grassland mean of Gherardi & Sala's Table 1, 1 - 0.64); None without a world."""
    if graze_npp is None:
        return None
    f = above(rain_mm) if rain_mm is not None else 1.0 - 0.64
    nap = np.maximum(np.asarray(graze_npp, float), 0.0) * f * KJ_PER_G_C  # kJ/m2/yr above ground
    b_kj = 10.0 ** PREY_LOG_A * nap ** PREY_EXP  # kJ/m2 of herbivores
    return b_kj / KJ_PER_G_LIVE  # g/m2 live weight = t/km2


def coevolved_loss(years_kyr) -> np.ndarray:
    """The overkill's share of meta.overkill by the years (kyr) the fauna has lived beside small folk: SANDOM_LOSS over its naive value,
    log-interpolated over COEVOL_KYR (1 for a newly reached land, ~0.5 after a million years, ~0.04 where small folk evolved)."""
    t = np.log10(np.maximum(np.asarray(years_kyr, float), COEVOL_KYR[0]))
    return np.interp(t, np.log10(COEVOL_KYR), np.array(SANDOM_LOSS) / SANDOM_LOSS[0])


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


def field(wild_t: np.ndarray, press: np.ndarray, refuge_mask: np.ndarray, stocked: np.ndarray | None = None, overkill=OVERKILL) -> dict:
    """The prey per cell, t/km2: the wild herds after overkill (overkill: a number or per cell, `coevolved_loss` x meta.overkill;
    press 0..1, the peoples' pressure; none in refuge country), the
    livestock (stocked 0..1, the share of the cell stocked) and their sum."""
    w = wild_t * np.where(refuge_mask, 1.0, 1.0 - overkill * np.clip(press, 0, 1))  # (overkill: meta.overkill, default OVERKILL)
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
