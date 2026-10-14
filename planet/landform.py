"""Landform classes: what kind of country each cell is, read from its
geological record (tectonics/record.py: the strata in order, when the crust
rifted, folded, how far it was exhumed) and its setting now (land or sea,
the coast, the climate, the volcanoes). The regional zoom (PW-010..012)
synthesises terrain to match: a great escarpment steps up to a plateau, a
fold belt has parallel ridges, a shield has domes and inselbergs.

Every class comes from recorded history, not from elevation or noise. The
rules (classify, in priority order: a cell takes the first that holds):

  arc            land within a cell of an arc volcano (the volcano table:
                 active, or extinct for at most 20 Myr)
  hotspot        oceanic land: an ocean-island volcano, or within a cell
                 of a hotspot vent standing above the sea (on a continent
                 a plume's lava makes a lava plateau instead)
  rift           continental land stretched by a rift in the last
                 RIFT_MYR, by at least RIFT_STRAIN (ln beta) (fault blocks
                 and grabens: East Africa, Basin and Range)
  escarpment     continental land on a rifted margin (rifted
                 ESCARPMENT_MYR ago), where the escarpment has retreated to
                 by now: retreat_km(rift age) from the rifted coast (one
                 stretched by at least RIFT_STRAIN), if
                 that coast is still passive (the sea floor off it rides
                 on the same plate) and there is a plateau to step up to
                 (at least ESCARPMENT_M) (Drakensberg, Western Ghats, Serra
                 do Mar)
  fold belt      the exposed strata predate the cell's last folding (a
                 collision or an accretionary wedge) and at least
                 FOLD_MIN_KM of folded cover is left (Zagros, Valley and
                 Ridge)
  lava plateau   flood basalt at the top, at least TRAPS_MIN_KM (Deccan,
                 Columbia River)
  dune field     sandstone or sand-rich cover at the top in a hyper-arid
                 (< DUNES_MM) lowland (ergs: Rub' al Khali)
  karst          at least KARST_MIN_KM of limestone or dolomite at the top
                 in a wet (> KARST_MM), unfrozen climate
  caprock        flat-lying, exposed (not grown for EXPOSED_MYR) hard rock
                 (limestone, dolomite, sandstone, quartzite, basalt) over
                 soft (shale, evaporite, coal, tuff): mesas, cuestas,
                 stepped plateaus (Colorado Plateau, Niagara)
  coastal plain  low (< COASTAL_M), flat-lying sediment still being laid
                 down or just emerged (COASTAL_MYR), near the coast
                 (Gulf coastal plain)
  shield         old (> SHIELD_MYR) craton or granite basement exposed,
                 not folded for SHIELD_QUIET_MYR nor rifted for
                 SHIELD_QUIET_MYR / 3 (Canadian Shield, the African
                 shields: domes, inselbergs)
  hills          any other land: the zoom's graded hills and mountains

The parameters the zoom needs come along per cell (layers()):
  landform_age     Myr, by class: since rifting (rift, escarpment: sets
                   the retreat), folding (fold belt), eruption (lava
                   plateau, arc, hotspot), the top stratum last grew
                   (dunes, karst, caprock, coastal plain), the basement
                   formed (shield); 0 for hills
  strata_top       surface.ROCKS id exposed (the first stratum thicker
                   than VENEER_KM, else the basement)...
  strata_top_km    ...its thickness (0: basement)...
  strata_next      ...and what's under it (next stratum or the basement)
  strata_dip       deg: folded strata dip by how hard they were squeezed
                   (fold_dip); flat ones by the regional slope
  fold_wavelength  km between fold crests, from the folded pile's
                   thickness (fold_wavelength; 0 where not folded)
"""

from __future__ import annotations

import numpy as np

from . import kernels
from .geo import R_KM, xyz
from .surface import (ARC, COAL, CRATON, DOLOMITE, EVAPORITE, FLOOD_BASALT, GRANITE, HOTSPOT, LIMESTONE, QUARTZITE,
                      SANDSTONE, SHALE, TUFF)
from .tectonics import record as R
from .tectonics.isostasy import MIX, SAND

# id, key, name, colour, what landform_age measures
CLASSES = [
    (0, "sea", "sea", "#1c2f4f", ""),
    (1, "hills", "hills and mountains (graded)", "#9a9a7a", ""),
    (2, "shield", "old shield (granite domes, inselbergs)", "#b07a5a", "basement age"),
    (3, "fold_belt", "fold-and-thrust belt (parallel ridges)", "#8e5fb0", "since folding"),
    (4, "rift", "fault-block rift (tilted blocks, grabens)", "#e05a3a", "since rifting"),
    (5, "escarpment", "great escarpment (rifted margin)", "#f0a020", "since rifting"),
    (6, "caprock", "caprock plateau and cuestas", "#d8c060", "since the caprock last grew"),
    (7, "lava_plateau", "lava plateau (traps)", "#5a4a5e", "since the eruption"),
    (8, "karst", "karst (carbonate)", "#6fc0c8", "since the carbonate last grew"),
    (9, "dunes", "dune field (erg)", "#f2dc9a", "since the sand last grew"),
    (10, "coastal_plain", "coastal plain", "#8fc07a", "since the top stratum last grew"),
    (11, "arc", "volcanic arc", "#d1495b", "age of the nearest volcano"),
    (12, "hotspot", "hotspot volcano / island", "#a83250", "age of the nearest vent"),
]
(SEA, HILLS, SHIELD, FOLD_BELT, RIFT, ESCARPMENT, CAPROCK, LAVA_PLATEAU, KARST, DUNES, COASTAL_PLAIN, ARC_CLASS,
 HOTSPOT_CLASS) = range(len(CLASSES))

