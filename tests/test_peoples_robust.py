"""The peoples robustness suite (tools/peoples_robust.py) on the small fake time zoom: its variant trees stay valid, and one run of
each founding arm gives the numbers the report reads (shares, cells led, founding)."""

from __future__ import annotations

import numpy as np

from planet.lineages import spec as SP
from tests.test_lineages import _raw, faketz  # noqa: F401 (the fixture)
from tools import peoples_robust as PR


def _tree():
    raw = _raw()
    raw["lineage"].append({"id": "c", "parents": ["stem"], "at": "12 kyr"})
    return raw


def test_variants_stay_valid_trees():
    raw = _tree()
    for j in range(5):
        jr = PR.jitter(raw, np.random.default_rng(j))
        t = SP.parse(jr)  # (parents older than children, sapiens and extinction in order: the parser checks)
        assert {l.id for l in t.lines.values()} == {r["id"] for r in raw["lineage"]}
    jr = PR.jitter(raw, np.random.default_rng(1))
    assert any(r.get("at") != q.get("at") for r, q in zip(jr["lineage"], raw["lineage"]) if r["id"] in ("a", "b", "c", "fey"))
    t = SP.parse(PR.subset(raw, ["a"]))
    assert "a" in t.lines and "stem" in t.lines and "b" not in t.lines and "tmpl" in t.lines and "half" not in t.lines
    k = SP.parse(PR.knob(raw, "c", 2.0))
    assert k.lines["c"].demo("kind") == 2.0  # (the kind factor, PW-1275: x2 of 1)
    assert len(PR.plan()) > 100 and {v["family"] for v in PR.plan()} == {"base", "jitter", "subset", "knob", "portal", "authored"}
    for p in sorted(PR.TREES.glob("*.toml")):  # (the authored trees parse, and say why they exist)
        raw, info = PR.authored(p)
        assert SP.parse(raw).lines and info["rationale"]


def test_one_run_per_arm(faketz):  # noqa: F811
    for arm in PR.ARMS:
        m = PR.run_one({"raw": _tree(), "world": faketz, "arm": arm, "now": 40.0, "recent": {"kyr": 20, "seed": 1, "climate_every": 0}})
        P = m["peoples"]
        assert {"a", "b", "c", "fey"} <= P.keys()
        assert abs(sum(v["share"] for v in P.values()) - 1.0) < 1e-6
        assert all(0.0 <= v["led"] <= 1.0 for v in P.values())
        assert P["a"]["found_mkm2"] is not None and P["a"]["origin"]["why"]
        assert not P["gone"]["alive"] and P["gone"]["authored_extinct"]
        assert all(v["inherit_mkm2"] == 0.0 for v in P.values())  # (owner D20: a stem's land passes to no child at its end)
        assert isinstance(m["blocs"], list)
