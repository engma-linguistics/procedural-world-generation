"""PW-820: the culinary water goods ask a physical question (m3/s, km2, km), so the same ground gives the same answer at
L6 and L7. The measured agreement on refined pairs is in docs/review/pw820-water-units/README.md (tools/water_units_check.py)."""

import numpy as np
import pytest

from planet import coastform as CF
from planet.geo import R_KM
from planet.grid import shared_grid
from planet.hydrology import discharge
from planet.lineages import land as LD
from planet.lineages import seafood as SF
from planet.lineages.gridops import nbr_reduce

LEVELS = (6, 7)


@pytest.fixture(scope="module")
def grids():
    return {lv: shared_grid(lv) for lv in LEVELS}


def _flow_for(g, q):
    """The `flow` layer value that is q m3/s on grid g."""
    return q / float(discharge(g, np.array([1.0]))[0])


def _river(g, q_mouth, length_km):
    """A straight river of q_mouth m3/s from an inland cell to a sea cell (a geodesic chain of cells), all its cells at that discharge:
    returns (layers, land, coast, chain from the mouth upstream)."""
    n = g.n
    a = int(np.argmax(g.centers[:, 2]))  # (the north pole cell: the sea)
    land = np.ones(n, bool)
    land[a] = False
    chain = [a]
    hop = g.spacing * R_KM
    for _ in range(int(round(length_km / hop)) + 1):  # (walk south: each step the neighbour furthest from the pole)
        i = chain[-1]
        nb = g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]
        chain.append(int(nb[np.argmin(g.centers[nb, 2])]))
    down = np.full(n, -1)
    for up, dn in zip(chain[1:], chain[:-1]):
        down[up] = dn
    L = {"flow": np.where(np.isin(np.arange(n), chain[1:]), _flow_for(g, q_mouth), 0.0), "downstream": down,
         "temperature": np.full(n, 5.0), "river_frozen": np.zeros(n), "lake": np.zeros(n), "lake_kind": np.zeros(n, int)}
    coast = land & nbr_reduce(g, np.logical_or, (~land)[g.nbr_idx])
    return L, land, coast, chain[1:]


def _get(L, n):
    return lambda k: np.asarray(L[k], float) if k in L else np.zeros(n)


@pytest.mark.parametrize("q", [150.0, 450.0, 2000.0])
def test_a_river_of_the_same_discharge_has_the_same_run_at_both_levels(grids, q):
    out = {}
    for lv, g in grids.items():
        L, land, coast, chain = _river(g, q, 600.0)
        r = SF.seafood(g, L, land, coast, _get(L, g.n))["fish_run"]
        hop = g.spacing * R_KM
        k = int(round(480.0 / hop))  # (the cell ~480 km upstream)
        out[lv] = (r[chain[0]], r[chain[k]], k * hop)
    (m6, u6, d6), (m7, u7, d7) = out[6], out[7]
    assert m6 == pytest.approx(m7, abs=1e-9)
    assert (m6 > 0) == (q >= SF.RUN_Q[0])
    if m6 > 0:  # (carried upstream at one e-folding distance in km, not per cell: the same at the same km)
        assert u6 / m6 == pytest.approx(np.exp(-d6 / SF.RUN_EFOLD_KM), rel=1e-6)
        assert u7 / m7 == pytest.approx(np.exp(-d7 / SF.RUN_EFOLD_KM), rel=1e-6)


def test_the_lick_threshold_is_a_discharge(grids):
    for lv, g in grids.items():
        L, land, coast, chain = _river(g, SF.LICK_Q * 1.05, 300.0)
        L.update(surface_rock=np.full(g.n, 8.0), salinity=np.zeros(g.n), precipitation=np.full(g.n, 800.0), pet=np.full(g.n, 600.0),
                 coast_type=np.zeros(g.n), sst_jul=np.full(g.n, 10.0), res_salt=np.zeros(g.n), spring=np.zeros(g.n))
        lick = SF.salt(g, L, land, coast, _get(L, g.n))["salt_lick"]
        assert (lick[chain] == SF.LICK).all(), lv
        L["flow"] = L["flow"] * 0.9  # (now just under the threshold)
        assert SF.salt(g, L, land, coast, _get(L, g.n))["salt_lick"].max() == 0, lv


def test_a_lake_and_an_island_of_the_same_area_read_alike(grids):
    for k6 in (1, 2):  # (a lake of k6 L6 cells is 4 x k6 L7 cells: the same km2)
        fish = {}
        for lv, g in grids.items():
            k = k6 * 4 ** (lv - 6)
            cells = _blob(g, k)
            n = g.n
            L = {"lake": np.isin(np.arange(n), cells).astype(float), "lake_kind": np.where(np.isin(np.arange(n), cells), 1, 0),
                 "downstream": np.full(n, -1)}
            land = np.ones(n, bool)
            fish[lv] = SF.seafood(g, L, land, np.zeros(n, bool), _get(L, n))["fish_lake"][cells[0]]
        assert fish[6] == pytest.approx(fish[7], abs=0.01) and fish[6] > 0.35
    for lv, g in grids.items():  # (an island: up to ISLAND_KM2, or a single cell, which the coarse grid can't draw smaller)
        land = np.zeros(g.n, bool)
        land[0] = True
        assert CF.island_mask(g, land)[0], lv
        land[_blob(g, int(np.ceil(CF.ISLAND_KM2 / SF.cell_km2(g))) + 1)] = True
        assert not CF.island_mask(g, land)[0], lv
        small = np.zeros(g.n, bool)
        small[_blob(g, max(1, int(CF.ISLAND_KM2 // SF.cell_km2(g))))] = True
        assert CF.island_mask(g, small)[0], lv


def _blob(g, k):
    """k connected cells grown from cell 0 (breadth first)."""
    cells, i = [0], 0
    while len(cells) < k:
        cells += [c for c in g.nbr_idx[g.nbr_off[cells[i]]:g.nbr_off[cells[i] + 1]].tolist() if c not in cells]
        i += 1
    return cells[:k]


def test_reach_rings_span_the_same_km(grids):
    """A district's good reaches REACH_KM (whole rings, at least one): one ring at L6 and L7, two at L8."""
    assert SF.rings_for(grids[6], LD.REACH_KM) == 1 and SF.rings_for(grids[7], LD.REACH_KM) == 1
    assert SF.rings_for(shared_grid(8), LD.REACH_KM) == 2
    assert SF.rings_for(grids[6], SF.SEA_REACH_KM) == 1 and SF.rings_for(grids[7], SF.SEA_REACH_KM) == 2