LAYERS = ("landform", "landform_age", "strata_top", "strata_top_km", "strata_next", "strata_dip", "fold_wavelength")

VENEER_KM = 0.02  # strata thinner than this are looked through (a veneer of soil or alluvium)
HARD = (LIMESTONE, DOLOMITE, SANDSTONE, QUARTZITE, FLOOD_BASALT)
SOFT = (SHALE, EVAPORITE, COAL, TUFF)
CARBONATE = (LIMESTONE, DOLOMITE)
RIFT_MYR = 20.0
RIFT_STRAIN = 0.2  # ln(beta): crust thinned by ~18%
ESCARPMENT_MYR = (8.0, 400.0)
ESCARPMENT_M = 300.0
FOLD_MIN_KM = 0.2
TRAPS_MIN_KM = 0.2
DUNES_MM, DUNES_SAND, DUNES_MAX_M = 150.0, 0.35, 1500.0
KARST_MIN_KM, KARST_MM = 0.4, 700.0
CAP_KM = (0.03, 1.5)
EXPOSED_MYR = 10.0
COASTAL_M, COASTAL_MYR, COASTAL_KM = 300.0, 30.0, 400.0
SHIELD_MYR = 500.0
SHIELD_QUIET_MYR = 300.0


def retreat_km(age):
    """How far a great escarpment has retreated inland from its rifted
    coast, rift_age Myr after breakup: fast at first, then slowing as the
    rivers that cut back into it shrink (Drakensberg ~150 km in ~180 Myr,
    Western Ghats ~60-80 km in ~65 Myr)."""
    return 200.0 * (1 - np.exp(-np.maximum(age, 0) / 150.0))


def fold_dip(strain_km):
    """deg: the steeper, the more crust was stacked onto the cell in its
    folding episode (gentle open folds to steep, tight ones)."""
    return 8.0 + 52.0 * (1 - np.exp(-np.maximum(strain_km, 0) / 20.0))


def fold_wavelength(fold_km):
    """km between fold crests: ~1.5x the folded pile's thickness (detachment
    folds; Zagros ~10-15 km over ~6-12 km of cover), 3-30 km."""
    return np.clip(1.5 * fold_km + 2.0, 3.0, 30.0)


def near_volcanoes(grid, rows, keep):
    """Cells within a cell of the volcanoes rows[keep] (rows: the volcano
    table, tectonics.volcanism.COLUMNS) and the youngest such volcano's age
    per cell (inf elsewhere)."""
    age = np.full(grid.n, np.inf)
    sel = [r for r, k in zip(rows, keep) if k]
    if not sel:
        return age
    a = np.array(sel, float)
    c = grid.locate(xyz(np.radians(a[:, 0]), np.radians(a[:, 1])))
    np.minimum.at(age, c, a[:, 3])
    deg = np.diff(grid.nbr_off)
    src = np.repeat(np.arange(grid.n), deg)
    np.minimum.at(age, grid.nbr_idx, age[src])
    return age


def coast_km(grid, land, sources):
    """km from each land cell's centre to the nearest coast among the
    coastal land cells `sources` (inf where unreached), over land."""
    d, _ = kernels.bfs_within(np.flatnonzero(sources), land.astype(np.int64), grid.nbr_off, grid.nbr_idx, 10**6)
    km = (d + 0.5) * grid.spacing * R_KM
    return np.where(d >= 0, km, np.inf)


def regional_dip(grid, elev):
    """deg: the regional slope of the land (mean drop to lower neighbours
    over the cell spacing), the tilt flat-lying strata get from it."""
    h = np.maximum(elev, 0.0)
    deg = np.diff(grid.nbr_off)
    src = np.repeat(np.arange(grid.n), deg)
    drop = np.maximum(h[src] - h[grid.nbr_idx], 0)
    mean = np.bincount(src, drop, grid.n) / deg
    return np.degrees(np.arctan(mean / (grid.spacing * R_KM * 1000.0)))


