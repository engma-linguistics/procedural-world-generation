"""Valley floors of a fine zoom's alluvial rivers (PW-412).

The fine landscape pass is a stream-power profile from the imposed
courses: on its own it cuts a V straight down to a 1-px channel, even for a
300 m^3/s river at 0.04%, so a meander train had no room (PW-405 limits
its swing by the valley floor's half width). Here each alluvial reach
(zoom_fine._courses: gentle for its rock, braided or single-thread) gets a
floor round its valley axis (the smoothed course, before the meanders):

- width FLOOR_W channel widths (w = 4 Q^0.5 m) x the reach's alluvial share
  (1 on gentle reaches, 0 on bedrock / steep ones: a gorge keeps no floor)
  x sqrt(rock erodibility) (soft rock widens its valley faster): about
  ten widths each side on a lowland shale reach, five on a craton's;
- its surface FREEBOARD bankfull depths (d = 0.27 Q^0.39 m) above the
  course's water (the parent's water surface, as the channel pixels), so
  it falls down-valley as the river does and is nearly flat across it:
  natural levees (LEVEE depths at the bank, falling off over LEVEE_W
  widths), the backswamp beyond, rising TOE depths to the valley sides
  (their fans and colluvium);
- the meander belt inside it: the channel's width plus BELT_X x the
  meander train's amplitude each side (the swing the reach allows; ~12
  widths across at full swing), as wide as the floor on braided reaches.

The floor is held through the landscape pass (the hillslopes are shaped
from its edge) and counted in the parent's 3x3 block means: the volume cut
for it goes back onto the block's hillslopes (zoom_fine.block_gap). Where
a block is nearly all floor (a big river's plain) there is not enough
hillslope to take it: those blocks keep the floor's level, their error in
stats["floodplain"]["block_rms_error_m"]. A later time pass (PW-416)
migrates the channel inside the belt and floor: both are saved
(layers valley_floor, floor_m).
"""

from __future__ import annotations

import numpy as np
from numba import njit

FLOOR_W = 20.0  # an alluvial valley floor's width, channel widths (x sqrt of the rock's erodibility)
BELT_X = 2.0  # the meander belt: the channel's width plus this x the meander train's amplitude each side
FREEBOARD = 0.5  # the floor stands this x the bankfull depth above the course's (mean) water
LEVEE = 0.3  # natural levees: this x the bankfull depth above the floor at the bank ...
LEVEE_W = 2.0  # ... falling off over this many channel widths (the backswamp beyond)
TOE = 0.5  # the floor rises this x the bankfull depth to its margins
SMOOTH = 3  # 3x3 smoothing passes over the floor (its level jumps between axis samples)
HARMONIC_IT = 200  # its level's relaxation sweeps (from the nearest axis's: only the confluences move far)
CONF = 1.0  # beyond the parent's pixel scale a floor spreads only where the parent's ground (its 3x3 block
# means) stands within this many bankfull depths of its level


def depth(q):
    """Bankfull depth (m) of a river of mean discharge q m^3/s (hydraulic geometry)."""
    return 0.27 * np.maximum(q, 0.0) ** 0.39


def half_width(w_km, alluv, k_rock):
    """A reach's valley floor half width (km): w_km its channel width, alluv
    its alluvial share (0 bedrock .. 1 gentle), k_rock its rock's erodibility."""
    return 0.5 * FLOOR_W * w_km * alluv * np.sqrt(np.clip(k_rock, 0.3, 2.0))


@njit(cache=True)
def spread(E, A, blocked, nx, ny, gate, t3, near, conf, fb):
    """Max-plus chamfer spreading (raster sweeps, steps 1 and sqrt 2 px):
    E[i] = max over j of E[j] - d(i, j), never through blocked pixels; the
    attributes A[:, i] follow the winning source. gate (a floor's spread;
    A = level, width, depth, half width in px): beyond `near` px of its
    axis a source reaches a pixel only where t3 there is within conf x its
    depth of its floor (level + fb x depth). In place."""
    s2 = 1.41421356
    na = A.shape[0]
    for sweep in range(4 if gate else 2):
        fwd = sweep % 2 == 0
        for t in range(nx * ny):
            i = t if fwd else nx * ny - 1 - t
            if blocked[i]:
                continue
            r, c = i // nx, i % nx
            for k in range(4):
                if fwd:
                    dr, dc = (-1, -1, -1, 0)[k], (-1, 0, 1, -1)[k]
                else:
                    dr, dc = (1, 1, 1, 0)[k], (1, 0, -1, 1)[k]
                rr, cc = r + dr, c + dc
                if rr < 0 or rr >= ny or cc < 0 or cc >= nx:
                    continue
                j = rr * nx + cc
                if blocked[j]:
                    continue
                v = E[j] - (s2 if dr != 0 and dc != 0 else 1.0)
                if v > E[i]:
                    if gate and A[3, j] - v > near and t3[i] - (A[0, j] + fb * A[2, j]) > conf * A[2, j]:
                        continue
                    E[i] = v
                    for a in range(na):
                        A[a, i] = A[a, j]


