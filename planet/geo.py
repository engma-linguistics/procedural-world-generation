"""Sphere geometry shared by every module: the planet's radius and
conversions between unit vectors and latitude/longitude (degrees)."""

from __future__ import annotations

import numpy as np

R_KM = 6371.0  # planet radius (Earth's), km


def latlon(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(lat, lon) in degrees of unit vector(s) p, shape (..., 3)."""
    p = np.asarray(p)
    return np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1))), np.degrees(np.arctan2(p[..., 1], p[..., 0]))


def xyz(lat_rad, lon_rad) -> np.ndarray:
    """Unit vector(s), shape (..., 3), from latitude and longitude in radians."""
    return np.stack([np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)], -1)


# The sea is the water that reaches the world ocean (PW-1229). Ground below sea level that is cut off from it is
# land: a closed hollow the rivers and lakes fill to a lake (the Dead Sea) or leave a dry depression
# (Qattara, Death Valley, Lake Eyre's basin). Two rules stand in for the straits a grid of 30-110 km cells can't
# resolve:
# - SEA_MIN_KM2: a body this large is sea even with no link the grid sees. On Earth's L6 and L7 grids the
#   Baltic (0.39 Mkm2 there), the Black Sea (0.40-0.42) and the Red Sea (0.47-0.49) are such bodies, joined to the
#   ocean by straits of 1-30 km; the Caspian (0.62-0.66 with its shores) is the one lake that big, and it was a
#   sea (Paratethys) until a few Myr ago: at this size a cut-off body is a remnant sea or an enclosed ocean (some
#   worlds wall off ocean basins of 10-80 Mkm2), which the climate's ocean, not a lake, should carry. The pockets
#   PW-1229 is about are far smaller: 1-7 cells of a lowland at sea level, or the PW-171 pits (L7: up to ~0.1 Mkm2).
# - SILL_M: a body joins the sea it is one land cell away from when that cell's bed is no higher than this: a
#   lowland cell between two waters whose mean is within a few metres of the sea is mostly shore and shallows,
#   and a strait narrower than the cell (the Danish straits, the Kerch strait) can cross it. A higher cell is a
#   real divide at the grid's scale (Qattara's 200 m plateau to the Mediterranean, the Dead Sea's hills).
SEA_MIN_KM2 = 0.3e6
SILL_M = 10.0


def _grid_of(n: int, grid=None):
    """The (unwalled) sphere grid of n cells: grid's own base if given, else the shared grid of that size."""
    if grid is not None:
        return getattr(grid, "base", grid)
    from .grid import shared_grid
    level = int(round(np.log((n - 2) / 10) / np.log(4))) if n > 12 else 0
    if 10 * 4 ** level + 2 != n:
        raise ValueError(f"is_land: {n} cells is no sphere grid; pass grid=")
    return shared_grid(level)


def is_land(elev, ice=None, grid=None) -> np.ndarray:
    """Land: everything but the sea. The sea is ground at or below sea level,
    not under grounded ice, that reaches the world ocean (its largest body
    of water, along the grid's links), with the rules above for straits the
    grid can't resolve (SEA_MIN_KM2, SILL_M). So land is ground above sea
    level, ground under grounded ice, whose bed may lie below the sea
    (pressed down by the ice's load, or a marine ice sheet; PW-307), and
    ground below sea level cut off from the ocean (PW-1229). Worlds and runs
    store the true bed, so every consumer tells land from sea with this,
    never with elevation > 0. grid: the cells' grid (default: the shared
    sphere grid with as many cells; a walled grid's base is used)."""
    elev = np.asarray(elev)
    wet = elev <= 0
    if ice is not None:
        wet &= ~(np.asarray(ice) > 0)
    if not wet.any():
        return ~wet
    g = _grid_of(elev.shape[0], grid)
    from . import kernels
    lab, k = kernels.components(wet, g.nbr_off, g.nbr_idx)
    size = np.bincount(lab[wet], minlength=k)
    sea = size * cell_area_km2(g.n) >= SEA_MIN_KM2
    sea[np.argmax(size)] = True
    if not sea.all():
        # bodies one low cell apart join (union-find over the bodies), and any group with a sea in it is sea
        src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
        dst = g.nbr_idx
        sill = ~wet & (elev <= SILL_M)
        e = sill[src] & wet[dst]
        s, b = src[e], lab[dst[e]]  # (sill cell, a body beside it)
        low = np.full(g.n, k)
        np.minimum.at(low, s, b)
        pair = b != low[s]  # (each other body beside a sill joins its lowest-numbered one)
        parent = np.arange(k)

        def root(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for x, y in set(zip(low[s][pair].tolist(), b[pair].tolist())):
            rx, ry = root(x), root(y)
            if rx != ry:
                parent[rx] = ry
        roots = np.array([root(x) for x in range(k)])
        sea = np.bincount(roots, weights=sea, minlength=k)[roots] > 0
    return ~(wet & sea[np.maximum(lab, 0)])


def world_land(L: dict, grid=None) -> np.ndarray:
    """is_land of a world's layers (elevation, and ice where it has any)."""
    return is_land(L["elevation"], L.get("ice"), grid)


def arc(dots) -> np.ndarray:
    """Great-circle angle (radians) from the dot products of unit vectors. The caller forms the dot
    product (a @ b or (a * b).sum(1)), which keeps each call site's float order."""
    return np.arccos(np.clip(dots, -1, 1))


def arc_km(dots) -> np.ndarray:
    """Great-circle distance (km) from the dot products of unit vectors (see arc)."""
    return arc(dots) * R_KM


def cell_area_km2(n: int) -> float:
    """Area of one of n equal-area cells on the sphere, km^2."""
    return 4 * np.pi * R_KM ** 2 / n


def smoothstep(e0, e1, x):
    """0 below e0, 1 above e1, cubic Hermite between (e0 > e1 gives a falling step)."""
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def ramp(x, a, b):
    """0 at a, 1 at b (either direction), linear and clipped."""
    return np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)
