"""Terrain indices of a regional zoom (PW-196): what the finished heightmap
does to the light and the water a pixel gets, for the zoom's vegetation
(zoom_vegetation, PW-214) and later soils (PW-185) and microclimate (PW-101).

- Radiation index: the sunshine a pixel's slope receives over a day, as a
  share of what flat ground at the same place gets, month by month: the
  direct beam integrated over the day (the sun's path at the pixel's
  latitude and the month's declination, dimmed through a longer air path
  at low sun) on the slope's own plane, plus a diffuse share from the part
  of the sky the slope sees. Poleward slopes get less (in winter much less),
  equatorward ones more. No shading by neighbouring hills.
- Topographic wetness index TWI = ln(a / tan b) (Beven and Kirkby 1979):
  a = upslope area per unit contour width (m), b = the slope. Wet hollows
  and valley floors high (~12-20), ridges and steep slopes low (~4-8).
  It depends on the pixel size (a grows with it): compare zooms of one
  resolution.
- Distance to the nearest river (discharge >= RIVER_Q) and to the sea, and
  which river pixel is the nearest (its discharge and height: how far above
  it a pixel sits).

Everything is deterministic in the heightmap and the discharge, so two
overlapping zooms agree where those agree.
"""

from __future__ import annotations

import numpy as np
from numba import njit, prange

from . import climate

RIVER_Q = 1.0  # m^3/s: a stream carrying this much (mean) counts as a river for the distances
DIFFUSE = 0.3  # share of the light that comes diffusely from the sky (clear to partly cloudy)
TRANSMISSION = 0.75  # clear-sky beam transmission through one air mass


@njit(parallel=True, cache=True)
def _radiation(ge, gn, lat, decl, diffuse, tau, out):
    """out[m, i]: the light on pixel i's slope over a day in month m as a
    share of flat ground's. ge, gn: the slope's gradient east and north
    (dz/dx, dz/dy, true directions); lat, decl in radians."""
    n = ge.shape[0]
    nh = 48
    for i in prange(n):
        nrm = np.sqrt(1.0 + ge[i] * ge[i] + gn[i] * gn[i])
        ue, un, uu = -ge[i] / nrm, -gn[i] / nrm, 1.0 / nrm
        sky = 0.5 * (1.0 + uu)  # the share of the sky the slope sees
        sp, cp = np.sin(lat[i]), np.cos(lat[i])
        for m in range(decl.shape[0]):
            sd, cd = np.sin(decl[m]), np.cos(decl[m])
            s_sl = 0.0
            s_fl = 0.0
            for k in range(nh):
                hh = -np.pi + (k + 0.5) * 2.0 * np.pi / nh
                ch = np.cos(hh)
                up = sp * sd + cp * cd * ch
                if up <= 0.0:
                    continue
                w = tau ** (1.0 / max(up, 0.05))  # a longer air path at low sun
                e = -cd * np.sin(hh)
                no = cp * sd - sp * cd * ch
                d = ue * e + un * no + uu * up
                if d > 0.0:
                    s_sl += d * w
                s_fl += up * w
            r = s_sl / s_fl if s_fl > 1e-9 else 1.0
            out[m, i] = (1.0 - diffuse) * r + diffuse * sky


@njit(cache=True)
def nearest(mask, nx, ny):
    """Chamfer distance (pixels; 1 and sqrt 2 steps) from every pixel to the
    nearest mask pixel, and that pixel's index (-1, inf: no mask pixel)."""
    n = nx * ny
    d = np.full(n, np.inf)
    src = np.full(n, -1, np.int64)
    for i in range(n):
        if mask[i]:
            d[i] = 0.0
            src[i] = i
    s2 = 1.4142135623730951
    for r in range(ny):
        for c in range(nx):
            i = r * nx + c
            for dr, dc, w in ((-1, -1, s2), (-1, 0, 1.0), (-1, 1, s2), (0, -1, 1.0)):
                rr, cc = r + dr, c + dc
                if rr < 0 or cc < 0 or cc >= nx:
                    continue
                j = rr * nx + cc
                if d[j] + w < d[i]:
                    d[i] = d[j] + w
                    src[i] = src[j]
    for r in range(ny - 1, -1, -1):
        for c in range(nx - 1, -1, -1):
            i = r * nx + c
            for dr, dc, w in ((1, 1, s2), (1, 0, 1.0), (1, -1, s2), (0, 1, 1.0)):
                rr, cc = r + dr, c + dc
                if rr >= ny or cc < 0 or cc >= nx:
                    continue
                j = rr * nx + cc
                if d[j] + w < d[i]:
                    d[i] = d[j] + w
                    src[i] = src[j]
    return d, src


