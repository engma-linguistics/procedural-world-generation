"""Numba kernels for planet.timezoom: the yearly cycle and surface mass
balance of each cell, and shallow-ice flow on the geodesic grid.

Directed edges are in the grid's CSR order: edge e = nbr_off[i] + k goes
from cell i to nbr_idx[e]. Per edge: dist (m, centre to centre), elen (m,
the shared side's length), (ux, uy, uz) the unit tangent at i toward the
neighbour. Per cell: area (m2).
"""

from __future__ import annotations

import math

import numpy as np
from numba import njit

DAYS = 365.25 / 12  # days per month
SQRT2PI = math.sqrt(2 * math.pi)


@njit(cache=True)
def climate_step(land, north, t_mean, half, p_jul, p_jan, dt_base, dt_wet, k_orb, band, dq, f_ice, f_alb,
                 cool, damp, hold, bare_share, snow_w,
                 sigma, ddf_snow, ddf_ice, refreeze, precip_k,
                 smb, t_ann, t_warm, t_cold, p_scale, f_sum):
    """One (orbit-averaged) year at every cell (icemass describes the rule).

    Each month m (0 = the month after the March equinox) has the
    temperature t_mean + half * cos(2 pi (m - peak) / 12), peak = July in the
    north and January in the south, plus dt_base (lapse rate over the
    changed surface, global temperature change), the orbital anomaly
    k_orb * dq[band, m] (dq: insolation change, W/m2, averaged with the month
    before: the ground lags the sun). An ice sheet keeps itself cold (as in
    climate.compute): `cool` C colder all year, phased in by f_ice (0..1,
    with thickness). The year runs from the autumn after the summer: snow
    falls below ~0 C and lies on the ground; while it lies (bright: its
    water equivalent / snow_w, up to 1) the summer's warmth above the
    annual mean is damped by damp[i] (bright snow takes little of the
    summer sun; a sheet's own air mass, icemass.sheet_cover) and what is
    left above 0 C times `hold` (melting holds it near 0 C). Once the
    year's snow has melted away the surface is bare: ground, or bare ice
    (f_alb: 0..1 with the ice's thickness), which keeps bare_share of the
    snow's effects. So a sheet's margin, where the snow is gone by early
    summer, melts in the full summer, while snow that lasts the summer
    keeps it cool (and the snowline depends on the snowfall). Rain falls
    at p_jul (Apr-Sep) or p_jan (Oct-Mar) mm/yr (climate.compute's, which
    already dries the air over high ground), times exp(precip_k * dT) with
    dT = dt_wet (global change since then) + the year's mean orbital
    anomaly: warm air carries more water. Positive degree days with daily
    weather of spread `sigma` (Reeh 1991) melt the lying snow first
    (ddf_snow mm w.e. per degree-day; a share `refreeze` of the melt
    refreezes as ice in the snowpack), then ice (ddf_ice).
    Out: smb (m of ice per yr, land cells only; >0 grows ice even on bare
    ground: snow that outlasts the summer), annual mean / warmest / coldest
    month temperatures, the rain scale factor, and f_sum: the surface's
    mean brightness (0..1) over the summer months."""
    n = t_mean.shape[0]
    for i in range(n):
        peak = 3 if north[i] else 9
        b = band[i]
        osum = 0.0
        for m in range(12):
            osum += k_orb[i] * 0.5 * (dq[b, m] + dq[b, (m + 11) % 12])
        ps = math.exp(precip_k * (dt_wet[i] + osum / 12.0))
        ps = min(3.0, max(0.02, ps))
        p_scale[i] = ps
        tsum, tmax, tmin = 0.0, -1e9, 1e9
        lying, snow, lost, ice_melt = 0.0, 0.0, 0.0, 0.0
        fs, ns = 0.0, 0
        bare = bare_share * f_alb[i]
        for k in range(12):
            m = (peak + 3 + k) % 12
            d_orb = k_orb[i] * 0.5 * (dq[b, m] + dq[b, (m + 11) % 12])
            sw = half[i] * math.cos(2 * math.pi * (m - peak) / 12.0)
            lit = min(1.0, lying / snow_w) if land[i] else 0.0
            f = lit + (1.0 - lit) * bare
            if sw > 0.0:
                fs += f
                ns += 1
                sw *= 1.0 - f * damp[i]
            t = t_mean[i] + dt_base[i] + sw + d_orb - f_ice[i] * cool
            if f > 0.0 and t > 0.0:
                t *= 1.0 - f * (1.0 - hold)
            tsum += t
            tmax = max(tmax, t)
            tmin = min(tmin, t)
            if land[i]:
                # snow share: all snow below -2 C, all rain above +2 C
                sf = min(1.0, max(0.0, 0.5 - t / 4.0))
                p = p_jul[i] if m < 6 else p_jan[i]
                fall = sf * p / 12.0 * ps  # mm w.e.
                snow += fall
                lying += fall
                x = t / sigma
                pdd = DAYS * (sigma / SQRT2PI * math.exp(-0.5 * x * x) + 0.5 * t * math.erfc(-x / math.sqrt(2.0)))
                melt = min(lying, ddf_snow * pdd)
                lying -= melt
                lost += (1.0 - refreeze) * melt
                ice_melt += ddf_ice * (pdd - melt / ddf_snow)
        t_ann[i], t_warm[i], t_cold[i] = tsum / 12.0, tmax, tmin
        f_sum[i] = fs / max(ns, 1)
        if land[i]:
            smb[i] = (snow - lost - ice_melt) / 917.0  # m of ice
        else:
            smb[i] = 0.0


