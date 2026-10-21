"""Map projections of the sphere in pure numpy (PW-477), for `planet export --projection`.

A `Projection` is a name plus a centre (lat0, lon0). Every projection is used in
an oblique aspect: the sphere is first rotated so the centre sits at (0 N, 0 E)
with north up there, then the standard formulas apply. So the whole-world
projections (equirect, equal-earth, mollweide) can be centred on any point, and
the azimuthal ones (laea, aeqd, ortho, stereo) are centred on it by nature.

Coordinates are on the unit sphere (R = 1, multiply by the radius for metres);
x runs east and y north on the map. Points a projection cannot show (the far
side of an orthographic globe, the antipode of a stereographic map, outside the
Equal Earth / Mollweide outline) give NaN going forward and `valid = False`
going back. Round trips and known points are tested in tests/test_projection.py.
"""

from __future__ import annotations

import re

import numpy as np

from .geo import R_KM, xyz

NAMES = ("equirect", "equal-earth", "mollweide", "laea", "aeqd", "ortho", "stereo")
WORLD_PROJECTIONS = ("equirect", "equal-earth", "mollweide")  # (whole world in one outline)
STEREO_MAX = np.radians(160.0)  # the stereographic map is cut at this angular distance
STEREO_DEFAULT = np.radians(120.0)  # and shows this much by default

_A1, _A2, _A3, _A4 = 1.340264, -0.081106, 0.000893, 0.003796  # Equal Earth (Savric et al. 2018)
_EE_M = np.sqrt(3) / 2


def _ee_dpoly(t):
    t2 = t * t
    return _A1 + 3 * _A2 * t2 + 7 * _A3 * t2 * t2 * t2 + 9 * _A4 * t2 * t2 * t2 * t2


def _ee_y(t):
    t2 = t * t
    return t * (_A1 + _A2 * t2 + _A3 * t2**3 + _A4 * t2**4)


def _moll_theta(lat):
    """Auxiliary angle with 2t + sin 2t = pi sin(lat) (Newton, poles exact)."""
    s = np.pi * np.sin(lat)
    t = lat.copy() if isinstance(lat, np.ndarray) else np.array(lat, float)
    for _ in range(40):
        d = 2 + 2 * np.cos(2 * t)
        t = t - (2 * t + np.sin(2 * t) - s) / np.maximum(d, 1e-9)
    t = np.where(np.abs(lat) > np.radians(89.99999), np.sign(lat) * np.pi / 2, t)
    return np.clip(t, -np.pi / 2, np.pi / 2)


