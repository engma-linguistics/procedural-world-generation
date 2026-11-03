"""Den ground (PW-1382): how well a cell's rock and ground give a den people (goblins, kobolds, troglodytes: the `denning` trait)
caves, rock shelters or ground to dig, 0..1, from the world's geology. It is a preference, never a requirement (Daniel 11-02:
"let appropriate races prefer them, but not rely on them. Goblins can live all over! Kobolds too"): the ladder thins a den people
off good den ground to (1 - den trait) of its density there (history.model.run, ladder.Ladder.thin), never to nothing, and the
habitat (where it can live) does not read it at all.

A cell's den ground is the best of what it offers (sources in docs/review/peoples/dens/round1.md, read in lane 143):

  karst caves       exposed carbonate (limestone, dolomite: surface_rock): "it is safe to assume that all carbonate rocks are
                    karstified unless proven otherwise" (Goldscheider et al. 2020, Hydrogeol J 28:1661, who map carbonate on 15.2%
                    of the ice-free land, 34% of it in arid climates), so carbonate counts in any climate, the wet karst landform
                    most; evaporite (gypsum karst, "karstification also occurs in evaporite rocks such as gypsum") less
  lava tubes        flood basalt and hotspot basalt, the lava-plateau and hotspot landforms: "Lava tubes are usually only found in
                    pahoehoe flows" (NPS, Basaltic Lava Flows), the basalt plains and shields
  carved rock       volcanic tuff: Cappadocia's houses, churches and underground cities "from the soft rocks of volcanic deposits"
  rock shelters     a cliff of hard bedded rock over a softer one, with relief to cut it: sandstone, quartzite, carbonate, basalt and
                    coal measures (Knoll 2003, GSA abstract, Cumberland Plateau: "preferential erosion of intercalated layers of
                    shale or coal at a cliff base with subsequent roof collapse"; Tasmania's shelters "usually in areas of limestone,
                    dolerite and sandstone"); the caprock and escarpment landforms are such cliffs by definition. Crystalline and
                    soft rock with relief gives fewer (a judgement: overhangs and boulder caves, no source)
  sea caves         sea cliffs (coast forms)
  dug ground        thick loess (the yaodong of the Loess Plateau, dug into loess for its "wall stability", 30-40 million people in
                    the early 2000s: Wikipedia, Yaodong), and less, deep well-drained mineral soil out of permafrost
"""

from __future__ import annotations

import numpy as np

from ..surface import (COAL, DOLOMITE, EVAPORITE, FLOOD_BASALT, HOTSPOT, LIMESTONE, QUARTZITE, SANDSTONE, SHALE, TUFF)

# the score of each kind of den ground at its best (judgements on the sources above: caves in carbonate and lava tubes are whole
# cave systems, a shelter is one overhang, a dug burrow needs labour)
KARST = 1.0  # the karst landform (wet, unfrozen carbonate: landform.py)
CARBONATE = 0.8  # exposed limestone or dolomite elsewhere (dry or cold karst; Goldscheider: carbonate is karstified unless shown not)
GYPSUM = 0.5  # evaporite (gypsum karst)
LAVA = 0.7  # basalt plains and shields (lava tubes in pahoehoe)
TUFF_X = 0.8  # tuff: soft enough to carve, firm enough to stand
SHELTER = 0.8  # hard bedded rock with full relief, and the caprock and escarpment landforms
SHELTER_OTHER = 0.4  # crystalline or soft rock with full relief (a judgement)
SEA_CAVE = 0.5  # sea cliffs
LOESS_X = 0.8  # thick loess
LOESS_M = (0.5, 3.0)  # m of loess from which it digs, to full (yaodong are cut in loess tens of metres thick; a few metres take a burrow)
SOIL_X = 0.3  # deep, well-drained mineral soil out of permafrost
SOIL_M = (0.5, 2.0)  # m of soil, likewise
RISE = (1.5, 5.0)  # m per km between neighbours: relief from which a cell has cliffs, to full (land.HILL_SLOPE starts at 1.5)
HARD = (SANDSTONE, QUARTZITE, LIMESTONE, DOLOMITE, FLOOD_BASALT, HOTSPOT, COAL)  # cliff-forming, bedded or jointed (coal measures:
# sandstone over shale and coal, Knoll's shelters)
DIG_TEXTURE = (2, 3, 4)  # soils.TEXTURES loam, silt, clay (sand caves in, peat is wet)
DIG_DRAINAGE = (1, 2, 3)  # soils.DRAINAGE excessive, well, moderate


def _ramp(x, lo, hi):
    return np.clip((np.asarray(x, float) - lo) / (hi - lo), 0.0, 1.0)


def fitness(f, rise: np.ndarray, cliff: np.ndarray, land: np.ndarray) -> np.ndarray:
    """Den ground 0..1 per cell from the world's layers (`f(name)`: the layer as floats, zeros when missing), the relief `rise`
    (m per km to the steepest neighbour) and the sea-cliff good `cliff` (0..1). 0 off land and under ice."""
    from ..landform import CAPROCK, ESCARPMENT, HOTSPOT_CLASS, KARST as KARST_CLASS, LAVA_PLATEAU
    rock = f("surface_rock").astype(int)
    lf = f("landform").astype(int)
    relief = _ramp(rise, *RISE)
    carb = np.isin(rock, (LIMESTONE, DOLOMITE))
    parts = [
        np.where(lf == KARST_CLASS, KARST, np.where(carb, CARBONATE, np.where(rock == EVAPORITE, GYPSUM, 0.0))),
        np.where(np.isin(lf, (LAVA_PLATEAU, HOTSPOT_CLASS)) | np.isin(rock, (FLOOD_BASALT, HOTSPOT)), LAVA, 0.0),
        np.where(rock == TUFF, TUFF_X, 0.0),
        np.where(np.isin(lf, (CAPROCK, ESCARPMENT)), SHELTER, 0.0),
        relief * np.where(np.isin(rock, HARD), SHELTER, np.where(rock == SHALE, 0.5 * SHELTER_OTHER, SHELTER_OTHER)),
        SEA_CAVE * np.clip(cliff, 0, 1),
        LOESS_X * _ramp(f("loess"), *LOESS_M),
        SOIL_X * _ramp(f("soil_depth"), *SOIL_M) * np.isin(f("soil_texture").astype(int), DIG_TEXTURE)
        * np.isin(f("soil_drainage").astype(int), DIG_DRAINAGE) * (f("permafrost") <= 0),
    ]
    out = np.max(parts, axis=0)
    return np.where(land & (f("ice") <= 0), np.clip(out, 0.0, 1.0), 0.0)
