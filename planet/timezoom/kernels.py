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
from numba import njit, prange

DAYS = 365.25 / 12  # days per month
SQRT2PI = math.sqrt(2 * math.pi)


@njit(cache=True, parallel=True)
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
    mean brightness (0..1) over the summer months. Cells are independent
    (prange, no reductions across cells): the same bits at any thread count."""
    n = t_mean.shape[0]
    for i in prange(n):
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
                ds = ddf_snow
                melt = min(lying, ds * pdd)
                lying -= melt
                lost += (1.0 - refreeze) * melt
                ice_melt += ddf_ice * (pdd - melt / ds)
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


@njit(cache=True, inline="always")
def _held(bed, H, sl, flt, hold, i, j):
    """What's left (1 - hold[i]) of cell i's flow into cell j where ice
    would float on j (across i's grounding line), else 1."""
    if hold[i] > 0.0 and bed[j] < sl and (1.0 - flt) * H[j] <= sl - bed[j]:
        return 1.0 - hold[i]
    return 1.0


@njit(cache=True)
def _sia_receivers(active, off, idx, n):
    """Which cells each sub-step's volume changes land on, and in what
    order: for target cell c, the directed edges whose transfer it receives
    (+) or gives (-), in the order a loop over `active` and each cell's edges
    would add them up (so a parallel gather over the targets sums exactly as
    that loop does: bit-identical, whatever the thread count). Returns
    (targets, rec_off, rec_e, rec_give), the records of targets[t] at
    rec_off[t]:rec_off[t + 1]."""
    cnt = np.zeros(n, np.int64)
    for a in range(active.shape[0]):
        i = active[a]
        for e in range(off[i], off[i + 1]):
            cnt[i] += 1
            cnt[idx[e]] += 1
    targets = np.flatnonzero(cnt)
    slot = np.full(n, -1, np.int64)
    rec_off = np.zeros(targets.shape[0] + 1, np.int64)
    for t in range(targets.shape[0]):
        slot[targets[t]] = t
        rec_off[t + 1] = rec_off[t] + cnt[targets[t]]
    fill = rec_off[:-1].copy()
    rec_e = np.empty(rec_off[-1], np.int64)
    rec_give = np.empty(rec_off[-1], np.bool_)
    for a in range(active.shape[0]):
        i = active[a]
        for e in range(off[i], off[i + 1]):
            r = fill[slot[i]]
            rec_e[r], rec_give[r] = e, True
            fill[slot[i]] += 1
            r = fill[slot[idx[e]]]
            rec_e[r], rec_give[r] = e, False
            fill[slot[idx[e]]] += 1
    return targets, rec_off, rec_e, rec_give


@njit(cache=True, parallel=True)
def sia_flow(H, bed, sl, active, off, idx, dist, elen, ux, uy, uz, area, gamma, d_cap, dt_total, cfl, flt, d2min, hold,
             rate, applied, B, U, UL, W, tau_y, drop):
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
    ring around it) are visited. hold (per cell, 0..1): the share of a
    grounded front's flow across its grounding line (into cells where ice
    floats) its ice shelf holds back (buttressing, PW-367;
    timezoom.shelf_cover). rate (m/yr per cell): the surface mass
    balance, applied to the active cells within each sub-step (not below
    zero thickness; `applied` gets the m it changed each cell by), so a
    margin's melt and the flow feeding it act together (PW-366: applied
    once before the step's flow, a ~1 km margin could melt out in one
    500-yr step, or the flow left a film of ice beyond the front that the
    next step's balance saw as the margin, so the front cell took the
    interior's snow, PW-422). Returns the number of sub-steps.
    Each pass is per cell (prange); the volume moved along each edge is
    gathered by the cells it reaches in a fixed order (_sia_receivers), so
    the result doesn't depend on the thread count (PW-215).

    Glacial debris (PW-037): B (m of rock per cell, carried in the ice)
    moves with the ice, each transfer taking the share of the cell's debris
    that it takes of the cell's ice; where the balance thins the ice, the
    melted share of its debris is dropped (into `drop`, m). U (m) adds up
    the depth-averaged speed D |grad s| / H times each sub-step's length
    (U / dt_total: the step's mean, m/yr), and UL the same speed at a basal
    shear stress (rho g H |grad s|) of at most tau_y (Pa): the shallow-ice
    speed goes as tau^3 H, so where tau passes tau_y it is x (tau_y / tau)^3
    (glacial_erosion: a bed holds at most its yield stress), and W (Pa m)
    the work the flow does on its bed, that stress x that speed x time (the
    heat of sliding and of the shearing near the bed, W / dt_total / yr: W/m2)."""
    na = active.shape[0]
    n = H.shape[0]
    D = np.zeros(n)
    vE = np.empty(idx.shape[0])  # volume moved along each edge this sub-step (-1: none)
    bE = np.zeros(idx.shape[0])  # debris moved with it (m3)
    spd = np.zeros(n)
    lim = np.zeros(n)
    tbc = np.zeros(n)
    targets, rec_off, rec_e, rec_give = _sia_receivers(active, off, idx, n)
    nt = targets.shape[0]
    t = 0.0
    nsub = 0
    while t < dt_total - 1e-9:
        for a in prange(na):
            i = active[a]
            if H[i] <= 0.0:
                D[i] = 0.0
                spd[i] = 0.0
                lim[i] = 0.0
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
            D[i] = min(gamma * h2 * h2 * H[i] * g2, d_cap)
            gs = math.sqrt(g2)
            spd[i] = D[i] * gs / H[i]
            tb = RHO_G * H[i] * gs
            lim[i] = spd[i] if tb <= tau_y else spd[i] * (tau_y / tb) ** 3
            tbc[i] = min(tb, tau_y)
        dmax = 0.0
        for a in range(na):
            dmax = max(dmax, D[active[a]])
        if dmax <= 0.0:  # (no flow: the rest of the step's balance at once)
            dt = dt_total - t
            _balance(H, active, rate, applied, dt, B, drop)
            break
        dt = min(dt_total - t, cfl * d2min / dmax)
        # each cell's outflow, limited to what the cell holds, and so what moves along each of its edges
        for a in prange(na):
            i = active[a]
            for e in range(off[i], off[i + 1]):
                vE[e] = -1.0
            if H[i] <= 0.0:
                continue
            si = _surf(bed, H, sl, flt, i)
            out = 0.0
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                q = 0.5 * (D[i] + D[j]) * (si - _surf(bed, H, sl, flt, j)) * elen[e] / dist[e]
                if q > 0.0:
                    out += q * _held(bed, H, sl, flt, hold, i, j)
            if out <= 0.0:
                continue
            # (written so a vanishing outflow, which can underflow to 0 for a
            # film of ice, never divides by zero)
            need = dt * out
            held = H[i] * area[i]
            scale = 1.0 if need <= held else held / need
            U[i] += dt * spd[i]
            UL[i] += dt * lim[i]
            W[i] += dt * lim[i] * tbc[i]
            rock = B[i] * area[i]  # m3 of debris in the cell
            for e in range(off[i], off[i + 1]):
                j = idx[e]
                q = 0.5 * (D[i] + D[j]) * (si - _surf(bed, H, sl, flt, j)) * elen[e] / dist[e]
                if q > 0.0:
                    vE[e] = q * _held(bed, H, sl, flt, hold, i, j) * scale * dt
                    # (the debris: its share of the ice; a film of ice never overflows)
                    bE[e] = rock * min(vE[e] / held, 1.0) if rock > 0.0 and held > 0.0 else 0.0
        # every cell that gives or receives: its net change, then its thickness
        for k in prange(nt):
            c = targets[k]
            dv = 0.0
            db = 0.0
            for r in range(rec_off[k], rec_off[k + 1]):
                v = vE[rec_e[r]]
                if v >= 0.0:
                    if rec_give[r]:
                        dv -= v
                        db -= bE[rec_e[r]]
                    else:
                        dv += v
                        db += bE[rec_e[r]]
            if dv != 0.0:
                H[c] = max(0.0, H[c] + dv / area[c])
            if db != 0.0:
                B[c] = max(0.0, B[c] + db / area[c])
        _balance(H, active, rate, applied, dt, B, drop)
        t += dt
        nsub += 1
    return nsub


@njit(cache=True, inline="always")
def _balance(H, active, rate, applied, dt, B, drop):
    """The surface mass balance over dt years on the active cells (sia_flow);
    melt drops its share of the column's debris B into drop."""
    for a in range(active.shape[0]):
        i = active[a]
        if rate[i] != 0.0:
            h = max(0.0, H[i] + rate[i] * dt)
            if h < H[i] and B[i] > 0.0:
                x = B[i] * (1.0 - h / H[i])
                B[i] -= x
                drop[i] += x
            applied[i] += h - H[i]
            H[i] = h


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


RHO_G = 917.0 * 9.81  # ice's weight per m3 (N)
YEAR_S = 3.15576e7  # s per yr
K_ICE = 2.1  # W/m/K, ice's thermal conductivity
KAPPA_ICE = 36.0  # m2/yr, its thermal diffusivity (1.15e-6 m2/s)
PMP = 8.7e-4  # C per m of ice: the pressure-melting point's fall (air-saturated ice)


@njit(cache=True, inline="always")
def thawed(h, t_s, acc, geo):
    """Share (0..1) of a column's bed at the melting point: Robin's (1955)
    steady column with geothermal flux geo (W/m2) under an accumulation
    rate acc (m/yr of ice; snow sinking through the ice carries the
    surface's cold down), pure conduction where acc <= 0; the base is
    t_s + (geo/k) L (sqrt(pi)/2) erf(h/L) warm, L = sqrt(2 kappa h / acc).
    A 2 C ramp below the melting point (-PMP h) to frozen."""
    g = geo / K_ICE  # C per m
    if acc > 1e-6:
        L = math.sqrt(2.0 * KAPPA_ICE * h / acc)
        rise = g * L * 0.886226925 * math.erf(h / L)
    else:
        rise = g * h
    return min(max(1.0 + (t_s + rise + PMP * h) / 2.0, 0.0), 1.0)


@njit(cache=True)
def glacial_erosion(H, bed, sl, flt, active, off, idx, uacc, wacc, t_s, acc, geo, slide, erod, k_g, l_exp,
                    adverse, dt, deep, cut, wet):
    """Glacial erosion over a step of dt years (PW-037), m of bed per cell
    into cut: k_g x erod x ub^l_exp x dt (Hallet's abrasion law), on
    grounded ice, and the thawed share of each grounded cell's bed into wet.
    ub (m/yr), the sliding speed: slide x the shallow-ice speed at a basal
    shear stress of at most the bed's yield stress (uacc / dt: the step's
    mean, sia_flow's UL) x the thawed share of the bed. A bed holds at
    most its yield stress (Nye's plastic bed, ~100 kPa; ice sheets' basal
    stresses are 50-150 kPa, Cuffey & Paterson 2010), so where the
    shallow-ice slope asks more (the grid's cliff-like margins, a
    collapsing or surging sheet) the ice slides as at the yield stress, and
    the rest of its fall is unresolved margin, not faster abrasion. The bed
    is thawed (thawed: t_s the ice surface's annual mean, C; acc the
    accumulation, m/yr) by the geothermal flux geo (W/m2) and the flow's
    own heat at its bed (wacc / dt: sia_flow's W, Pa m/yr; the heat of
    sliding and of the shear near the bed, Cuffey & Paterson 2010 ch. 9:
    ~0.1-1 W/m2 under fast ice, so fast outlets are warm-based and slow
    cold domes frozen). Where
    the bed rises toward the ice's way down (its surface's steepest
    descent) more steeply than `adverse` x the surface falls, meltwater
    flowing up out of the basin supercools and freezes (Alley et al. 2003),
    so the basin stops deepening: the bound on an overdeepening. Not on a
    bed deeper than `deep` below the sea (the time zoom calves such ice at
    once: calve_depth, PW-199)."""
    for a in range(active.shape[0]):
        i = active[a]
        cut[i] = 0.0
        wet[i] = 0.0
        if H[i] <= 1.0 or bed[i] + H[i] <= sl + flt * H[i] or sl - bed[i] > deep:
            continue
        wet[i] = thawed(H[i], t_s[i], acc[i], geo + wacc[i] / dt / YEAR_S)
        if uacc[i] <= 0.0 or wet[i] <= 0.0:
            continue
        ub = slide * uacc[i] / dt * wet[i]
        si = _surf(bed, H, sl, flt, i)
        best = 0.0
        jd = -1
        for e in range(off[i], off[i + 1]):
            fall = si - _surf(bed, H, sl, flt, idx[e])
            if fall > best:
                best = fall
                jd = idx[e]
        if jd >= 0 and bed[jd] - bed[i] > adverse * best:
            continue
        cut[i] = k_g * erod[i] * ub ** l_exp * dt


@njit(cache=True)
def hop_scatter(m, off, idx, w, keep, hops, out):
    """Spread the amounts m (any conserved quantity per cell, e.g. m3) over
    up to `hops` hops along the directed edges: at each hop a cell lays
    down the share `keep` where it is and passes the rest to its neighbours
    in proportion to the edge weights w (>= 0); a cell with no weight
    (a sink, the end of a route) lays down all it holds, and so does the
    last hop. Adds to out; sum(out) = sum(m)."""
    n = m.shape[0]
    cur = m.copy()
    nxt = np.zeros(n)
    for h in range(hops):
        nxt[:] = 0.0
        last = h == hops - 1
        for i in range(n):
            c = cur[i]
            if c <= 0.0:
                continue
            s = 0.0
            for e in range(off[i], off[i + 1]):
                s += w[e]
            if s <= 0.0 or last:
                out[i] += c
                continue
            out[i] += keep * c
            r = (1.0 - keep) * c / s
            for e in range(off[i], off[i + 1]):
                if w[e] > 0.0:
                    nxt[idx[e]] += r * w[e]
        cur, nxt = nxt, cur
