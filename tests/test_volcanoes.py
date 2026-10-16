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


def test_zoom_fills_active_arcs_with_minor_cones():
    """PW-116: the run keeps one arc volcano per ~120 km of active arc; the
    zoom adds minor cones between neighbours along the chain, so a volcanic
    front has one every ~50-70 km: on the line, lower than the pair, not to
    a volcano 300 km off the chain nor between extinct ones."""
    lon_of = lambda x_km: float(np.degrees(x_km / R_KM))
    lat_of = lon_of
    arc = lambda x, y=0.0, active=1, H=2500: [lat_of(y), lon_of(x), V.ARC, 1.0 if active else 15.0, active, H - 500,
                                             -500, H, H / V.ARC_SLOPE / 1000, 1000, 0, 0.0]
    rows = [arc(x) for x in (-195, -65, 65, 195)] + [arc(0, 300)] + [arc(x, -150, active=0) for x in (-60, 60)]
    w = _flat_sea_world(rows)
    tab = ZV.table(w)
    minor = ZV.arc_infill(tab, 1)
    assert len(minor) == 3  # (one in each 130 km gap of the chain, none to the far or the extinct ones)
    for m in minor:
        y = np.radians(m["lat"]) * R_KM
        assert abs(y) < 25 and m["active"] and m["kind"] == V.ARC
        assert 0.55 * 2500 <= m["height_m"] <= 0.95 * 2500 and m["floor_m"] == -500
    xs_ = sorted(np.radians(m["lon"]) * R_KM for m in minor)
    assert all(abs(a - b) < 30 for a, b in zip(xs_, (-130, 0, 130)))
    # drawn as cones in the zoom, and listed
    fr = zoom.Frame(0.0, 0.0)
    n, res = 300, 2.0
    xs = (np.arange(n) + 0.5 - n / 2) * res
    X, Y = np.meshgrid(xs, -xs)
    px, py = X.ravel(), Y.ravel()
    Pk = np.ascontiguousarray(fr.to_sphere(px, py) * R_KM)
    f = ZV.fields(w, fr, px, py, res, 55.0, Pk, 1, n * res)
    assert sum(1 for v in f["list"] if v.get("minor")) == 3
    for m in minor:
        k = int(np.argmin(np.hypot(px - np.radians(m["lon"]) * R_KM, py - np.radians(m["lat"]) * R_KM)))
        assert f["bump"][k] > m["floor_m"] + 0.5 * m["height_m"]
        # (on the ground, not its interpolated floor; not held through the landscape pass;
        # flagged, so zoom.py takes its volume off its cells' other land)
        assert f["bump_minor"][k] and f["bump_abs"][k] == 0 and not np.isfinite(f["pin"][k])


def test_continental_vent_is_a_caldera_on_a_lava_plain():
    """A hotspot vent on a continent (floor 800 m) is drawn as a broad lava
    plain with a caldera (rim above a sunk floor) rather than a shield,
    holding about the shield's volume (PW-118)."""
    fr = zoom.Frame(0.0, 0.0)
    n, res = 200, 1.0
    xs = (np.arange(n) + 0.5 - n / 2) * res
    X, Y = np.meshgrid(xs, -xs)
    px, py = X.ravel(), Y.ravel()
    Pk = np.ascontiguousarray(fr.to_sphere(px, py) * R_KM)
    H, r, f0 = 2400.0, 25.0, 800.0
    w = _flat_sea_world([[0.0, 0.0, V.VENT, 0.5, 1, f0 + H, f0, H, r, 1000, 0, 0.0]])
    f = ZV.fields(w, fr, px, py, res, 55.0, Pk, 1, n * res)
    z = np.where(np.isfinite(f["bump"]), f["bump"], f0) - f0
    rho = np.hypot(px, py)
    assert f["list"][0]["form"] == "active caldera"
    assert z.max() < 0.5 * H  # no shield summit
    rim = z[(rho > 0.8 * r) & (rho < 1.2 * r)].max()
    plain = np.median(z[(rho > 1.3 * r) & (rho < 1.45 * r)])
    assert rim > plain > 0.15 * H  # a raised rim on a lava plain ...
    assert z[rho < 0.5 * r].min() < plain  # ... round a sunk caldera floor
    assert np.percentile(z[(rho > 1.25 * r) & (rho < 1.45 * r)], 90) - plain < 0.1 * plain  # the plain is flat
    vol = z.sum() * res * res / 1000.0  # km^3
    assert 0.75 < vol / (np.pi * r * r * H / 1000.0) < 1.3, vol  # (the lobed outline spreads it a little, as a shield)


def test_vents_on_a_plateau_they_built_leave_no_sea_holes():
    """PW-310: hotspot vents recorded on a -4 km sea floor where the coarse
    cells stand at 1.5 km (a ridge the vents built together, under ice on
    592f2a): the province takes off only the cones' own share of the cells'
    means, so the ground between them stays land, not round holes of sea."""
    from test_zoom_landforms import _plain_world
    lon_of = lambda x_km: float(np.degrees(x_km / R_KM))
    bias = []
    for vents in ([], [[0.0, lon_of(x), V.VENT, 3.0, 0, 1200, -4000, 6500, 25.0, 30000, 0, 0.0] for x in (-60.0, 60.0)]):
        w, _ = _plain_world(1500.0, 0.0, 0.0)
        w["meta"] = {**w["meta"], "volcano_columns": list(V.COLUMNS), "volcanoes": vents}
        z = zoom.build(w, 0.0, 0.0, size_km=300, res_km=1.0, iterations=4, log=lambda *a: None)
        sea = (z["layers"]["water"] == 1).mean()
        assert sea < 0.01, sea  # (with the vents it was ~40% sea, in rings round them)
        bias.append(z["stats"]["inland_cell_mean_bias_m"])
    # the cells keep their means about as well as without the vents (was -1.9 km on 592f2a)
    assert abs(bias[1] - bias[0]) < 200, bias