@njit(cache=True)
def harmonic(z, held, mask, nx, ny, iters):
    """Over the mask, z relaxed to a harmonic surface (Gauss-Seidel, over-
    relaxed) with the held pixels fixed and no flow across the mask's edge.
    In place."""
    for _ in range(iters):
        for i in range(nx * ny):
            if not mask[i] or held[i]:
                continue
            r, c = i // nx, i % nx
            s = 0.0
            n = 0
            if r > 0 and mask[i - nx]:
                s += z[i - nx]
                n += 1
            if r < ny - 1 and mask[i + nx]:
                s += z[i + nx]
                n += 1
            if c > 0 and mask[i - 1]:
                s += z[i - 1]
                n += 1
            if c < nx - 1 and mask[i + 1]:
                s += z[i + 1]
                n += 1
            if n > 0:
                z[i] += 1.8 * (s / n - z[i])


def _spread(E, A, blocked, nb):
    spread(E, A, blocked, nb, nb, False, np.zeros(1), 0.0, 0.0, 0.0)


def floors(nb, res, src, hf, belt, z0, w, d, course, bed, q_ch, blocked, t3, near):
    """The valley floors round the axis samples src (fine pixel indices),
    each with its floor half width hf and belt half width belt (km), the
    course's water there z0 (m), channel width w (km), bankfull depth d (m).
    course, bed, q_ch: the channel pixels, their water and discharge;
    blocked: pixels no floor reaches (sea, lakes, gorges, cones); t3: the
    parent's ground, its 3x3 block means (bicubic): beyond near (km) of
    the axis a floor goes on only where they are within CONF bankfull depths
    of its level (a block mostly floor has too little hillslope to take the
    volume cut for it). Returns (floor mask, belt mask, floor surface m:
    also under the channels; nan elsewhere)."""
    npx = nb * nb
    o = np.argsort(hf)  # (the widest floor's sample wins a pixel)
    E = np.full(npx, -np.inf)
    A = np.zeros((4, npx))
    E[src[o]] = hf[o] / res
    A[:, src[o]] = np.vstack([z0, w, d, hf / res])[:, o]
    # (beyond `near`, a floor goes on only over the parent's low ground: gated in the spread, so it stays in
    # one piece and a tributary's narrower reach doesn't stop the main river's floor)
    spread(E, A, blocked, nb, nb, True, t3, near / res, CONF, FREEBOARD)
    A[3] *= res
    zc, wv, dv, hv = A
    from_axis = hv - E * res  # (km)
    on = (E >= 0) & (hv > 0) & ~blocked
    Eb = np.full(npx, -np.inf)
    Eb[src[o]] = np.where(belt[o] > 0, belt[o] / res, -np.inf)
    _spread(Eb, np.zeros((0, npx)), blocked | ~on, nb)
    # each channel pixel's own discharge (a wide channel's edge pixels: its centre line's), then the
    # distance to the nearest channel, its water and its size there (levees: a tributary's are its own)
    Eq = np.where(course & (q_ch > 0), 0.0, -np.inf)
    Aq = np.vstack([q_ch])
    _spread(Eq, Aq, ~course, nb)
    Ec = np.where(course, 0.0, -np.inf)
    Ac = np.vstack([np.where(course, bed, 0.0), np.where(course, Aq[0], 0.0)])
    _spread(Ec, Ac, blocked & ~course, nb)
    wc, dc = 4.0 * np.sqrt(np.maximum(Ac[1], 0.0)) / 1000.0, depth(Ac[1])
    frac = np.clip(from_axis / np.maximum(hv, 1e-9), 0.0, 1.0)  # (0 on the axis .. 1 at the margin)
    bank = np.maximum(-Ec * res - 0.5 * wc, 0.0)
    # the level: the axes' (their water plus the freeboard), spread smoothly between them (harmonic: where
    # two rivers' floors meet, at a confluence, no step between their levels)
    lev = zc + FREEBOARD * dv
    ax = np.zeros(npx, np.bool_)
    ax[src] = True
    ax &= on
    lev[src[o]] = (z0 + FREEBOARD * d)[o]
    harmonic(lev, ax, on, nb, nb, HARMONIC_IT)
    z = lev + dv * TOE * frac * frac + LEVEE * dc * np.exp(-bank / np.maximum(LEVEE_W * wc, 1e-9))
    z = np.where(on, z, np.nan)
    m = on.reshape(nb, nb)
    for _ in range(SMOOTH):  # (masked 3x3 mean)
        zz = np.where(m, z.reshape(nb, nb), 0.0)
        s = np.zeros_like(zz)
        n = np.zeros_like(zz)
        p = np.pad(zz, 1)
        pm = np.pad(m.astype(float), 1)
        for dr in range(3):
            for dc_ in range(3):
                s += p[dr:dr + nb, dc_:dc_ + nb]
                n += pm[dr:dr + nb, dc_:dc_ + nb]
        z = np.where(on, (s / np.maximum(n, 1)).ravel(), np.nan)
    # (never below the channel beside it: its water there plus a quarter of its depth)
    z = np.where(on, np.maximum(z, Ac[0] + 0.25 * dc), np.nan)
    return on, on & (Eb >= 0), z
