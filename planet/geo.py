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


def is_land(elev, ice=None) -> np.ndarray:
    """Land: ground above sea level, or under grounded ice, whose bed may lie
    below the sea (pressed down by the ice's load, or a marine ice sheet), as
    a run's Simulation.land(). Worlds store the true bed (PW-307), so every
    world consumer tells land from sea with this, never with elevation > 0."""
    land = np.asarray(elev) > 0
    return land if ice is None else land | (np.asarray(ice) > 0)


def world_land(L: dict) -> np.ndarray:
    """is_land of a world's layers (elevation, and ice where it has any)."""
    return is_land(L["elevation"], L.get("ice"))


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
