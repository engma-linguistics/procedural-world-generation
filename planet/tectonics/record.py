"""Each cell's geological record: its top strata in order, and the dated
events that shaped its crust. It rides with the plate like the rest of the
crust (Plates.rec, Plates.lith, in the plate's own frame), so a rifted
margin carried across an ocean still knows when it rifted.

Strata
------
The sediment cover (Plates.cover, its well-mixed composition in
isostasy.EXTRA) stays the mass balance that erosion, isostasy and the
budget use. The strata record how that cover is layered: K layers, top
first, each with a thickness (km), a lithology (a surface.ROCKS id: shale,
sandstone, limestone, dolomite, evaporite, coal, flood basalt, tuff,
quartzite) and the time it last grew (Myr). The layers always add up to the
cover; the bottom one takes whatever the record can't resolve (older cover
merged into it, the set-up's blanket, sampling fixes), see reconcile().

- Deposits go on top (add_top). A deposit continues the top layer if it's
  the same rock and the top is still growing (last grew within HIATUS);
  a thin, still-growing top (< MIN_KM) is absorbed into the deposit (the
  thicker of the two names it: thin interbeds aren't resolved). Otherwise
  it starts a new layer, and if the stack is full the two bottom layers
  merge.
- Erosion takes from the top (remove_top); burial into the basement from
  the bottom (remove_bottom).
- A layer is folded if it last grew before the cell's last folding
  (t_fold): later layers lie flat on the unconformity above it.
- Diagenesis and metamorphism: limestone buried under DOLOMITE_BURIAL_KM
  turns to dolomite; sandstone folded in thick (> QUARTZITE_CRUST_KM)
  crust to quartzite (fold()).

History
-------
  t_rift       Myr: when the crust was last stretched by a rift (crust.stretch)
  rift_strain  how much it was stretched in that episode: ln(thickness
               before / after), ln(beta) (0.4: thinned by a third)
  t_fold       Myr: when it was last folded/thrust (a collision, an
               accretionary wedge)
  fold_km      km of sediment cover folded in that episode (sets the fold
               wavelength)
  fold_strain  km of crust stacked onto the cell in that episode (how hard
               it was squeezed: sets the dips)
  exhumed      km of rock eroded off since the basement last formed or was
               remade (arc, collision, birth): deep roots come up
  t_ice        Myr: when it was last under land ice
Times are absolute (Myr since the run began; NEVER: not yet).
"""

from __future__ import annotations

import numpy as np
from numba import njit

from ..surface import DOLOMITE, LIMESTONE, QUARTZITE, SANDSTONE, SHALE

K = 3  # strata per cell
RECORD = tuple(f"km{j}" for j in range(K)) + tuple(f"t{j}" for j in range(K)) + (
    "t_rift", "rift_strain", "t_fold", "fold_km", "fold_strain", "exhumed", "t_ice")
KM, T = slice(0, K), slice(K, 2 * K)
T_RIFT, RIFT_STRAIN, T_FOLD, FOLD_KM, FOLD_STRAIN, EXHUMED, T_ICE = range(2 * K, 2 * K + 7)
NEVER = -1.0e6

MIN_KM = 0.05  # km: a growing top layer thinner than this is absorbed by the next deposit
HIATUS = 20.0  # Myr: a layer that hasn't grown for this long is closed (the next deposit starts a new one)
DOLOMITE_BURIAL_KM = 1.0  # km of overburden that turns limestone into dolomite
QUARTZITE_CRUST_KM = 45.0  # km of crust: sandstone folded in crust this thick is metamorphosed
FOLD_EPISODE = 50.0  # Myr: folding (or rifting) again within this long continues the same episode


def blank() -> np.ndarray:
    """The record of crust that has none yet (new sea floor)."""
    row = np.zeros(len(RECORD), np.float32)
    row[T] = NEVER
    row[[T_RIFT, T_FOLD, T_ICE]] = NEVER
    return row