@njit(cache=True, inline="always")
def _surf(bed, H, sl, flt, j):
    """Ice (or sea, or ground) surface: grounded ice sits on its bed,
    floating ice shows `flt` of its thickness above the sea."""
    return max(bed[j] + H[j], sl + flt * H[j])


@njit(cache=True)
def sia_flow(H, bed, sl, active, off, idx, dist, elen, ux, uy, uz, area, gamma, d_cap, dt_total, cfl, flt, d2min):
    """Shallow-ice flow for dt_total years: ice thickness diffuses with
    D = gamma H^5 |grad s|^2 (Glen's law, n = 3, no sliding), s the ice
    surface, so it flows downhill on its own surface slope and spreads under
    its own weight. Finite volumes: the flux across each side is
    D_side (s_i - s_j) / dist * side length, D_side the mean of the two
    cells' D (Mahaffy), |grad s| per cell from the Green-Gauss sum over its
    sides or its steepest way down, whichever is larger. Explicit sub-steps sized by the largest D (D capped at d_cap:
    at ~110 km cells a margin is one cliff-like step the model can't
    resolve). Outflow is limited to what a cell holds, so H stays >= 0 and
    ice is exactly conserved. Only the `active` cells (ice and a 2-cell
    ring around it) are visited. Returns the number of sub-steps."""
    na = active.shape[0]
    n = H.shape[0]
    D = np.zeros(n)
    out = np.zeros(n)
    dV = np.zeros(n)
    t = 0.0
    nsub = 0
    while t < dt_total - 1e-9:
        dmax = 0.0
        for a in range(na):
            i = active[a]
            if H[i] <= 0.0:
                D[i] = 0.0
                continue
            si = _surf(bed, H, sl, flt, i)
            gx, gy, gz = 0.0, 0.0, 0.0
            down2 = 0.0
            for e in range(off[i], off[i + 1]):
                sj = _surf(bed, H, sl, flt, idx[e])
                w = 0.5 * elen[e] * (sj - si)
                gx += w * ux[e]
                gy += w * uy[e]
                gz += w * uz[e]
                if sj < si:
                    down2 = max(down2, ((si - sj) / dist[e]) ** 2)
            # (the steepest way down, too: on a lone peak, a one-cell cap on an island, the Green-Gauss sum
            # of slopes on all sides cancels and the ice would pile up without flowing, 10+ km; PW-199)
            g2 = max((gx * gx + gy * gy + gz * gz) / (area[i] * area[i]), down2)
            h2 = H[i] * H[i]
            d = min(gamma * h2 * h2 * H[i] * g2, d_cap)
            D[i] = d
            dmax = max(dmax, d)
        if dmax <= 0.0:
            break
        dt = min(dt_total - t, cfl * d2min / dmax)
        # outflow per cell, to limit it to what the cell holds
        for a in range(na):
            i = active[a]
            out[i] = 0.0
            if H[i] <= 0.0:
                continue
            si = _surf(bed, H, sl, flt, i)
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                q = 0.5 * (D[i] + D[j]) * (si - _surf(bed, H, sl, flt, j)) * elen[e] / dist[e]
                if q > 0.0:
                    out[i] += q
        for a in range(na):
            i = active[a]
            if out[i] <= 0.0:
                continue
            # (written so a vanishing outflow, which can underflow to 0 for a
            # film of ice, never divides by zero)
            need = dt * out[i]
            held = H[i] * area[i]
            scale = 1.0 if need <= held else held / need
            si = _surf(bed, H, sl, flt, i)
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                q = 0.5 * (D[i] + D[j]) * (si - _surf(bed, H, sl, flt, j)) * elen[e] / dist[e]
                if q > 0.0:
                    v = q * scale * dt
                    dV[i] -= v
                    dV[j] += v
        for a in range(na):
            i = active[a]
            if dV[i] != 0.0:
                H[i] = max(0.0, H[i] + dV[i] / area[i])
                dV[i] = 0.0
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                if dV[j] != 0.0:
                    H[j] = max(0.0, H[j] + dV[j] / area[j])
                    dV[j] = 0.0
        t += dt
        nsub += 1
    return nsub


@njit(cache=True)
def dilate(mask, off, idx, rings):
    """Cells within `rings` steps of a True cell."""
    m = mask.copy()
    for _ in range(rings):
        new = m.copy()
        for i in range(m.shape[0]):
            if m[i]:
                for e in range(off[i], off[i + 1]):
                    new[idx[e]] = True
        m = new
    return m
