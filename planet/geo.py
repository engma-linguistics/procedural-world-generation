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