def empty(shape) -> tuple[np.ndarray, np.ndarray]:
    """(rec, lith) arrays of the given leading shape, all blank."""
    rec = np.empty((*shape, len(RECORD)), np.float32)
    rec[...] = blank()
    return rec, np.zeros((*shape, K), np.uint8)


# ---------------------------------------------------------------------------
# the stack (per cell, on world-view arrays rec (n, R) and lith (n, K))
# ---------------------------------------------------------------------------
@njit(cache=True)
def _push(rec, lith, i, km, rock, t):
    """A new top layer on cell i (the two bottom layers merge if full)."""
    last = K - 1  # the slot the shift fills from above
    if rec[i, K - 1] > 0:
        a, b = rec[i, K - 2], rec[i, K - 1]
        if a > b:
            lith[i, K - 1] = lith[i, K - 2]
        rec[i, K - 1] = a + b
        rec[i, 2 * K - 1] = max(rec[i, 2 * K - 2], rec[i, 2 * K - 1])
        last = K - 2
    for j in range(last, 0, -1):
        rec[i, j] = rec[i, j - 1]
        rec[i, K + j] = rec[i, K + j - 1]
        lith[i, j] = lith[i, j - 1]
    rec[i, 0] = km
    rec[i, K] = t
    lith[i, 0] = rock


@njit(cache=True)
def add_top(rec, lith, add, rock, t):
    """Deposit add[i] km of rock[i] on top of each cell, at time t."""
    for i in range(rec.shape[0]):
        a = add[i]
        if a <= 0:
            continue
        r = rock[i]
        if rec[i, 0] <= 0:
            for j in range(K):  # (an emptied stack: start afresh)
                rec[i, j] = 0.0
            rec[i, 0] = a
            rec[i, K] = t
            lith[i, 0] = r
            continue
        growing = t - rec[i, K] <= HIATUS and rec[i, K] > rec[i, T_FOLD]
        if growing and lith[i, 0] == r:
            rec[i, 0] += a
            rec[i, K] = t
        elif growing and rec[i, 0] < MIN_KM:
            if a > rec[i, 0]:
                lith[i, 0] = r
            rec[i, 0] += a
            rec[i, K] = t
        else:
            _push(rec, lith, i, a, r, t)


@njit(cache=True)
def _shift_up(rec, lith, i):
    for j in range(K - 1):
        rec[i, j] = rec[i, j + 1]
        rec[i, K + j] = rec[i, K + j + 1]
        lith[i, j] = lith[i, j + 1]
    rec[i, K - 1] = 0.0
    rec[i, 2 * K - 1] = NEVER
    lith[i, K - 1] = 0


@njit(cache=True)
def remove_top(rec, lith, rem):
    """Erode rem[i] km off the top of each cell's strata."""
    for i in range(rec.shape[0]):
        r = rem[i]
        while r > 0 and rec[i, 0] > 0:
            take = min(r, rec[i, 0])
            rec[i, 0] -= take
            r -= take
            if rec[i, 0] <= 1e-7:
                _shift_up(rec, lith, i)


@njit(cache=True)
def remove_bottom(rec, lith, rem):
    """Take rem[i] km off the bottom of each cell's strata (buried into the basement)."""
    for i in range(rec.shape[0]):
        r = rem[i]
        j = K - 1
        while r > 0 and j >= 0:
            if rec[i, j] > 0:
                take = min(r, rec[i, j])
                rec[i, j] -= take
                r -= take
                if rec[i, j] <= 1e-7:
                    rec[i, j] = 0.0
                    rec[i, K + j] = NEVER
                    lith[i, j] = 0
            j -= 1


