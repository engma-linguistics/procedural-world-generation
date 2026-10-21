"""Where the ice's debris ends up (PW-495, PW-497): rock the glacial carving took, laid down again by
the sea, the meltwater and the wind, volume conserved (hop_scatter moves volumes, m3).

  fan      debris dropped in the sea spreads down the sea floor's slope, a grounding-zone wedge / trough-mouth
           fan (Dowdeswell et al. 2016: debris flows carry it 100s of km down the slope);
  outwash  a share of the debris melted out on land goes on in the meltwater, down the bare ground's steepest
           descent, as a sandur;
  loess    the silt of the outwash is lifted off the plain and carried along the cold season's wind.

All three are an exponential fall-off from the source along their route, with an e-folding length that is a
share of the planet's radius (so a small or large planet scales it): 0.04 R is 255 km on Earth."""

from __future__ import annotations

import math

import numpy as np

from .kernels import hop_scatter


class Deposits:
    """Routing weights per directed edge, made from the step's bed (rebuilt on each call: the bed moves)."""

    def __init__(self, g, G: dict, area: np.ndarray, p):
        self.g, self.area, self.p = g, area, p
        self.src = g.nbr_src
        self.dx = float(G["dist"].mean())  # m, between cell centres
        self.R = math.sqrt(float(area.sum()) / (4 * math.pi))  # m, the planet's radius
        self.u = np.stack([G["ux"], G["uy"], G["uz"]], 1)  # per edge: unit tangent toward the neighbour

    def _spread(self, x, w, frac: float) -> np.ndarray:
        """x (m per cell) spread along the edge weights w with an e-folding length frac x radius."""
        L = max(frac * self.R, 0.5 * self.dx)
        keep = 1.0 - math.exp(-self.dx / L)
        hops = int(math.ceil(3.0 * L / self.dx)) + 1
        out = np.zeros(len(x))
        hop_scatter(x * self.area, self.g.nbr_off, self.g.nbr_idx, w, keep, hops, out)
        return out / self.area

    def _fall(self, bed, ok):
        """Per edge: the bed's drop to the neighbour, where both cells are in `ok` and the neighbour is lower."""
        d = bed[self.src] - bed[self.g.nbr_idx]
        return np.where(ok[self.src] & ok[self.g.nbr_idx] & (d > 0), d, 0.0)

    def fan(self, x, bed, sl):
        """x dropped in the sea: down the sea floor, over every sea neighbour not higher than the pile (the
        weight is the fall plus fan_flat, so a flat shelf still spreads it: a pile spills over its rim)."""
        sea = bed < sl
        d = bed[self.src] - bed[self.g.nbr_idx] + self.p.fan_flat
        w = np.where(sea[self.src] & sea[self.g.nbr_idx], np.maximum(d, 0.0), 0.0)
        return self._spread(x, w, self.p.fan_km_r)

    def outwash(self, x, bed, bare):
        """x out of the ice on land: down the ice-free ground (bare), steepest descent weighted by the fall^2."""
        w = self._fall(bed, bare) ** 2
        return self._spread(x, w, self.p.outwash_km_r)

    def wind(self, x, wind):
        """x lifted: along the wind (n, 3 tangent vectors), to the neighbours it blows toward (cos^2)."""
        c = np.einsum("ij,ij->i", wind[self.src], self.u)
        sp = np.linalg.norm(wind, axis=1)[self.src]
        w = np.where(sp > 1e-6, np.maximum(c / np.maximum(sp, 1e-9), 0.0), 0.0) ** 2
        return self._spread(x, w, self.p.loess_km_r)
