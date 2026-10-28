"""Static prey: wild herbivore biomass from absolute NPP, livestock included (PW-966).

One field per cell, made once from the world's grazing NPP (gameattrs `grazing_npp`: the herb layer's NPP plus browse,
season-weighted, g C/m2/yr; forests hold less than savanna because forest NPP is mostly wood). There are no predator-prey cycles
(owner, 10-28: "just fit to what should work"). It feeds:
- the megafauna's natural density (history.megafauna: dragons on Carbone & Gittleman 2002's carnivores per prey biomass);
- people density later (PW-833: density = way-of-life factor x f(absolute NPP); `productivity` is that f, not yet read).

**The fit.** Wild herbivore biomass is taken proportional to the grazing NPP, through PW-966's rich-savanna anchor: ~10 t/km2 at a
savanna's ~470 g C/m2/yr (the model's savanna median on world 2a7385). The slope is 1, the plainest assumption. McNaughton et
al. 1989 (Nature 341:142) and Coe, Cumming & Phillipson 1976 (Oecologia 22:341) are the published fits to put here; neither is on
file yet (docs/references/megafauna/README.md), so their coefficients are not used. With this anchor the model's biome medians
give temperate forest ~0.3, boreal ~0.6, tundra ~1.3, temperate grassland ~5.7 and savanna ~10 t/km2.

**Overkill.** Where small folk press the land (the megafauna pressure, history.megafauna.pressure) the wild big herbivores fall
to (1 - OVERKILL x pressure) of their potential, the late-Pleistocene pattern after people arrive (Sandom et al. 2014, Proc R Soc B
281:20133254; not on file). Country hostile to small folk keeps them: tundra, high mountains and the sea (REFUGE), where frost,
cloud and storm giants herd or tend them (PW-724). Overkill never zeroes the prey (and never the dragons: livestock below).

**Livestock** counts as prey where peoples herd or farm (owner, 10-28: dragons take cattle-sized prey readily, later tribute and
kobold thralls). A people's way of life sets the share of its country stocked (LIVESTOCK), at the pasture's wild potential
(LIVESTOCK_X): a model assumption, not a fitted number.
"""

from __future__ import annotations

import numpy as np

PREY_G_REF = 470.0  # g C/m2/yr of grazing NPP at the anchor (a rich savanna; the model's savanna median on 2a7385)...
PREY_T_REF = 10.0  # ...and its wild herbivore biomass, t/km2 (PW-966's rich-savanna example)
PREY_EXP = 1.0  # biomass ~ grazing NPP^PREY_EXP (1: proportional; a published slope to replace it, see the module note)
OVERKILL = 0.6  # the share of the wild big herbivores lost where small folk press the land fully (a judgement, after Sandom et al. 2014)
REFUGE = ("tundra", "mountain")  # places (history.tags) hostile to small folk, where the wild herds persist (and the sea)
LIVESTOCK = {"pastoral_nomad": 1.0, "transhumant": 0.9, "agro_pastoral": 0.8, "farmer": 0.5, "horticulturalist": 0.2}
# the share of a people's country stocked, by way of life (herders all of it; farmers keep draught, dairy and meat stock on part)
LIVESTOCK_X = 1.0  # stocked country carries livestock at the pasture's wild herbivore potential (t/km2)
HEAD_T = 0.5  # t live weight per head of cattle (PW-967: an ancient's ~100 head a year is ~50 t)


def wild(graze_npp: np.ndarray | None) -> np.ndarray | None:
    """Wild herbivore biomass, t/km2, per cell, from the grazing NPP (g C/m2/yr); None without a world."""
    if graze_npp is None:
        return None
    return PREY_T_REF * (np.maximum(np.asarray(graze_npp, float), 0.0) / PREY_G_REF) ** PREY_EXP


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
    """f(absolute NPP) for people density (PW-833, not yet read): the wild prey over its median on the land with any."""
    sel = land & (wild_t > 0)
    ref = float(np.median(wild_t[sel])) if sel.any() else 1.0
    return wild_t / max(ref, 1e-9)
