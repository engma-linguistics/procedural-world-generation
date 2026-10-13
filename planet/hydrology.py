"""Rivers, lakes and fluvial erosion on the cell graph.

1. Priority-flood (Barnes et al. 2014): grow inward from the ocean, always
   expanding the lowest known cell next. Each land cell's 'downstream' is
   whichever cell reached it first, so every drop of rain has a route to
   the sea. Cells that had to be raised to drain (pits) are lakes.
2. Flow accumulation: walk from the headwaters down, summing rainfall.
   Big sums = big rivers.
3. Stream-power erosion (Braun & Willett 2013): cut each cell toward its
   downstream neighbour at a rate ~ sqrt(flow). Big rivers carve deep
   valleys, ridges stay sharp. The implicit form used here can't blow up
   numerically, however hard you push it.
"""

from __future__ import annotations

import heapq

import numpy as np

from .grid import Grid


def priority_flood(grid: Grid, elev: np.ndarray, eps: float = 0.01):
    """Returns (filled, downstream, order). order runs outlet -> headwater."""
    n = grid.n
    filled = elev.astype(float).copy()
    down = np.full(n, -1)
    closed = elev <= 0
    if not closed.any():
        closed[np.argmin(elev)] = True
    heap = [(filled[i], i) for i in np.flatnonzero(closed)]
    heapq.heapify(heap)
    order = []
    nbrs = grid.neighbors
    while heap:
        z, i = heapq.heappop(heap)
        order.append(i)
        for j in nbrs[i]:
            if not closed[j]:
                closed[j] = True
                if filled[j] < z + eps:
                    filled[j] = z + eps
                down[j] = i
                heapq.heappush(heap, (filled[j], j))
    return filled, down, np.array(order)


def accumulate(down: np.ndarray, order: np.ndarray, rain: np.ndarray) -> np.ndarray:
    flow = rain.astype(float).copy()
    for i in order[::-1]:
        d = down[i]
        if d >= 0:
            flow[d] += flow[i]
    return flow


def erode(grid: Grid, elev: np.ndarray, precip_mm: np.ndarray, iterations: int = 12,
          strength: float = 1.0, diffusion: float = 0.08):
    """Carve river valleys. Returns new elevation."""
    h = elev.astype(float).copy()
    rain = precip_mm / 1000.0  # metres/yr; flow then ~ 'cells x m/yr'
    k = 0.018 * strength * 2 ** (grid.level - 5)  # finer cells -> more upstream cells
    a, b = grid.edges[:, 0], grid.edges[:, 1]
    deg = np.bincount(np.concatenate([a, b]), minlength=grid.n)
    for _ in range(iterations):
        _, down, order = priority_flood(grid, h)
        flow = accumulate(down, order, rain)
        f = k * np.sqrt(flow)
        for i in order:
            d = down[i]
            if d < 0:
                continue
            hd = max(h[d], 0.0)
            if h[i] > hd:
                h[i] = (h[i] + f[i] * hd) / (1 + f[i])
        # Hillslope creep: land relaxes a bit toward its neighbours.
        land = h > 0
        nb_mean = (np.bincount(a, h[b], grid.n) + np.bincount(b, h[a], grid.n)) / deg
        h = np.where(land, (1 - diffusion) * h + diffusion * np.maximum(nb_mean, 1.0), h)
    return h


def rivers_and_lakes(grid: Grid, elev: np.ndarray, precip_mm: np.ndarray):
    filled, down, order = priority_flood(grid, elev)
    flow = accumulate(down, order, precip_mm / 1000.0)
    lake = (elev > 0) & (filled - elev > 5)
    return flow, down, lake
