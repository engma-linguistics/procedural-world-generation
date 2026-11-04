"""Summit height (PW-846): cell mean + Earth's sub-cell relief, display only."""
import re
from pathlib import Path

import numpy as np

from planet.grid import build_grid
from planet.summit import RELIEF_KNOTS, local_relief, summit_m


def test_js_table_matches():
    src = (Path(__file__).parent.parent / "viewer/globe/summit.js").read_text()
    body = src[src.index("RELIEF_KNOTS = ["):src.index("];")]
    js = np.array([[float(a), float(b)] for a, b in re.findall(r"\[(\d+), (\d+)\]", body)])
    assert np.array_equal(js, RELIEF_KNOTS)


def test_summit_rules():
    g = build_grid(4)
    flat = np.full(g.n, 300.0)
    assert np.array_equal(summit_m(g, flat), flat)  # no relief around: no extra height
    sea = np.full(g.n, -2000.0)
    assert np.array_equal(summit_m(g, sea), sea)
    e = np.full(g.n, 100.0)
    e[10] = 5000.0
    s = summit_m(g, e)
    assert s[10] > 5000.0 + 2000.0 and np.all(s >= e)  # a 4.9 km step: Earth's 2+ km of sub-cell relief
    assert local_relief(g, e)[10] == 4900.0
