"""Discrete volcanoes: hotspot vents ride their plate in a spaced chain, the
volcano table reaches worlds, and the zoom draws separate cones with sea
between them."""

import numpy as np

from planet import timeline as T
from planet import zoom, zoom_volcanoes as ZV
from planet.geo import R_KM, xyz
from planet.tectonics import volcanism as V


def test_vents_form_spaced_chains(sim4):
    vents = [v for v in sim4.volcanoes if v["kind"] == V.VENT]
    assert vents, "no hotspot vents after 300 Myr"
    # one active vent per plume at most, and only plumes that are alive feed one
    live = {h["id"] for h in sim4.hotspots}
    active = [v["plume"] for v in vents if v["active"]]
    assert len(active) == len(set(active)) and set(active) <= live
    # consecutive vents of a plume on the same plate are ~50-150 km apart in
    # the plate's frame (the vent gap; a vent born where the plume changed
    # plates starts afresh, so skip pairs across plates)
    gaps = []
    for pid in {v["plume"] for v in vents}:
        ch = sorted((v for v in vents if v["plume"] == pid), key=lambda v: v["id"])
        for a, b in zip(ch, ch[1:]):
            if a["label"] == b["label"] and abs(a["born"] - b["born"]) <= sim4.dt:
                gaps.append(np.arccos(np.clip(a["ppos"] @ b["ppos"], -1, 1)) * R_KM)
    assert gaps and 45 <= np.median(gaps) <= 155, np.median(gaps)
    # each vent carries its own size and stays within the summit limits
    for v in vents:
        assert v["vol"] >= 0 and v["height"] >= 0
        assert v["floor"] + v["height"] - v["eroded"] == v["top"] or abs(
            v["floor"] + v["height"] - v["eroded"] - v["top"]) < 1e-6
        assert v["top"] <= V.TOP_MAX[0] + 1e-6


def test_volcano_table_in_world(sim4):
    w = T.world_from_sim(sim4)
    assert w["meta"]["volcano_columns"] == list(V.COLUMNS)
    rows = w["meta"]["volcanoes"]
    assert len(rows) == len(sim4.volcanoes) and all(len(r) == len(V.COLUMNS) for r in rows)
    kinds = {r[2] for r in rows}
    assert V.VENT in kinds


def _flat_sea_world(vents):
    """A world dict with just what zoom_volcanoes.fields reads."""
    return {"meta": {"volcano_columns": list(V.COLUMNS), "volcanoes": vents}}


def test_zoom_cones_are_separate_islands():
    """Two hotspot vents 90 km apart on a 4 km deep floor: two islands with
    sea between them, and an atoll ring with a lagoon round an old one."""
    fr = zoom.Frame(0.0, 0.0)
    n, res = 200, 1.0
    xs = (np.arange(n) + 0.5 - n / 2) * res
    X, Y = np.meshgrid(xs, -xs)
    px, py = X.ravel(), Y.ravel()
    Pk = np.ascontiguousarray(fr.to_sphere(px, py) * R_KM)
    lon_of = lambda x_km: float(np.degrees(x_km / R_KM))
    row = lambda x, age, active, top, reef=0, shore=0.0: [0.0, lon_of(x), V.VENT, age, active, top, -4000, 7500,
                                                          30.0, 50000, reef, shore]
    w = _flat_sea_world([row(-45, 0.0, 1, 3500), row(45, 3.0, 0, 2500)])
    f = ZV.fields(w, fr, px, py, res, 55.0, Pk, 1, n * res)
    z = np.maximum(f["floor"], f["z"])
    at = lambda x: int(np.argmin(np.hypot(px - x, py)))
    assert z[at(-45)] > 3000 and z[at(45)] > 1500
    assert z[at(0)] < -500, z[at(0)]  # the channel between them is sea
    assert {v["form"] for v in f["list"]} == {"active shield volcano", "eroded volcanic island"}
    # an atoll: a reef ring (some islets) round a shallow lagoon, deep water outside
    w = _flat_sea_world([row(0, 30.0, 0, -200, reef=V.REEF, shore=20.0)])
    f = ZV.fields(w, fr, px, py, res, 55.0, Pk, 1, n * res)
    z = np.maximum(f["floor"], f["z"])
    r = np.hypot(px, py)
    assert (z[(r > 12) & (r < 30)] > 0).any()  # motu on the (lobed) rim
    lagoon = z[r < 12]
    assert (lagoon < 0).all() and (lagoon > -80).all()
    assert np.median(z[np.abs(r - 34) < 1]) < -800  # the reef front drops off
    assert f["list"][0]["form"] == "atoll"
