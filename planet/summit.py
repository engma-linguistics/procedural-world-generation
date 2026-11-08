"""Summit height: a cell's mean height plus Earth's measured sub-cell relief (PW-846).

The model stores one height per cell, the cell's average. A real range is
narrower than a ~60 km cell, so the true summit stands above that average
(Earth's L7 cell means top out at 5.9 km, Tibet; Everest is 8.8 km). The
summit is a display number only: drainage, lakes and climate keep the cell
means. Never feed it back into the simulation.

Fit (scout 171, docs/review/tectonics/mountains/scout1.md; fit script
docs/review/tectonics/mountains/pw846_fit.py): in 0.5 degree blocks (~55 km, one
L7 cell) of the HydroSHEDS v1 30-arcsecond DEM (Lehner, Verdin & Jarvis 2008,
Eos 89(10); loaded by tools/earth_data.py), the 75th percentile of (highest 1 km pixel -
block mean) against the block's local relief (highest minus lowest block mean
over the block and its 8 neighbours), 57,717 land blocks. The relief ("slope")
term explains the spread far better than the block mean does: at a mean of
2-3 km the median is 42 m on flat ground and 1,684 m in rugged ground
(pw846_fit.py prints the bins).

viewer/globe/summit.js repeats RELIEF_KNOTS (tests/test_summit.py checks they match).
"""
import numpy as np

# (local relief m, 75th percentile of sub-cell relief m): per equal-count bin of the fit,
# the bin's median relief and its 75th-percentile (highest pixel - block mean). The 75th
# not the median, because the figure is used for the top of the range: the median
# understates the cell a world's tallest peak sits in (Earth's L7 top cell reads 7.3 km
# with it, 7.7 km with this).
RELIEF_KNOTS = np.array([
    (0, 0), (58, 86), (142, 186), (282, 464), (484, 771), (690, 950), (884, 1088),
    (1117, 1255), (1464, 1513), (1904, 1774), (2527, 2137), (3345, 2479),
], float)


def local_relief(g, elev: np.ndarray) -> np.ndarray:
    """Highest minus lowest land height over each cell and its neighbours (m)."""
    e = np.asarray(elev, float)
    land = e > 0
    hi = np.where(land, e, -np.inf)
    lo = np.where(land, e, np.inf)
    off = g.nbr_off[:-1]
    hmax = np.maximum(hi, np.maximum.reduceat(hi[g.nbr_idx], off))
    lmin = np.minimum(lo, np.minimum.reduceat(lo[g.nbr_idx], off))
    return np.where(land, hmax - lmin, 0.0)


def sub_cell_relief(rel: np.ndarray) -> np.ndarray:
    """Summit-over-mean (upper-middle estimate) (m) for a local relief (m); flat beyond the last knot."""
    return np.interp(rel, RELIEF_KNOTS[:, 0], RELIEF_KNOTS[:, 1])


def summit_m(g, elev: np.ndarray) -> np.ndarray:
    """Each cell's summit height (m): the mean on the sea floor, mean + sub-cell relief on land."""
    e = np.asarray(elev, float)
    return np.where(e > 0, e + sub_cell_relief(local_relief(g, e)), e)