class Projection:
    """A named projection centred on (lat0, lon0), degrees. `forward`/`inverse`
    work on lat/lon (degrees) or on world unit vectors (`project`, `unproject`)."""

    def __init__(self, name: str, lat0: float = 0.0, lon0: float = 0.0):
        if name not in NAMES:
            raise ValueError(f"unknown projection {name!r} (one of {', '.join(NAMES)})")
        if not -90 <= lat0 <= 90:
            raise ValueError(f"centre latitude {lat0} outside -90..90")
        self.name, self.lat0, self.lon0 = name, float(lat0), float(((lon0 + 180) % 360) - 180)
        la, lo = np.radians(lat0), np.radians(lon0)
        self.c = xyz(la, lo)
        self.e = np.array([-np.sin(lo), np.cos(lo), 0.0])  # east (any, at a pole: the lon0 meridian's)
        self.n = np.cross(self.c, self.e)
        self.frame = np.stack([self.c, self.e, self.n])  # world -> local: q = p @ frame.T

    # --- the spherical-frame ---------------------------------------------------
    def to_local(self, p):
        return np.asarray(p, float) @ self.frame.T

    def to_world(self, q):
        return np.asarray(q, float) @ self.frame

    # --- forward -------------------------------------------------------------
    def project(self, p):
        """(x, y) on the unit sphere's map of world unit vectors p (..., 3); NaN where not shown."""
        q = self.to_local(p)
        return self._forward_q(q)

    def forward(self, lat, lon):
        """(x, y) of lat/lon in degrees."""
        return self.project(xyz(np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))))

    def _forward_q(self, q):
        qx, qy, qz = q[..., 0], q[..., 1], q[..., 2]
        n = self.name
        if n in WORLD_PROJECTIONS:
            lat, lon = np.arcsin(np.clip(qz, -1, 1)), np.arctan2(qy, qx)
            if n == "equirect":
                return lon, lat
            if n == "equal-earth":
                th = np.arcsin(_EE_M * np.sin(lat))
                return 2 * np.sqrt(3) * lon * np.cos(th) / (3 * _ee_dpoly(th)), _ee_y(th)
            th = _moll_theta(lat)
            return 2 * np.sqrt(2) / np.pi * lon * np.cos(th), np.sqrt(2) * np.sin(th)
        cosc = np.clip(qx, -1, 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            c = np.arccos(cosc)
            if n == "laea":
                k = np.sqrt(2 / (1 + cosc))
                bad = cosc < -1 + 1e-12
            elif n == "aeqd":
                k = np.where(c > 1e-12, c / np.sin(np.maximum(c, 1e-12)), 1.0)
                bad = c > np.pi - 1e-9
            elif n == "ortho":
                k = np.ones_like(cosc)
                bad = cosc < 0
            else:  # stereo
                k = 2 / (1 + cosc)
                bad = c > STEREO_MAX
        with np.errstate(invalid="ignore"):
            return np.where(bad, np.nan, k * qy), np.where(bad, np.nan, k * qz)

    # --- inverse -------------------------------------------------------------
    def unproject(self, x, y):
        """(world unit vectors (..., 3), valid) of map coordinates; invalid ones point at the centre."""
        x, y = np.asarray(x, float), np.asarray(y, float)
        n = self.name
        if n in WORLD_PROJECTIONS:
            if n == "equirect":
                lat, lon = y, x
                ok = (np.abs(lat) <= np.pi / 2) & (np.abs(lon) <= np.pi)
            elif n == "equal-earth":
                ymax = _ee_y(np.pi / 3)
                th = np.clip(y / 1.3, -np.pi / 3, np.pi / 3)  # (y ~ 1.3 theta)
                for _ in range(30):
                    th = th - (_ee_y(th) - y) / _ee_dpoly(th)
                th = np.clip(th, -np.pi / 3, np.pi / 3)
                lat = np.arcsin(np.clip(np.sin(th) / _EE_M, -1, 1))
                lon = 3 * x * _ee_dpoly(th) / (2 * np.sqrt(3) * np.cos(th))
                ok = (np.abs(y) <= ymax * (1 + 1e-12)) & (np.abs(lon) <= np.pi * (1 + 1e-12))
            else:
                s = np.clip(y / np.sqrt(2), -1, 1)
                th = np.arcsin(s)
                lat = np.arcsin(np.clip((2 * th + np.sin(2 * th)) / np.pi, -1, 1))
                with np.errstate(invalid="ignore", divide="ignore"):
                    lon = np.pi * x / (2 * np.sqrt(2) * np.cos(th))
                ok = (np.abs(y) <= np.sqrt(2) * (1 + 1e-12)) & (np.abs(lon) <= np.pi * (1 + 1e-12))
            ok &= np.isfinite(lat) & np.isfinite(lon)
            q = xyz(np.where(ok, lat, 0.0), np.where(ok, lon, 0.0))
        else:
            rho = np.hypot(x, y)
            if n == "laea":
                ok, c = rho <= 2, 2 * np.arcsin(np.clip(rho / 2, 0, 1))
            elif n == "aeqd":
                ok, c = rho <= np.pi, rho
            elif n == "ortho":
                ok, c = rho <= 1, np.arcsin(np.clip(rho, 0, 1))
            else:
                c = 2 * np.arctan(rho / 2)
                ok = c <= STEREO_MAX
            with np.errstate(invalid="ignore", divide="ignore"):
                ux, uy = np.where(rho > 1e-15, x / np.maximum(rho, 1e-300), 0.0), np.where(rho > 1e-15, y / np.maximum(rho, 1e-300), 0.0)
            q = np.stack([np.cos(c), np.sin(c) * ux, np.sin(c) * uy], -1)
            q = np.where(ok[..., None], q, [1.0, 0.0, 0.0])
        return self.to_world(q), ok

    # --- extents and descriptions ---------------------------------------------
    def full_extent(self) -> tuple[float, float]:
        """Half-width and half-height (unit sphere) of the whole-world map (azimuthal: the
        disc of the default view: laea / ortho: the globe, aeqd: the globe, stereo: 120 deg)."""
        n = self.name
        if n == "equirect":
            return np.pi, np.pi / 2
        if n == "equal-earth":
            return float(2 * np.sqrt(3) * np.pi / (3 * _ee_dpoly(0.0))), float(_ee_y(np.pi / 3))
        if n == "mollweide":
            return 2 * np.sqrt(2), np.sqrt(2)
        r = {"laea": 2.0, "aeqd": np.pi, "ortho": 1.0, "stereo": 2 * np.tan(STEREO_DEFAULT / 2)}[n]
        return r, r

    def proj_string(self) -> str | None:
        """A PROJ string for the sphere of this planet's radius, or None where PROJ has no
        plain equivalent (an oblique Equal Earth / Mollweide / equirectangular map)."""
        R = f"+R={R_KM * 1000:g} +x_0=0 +y_0=0 +units=m +no_defs"
        n = self.name
        if n in ("laea", "aeqd", "stereo", "ortho"):
            p = {"laea": "laea", "aeqd": "aeqd", "stereo": "stere", "ortho": "ortho"}[n]
            return f"+proj={p} +lat_0={self.lat0:g} +lon_0={self.lon0:g} {R}"
        if abs(self.lat0) > 1e-9:
            return None
        p = {"equirect": "eqc +lat_ts=0 +lat_0=0", "equal-earth": "eqearth", "mollweide": "moll"}[n]
        return f"+proj={p} +lon_0={self.lon0:g} {R}"

    def describe(self) -> dict:
        return {"name": self.name, "center": {"lat": self.lat0, "lon": self.lon0},
                "oblique_frame": {"rows": ["centre", "east", "north"], "matrix": np.round(self.frame, 9).tolist(),
                                  "note": "local = frame @ world unit vector (world: x through 0N 0E, y 90E, z north); "
                                          "then the standard formula with the centre at 0N 0E, north up"},
                "proj": self.proj_string(),
                "proj_note": None if self.proj_string() else "oblique aspect has no plain PROJ string; "
                                                             "use oblique_frame"}


# ---------------------------------------------------------------------------
# Command-line values
# ---------------------------------------------------------------------------
def parse_center(s) -> tuple[float, float]:
    """'lat,lon' (degrees) to a tuple."""
    if not isinstance(s, str):
        lat, lon = s
        return float(lat), float(lon)
    try:
        lat, lon = (float(v) for v in s.replace(" ", "").split(","))
    except ValueError:
        raise ValueError(f"--center wants lat,lon in degrees (e.g. 48.5,-2), not {s!r}") from None
    if not -90 <= lat <= 90:
        raise ValueError(f"centre latitude {lat} outside -90..90")
    return lat, lon


def parse_extent(s) -> tuple[float, float]:
    """'2000km', '3000x2000km', '30deg' or '40x20deg' to (width_km, height_km) of the map
    plane (degrees are arc degrees of the planet, 1 deg = R * pi / 180 km). A tuple of km passes."""
    if not isinstance(s, str):
        w, h = s
        return float(w), float(h)
    m = re.fullmatch(r"\s*([0-9.]+)\s*(?:x\s*([0-9.]+))?\s*(km|deg)?\s*", s)
    if not m or not m.group(3):
        raise ValueError(f"--extent wants e.g. 2000km, 3000x2000km, 30deg, 40x20deg, not {s!r}")
    f = R_KM * np.pi / 180 if m.group(3) == "deg" else 1.0
    w = float(m.group(1)) * f
    h = float(m.group(2)) * f if m.group(2) else w
    if w <= 0 or h <= 0:
        raise ValueError("--extent must be positive")
    return w, h


def pixel_grid(proj: Projection, width: int, extent_km: tuple[float, float] | None = None):
    """The pixel centres of a map `width` px wide: square pixels, centre of the map at the
    projection's origin. Returns dict(width, height, step (unit sphere per px), x, y (ny, nx),
    pts (ny*nx, 3 world vectors), valid (ny, nx), hw, hh (half extents, unit sphere))."""
    hw, hh = proj.full_extent()
    if extent_km:
        hw, hh = extent_km[0] / 2 / R_KM, extent_km[1] / 2 / R_KM
    width = max(int(width), 1)
    step = 2 * hw / width
    height = max(int(round(2 * hh / step)), 1)
    hh = height * step / 2
    X, Y = np.meshgrid(-hw + (np.arange(width) + 0.5) * step, hh - (np.arange(height) + 0.5) * step)
    pts, valid = proj.unproject(X, Y)
    return {"width": width, "height": height, "step": step, "x": X, "y": Y, "valid": valid,
            "pts": pts.reshape(-1, 3), "hw": hw, "hh": hh}


def pixel_size_m(pts: np.ndarray, valid: np.ndarray, shape: tuple) -> tuple[np.ndarray, np.ndarray]:
    """Metres on the ground between neighbouring pixel centres (across, down) from their sphere
    points (n, 3), padded to the raster's shape; invalid pixels take the median."""
    ny, nx = shape
    p = pts.reshape(ny, nx, 3)

    def dist(a, b):
        return R_KM * 1000 * np.arccos(np.clip((a * b).sum(-1), -1, 1))

    dx, dy = np.empty(shape), np.empty(shape)
    dx[:, :-1] = dist(p[:, 1:], p[:, :-1])
    dx[:, -1:] = dx[:, -2:-1] if nx > 1 else 1.0
    dy[:-1] = dist(p[1:], p[:-1])
    dy[-1:] = dy[-2:-1] if ny > 1 else 1.0
    ok = valid & np.roll(valid, -1, 1) & np.roll(valid, -1, 0)
    med = lambda a: float(np.median(a[ok])) if ok.any() else 1.0  # noqa: E731
    return np.where(ok, np.maximum(dx, 1.0), med(dx)), np.where(ok, np.maximum(dy, 1.0), med(dy))