@njit(cache=True)
def reconcile(rec, lith, cover, rock, t, tol=1e-5):
    """Make each cell's strata add up to its cover (km): what's missing goes
    into the bottom layer (or, with no strata, becomes one layer of rock[i]
    dated t), what's too much comes off the bottom."""
    for i in range(rec.shape[0]):
        s = 0.0
        deepest = -1
        for j in range(K):
            if rec[i, j] > 0:
                s += rec[i, j]
                deepest = j
        d = cover[i] - s
        if cover[i] <= tol:
            for j in range(K):
                rec[i, j] = 0.0
                rec[i, K + j] = NEVER
                lith[i, j] = 0
        elif d > tol:
            if deepest < 0:
                rec[i, 0] = d
                rec[i, K] = t
                lith[i, 0] = rock[i]
            else:
                rec[i, deepest] += d
        elif d < -tol:
            r = -d
            j = K - 1
            while r > 0 and j >= 0:
                if rec[i, j] > 0:
                    take = min(r, rec[i, j])
                    rec[i, j] -= take
                    r -= take
                    if rec[i, j] <= 1e-7:
                        rec[i, j] = 0.0
                        rec[i, K + j] = NEVER
                        lith[i, j] = 0
                j -= 1


@njit(cache=True)
def diagenesis(rec, lith):
    """Limestone buried under DOLOMITE_BURIAL_KM of younger strata turns to
    dolomite (a hard carbonate caprock once it's exhumed again)."""
    for i in range(rec.shape[0]):
        above = 0.0
        for j in range(K):
            if rec[i, j] <= 0:
                break
            if lith[i, j] == LIMESTONE and above >= DOLOMITE_BURIAL_KM:
                lith[i, j] = DOLOMITE
            above += rec[i, j]


@njit(cache=True)
def fold(rec, lith, squeezed, strain, cover, crust, t):
    """Fold and thrust the strata of the squeezed cells (strain: km of crust
    stacked on each this step): date the folding, measure the episode, and
    metamorphose sandstone in thick crust into quartzite."""
    for i in range(rec.shape[0]):
        if not squeezed[i]:
            continue
        if t - rec[i, T_FOLD] > FOLD_EPISODE:
            rec[i, FOLD_STRAIN] = 0.0
            rec[i, FOLD_KM] = 0.0
        rec[i, T_FOLD] = t
        rec[i, FOLD_STRAIN] += strain[i]
        rec[i, FOLD_KM] = max(rec[i, FOLD_KM], cover[i])
        if crust[i] > QUARTZITE_CRUST_KM:
            for j in range(K):
                if rec[i, j] > 0 and lith[i, j] == SANDSTONE:
                    lith[i, j] = QUARTZITE


def rift(rec, rifting, strain, t):
    """Date the rifting of the cells being stretched and add up their
    stretching (strain: ln(beta) of this step) over the episode."""
    new = rifting & (t - rec[:, T_RIFT] > FOLD_EPISODE)
    rec[new, RIFT_STRAIN] = 0.0
    rec[rifting, T_RIFT] = t
    rec[rifting, RIFT_STRAIN] += strain[rifting]


def top(rec, lith, basement, veneer=0.0):
    """What's exposed and what's under it: (rock, km, folded?, last grew,
    rock below), per cell. The top is the first layer thicker than veneer
    km (thin veneers are looked through), else the basement (km 0)."""
    n = len(basement)
    km, t, L = rec[:, KM], rec[:, T], lith
    thick = km > veneer
    j = np.where(thick.any(1), thick.argmax(1), K)
    i = np.arange(n)
    jj = np.minimum(j, K - 1)
    has = j < K
    rock = np.where(has, L[i, jj], basement).astype(np.uint8)
    top_km = np.where(has, km[i, jj], 0.0)
    top_t = np.where(has, t[i, jj], NEVER)
    folded = has & (top_t <= rec[:, T_FOLD])
    j2 = np.minimum(j + 1, K - 1)
    below_has = has & (j + 1 < K) & (km[i, j2] > 0)
    below = np.where(below_has, L[i, j2], basement).astype(np.uint8)
    return rock, top_km, folded, top_t, below


def default_rock(cover, mix):
    """The rock a stretch of cover with no record is taken to be: its main
    ingredient (surface.surface_rock's rule without the basement)."""
    from ..surface import MIX_ROCKS
    parts = np.column_stack([mix, np.maximum(cover - mix.sum(1), 0)])
    return np.append(MIX_ROCKS, SHALE)[np.argmax(parts, axis=1)].astype(np.uint8)