def gradients(surface: np.ndarray, lat: np.ndarray, nx: int, ny: int, res_km: float):
    """The surface's gradient (dz/dx, m per m) east and north in true
    directions (the zoom's grid north turns away from true north away from
    its centre), and the slope (tan)."""
    z = surface.reshape(ny, nx).astype(float)
    dzdr, dzdc = np.gradient(z, res_km * 1000.0)
    gx, gy = dzdc.ravel(), -dzdr.ravel()  # grid east, grid north (rows go south)
    la = lat.reshape(ny, nx)
    dlr, dlc = np.gradient(la)
    ux, uy = dlc.ravel(), -dlr.ravel()  # true north in grid coordinates
    nrm = np.hypot(ux, uy)
    ok = nrm > 1e-12
    ux = np.where(ok, ux / np.where(ok, nrm, 1), 0.0)
    uy = np.where(ok, uy / np.where(ok, nrm, 1), 1.0)
    gn = gx * ux + gy * uy
    ge = gx * uy - gy * ux
    return ge, gn, np.hypot(gx, gy)


def radiation(ge: np.ndarray, gn: np.ndarray, lat: np.ndarray, tilt: float = 23.4) -> np.ndarray:
    """(12, n): each month's radiation index (see the module doc)."""
    mid = np.cumsum(climate.MONTH_DAYS) - climate.MONTH_DAYS / 2
    decl = np.radians(tilt) * np.sin(2 * np.pi * (mid - 80.0) / 365.25)  # as climate.insolation
    out = np.empty((12, len(ge)))
    _radiation(np.ascontiguousarray(ge, dtype=np.float64), np.ascontiguousarray(gn, dtype=np.float64),
               np.radians(np.asarray(lat, float)), decl, DIFFUSE, TRANSMISSION, out)
    return out


def indices(surface: np.ndarray, land: np.ndarray, sea: np.ndarray, discharge: np.ndarray, area_km2: np.ndarray,
            lat: np.ndarray, nx: int, ny: int, res_km: float, tilt: float = 23.4) -> dict:
    """The terrain indices of a zoom. surface: the ground, or the water's
    surface on lakes and the sea (m); land: land pixels (not sea or lake);
    discharge (m^3/s), area_km2: the upstream area (drainage_area); lat in
    degrees. Returns (n,) arrays (sea and lake pixels: neutral values):
      ri12 (12, n), radiation_index (the year's light on the slope / on flat
      ground, months weighted by their light), twi, slope (tan),
      river_dist (px; inf without rivers), river_q (m^3/s) and river_h (m) of
      the nearest river pixel, coast_dist (px from the sea)."""
    ge, gn, slope = gradients(surface, lat, nx, ny, res_km)
    ge, gn, slope = (np.where(land, v, 0.0) for v in (ge, gn, slope))
    ri12 = radiation(ge, gn, lat, tilt)
    ra = climate.insolation(np.asarray(lat, float), tilt)
    ri = (ri12 * ra).sum(0) / np.maximum(ra.sum(0), 1e-9)
    a = np.maximum(area_km2, res_km * res_km) * 1e6 / (res_km * 1000.0)  # m^2 per m of contour
    twi = np.where(land, np.log(a / np.maximum(slope, 1e-3)), 0.0)
    river = land & (discharge >= RIVER_Q)
    rd, src = nearest(river, nx, ny)
    has = src >= 0
    sj = np.maximum(src, 0)
    cd, _ = nearest(sea, nx, ny)
    return dict(ri12=ri12, radiation_index=np.where(land, ri, 1.0), twi=twi, slope=slope, river=river,
                river_dist=rd, river_q=np.where(has, discharge[sj], 0.0),
                river_h=np.where(has, surface[sj], surface), coast_dist=cd)
