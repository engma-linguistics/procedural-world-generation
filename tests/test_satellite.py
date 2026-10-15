"""The satellite view's colours (planet/satellite.py, PW-083) on a few made-up places."""

import numpy as np

from planet import satellite as SAT
from planet import vegetation as V


def _nu(**cover):
    nu = np.zeros((V.NP, 1))
    for k, v in cover.items():
        nu[V.IDX[k], 0] = v
    return nu


PLACES = {  # name: (lat, elev, water, temp, t_warm, t_cold, p_jul, p_jan, nu, cover, tree, extra)
    "rainforest": (0, 200, 0, 26, 27, 25, 2500, 2500, _nu(TrBE=0.95), 0.95, 0.9, {}),
    "sahara": (22, 400, 0, 26, 34, 16, 20, 20, _nu(), 0.0, 0.0, {}),
    "taiga": (62, 200, 0, -5, 16, -25, 500, 300, _nu(BoNE=0.8, Moss=0.1), 0.85, 0.75, {}),
    "steppe": (48, 300, 0, 6, 22, -12, 400, 150, _nu(C3G=0.8), 0.7, 0.0, {}),
    "deep sea": (20, -4500, 1, 24, 27, 21, 1000, 1000, _nu(), 0, 0, {}),
    "arctic sea": (85, -3000, 1, -18, -1, -32, 200, 100, _nu(), 0, 0, {}),
    "ice sheet": (75, 2500, 0, -30, -12, -45, 200, 150, _nu(), 0, 0, {"ice": 2000.0}),
}


def _colours():
    rows = list(PLACES.values())
    col = lambda j: np.array([r[j] for r in rows], float)  # noqa: E731
    nu = np.concatenate([r[8] for r in rows], 1)
    ice = np.array([r[11].get("ice", 0.0) for r in rows])
    water = col(2).astype(int)
    return {k: dict(zip(PLACES, v.astype(int))) for k, v in SAT.seasons(
        col(0), elev=col(1), water=water, lake_depth=np.zeros(len(rows)), temp=col(3), t_warm=col(4), t_cold=col(5),
        p_jul=col(6), p_jan=col(7), nu=nu, cover=col(9), tree=col(10), ice=ice).items()}


def test_satellite_colours_look_right():
    c = _colours()
    jul, jan = c["jul"], c["jan"]
    r, g, b = jul["rainforest"]
    assert g > r and g > b and g < 110  # dark green
    r, g, b = jul["sahara"]
    assert r > g > b and r > 170  # bright tan
    assert jan["taiga"].mean() > jul["taiga"].mean() + 40  # snow in winter, partly hidden by the trees
    assert jan["taiga"].min() < 230  # (the dark forest shows through)
    assert jul["steppe"][1] >= jul["steppe"][2] + 20  # green-ish in summer
    r, g, b = jul["deep sea"]
    assert b > r and b > g and b < 90  # deep blue
    assert jan["arctic sea"].min() > 200  # sea ice in winter
    assert jul["ice sheet"].min() > 190
    # 'year' is each hemisphere's summer
    assert np.array_equal(c["year"]["taiga"], jul["taiga"])


def test_pack_roundtrip():
    rgb = np.array([[0, 0, 0], [255, 128, 7], [12, 250, 99]], np.uint8)
    assert np.array_equal(SAT.unpack(SAT.pack(rgb)), rgb)
