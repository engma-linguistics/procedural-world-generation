"""Published ranges as optional random draws (PW-1383, Daniel 11-02: "when we have ranges published can we utilize those as a
(optionally) random selector for that variable?").

Where a density-ladder number has a source that gives a range, the range is written here, beside its source, and with the setting
`meta.draw_ranges = true` each peoples run draws the number from it instead of using the fixed value (ladder.py's constants, which
stay the fixed values and the default). Off, nothing here is read and the run is bit-identical to before.

Only ranges the write-ups cite (docs/review/peoples/density-ladder/ladder.md, rich-foragers.md) are listed: the endpoints are those
documents' own, never read from memory. A constant whose source gives only one number, or a judgement, is in FIXED with the reason,
and is never drawn.

**The draw.** One number per name from numpy's generator seeded (peoples seed = meta.seed, 1383, crc32 of the name's group), so a
world's draws are the same every time, differ between seeds, and do not depend on how many other names exist. Densities that the
sources span over a factor of 7 or more are drawn **log-uniform** (equal chance per doubling: a source's "2-20" is not "mostly near
11"; the geometric mean sits near the central value the ladder uses); the narrow ones (a slope 1.26-1.28, a time 0.6-1 kyr) uniform.
Names in one `group` share one draw (u in 0..1), so the three plough stages stay in order: each is lo x (hi/lo)^u, and the stages'
ranges rise at both ends, so a high draw is high for all of them.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass

import numpy as np

SALT = 1383


@dataclass(frozen=True)
class Range:
    lo: float
    hi: float
    log: bool  # log-uniform (True) or uniform
    group: str  # names sharing a group share one draw
    source: str  # where the range is published (ladder.md / rich-foragers.md; the sources they read)


RANGES: dict[str, Range] = {
    "forager_pow": Range(1.26, 1.28, False, "forager_pow",
                         "Binford 2001 Table 5.01 via D-PLACE: terrestrial fit slope 1.26, all foragers 1.28 (ladder.md, forager rows)"),
    "fish_top": Range(0.3, 2.0, True, "fish_top",
                      "fishing foragers 0.3-2 /km2 (ladder.md summary; Binford sedentary and fishing-led, Kelly 2013 Table 7-3 Northwest "
                      "Coast 0.1-2). The rich-coast California tail to ~9 is left out: one region's whole-range figure"),
    "garden": Range(2.0, 20.0, True, "garden",
                    "gardeners ~2-20 /km2 (ladder.md summary and TABLE: Boserup fallow classes, PNG). PNG's 5-40 by land quality is not "
                    "added: the ladder already scales a rung by the land's NPP"),
    "plough_0": Range(2.5, 14.0, True, "plough",
                      "Early Bronze Age Greece 2.5-14 /km2 (Renfrew 1972, Lukermann, Angel, via Butzer 1976 pp. 82-84)"),
    "plough_1": Range(10.8, 17.9, True, "plough",
                      "Roman Rhineland west of the Rhine 10.8-17.9 /km2 (Zimmermann et al. 2009 PPS, read)"),
    "plough_2": Range(13.0, 35.0, True, "plough",
                      "England 1086 ~13 to the 1315-1348 peak ~35 /km2 (Broadberry, Campbell & van Leeuwen 2011; densities are ladder.md's arithmetic)"),
    "nomad": Range(0.35, 2.0, True, "nomad",
                   "Mongolia ~0.35 (c. 1911) to ~0.54 (1956); Kenya's driest districts modelled 1-2 /km2 (ladder.md pastoral row)"),
    "rich_t": Range(0.6, 1.0, False, "rich_t",
                    "moderately rich coasts took up farming within ~0.6 kyr (Yayoi rice to southern Tohoku, Mizoguchi) to ~1 kyr (Ertebolle "
                    "beside farmers, Gron; rich-foragers.md, RICH_T)"),
}

FIXED: dict[str, str] = {
    "FORAGER (0.036 at NPP 330)": "fixed: no published range at the reference land. Binford's spans (hunting-led 0.01-0.044, gathering "
                                  "0.036-0.33, all 0.11 median) are across all land qualities; at one NPP the scatter around the fit is "
                                  "not given (r 0.55). Only the fit's slope is drawn",
    "FISH_MIN (0.2)": "fixed: a judgement (Kelly p. 46 is the idea), no range",
    "PLOUGH_TOP (35)": "fixed: England's medieval peak 35-36 (a point; Broadberry et al.), no range to speak of",
    "PLOUGH_STEPS (0, 3.2, 5.3 kyr)": "fixed: tech-tree dates (techtree.toml), not a density",
    "IRR (30 ... 240 per watered km2)": "fixed: Butzer 1976 Table 4 is one 'hypothetical' series; the other figures (delta 10-135, "
                                        "nomes median 172 up to 500, 1882 census 240-280) are other places and measures, not a range for it",
    "IRR_LAG, TERRACE_LAG": "fixed: tech-tree dates",
    "WATER_FLOW, WATER_MAX, FARM_FULL": "fixed: judgements",
    "DEN_FARM_W, RAID_CAP, RAID_HALF, RAID_REACH": "fixed: judgements; no measured raiding share was found (ladder.md, Raiding)",
    "TRADE_CAP, TRADE_FULL": "fixed: a placeholder until trade exists",
    "MUSHROOM_X (0.1)": "fixed: derived (~520 kcal a kg of straw against 1,800-2,600 in a kg of wheat), a bonus not a sourced range",
    "RICH_HALF (3)": "fixed: a judgement. The only range near it, richness 7-16 for the Calusa, is the case's, not the constant's",
    "RICH_POW, HERD_POW": "fixed: judgements (the steepness)",
    "agro-pastoral rung": "fixed: no constant of its own; it mixes the farm and herd rungs (Wilson 6-14, Kalff 1-2 to ~200 are modelled ranges "
                          "that no constant reads)",
    "kind factor 0.8-1.2": "fixed: an owner ruling (PW-1350), not a published range",
    "dens.py scores (KARST ... SOIL_M)": "fixed: judgements on the sources (dens/round1.md); none gives a range for a score",
}


def draw(seed: int) -> dict[str, float]:
    """Every ranged name's value for a peoples seed: uniform or log-uniform in its range, one draw per group (see the module docstring)."""
    us = {}
    for g in sorted({r.group for r in RANGES.values()}):
        us[g] = float(np.random.default_rng((int(seed), SALT, zlib.crc32(g.encode()))).random())
    out = {}
    for k, r in RANGES.items():
        u = us[r.group]
        out[k] = r.lo * (r.hi / r.lo) ** u if r.log else r.lo + (r.hi - r.lo) * u
    return out


def table() -> list[dict]:
    """The ranges as rows (name, lo, hi, scale, source) for the write-up and the metadata."""
    return [{"name": k, "lo": r.lo, "hi": r.hi, "scale": "log" if r.log else "linear", "group": r.group, "source": r.source}
            for k, r in RANGES.items()]