def classify(grid, t, elev, cont, rock, cover, mix, rec, lith, crust_age, precip, temp, volcanoes,
             plate=None) -> dict:
    """The landform layers (LAYERS) for one moment. elev: m above sea level;
    rock: basement; mix: the cover's isostasy.MIX columns; rec, lith: the
    record (world view); crust_age: Myr; precip mm/yr, temp C; volcanoes:
    the volcano table (rows of tectonics.volcanism.COLUMNS); plate: which
    plate each cell is on (None: all one)."""
    from .tectonics.volcanism import ARC as V_ARC, VENT
    n = grid.n
    land = elev > 0
    top, top_km, folded, top_t, below = R.top(rec, lith, rock, VENEER_KM)
    age_top = t - top_t
    t_rift, t_fold = rec[:, R.T_RIFT], rec[:, R.T_FOLD]
    rifted, folded_ever = t_rift > R.NEVER / 2, t_fold > R.NEVER / 2
    cls = np.where(land, HILLS, SEA).astype(np.uint8)
    age = np.zeros(n)
    free = land.copy()

    def claim(mask, k, a):
        m = mask & free
        cls[m] = k
        age[m] = np.broadcast_to(a, (n,))[m]
        free[m] = False

    vrows = volcanoes or []
    v_arc = near_volcanoes(grid, vrows, [r[2] == V_ARC for r in vrows])
    claim(np.isfinite(v_arc), ARC_CLASS, v_arc)
    v_hot = near_volcanoes(grid, vrows, [r[2] == VENT and r[5] > 0 for r in vrows])
    claim(~cont & (np.isfinite(v_hot) | (rock == HOTSPOT)), HOTSPOT_CLASS,
          np.where(np.isfinite(v_hot), v_hot, crust_age))

    rift_age = t - t_rift
    stretched = rifted & (rec[:, R.RIFT_STRAIN] >= RIFT_STRAIN)
    claim(cont & stretched & (rift_age <= RIFT_MYR), RIFT, rift_age)
    coast = land & (np.add.reduceat((~land)[grid.nbr_idx], grid.nbr_off[:-1]) > 0)
    plate = np.zeros(n, np.int64) if plate is None else np.asarray(plate)
    src = np.repeat(np.arange(n), np.diff(grid.nbr_off))
    passive = np.add.reduceat(~land[grid.nbr_idx] & (plate[grid.nbr_idx] == plate[src]), grid.nbr_off[:-1]) > 0
    d_rift = coast_km(grid, land, coast & stretched & passive)
    w = 0.75 * grid.spacing * R_KM
    esc = cont & rifted & (rift_age >= ESCARPMENT_MYR[0]) & (rift_age <= ESCARPMENT_MYR[1])
    claim(esc & (np.abs(d_rift - retreat_km(rift_age)) <= w) & (elev >= ESCARPMENT_M), ESCARPMENT, rift_age)

    folded_km = np.where(folded, cover, 0.0)  # the exposed stratum and all below it predate the folding
    claim(folded & (folded_km >= FOLD_MIN_KM), FOLD_BELT, t - t_fold)
    claim((top == FLOOD_BASALT) & (top_km >= TRAPS_MIN_KM), LAVA_PLATEAU, age_top)
    sand = (mix[:, SAND - MIX.start] / np.maximum(cover, 1e-9) >= DUNES_SAND) & (cover > VENEER_KM)
    claim((precip < DUNES_MM) & ((top == SANDSTONE) | sand) & (elev < DUNES_MAX_M), DUNES, age_top)
    claim(np.isin(top, CARBONATE) & (top_km >= KARST_MIN_KM) & (precip > KARST_MM) & (temp > 0), KARST, age_top)
    cap = (np.isin(top, HARD) & ~folded & np.isin(below, SOFT) & (top_km >= CAP_KM[0]) & (top_km <= CAP_KM[1])
           & (age_top >= EXPOSED_MYR))
    claim(cap, CAPROCK, age_top)
    d_coast = coast_km(grid, land, coast)
    young = np.isin(top, (SANDSTONE, SHALE)) & ~folded & (age_top <= COASTAL_MYR)
    claim(young & (elev < COASTAL_M) & (d_coast <= COASTAL_KM), COASTAL_PLAIN, age_top)
    quiet = (t - np.where(folded_ever, t_fold, -np.inf) >= SHIELD_QUIET_MYR) & (
        t - np.where(stretched, t_rift, -np.inf) >= SHIELD_QUIET_MYR / 3)
    claim(cont & (top_km == 0) & np.isin(rock, (CRATON, GRANITE)) & (crust_age >= SHIELD_MYR) & quiet,
          SHIELD, crust_age)

    dip = np.where(folded, fold_dip(rec[:, R.FOLD_STRAIN]), regional_dip(grid, elev))
    return {"landform": cls, "landform_age": np.round(np.maximum(age, 0)),
            "strata_top": top, "strata_top_km": np.where(land | (cover > 0), top_km, 0.0), "strata_next": below,
            "strata_dip": dip, "fold_wavelength": np.where(folded, fold_wavelength(rec[:, R.FOLD_KM]), 0.0)}


def legend() -> list[dict]:
    """The class ids -> names and colours, as runs and worlds store them."""
    return [{"id": c[0], "key": c[1], "name": c[2], "color": c[3], "age": c[4]} for c in CLASSES]


def shares(landform: np.ndarray) -> dict:
    """% of the land in each class (by key)."""
    land = landform > 0
    cnt = np.bincount(landform[land], minlength=len(CLASSES))
    return {CLASSES[k][1]: round(100 * float(c) / max(int(land.sum()), 1), 1) for k, c in enumerate(cnt) if k and c}
