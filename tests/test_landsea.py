"""Land and sea by connection to the world ocean (geo.is_land, PW-1229): ground below sea level cut off from
the ocean is land (a lake or a dry depression), a strait narrower than a cell (one low land cell) joins a body
to the sea, a body big enough to be an ocean of its own is sea, and the viewer's copy (landsea.js) agrees."""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from planet import geo, hydrology
from planet.geo import is_land
from planet.grid import shared_grid

VIEWER = Path(__file__).resolve().parent.parent / "viewer"


def _km(g, lat, lon):
    return geo.arc_km(g.centers @ geo.xyz(np.radians(lat), np.radians(lon)))


def _base(g):
    """Land at 200 m north of 30 S, the world ocean (3 km deep) south of it."""
    return np.where(g.lat < -30, -3000.0, 200.0)


def _path_to_sea(g, e, start):
    """The cells from start (a cell, or a mask of cells) to the nearest cell of the world ocean (BFS over the
    grid; a start cell first, the ocean's cell last)."""
    sea = g.lat < -30
    prev = np.full(g.n, -1)
    seen = np.zeros(g.n, bool)
    seen[start] = True
    q, h = list(np.flatnonzero(seen)), 0
    while h < len(q):
        i = q[h]
        h += 1
        if sea[i]:
            break
        for j in g.neighbors[i]:
            if not seen[j]:
                seen[j], prev[j] = True, i
                q.append(j)
    path = [i]
    while prev[path[-1]] >= 0:
        path.append(prev[path[-1]])
    return path[::-1]


def test_cut_off_pocket_is_land_and_a_connected_inlet_is_sea():
    g = shared_grid(5)
    e = _base(g)
    pocket = _km(g, 20, 0) < 250  # (~0.2 Mkm2, 2-3000 km from the ocean)
    e[pocket] = -50.0
    inlet = _km(g, -22, 90) < 250  # below 0, joined to the ocean along the grid's links
    e[inlet] = -50.0
    e[_path_to_sea(g, e, int(np.argmin(_km(g, -22, 90))))[1:-1]] = -10.0
    land = is_land(e, grid=g)
    assert land[pocket].all()
    assert not land[inlet].any()
    assert not land[g.lat < -30].any() and land[(e > 0)].all()
    # the old rule (elevation > 0) and the new agree off the pocket
    assert np.array_equal(land[~pocket], (e > 0)[~pocket])
    # the default grid (by the cell count) is the same
    assert np.array_equal(is_land(e), land)


def test_grounded_ice_is_land_and_walls_off_a_pocket():
    g = shared_grid(5)
    e = _base(g)
    near = _km(g, -32, 0) < 400  # a bay of the ocean pressed 100 m down under ice except its middle
    e[near] = -100.0
    ice = np.where(near & (_km(g, -32, 0) > 150), 500.0, 0.0)
    land = is_land(e, ice, g)
    assert land[ice > 0].all()


@pytest.mark.parametrize("sill_m, joined", [(-5.0, True), (geo.SILL_M, True), (5 * geo.SILL_M, False)])
def test_a_one_cell_strait_joins_only_when_the_cell_is_low(sill_m, joined):
    """A body one land cell from the sea: a strait narrower than the cell can cross a lowland cell (its bed
    within SILL_M of the sea), not a higher one; a channel below 0 all the way is plain connection."""
    g = shared_grid(5)
    e = _base(g)
    body = _km(g, 0, 40) < 250
    e[body] = -50.0
    path = _path_to_sea(g, e, body)[1:-1]  # (from the body's edge: only the first cell touches it)
    e[path] = -10.0
    e[path[0]] = sill_m  # (the one cell between)
    land = is_land(e, grid=g)
    assert (not land[body].any()) if joined else land[body].all()


def test_a_body_as_big_as_an_ocean_is_sea():
    g = shared_grid(5)
    e = _base(g)
    big = _km(g, 40, 120) < 500  # ~0.8 Mkm2, far from the ocean
    small = _km(g, 40, -60) < 200
    e[big | small] = -2000.0
    land = is_land(e, grid=g)
    assert not land[big].any() and land[small].all()
    assert np.pi * 500 ** 2 > geo.SEA_MIN_KM2 > np.pi * 200 ** 2


def test_a_pocket_holds_a_lake_or_stays_a_dry_basin():
    """Hydrology takes the pocket for a closed hollow on land: no river ends in it as at a coast; with rain it
    fills to a lake (its surface may stand below sea level), in a desert it stays dry."""
    g = shared_grid(6)
    e = _base(g)
    d = _km(g, 20, 0)
    pocket = d < 250  # (~0.2 Mkm2: below SEA_MIN_KM2)
    e = np.where(pocket, -300.0 + 300.0 * (d / 250.0) ** 2, e)
    for runoff, wet_ok in ((30.0, True), (0.1, False)):
        c = {"runoff": np.full(g.n, runoff), "aet": np.full(g.n, 600.0), "lake_evap": np.full(g.n, 1500.0)}
        flow, down, lk = hydrology.rivers_and_lakes(g, e, c, channel=0.0)
        assert not lk["sea"][pocket].any()
        assert lk["endorheic"][pocket].all() or lk["kind"][pocket].max() == hydrology.OPEN_LAKE
        assert lk["wet"][pocket].any() == wet_ok
        if wet_ok:
            assert lk["kind"][lk["wet"] & pocket].max() == hydrology.CLOSED_LAKE
            assert lk["level"][pocket & lk["wet"]].max() < 0.0  # (a closed lake below sea level: the Dead Sea)


_JS = """
import { seaMask } from '%s';
const d = JSON.parse(require('fs').readFileSync('%s', 'utf8'));
console.log(JSON.stringify(d.cases.map((c) => Array.from(seaMask(c.e, c.ice, d.nbr)))));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_viewer_sea_matches_python(tmp_path):
    g = shared_grid(4)
    rng = np.random.default_rng(3)
    cases = []
    for k in range(6):
        e = rng.normal(0, 400, g.n) + 300 * np.sin(np.radians(g.lat) * 3 + k)
        e = np.round(e)
        e[rng.random(g.n) < 0.1] = rng.choice([0.0, geo.SILL_M, geo.SILL_M + 1])  # (ties at the thresholds)
        ice = np.where(rng.random(g.n) < 0.05, 300.0, 0.0) if k % 2 else None
        cases.append((e, ice))
    data = tmp_path / "cases.json"
    data.write_text(json.dumps({"nbr": g.neighbors, "cases": [
        {"e": e.tolist(), "ice": None if ice is None else ice.tolist()} for e, ice in cases]}))
    mod = tmp_path / "landsea.mjs"
    mod.write_text((VIEWER / "globe" / "landsea.js").read_text())
    run = tmp_path / "run.mjs"
    run.write_text("import { createRequire } from 'module'; const require = createRequire(import.meta.url);\n"
                   + _JS % (mod.as_posix(), data.as_posix()))
    r = subprocess.run(["node", str(run)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)
    for (e, ice), sea in zip(cases, got):
        want = ~is_land(e, ice, g)
        assert np.array_equal(np.array(sea, bool), want)
        assert want.sum() < (~((e > 0) | ((ice if ice is not None else 0) > 0))).sum()  # (some pockets turn land)
