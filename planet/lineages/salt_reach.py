"""Salt reach (PW-745, light first pass): how far a people is from salt once trade is counted.

`seafood.salt` gives each land cell its land distance to the nearest source (`_salt_km`, one hop = one cell step, bent by
ROUTE). Here the same graph is walked as a cost-distance: a step along a river (both cells carry a river) costs RIVER_COST of
its length (boats and towpaths), a step inside a contact zone (a land cell next to a land cell of another people, and the ring
around it: where the peoples meet and trade) costs TRADE_COST, any other step the full length. A cell whose own walk to salt
is within `traded_km` has salt; one beyond it but within TRADE_CAP_KM of cost-distance gets it by trade (dear); the rest are
cut off (traders do not carry salt further than that). Nothing here makes salt, salts food or moves people: it only reads.
"""
from __future__ import annotations

import numpy as np
from numba import njit

from ..geo import R_KM
from ..hydrology import discharge

RIVER_COST = 0.5  # a river step costs this share of a land step
TRADE_COST = 0.6  # so does a step in a contact zone (peoples that meet carry goods across)
TRADE_CAP_KM = 450.0  # cost-km: salt is not traded further than this from its source (1.5x the km people walk for it)
RIVER_Q = 200.0  # m3/s: a river this big is a route (boats, towpaths) (JUDGEMENT, as seafood.LICK_Q; PW-820: the old 2 cells of runoff at L7)
UNREACHED = 5000.0
ROUTE = 1.3  # as seafood.ROUTE
MINED_CAP = 1.6  # salt a mining people works, or its colony (mining.py), is traded this much further (cost-km) than the salt of unworked beds: a mine is a salt works
WORKS_CAP = 1.25  # salt any other settled people works from the beds in its country (a salt works, PW-854): traded this much further, a little less than a mining people's


@njit(cache=True)
def _spfa(sources, cost, nbr_off, nbr_idx, hop_km, limit):
    """Multi-source shortest cost-distance over the cells where cost > 0 (the multiplier of a step between two cells is
    the larger of theirs); cells beyond `limit` stay at limit + 1 (unreached)."""
    n = cost.shape[0]
    d = np.full(n, limit + 1.0)
    inq = np.zeros(n, np.bool_)
    cap = n * 8
    q = np.empty(cap, np.int64)
    head, tail, size = 0, 0, 0
    for s in sources:
        d[s] = 0.0
        q[tail % cap] = s
        tail += 1
        size += 1
        inq[s] = True
    while size > 0:
        i = q[head % cap]
        head += 1
        size -= 1
        inq[i] = False
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if cost[j] <= 0.0:
                continue
            nd = d[i] + hop_km * max(cost[j], cost[i])
            if nd < d[j] and nd <= limit:
                d[j] = nd
                if not inq[j]:
                    inq[j] = True
                    q[tail % cap] = j
                    tail += 1
                    size += 1
    return d


def contact_zone(g, land: np.ndarray, peoples: np.ndarray, sea_lines: np.ndarray) -> np.ndarray:
    """Land cells next to a land cell led by another (land) people, and the ring around them."""
    pe = peoples.astype(int)
    p = np.where(land & (peoples != 255) & ~sea_lines[np.minimum(pe, len(sea_lines) - 1)], pe, -1)
    src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    a, b = p[src], p[g.nbr_idx]
    edge = np.zeros(g.n, bool)
    edge[src[(a >= 0) & (b >= 0) & (a != b)]] = True
    ring = np.logical_or.reduceat(edge[g.nbr_idx], g.nbr_off[:-1]) | edge
    return ring & land


def reach(g, land: np.ndarray, own_km: np.ndarray, flow: np.ndarray, zone: np.ndarray, traded_km: float,
          cap_km: float = TRADE_CAP_KM, mined: np.ndarray | None = None, works: np.ndarray | None = None) -> dict:
    """Per cell: `km` (cost-distance to salt; UNREACHED beyond the cap or where a landmass has no salt) and `how`
    (0 not land, 1 own: within `traded_km` on foot, 2 traded: beyond it but within the cap, 3 cut off).
    `mined`: cells that are a salt mine (a source worked by a mining people or its colony): their salt is traded MINED_CAP x further;
    `works`: the salt works of any other settled people on beds in its country, WORKS_CAP x further; `gain` marks the cells that
    are traded only thanks to either."""
    src = np.flatnonzero(land & (own_km == 0))
    cost = np.where(land, 1.0, 0.0)
    cost = np.where(land & zone, TRADE_COST, cost)
    cost = np.where(land & (discharge(g, flow) >= RIVER_Q), np.minimum(cost, RIVER_COST), cost)
    hop_km = float(g.spacing * R_KM * ROUTE)
    km = _spfa(src.astype(np.int64), cost, g.nbr_off.astype(np.int64), g.nbr_idx.astype(np.int64), hop_km, UNREACHED - 1.0)
    km = np.where(land & (km <= UNREACHED - 1.0), km, UNREACHED)
    how = np.zeros(g.n, np.int8)
    how[land] = np.where(own_km[land] <= traded_km, 1, np.where(km[land] <= cap_km, 2, 3))
    gain = np.zeros(g.n, bool)
    for cells, mult in ((works, WORKS_CAP), (mined, MINED_CAP)):  # (the further reach second: a mine beats a plain works)
        if cells is not None and (cells & land & (own_km == 0)).any():
            msrc = np.flatnonzero(cells & land & (own_km == 0))
            km_m = _spfa(msrc.astype(np.int64), cost, g.nbr_off.astype(np.int64), g.nbr_idx.astype(np.int64), hop_km, UNREACHED - 1.0)
            new = land & (how == 3) & (km_m <= cap_km * mult)
            how[new] = 2
            km = np.where(new, km_m, km)
            gain |= new
    return {"km": km, "how": how, "gain": gain}
