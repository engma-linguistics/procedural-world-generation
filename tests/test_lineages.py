"""Lineages lane (docs/proposals/lineages.md): the recent pass and the peoples' history,
on a small fake time zoom (level 3) in a temporary store."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from planet import store as S
from planet import timeline as T
from planet.grid import build_grid
from planet.lineages import recent as R

LEVEL = 3


def _fake_timezoom(root, kyr=40.0, every=2.0) -> str:
    """Two continents (lon -60..60 and 90..150) joined by a shelf (60..90, |lat| < 25, 40 m deep)
    that is dry while the glacial index is high (sea down 80 m), a polar ice cap that grows with it,
    and a small island (lon -120)."""
    S.set_root(root)
    g = build_grid(LEVEL)
    lat, lon = g.lat, g.lon
    ts = np.arange(0, kyr + every / 2, every)
    gi = np.clip(np.sin(np.pi * ts / kyr) * 1.2, 0, 1)  # glacial index: up, then down
    bed = np.full(g.n, -2000.0)
    bed[np.abs(lon) < 60] = 400
    bed[(lon > 90) & (lon < 150)] = 300
    bed[(lon > 60) & (lon < 90) & (np.abs(lat) < 25)] = -40
    d = np.degrees(np.arccos(np.clip(np.cos(np.radians(lat)) * np.cos(np.radians(lon + 120)), -1, 1)))
    bed[d < 9] = 200
    data = {k: [] for k in ("elevation", "ice", "temperature", "climate", "tree_cover")}
    frames = []
    for t, I in zip(ts, gi):
        ice = np.where((np.abs(lat) > 62 - 12 * I) & (bed > 0), 800.0 * (0.3 + I), 0.0)
        elev = bed + 80 * I + ice
        temp = 29 - 0.45 * np.abs(lat) - 6 * I
        land = (elev > 0) | (ice > 0)
        clim = np.where(temp > 22, 0, np.where(temp > 6, 14, 28))
        clim = np.where(land, clim, 30)
        data["elevation"].append(S.encode(np.round(elev), S.LAYERS["elevation"]))
        data["ice"].append(S.encode(np.round(ice), {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1}))
        data["temperature"].append(S.encode(np.round(temp), S.LAYERS["temperature"]))
        data["climate"].append(S.encode(clim, S.LAYERS["climate"]))
        data["tree_cover"].append(S.encode(np.where(land & (temp > 0), 50, 0), S.LAYERS["tree_cover"]))
        frames.append({"t": float(t), "omega": {}, "hotspots": [], "volcanoes": [],
                       "stats": {"t": float(t), "sea_level_change_m": -80 * I, "ice_pct": float((ice > 0).mean() * 100),
                                 "ice_volume_mkm3": float(I), "glacial_index": float(I), "global_temp_c": 14 - 6 * I,
                                 "max_ice_m": float(ice.max()), "ice_age": "building"}})
    specs = {"elevation": S.LAYERS["elevation"], "ice": {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1},
             "temperature": S.LAYERS["temperature"], "climate": S.LAYERS["climate"], "tree_cover": S.LAYERS["tree_cover"]}
    run_id = "faketz"
    out = S.path_of("run", run_id)
    layers = S.write_layers(out, {k: np.stack(v) for k, v in data.items()}, specs)
    S.write_grid(g)
    S.write_json(out / "run.json", {
        "format": "procgen-run/2", "kind": "timezoom", "id": run_id, "name": "fake time zoom",
        "meta": {"kind": "timezoom", "time_unit": "kyr", "source_run": "earth", "source_name": "fake", "at_myr": 0.0,
                 "kyr": kyr, "step_kyr": 0.5, "every": every, "myr": kyr / 1000, "frames": len(ts), "seed": 1,
                 "level": LEVEL, "cells": g.n, "cell_size_km": 900, "params": {}, "created": "now"},
        "grid": f"../../grids/L{LEVEL}.json", "legend": S.legends(), "layers": layers, "events": [], "frames": frames})
    return run_id


@pytest.fixture
def faketz(tmp_path):
    old = S.root()
    tz = _fake_timezoom(tmp_path)
    yield tz
    S.set_root(old)


def test_recent_interpolates_the_time_zoom(faketz):
    ps = R.Pass(faketz, now_kyr=40.0, params=R.RecentParams(kyr=10, seed=3))
    assert ps.start == pytest.approx(-10.0)
    a = ps.fields(-9.0, variability=False)  # time zoom 31 kyr: halfway between the 30 and 32 kyr frames
    run, arr = T.load_frames(S.find_run(faketz), ("temperature",))
    want = 0.5 * (T.frame(run, arr, "temperature", 15) + T.frame(run, arr, "temperature", 16))
    assert np.allclose(a["temperature"], want)
    assert len(ps.steps) == 101 and ps.frame_times()[0] == -10.0 and ps.frame_times()[-1] == 0.0


def test_recent_variability_is_seeded_and_bounded(faketz):
    p1 = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=5, episodes_per_kyr=0.5))
    p2 = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=5, episodes_per_kyr=0.5))
    assert np.array_equal(p1.noise, p2.noise) and [e.t0 for e in p1.episodes] == [e.t0 for e in p2.episodes]
    assert 0.1 < p1.noise.std() < 1.0
    dT, rf, _ = p1.anomaly(-5.0)
    assert np.all(rf > 0.4) and np.all(rf <= 1.0) and np.all(np.abs(dT) < 6)
    # the window holds the deglaciation (index 1 -> 0): one cold reversal
    assert sum(e.kind == "cold reversal" for e in p1.episodes) == 1


def test_recent_saved_as_a_viewable_time_zoom(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=10, every=1.0, seed=1))
    out = R.save(ps)
    run = json.loads((out / "run.json").read_text())
    assert run["kind"] == "timezoom" and run["meta"]["phase"] == "recent" and run["meta"]["timezoom"] == faketz
    assert [f["t"] for f in run["frames"]] == [float(t) for t in range(-10, 1)]
    assert set(run["layers"]) >= {"elevation", "ice", "temperature", "climate", "precipitation"}
    _, arr = T.load_frames(out, ("precipitation",))
    assert arr["precipitation"].shape == (11, build_grid(LEVEL).n)
    assert (out / "run.txt").is_file()
    assert R.resolve(faketz) == (faketz, None, None)


# ---- the input and the history -------------------------------------------------------------------
from planet.lineages import history as H  # noqa: E402
from planet.lineages.gridops import nbr_reduce  # noqa: E402
from planet.lineages import output as O  # noqa: E402
from planet.lineages import run as LR  # noqa: E402
from planet.lineages import spec as SP  # noqa: E402
from planet.lineages.history import megafauna as MG  # noqa: E402


def _raw():
    return {"meta": {"name": "t", "seed": 2, "mixing_start": "3 kyr"}, "lineage": [
        {"id": "stem", "origin": "root", "at": "30 kyr", "temp_c": [5, 30], "rain_mm": [100, 5000]},
        {"id": "a", "parents": ["stem"], "at": "20 kyr"},
        {"id": "b", "parents": ["stem"], "at": "15 kyr", "traits": ["swims"]},
        {"id": "fey", "origin": "arrival", "at": "10 kyr", "place": [0, 120]},
        {"id": "half", "origin": "hybrid", "exempt": True, "parents": ["a", "fey"], "at": "8 kyr"},
        {"id": "tmpl", "origin": "template", "parents": ["a"], "at": "4 kyr", "share": 0.05},
        {"id": "gone", "parents": ["a"], "at": "12 kyr", "extinct": "5 kyr"}],
        "wish": [{"a": "b", "want": "coast"}]}


def test_spec_parses_the_dag_and_the_preset():
    t = SP.parse(_raw())
    assert t.lines["half"].origin == "hybrid" and t.lines["half"].overlay
    assert t.lines["tmpl"].overlay and not t.lines["a"].overlay
    assert t.lines["stem"].children == ["a", "b"] and t.lines["gone"].extinct_kyr == 5.0
    assert SP.parse_ago("8 Myr") == 8000 and SP.parse_ago("12000 yr") == 12 and SP.parse_ago(450) == 450
    assert SP.parse(SP.to_raw(t)).lines.keys() == t.lines.keys()
    dnd = SP.load(LR.SAMPLES / "dnd.toml")
    assert {"elf", "human", "half_elf", "tiefling", "kobold", "aarakocra", "leonin", "tabaxi", "storm_giant", "cloud_giant",
            "frost_giant", "fire_giant", "hill_giant"} <= dnd.lines.keys()
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr"},
                              {"id": "y", "parents": ["x"], "at": "2 kyr"}]})  # child older than parent


def test_spec_disable_reparents_and_cascades():
    raw = _raw()
    raw["lineage"][1]["enabled"] = False  # 'a' off: its split child 'gone' re-parents to 'stem'; half, tmpl go
    t = SP.parse(raw)
    assert "a" not in t.lines and t.lines["gone"].parents == ["stem"]
    assert "half" not in t.lines and "tmpl" not in t.lines and set(t.disabled) == {"a", "half", "tmpl"}
    raw = _raw()
    raw["lineage"][0]["enabled"] = False  # the root off: its children become roots
    t = SP.parse(raw)
    assert t.lines["a"].origin == "root" and t.lines["a"].parents == []


def test_history_places_splits_hybrids_templates_and_extinctions(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    tree = SP.parse(_raw())
    h, res, pres = H.simulate(tree, ps, tries=2)
    assert {"stem", "a", "b", "fey", "gone"} <= h.origins.keys()
    assert "stem" in h.ended  # ended at its last split; its range went to a and b
    assert "gone" in h.ended and not (res["present"][h.idx["gone"]] > 0).any()
    pa = res["present"][h.idx["a"]] > H.EST
    assert pa.any()
    tm = res["present"][h.idx["tmpl"]] > H.EST
    assert tm.any() and not (tm & ~pa).any()  # a template lives only on its host
    assert pres["wishes"] and len(pres["tries"]) == 2
    out = O.save(h, res, pres, name="test peoples")
    run = json.loads((out / "run.json").read_text())
    assert run["kind"] == "peoples" and run["meta"]["kind"] == "peoples" and "phase" not in run["meta"] and run["frames"][-1]["t"] == 0
    assert run["meta"]["draw_ranges"] is False and run["meta"]["range_draws"] == {}  # (PW-1383: off by default)
    assert [l["id"] for l in run["meta"]["lineages"]] == [l.id for l in h.lines]
    _, arr = T.load_frames(out, ("peoples",))
    assert arr["peoples"].shape[0] == len(run["frames"])


def test_a_stem_s_land_lies_empty_at_its_end(faketz):
    """Owner D20 (PW-1181, superseding PW-677's handover): when a stem ends at its last split its remaining range passes to no child, of
    its own kind or any other; it lies empty for the children to spread into. Its last land is kept (PW-1184: a later split founds by it)."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_raw()), ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    h.active = {l.id: False for l in h.lines}
    h.ended = {}
    step = h.steps[-1]
    env = step.get()
    tags = H._tags(h.grid, env)
    lon = h.grid.lon
    west = tags["land"] & (np.abs(lon) < 60)
    east = tags["land"] & (lon > 90) & (lon < 150)
    assert west.any() and east.any()
    h.p[h.idx["stem"]][west | east] = 1.0
    h.p[h.idx["a"]][west & (lon < 0)] = 1.0  # the child 'a' lives on part of the west continent only; 'b' is not yet alive
    h.active["stem"] = h.active["a"] = True
    h._last_held = {}
    a0 = h.p[h.idx["a"]].copy()
    h._end_parent(h.tree.lines["stem"], step, env, tags)
    assert not (h.p[h.idx["stem"]] > 0).any()
    assert (h.p[h.idx["a"]] == a0).all()  # (nothing handed over, joined to its land or cut off)
    assert (h._last_held[h.idx["stem"]] == (west | east)).all()


def test_a_split_needs_a_patch_of_its_habitat_for_its_founders(faketz):
    """PW-1558 (lanes 269, 269c): a split founded on an islet smaller than a founders' country has no room there (it arises in the
    nearest free country instead, _origin_split), nor on a sliver of its habitat on a landmass whose other habitat lies apart from it;
    on a continent of its habitat it has."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_raw()), ps, 1)
    env = h.steps[-1].get()
    tags = H._tags(h.grid, env)
    lon, lat = h.grid.lon, h.grid.lat
    west = tags["land"] & (np.abs(lon) < 60)
    c = int(np.argmax(np.where(west, -np.abs(lon) - np.abs(lat), -1e9)))
    islet = H.rings(c, np.ones(h.grid.n, bool), 1, h.grid.nbr_off, h.grid.nbr_idx)
    K = np.where(islet, 1.0, 0.0)  # (it can live only there)
    assert islet.sum() < h._founders_cells(K)
    assert not h._founders_room(c, K, islet)
    assert not h._founders_room(c, K, tags["land"] | islet)  # (a continent with only the islet's worth of its habitat: no room either)
    K2 = np.where(tags["land"] | islet, 1.0, 0.0)
    assert h._founders_room(c, K2, tags["land"] | islet)
    apart = tags["land"] & ~h._dilate(islet, 2)  # (its habitat elsewhere on the land, not touching the patch at c)
    K3 = np.where(islet | apart, 1.0, 0.0)
    assert apart.sum() >= h._founders_cells(K3) and not h._founders_room(c, K3, tags["land"] | islet)


def test_walkers_dont_cross_the_sea_swimmers_do(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    g = ps.grid
    env = ps.fields(0.0, variability=False)
    tags = H._tags(g, env)
    walker = SP.Lineage("w", temp_c=(-20, 40), rain_mm=(1, 9000))
    K = H.capacity(walker, env, tags)
    island = env["land"] & (g.lon < -100) & (g.lon > -140)  # the fake island
    assert island.any() and K[island].max() > 0.5
    p = np.zeros(g.n)
    p[np.argmax(np.where(np.abs(g.lon) < 30, K, 0))] = 1.0
    land = env["land"]
    enter = np.ones(g.n)
    a = H.spread(p.copy(), K, enter, tags["elev"], 0.0, 0.0, land, g.nbr_off, g.nbr_idx, 400)
    assert not (a[island] > 0).any()
    b = H.spread(p.copy(), K, enter, tags["elev"], 0.0, 0.9, land, g.nbr_off, g.nbr_idx, 400)
    assert (b[island] > 0).any()


def test_long_crossings_scale_with_gap_and_way(faketz, monkeypatch):
    """crossing.py: the sea gap is counted in sea cells from the line's own coast; swimmers reach the
    fake island over a long step, a walker's rafting almost never does in a short one."""
    from planet.lineages import crossing as C
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    g = ps.grid
    env = ps.fields(0.0, variability=False)
    tags = H._tags(g, env)
    island = env["land"] & (g.lon < -100) & (g.lon > -140)
    p = np.where(env["land"] & (np.abs(g.lon) < 60), 1.0, 0.0)
    src = (p > 0) & tags["coast"]
    d = C.sea_gap(src, env["land"], g.nbr_off, g.nbr_idx, 50)
    assert (d[island] > 0).all() and (d[src] == 0).all()
    cr = C.Crossings(g, env, g.spacing * 6371, 1.0)
    K = np.where(tags["land"], 1.0, 0.0)
    swimmer = SP.Lineage("s", traits=["swims"])
    walker = SP.Lineage("w")
    rng = np.random.default_rng(0)
    monkeypatch.setitem(SP.HOPS, "swims", (1.0, 8000.0, None))  # (level 3 cells are ~900 km: a long-range swimmer)
    got = cr.hop(swimmer, p, K, K, env, tags, 100.0, 4000.0, rng, H.EST)
    assert any(island[c] for c, _, _ in got)
    # (before the canoes, a walker only drifts; then a small share of its frontier paddles short gaps and, from
    # the voyages, sails further, PW-650, PW-677)
    assert C.modes(walker, 100.0) == [("raft",) + SP.HOPS["raft"][:2]]
    canoe = dict((w, (r, L)) for w, r, L in C.modes(walker, 10.0))["seafaring"]
    # (PW-720: one craft ladder for peoples and animals: a default people only paddles canoes; planked boats need a sea share of 0.2, sailing ships 0.3)
    assert canoe[1] == SP.BOATS[1] and dict((w, L) for w, _, L in C.modes(walker, 1.0))["seafaring"] == canoe[1]
    mar = SP.Lineage("m", sea_share=0.25)
    reach = lambda ln, t: dict((w, L) for w, _, L in C.modes(ln, t))["seafaring"]  # noqa: E731
    assert reach(mar, 10.0) == 300.0 and reach(mar, 5.0) == 1500.0 and reach(mar, 1.0) == 1500.0 and reach(SP.Lineage("t", sea_share=0.5), 1.0) == 2500.0
    assert C.modes(SP.Lineage("w0", sea_share=0.0), 1.0) == [("raft",) + SP.HOPS["raft"][:2]]
    boat = dict((w, (r, L)) for w, r, L in C.modes(walker, 1.0))["seafaring"]
    sailor = dict((w, (r, L)) for w, r, L in C.modes(SP.Lineage("s", traits=["seafaring"]), 1.0))["seafaring"]
    assert boat[0] < 0.1 * sailor[0] and boat[1] < sailor[1]
    hits = sum(any(island[c] for c, _, _ in cr.hop(walker, p, K, K, env, tags, 1.0, 0.1, rng, H.EST)) for _ in range(50))
    assert hits == 0


def test_expansive_peoples_press_into_held_country():
    """PW-869: an expansive people with little of its country filled presses on; a homebody or a people that has filled its country does not."""
    f = H.expanse_factor
    assert f(0.25, 10, 1000) == 1.0
    young = f(0.7, 10, 1000)  # (expansive, a sliver of its country: presses)
    assert young == pytest.approx(1 - H.EXPANSE_PRESS * (1 - 10 / (H.EXPANSE_FILL * 1000)))
    assert f(0.7, 10, 1000) < f(0.5, 10, 1000) < f(0.4, 10, 1000) == 1.0  # (the more expansive, the more)
    assert f(0.7, int(H.EXPANSE_FILL * 1000), 1000) == 1.0  # (filled: no more pressing)


def test_a_people_on_the_upswing_has_an_edge_that_fades_when_it_stalls():
    """Owner 10-30 (lane 73): momentum, not a founding window. A newcomer (no lagged mass yet) and a people that has doubled against its
    lagged mass have the full edge; growth stalling lets the reference catch up and the edge fades; a shrinking people has none. The
    edge's strength is the era's dial, early before the farming onset and late at the present."""
    mo, ref = H.surge(10.0, 0.0, 0.1)
    assert mo == 1.0 and 0 < ref < 10.0
    for _ in range(200):  # (40 kyr at a stalled mass)
        mo, ref = H.surge(10.0, ref, 0.2)
    assert mo < 0.01
    assert H.surge(20.0, 10.0, 0.0)[0] == pytest.approx(1.0)  # (twice its lagged mass: full)
    assert H.surge(5.0, 10.0, 0.1)[0] == 0.0  # (shrinking)
    assert H.surge(10.0, 0.0, 400.0)[0] < 0.01  # (a deep step: long caught up)
    assert H.surge_q(1.0, 1.0, 100.0) == pytest.approx(H.SURGE_Q) and H.surge_q(1.0, 0.0, 0.0) == 0.0
    assert H.surge_q(2.0, 0.0, H.SURGE_LATE_FROM_KYR / 2) == pytest.approx(H.SURGE_Q)  # (half way: the blend)


def test_peoples_that_would_coexist_can_invade_each_other_whoever_came_first():
    """Lane 73 (mutual invasibility): where a pair competes under 1 both ways (Lotka-Volterra coexistence), an incumbent at its full
    habitat weighs on a newcomer only at its coexistence share, so the newcomer's room is its own share (before: K(1 - a), under the
    establishment threshold, and the first comer kept the niche). Over 1 (exclusion) nothing changes."""
    from planet.lineages.spread import coexist_cap, load_rows
    n = 3
    p = np.zeros((2, n))
    p[1] = 0.72  # (the incumbent, row 1, at its full habitat)
    Km = np.full((2, n), 0.72)
    rows, idx, c = np.array([1]), np.arange(n), np.zeros(n)
    a = np.array([0.0, 0.35])
    t = np.array([0.0, 0.52])  # (closed country: 0.87 both ways, the dwarves and kobolds)
    W = np.ones((1, n))  # (no fit weight: the pair suits the cells alike)
    P = coexist_cap(p, rows, a, t, a, t, Km, Km[0], idx, c, W)
    share = 0.72 * (1 - 0.87) / (1 - 0.87 ** 2)
    assert P[0] == pytest.approx(share)
    room = Km[0] - load_rows(P, a, t, rows, c)
    assert room == pytest.approx(share) and (room > H.EST).all() and (0.72 - 0.87 * 0.72) < H.EST  # (was locked out)
    assert load_rows(p[1:2], a, t, rows, c) == pytest.approx(H.rivals_load(p, rows, a, t, idx, c))
    t2 = np.array([0.0, 0.9])  # (1.25: exclusion, the presence counts in full)
    assert (coexist_cap(p, rows, a, t2, a, t2, Km, Km[0], idx, c, W)[0] == p[1]).all()
    Km0 = np.zeros((2, n))  # (a row not yet set reads K_j as the presence)
    assert coexist_cap(p, rows, a, t, a, t, Km0, Km[0], idx, c, W)[0] == pytest.approx(share)


def test_rafts_and_dugouts_give_coastal_peoples_an_early_rung():
    """PW-869: from RAFT_KYR a people with a sea share of 0.1 crosses ~100 km gaps; before it, and below the share, only the drift raft.
    Animals do not ride in them."""
    from planet.lineages import animal_defs as AD
    from planet.lineages import crossing as C
    sailor = SP.Lineage("s", sea_share=0.6)
    reach = lambda ln, t: dict((w, L) for w, _, L in C.modes(ln, t)).get("seafaring")  # noqa: E731
    assert reach(sailor, 130.0) is None and reach(sailor, 80.0) == 120.0 and reach(sailor, 50.0) == 300.0 and reach(sailor, 5.0) == 1500.0
    assert reach(SP.Lineage("w", sea_share=0.05), 80.0) is None  # (a share under 0.1: no rafts)
    assert AD.craft_for(0, 80.0) is None and AD.craft_for(2, 80.0) is None  # (no animal rides a raft)
    assert [c[0] for c in AD.craft_ladder()][0] == "raft or dugout"


def test_closed_country_keeps_peoples_apart(faketz):
    """Competition rises toward exclusion where the contact value is low (crossing.corridor)."""
    from planet.lineages import crossing as C
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    env = ps.fields(0.0, variability=False)
    tags = H._tags(ps.grid, env)
    c = C.corridor(tags, env, None)
    assert c[~tags["land"]].max() == 0 and 0 < c[tags["land"]].min() and c[tags["land"]].max() <= 1
    assert c[tags["coast"]].min() >= c[tags["land"] & tags["mountain"]].max() if (tags["mountain"]).any() else True
    a, b = SP.Lineage("a"), SP.Lineage("b", traits=["flies"])
    assert H.same_way(a, a) == 1.0 and H.same_way(a, b) == 0.5


def _spread_full_sweep(p, room, enter, elev, relief_k, sea, land, nbr_off, nbr_idx, passes):
    """The plain Jacobi sweep over every cell (the reference the front-only spread must equal)."""
    from numba import njit

    @njit
    def sweep(p, room, enter, elev, relief_k, sea, land, nbr_off, nbr_idx, passes, est):
        n = p.shape[0]
        c = p.copy()
        new = c.copy()
        for _ in range(passes):
            changed = False
            for i in range(n):
                best = c[i]
                for k in range(nbr_off[i], nbr_off[i + 1]):
                    j = nbr_idx[k]
                    if c[j] <= best:
                        continue
                    if land[i]:
                        f = enter[i]
                        dh = elev[i] - elev[j]
                        if relief_k > 0 and dh > 0:
                            f *= np.exp(-relief_k * dh / 1000.0)
                    else:
                        f = sea
                    best = max(best, c[j] * f)
                if best > new[i] + 1e-6:
                    new[i] = best
                    changed = True
            c[:] = new
            if not changed:
                break
        for i in range(n):
            if land[i] and c[i] >= est and room[i] > p[i]:
                v = min(room[i], c[i])
                if v >= est and v > p[i]:
                    p[i] = v
        return p
    return sweep(p.copy(), room, enter, elev, relief_k, sea, land, nbr_off, nbr_idx, passes, H.EST)


def test_front_only_spread_equals_the_full_sweep():
    g = build_grid(LEVEL)
    rng = np.random.default_rng(3)
    land = rng.random(g.n) < 0.7
    elev = rng.random(g.n) * 3000
    room = np.where(land, rng.random(g.n), 0.0)
    enter = 0.5 + 0.5 * rng.random(g.n)
    p = np.where(land & (rng.random(g.n) < 0.03), 0.3 + 0.7 * rng.random(g.n), 0.0)
    for passes, sea, rk in ((1, 0.0, 0.6), (3, 0.55, 0.6), (400, 0.3, 0.0)):
        a = H.spread(p.copy(), room, enter, elev, rk, sea, land, g.nbr_off, g.nbr_idx, passes)
        b = _spread_full_sweep(p, room, enter, elev, rk, sea, land, g.nbr_off, g.nbr_idx, passes)
        assert np.array_equal(a, b)


def test_near_wish_pulls_toward_a_shared_border(faketz):
    """A 'near' wish pulls the habitat toward the other's border (not into its range), pulls either
    people's origin toward the other, and the two compete less with each other."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1},
           "lineage": [{"id": "a", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "b", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}],
           "wish": [{"a": "a", "b": "b", "want": "near"}]}
    tree = SP.parse(raw)
    h = H.History(tree, ps, 1)
    g = h.grid
    ia, ib = h.idx["a"], h.idx["b"]
    assert h.alpha[ia, ib] < H.niche_overlap(tree.lines["a"], tree.lines["b"], tree)
    h.p = np.zeros((2, g.n))
    h.active = {"a": True, "b": True}
    land = ps.fields(0.0, variability=False)["land"]
    cell = int(np.argmax(land & (np.abs(g.lon) < 20) & (np.abs(g.lat) < 20)))
    b = H.rings(cell, land, 2, g.nbr_off, g.nbr_idx)
    h.p[ib][b] = 0.8
    m = h._wish_near(tree.lines["a"])
    d = H.graph_dist(b, 100, g.nbr_off, g.nbr_idx)
    assert np.allclose(m[b], 1.0)  # not into b's range
    assert m[d == 1].min() > 1.4 and m[d >= 2].max() < m[d == 1].min()  # (falls off: 300 km is under a cell here)
    h.p[ib][:] = 0
    h.p[ia][b] = 0.8
    mo = h._wish_near(tree.lines["b"], origin=True)  # (either people of the wish, at its origin)
    assert mo[d == 1].min() > 2 and np.allclose(mo[b], 1.0)


def test_apart_wish_cuts_both_peoples_and_scores_against_the_niches(faketz):
    """PW-682: 'apart' keeps each people out of the other's country; its score is against what the niches alone
    would give, and a pair whose niches don't meet isn't counted."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1},
           "lineage": [{"id": "a", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "b", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "c", "appears": "30 kyr", "temp_c": [-60, -50], "rain_mm": [1, 9000]}],
           "wish": [{"a": "a", "b": "b", "want": "apart"}, {"a": "a", "b": "c", "want": "apart"}]}
    tree = SP.parse(raw)
    h = H.History(tree, ps, 1)
    g = h.grid
    ia, ib = h.idx["a"], h.idx["b"]
    h.p = np.zeros((3, g.n))
    h.active = {"a": True, "b": True, "c": False}
    land = ps.fields(0.0, variability=False)["land"]
    cell = int(np.argmax(land & (np.abs(g.lon) < 20) & (np.abs(g.lat) < 20)))
    blob = H.rings(cell, land, 2, g.nbr_off, g.nbr_idx)
    h.p[ib][blob] = 0.8
    assert h._wish_near(tree.lines["a"])[blob].max() < 0.6  # a is cut where b lives...
    h.p[ib][:] = 0
    h.p[ia][blob] = 0.8
    assert h._wish_near(tree.lines["b"])[blob].max() < 0.6  # ...and b where a lives
    tags = H._tags(g, h.steps[-1].get(), h._chains, h._volcanic())
    assert H._niche_closeness(h, tree.wishes[0], tags) > 0.9 > H.APART_CONTESTED  # (the niches overlap everywhere)
    assert H._niche_closeness(h, tree.wishes[1], tags) < H.APART_CONTESTED  # (c lives where a doesn't)
    h.p[ib][blob] = 0.8
    ws = H.wish_scores(h, h.p, tags)
    assert ws[0]["contested"] and ws[0]["score"] < 0.5  # both on the same ground: the wish failed
    h.p[ib][:] = 0
    h.p[ic := h.idx["c"]][:] = 0
    ws = H.wish_scores(h, h.p, tags)
    assert ws[0]["score"] == 1.0 and not ws[1].get("contested", True)  # b gone: kept apart; a/c: nothing to keep apart


def test_contact_hybrid_lingers_when_its_parents_part(faketz):
    """PW-613: a contact hybrid grows where its parents meet, fades where they no longer do, and where they
    last met it lives on as a small people of its own (shown on the peoples layer there)."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1},
           "lineage": [{"id": "a", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "b", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "ab", "origin": "hybrid", "exempt": True, "parents": ["a", "b"], "at": "20 kyr"}]}
    tree = SP.parse(raw)
    h = H.History(tree, ps, 1)
    g = h.grid
    ia, ib, k = h.idx["a"], h.idx["b"], h.idx["ab"]
    h.p = np.zeros((3, g.n))
    h.active = {"a": True, "b": True, "ab": True}
    h._last_meet, h._apart, h._lingered, h.events = {}, set(), set(), []
    h._linger = np.zeros((3, g.n), bool)
    land = ps.fields(0.0, variability=False)["land"]
    cell = int(np.argmax(land & (np.abs(g.lon) < 20) & (np.abs(g.lat) < 20)))
    zone = H.rings(cell, land, 1, g.nbr_off, g.nbr_idx)
    K = np.where(land, 0.9, 0.0)
    step = H.Step(10.0, 1.0, "recent", True, None)
    h.p[ia][zone] = h.p[ib][zone] = 0.6
    h._hybrid(tree.lines["ab"], k, K, step)
    assert np.allclose(h.p[k][zone], 0.6) and not h._linger[k].any()
    h.p[ib][:] = h.p[ia][:] = 0.0  # the parents part (both moved away)
    for _ in range(60):  # 60 kyr: the linger has faded (LINGER_KYR), the last meeting place holds
        h._hybrid(tree.lines["ab"], k, K, step)
    held = h.p[k] >= H.EST
    assert held[zone].all() and h._linger[k][zone].all() and (h.p[k][zone] >= 0.9 * H.LINGER_MIN - 1e-9).all()
    assert [e["kind"] for e in h.events] == ["lingers"]
    f = h._frame(step, {"land": land})
    assert (f["peoples"][zone] == k).all()  # (its own people there, not an overlay)


def test_contact_hybrid_without_linger_vanishes_when_its_parents_part(faketz):
    """PW-758: linger = false: the hybrid lives where its parents meet and nowhere else, no people of its own."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1},
           "lineage": [{"id": "a", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "b", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "ab", "origin": "hybrid", "exempt": True, "parents": ["a", "b"], "at": "20 kyr", "linger": False}]}
    tree = SP.parse(raw)
    assert tree.lines["ab"].linger is False and SP.to_raw(tree)["lineage"][2]["linger"] is False
    h = H.History(tree, ps, 1)
    g = h.grid
    ia, ib, k = h.idx["a"], h.idx["b"], h.idx["ab"]
    h.p = np.zeros((3, g.n))
    h.active = {"a": True, "b": True, "ab": True}
    h._last_meet, h._apart, h._lingered, h.events = {}, set(), set(), []
    h._linger = np.zeros((3, g.n), bool)
    land = ps.fields(0.0, variability=False)["land"]
    cell = int(np.argmax(land & (np.abs(g.lon) < 20) & (np.abs(g.lat) < 20)))
    zone = H.rings(cell, land, 1, g.nbr_off, g.nbr_idx)
    K = np.where(land, 0.9, 0.0)
    step = H.Step(10.0, 1.0, "recent", True, None)
    h.p[ia][zone] = h.p[ib][zone] = 0.6
    h._hybrid(tree.lines["ab"], k, K, step)
    assert np.allclose(h.p[k][zone], 0.6)
    h.p[ib][:] = h.p[ia][:] = 0.0
    for _ in range(3):
        h._hybrid(tree.lines["ab"], k, K, step)
    assert not (h.p[k] >= H.EST).any() and not h._linger[k].any() and not h.events


def test_start_hints_place_an_origin_near_far_and_in_a_band(faketz):
    """PW-763: near / far_from / lat_band / landmass on a root's origin (soft multipliers on its placement)."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "a", "appears": "30 kyr", **base},
        {"id": "far", "appears": "20 kyr", "far_from": ["a"], **base},
        {"id": "near", "appears": "20 kyr", "near": ["a"], **base},
        {"id": "band", "appears": "20 kyr", "lat_band": [10, 25], **base}]}
    tree = SP.parse(raw)
    assert tree.lines["far"].start_far == ["a"] and {r["id"]: r for r in SP.to_raw(tree)["lineage"]}["band"]["lat_band"] == [10, 25]
    h = H.History(tree, ps, 1)
    g = h.grid
    land = ps.fields(0.0, variability=False)["land"]
    tags = {"land": land}
    cell = int(np.argmax(land & (np.abs(g.lon) < 20) & (np.abs(g.lat) < 20)))
    h.p = np.zeros((4, g.n))
    h.p[h.idx["a"]][H.rings(cell, land, 2, g.nbr_off, g.nbr_idx)] = 0.8
    h.active = {"a": True}
    d = H.graph_dist(h.p[h.idx["a"]] > H.EST, 400, g.nbr_off, g.nbr_idx)
    mf, mn = h._start_hints(tree.lines["far"], {}, tags), h._start_hints(tree.lines["near"], {}, tags)
    assert mf[cell] < 0.1 < mf[d > 10].max()
    assert mn[(d > 0) & (d < 4)].mean() > mn[d > 10].mean()
    mb = h._start_hints(tree.lines["band"], {}, tags)
    assert mb[(g.lat > 12) & (g.lat < 23)].min() == 1.0 and mb[g.lat < -30].max() < 0.01
    with pytest.raises(ValueError, match="unknown line"):
        SP.parse({"lineage": [{"id": "x", "appears": "1 Myr", "near": ["nope"]}]})


def test_land_use_moves_a_people_toward_its_goods(faketz):
    """[[use]]: a line's habitat is x(1 - pull + pull G) over the goods its traits look for, normalised to a
    mean of 1 over its own country; avoided goods cut; in the deep epochs the land use is off, and before
    the Holocene only the geology counts."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1, "land_pull": 0.5},
           "lineage": [{"id": "dw", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000], "traits": ["miner"]},
                       {"id": "hu", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000],
                        "traits": ["seafaring"]}],
           "use": [{"by": "miner", "good": "gold"}, {"by": "seafaring", "good": "nav_hazard", "weight": -1},
                   {"by": "seafaring", "good": "fertile", "weight": 0.5}]}
    tree = SP.parse(raw)
    assert SP.parse(SP.to_raw(tree)).uses == tree.uses
    with pytest.raises(ValueError):
        SP.parse({**raw, "use": [{"by": "miner", "good": "unobtainium"}]})
    g = build_grid(LEVEL)
    land = ps.fields(0.0, variability=False)["land"]
    gold = np.where(land & (g.lat > 0), 1.0, 0.0)
    goods = {"gold": gold, "nav_hazard": np.where(land & (g.lon > 0), 1.0, 0.0), "fertile": np.zeros(g.n)}
    h = H.History(tree, ps, 1, goods=goods)
    m = h._land_mult(tree.lines["dw"], True)
    hab = H.capacity(tree.lines["dw"], *h._pres) > 0.25
    assert abs(m[hab].mean() - 1) < 1e-9 and m[gold > 0].min() > 1.2 * m[land & (gold == 0)].max()
    mh = h._land_mult(tree.lines["hu"], True)
    assert mh[land & (g.lon > 0)].max() < mh[land & (g.lon <= 0)].min()  # (avoids the hazards)
    assert np.isscalar(h._land_mult(tree.lines["hu"], False)) or np.allclose(h._land_mult(tree.lines["hu"], False), 1)
    env = ps.fields(0.0, variability=False)
    tags = H._tags(g, env)
    deep = H.Step(500.0, 1.0, "deep", True, None)
    assert np.allclose(h._K(tree.lines["dw"], env, tags, deep), H.capacity(tree.lines["dw"], env, tags))


def test_a_use_can_name_a_line_and_its_own_pull(faketz):
    """[[use]] by a line's id applies to that line only; its pull overrides meta.land_pull (the strongest
    pull of a line's favoured goods); the volcanic and hills place tags exist (volcanic only with goods)."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1, "land_pull": 0.5},
           "lineage": [{"id": "fire", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "other", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}],
           "use": [{"by": "fire", "good": "volcanic", "pull": 0.9}]}
    tree = SP.parse(raw)
    assert SP.parse(SP.to_raw(tree)).uses == tree.uses
    assert tree.uses_of(tree.lines["other"]) == [] and tree.pull_of(tree.lines["fire"]) == 0.9
    with pytest.raises(ValueError):
        SP.parse({**raw, "use": [{"by": "fire", "good": "volcanic", "pull": 2}]})
    g = build_grid(LEVEL)
    env = ps.fields(0.0, variability=False)
    land = env["land"]
    volc = np.where(land & (g.lat > 0), 1.0, 0.0)
    h = H.History(tree, ps, 1, goods={"volcanic": volc})
    m = h._land_mult(tree.lines["fire"], True)
    assert m[volc > 0].min() > 5 * m[land & (volc == 0)].max()  # (1 - 0.9 + 0.9) / (1 - 0.9) = 10
    strict = SP.parse({**raw, "use": [{"by": "fire", "good": "volcanic", "pull": 0.9, "strict": True}]})
    assert SP.parse(SP.to_raw(strict)).uses == strict.uses and strict.strict_of(strict.lines["fire"])
    ms = H.History(strict, ps, 1, goods={"volcanic": volc})._land_mult(strict.lines["fire"], True)
    assert np.allclose(ms[land & (volc == 0)], 0.1) and np.allclose(ms[volc > 0], 1.0)  # (not renormalised)
    tags = H._tags(g, env, False, h._volcanic())
    assert (tags["volcanic"] == (tags["land"] & (volc > 0))).all() and not H._tags(g, env)["volcanic"].any()
    assert not (tags["hills"] & tags["mountain"]).any() and not (tags["hills"] & ~tags["land"]).any()


def test_demography_defaults_inheritance_and_numbers(faketz):
    """PW-650: the four knobs come from the traits unless given, a split inherits what its parent was given;
    a sparse people's small separate patch fades below the viable population (its largest never does);
    the population is presence x density x area, and each landmass says who found it first."""
    from planet.lineages import crossing as C
    raw = {"meta": {"name": "d", "seed": 1, "viable_pop": 500},
           "lineage": [{"id": "g", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000],
                        "kind": 0.8, "traits": ["insular"]},
                       {"id": "g2", "parents": ["g"], "at": "10 kyr"},
                       {"id": "f", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000],
                        "traits": ["agricultural", "seafaring"]}]}
    t = SP.parse(raw)
    assert t.lines["g2"].demo("kind") == 0.8 and t.lines["g"].demo("insularity") == SP.DEMOGRAPHY["insular"]["insularity"]
    assert t.lines["f"].demo("kind") == 1.0 and t.lines["f"].demo("sea_share") == 0.6
    assert SP.parse(SP.to_raw(t)).lines["g2"].kind == 0.8
    for bad in ({"density": 2}, {"band_km2": 10}, {"kind": 3}):  # (PW-1275: density comes from the ladder; kind within 0.5-2)
        with pytest.raises(ValueError):
            SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", **bad}]})
    assert C.hop_mult(t.lines["f"]) > 2 * C.hop_mult(t.lines["g"])
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "sea_share": 2}]})
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(t, ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    h.faded = {}
    env = ps.fields(0.0, variability=False)
    k = h.idx["g"]
    h.dens[k] = 1e-5  # (PW-1275: no world, no ladder: the number the test needs)
    big = env["land"] & (np.abs(h.grid.lon) < 50)
    small = env["land"] & (h.grid.lon < -100) & (h.grid.lon > -140)  # the fake island
    h.p[k][big | small] = 0.5
    h._viable(t.lines["g"], k, 4.0, None)
    assert (h.p[k][big] == 0.5).all() and not (h.p[k][small] > 0).any()
    pop = h.population(k)
    assert abs(pop.sum() - 0.5 * big.sum() * 1e-5 * h.cell_mkm2 * 1e6) < 1e-6 * pop.sum()
    _, _, pres = H.simulate(t, ps, tries=1)
    # (PW-1558: g2 is no longer stranded on a fake island, so compare people per km2, not head counts: f's
    # agricultural/seafaring defaults give it the denser country; g2's sparse defaults come from insular g)
    lf, l2 = pres["lines"]["f"], pres["lines"]["g2"]
    assert lf["area_mkm2"] > 0 and l2["area_mkm2"] > 0
    assert lf["population"] / lf["area_mkm2"] > l2["population"] / l2["area_mkm2"]
    first = [m for m in pres["landmasses"] if m["discovered"]]
    assert first and all(m["discovered"]["by"] in t.lines for m in first)


def test_groups_within_a_people(faketz):
    """PW-665: a group is a way of life within a people (origin 'group', group_of): it inherits what it leaves
    out (demography too), never ends its people, appears where its own niche beats its people's, mixes with it
    as kin (no closed-country exclusion), keeps a range of its own, and rolls up into its people in the summaries."""
    raw = {"meta": {"name": "g", "seed": 3},
           "lineage": [{"id": "orc", "origin": "root", "at": "30 kyr", "temp_c": [0, 18], "rain_mm": [1, 9000]},
                       {"id": "warm_orc", "origin": "group", "group_of": "orc", "at": "10 kyr", "temp_c": [16, 32]},
                       {"id": "elf", "origin": "root", "at": "30 kyr", "temp_c": [0, 18], "rain_mm": [1, 9000]},
                       {"id": "half", "origin": "hybrid", "exempt": True, "parents": ["orc", "elf"], "at": "5 kyr"}],
           "wish": [{"a": "elf", "b": "orc", "want": "apart"}]}
    t = SP.parse(raw)
    g = t.lines["warm_orc"]
    assert g.origin == "group" and g.group_of == "orc" and t.groups_of("orc") == ["warm_orc"] and t.people_of("warm_orc") == "orc"
    assert g.demo("kind") == 1.0 and g.rain_mm == (1.0, 9000.0) and t.lines["orc"].children == []
    assert {l.id for l in t.leaves()} >= {"orc", "warm_orc"}  # (a group never ends its people)
    assert SP.parse(SP.to_raw(t)).lines["warm_orc"].group_of == "orc"
    assert SP.parse({**raw, "lineage": [raw["lineage"][0], {k: v for k, v in raw["lineage"][1].items() if k != "at"}], "wish": []}
                    ).lines["warm_orc"].ago_kyr == SP.GROUP_KYR
    off = SP.parse({**raw, "lineage": [{**raw["lineage"][0], "enabled": False}, *raw["lineage"][1:]], "wish": []})
    assert "warm_orc" in off.disabled  # (no groups without their people)
    with pytest.raises(ValueError):  # (a group of a group)
        SP.parse({**raw, "lineage": [*raw["lineage"], {"id": "x", "origin": "group", "group_of": "warm_orc", "at": "1 kyr"}]})
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(t, ps, 1)
    i, j, e = h.idx["warm_orc"], h.idx["orc"], h.idx["elf"]
    assert h.terr[i, j] == 0 and h.terr[j, i] == 0 and h.terr[j, e] > 0
    assert h.alpha[i, j] == 1.0 and h.alpha[j, i] == 1.0  # (kin: one capacity, PW-1205)
    h, res, pres = H.simulate(t, ps, tries=1)
    assert "orc" not in h.ended and "warm_orc" in h.origins
    assert h.origins["warm_orc"]["why"].startswith("where its way of life")
    P = res["present"]
    po, pg = P[h.idx["orc"]] >= H.EST, P[h.idx["warm_orc"]] >= H.EST
    assert po.any() and pg.any()
    assert (P[h.idx["orc"]] + P[h.idx["warm_orc"]] <= 1.0 + 1e-9).all()  # (one people, one capacity: its ways of life never stack, PW-1205)
    temp = ps.fields(0.0, variability=False)["temperature"]
    assert temp[pg].mean() > temp[po].mean() + 3  # (each holds the land its way of life suits)
    w = pres["peoples"]["orc"]
    assert w["groups"] == ["warm_orc"] and pres["lines"]["warm_orc"]["group_of"] == "orc"
    assert w["population"] == pres["lines"]["orc"]["population"] + pres["lines"]["warm_orc"]["population"]
    assert w["area_mkm2"] >= max(pres["lines"]["orc"]["area_mkm2"], pres["lines"]["warm_orc"]["area_mkm2"])
    assert np.array_equal(h.whole("orc", P) >= H.EST, po | pg)
    assert all(not {"orc", "warm_orc"} <= set(z["lines"]) for z in pres["mixing_zones"])  # (one people, not a mix)
    out = O.save(h, res, pres, name="test groups")
    run = json.loads((out / "run.json").read_text())
    ml = {l["id"]: l for l in run["meta"]["lineages"]}
    assert ml["warm_orc"]["group_of"] == "orc" and ml["orc"]["groups"] == ["warm_orc"]
    assert ml["warm_orc"]["color"] == O.tint(ml["orc"]["color"], 0) and "way of life" in ml["warm_orc"]["story"]
    _, arr = T.load_frames(out, ("peoples", "peoples_whole"))
    last = arr["peoples_whole"][-1]
    assert not (last == h.idx["warm_orc"]).any() and ((arr["peoples"][-1] == h.idx["warm_orc"]) <= (last == h.idx["orc"])).all()
    assert "Peoples with their groups" in (out / "run.txt").read_text()
    _, ga = T.load_frames(out, ("groups_best", "groups_best_pct"))  # (a group's own range at every frame, PW-742)
    gl = ga["groups_best"][-1]
    assert (gl == h.idx["warm_orc"]).any() and set(np.unique(gl).tolist()) <= {h.idx["warm_orc"], 255}
    assert (ga["groups_best_pct"][-1][gl == 255] == 0).all() and (ga["groups_best_pct"][-1][gl == h.idx["warm_orc"]] >= 12).all()


def test_an_among_wish_lets_a_people_share_a_friendly_peoples_country_and_a_squeezed_people_integrates(faketz):
    """PW-889: 'among' (a lives readily inside b's country) cuts the pair's competition by AMONG_TOLERANCE both ways, more than 'near', with
    no frontier invasion between them, raises their cohabitation and leaves the habitat alone; a squeezed people (crowded and holding
    little of its country) feels its friendlier rivals less, in proportion to how readily they live side by side."""
    from planet.lineages import compose as CP
    from planet.lineages.history import pressure as PR
    base = {"meta": {"seed": 1}, "lineage": [
        {"id": "gob", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "bug", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "elf", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}]}
    near = {**base, "wish": [{"a": "bug", "b": "gob", "want": "near"}]}
    among = {**base, "wish": [{"a": "bug", "b": "gob", "want": "among"}]}
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h0, hn, ha = (H.History(SP.parse(r), ps, 1) for r in (base, near, among))
    b, gb, e = ha.idx["bug"], ha.idx["gob"], ha.idx["elf"]
    assert ha.alpha[b, gb] == pytest.approx(h0.alpha[b, gb] * (1 - H.AMONG_TOLERANCE)) and ha.alpha[gb, b] == pytest.approx(h0.alpha[gb, b] * (1 - H.AMONG_TOLERANCE))
    assert ha.alpha[b, gb] < hn.alpha[b, gb] < h0.alpha[b, gb] and ha.alpha[b, e] == h0.alpha[b, e]
    assert ha._among[b, gb] and ha._among[gb, b] and not ha._among[b, e] and not hn._among.any()
    assert ha.cohab[b, gb] > h0.cohab[b, gb] and ha.cohab[b, gb] == pytest.approx(hn.cohab[b, gb])
    t = SP.parse(among)
    env = ps.fields(0.0, variability=False)
    ha.active = {x: True for x in ("gob", "bug", "elf")}
    ha.p = np.zeros((3, ha.grid.n))
    ha.p[gb] = 0.5
    assert np.array_equal(ha._wish_near(t.lines["bug"]), np.ones(ha.grid.n))  # (no pull or push on the habitat)
    with pytest.raises(ValueError):
        SP.parse({**base, "wish": [{"a": "bug", "want": "among"}]})
    assert SP.parse(SP.to_raw(t)).wishes[0].want == "among"
    # the squeeze: crowding x how little of its country a people holds
    assert PR.squeeze(0.8, 100, 2000) == pytest.approx(0.8 * (1 - 100 / (H.SQUEEZE_FILL * 2000)))
    assert PR.squeeze(0.8, 1500, 2000) == 0.0 and PR.squeeze(0.0, 10, 2000) == 0.0
    w = PR.integration_weights(np.array([1.0, 0.5, 0.0]), 1.0)
    assert w[0] == pytest.approx(1 - H.INTEGRATE) and w[1] == pytest.approx(1 - 0.5 * H.INTEGRATE) and w[2] == 1.0
    assert CP.cohabitation(t, ha.lines, ha.idx)[b, gb] > CP.cohabitation(SP.parse(base), h0.lines, h0.idx)[b, gb]


def test_city_minorities_are_gone():
    """PW-1369 (11-02): the city minorities (groups with `cities`, PW-889) were removed until a towns and minorities model: a tree that
    still gives `cities` or `hosts` is refused with a pointer, and the D&D preset has no groups left."""
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "human", "origin": "root", "at": "30 kyr"}, {"id": "gob", "origin": "root", "at": "30 kyr"},
        {"id": "town_gob", "origin": "group", "group_of": "gob", "at": "5 kyr", "cities": True}]}
    with pytest.raises(ValueError, match="PW-1369"):
        SP.parse(raw)
    with pytest.raises(ValueError, match="PW-1369"):
        SP.parse({**raw, "lineage": [*raw["lineage"][:2], {"id": "town_gob", "origin": "group", "group_of": "gob", "hosts": ["human"]}]})
    t = SP.load(Path(SP.__file__).parent / "samples" / "dnd.toml")
    assert not [l.id for l in t.lines.values() if l.origin == "group"]


def test_peoples_change_the_land_from_their_ways_of_life():
    """PW-662: shares come from the [[use]] table, not names; fields, pasture, fire and woods follow the people."""
    from planet.lineages import landuse as LU
    t = SP.load(LR.tree_path("dnd"))
    s = {k: LU.shares(t, t.lines[k]) for k in ("human", "hobgoblin", "hill_giant", "dwarf")}
    assert s["human"]["farm"] == 1 and s["hill_giant"]["herd"] == 1 and s["hobgoblin"]["farm"] == s["hobgoblin"]["herd"] == 0.5
    assert s["dwarf"]["farm"] == 1  # (PW-1351: dwarves farm their valleys; the density ladder decides per cell, PW-1275)
    n = 4
    z, one = np.zeros(n), np.ones(n)
    fcls = np.array([4, 4, 1, 0])
    # farmers: dense on prime land clear more than sparse; poor land is capped; no farmland, no fields
    out = LU.cover(np.array([20, 5, 20, 20.0]), np.array([20, 5, 20, 20.0]), z, z, 0.8 * one, fcls, 0.5 * one)
    assert out["crop"][0] > out["crop"][1] > 0 and out["crop"][2] <= LU.CROP_CAP[1] and out["crop"][3] == 0
    assert out["tree_after"][3] < 0.8  # (wood cutting thins even there)
    assert (out["crop"] + out["pasture"] + out["burned"] <= 1 + 1e-9).all()
    # herders: pasture and burned grassland on grazing land, none without grazing
    h = LU.cover(np.full(n, 3.0), z, np.full(n, 3.0), z, 0.4 * one, np.zeros(n, int), np.array([0.8, 0.8, 0.05, 0.8]))
    assert h["pasture"][0] > 0 and h["burned"][0] > 0 and h["pasture"][2] == 0 and h["burned"][2] == 0 and (h["crop"] == 0).all()
    # nobody, nothing
    e = LU.cover(z, z, z, z, 0.8 * one, fcls, one)
    assert (e["crop"] == 0).all() and (e["pasture"] == 0).all() and np.allclose(e["tree_after"], 0.8)


# ---- senses and bodies (PW-694) ---------------------------------------------------------------------
def test_body_traits_default_inherit_and_round_trip():
    dnd = SP.load(LR.SAMPLES / "dnd.toml")
    b = lambda k: dnd.lines[k].body  # noqa: E731
    # real-world analogues: cats taste no sweet, birds feel no capsaicin, herding peoples keep lactase
    assert not b("tabaxi")["sweet"] and not b("leonin")["sweet"] and b("leonin")["diet"] == "obligate_carnivore"
    assert not b("aarakocra")["capsaicin"] and not b("kenku")["sweet"] and b("human")["capsaicin"] and b("human")["sweet"]
    assert not b("human")["milk"]  # (the herders' lactase went with the human herder groups, PW-1357: inbox draft)
    assert set(b("tabaxi")["toxic"]) == {"alliums", "theobromine"} and b("human")["toxic"] == []
    assert dnd.lines["tabaxi"].body_given == {}  # (inherited from the feline stem, not given)
    assert SP.parse(SP.to_raw(dnd)).lines["tabaxi"].body == b("tabaxi")
    assert SP.body_notes(SP.BODY_DEFAULT) == [] and "cannot taste sweet" in SP.body_notes(b("leonin"))
    base = {"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "body": {"toxic": ["alliums"], "smell": "keen"}},
                        {"id": "y", "parents": ["x"], "at": "0.5 kyr", "body": {"smell": "low"}}]}
    t = SP.parse(base)
    assert t.lines["y"].body["smell"] == "low" and t.lines["y"].body["toxic"] == ["alliums"] and t.lines["y"].body["sweet"]
    for bad in ({"sweet": "yes"}, {"diet": "frugivore"}, {"toxic": ["lead"]}, {"taste": 1}):
        with pytest.raises(ValueError):
            SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "body": bad}]})


# ---- composition of peoples per cell (PW-689) and body shares (PW-701) ------------------------------
def test_body_flags_can_be_a_share_of_a_people():
    dnd = SP.load(LR.SAMPLES / "seven_meals.toml")  # (the dnd preset's herder groups are gone, PW-1357)
    herd = next(l for l in dnd.lines.values() if isinstance(l.body.get("milk"), float) and 0 < l.body["milk"] < 1)
    assert dnd.share_traits() == ["milk"]
    assert f"{round(100 * herd.body['milk'])}% digest milk as adults" in SP.body_notes(herd.body)
    assert SP.parse(SP.to_raw(dnd)).lines[herd.id].body["milk"] == herd.body["milk"]
    for bad in (1.5, -0.1, "some"):
        with pytest.raises(ValueError):
            SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "body": {"milk": bad}}]})


def test_composition_follows_who_reaches_and_tolerates_a_place():
    from planet.lineages import compose as CP
    t = SP.parse({"lineage": [{"id": "a", "origin": "root", "at": "9 kyr"}, {"id": "b", "origin": "root", "at": "9 kyr"},
                              {"id": "c", "origin": "root", "at": "9 kyr", "traits": ["insular"]}],
                  "wish": [{"a": "a", "b": "b", "want": "near"}, {"a": "a", "b": "c", "want": "apart"}]})
    lines = t.order()
    idx = {l.id: k for k, l in enumerate(lines)}
    H_ = CP.cohabitation(t, lines, idx)
    ia, ib, ic = idx["a"], idx["b"], idx["c"]
    assert np.allclose(H_, H_.T) and H_[ia, ib] > 0.5 > H_[ia, ic]  # (near pairs mix readily, apart or insular ones rarely)
    Pw = np.zeros((3, 1))
    Pw[ia], Pw[ib], Pw[ic] = 0.8, 0.5, 0.5
    early = CP.compose(Pw, Pw, H_, 0.0, 0.12)
    late = CP.compose(Pw, Pw, H_, 1.0, 0.12)
    for c in (early, late):
        assert int(c["mix_lead_share"][0]) + int(c["mix_second_share"][0]) + int(c["mix_other_share"][0]) == 100
    assert early["mix_lead_share"][0] > late["mix_lead_share"][0]  # (little intermingling before the late mixing)
    assert late["mix_second"][0] == ib  # (the tolerated people is second)
    z = CP.compose(np.zeros((3, 2)), np.zeros((3, 2)), H_, 1.0, 0.12)
    assert (z["mix_lead_share"] == 0).all() and (z["mix_second"] == 255).all()
    m = CP.compose(Pw, Pw, H_, 1.0, 0.12, {"milk": np.array([[0.0], [1.0], [0.0]])})  # (a trait share mixed by the composition)
    assert abs(int(m["body_milk"][0]) - int(m["mix_second_share"][0])) <= 1


# ---- animals (PW-691) and boats (PW-688 part 2) --------------------------------------------------------------------
def test_wild_horse_range_is_open_temperate_grassland():
    from planet.lineages import animal_defs as AD
    n = 6  # steppe, forest, desert, tundra, tropical savanna, high plateau
    env = {"temperature": np.array([8, 8, 15, -10, 28, 8.0]), "precipitation": np.array([500, 1200, 80, 300, 900, 400.0]),
           "tree_cover": np.array([5, 70, 0, 0, 10, 0.0]), "elevation": np.array([300, 300, 300, 300, 300, 5000.0]), "ice": np.zeros(n)}
    w = AD.wild_horse(env, {}, np.ones(n, bool))
    assert w[0] == 1 and (w[1:] < 0.35).all() and (AD.wild_horse(env, {}, np.zeros(n, bool)) == 0).all()
    # the other animals read the same land differently: dogs nearly anywhere with rain, cattle only on moist ground
    assert AD.wild_dog(env, {}, np.ones(n, bool))[[0, 1, 3, 4]].min() > 0.9 and AD.wild_dog(env, {}, np.ones(n, bool))[2] < 0.5
    tags = {k: np.zeros(n, bool) for k in ("hills", "mountain", "wetland")}
    moist = {**env, "temperature": np.full(n, 15.0), "precipitation": np.array([1200, 1200, 80, 1200, 1200, 1200.0]), "tree_cover": np.full(n, 10.0)}
    wc = AD.wild_cattle(moist, tags, np.ones(n, bool))
    assert wc[0] > 0.9 and wc[2] == 0 and wc[5] == 0  # (moist grass: yes; desert and the high plateau: no)


def test_craft_ladder_and_mode_gates():
    from planet.lineages import animal_defs as AD
    assert AD.craft_for(0, 70.0) is None and AD.craft_for(0, 40.0)[0].startswith("canoe")
    assert AD.craft_for(1, 40.0) is None and AD.craft_for(1, 4.0)[0] == "planked boat"  # (a sheep needs a planked boat)
    assert AD.craft_for(2, 4.0) is None and AD.craft_for(2, 2.0)[0] == "sailing ship"  # (a horse needs a sailing ship)
    assert [a.id for a in AD.resolve(None, [], "fantasy")] == list(AD.REAL_IDS)  # (fantasy rows are off by default)
    assert "great_elk" in [a.id for a in AD.resolve(None, ["great_elk"], "fantasy")]
    assert "great_elk" not in [a.id for a in AD.resolve(["great_elk"], ["great_elk"], "real")]  # (and gone in the real-world mode)
    raw = {"meta": {"animals": ["horse"], "animals_force": ["great_elk", "riding_lizard"], "mode": "real"},
           "lineage": [{"id": "a", "origin": "root", "at": "9 kyr", "real": True}]}
    t = SP.parse(raw)
    assert t.animals == ["horse"] and t.animals_force == []
    assert SP.parse({**raw, "meta": {**raw["meta"], "mode": "fantasy"}}).animals_force == ["great_elk", "riding_lizard"]
    with pytest.raises(ValueError):
        SP.parse({**raw, "meta": {"animals": ["unicorn"]}})


def _animal_tree(animals=("horse",), force=(), mode="fantasy", seed=1):
    raw = {"meta": {"name": "h", "seed": seed, "mixing_start": "3 kyr", "mode": mode, "animals": list(animals), "animals_force": list(force),
                    "animals_at": {"horse": "9 kyr", "dog": "20 kyr", "great_elk": "9 kyr"}}, "lineage": [
        {"id": "herd", "origin": "root", "at": "30 kyr", "temp_c": [-5, 35], "rain_mm": [50, 6000], "traits": ["nomadic"], "real": True},
        # (an arrival: two roots would start on landmasses of their own, PW-888, and the test wants them to meet)
        {"id": "farm", "origin": "arrival", "at": "30 kyr", "temp_c": [-5, 35], "rain_mm": [50, 6000], "traits": ["agricultural"], "real": True}],
        "use": [{"by": "nomadic", "good": "grazing"}, {"by": "agricultural", "good": "fertile"}]}
    return SP.parse(raw)


def test_horses_are_tamed_where_herders_meet_the_wild_range_and_riding_spreads(faketz, monkeypatch):
    import dataclasses
    from planet.lineages import animal_defs as AD
    wild = lambda env, tags, land: np.where(land & (np.abs(env["temperature"] - 12) < 8), 0.9, 0.0)  # noqa: E731
    horse = dataclasses.replace(AD.BY_ID["horse"], wild=wild)
    monkeypatch.setattr(AD, "TABLE", tuple(horse if a.id == "horse" else a for a in AD.TABLE))
    # a taming is chance (about half of the seeds on this fake world): the claims hold in EVERY seed that tames, and the rate is asserted
    seeds, tamed_in, riders = range(1, 9), [], []
    for sd in seeds:
        ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=sd))
        h, res, pres = H.simulate(_animal_tree(seed=sd), ps, tries=1)
        hs = pres["animals"]["stocks"]["horse"]
        if not hs["tamed"]:
            assert hs["never"] and hs["known_mkm2"] == 0
            continue
        tamed_in.append(sd)
        t = hs["tamed"][0]
        assert t["line"] == "herd" and t["first"] and t["ago_kyr"] <= hs["date_drawn_kyr"] + 1e-6 and hs["wild_mkm2"] > 0
        assert hs["known_mkm2"] > 0 and hs["users_share"]["farm"] > 0
        # the herders ride wherever they still hold ground on the landmass where they tamed it; a line the farmers have squeezed
        # off that landmass by the end (seed 4: 106 -> 3 Mkm2, its last 6 cells an island the horse never reached) has no horse to ride (PW-783)
        from planet.lineages.spread import EST
        lab = h.cross.label
        # (PW-794: a contact-speed mount also crosses a land bridge while it lasts, so "the landmass where they tamed it" is every landmass its use reached)
        reached = [c for c, nm in enumerate(h.cross.names) if nm["name"] in hs["reached_kyr"]]
        home = (h.p[h.idx["herd"]] >= EST) & np.isin(lab, reached)
        riders.append((sd, bool(home.any()), hs["users_share"]["herd"]))
        assert hs["propensity"]["herd"] == 1.0 and hs["propensity"]["farm"] < hs["propensity"]["herd"]
        assert any(e["kind"] == "animals" for e in h.events) and not hs["fantasy"]
        keep = (h, res, pres, ps)
    assert len(tamed_in) >= len(seeds) // 4, tamed_in  # (it was 4 of 8 when this was written)
    assert all(r > 0.5 for _, on_home, r in riders if on_home), riders  # herders ride across their land in EVERY seed that tames and where they still hold the horse's landmass
    assert all(r == 0.0 for _, on_home, r in riders if not on_home), riders  # (and a line on a landmass the horse never reached rides nothing)
    assert any(on_home for _, on_home, _ in riders), riders
    h, res, pres, ps = keep
    # layers on the run (bit flags), and the story says so
    out = O.save(h, res, pres, name="horse test")
    run = json.loads((out / "run.json").read_text())
    assert {"animal_wild", "animal_known"} <= run["layers"].keys() and run["meta"]["animals"]["stocks"]["horse"]["tamed"][0]["line"] == "herd"
    assert "first to tame the horse" in run["meta"]["lineages"][h.idx["herd"]]["story"]
    assert "Animals" in (out / "run.txt").read_text() and "sailing ship" in (out / "run.txt").read_text()
    # none: nothing is stored
    h0, res0, pres0 = H.simulate(_animal_tree(()), ps, tries=1)
    assert pres0["animals"] is None and h0.animals is None
    assert "animal_wild" not in json.loads((O.save(h0, res0, pres0, name="no animals") / "run.json").read_text())["layers"]


def test_dairy_comes_from_the_herd_and_the_way_of_life_not_from_lactase(faketz, monkeypatch):
    """PW-784: a herding people with no lactase still has dairy (fermented, the brief says), and `milks = false` takes it away."""
    import dataclasses
    from planet.lineages import animal_defs as AD
    assert SP.parse_body({"milks": False}) == {"milks": False} and SP.BODY_DEFAULT["milks"] is True
    assert "do not milk their animals" in SP.body_notes({**SP.BODY_DEFAULT, "milks": False})
    with pytest.raises(ValueError):
        SP.parse_body({"milks": 0.5})
    wild = lambda env, tags, land: np.where(land & (np.abs(env["temperature"] - 12) < 8), 0.9, 0.0)  # noqa: E731
    horse = dataclasses.replace(AD.BY_ID["horse"], wild=wild)
    monkeypatch.setattr(AD, "TABLE", tuple(horse if a.id == "horse" else a for a in AD.TABLE))
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    for milks in (True, False):
        tree = _animal_tree(seed=1)
        tree.lines["herd"].body["milk"] = 0.0  # (nobody digests fresh milk)
        tree.lines["herd"].body["milks"] = milks
        h, res, pres = H.simulate(tree, ps, tries=1)
        dairy = pres["animals"]["dairy"]
        assert pres["animals"]["stocks"]["horse"]["tamed"], "seed 1 tames the horse on the fake world"
        if milks:
            d = dairy["herd"]
            assert d["lactase_share"] == 0.0 and d["milks_share"] > 0.9 and d["dairy_share"] > 0 and "horse" in d["animals"]
            assert "farm" not in dairy or dairy["farm"]["dairy_share"] < d["dairy_share"]  # (farmers milk less, by their herd share)
        else:
            assert "herd" not in dairy


def test_fantasy_animals_are_off_unless_forced_and_never_in_real_mode(faketz, monkeypatch):
    import dataclasses
    from planet.lineages import animal_defs as AD
    wild = lambda env, tags, land: np.where(land, 0.9, 0.0)  # noqa: E731
    elk = dataclasses.replace(AD.BY_ID["great_elk"], wild=wild, rare=0.0)  # (a taming that never happens by chance)
    monkeypatch.setattr(AD, "TABLE", tuple(elk if a.id == "great_elk" else a for a in AD.TABLE))
    monkeypatch.setattr(AD, "BY_ID", {a.id: a for a in AD.TABLE})
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h, res, pres = H.simulate(_animal_tree(("horse", "great_elk")), ps, tries=1)  # (listed, but rare: not here)
    assert pres["animals"]["stocks"]["great_elk"]["never"] and not pres["animals"]["stocks"]["great_elk"]["tamed"]
    h, res, pres = H.simulate(_animal_tree(("horse",), force=("great_elk",)), ps, tries=1)  # (forced: always)
    st = pres["animals"]["stocks"]["great_elk"]
    assert st["fantasy"] and st["tamed"] and st["known_mkm2"] > 0
    h, res, pres = H.simulate(_animal_tree(("horse",), force=("great_elk",), mode="real"), ps, tries=1)
    assert "great_elk" not in pres["animals"]["stocks"]
    assert "great_elk" not in pres["animals"]["stocks"] and "riding_lizard" not in pres["animals"]["stocks"]


def test_no_wild_range_no_taming(faketz):
    # (the fake world is forested everywhere: nowhere for wild horses)
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h, res, pres = H.simulate(_animal_tree(), ps, tries=1)
    hs = pres["animals"]["stocks"]["horse"]
    assert hs["tamed"] == [] and hs["never"] and not h.animals.stocks[0].rd.any()


def test_composition_is_by_heads_not_ground_held():
    from planet.lineages import compose as CP
    t = SP.parse({"lineage": [{"id": "a", "origin": "root", "at": "9 kyr"}, {"id": "b", "origin": "root", "at": "9 kyr"}]})
    lines = t.order()
    H_ = CP.cohabitation(t, lines, {l.id: k for k, l in enumerate(lines)})
    Pw = np.array([[0.8], [0.8]])  # equal ground held
    even = CP.compose(Pw, Pw, H_, 1.0, 0.12)
    dense = CP.compose(Pw, Pw, H_, 1.0, 0.12, dens=np.array([1.0, 6.0]))
    assert abs(int(even["mix_lead_share"][0]) - 100 * 1 / (1 + H_[0, 1])) <= 1
    # b has six times the heads per km2: it outweighs a, so it is the composition's leader (PW-705), the share a "lead" should be
    assert dense["mix_lead"][0] == 1 and dense["mix_second"][0] == 0
    assert dense["mix_lead_share"][0] > dense["mix_second_share"][0]
    assert even["mix_lead"][0] in (0, 1) and dense["mix_lead_share"][0] > even["mix_lead_share"][0]


def test_era_is_a_validated_placeholder_setting():
    raw = {"lineage": [{"id": "a", "origin": "root", "at": "9 kyr"}]}
    assert SP.parse(raw).era == "renaissance"
    t = SP.parse({**raw, "meta": {"era": "Bronze Age"}})
    assert t.era == "bronze age" and SP.parse(SP.to_raw(t)).era == "bronze age"
    with pytest.raises(ValueError):
        SP.parse({**raw, "meta": {"era": "space age"}})


def test_a_use_pulls_in_proportion_to_its_weight():
    raw = {"meta": {"land_pull": 0.5}, "lineage": [{"id": "a", "origin": "root", "at": "9 kyr", "traits": ["miner"]}],
           "use": [{"by": "a", "good": "gold", "weight": 1.0}, {"by": "a", "good": "timber", "weight": 0.5},
                   {"by": "a", "good": "iron", "weight": 1.0, "pull": 0.8}]}
    t = SP.parse(raw)
    assert t.pulls_of(t.lines["a"]) == {"gold": 0.5, "timber": 0.25, "iron": 0.8}
    assert t.pull_of(t.lines["a"]) == 0.8


# ---- world mode (PW-695) and portals (PW-697) ---------------------------------------------------
def _mode_raw(**meta):
    return {"meta": meta, "lineage": [
        {"id": "stem", "origin": "root", "at": "9 kyr", "real": True},
        {"id": "human", "parents": ["stem"], "at": "6 kyr", "real": True},
        {"id": "elf", "origin": "arrival", "at": "4 kyr"},
        {"id": "half", "origin": "hybrid", "exempt": True, "parents": ["human", "elf"], "at": "2 kyr"},
        {"id": "ork", "parents": ["stem"], "at": "5 kyr"}],
        "wish": [{"a": "human", "b": "elf", "want": "near"}],
        "use": [{"by": "human", "good": "mithril"}, {"by": "human", "good": "iron"}]}


def test_real_mode_keeps_only_the_marked_lines_and_no_fantasy_goods():
    fan = SP.parse(_mode_raw())
    assert fan.mode == "fantasy" and set(fan.lines) == {"stem", "human", "elf", "half", "ork"} and len(fan.uses) == 2
    real = SP.parse(_mode_raw(mode="real"))
    assert real.mode == "real" and set(real.lines) == {"stem", "human"} and not real.wishes
    assert [u.good for u in real.uses] == ["iron"]  # (mithril is a fantasy good)
    assert SP.parse(_mode_raw(), mode="real").mode == "real"  # (an override, as `planet lineages --mode real`)
    back = SP.parse(SP.to_raw(real))
    assert back.mode == "real" and set(back.lines) == {"stem", "human"}
    assert SP.parse(SP.to_raw(fan)).lines["human"].real
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "a", "origin": "root", "at": "1 kyr"}], "meta": {"mode": "real"}})  # no human marked
    with pytest.raises(ValueError):
        SP.parse(_mode_raw(mode="magic"))


def test_the_dnd_preset_has_a_human_real_mode():
    real = SP.load(LR.SAMPLES / "dnd.toml", "real")
    assert real.mode == "real" and set(real.lines) == {"archaic_human", "human"}  # (no groups, PW-1357)
    assert SP.load(LR.SAMPLES / "dnd.toml").mode == "fantasy"


def test_portal_settings_are_validated_and_round_trip():
    t = SP.parse(_mode_raw(portal_mode="sites", portals=3, portal_sites=["forest", "reef"]))
    assert (t.portal_mode, t.portals, t.portal_sites) == ("sites", 3, ["forest", "reef"])
    b = SP.parse(SP.to_raw(t))
    assert (b.portal_mode, b.portals, b.portal_sites) == ("sites", 3, ["forest", "reef"])
    assert SP.parse(_mode_raw()).portal_mode == "off"
    for bad in ({"portal_mode": "everywhere"}, {"portals": 0}, {"portal_sites": ["moon"]}):
        with pytest.raises(ValueError):
            SP.parse(_mode_raw(**bad))


def test_portals_are_placed_apart_on_land(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    for mode in ("random", "sites"):
        tree = SP.parse(_mode_raw(portal_mode=mode, portals=2))
        h = H.History(tree, ps, 1)
        pts = h.portal_cells()
        assert len(pts) == 2
        land = H._tags(h.grid, h.steps[-1].get())["land"]
        assert all(land[p["cell"]] for p in pts)
        d = np.arccos(np.clip(h.grid.centers[pts[0]["cell"]] @ h.grid.centers[pts[1]["cell"]], -1, 1)) * H.R_KM
        assert d >= H.PORTAL_SEP_KM
    assert H.History(SP.parse(_mode_raw()), ps, 1).portal_cells() == []  # (off: none)
    sites = H.History(SP.parse(_mode_raw(portal_mode="sites", portals=1, portal_sites=["forest"])), ps, 1).portal_cells()
    assert sites[0]["kind"] == "forest"


def test_recent_rain_is_a_full_climate_every_2_kyr(faketz):
    """PW-599 C: the rain comes from climate.compute at the time zoom's frames (2 kyr apart) in the window, linear
    in time between them; climate_every=0 keeps the keyframe's rain scaled with the warming."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=10, seed=3))
    tn, rn = ps._climate()
    assert tn.tolist() == [-10.0, -8.0, -6.0, -4.0, -2.0, 0.0] and rn.shape == (6, ps.grid.n)
    mid = ps.fields(-9.0, variability=False)["precipitation"]  # halfway between the -10 and -8 kyr climates
    assert np.allclose(mid, 0.5 * (rn[0] + rn[1]))
    assert np.allclose(ps.fields(-8.0, variability=False)["precipitation"], rn[1])
    old = R.Pass(faketz, 40.0, R.RecentParams(kyr=10, seed=3, climate_every=0))
    scaled = old.fields(-8.0, variability=False)["precipitation"]
    assert old._clim is None and not np.allclose(scaled, rn[1])  # (a different rain: the climate's own)


def test_recent_climates_are_kept_beside_the_time_zoom_and_never_read_stale(faketz):
    """PW-740: the full climates of the recent pass are written next to the time zoom, keyed by the zoom, window, spacing
    and model source: a second pass reads them back bit for bit, a changed window or spacing makes them again."""
    a = R.Pass(faketz, 40.0, R.RecentParams(kyr=10, seed=3))
    tn, rn = a._climate()
    f = a.tz_dir / "recent_rain.npz"
    assert f.exists()
    b = R.Pass(faketz, 40.0, R.RecentParams(kyr=10, seed=9))  # (the seed does not enter the climates)
    tn2, rn2 = b._climate()
    assert np.array_equal(tn, tn2) and np.array_equal(rn, rn2) and b.climate_s < 0.5 * max(a.climate_s, 1e-9) + 0.05
    c = R.Pass(faketz, 40.0, R.RecentParams(kyr=10, seed=3, climate_every=4.0))
    assert c._clim_read(c._clim_key()) is None and len(c._climate()[0]) < len(tn)
    f.write_bytes(b"not an npz")  # (an unreadable file is just a miss)
    assert R.Pass(faketz, 40.0, R.RecentParams(kyr=10, seed=3))._clim_read(a._clim_key()) is None


def test_land_goods_are_kept_on_disk_keyed_by_world_and_code(tmp_path, monkeypatch):
    """PW-740: land.goods writes its goods beside the worlds and reads them back identically; a changed world file or
    changed model source gives another key, so an old file is never read."""
    from planet.lineages import land as LD
    old = S.root()
    S.set_root(tmp_path)
    try:
        (tmp_path / "worlds").mkdir()
        w = tmp_path / "worlds" / "abc123.json"
        w.write_text('{\n"format": "x",\n"meta": {}\n}\n')
        out = {"fertile": np.linspace(0, 1, 7), "_raw": {"fertile": np.arange(7.0)}, "_peat": np.zeros(7), "_land": np.arange(7) > 2,
               "_made": ["resources"], "_missing": [], "_s": 1.5}
        k = LD._disk_key("abc123")
        assert LD._disk_read("abc123", k) is None
        LD._disk_write("abc123", k, out)
        back = LD._disk_read("abc123", k)
        assert np.array_equal(back["fertile"], out["fertile"]) and np.array_equal(back["_raw"]["fertile"], out["_raw"]["fertile"])
        assert back["_land"].dtype == bool and back["_made"] == ["resources"] and back["_missing"] == [] and back["_s"] == 1.5
        w.write_text('{\n"format": "y",\n"meta": {}\n}\n')  # (the world changed)
        k2 = LD._disk_key("abc123")
        assert k2 != k and LD._disk_read("abc123", k2) is None
        monkeypatch.setattr(LD, "code_hash", lambda scope: "another model")
        assert LD._disk_key("abc123") != k2
    finally:
        S.set_root(old)


def test_culinary_body_keys_validate_inherit_and_read_in_the_preset():
    """PW-726: suction, teeth, gut, salt, display, shed, hours, thermo and fire are validated, inherited key by key,
    spoken in the story notes and set in the preset where the D&D analogue is clear."""
    dnd = SP.load(LR.SAMPLES / "dnd.toml")
    b = lambda k: dnd.lines[k].body  # noqa: E731
    assert b("aarakocra")["suction"] == "none" and b("aarakocra")["teeth"] == "beak" and b("aarakocra")["thermo"] == "endo"
    assert b("dragonborn")["suction"] == "poor" and b("lizardfolk")["thermo"] == "ecto" and b("hill_giant")["gut"] == "foregut"
    assert b("tabaxi")["teeth"] == "conical" and b("triton")["fire"] is False and b("human")["fire"] is True and b("human")["gut"] == "simple"
    assert "cook without fire" in SP.body_notes(b("triton")) and "are ectotherms" in " ".join(SP.body_notes(b("lizardfolk")))
    assert SP.parse(SP.to_raw(dnd)).lines["triton"].body == b("triton")
    for bad in ({"suction": "strong"}, {"teeth": "tusks"}, {"gut": "four"}, {"display": "mane"}, {"shed": "yearly"}, {"fire": "yes"}, {"fire": 0.5}):
        with pytest.raises(ValueError):
            SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "body": bad}]})
    t = SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "body": {"display": "antlers", "shed": "males"}},
                              {"id": "y", "parents": ["x"], "at": "0.5 kyr", "body": {"shed": "both"}}]})
    assert t.lines["y"].body["display"] == "antlers" and t.lines["y"].body["shed"] == "both" and t.lines["y"].body["hours"] == "diurnal"


def test_brief_helpers():
    from planet.lineages import brief as BR
    assert BR._frost_months(5.0, 20.0) == 0.0 and BR._frost_months(-5.0, -1.0) == 12.0 and 3 < BR._frost_months(-10.0, 10.0) < 7
    assert BR._popcount(np.array([0, 0b101, 4095])).tolist() == [0, 2, 12]
    assert BR._shares(np.array([1, 1, 2, 3]), {1: "a", 2: "b"}, np.array([1, 1, 1, 0], bool)) == {"a": 0.667, "b": 0.333}
    assert abs(BR._gc(0, 0, 0, 90) - 3.14159265 / 2 * BR.R_KM) < 1


# ---- crops (PW-721), who tames by trait (PW-718) and fuels (PW-722) -------------------------------------------------
def test_crop_ranges_read_the_land_and_widen_for_growing():
    from planet.lineages import crop_defs as CD
    n = 5  # temperate plain, warm wet lowland, hot dry desert, cold tundra, cool highland
    env = {"temperature": np.array([12, 26, 30, -8, 8.0]), "precipitation": np.array([600, 2200, 60, 250, 900.0]),
           "tree_cover": np.array([10, 40, 0, 0, 20.0]), "elevation": np.array([100, 50, 100, 100, 2500.0]), "ice": np.zeros(n)}
    tags = {"wetland": np.array([0, 1, 0, 0, 0], bool), "volcanic": np.zeros(n, bool), "hills": np.zeros(n, bool)}
    land = np.ones(n, bool)
    wheat, rice, potato = (CD.BY_ID[k].wild(env, tags, land) for k in ("wheat", "rice", "potato"))
    assert wheat[0] > 0.9 and wheat[2] == 0 and wheat[3] == 0  # (open temperate ground; not desert or tundra)
    assert rice[1] > 0.5 and rice[0] == 0 and rice[2] == 0  # (warm wet flats only)
    assert potato[4] > 0.5 and potato[1] == 0  # (cool uplands, not the hot lowland)
    assert (CD.BY_ID["wheat"].wild(env, tags, land, widen=0.6) >= wheat).all()  # (grown past where it grew wild)
    assert (CD.BY_ID["wheat"].wild(env, tags, np.zeros(n, bool)) == 0).all()
    assert [a.id for a in CD.resolve(None, [], "fantasy")] == list(CD.REAL_IDS) and not any(a.fantasy for a in CD.resolve(None, ["emberpod"], "real"))
    assert "emberpod" in [a.id for a in CD.resolve(None, ["emberpod"], "fantasy")]
    raw = {"meta": {"crops": ["wheat"], "crops_force": ["emberpod"], "mode": "real"}, "lineage": [{"id": "a", "origin": "root", "at": "9 kyr", "real": True}]}
    assert SP.parse(raw).crops == ["wheat"] and SP.parse(raw).crops_force == []
    with pytest.raises(ValueError):
        SP.parse({**raw, "meta": {"crops": ["manna"]}})


def test_hunters_tame_dogs_not_whoever_lacks_a_farm_or_herd_use():
    from planet.lineages import landuse as LU
    raw = {"meta": {"name": "h", "seed": 1}, "lineage": [
        {"id": "plain", "origin": "root", "at": "30 kyr"},
        {"id": "hunt", "origin": "root", "at": "30 kyr", "traits": ["hunter"]},
        {"id": "farm", "origin": "root", "at": "30 kyr", "traits": ["agricultural"]}],
        "use": [{"by": "agricultural", "good": "fertile"}]}
    t = SP.parse(raw)
    assert LU.shares(t, t.lines["plain"])["forage"] == 0.0  # (no use of any food good: no longer counted a forager)
    assert LU.shares(t, t.lines["hunt"])["forage"] == 1.0 and LU.shares(t, t.lines["farm"])["forage"] == 0.0


def test_hunters_learn_crops_slower_and_meat_eaters_lean_to_herds():
    """PW-1373 B (owner 11-02): a people takes a crop up once it has stood on a fifth of its land for LAG_KYR / propensity (farmers
    at once, hunters ~10x slower); obligate carnivores lean to herds over crops through their propensities (not a ban)."""
    from planet.lineages import animals as AN, crops as CR
    lag = CR.learn_lag([1.0, 0.1, 0.0])
    assert lag[0] == pytest.approx(CR.LAG_KYR) and lag[1] == pytest.approx(10 * CR.LAG_KYR) and np.isinf(lag[2])
    t = SP.load(Path(SP.__file__).parent / "samples" / "dnd.toml")

    class _H:  # (just what Stock's propensity reads)
        def __init__(self, tree):
            self.tree, self.lines = tree, [l for l in tree.order()]
    h = _H(t)
    ids = [l.id for l in h.lines]
    st = AN.Stock.__new__(AN.Stock)
    from planet.lineages import crop_defs as CD, animal_defs as AD, landuse as LU
    sh = np.array([[LU.shares(t, l)[k] for k in ("farm", "herd", "forage", "gather")] if not l.overlay else [0.0] * 4 for l in h.lines])
    st.sh = {"farm": sh[:, 0], "herd": sh[:, 1], "forage": sh[:, 2], "gather": sh[:, 3]}
    prop = {}
    for a in (CD.BY_ID["wheat"], AD.BY_ID["caprine"]):
        st.a = a
        prop[a.id] = {i: st._propensity(l, k) for k, (i, l) in enumerate(zip(ids, h.lines))}
    assert t.lines["tabaxi"].body["diet"] == "obligate_carnivore"
    assert prop["caprine"]["tabaxi"] > 2 * prop["wheat"]["tabaxi"] > 0  # (the cat-folk lean to herds, and may still farm)
    assert prop["wheat"]["leonin"] > 0 and prop["caprine"]["leonin"] > 10 * prop["wheat"]["leonin"]
    assert prop["wheat"]["human"] > 0.9 and CR.learn_lag([prop["wheat"]["tabaxi"]])[0] >= 10 * CR.LAG_KYR - 1e-9


def test_crops_are_cultivated_by_farmers_add_capacity_and_leave_layers(faketz, monkeypatch):
    import dataclasses
    from planet.lineages import crop_defs as CD
    wild = lambda env, tags, land, widen=0.0: np.where(land & (np.abs(env["temperature"] - 12) < 8 + 6 * widen), 0.9, 0.0)  # noqa: E731
    wheat = dataclasses.replace(CD.BY_ID["wheat"], wild=wild)
    monkeypatch.setattr(CD, "TABLE", tuple(wheat if a.id == "wheat" else a for a in CD.TABLE))
    monkeypatch.setattr(CD, "BY_ID", {a.id: a for a in CD.TABLE})
    tree = _animal_tree(())
    tree.crops, tree.crops_at = ["wheat"], {"wheat": 12.0}
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h, res, pres = H.simulate(tree, ps, tries=1)
    st = pres["crops"]["stocks"]["wheat"]
    assert st["tamed"] and st["tamed"][0]["line"] == "farm" and st["tamed"][0]["first"] and st["known_mkm2"] > 0 and st["grown_mkm2"] > 0
    assert st["adoption"]["farm"] > st["adoption"].get("herd", 0.0) and st["propensity"]["farm"] > st["propensity"]["herd"]
    know = h.crops.know()
    assert know.max() > 0.5 and know.max() <= 1.0 and np.all(np.asarray(h.crops.k_mult(h.idx["herd"])) >= 1.0)
    out = O.save(h, res, pres, name="crop test")
    run = json.loads((out / "run.json").read_text())
    assert {"crop_wild", "crop_known"} <= run["layers"].keys() and run["layers"]["crop_known"]["dtype"] == "uint64"
    assert any(e["kind"] == "crops" for e in h.events) and "first to cultivate wheat and barley" in run["meta"]["lineages"][h.idx["farm"]]["story"]
    assert "Crops (PW-721)" in (out / "run.txt").read_text()
    rt = np.fromfile(out / "layers" / "route_wheat.bin", np.uint8)  # how each cell came to know wheat (PW-742)
    assert set(np.unique(rt).tolist()) <= {0, 1, 2, 3} and (rt == 1).any() and (rt > 0).sum() == int((h.crops.stocks[0].rd >= H.EST).sum())
    assert st["route_file"] == "layers/route_wheat.bin"


def test_fuels_follow_trees_herds_peat_crops_and_coast():
    from planet.lineages import fuels as FU
    # forest, steppe herd country, bog, grain plain, treeless coast, dense town in woods; coal outcrop
    z = np.zeros(6)
    sh = FU.mix(tc=np.array([0.9, 0.02, 0.05, 0.1, 0.0, 0.7]), pasture=np.array([0, 0.5, 0.0, 0.1, 0.0, 0.0]), crop=np.array([0, 0, 0, 0.6, 0.0, 0.2]),
                dens=np.array([2, 2, 2, 5, 2, 40.0]), herd_known=np.array([0, 1, 1, 1, 1, 1.0]), peat_m=np.array([0, 0, 2.0, 0, 0, 0.0]),
                straw_mix=np.full(6, 0.9), graze=np.array([0.1, 0.8, 0.2, 0.3, 0.1, 0.1]), coast=np.array([0, 0, 0, 0, 1, 0], bool), coal=z)
    lead = [FU.FUELS[int(np.argmax([sh[k][i] for k in FU.FUELS]))] for i in range(6)]
    assert lead[:5] == ["wood", "dung", "peat", "straw", "drift"], lead
    assert all(abs(sum(sh[k][i] for k in FU.FUELS) - 1) < 1e-9 for i in range(6)) and sh["charcoal"][5] > sh["charcoal"][0] >= 0  # (towns burn charcoal)
    nobody = FU.mix(z, z, z, z, z, z, z, z, z.astype(bool), z)
    assert all(nobody[k].sum() == 0 for k in FU.FUELS)  # (no people, no fuel)
    c = FU.mix(tc=np.array([0.1]), pasture=np.zeros(1), crop=np.zeros(1), dens=np.array([3.0]), herd_known=np.zeros(1), peat_m=np.zeros(1),
               straw_mix=np.zeros(1), graze=np.zeros(1), coast=np.zeros(1, bool), coal=np.array([0.9]))
    assert c["coal"][0] > c["wood"][0]
    assert FU.sentence([("dung", 0.7), ("wood", 0.2)]) == "It cooks mostly over dung fires."
    assert FU.sentence([("wood", 0.45), ("peat", 0.3), ("dung", 0.1)]) == "It cooks over wood fires and peat fires."


def test_fuels_coal_by_era_heath_in_the_cold_and_fat_where_nothing_else():
    from planet.lineages import fuels as FU
    one = np.ones(1)
    z = np.zeros(1)
    kw = dict(tc=np.array([0.0]), pasture=z, crop=z, dens=np.array([3.0]), herd_known=z, peat_m=z, straw_mix=z, graze=np.array([0.9]),
              coast=np.zeros(1, bool), coal=np.array([0.9]))
    assert FU.mix(**kw, coal_known=FU.COAL_ERA["stone age"])["coal"][0] == 0 < FU.mix(**kw, coal_known=FU.COAL_ERA["medieval"])["coal"][0]
    assert FU.COAL_ERA["classical"] < FU.COAL_ERA["medieval"] < FU.COAL_ERA["renaissance"] == 1.0
    kw["coal"] = z
    warm, cold = FU.mix(**kw, temp=np.array([15.0])), FU.mix(**kw, temp=np.array([-8.0]))
    assert warm["heath"][0] == 0 < cold["heath"][0] and cold["grass"][0] == 0 < warm["grass"][0]  # (tundra grass is heath)
    coast = FU.mix(**{**kw, "coast": np.ones(1, bool)}, sea=one)
    assert coast["oil"][0] > 0 and FU.mix(**kw, sea=one)["oil"][0] == 0  # (oil only on a coast with sea mammals)
    treeless = FU.mix(**{**kw, "herd_known": one}, temp=np.array([20.0]))
    woods = FU.mix(**{**kw, "tc": 0.9 * one, "herd_known": one}, temp=np.array([20.0]))
    assert treeless["tallow"][0] > woods["tallow"][0] >= 0 and treeless["bone"][0] > woods["bone"][0]  # (fat fills in where wood is scarce)
    for sh in (warm, cold, coast, treeless, woods):
        assert abs(sum(sh[k][0] for k in FU.FUELS) - 1) < 1e-9


def _toy_world():
    """A level-3 grid with a continent (north of 5 N, 0..150 E) and a one-cell island, for the salt and sea-food goods."""
    from planet.geo import world_land
    from planet.grid import shared_grid
    g = shared_grid(3)
    lat, lon = g.lat, g.lon
    elev = np.where((lat > 5) & (lon > 0) & (lon < 150), 300.0, -2000.0)
    isl = int(np.argmin(np.where((elev < 0) & (lat < -40), np.abs(lon), 1e9)))
    elev[isl] = 100.0
    L = {"elevation": elev, "ice": np.zeros(g.n)}
    return g, L, world_land(L), isl


def _getter(L, n):
    return lambda k: np.asarray(L[k], float) if k in L else np.zeros(n)


def test_salt_distance_and_sources_and_sea_food():
    from planet.lineages import seafood as SF
    g, L, land, isl = _toy_world()
    n = g.n
    sea = ~land
    coast = land & nbr_reduce(g, np.logical_or, sea[g.nbr_idx])
    inland = land & ~coast & ~nbr_reduce(g, np.logical_or, coast[g.nbr_idx])
    pit = int(np.flatnonzero(inland)[0])
    L["res_salt"] = np.zeros(n)
    L["res_salt"][pit] = 0.9
    L["salinity"] = np.where(sea, 35.0, 0.0)
    L["precipitation"] = np.full(n, 1000.0)
    L["pet"] = np.full(n, 500.0)
    L["coast_type"] = np.where(coast, 10, 0)
    L["sst_jul"] = L["sst_jan"] = np.where(sea, 10.0, 0.0)
    out = SF.salt(g, L, land, coast, _getter(L, n))
    km = out["_salt_km"]
    assert km[pit] == 0 and out["_salt_kind"][pit] == 1  # (rock salt where it is)
    assert km[isl] == 0 and out["_salt_kind"][isl] == 4  # (the island is its own coast: sea salt)
    far = int(np.argmax(np.where(land & ~coast, km, -1)))  # (the interior cell farthest from a source)
    assert 0 < km[far] < SF.SALT_UNREACHED
    assert (km[land] >= 0).all() and (out["salt"] >= 0).all() and (out["salt"] <= 1).all()
    # a dry coast makes solar-pan salt, a damp one only the dearer boiled salt; a brackish sea makes none
    Ld = {**L, "pet": np.full(n, 3000.0)}
    dry = SF.salt(g, Ld, land, coast, _getter(Ld, n))
    assert dry["salt_sea"][coast].max() > out["salt_sea"][coast].max() > 0
    Lb = {**L, "salinity": np.where(sea, 5.0, 0.0)}
    assert SF.salt(g, Lb, land, coast, _getter(Lb, n))["salt_sea"].max() == 0
    # sea food: cold upwelling coasts beat warm still ones
    L2 = {**L, "upwelling": np.where(sea, 3.0, 0.0), "sst_jul": np.where(sea, 8.0, 0.0), "sst_jan": np.where(sea, 6.0, 0.0),
          "tide_range": np.where(sea, 1.5, 0.0), "seals": np.where(coast, 0.5, 0.0)}
    rich = SF.seafood(g, L2, land, coast, _getter(L2, n))
    L3 = {**L, "sst_jul": np.where(sea, 28.0, 0.0), "sst_jan": np.where(sea, 26.0, 0.0)}
    poor = SF.seafood(g, L3, land, coast, _getter(L3, n))
    assert rich["fish_sea"][coast].mean() > poor["fish_sea"][coast].mean() >= 0
    assert rich["sea_mammals"][coast].mean() > poor["sea_mammals"][coast].mean()  # (seals and whales on the cold coast)
    for k in ("fish", "shellfish", "sea_mammals"):
        assert (rich[k] >= 0).all() and (rich[k] <= 1).all()


def test_salt_playa_lick_and_basin_brine():
    """PW-746: a closed dry basin makes a playa, a river over shale a lick, a spring over a sediment basin a brine."""
    from planet.lineages import seafood as SF
    g, L, land, isl = _toy_world()
    n = g.n
    sea = ~land
    coast = land & nbr_reduce(g, np.logical_or, sea[g.nbr_idx])
    inland = np.flatnonzero(land & ~coast & ~nbr_reduce(g, np.logical_or, coast[g.nbr_idx]))
    a, b, c = int(inland[0]), int(inland[len(inland) // 2]), int(inland[-1])
    L["salinity"] = np.where(sea, 35.0, 0.0)
    L["precipitation"] = np.full(n, 1000.0)
    L["pet"] = np.full(n, 500.0)
    L["coast_type"] = np.where(coast, 10, 0)
    L["sst_jul"] = L["sst_jan"] = np.where(sea, 10.0, 0.0)
    L["downstream"] = np.full(n, 0)
    L["downstream"][a] = -1  # (a drainage ends here)
    L["pet"] = np.where(np.arange(n) == a, 3000.0, 500.0)
    L["surface_rock"] = np.zeros(n)
    L["surface_rock"][b] = 8
    L["flow"] = np.zeros(n)
    L["flow"][b] = 5.0
    L["spring"] = np.zeros(n)
    L["spring"][c] = 1
    L["surface_rock"][c] = 8
    L["sediment_cover"] = np.full(n, 2.0)
    out = SF.salt(g, L, land, coast, _getter(L, n))
    assert out["salt_lake"][a] > 0.9 and out["_salt_km"][a] == 0
    assert out["salt_lick"][b] == SF.LICK and out["salt_spring"][c] >= 0.5


def test_ways_of_life_set_the_uses_a_people_reads():
    """PW-723: a way replaces the food rows its traits give (not harbours or place rows), inherits down the tree, and
    sets the shares that decide who tames, cultivates and herds."""
    from planet.lineages import landuse as LU
    t = SP.load(LR.tree_path("dnd"))
    assert t.lines["hill_giant"].way == "pastoral_nomad" and t.lines["halfling"].way == "farmer"
    assert t.lines["archaic_human"].way == "forager"
    assert LU.shares(t, t.lines["hill_giant"])["herd"] == 1
    assert LU.shares(t, t.lines["archaic_human"])["forage"] == 1
    assert dict(t.uses_of(t.lines["human"])).get("harbour", 0) > 0  # (seafaring's harbour row stays under the farmer way)
    raw = SP.to_raw(t)
    assert {r["id"]: r.get("way") for r in raw["lineage"]}["hill_giant"] == "pastoral_nomad"
    bad = [{**r, "way": "bard"} if r["id"] == "human" else r for r in raw["lineage"]]
    with pytest.raises(ValueError):
        SP.parse({**raw, "lineage": bad})


# ---- contacts, interfertility tiers, substrate and clines (PW-727) --------------------------------------------------
def test_interfertility_tiers_come_from_split_depth_with_overrides():
    raw = {"meta": {"name": "t", "seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "30 Myr"},
        {"id": "a", "parents": ["stem"], "at": "500 kyr"}, {"id": "b", "parents": ["stem"], "at": "200 kyr"},
        {"id": "c", "parents": ["stem"], "at": "20 Myr"}, {"id": "a2", "parents": ["a"], "at": "5 kyr"},
        {"id": "d", "parents": ["stem"], "at": "2.5 Myr"},
        {"id": "fey", "origin": "arrival", "at": "10 kyr", "place": [0, 120]},
        {"id": "half", "origin": "hybrid", "parents": ["a", "fey"], "at": "8 kyr"},
        {"id": "far", "origin": "root", "at": "30 Myr"}],
        "interfertile": [{"a": "a", "b": "c", "tier": 1}]}
    t = SP.parse(raw)
    assert t.split_kyr("a", "b") == 500 and t.tier_of("a", "b") == 1 and t.tier_of("b", "a") == 1
    assert t.tier_of("a", "a2") == 0 and t.tier_of("a", "c") == 1  # (the override beats the 20 Myr split)
    assert t.tier_of("b", "d") == 2 and t.tier_of("a2", "b") == 1  # (2.5 Myr: mostly sterile, PW-851)
    assert t.tier_of("b", "c") == 3 and t.tier_of("d", "c") == 3  # (20 Myr: no young; it was T2 under the old 40 Myr limit)
    assert t.tier_of("a", "fey") == 3 and t.tier_of("stem", "far") == 3  # (an arrival from outside, another root)
    assert t.tier_of("half", "a") == 0 and t.tier_of("half", "b") == 1  # (an overlay is interfertile with its hosts)
    assert SP.parse(SP.to_raw(t)).tiers == t.tiers
    raw["meta"]["tier_kyr"] = ["1 kyr", "100 kyr", "5 Myr"]
    assert SP.parse(raw).tier_of("a", "b") == 2
    with pytest.raises(ValueError):
        SP.parse({**raw, "interfertile": [{"a": "a", "b": "nope", "tier": 1}]})


def test_hybrid_fertility_follows_divergence_times():
    """PW-851: fertile out to ~1-2 Myr of divergence, mostly sterile to ~4 Myr, none beyond; from the lineages' own dates."""
    f = SP.fertility_at
    assert f(0) == f(500) == f(1000) == 1.0  # (T0, T1: fertile)
    assert 0.1 < f(1200) <= 0.2 and 0.02 < f(2500) < 0.1 and f(3999) < 0.03  # (mostly sterile, falling)
    assert f(1200) > f(2000) > f(3000) > f(3999) > 0 and f(4000) == f(20000) == 0.0
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr"},
        {"id": "a", "parents": ["stem"], "at": "500 kyr"}, {"id": "b", "parents": ["stem"], "at": "2.5 Myr"},
        {"id": "c", "parents": ["stem"], "at": "8 Myr"}, {"id": "fey", "origin": "arrival", "at": "20 kyr"}],
        "interfertile": [{"a": "a", "b": "c", "tier": 1}]}
    t = SP.parse(raw)
    assert t.fertility("a", "a") == 1.0 and t.fertility("a", "stem") == 1.0
    assert 0 < t.fertility("a", "b") < 0.1 and t.fertility("b", "c") == 0.0  # (2.5 and 8 Myr)
    assert t.fertility("a", "c") == 1.0 and t.fertility("a", "fey") == 0.0  # (an override; no common ancestor: no young, PW-752)


def test_interfertility_stages_follow_realistic_genetics_with_the_genre_exemption(faketz):
    """PW-752 (owner 10-29): by split depth a pair's young are viable, absorbed into a parent people, sterile, or impossible; a declared hybrid
    exists only where that allows it, unless it is `exempt` (half-elves, half-orcs); [[interfertile]] rows set a stage by name."""
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr"},
        {"id": "a", "parents": ["stem"], "at": "500 kyr"}, {"id": "b", "parents": ["stem"], "at": "2.5 Myr"},
        {"id": "a2", "parents": ["a"], "at": "6 kyr"}, {"id": "c", "parents": ["stem"], "at": "8 Myr"},
        {"id": "fey", "origin": "arrival", "at": "20 kyr"}, {"id": "fey2", "parents": ["fey"], "at": "12 kyr"},
        {"id": "viable", "origin": "hybrid", "parents": ["a", "a2"], "at": "5 kyr"},
        {"id": "absorbed", "origin": "hybrid", "parents": ["a", "stem"], "at": "5 kyr"},
        {"id": "sterile", "origin": "hybrid", "parents": ["a", "b"], "at": "5 kyr"},
        {"id": "sterile_own", "origin": "hybrid", "parents": ["a", "b"], "at": "5 kyr", "contact": False},
        {"id": "none", "origin": "hybrid", "parents": ["a", "fey"], "at": "5 kyr"},
        {"id": "genre", "origin": "hybrid", "parents": ["a", "fey"], "at": "5 kyr", "exempt": True}],
        "interfertile": [{"a": "b", "b": "c", "stage": "absorbed"}]}
    t = SP.parse(raw)
    assert [t.stage_of(*p) for p in (("a", "a2"), ("a", "stem"), ("a", "b"), ("a", "c"), ("a", "fey"))] == [*SP.STAGES, "impossible"]
    assert t.stage_of("b", "c") == "absorbed" and t.tier_of("b", "c") == 1  # (a row by stage name)
    assert t.split_kyr("fey", "fey2") == 12 and t.stage_of("fey", "fey2") == "absorbed"  # (an arrival's own split child is its kin)
    hf = {k: t.hybrid_factor(t.lines[k]) for k in ("viable", "absorbed", "sterile", "sterile_own", "none", "genre")}
    assert hf["viable"] == (1.0, True) and hf["genre"] == (1.0, True)
    assert hf["absorbed"] == (0.0, False) and hf["none"] == (0.0, False) and hf["sterile_own"] == (0.0, False)
    assert 0 < hf["sterile"][0] < 0.1 and hf["sterile"][1] is False  # (born where the parents meet, mostly sterile, never a people)
    r2 = SP.to_raw(t)
    assert next(x for x in r2["lineage"] if x["id"] == "genre")["exempt"] is True and SP.parse(r2).tiers == t.tiers
    with pytest.raises(ValueError):
        SP.parse({**raw, "interfertile": [{"a": "b", "b": "c", "stage": "kin"}]})
    # in a run: the absorbed and impossible hybrids are never born (an event says why, and they are lost); the exempt one is
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw2 = {"meta": {"seed": 1}, "lineage": [
        {"id": "a", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "b", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "none", "origin": "hybrid", "parents": ["a", "b"], "at": "20 kyr"},
        {"id": "genre", "origin": "hybrid", "parents": ["a", "b"], "at": "20 kyr", "exempt": True}]}
    tree2 = SP.parse(raw2)
    h = H.History(tree2, ps, 1)
    g = h.grid
    h.run()  # (sets up the run's state; the parents may never meet on this coarse grid, so they are made to meet below)
    h.p[:] = 0.0
    h.started = {"a": 30.0, "b": 30.0}
    h.active = {"a": True, "b": True, "none": False, "genre": False}
    h.events, h.origins, h._unborn = [], {}, set()
    step = h.steps[-1]
    env = step.get()
    land = env["land"]
    cell = int(np.argmax(land & (np.abs(g.lon) < 20) & (np.abs(g.lat) < 20)))
    zone = H.rings(cell, land, 1, g.nbr_off, g.nbr_idx)
    h.p[h.idx["a"]][zone] = h.p[h.idx["b"]][zone] = 0.6
    h._start_due(step, env, H._tags(g, env), {})
    assert "genre" in h.origins and (h.p[h.idx["genre"]][zone] >= H.EST).all()
    assert "none" not in h.origins and not h.p[h.idx["none"]].any()
    assert [e for e in h.events if e["kind"] == "unborn" and e["line"] == "none" and "impossible" in e["text"]]
    h._hybrid(tree2.lines["none"], h.idx["none"], np.where(land, 0.9, 0.0), step)
    assert not h.p[h.idx["none"]].any()


def test_dnd_half_elves_and_half_orcs_are_the_only_mixed_peoples_and_always_possible():
    """PW-752: the shared preset tracks no minor mixed peoples; half-elves (no common ancestor with humans: impossible by descent) and
    half-orcs (700 kyr: absorbed by descent) are its genre exemptions, and elves and drow are kin."""
    for name in ("dnd", "seven_meals"):
        t = LR.load_tree(name)
        hy = {l.id for l in t.lines.values() if l.origin == "hybrid"}
        assert hy == {"half_elf", "half_orc"}, (name, hy)
        assert all(t.lines[x].exempt and t.hybrid_factor(t.lines[x])[0] == 1.0 for x in hy)
        assert t.stage_of("human", "elf") == "impossible" and t.stage_of("human", "orc") == "absorbed"
    t = LR.load_tree("dnd")
    assert t.stage_of("elf", "drow") == "absorbed" and t.stage_of("lizardfolk", "troglodyte") == "sterile"


def test_a_contact_hybrid_of_distant_parents_is_a_thinner_share(faketz):
    """PW-851: the hybrid's share of its hosts' people scales with its parents' fertility, so the same cell holds fewer hybrids of a
    mostly sterile pair than of a fertile one (PW-752: the fertile pair's, absorbed by descent, made exempt here)."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "a", "parents": ["stem"], "at": "500 kyr"}, {"id": "b", "parents": ["stem"], "at": "600 kyr"},
        {"id": "far", "parents": ["stem"], "at": "2.5 Myr"},
        {"id": "ab", "origin": "hybrid", "exempt": True, "parents": ["a", "b"], "at": "20 kyr", "share": 0.2},
        {"id": "afar", "origin": "hybrid", "parents": ["a", "far"], "at": "20 kyr", "share": 0.2}]}
    h = H.History(SP.parse(raw), ps, 1)
    P = np.zeros((len(h.lines), h.grid.n))
    h._linger = np.zeros(P.shape, bool)
    for q in ("a", "b", "far"):
        P[h.idx[q]] = 0.8
    P[h.idx["ab"]] = 0.5
    P[h.idx["afar"]] = 0.5
    full, thin = h.population(h.idx["ab"], P), h.population(h.idx["afar"], P)
    assert full.sum() > 0 and thin.sum() > 0 and thin.sum() < 0.2 * full.sum()


def test_contacts_record_borders_tiers_and_substrate_and_clines_carry_a_share(faketz):
    from planet.lineages import contacts as CT
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "a", "parents": ["stem"], "at": "25 kyr"}, {"id": "b", "parents": ["stem"], "at": "20 kyr"}]}
    tree = SP.parse(raw)
    h = H.History(tree, ps, 1)
    g = h.grid
    land = ps.fields(0.0, variability=False)["land"]
    ia, ib = h.idx["a"], h.idx["b"]
    west, east = land & (g.lon < 0) & (np.abs(g.lat) < 40), land & (g.lon >= 0) & (np.abs(g.lat) < 40)
    ct = CT.Contacts(h)
    n = len(h.lines)
    tags = {"coast": np.zeros(g.n, bool), "open": np.ones(g.n, bool)}
    corr = np.full(g.n, 0.5)

    def frame(ago, Pw):
        ct.update(Pw, H.Step(ago, 1.0, "recent", True, None), tags, corr, land)

    P = np.zeros((n, g.n))
    P[ia][west | east] = 0.8  # a holds both sides, b nowhere: no contact, and nobody to take over from
    frame(10.0, P)
    P[ib][east] = 0.8
    P[ia][east] = 0.0
    frame(6.0, P)  # b takes the east from a, the two now share a border
    P[ia][west] = 0.0
    frame(0.0, P)  # a leaves the west (no one else there)
    sm = ct.summary()
    (pair,) = sm["pairs"]
    assert {pair["a"], pair["b"]} == {"a", "b"} and pair["tier"] == "T1" and pair["first_contact_kyr"] == 6.0
    assert pair["years_in_contact"] == 5000 and pair["in_contact_now"] is False and pair["border_km_peak"] > 0
    held = sm["substrate"]["b"]["held_before"]
    assert held and held[0]["id"] == "a" and held[0]["held_until_kyr"] == 6.0
    # a cline: a trait one people has runs into the next people's country, away from the border, not in a far people
    lead = np.where(west, ia, np.where(east, ib, 255)).astype(np.uint8)
    body = np.where(west, 100, 0).astype(np.uint8)
    comp = {"body_milk": body.copy()}
    assert CT.cline(h, comp, lead, land) > 0
    out = comp["body_milk"]
    assert out[west].mean() < 100 and 0 < out[east].mean() < 50 and out[east].max() > 0
    assert (out[~(west | east)] == 0).all()
    far = SP.parse({"lineage": [{"id": "a", "origin": "root", "at": "1 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                                {"id": "b", "origin": "root", "at": "1 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}]})
    h2 = H.History(far, ps, 1)
    comp2 = {"body_milk": body.copy()}
    assert CT.cline(h2, comp2, lead, land) == 0 and (comp2["body_milk"] == body).all()  # (a distant tier pushes no share across)


def test_sparse_smooth_equals_the_full_neighbour_mean(faketz):
    """PW-743: _smooth sums only the cells next to a held cell; the result is the full neighbour mean to the last bit."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse({"meta": {"seed": 1}, "lineage": [{"id": "a", "origin": "root", "at": "10 kyr"}]}), ps, 1)
    g = h.grid
    rng = np.random.default_rng(3)
    for frac in (0.0, 0.002, 0.05, 0.4):
        x = np.where(rng.random(g.n) < frac, rng.random(g.n), 0.0)
        full = np.maximum(x, nbr_reduce(g, np.add, x[g.nbr_idx]) / np.diff(g.nbr_off))
        assert np.array_equal(h._smooth(x), full)


# ---- reputation and exonyms (PW-731) -----------------------------------------------------------------------------------
from planet.lineages import reputation as RP  # noqa: E402


def _rep_tree(efold=None):
    devil = {"id": "devil", "label": "devils", "body": {"display": "horns"}, "valence": ["feared", "despised"]}
    if efold:
        devil["efold_kyr"] = efold
    return SP.parse({"meta": {"name": "t", "seed": 1}, "lineage": [
        {"id": "farmers", "origin": "root", "at": "1 Myr"}, {"id": "hunters", "origin": "root", "at": "1 Myr"},
        {"id": "herders", "origin": "root", "at": "1 Myr", "body": {"display": "horns"}},
        {"id": "sailors", "origin": "root", "at": "1 Myr", "traits": ["swims"]},
        {"id": "reavers", "origin": "root", "at": "1 Myr", "traits": ["swims"]}],
        "exonym": [devil, {"id": "sea", "label": "sea elves", "traits": ["swims"], "valence": ["exotic", "edge"]},
                   {"id": "raiders", "label": "raiders", "valence": ["feared"]},
                   {"id": "lesser", "label": "lesser folk", "valence": ["despised"]},
                   {"id": "far", "label": "the far folk", "valence": ["edge"]}]})


def _pair(a, b, years, km=400, mixed=0.0, first=20.0, now=True):
    return {"a": a, "b": b, "tier": "T3", "split_kyr": None, "first_contact_kyr": first, "years_in_contact": years, "in_contact_now": now,
            "border_km_now": km, "border_km_peak": km, "mixed_pct_now": mixed, "kind": "coast", "series": []}


def _contacts(took_kyr=1.0):
    sub = {"farmers": {"cells": 700, "first_here_share": 1.0, "held_before": []},
           "hunters": {"cells": 500, "first_here_share": 1.0, "held_before": []},
           "sailors": {"cells": 100, "first_here_share": 1.0, "held_before": []},
           "reavers": {"cells": 100, "first_here_share": 1.0, "held_before": []},
           "herders": {"cells": 900, "first_here_share": 0.7, "held_before": [{"id": "farmers", "cells": 300, "share": 0.3, "held_until_kyr": took_kyr}]}}
    return {"pairs": [_pair("farmers", "herders", 30000, mixed=5.0), _pair("farmers", "hunters", 90000, mixed=10.0),
                      _pair("farmers", "sailors", 800, km=60), _pair("farmers", "reavers", 900, km=60),
                      _pair("hunters", "sailors", 1000, km=60, now=True)], "substrate": sub, "tier_kyr": [10, 1000, 40000]}


def test_reputation_is_set_by_conquest_contact_and_body_not_by_what_a_people_is():
    r = RP.build(_rep_tree(), _contacts())["rows"]
    f = r["farmers"]
    assert f["herders"]["valence"] == "feared" and f["herders"]["name"] == "devils" and f["herders"]["category"] == "devil"
    assert f["herders"]["strength"] > 0.5 and "took 300 cells" in f["herders"]["basis"]
    assert r["herders"]["farmers"]["valence"] == "despised" and r["herders"]["farmers"]["name"] == "lesser folk"  # the conqueror's view; no horns on the farmers
    assert f["hunters"]["valence"] == "neighbour" and f["hunters"]["name"] == "hunters" and f["hunters"]["category"] is None  # rich peaceful contact: its own name
    # thin contact: the body picks the name (swimmers: sea elves), and two such peoples are lumped under it
    assert f["sailors"]["valence"] == "edge" and f["sailors"]["name"] == "sea elves" and f["sailors"]["lumped_with"] == ["reavers"]
    assert "devils" in f["herders"]["text"]


def test_conquest_memory_fades_unless_the_legend_row_keeps_it_longer():
    old = RP.build(_rep_tree(), _contacts(took_kyr=12.0))["rows"]["farmers"]["herders"]
    assert old["valence"] == "neighbour"  # 12 kyr at an e-folding of 2.4 kyr: gone, the pair reads by its contact
    kept = RP.build(_rep_tree(efold=20.0), _contacts(took_kyr=12.0))["rows"]["farmers"]["herders"]
    assert kept["valence"] == "feared" and kept["name"] == "devils" and 0.05 < kept["strength"] < 0.6
    assert kept["memory_kyr"] == 20.0 and "memory_kyr" not in RP.build(_rep_tree(), _contacts())["rows"]["farmers"]["herders"]  # (PW-754: only a legend row says so)
    ordinary = RP.build(_rep_tree(), _contacts(took_kyr=1.0))["rows"]["farmers"]["sailors"]
    assert "memory_kyr" not in ordinary  # rows without their own memory length behave as before
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr"}], "exonym": [{"id": "q", "efold_kyr": 0}]})


def test_a_people_that_never_met_borrows_its_best_connected_neighbours_view():
    c = _contacts()
    c["pairs"].append(_pair("hunters", "reavers", 40000, mixed=5.0))
    r = RP.build(_rep_tree(), c)["rows"]
    # the reavers never met the herders; their best-connected neighbour (the hunters) did not either, so nothing is borrowed there,
    # but the hunters, who never met the herders, borrow the farmers' view (their best-connected neighbour: 90000 yr) at half strength
    b = r["hunters"]["herders"]
    assert b["borrowed_from"] == "farmers" and b["valence"] == "feared" and b["strength"] == round(r["farmers"]["herders"]["strength"] / 2, 3)
    assert "herders" not in r["reavers"]


def test_exonym_rows_are_validated_and_survive_the_round_trip():
    t = _rep_tree()
    assert SP.parse(SP.to_raw(t)).exonyms == t.exonyms
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr"}], "exonym": [{"id": "q", "body": {"display": "wings"}}]})
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr"}], "exonym": [{"id": "q", "valence": ["scorned"]}]})
    assert SP.load(LR.SAMPLES / "dnd.toml").exonyms  # the preset ships the generic folk table


def test_an_authored_conquest_event_is_remembered_by_the_overrun_under_the_legend_row():
    """PW-730: `[[event]] kind = conquest` is read by the reputation pass; the legend row's memory length keeps it."""
    raw = SP.to_raw(_rep_tree(efold=20.0))
    raw["event"] = [{"kind": "conquest", "by": "herders", "over": ["hunters"], "at": "12 kyr", "note": "x"}]
    t = SP.parse(raw)
    assert t.events == [{"kind": "conquest", "by": "herders", "over": ["hunters"], "at": 12.0, "strength": RP.EVENT_STRENGTH, "note": "x"}]
    assert SP.parse(SP.to_raw(t)).events == t.events
    c = _contacts(took_kyr=1.0)
    c["pairs"].append(_pair("herders", "hunters", 40000, mixed=2.0))
    r = RP.build(t, c)["rows"]["hunters"]["herders"]
    assert r["valence"] == "feared" and r["name"] == "devils" and r["memory_kyr"] == 20.0 and "authored" in r["basis"]
    assert 0.3 < r["strength"] < RP.EVENT_STRENGTH  # (0.8 x exp(-12 / 20))
    plain = SP.parse({**raw, "event": [], "exonym": [e for e in raw["exonym"] if "efold_kyr" not in e]})  # no legend row: 12 kyr is gone
    assert RP.build(plain, c)["rows"]["hunters"]["herders"]["valence"] != "feared"
    for bad in ({"kind": "raid", "by": "herders", "over": "hunters", "at": "1 kyr"}, {"by": "herders", "over": "nobody", "at": "1 kyr"},
                {"by": "herders", "over": "hunters", "at": "1 kyr", "until": "0.5 kyr"},
                {"kind": "polity", "by": "herders", "over": "hunters", "at": "1 kyr", "until": "2 kyr"},
                {"by": "herders", "over": "hunters"}, {"by": "herders", "over": "hunters", "at": "1 kyr", "from": "the steppe"},
                {"by": "herders", "over": "hunters", "at": "1 kyr", "strength": 0}):
        with pytest.raises(ValueError):
            SP.parse({**raw, "event": [bad]})


# ---- the owner's world preset (PW-730) ----------------------------------------------------------------------------------
def test_seven_meals_tiers_follow_the_culinary_repos_tree_and_the_ruminant_peoples_are_a_deep_branch():
    t = SP.load(LR.SAMPLES / "seven_meals.toml")
    tier = lambda a, b: t.tier_of(a, b)  # noqa: E731
    # genetics.md's tier table falls out of the split depths
    for a, b in (("human", "orc"), ("human", "goliath"), ("leonin", "tabaxi"), ("goblin", "hobgoblin"), ("hill_giant", "storm_giant")):
        assert tier(a, b) == 1, (a, b)
    for a, b in (("human", "dwarf"), ("dwarf", "halfling"), ("human", "halfling"), ("goblin", "bugbear"),
                 ("dragonborn", "kobold"), ("merfolk", "deep_folk"), ("human", "hill_giant")):
        assert tier(a, b) == 2, (a, b)
    # dragons are a deep reptile line (PW-855): the lizardfolk and tortles split from them in the dinosaur era, so they are no kin of the
    # dragon-blooded peoples any more; dragonborn and kobolds are kin of the dragons (split off recently) and of each other (T2)
    for a, b in (("human", "leonin"), ("human", "lizardfolk"), ("elf", "gnome"), ("human", "elf"), ("tortle", "dragonborn"), ("human", "aarakocra"),
                 ("lizardfolk", "dragonborn"), ("lizardfolk", "kobold"), ("lizardfolk", "draconic")):
        assert tier(a, b) == 3, (a, b)
    assert tier("draconic", "dragonborn") == 2 and tier("draconic", "kobold") == 2
    assert not t.lines["draconic"].persists and t.lines["draconic"].ago_kyr >= 10_000  # (the ur-dragon: near the root, ~19.5 Myr; it ends at its last split, PW-924)
    assert tier("arha", "anja") == 0 and tier("lizard_desert", "lizard_delta") == 0 and tier("aarakocra", "kenku") == 0
    # goliaths are sisters of the humans, not giant-kin
    assert "giant" not in t.ancestors("goliath") and t.lines["goliath"].parents == ["human_line"]
    # the ruminant peoples (PW-734, PW-858): a deep branch, no hybrids with humans, no tiefling template
    assert tier("antelope_folk", "human") == 3 and tier("cervid_folk", "human") == 3 and tier("antelope_folk", "cervid_folk") == 3  # (both ~3 Myr, held T3 by an [[interfertile]] row: deer and antelope do not interbreed, PW-851)
    assert not [l for l in t.lines.values() if l.origin == "template" and "human" in l.parents]
    # half-elves (PW-758): a contact hybrid that never lingers, so no people of their own
    he = t.lines["half_elf"]
    assert he.origin == "hybrid" and he.contact and not he.linger
    assert all(t.lines[k].body["gut"] == "foregut" and t.lines[k].body["cellulose"] for k in ("antelope_folk", "cervid_folk"))


def test_seven_meals_horns_and_antlers_follow_real_species_and_the_horned_and_antlered_are_remembered_long():
    t = SP.load(LR.SAMPLES / "seven_meals.toml")
    b = lambda k: t.lines[k].body  # noqa: E731
    assert b("antelope_folk")["display"] == "horns" and b("cervid_folk")["display"] == "antlers"
    # antlers: reindeer-like both sexes; deer-, moose-like males only. Horns: oryx-, ibex-like both sexes; saiga-, impala-like males only
    assert (b("cervid_tundra")["display_sex"], b("cervid_tundra")["shed"]) == ("both", "both")
    assert all((b(k)["display_sex"], b(k)["shed"]) == ("males", "males") for k in ("cervid_forest", "cervid_boreal"))
    assert all(b(k)["display_sex"] == "both" for k in ("antelope_oryx", "antelope_mountain"))
    assert all(b(k)["display_sex"] == "males" for k in ("antelope_steppe", "antelope_savanna"))
    assert "in males only" in " ".join(SP.body_notes(b("antelope_steppe"))) and "in males only" not in " ".join(SP.body_notes(b("antelope_oryx")))
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "body": {"display_sex": "females"}}]})
    # the neighbours' horned ones and antlered ones are legends: their own memory length, longer than an ordinary conquest's
    rows = {r["id"]: r for r in t.exonyms}
    assert rows["horned"]["body"] == {"display": "horns"} and rows["antlered"]["body"] == {"display": "antlers"}
    assert rows["horned"]["efold_kyr"] > RP.EFOLD_KYR * 10 and rows["antlered"]["efold_kyr"] > RP.EFOLD_KYR * 10
    # PW-858: no fiend, infernal, abyssal, devil or demon label anywhere in the preset
    import re
    assert not re.search(r"fiend|infernal|abyssal|devil|demon", (LR.SAMPLES / "seven_meals.toml").read_text(), re.I)
    assert t.lines["aarakocra"].body["sweet"] is True and t.lines["arha"].body["milk"] == 0.1
    # (intended change, owner 2026-10-24: the preset ships no authored conquests, the horned and antlered names come from the sim; both ruminant peoples are aggressive)
    assert t.events == [] and "aggressive" in t.lines["antelope_folk"].traits and "aggressive" in t.lines["cervid_folk"].traits
    assert t.lines["antelope_folk"].trait("push", 1.0) == 0.7


# ---- derived incursions (PW-756) ---------------------------------------------------------------------------------------
def test_a_sudden_advance_into_another_peoples_land_is_an_incursion_with_a_direction_and_slow_drift_is_not(faketz):
    from planet.lineages import contacts as CT
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    tree = SP.parse({"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "a", "parents": ["stem"], "at": "25 kyr"}, {"id": "b", "parents": ["stem"], "at": "20 kyr"}]})
    h = H.History(tree, ps, 1)
    g = h.grid
    land = ps.fields(0.0, variability=False)["land"]
    ia, ib = h.idx["a"], h.idx["b"]
    band = land & (np.abs(g.lat) < 40)
    home = band & (g.lon < -20) & (g.lat > 0)
    east = band & (g.lon >= -20)
    tags = {"coast": np.zeros(g.n, bool), "open": np.ones(g.n, bool)}
    corr = np.full(g.n, 0.5)
    n = len(h.lines)

    def frame(ct, ago, dt, own_b):
        P = np.zeros((n, g.n))
        P[ib][own_b] = 0.8
        P[ia][band & ~own_b] = 0.8
        ct.update(P, H.Step(ago, dt, "recent", True, None), tags, corr, land)

    ct = CT.Contacts(h)
    frame(ct, 10.0, 0.5, home)  # b holds its home in the north-west, a the rest
    frame(ct, 9.5, 0.5, home)
    frame(ct, 9.0, 0.5, home | east)  # b takes the whole east within one frame: an incursion
    frame(ct, 0.0, 9.0, home | east)
    inc = ct.summary()["incursions"]
    assert len(inc) == 1 and inc[0]["by"] == "b" and inc[0]["over"] == "a"
    assert inc[0]["cells"] == int(east.sum()) and inc[0]["gain"] >= CT.INCURSION_GAIN and 8.9 < inc[0]["ago_kyr"] < 9.1
    assert inc[0]["from_deg"] is not None and 180 < inc[0]["from_deg"] < 360  # (b's older land lies to the west of the east it took)
    # the same ground taken a sliver at a time (a cell column per 2 kyr window) is the frontier's give and take, not an incursion
    ct2 = CT.Contacts(h)
    cols = np.unique(np.round(g.lon[east] / 4))
    taken = np.zeros(g.n, bool)
    for i, c in enumerate(cols):
        frame(ct2, 90.0 - 3.0 * i, 3.0, home | taken)
        taken |= east & (np.round(g.lon / 4) == c)
    frame(ct2, 0.0, 3.0, home | taken)
    slow = ct2.summary()["incursions"]
    assert len(slow) < len(cols) and sum(r["cells"] for r in slow) < int(east.sum())  # (some columns are big enough to count alone; not all)


def test_a_fast_rise_of_a_people_living_among_another_is_a_settled_among_incursion(faketz):
    from planet.lineages import contacts as CT
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    tree = SP.parse({"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "a", "parents": ["stem"], "at": "25 kyr"}, {"id": "b", "parents": ["stem"], "at": "20 kyr"}]})
    h = H.History(tree, ps, 1)
    g = h.grid
    land = ps.fields(0.0, variability=False)["land"]
    ia, ib = h.idx["a"], h.idx["b"]
    band = land & (np.abs(g.lat) < 40)
    tags = {"coast": np.zeros(g.n, bool), "open": np.ones(g.n, bool)}
    corr = np.full(g.n, 0.5)
    n = len(h.lines)

    def frame(ct, ago, dt, b_in_a):
        P = np.zeros((n, g.n))
        P[ia][band] = 0.8  # a leads everywhere throughout
        P[ib][band & (g.lon < -20)] = 0.3 if b_in_a else 0.0
        ct.update(P, H.Step(ago, dt, "recent", True, None), tags, corr, land)

    ct = CT.Contacts(h)
    frame(ct, 10.0, 0.5, False)
    frame(ct, 9.5, 0.5, True)  # b appears among a within one frame; a still leads
    frame(ct, 0.0, 9.5, True)
    inc = ct.summary()["incursions"]
    assert len(inc) == 1 and inc[0]["by"] == "b" and inc[0]["over"] == "a" and inc[0]["kind"] == "settled_among"
    assert inc[0]["cells"] == int((band & (g.lon < -20)).sum())


def test_reputation_reads_derived_incursions_before_authored_events_and_names_the_direction():
    c = _contacts(took_kyr=40.0)  # (the substrate takeover is too old to count)
    c["incursions"] = [{"by": "herders", "over": "farmers", "ago_kyr": 1.0, "span_kyr": 0.5, "cells": 120, "mkm2": 0.4, "gain": 0.3,
                        "local_share": 0.4, "lat": 40.0, "lon": 10.0, "from_deg": 280}]
    raw = SP.to_raw(_rep_tree())
    raw["event"] = [{"kind": "conquest", "by": "herders", "over": ["farmers"], "at": "3 kyr"}]
    t = SP.parse(raw)
    r = RP.build(t, c)["rows"]["farmers"]["herders"]
    assert r["valence"] == "feared" and r["name"] == "devils" and r["basis"].startswith("incursion (derived)") and r["from_dir"] == "west"
    assert "from the west" in r["text"] and r["since_kyr"] == 1.0
    c["incursions"] = []  # nothing derived: the authored anchor stands in
    r2 = RP.build(t, c)["rows"]["farmers"]["herders"]
    assert r2["basis"].startswith("conquest (authored)") and "from_dir" not in r2
    assert RP.compass(0) == "north" and RP.compass(350) == "north" and RP.compass(135) == "south-east" and RP.compass(260) == "west"


def test_an_authored_polity_is_resented_by_the_ruled_and_compact_ranges_give_a_direction():
    """PW-756: `[[event]] kind = polity` (S ruled O from `at` until `until`) is read as 'resented', fading from the rule's end;
    a feared or resented row with no derived direction takes the bearing between the two present ranges where both are compact."""
    raw = SP.to_raw(_rep_tree())
    raw["exonym"].append({"id": "overlords", "label": "the overlords", "valence": ["resented"]})
    raw["event"] = [{"kind": "polity", "by": "herders", "over": ["hunters"], "at": "3 kyr", "until": "0.5 kyr"}]
    t = SP.parse(raw)
    assert t.events[0]["kind"] == "polity" and t.events[0]["until"] == 0.5 and SP.parse(SP.to_raw(t)).events == t.events
    c = _contacts(took_kyr=40.0)
    c["pairs"].append(_pair("herders", "hunters", 40000, mixed=2.0))
    r = RP.build(t, c)["rows"]["hunters"]["herders"]
    assert r["valence"] == "resented" and r["name"] == "the overlords" and r["basis"].startswith("rule (authored)") and r["since_kyr"] == 0.5
    assert 0.6 < r["strength"] < RP.EVENT_STRENGTH and "until 500 years ago" in r["text"] and "from_dir" not in r  # (no centroids: no direction)
    standing = SP.parse({**raw, "event": [{"kind": "polity", "by": "herders", "over": "hunters", "at": "3 kyr"}]})
    r2 = RP.build(standing, c)["rows"]["hunters"]["herders"]
    assert r2["strength"] == RP.EVENT_STRENGTH and "to this day" in r2["text"]
    assert RP.build(t, c)["rows"]["herders"]["hunters"]["valence"] != "resented"  # (the rulers do not resent the ruled)
    # direction from the present ranges: the herders lie due west of the hunters, both compact
    c["substrate"]["hunters"].update(lat=0.0, lon=20.0, compact=0.97)
    c["substrate"]["herders"].update(lat=0.0, lon=0.0, compact=0.95)
    r3 = RP.build(t, c)["rows"]["hunters"]["herders"]
    assert r3["from_dir"] == "west" and "from the west" in r3["text"]
    c["substrate"]["herders"]["compact"] = 0.5  # spread round the globe: no one direction
    assert "from_dir" not in RP.build(t, c)["rows"]["hunters"]["herders"]
    c["substrate"]["herders"].update(lon=19.0, compact=0.95)  # (about 111 km apart: too close to say)
    assert "from_dir" not in RP.build(t, c)["rows"]["hunters"]["herders"]


def test_herders_press_on_pasture_only_in_proportion_to_the_herds_they_keep(faketz):
    """PW-756: spec.WAY_PRESS names the good a way presses for; history scales the rivals' load there by the people's herding."""
    for way, (good, share) in SP.WAY_PRESS.items():
        assert way in SP.WAYS and good in SP.WAYS[way] and 0 < share < 1  # (a way presses for a good it reads)
    from planet.lineages.animals import Animals
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    tree = SP.parse({"meta": {"seed": 1}, "lineage": [
        {"id": "a", "origin": "root", "at": "10 kyr", "way": "pastoral_nomad", "temp_c": [-20, 40], "rain_mm": [1, 9000]}]})
    h = H.History(tree, ps, 1)
    an = Animals(h)
    k = h.idx["a"]
    assert an.herding(k) == 0.0  # (no herd animal known to it: nothing to press with)
    herd = [s for s in an.stocks if "herd" in s.a.k]
    assert herd
    herd[0].adopt[k] = 0.3
    assert an.herding(k) == 0.3


def test_presets_orc_kin_pair_farm_and_herd_and_aarakocra_taste_like_humans_but_for_capsaicin():
    """PW-762 / PW-764 / PW-765: the orc groups are one people split by way of life and wished near; aarakocra taste sweet and
    roughly like humans but feel no capsaicin; the regional foods sit beyond bit 31 (uint64 crop layers)."""
    from planet.lineages import crop_defs as CD
    for name, herd, farm in (("dnd", None, None), ("seven_meals", "arha", "anja")):  # (dnd: no groups, PW-1357; the orc pair is a note)
        t = SP.load(LR.tree_path(name))
        if herd:
            assert t.lines[herd].way == "pastoral_nomad" and t.lines[farm].way == "farmer" and t.tier_of(herd, farm) == 0
            assert any({w.a, w.b} == {herd, farm} and w.want == "near" for w in t.wishes)
        b = t.lines["aarakocra"].body
        assert b["sweet"] is True and b["capsaicin"] is False and b["bitter"] == "normal" and b["smell"] == "normal"
    assert max(a.bit for a in CD.TABLE) >= 32 and len({a.bit for a in CD.TABLE}) == len(CD.TABLE)
    assert {"nightshade_fruit", "cacao", "pseudograin"} <= set(CD.IDS) and all(CD.BY_ID[i].weight == 0 for i in ("cacao", "squash"))


# ---- marine peoples (PW-775) ----------------------------------------------------------------------
def _marine_raw(marine: bool, more: bool = False):
    rows = [{"id": "land", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000], "traits": ["coastal"]}]
    if more:  # (a split and a template: they draw at their own starts, after the marine lines' starts)
        rows += [{"id": "stem", "origin": "root", "at": "29 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                 {"id": "twig", "origin": "split", "parents": ["stem"], "at": "15 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                 {"id": "curse", "origin": "template", "parents": ["land"], "at": "8 kyr", "share": 0.1, "sites": 2}]
    if marine:
        if more:  # (a marine child of a land stem: it neither takes the stem's land nor holds back its end)
            rows += [{"id": "tidal", "origin": "split", "parents": ["stem"], "at": "12 kyr", "realm": "coast", "temp_c": [-20, 40], "traits": ["swims"]}]
        rows += [{"id": "tide", "origin": "root", "at": "25 kyr", "realm": "coast", "temp_c": [-20, 40], "traits": ["swims"]},
                 {"id": "storm", "origin": "root", "at": "25 kyr", "realm": "sea", "temp_c": [-20, 40], "elev_m": [-3000, 0], "traits": ["swims"]}]
    return {"meta": {"seed": 3}, "lineage": rows}


def test_marine_realms_parse_and_reject_land_only_origins():
    t = SP.parse(_marine_raw(True))
    assert t.lines["tide"].realm == "coast" and t.lines["storm"].marine and not t.lines["land"].marine
    assert SP.parse(SP.to_raw(t)).lines["tide"].realm == "coast"
    with pytest.raises(ValueError):  # a group is a way of life on land
        SP.parse({"lineage": [{"id": "g", "origin": "root", "at": "20 kyr"}, {"id": "h", "origin": "group", "parents": ["g"], "at": "10 kyr", "realm": "sea"}]})
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "realm": "air"}]})


def test_marine_lines_hold_the_shore_and_the_sea_and_meet_the_land_people_on_the_coast(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h, res, pres = H.simulate(SP.parse(_marine_raw(True)), ps, tries=1)
    env, tags = h.present()
    k = {x: h.idx[x] for x in ("land", "tide", "storm")}
    held = h.p >= H.EST
    assert held[k["land"]][tags["land"]].any() and not held[k["land"]][~tags["land"]].any()
    assert held[k["tide"]].any() and not (held[k["tide"]] & ~tags["shore"]).any()  # only the shore ring
    assert held[k["storm"]].sum() > held[k["tide"]].sum() and not (held[k["storm"]] & env["land"]).any()  # open water too, no land
    assert not (held[k["storm"]] & (env["elevation"] < -3700)).any()  # inside the depth band (and its soft edge)
    pairs = {frozenset((h.lines[a].id, h.lines[b].id)) for a, b in h.contacts.pairs}
    assert frozenset(("land", "tide")) in pairs  # the shared coast is a contact
    assert {"land", "tide", "storm"} <= pres["lines"].keys()
    assert all(pres["lines"][x].get("area_mkm2", 0) > 0 for x in ("tide", "storm"))
    run = json.loads((O.save(h, res, pres, name="marine test") / "run.json").read_text())  # (the stories, homeland and layers take them)
    assert {l["id"]: l["realm"] for l in run["meta"]["lineages"]} == {"land": "land", "tide": "coast", "storm": "sea"}
    assert any(p["a"] in ("tide", "land") and p["b"] in ("tide", "land") for p in run["meta"]["contacts"]["pairs"])


def test_marine_lines_leave_the_land_peoples_as_they_were(faketz):
    """Marine lines draw from their own generator (PW-779): the land people is byte-identical with or without them."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h0, _, _ = H.simulate(SP.parse(_marine_raw(False, True)), ps, tries=1)
    h1, _, _ = H.simulate(SP.parse(_marine_raw(True, True)), ps, tries=1)
    for lid in ("land", "stem", "twig", "curse"):
        assert np.array_equal(h0.p[h0.idx[lid]], h1.p[h1.idx[lid]]), lid
    assert h0.p[h0.idx["land"]].max() > 0 and h0.p[h0.idx["twig"]].max() > 0 and h1.p[h1.idx["storm"]].max() > 0


def test_a_group_carries_its_own_markers_and_its_people_keeps_the_default():
    """PW-776: groups are cultures with markers (lactase on the Arha only), not subspecies; seven_meals puts milk on them alone."""
    t = SP.parse({"lineage": [{"id": "orc", "origin": "root", "at": "300 kyr"},
                              {"id": "herd", "origin": "group", "group_of": "orc", "at": "9 kyr", "body": {"milk": 0.1}},
                              {"id": "farm", "origin": "group", "group_of": "orc", "at": "9 kyr"}]})
    assert t.lines["herd"].body["milk"] == 0.1 and t.lines["farm"].body["milk"] is False and t.lines["orc"].body["milk"] is False
    assert SP.parse(SP.to_raw(t)).lines["herd"].body["milk"] == 0.1
    sm = LR.load_tree("seven_meals")
    assert sm.lines["arha"].body["milk"] == 0.1 and sm.lines["anja"].body["milk"] is False and sm.lines["orc"].body["milk"] is False
    ruminants = [k for k in sm.lines if k.startswith(("antelope_", "cervid_"))]  # PW-793: the antelope-kin, cervid-kin and all their cultures do not milk
    assert len(ruminants) == 9 and all(sm.lines[k].body["milks"] is False for k in ruminants)


def test_salt_reach_rivers_and_contact_zones_shorten_the_trade_route_and_the_cap_cuts_off():
    """PW-745: cost-distance to salt: a river and a contact zone make a cell nearer than on foot; beyond the cap it is cut off."""
    from planet.lineages import salt_reach as SR
    g, L, land, isl = _toy_world()
    own = np.where(land, 1000.0, 0.0)
    pit = int(np.flatnonzero(land)[0])
    own[pit] = 0.0
    none = np.zeros(g.n, bool)
    plain = SR.reach(g, land, own, np.zeros(g.n), none, 300.0, cap_km=1e9)
    riv = SR.reach(g, land, own, np.full(g.n, 5.0), none, 300.0, cap_km=1e9)
    zone = SR.reach(g, land, own, np.zeros(g.n), land.copy(), 300.0, cap_km=1e9)
    far = land & (plain["km"] < SR.UNREACHED) & (plain["km"] > 0)
    assert far.any()
    assert np.allclose(riv["km"][far], plain["km"][far] * SR.RIVER_COST) and np.allclose(zone["km"][far], plain["km"][far] * SR.TRADE_COST)
    capped = SR.reach(g, land, own, np.zeros(g.n), none, 300.0, cap_km=float(np.median(plain["km"][far])))
    assert (capped["how"][far] == 3).any() and (capped["how"][far] == 2).any()  # (inside the cap: traded; beyond: cut off)
    assert plain["how"][pit] == 1 and (plain["how"][~land] == 0).all()


def test_salt_miners_happen_where_the_beds_are_and_not_where_they_are_not():
    """PW-797: a people with the miner trait works rock salt only on country that holds beds (and ore beside it makes it both);
    no beds, no salt miners; no miner trait, no mining; worked salt reaches further, and only from where it is worked."""
    from planet.lineages import mining as MN
    from planet.lineages import salt_reach as SR
    n = 100
    beds, ore = np.zeros(n), np.zeros(n)
    beds[:20], ore[10:40] = 0.9, 0.9  # cells 0..9 salt only, 10..19 both, 20..39 ore only, the rest neither
    G = {"salt_rock": beds, "gold": ore, "_land": np.ones(n, bool)}

    def cells(a, b):
        return np.isin(np.arange(n), np.arange(a, b))

    assert MN.people_kind(G, cells(0, 10))["kind"] == "salt"
    assert MN.people_kind(G, cells(10, 20))["kind"] == "salt and ore"
    assert MN.people_kind(G, cells(20, 40))["kind"] == "ore"
    assert MN.people_kind(G, cells(40, 100))["kind"] is None  # (stone only)
    assert MN.people_kind(G, np.zeros(n, bool)) is None
    # a few salt cells in a big country are a mine, not a mining people (HELD_MIN)
    assert MN.people_kind(G, cells(18, 100))["kind"] == "ore" and MN.people_kind(G, cells(0, 100))["kind"] == "salt and ore"
    # a world without beds has no salt miners whatever the people
    assert MN.people_kind({**G, "salt_rock": np.zeros(n)}, cells(0, 100))["kind"] == "ore"
    assert MN.people_kind({k: v for k, v in G.items() if k != "salt_rock"}, cells(0, 100))["kind"] == "ore"
    # worked salt: beds AND a miner there
    worked = MN.worked_salt(G, cells(5, 60))
    assert worked.sum() == 15 and worked[5:20].all() and not worked[:5].any() and not worked[20:].any()
    assert not MN.worked_salt(G, np.zeros(n, bool)).any()
    assert MN.is_miner(["subterranean", "miner"]) and not MN.is_miner(["subterranean"]) and not MN.is_miner(None)
    # what the miners buy back is what their country lacks
    assert MN.people_kind({**G, "fertile": np.zeros(n), "grazing": np.ones(n)}, cells(0, 10))["lacks"] == ["grain and bread"]
    # reach: worked beds carry salt further; nothing changes without a mine or off the beds
    g, L, land, isl = _toy_world()
    own = np.where(land, 1000.0, 0.0)
    pit = int(np.flatnonzero(land)[0])
    own[pit] = 0.0
    flow, none = np.zeros(g.n), np.zeros(g.n, bool)
    base = SR.reach(g, land, own, flow, none, 300.0, cap_km=SR.UNREACHED)
    far = land & (base["km"] < SR.UNREACHED)
    cap = float(np.median(base["km"][far]))
    plain = SR.reach(g, land, own, flow, none, 300.0, cap_km=cap)
    assert not plain["gain"].any() and (plain["how"][far] == 3).any()
    off = none.copy()
    off[int(np.flatnonzero(~land)[0])] = True
    for m in (None, none, off):  # (no mine info, no mine, a "mine" off the land)
        r = SR.reach(g, land, own, flow, none, 300.0, cap_km=cap, mined=m)
        assert (r["how"] == plain["how"]).all() and not r["gain"].any()
    mined = none.copy()
    mined[pit] = True
    r = SR.reach(g, land, own, flow, none, 300.0, cap_km=cap, mined=mined)
    assert r["gain"].any() and (r["how"][r["gain"]] == 2).all() and (plain["how"][r["gain"]] == 3).all()
    assert (r["how"][~r["gain"]] == plain["how"][~r["gain"]]).all()  # (only the cells the mine brings in change)
    assert (r["km"][r["gain"]] <= cap * SR.MINED_CAP).all()


def test_salt_is_sought_by_settlements_not_by_a_salt_dwarf_group():
    """PW-854: no salt-dwarf subgroup in the sample trees; any settled people works the beds in its country (salt works), the miners
    (dwarves) work them as mines and send colonies to beds in reach of their country; each reaches salt further than unworked beds."""
    from planet.lineages import mining as MN
    from planet.lineages import salt_reach as SR
    for name in ("dnd", "seven_meals"):
        tree = LR.load_tree(name)
        assert "salt_dwarf" not in tree.lines and not [u for u in tree.uses if u.by == "salt_dwarf"]
    n = 100
    G = {"salt_rock": np.where(np.arange(n) < 60, 0.9, 0.0), "_land": np.ones(n, bool)}
    idx = np.arange(n)
    settled = idx >= 10  # (cells 0..9 empty land)
    miners = (idx >= 20) & (idx < 30)
    near = (idx >= 15) & (idx < 45)  # (within reach of the miners)
    mined = MN.worked_salt(G, miners) | MN.colony_cells(G, miners, settled, near)
    assert mined[20:30].all() and mined[15:20].all() and mined[30:45].all()  # (their own beds, and their neighbours' within reach)
    assert not mined[:10].any() and not mined[10:15].any() and not mined[45:].any()  # (empty land: no works; out of reach: no colony)
    works = MN.settled_works(G, settled, mined)
    assert works[10:15].all() and works[45:60].all() and not works[60:].any() and not (works & mined).any()
    assert not MN.colony_cells(G, np.zeros(n, bool), settled, np.zeros(n, bool)).any()  # (no miners, no colonies)
    # reach: a works brings salt in further than none, a mine further than a works
    g, L, land, isl = _toy_world()
    own = np.where(land, 1000.0, 0.0)
    pit = int(np.flatnonzero(land)[0])
    own[pit] = 0.0
    flow, none = np.zeros(g.n), np.zeros(g.n, bool)
    base = SR.reach(g, land, own, flow, none, 300.0, cap_km=SR.UNREACHED)
    cap = float(np.median(base["km"][land & (base["km"] < SR.UNREACHED)])) / 1.2  # (the median cell is inside the works band: cap < km <= 1.25 cap)
    src = none.copy()
    src[pit] = True
    plain = SR.reach(g, land, own, flow, none, 300.0, cap_km=cap)
    w = SR.reach(g, land, own, flow, none, 300.0, cap_km=cap, works=src)
    m = SR.reach(g, land, own, flow, none, 300.0, cap_km=cap, mined=src)
    assert not plain["gain"].any() and w["gain"].any()
    assert m["gain"].sum() > w["gain"].sum() and (m["gain"] | ~w["gain"]).all()  # (a mine reaches a superset of a works)


# ---- contact hybrids need contact, not overlap (PW-852) ---------------------------------------------------------------
def test_a_frontier_is_contact_two_ranges_that_only_touch_make_a_hybrid_where_they_touch(faketz):
    """PW-852: in closed country a rival excludes the other from its cells, so two peoples on one continent usually only touch.
    Contact is the border: the hybrid is where one holds a cell and the other the cell beside it, and nowhere else."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "a", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "b", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "ab", "origin": "hybrid", "exempt": True, "parents": ["a", "b"], "at": "20 kyr"}]}
    h = H.History(SP.parse(raw), ps, 1)
    g = h.grid
    land = ps.fields(0.0, variability=False)["land"]
    lat0 = g.lat[np.argmax(land & (np.abs(g.lon) < 20) & (np.abs(g.lat) < 20))]
    box = land & (np.abs(g.lon) < 20) & (np.abs(g.lat - lat0) < 15)
    west, east = box & (g.lon < 0), box & (g.lon >= 0)
    a, b = np.where(west, 0.7, 0.0), np.where(east, 0.7, 0.0)
    assert west.any() and east.any() and not (a * b).any()  # (disjoint ranges)
    touch = h._meeting(a, b) >= H.EST
    assert touch.any() and not (touch & ~(west | east)).any()  # (only on the two ranges' own cells)
    beside = (h._dilate(west, 1) & east) | (h._dilate(east, 1) & west)
    assert (touch == beside).all()  # exactly the cells with the other people beside them
    assert np.allclose(h._meeting(a, b)[touch], 0.7)
    assert (h._meeting(a, np.zeros(g.n)) == 0).all()  # nobody beside them: no contact
    assert (h._meeting(a, a) == a).all()  # (full overlap is as it was: the weaker of the two)


def test_a_contact_hybrid_appears_soon_after_both_parents_hold_one_continent(faketz):
    """PW-852: an arrival whose hybrid is wanted comes down near the other parent, and the hybrid appears within a few kyr of
    the two sharing a land (the dnd run 6b5d0e never produced half-elves though the elves and humans shared a continent)."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 3}, "lineage": [
        {"id": "human", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "elf", "origin": "arrival", "at": "14 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "half", "origin": "hybrid", "exempt": True, "parents": ["human", "elf"], "at": "10 kyr", "contact": True}]}
    h = H.History(SP.parse(raw), ps, 3)
    h.dens[:] = 2.0  # (PW-1275: no world, no ladder: the number the test needs)
    seen = {}
    orig = H.History._frame

    def frame(self, step, env):
        lab, _ = self.grid.components(env["land"])
        hu, el = self.whole("human") >= H.EST, self.whole("elf") >= H.EST
        shared = set(lab[hu & (lab >= 0)].tolist()) & set(lab[el & (lab >= 0)].tolist())
        if shared and "share" not in seen:
            seen["share"] = step.ago
        return orig(self, step, env)

    H.History._frame = frame
    try:
        h.run()
    finally:
        H.History._frame = orig
    assert "half" in h.origins, "the hybrid never appeared"
    assert "share" in seen and seen["share"] <= 14.0  # (the arrival came down on the humans' own land)
    assert 7.0 <= h.started["half"] <= 10.0  # (the hybrid line's own date is 10 kyr ago: it appears within 3 kyr of that, not never)


def test_the_stock_tiefling_is_a_late_template_on_humans():
    """PW-858: dnd's tieflings are a demonic template on humans from a historical event within the last ~10 kyr, never a people of their own."""
    t = SP.load(LR.SAMPLES / "dnd.toml")
    tf = t.lines["tiefling"]
    assert tf.origin == "template" and tf.parents == ["human"] and 0 < tf.ago_kyr <= 10
    assert "infernal" not in tf.name.lower()


def test_an_arrival_whose_hybrid_is_wanted_comes_down_within_reach_of_the_other_parent(faketz):
    """PW-852: the arrival's pull toward the other parent holds it within 2.5 x HYBRID_REACH_KM (it was three cells), whatever the dice."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 3}, "lineage": [
        {"id": "human", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "elf", "origin": "arrival", "at": "14 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "half", "origin": "hybrid", "exempt": True, "parents": ["human", "elf"], "at": "10 kyr", "contact": True}]}
    tree = SP.parse(raw)
    far = []
    for seed in range(1, 13):
        h = H.History(tree, ps, seed)
        h.p = np.zeros((len(h.lines), h.grid.n))
        h.active = {l.id: False for l in h.lines}
        step = h.steps[-1]
        env = step.get()
        tags = H._tags(h.grid, env)
        g = h.grid
        patch = tags["land"] & (g.lon > 90) & (g.lon < 110) & (np.abs(g.lat) < 10)  # (the humans: a patch of the east continent)
        assert patch.any()
        h.p[h.idx["human"]][patch] = 0.8
        h.active["human"] = True
        K = h._K(tree.lines["elf"], env, tags, step)
        h._origin(tree.lines["elf"], step, env, tags, K)
        c = h.origins["elf"]["cell"]
        reach = max(H.HYBRID_REACH_KM / h.cell_km, 1.0)  # (cells; a cell at least on this coarse test grid)
        d = H.graph_dist(patch, int(np.ceil(3 * reach)), g.nbr_off, g.nbr_idx)[c]
        far.append(d < 0 or d > 2.5 * reach)
    assert not any(far), (far, h.grid.n, h.cell_km)


def test_dragons_are_a_deep_extant_reptile_line_with_kinds_by_biome():
    """PW-855: the draconic stem is the dragons: dinosaur-era reptiles, megafauna at giant-like density, whose chromatic and metallic
    kinds split into the colours, each in its own country; the stems end at their last split (PW-924: no dragon of no set colour); the lizardfolk and tortles split from the reptile line as long ago, so
    the dragon-blooded peoples are no kin of them."""
    chromatic, metallic = {"red", "blue", "green", "black", "white"}, {"gold", "silver", "bronze", "copper", "brass"}
    for name in ("dnd", "seven_meals"):
        t = LR.load_tree(name)
        d = t.lines["draconic"]
        assert not d.persists and d.megafauna and d.ago_kyr >= 10_000 and t.lines[d.parents[0]].ago_kyr <= 20_000  # (the ur-dragon: near a root no older than 20 Myr)
        for g in ("chromatic_dragon", "metallic_dragon"):  # (owner: the two great kinds split ~2.5 Myr ago)
            assert t.lines[g].parents == ["draconic"] and 1_000 <= t.lines[g].ago_kyr <= 4_000 and t.lines[g].megafauna and not t.lines[g].persists
        leaves = [x.id for x in t.leaves()]
        assert t.dragon_km2 >= 1000 and not {"draconic", "chromatic_dragon", "metallic_dragon"} & set(leaves)
        kinds = {l.id.removesuffix("_dragon"): l for l in t.lines.values() if l.id.endswith("_dragon") and l.origin == "split" and l.id in leaves}
        assert set(kinds) == chromatic | metallic and all(l.megafauna for l in kinds.values())
        assert all(l.parents == ["chromatic_dragon" if l.id.removesuffix("_dragon") in chromatic else "metallic_dragon"] and l.prefers and 500 <= l.ago_kyr <= 1_000 for l in kinds.values())
        assert len({tuple(l.prefers) for l in kinds.values()}) >= 8  # (kinds differ by biome)
        for k in ("lizardfolk", "tortle"):  # (PW-988: the old 3 Myr cap was a placeholder; they split after the dragons' minds, the elder line)
            assert t.lines[k].ago_kyr < d.sapient_kyr and t.tier_of(k, "dragonborn") == 3 and t.tier_of(k, "kobold") == 3
        assert t.tier_of("dragonborn", "kobold") == 2 and t.tier_of("draconic", "dragonborn") <= 2
        for k in ("dragonborn", "kobold"):
            assert t.lines[k].parents == ["draconic"] and t.lines[k].start_near == ["draconic"]
    t = LR.load_tree("dnd")  # PW-988 (owner 10-29): the tortles, lizardfolk and troglodytes are a branch of their own, the troglodytes the later split
    s = t.lines["saurian"]
    assert s.parents == ["reptilian"] and not s.persists and s.sapient_kyr < t.lines["draconic"].sapient_kyr
    assert all(t.lines[k].parents == ["saurian"] for k in ("tortle", "lizardfolk", "troglodyte"))
    assert t.split_kyr("lizardfolk", "troglodyte") < t.split_kyr("lizardfolk", "tortle") == t.split_kyr("troglodyte", "tortle")


def test_landmasses_are_named_from_the_worlds_seed_and_rank():
    """PW-853: the continents have generated names, the same for the world's summary and the peoples' history, stable per seed."""
    from planet import names as NM
    from planet import world as WD
    a = NM.landmass_names(11, 8)
    assert len(set(a)) == 8 and all(n[0].isupper() and n.isalpha() for n in a)
    assert a == NM.landmass_names(11, 12)[:8] and NM.landmass_name(11, 3, tuple(a[:3])) == a[3]  # (a rank's name does not depend on how many)
    assert NM.landmass_names(12, 8) != a
    g = build_grid(LEVEL)
    land = g.lat > 20
    m = WD.landmasses(g, land, seed=11)
    assert m[0]["name"] == a[0] and m[0]["letter"] == "A"
    assert WD.landmasses(g, land)[0]["name"] == "A"  # (without a seed: letters, as before)
    from planet.lineages.crossing import Crossings
    env = {"land": land}
    cr = Crossings(g, env, 100.0, 0.1, seed=11)
    assert cr.names[0]["called"] == a[0] and a[0] in cr.names[0]["name"] and cr.names[0]["kind"] in ("continent", "large island", "island")
    assert Crossings(g, env, 100.0, 0.1).names[0]["called"] is None  # (no world: by coordinates)


def test_owner_given_landmass_names_override_the_generated_ones(data_root):
    """PW-867: `planet name world:ID A=Jangwa` keeps the owner's name beside the world; the peoples' history (Crossings) uses it for that
    rank only, the others keep their generated names, and deleting the world takes the file with it."""
    from planet import names as NM
    from planet.lineages.crossing import Crossings
    gen = NM.landmass_names(11, 5)
    assert NM.rank_letter(0) == "A" and NM.rank_letter(25) == "Z" and NM.rank_letter(26) == "AA"
    assert NM.load_overrides("abc123") == {} and NM.load_overrides(None) == {}
    NM.save_overrides("abc123", {"A": "Jangwa", "C": "Kitu"})
    assert NM.load_overrides("abc123") == {"A": "Jangwa", "C": "Kitu"}
    assert S.names_path("abc123").parent.name == "names"
    mixed = NM.landmass_names(11, 5, NM.load_overrides("abc123"))
    assert mixed[0] == "Jangwa" and mixed[2] == "Kitu" and [mixed[1], mixed[3], mixed[4]] == [gen[1], gen[3], gen[4]]
    g = build_grid(LEVEL)
    land = g.lat > 20
    cr = Crossings(g, {"land": land}, 100.0, 0.1, seed=11, overrides={"A": "Jangwa"})
    assert cr.names[0]["called"] == "Jangwa" and "Jangwa" in cr.names[0]["name"]
    assert Crossings(g, {"land": land}, 100.0, 0.1, seed=11).names[0]["called"] == gen[0]  # (no override: as before)
    NM.save_overrides("abc123", {})  # (nothing left: the file goes)
    assert not S.names_path("abc123").exists()


def test_planet_name_command_stores_overrides(data_root, capsys):
    """PW-867: the CLI lists a world's landmass names, stores LETTER=Name, clears LETTER=, and --generated writes the generated names."""
    import argparse

    from planet import __main__ as CLI
    from planet import names as NM
    wid = "ab12cd"
    w = S.worlds_dir() / f"{wid}.json"
    w.parent.mkdir(parents=True, exist_ok=True)
    lm = [{"name": "A", "cells": 9, "pct_of_surface": 20.0}, {"name": "B", "cells": 5, "pct_of_surface": 8.0}]
    w.write_text("{\n\"format\": \"procgen-planet/2\",\n\"name\": \"t\",\n\"id\": \"" + wid + "\",\n\"meta\": {\"seed\": 11},\n"
                 + "\"summary\": " + json.dumps({"landmasses": lm}) + ",\n\"layers\": {}\n}\n")

    def run(*a, gen=False):
        CLI.cmd_name(argparse.Namespace(world=f"world:{wid}", assign=list(a), generated=gen))
    run("a=Jangwa")
    assert NM.load_overrides(wid) == {"A": "Jangwa"} and "Jangwa" in capsys.readouterr().out
    run("A=")
    assert NM.load_overrides(wid) == {}
    run(gen=True)
    gn = NM.landmass_names(11, 2)
    assert NM.load_overrides(wid) == {"A": gn[0], "B": gn[1]}
    with pytest.raises(SystemExit):
        run("Jangwa")  # (no LETTER=)
    S.delete("world", wid)
    assert not S.names_path(wid).exists()


def test_a_sea_landing_follows_the_pull_toward_the_partner():
    """PW-861: a people whose contact hybrid is wanted comes down by the other parent when it sails over: the landing cell and chance follow
    `pull` (history._partner_pull), as the plain landing is the nearest good coast."""
    from planet.geo import world_land
    from planet.grid import shared_grid
    from planet.lineages.crossing import Crossings
    g = shared_grid(3)
    elev = np.where((g.lat > 5) & (g.lat < 50) & (((g.lon > 0) & (g.lon < 40)) | ((g.lon > 70) & (g.lon < 150))), 300.0, -2000.0)
    land = world_land({"elevation": elev, "ice": np.zeros(g.n)})
    lab, _ = g.components(land)
    home = land & (g.lon < 40)
    tags = {"coast": land.copy(), "label": lab}
    env = {"land": land}
    line = SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 Myr", "traits": ["flies"]}]}).lines["x"]
    cr = Crossings(g, env, 300.0, 0.1)
    K = np.where(land, 1.0, 0.0)
    p = np.where(home, 1.0, 0.0)
    far = land & (g.lon > 120)
    out = cr.hop(line, p, K, K.copy(), env, tags, 1.0, 1e6, np.random.default_rng(1), 0.12)
    assert out and not far[out[0][0]] and not home[out[0][0]]  # (plain: the nearest good coast over the water)
    out = cr.hop(line, p, K, K.copy(), env, tags, 1.0, 1e6, np.random.default_rng(1), 0.12, np.where(far, 1e6, 1.0))
    assert out and far[out[0][0]]  # (pulled: the partner's coast)


def test_an_arrival_near_its_partner_takes_the_freest_country_when_none_is_free(faketz):
    """PW-861: on a crowded continent no land by the partner is free of rivals (half its best habitat), and the arrival fell back to its best
    habitat anywhere, far from the partner: it now takes the freest tier near the partner (ARRIVAL_ROOM). The partner's pull for sea landings is
    x(1 + PARTNER_PULL) on its range, falling off, none without a wanted hybrid."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 3}, "lineage": [
        {"id": "human", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "crowd", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "elf", "origin": "arrival", "at": "14 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "half", "origin": "hybrid", "exempt": True, "parents": ["human", "elf"], "at": "10 kyr", "contact": True}]}
    tree = SP.parse(raw)
    far = []
    for seed in range(1, 11):
        h = H.History(tree, ps, seed)
        h.p = np.zeros((len(h.lines), h.grid.n))
        h.active = {l.id: False for l in h.lines}
        h._corr_now = np.full(h.grid.n, 0.2)  # (closed country)
        step = h.steps[-1]
        env = step.get()
        tags = H._tags(h.grid, env)
        g = h.grid
        patch = tags["land"] & (g.lon > 90) & (g.lon < 110) & (np.abs(g.lat) < 10)
        crowd = tags["land"] & (g.lon > 60) & (g.lon < 140) & ~patch
        assert patch.any() and crowd.any()
        h.p[h.idx["human"]][patch] = 0.8
        h.p[h.idx["crowd"]][crowd] = 0.7  # (every cell around the humans is held: free room under half the best habitat)
        h.active["human"] = h.active["crowd"] = True
        elf = tree.lines["elf"]
        K = h._K(elf, env, tags, step)
        assert (K - h._rivals_here(elf, K))[crowd].max() < 0.5 * K.max()
        h._origin(elf, step, env, tags, K)
        c = h.origins["elf"]["cell"]
        reach = max(H.HYBRID_REACH_KM / h.cell_km, 1.0)
        d = H.graph_dist(patch, int(np.ceil(3 * reach)), g.nbr_off, g.nbr_idx)[c]
        far.append(d < 0 or d > 2.5 * reach)
    assert not any(far), far
    # the pull
    h.active["elf"] = False
    assert h._partner_pull(tree.lines["elf"]) is not None  # (the humans are alive: the elf lands by them)
    assert h._partner_pull(tree.lines["crowd"]) is None  # (no hybrid is wanted of the crowd)
    pu = h._partner_pull(tree.lines["elf"])
    here = h.whole("human") > H.EST
    assert pu[here].min() == pu.max() == 1 + H.PARTNER_PULL and pu.min() == 1.0
    h.active["human"] = False
    assert h._partner_pull(tree.lines["elf"]) is None  # (no partner alive)


def test_megafauna_press_the_peoples_hardly_at_all_and_the_kinds_inherit_it(faketz):
    """PW-855: a megafauna line (dragons: a handful per country) puts MEGAFAUNA_PUSH of its niche overlap on the peoples that share its
    country; its kind groups are megafauna too; its dragon-blooded children are not."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "persists": True},
        {"id": "red", "origin": "group", "group_of": "wyrm", "at": "20 kyr"},
        {"id": "kin", "parents": ["wyrm"], "at": "1 Myr"},
        {"id": "folk", "parents": ["stem"], "at": "2 Myr"}]}
    plain = H.History(SP.parse(base), ps, 1)
    raw = {**base, "lineage": [dict(r, **({"megafauna": True} if r["id"] == "wyrm" else {})) for r in base["lineage"]]}
    t = SP.parse(raw)
    assert t.lines["wyrm"].megafauna and t.lines["red"].megafauna and not t.lines["kin"].megafauna and not t.lines["folk"].megafauna
    assert SP.parse(SP.to_raw(t)).lines["wyrm"].megafauna
    mega = H.History(t, ps, 1)
    i, j = mega.idx["folk"], mega.idx["wyrm"]
    assert plain.alpha[i, plain.idx["wyrm"]] > 0
    assert np.isclose(mega.alpha[i, j], H.MEGAFAUNA_PUSH * plain.alpha[i, plain.idx["wyrm"]])
    assert np.isclose(mega.alpha[i, mega.idx["red"]], H.MEGAFAUNA_PUSH * plain.alpha[i, plain.idx["red"]])
    assert np.isclose(mega.alpha[i, mega.idx["kin"]], plain.alpha[i, plain.idx["kin"]])  # (the dragon-blooded peoples press as peoples)
    assert np.isclose(mega.alpha[j, i], plain.alpha[plain.idx["wyrm"], plain.idx["folk"]])  # (the peoples press the dragons as before)


def test_megafauna_are_counted_long_lived_and_coexist_by_kind(faketz):
    """PW-924: megafauna compete with each other at their niche overlap (red dragons and fire giants), a rivalry under 1 (the metallics)
    weakens it both ways; a long generation lowers the viable number of a patch; pockets within reach are one population; the present
    summary counts each pocket; the presets carry the Damuth densities, generations and group sizes."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1, "viable_pop": 500, "giant_km2": 5000, "dragon_generation": "line"}, "lineage": [  # (giants as dense as dragons here: their overlap, not their numbers; the lines' own generation, PW-959)
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "persists": True, "megafauna": True,
         "generation_yr": 200, "group_size": [1, 3], "traits": ["flies"]},
        {"id": "gold", "parents": ["wyrm"], "at": "1 Myr", "megafauna": True, "rivalry": 0.5},
        {"id": "giant", "parents": ["stem"], "at": "2 Myr", "megafauna": True, "generation_yr": 65, "group_size": [5, 20]},
        {"id": "folk", "parents": ["stem"], "at": "2 Myr"}]}
    t = SP.parse(raw)
    assert t.lines["gold"].group_size == (1.0, 3.0) and t.lines["gold"].generation_yr == 200 and t.lines["gold"].rivalry == 0.5
    t2 = SP.parse(SP.to_raw(t))
    assert t2.lines["gold"].rivalry == 0.5 and t2.lines["giant"].group_size == (5.0, 20.0)
    h = H.History(t, ps, 1)
    plain = H.History(SP.parse({**raw, "lineage": [{k: v for k, v in r.items() if k not in ("megafauna", "rivalry")} for r in raw["lineage"]]}), ps, 1)
    w, gd, gi, f = (h.idx[x] for x in ("wyrm", "gold", "giant", "folk"))
    assert np.isclose(h.alpha[w, gi], plain.alpha[w, gi])  # (megafauna among themselves: their niche overlap in full)
    assert np.isclose(h.alpha[f, gi], H.MEGAFAUNA_PUSH * plain.alpha[f, gi])  # (on the peoples: hardly at all)
    assert np.isclose(h.alpha[gd, gi], 0.5 * plain.alpha[gd, gi]) and np.isclose(h.alpha[gi, gd], 0.5 * plain.alpha[gi, gd])
    assert np.isclose(h.line_mvp(t.lines["wyrm"]), 500 * 25 / 200) and h.line_mvp(t.lines["folk"]) == 500
    g = h.grid
    held = np.zeros(g.n, bool)
    two = int(g.nbr_idx[g.nbr_off[g.nbr_idx[g.nbr_off[0]]]])  # (two cells from cell 0: a separate pocket within reach)
    held[[0, two]] = True
    far = int(np.argmin(g.centers @ g.centers[0]))  # (the antipode)
    held[far] = True
    assert g.components(held)[1] == 3
    lab, n = MG.linked_pockets(h, held, 4 * h.cell_km)
    assert n == 2 and lab[0] == lab[two] != lab[far] and (lab[~held] == -1).all()
    res = h.run()
    pres = H.present_summary(h, res["present"])
    for lid, r in pres["megafauna"].items():
        assert pres["lines"][lid]["megafauna"] and r["count"] == sum(p["count"] for p in r["pocket_list"]) and r["count"] > 0
        assert all(p["count"] >= 1 and p["country"] and p["groups"] for p in r["pocket_list"])
    assert "folk" not in pres["megafauna"]
    for name in ("dnd", "seven_meals"):
        tr = LR.load_tree(name)
        for l in tr.lines.values():
            if l.megafauna and "dragon" in l.id or l.id == "draconic":
                assert 1000 <= tr.dragon_km2 <= 10000 and l.generation_yr >= 150 and l.group_size[1] <= 3
            if l.megafauna and "giant" in l.id:
                assert 1000 <= tr.giant_km2 <= 10000 and 50 <= l.generation_yr <= 80 and l.group_size == (5.0, 20.0)
        from planet.lineages import life_history as LH  # (lane 78: a people's generation from its canon ages where given, else its own)
        assert 20 <= LH.generation_yr(tr.lines["dragonborn"]) <= 30 and tr.lines["metallic_dragon"].rivalry < 1  # (not the wyrms' 430)


def test_crowding_measures_the_share_of_habitat_rivals_take():
    """PW-887: crowding (0 free, 1 squeezed out) is the mean share of K over the held cells that rivals take; it drives exploration."""
    K = np.array([1.0, 1.0, 0.5, 1.0])
    held = np.array([True, True, True, False])
    assert H.crowding(K, K.copy(), held) == 0.0  # (all the room left)
    assert H.crowding(K, np.array([0.5, 0.5, 0.25, 0.0]), held) == pytest.approx(0.5)  # (half of every held cell)
    assert H.crowding(K, np.zeros(4), held) == 1.0
    assert H.crowding(K, K, np.zeros(4, bool)) == 0.0  # (no range: nothing)


def test_origins_pick_a_landmass_by_habitable_area_to_the_z(faketz):
    """PW-888: the landmass of an origin is drawn with probability ~ (habitable cells)^z (species-area, z = 0.3), the island
    keeping a share, a landmass too small to hold a viable founder population drawing none; habitat then picks the cell."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1, "viable_pop": 0}, "lineage": [{"id": "a", "appears": "30 kyr", **base}]}
    h = H.History(SP.parse(raw), ps, 1)
    g = h.grid
    land = ps.fields(0.0, variability=False)["land"]
    lab, n = g.components(land)
    sizes = np.bincount(lab[land], minlength=n).astype(float)
    assert n >= 3 and sizes.min() < 0.1 * sizes.max()  # two continents and an island
    K = np.where(land, 1.0, 0.0)
    line = h.tree.lines["a"]
    score = K * np.exp(np.random.default_rng(3).gumbel(size=g.n))  # (heavy-tailed luck, as _noise)
    env = {"land": land}
    picks = np.array([lab[int(np.argmax(h._by_landmass(line, score, K, env)))] for _ in range(1500)])
    got = np.bincount(picks, minlength=n) / len(picks)
    want = sizes ** H.SPECIES_AREA_Z / (sizes ** H.SPECIES_AREA_Z).sum()
    assert np.allclose(got, want, atol=0.05)
    assert got[np.argmax(sizes)] < 0.6 and (got > 0.03).sum() == n  # (the biggest does not take all; every landmass draws some)
    # a long-term viable population (ORIGIN_MVP_MULT x viable_pop) that the smallest landmass cannot hold: only the others draw
    h.tree.viable_pop = float(np.sort(sizes)[1] * h.dens[h.idx["a"]] * h.cell_mkm2 * 1e6 * 0.5 * 0.99 / H.ORIGIN_MVP_MULT)
    few = np.array([lab[int(np.argmax(h._by_landmass(line, score, K, env)))] for _ in range(300)])
    assert set(np.unique(few)) <= {int(i) for i in np.argsort(sizes)[-2:]}
    # one qualifying landmass: nothing is drawn
    one = np.where(lab == np.argmax(sizes), score, 0)
    assert np.array_equal(h._by_landmass(line, one, K, env), one)


def test_dragon_km2_sets_every_dragon_density(faketz):
    """PW-923 (owner): meta.dragon_km2 is the dragons' density, one per that many km2 (default 5,000); other lines keep theirs."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies"]},
        {"id": "giant", "parents": ["stem"], "at": "2 Myr", "megafauna": True}]}
    t = SP.parse(raw)
    assert t.dragon_km2 == 5000 and SP.parse(SP.to_raw(t)).dragon_km2 == 5000
    h = H.History(t, ps, 1)
    assert np.isclose(h.dens[h.idx["wyrm"]], 1 / 5000) and np.isclose(h.dens[h.idx["giant"]], 1 / 2000)  # (meta.giant_km2, PW-963: default 2,000)
    t2 = SP.parse({**raw, "meta": {"seed": 1, "dragon_km2": 1000}})
    assert np.isclose(H.History(t2, ps, 1).dens[h.idx["wyrm"]], 1 / 1000)
    t3 = SP.parse({**raw, "meta": {"seed": 1, "giant_km2": 5000}})
    assert t3.giant_km2 == 5000 and SP.parse(SP.to_raw(t3)).giant_km2 == 5000
    assert np.isclose(H.History(t3, ps, 1).dens[h.idx["giant"]], 1 / 5000)


def test_megafauna_natural_density_pressed_by_peoples(faketz):
    """PW-957, PW-963: a megafauna kind's natural density comes from its mass (dragons on Marshall et al. 2021's mesotherm line over
    every age, ~1 per 65 km2 at 3.2 t; giants as mass-scaled foragers, ~1 per 140 km2 at 2.2 t, 1 per 345 at 7.3 t); peoples press it
    down by the persecution kill (PW-1068), one rule for both, and the summary counts by it."""
    from planet.lineages.history import megafauna as MG
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1, "dragon_ages": "base"}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "folk", "parents": ["stem"], "at": "1 Myr"},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "mass_kg": 3200, "generation_yr": 200, "traits": ["flies"]},
        {"id": "hill", "parents": ["stem"], "at": "2 Myr", "megafauna": True, "mass_kg": 2200},
        {"id": "storm", "parents": ["hill"], "at": "1 Myr", "megafauna": True, "mass_kg": 7300}]}
    t = SP.parse(raw)
    assert t.lines["storm"].mass_kg == 7300 and SP.parse(SP.to_raw(t)).lines["hill"].mass_kg == 2200
    assert SP.parse({**raw, "lineage": raw["lineage"][:4] + [{"id": "kid", "parents": ["hill"], "at": "1 Myr", "megafauna": True}]}).lines["kid"].mass_kg == 2200
    h = H.History(t, ps, 1)
    w, hi, st, f = (h.idx[x] for x in ("wyrm", "hill", "storm", "folk"))
    assert 60 <= 1 / h.dens_nat[w] <= 70 and 130 <= 1 / h.dens_nat[hi] <= 150 and 330 <= 1 / h.dens_nat[st] <= 360
    assert h.dens_nat[f] == h.dens[f]
    # pressure: none on empty land, near full where a people holds it, and the density between natural and pressed by it
    h.dens[f] = h.dens_nat[f] = 1.0  # (PW-1275: no world, no ladder: the number the test needs)
    P = np.zeros((len(h.lines), h.grid.n))
    P[f, : h.grid.n // 2] = 0.5
    s = MG.pressure(h, P)
    assert s[: h.grid.n // 2].min() > 0.99 and s[h.grid.n // 2:].max() == 0
    # persecution (PW-1068): a kill against slow breeding, natural x 1 / (1 + kill / r); none on empty land, never zero, never above
    # natural; it rises with the era's tech level (MG.means), and a kind that breeds faster (the giants' shorter generation) loses less
    # the kill falls by age class (owner 10-30): wyrmlings reachable early, adults only at high tech, so a stone-age people barely dents them
    k0 = MG.kill(h, P)
    half = np.s_[: h.grid.n // 2]
    assert k0[h.grid.n // 2:].max() == 0 and k0[half].min() > 0
    h._ago_now = 0.0  # (the present: meta.era, renaissance)
    d = MG.local_density(h, w, k0)
    assert np.allclose(d[h.grid.n // 2:], h.dens_nat[w]) and (d >= 0).all() and (d <= h.dens_nat[w] + 1e-15).all()
    h._ago_now = 10.0  # (the stone age)
    d10 = MG.local_density(h, w, k0)
    assert (d10[half] > 0.9 * h.dens_nat[w]).all() and (d10[half] > d[half]).all()
    v0, v9 = MG.vulnerability(0.0), MG.vulnerability(0.9)
    assert v0[0] == v9[0] == 1 and v0[2] < 0.02 < 0.5 < v9[2] and (v0 <= v9).all()  # (the adults' share of the kill rises with tech)
    for e in (1e-4, 1e-3):  # (a kill on wyrmlings alone costs far less than the same on the adults: elasticity)
        assert MG.dragon_kept(h, e, 0.0) > MG.dragon_kept(h, e, 0.9) > 0
    assert np.isclose(MG.dragon_kept(h, 0.0, 0.5), 1.0) and MG.dragon_kept(h, 1.0, 1.0) == 0
    # local extirpation (PW-1246 B, lane 103): kept falls linearly with the births' rise F and is 0 once F >= BREED_X; KILL_Q is set so
    # LOSS_KM2 farmers of MEANS_REF at tech level LOSS_LEV reach that point on the default schedule (the lions' 25 per km2, Riggio 2013; this tree runs the base schedule, a little more vulnerable)
    from planet.lineages import dragon_ages as DA
    e_loss = MG.KILL_Q * MG.LOSS_KM2 * MG.MEANS_REF
    assert np.isclose(MG.births_rise(DA.DEFAULT, e_loss, MG.LOSS_LEV)[0], MG.BREED_X, rtol=1e-3)
    assert MG.dragon_kept(h, 0.7 * e_loss, MG.LOSS_LEV) > 0 and MG.dragon_kept(h, 1.1 * e_loss, MG.LOSS_LEV) == 0
    assert 0.2 < MG.dragon_kept(h, 0.5 * e_loss, MG.LOSS_LEV) < 0.7 and MG.dragon_kept(h, e_loss, 0.0) > 0.9
    assert np.isclose(MG.guild_kept(h, np.array([0.0, 0.5, 2.0]) * e_loss, 1.0), [1.0, 0.5, 0.0]).all()
    h._ago_now = 0.0
    dh = MG.local_density(h, hi, k0)
    assert (dh[half] / h.dens_nat[hi] < 1).all() and (dh[half] > 0).all()
    # the viewer's pressure settings (owner D14): meta.press_early / press_late multiply the kill, blended by tech level
    t5 = SP.parse({**raw, "meta": {**raw["meta"], "press_early": 0.25, "press_late": 4.0}})
    assert (t5.press_early, t5.press_late) == (0.25, 4.0) and SP.parse(SP.to_raw(t5)).press_late == 4.0
    assert MG.press_x(t5, 0.0) == 0.25 and MG.press_x(t5, 1.0) == 4.0 and MG.press_x(h.tree, 0.5) == 1.0
    h5 = H.History(t5, ps, 1)
    h5._ago_now = 0.0  # (the present, renaissance: mostly the late setting, harsher)
    assert (MG.local_density(h5, w, k0)[half] < d[half]).all()
    h5._ago_now = h._ago_now = 10.0  # (the stone age: the early setting, gentler)
    assert (MG.local_density(h5, w, k0)[half] > MG.local_density(h, w, k0)[half]).all()
    h._ago_now = 0.0
    # the world-builder's dial (lane 103): meta.dragon_abundance multiplies every dragon kind's density, not the giants'
    t6 = SP.parse({**raw, "meta": {**raw["meta"], "dragon_abundance": 4.0}})
    assert t6.dragon_abundance == 4.0 and SP.parse(SP.to_raw(t6)).dragon_abundance == 4.0 and SP.parse(raw).dragon_abundance == 1.0
    h6 = H.History(t6, ps, 1)
    h6._ago_now = 0.0
    assert np.allclose(MG.local_density(h6, w, k0), 4.0 * d) and np.allclose(MG.local_density(h6, hi, k0), dh)
    # the nominal density (meta.giant_km2) no longer sets any density
    t4 = SP.parse({**raw, "meta": {"seed": 1, "giant_km2": 50}})
    h4 = H.History(t4, ps, 1)
    assert np.allclose(MG.local_density(h4, h4.idx["hill"], np.zeros(h4.grid.n)), h4.dens_nat[h4.idx["hill"]])


def test_megafauna_tolerated_tier_and_ecological_release(faketz):
    """PW-1024: a megafauna kind's `tolerates` country (and its own just past its comfort range) holds it at TOLERATE_K with the comfort
    range's margin (EDGE_C...), never lowering its habitat anywhere; ecological release offers at most RELEASE_K of rich land near its own country that no other kind of its sort holds, none on land no richer than
    the median, and none in the deep epoch."""
    from planet.lineages.history import params as HP
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    env = ps.fields(0.0, variability=False)
    tags = H._tags(ps.grid, env)
    row = {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "traits": ["flies"], "temp_c": [10, 30], "rain_mm": [100, 9000],
           "prefers": ["coast"]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        dict(row, tolerates=["inland"]), dict(row, id="other", tolerates=[]), {"id": "folk", "parents": ["stem"], "at": "1 Myr"}]}
    t = SP.parse(raw)
    assert t.lines["wyrm"].tolerates == ["inland"] and SP.parse(SP.to_raw(t)).lines["wyrm"].tolerates == ["inland"]
    with pytest.raises(ValueError):
        SP.parse({**raw, "lineage": raw["lineage"][:1] + [dict(row, tolerates=["nowhere"])]})
    Kt, Kp = H.capacity(t.lines["wyrm"], env, tags), H.capacity(t.lines["other"], env, tags)
    own = tags["coast"]
    full = own & (Kp >= HP.TOLERATE_K)
    assert full.any() and np.allclose(Kt[full], Kp[full])  # (its own country as before, but past its comfort range's edge: there the margin holds it at half)
    edge = tags["inland"] & ~own & tags["land"]
    assert edge.any() and Kt[edge].max() <= HP.TOLERATE_K + 1e-9 and (Kt[edge] > Kp[edge] + 1e-9).any()
    assert np.all(Kt >= Kp - 1e-12)
    h = H.History(t, ps, 1)
    k, j = h.idx["wyrm"], h.idx["other"]
    step = type("Step", (), {"epoch": "recent", "ago": 1.0})()
    h._prey = np.full(h.grid.n, 10.0 * h.prey_ref)
    h.active = {x.id: x.id == "wyrm" for x in h.lines}
    h.p = np.zeros((len(h.lines), h.grid.n))
    h._K_own[k] = np.where(tags["land"], 1.0, 0.0)
    rel = MG.release(h, t.lines["wyrm"], k, env, tags, step)
    assert rel.max() <= MG.RELEASE_K + 1e-9 and (rel[tags["land"]] > 0).any()
    h.active["other"] = True
    h.p[j][tags["land"]] = 0.5  # (another dragon kind holds the land: nothing opens)
    assert not MG.release(h, t.lines["wyrm"], k, env, tags, step).any()
    h.p[j][:] = 0.0
    lat = np.degrees(np.arcsin(ps.grid.centers[:, 2]))
    h._K_own[k] = np.where(tags["land"] & (lat > 60), 1.0, 0.0)  # (its own country only in the far north: release only next to it)
    rel = MG.release(h, t.lines["wyrm"], k, env, tags, step)
    reach_km = (max(1, round(MG.RELEASE_KM / h.cell_km)) + 1) * 1.5 * h.cell_km
    far = tags["land"] & (lat < 60 - reach_km / 111.0)
    assert far.any() and not rel[far].any()
    h._prey = np.full(h.grid.n, h.prey_ref)  # (prey no better than the median: a dragon still hunts its range, HUNT_KM, but no farther; lane 90)
    rel = MG.release(h, t.lines["wyrm"], k, env, tags, step)
    hunt_km = (max(1, round(MG.HUNT_KM / h.cell_km)) + 1) * 1.5 * h.cell_km
    far = tags["land"] & (lat < 60 - hunt_km / 111.0)
    assert far.any() and not rel[far].any() and rel.max() <= MG.RELEASE_K + 1e-9
    assert MG.release(h, t.lines["wyrm"], k, env, tags, type("Step", (), {"epoch": "deep", "ago": 100.0})()) is None


def test_megafauna_natural_settings_and_prey(faketz):
    """PW-957, PW-958, PW-959, PW-966: meta.megafauna_natural picks the natural density (prey: Carbone & Gittleman on the prey field;
    mesotherm / mammal: Damuth at the ecological mass), meta.dragon_ages the schedule (ecological mass, stages), meta.dragon_generation
    the dragons' generation; the summary splits dragons by stage."""
    from planet.lineages import dragon_ages as DA
    from planet.lineages.history import megafauna as MG
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies"]},
        {"id": "hill", "parents": ["stem"], "at": "2 Myr", "megafauna": True, "mass_kg": 2200}]}
    assert (lambda x: (x.megafauna_natural, x.dragon_ages, x.dragon_generation))(SP.parse(raw)) == ("food", "younger", "schedule")  # (owner 10-28; food: owner 10-29, PW-990 B)
    raw = {**raw, "meta": {"seed": 1, "dragon_ages": "base"}}
    t = SP.parse(raw)
    t2 = SP.parse({**raw, "meta": {"seed": 1, "megafauna_natural": "mammal", "dragon_ages": "younger", "dragon_generation": "line"}})
    assert (SP.parse(SP.to_raw(t2)).megafauna_natural, SP.parse(SP.to_raw(t2)).dragon_ages) == ("mammal", "younger")
    for bad in ({"megafauna_natural": "x"}, {"dragon_ages": "x"}, {"dragon_generation": "x"}):
        with pytest.raises(ValueError):
            SP.parse({**raw, "meta": {"seed": 1, **bad}})
    base, young = DA.structure("base"), DA.structure("younger")
    assert 0.06 < base["share"][3] < 0.08 and 0.3 < base["biomass_share"][3] < 0.37 and 3000 < base["eco_mass_kg"] < 3300
    assert 400 < base["generation_yr"] < 460 and 650 < base["generation_mass_yr"] < 750
    assert young["share"][3] < base["share"][3] and young["share"][1] > base["share"][1]
    h = H.History(t, ps, 1)
    w, hi = h.idx["wyrm"], h.idx["hill"]
    assert h.prey_wild is None and 60 <= 1 / h.dens_nat[w] <= 70  # (no world: "prey" falls back to the mesotherm line)
    assert 400 < h.gen_yr(h.lines[w]) < 460 and h.gen_yr(h.lines[hi]) == h.lines[hi].generation_yr
    h2 = H.History(t2, ps, 1)
    assert h2.gen_yr(h2.lines[w]) == 200 and 25 <= 1 / h2.dens_nat[w] <= 80  # (mammal line at the younger schedule's lighter mass)
    # prey mode with a prey field: dragons per Carbone & Gittleman, ~1 per 530 km2 at 1 t/km2 of prey (base schedule)
    from planet.lineages import prey as PR
    g1 = (PR.KJ_PER_G_LIVE / 10.0 ** PR.PREY_LOG_A) ** (1 / PR.PREY_EXP) / PR.KJ_PER_G_C  # (g C/m2/yr that McNaughton's fit gives 1 t/km2 of wild prey)
    ps.graze_npp = g1 / PR.above(ps.rain0)  # (the fit reads the above-ground part, at each cell's rain: lane 90, PW-1073)
    h3 = H.History(SP.parse({**raw, "meta": {**raw["meta"], "megafauna_natural": "prey"}}), ps, 1)
    hf = H.History(t, ps, 1)  # (the default, "food": PW-990 B)
    del ps.graze_npp
    assert np.allclose(h3.prey_wild, 1.0)
    d = MG.natural(h3, w, h3.prey_wild)
    assert 500 <= 1 / d.mean() <= 560
    # food mode without a budget (the deep epoch): the wild offtake's apex part / a dragon's food, per t/km2 of prey
    df = MG.natural(hf, w, hf.prey_wild)
    assert np.allclose(df, MG.OFFTAKE * MG.dragon_share(hf) / (hf.dragon_struct["cattle_yr"] * PR.HEAD_T))  # (young dragons eat in the
    # smaller classes: the dragons' share is the apex class's over 1 - the young's share of their food, lane 90, PW-1071)
    assert np.allclose(MG.natural(h3, hi, h3.prey_wild), h3.dens_nat[hi])  # (giants: productivity 1 at the median)
    P = np.zeros((len(h3.lines), h3.grid.n))
    P[w] = 0.5
    h3._land_now = np.ones(h3.grid.n, bool)
    tags = {"land": np.ones(h3.grid.n, bool)}
    h3._K_now = {}
    out = MG.summary(h3, P, tags)
    r = out["wyrm"]
    assert sum(r["stages"]) == r["count"] > 0 and r["ages"] == "base" and "prey_t_km2" in r["pocket_list"][0]
    assert 500 <= r["natural_one_per_km2"] <= 560 and r["cattle_yr_each"] > 5
    assert "ancient" in MG.line_text("wyrm", "wyrms", r) or r["stages"][3] == 0


def test_dragons_held_to_their_food(faketz):
    """PW-977 stage 1: dragons crowded beyond the food a cell supplies (the wild herds' offtake plus the tolerable stock share) are
    scaled down to it, together across kinds; where the food is ample, nothing changes; and the summary reports the use."""
    from planet.lineages import prey as PR
    from planet.lineages.history import megafauna as MG
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1, "dragon_km2": 100, "megafauna_natural": "prey"}, "lineage": [  # (stage 1's cap, on the Carbone density)
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies"]},
        {"id": "drake", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies"]}]}
    t = SP.parse(raw)
    g1 = (PR.KJ_PER_G_LIVE / 10.0 ** PR.PREY_LOG_A) ** (1 / PR.PREY_EXP) / PR.KJ_PER_G_C
    ps.graze_npp = np.full(ps.grid.n, 0.2 * g1)  # (poor country: ~0.2 t/km2 of wild prey)
    h = H.History(t, ps, 1)
    del ps.graze_npp
    n = h.grid.n
    P = np.zeros((len(h.lines), n))
    P[h.idx["wyrm"]] = P[h.idx["drake"]] = 1.0
    w = h.idx["wyrm"]
    s = np.full(n, 1e-3)  # (a kill effort on every age class, PW-1068)
    ct = h.dragon_struct["cattle_yr"] * PR.HEAD_T
    tags = {"land": np.ones(n, bool)}
    MG.BUDGET = False
    try:
        prey, food, live = MG.prey_and_food(h, P, s * 0.0, tags)
    finally:
        MG.BUDGET = True
    assert np.allclose(food, MG.OFFTAKE * prey) and np.allclose(live, 0)
    free = MG.local_density(h, w, s, prey, food, P)
    assert np.allclose(free, MG._pressed(h, w, s, prey)) and 2 * free.max() * ct < food.min()  # (ample: untouched)
    old, MG.BUDGET = MG.OFFTAKE, False  # (stage 1 alone: the peoples' and the guild's shares are test_food_budget's)
    MG.OFFTAKE = 0.0002  # (a land that can feed little: the two kinds together would need more than it supplies)
    try:
        prey, food, live = MG.prey_and_food(h, P, s * 0.0, tags)
        d = MG.local_density(h, w, s, prey, food, P)
        assert (2 * free * ct > food).all() and np.allclose(2 * d * ct, food, rtol=1e-6) and (d < free).all()  # (shared across the kinds)
        P[h.idx["drake"]] = 0.0  # (one kind alone gets the whole supply)
        assert np.allclose(MG.local_density(h, w, s, prey, food, P) * ct, food, rtol=1e-6)
        MG.FOOD_CAP = False
        try:
            assert np.allclose(MG.local_density(h, w, s, prey, food, P), free)
        finally:
            MG.FOOD_CAP = True
    finally:
        MG.OFFTAKE, MG.BUDGET = old, True
    # the deep epoch has no food field: not held
    assert np.allclose(MG.local_density(h, w, s, None, None, P), MG.local_density(h, w, s, None))


def test_food_budget_peoples_then_guild_then_dragons(faketz):
    """PW-977 stage 2: per cell the wild offtake goes first to the peoples' hunters (density x game need), the giants and the rest of the
    predator guild (guild_ratio x the dragons' own natural food) take next, and the dragons get the rest; the guild ratio follows Carbone,
    Turvey & Bielby 2011's size classes."""
    from planet.lineages import prey as PR
    from planet.lineages.history import megafauna as MG
    assert 4.5 < MG.guild_ratio() < 5.5  # (the 1,123 and 5,347 kg classes hold ~17% of the guild's food: the rest takes ~5 times theirs)
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "hunt", "parents": ["stem"], "at": "5 Myr", "way": "forager", "traits": ["hunter"], "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "farm", "parents": ["stem"], "at": "5 Myr", "way": "farmer", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies"]}]}
    t = SP.parse(raw)
    g1 = (PR.KJ_PER_G_LIVE / 10.0 ** PR.PREY_LOG_A) ** (1 / PR.PREY_EXP) / PR.KJ_PER_G_C
    ps.graze_npp = 3.0 ** (1 / PR.PREY_EXP) * g1 / PR.above(ps.rain0)  # (~3 t/km2 of wild prey)
    ps.forage = np.full(ps.grid.n, 2.0)
    h = H.History(t, ps, 1)
    del ps.graze_npp, ps.forage
    n = h.grid.n
    hu, fa, w = h.idx["hunt"], h.idx["farm"], h.idx["wyrm"]
    assert h._meat[hu] > 5 * h._meat[fa] > 0 and h._meat[w] == 0  # (a forager lives on game, a farmer hardly hunts)
    tags = {"land": np.ones(n, bool)}
    P = np.zeros((len(h.lines), n))
    P[w] = 1.0
    h.mf_natural = "prey"  # (first under "prey", where the guild is a multiple of the dragons' own Carbone food)
    b0 = MG.budget(h, P, np.zeros(n), tags)
    assert np.allclose(b0["peoples"], 0) and np.allclose(b0["giants"], 0) and (b0["guild"] > 0).all()
    assert np.allclose(b0["food"], b0["wild"] + b0["stock"] - b0["guild"]) and (b0["food"] > 0).all()
    own = (1 - MG.dragon_share(h)) * (b0["wild"] + b0["stock"])  # (the guild: its size classes' share, in every mode since lane 90)
    assert np.allclose(b0["guild"], own)
    P[hu] = 1.0  # a forager people on the land: its hunters take before the guild and the dragons
    b1 = MG.budget(h, P, np.zeros(n), tags)
    need = h.dens_at(hu) * h._meat[hu]
    assert np.allclose(b1["peoples"], need, rtol=0.05)  # (their take comes out of what the guild and the dragons share; lane 90: the guild is a share,
    # no longer a fixed multiple, so the dragons no longer bear all of it)
    assert np.allclose(b1["food"] + b1["guild"], b0["food"] + b0["guild"] - b1["peoples"]) and (b1["food"] < b0["food"]).all()
    P[hu] = 0.0
    MG.BUDGET = False
    try:
        b2 = MG.budget(h, P, np.zeros(n), tags)
        assert np.allclose(b2["food"], b2["wild"] + b2["stock"]) and np.allclose(b2["guild"], 0)
    finally:
        MG.BUDGET = True
    h.mf_natural = h.tree.megafauna_natural
    # meta.megafauna_natural = "food" (the default, owner 10-29, PW-990 B): the guild splits the rest by size class, and the dragons'
    # natural density is their part / a dragon's food; under "prey" the guild is a multiple of the dragons' Carbone food (above)
    assert h.mf_natural == "food"
    b3 = MG.budget(h, P, np.zeros(n), tags)
    r = MG.guild_ratio()
    assert np.allclose(b3["food"], MG.dragon_share(h) * b3["pool"]) and np.allclose(b3["food"] + b3["guild"], b3["pool"])  # (nobody
    # kills here, so the guild is unpressed; the young dragons' food is inside the smaller classes' share, lane 90)
    nat = MG.natural(h, w, b3["prey"], b3["food"])
    assert np.allclose(nat * h.dragon_struct["cattle_yr"] * PR.HEAD_T, b3["food"])
    # the competition settings (coordinator 10-30, the paper's reframe): meta.rivals, meta.game_share, meta.overkill; defaults as before
    assert (t.rivals, t.game_share, t.overkill) == (1.0, 1.0, PR.OVERKILL) and np.isclose(MG.guild_ratio(h), r)
    P[hu] = 1.0
    b4 = MG.budget(h, P, np.ones(n), tags)  # (full overkill pressure)
    for k, v in (("rivals", 0.0), ("game_share", 0.0), ("overkill", 0.0)):
        old = getattr(h.tree, k)
        setattr(h.tree, k, v)
        try:
            b5 = MG.budget(h, P, np.ones(n), tags)
        finally:
            setattr(h.tree, k, old)
        assert (b5["food"] > b4["food"]).all(), k  # (less competition, more food for the dragons)
        if k == "rivals":
            assert np.allclose(b5["guild"], 0)
        if k == "game_share":
            assert np.allclose(b5["peoples"], 0)
        if k == "overkill":
            assert (b5["wild"] > b4["wild"]).all()
    t6 = SP.parse({**raw, "meta": {"seed": 1, "rivals": 0.5, "game_share": 0.25, "overkill": 0.23}})
    assert (SP.parse(SP.to_raw(t6)).rivals, t6.game_share, t6.overkill) == (0.5, 0.25, 0.23)
    with pytest.raises(ValueError):
        SP.parse({**raw, "meta": {"seed": 1, "game_share": 1.5}})


def test_food_chain_revisions_lane90(faketz):
    """Lane 90 (the dragon-density paper's Table 10): overkill follows how long small folk have held the land (Sandom 2014, PW-1000);
    the deep epoch has a planet food budget (PW-1062); the peoples press the smaller predators too (PW-1070); a linked population needs
    LINKED_MVP (PW-1069); the dragons' share counts the young in the smaller classes (PW-1071)."""
    from planet.lineages import prey as PR
    from planet.lineages.history import megafauna as MG
    assert 0.15 < MG.dragon_share() < 0.25 and MG.dragon_share() > 1 / (1 + MG.guild_ratio())
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "farm", "parents": ["stem"], "at": "5 Myr", "way": "farmer", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "wyrm", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies"]}]}
    g1 = (PR.KJ_PER_G_LIVE / 10.0 ** PR.PREY_LOG_A) ** (1 / PR.PREY_EXP) / PR.KJ_PER_G_C
    ps.graze_npp = 3.0 ** (1 / PR.PREY_EXP) * g1 / PR.above(ps.rain0)
    ps.forage = np.full(ps.grid.n, 2.0)
    h = H.History(SP.parse(raw), ps, 1)
    h.dens[[i for i, l in enumerate(h.lines) if not l.megafauna]] = 5.0 if 'farm' in h.idx else 2.0  # (PW-1275: no world, no ladder: the number the test needs)
    del ps.graze_npp, ps.forage
    n, fa, w = h.grid.n, h.idx["farm"], h.idx["wyrm"]
    land = np.ones(n, bool)
    P = np.zeros((len(h.lines), n))
    P[fa, : n // 2] = 1.0
    # the overkill's clock: land held 1 kyr is naive (meta.overkill), land held 3 Myr nearly spared
    h._ago_now = 3000.0
    MG.note_settled(h, P, 3000.0)
    h._ago_now = 0.0
    ok_old = np.asarray(MG.overkill(h))
    assert np.allclose(ok_old[: n // 2], PR.OVERKILL * 0.02 / 0.46)
    h._first_ago[:] = -1.0
    MG.note_settled(h, P, 1.0)
    assert np.allclose(np.asarray(MG.overkill(h))[: n // 2], PR.OVERKILL)
    # the deep epoch: one planet figure, less with peoples on half the land than with none
    MG.deep_budget(h, np.zeros_like(P), land)
    empty = h._deep_food
    assert np.isclose(empty, MG.OFFTAKE * h._wild_mean * MG.dragon_share(h))
    MG.deep_budget(h, P, land)
    assert 0 < h._deep_food < empty
    nat = MG.natural(h, w, None, None)
    assert np.isclose(nat, h._deep_food / (h.dragon_struct["cattle_yr"] * PR.HEAD_T))
    # the smaller predators: kept below 1 where the farmers kill, 1 where nobody does
    gk = MG.guild_kept(h, MG.kill(h, P, land))
    assert gk[: n // 2].max() < 1.0 and np.allclose(gk[n // 2:], 1.0)
    # a linked population's floor
    assert MG.linked_mvp(h, h.lines[w]) == max(h.line_mvp(h.lines[w]), MG.LINKED_MVP) >= MG.LINKED_MVP


def test_people_density_reads_the_ladder(faketz):
    """PW-1275: a people's density per cell is its kind factor x the ladder's rung for the way it lives there: foragers on the NPP to
    the 1.3, farmers once they know cultivation on farmable land (the land decides, Q2 A), a poorer world fewer; no world, a number."""
    from planet.lineages import ladder as LA
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"parents": ["stem"], "at": "1 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "hunt", **base, "way": "forager", "traits": ["hunter"]}, {"id": "farm", **base, "way": "farmer", "kind": 1.2},
        {"id": "den", **base, "traits": ["denning"]}]}
    h0 = H.History(SP.parse(raw), ps, 1)
    assert h0._dmap is None and np.ndim(h0.dens_at(h0.idx["hunt"])) == 0 and h0.dens[h0.idx["hunt"]] == pytest.approx(LA.FORAGER)
    n = ps.grid.n
    rng = np.random.default_rng(3)
    ps.graze_npp = rng.uniform(0.1, 2.0, n) * LA.GRAZE_REF
    ps.npp = rng.uniform(0.1, 2.0, n) * LA.NPP_REF
    goods = {"fertile": rng.uniform(0, 1, n), "grazing": rng.uniform(0, 1, n), "fish": np.zeros(n)}
    h = H.History(SP.parse(raw), ps, 1, goods=goods)
    lad = h.ladder
    assert lad.ok and lad.den[h.idx["den"]] and not lad.den[h.idx["hunt"]]
    hu, fa = h.idx["hunt"], h.idx["farm"]
    d, sf, sh, rung, *_ = lad.line(hu, (False, False, -1.0, -1.0), None)
    assert np.allclose(d, LA.FORAGER * (ps.npp / LA.NPP_REF) ** LA.FORAGER_POW) and not sf.any() and (rung == 0).all()
    d2, sf2, _, rung2, *_ = lad.line(fa, (True, False, -1.0, -1.0), None)  # (gardens where the land is farmable, foraging elsewhere)
    farmable = np.clip(goods["fertile"] / LA.FARM_FULL, 0, 1)
    assert np.allclose(sf2, farmable) and np.allclose(d2, farmable * LA.GARDEN * ps.npp / LA.NPP_REF + (1 - farmable) * d)
    d3, *_ = lad.line(fa, (True, False, 2.0, -1.0), None)  # (the medieval plough, never above its top)
    assert d3.max() <= LA.PLOUGH_TOP + 1e-9 and (d3 >= d2 - 1e-9).all()
    dd, sfd, *_ = lad.line(h.idx["den"], (True, False, -1.0, -1.0), np.full(n, LA.RAID_HALF))  # (dens: farm rarely, raid to the cap)
    assert np.allclose(sfd, LA.DEN_FARM_W * farmable)
    lad.refresh(1.0, False, force=True)
    assert np.allclose(h._dmap[fa], 1.2 * lad.line(fa, lad.state[fa], None)[0])  # (x the kind factor)


def test_rich_wild_land_resists_farming(faketz):
    """PW-1385 A: where the wild feeds far more than the land's ordinary foraging (rich waters), a people knowing crops farms only
    part of the farmable land, more of it the longer it has known crops; ordinary land farms in full. Herding goes
    where it feeds more than the wild."""
    from planet.lineages import ladder as LA
    assert np.allclose(LA.rich_keep(np.ones(3), -1.0), 1.0)  # (ordinary land: all farmed)
    r = np.array([1.0 + LA.RICH_HALF, 1.0 + 3 * LA.RICH_HALF])
    k0, k2 = LA.rich_keep(r, -1.0), LA.rich_keep(r, 2.0)
    assert k0[0] == pytest.approx(0.5) and k0[1] < k0[0] and (k2 > k0).all()  # (half at the half point; more farmed with time)
    assert LA.herd_keep(np.array([1.0]), np.array([1.0]))[0] == pytest.approx(0.5)
    assert LA.herd_keep(np.array([1.0]), np.array([0.01]))[0] > 0.99
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"parents": ["stem"], "at": "1 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "farm", **base, "way": "farmer"}]}
    n = ps.grid.n
    ps.graze_npp = np.full(n, LA.GRAZE_REF)
    ps.npp = np.full(n, LA.NPP_REF)
    fish = np.where(np.arange(n) % 2 == 0, 0.0, 1.0)  # (every other cell on the richest waters)
    h = H.History(SP.parse(raw), ps, 1, goods={"fertile": np.ones(n), "grazing": np.zeros(n), "fish": fish})
    _, sf, *_ = h.ladder.line(h.idx["farm"], (True, False, -1.0, -1.0), None)
    assert np.allclose(sf[fish == 0], 1.0) and (sf[fish == 1] < 0.5).all()


def test_foragers_trade_with_farmer_neighbours(faketz):
    """PW-1386: a forager people near farmers gets a share of its foraging food from them, rising with the farmers' density within reach
    (half the cap at BARTER_HALF) and never reaching BARTER_CAP; none with no farmers near; farming, den and fishing-led cells keep their own."""
    from planet.lineages import ladder as LA
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"parents": ["stem"], "at": "1 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "hunt", **base, "way": "forager", "traits": ["hunter"]}, {"id": "farm", **base, "way": "farmer"},
        {"id": "den", **base, "traits": ["denning"]}]}
    n = ps.grid.n
    ps.graze_npp = np.full(n, LA.GRAZE_REF)
    ps.npp = np.full(n, LA.NPP_REF)
    fish = np.where(np.arange(n) % 2 == 0, 0.0, 1.0)  # (every other cell on the richest waters: fishing leads there)
    h = H.History(SP.parse(raw), ps, 1, goods={"fertile": np.ones(n), "grazing": np.zeros(n), "fish": fish})
    lad, hu, fa, dn = h.ladder, h.idx["hunt"], h.idx["farm"], h.idx["den"]
    t = (False, False, -1.0, -1.0, 0.0)
    d0, *_, b0 = lad.line(hu, t, None)
    dz, *_, bz = lad.line(hu, t, np.zeros(n), np.zeros(n))
    assert b0 is None and np.array_equal(d0, dz) and not bz.any()  # (no farmers near: as before, to the bit)
    land = fish == 0
    dh, *_, bh = lad.line(hu, t, None, np.full(n, LA.BARTER_HALF))
    assert np.allclose(dh[land], d0[land] / (1 - LA.BARTER_CAP / 2)) and np.allclose(bh[land], LA.BARTER_CAP / 2)
    assert np.array_equal(dh[~land], d0[~land]) and not bh[~land].any()  # (the fishers' richer waters are their own)
    dx, *_, bx = lad.line(hu, t, None, np.full(n, 1e4))
    assert (bx[land] < LA.BARTER_CAP).all() and (bx[land] > 0.99 * LA.BARTER_CAP).all() and (dx[land] > dh[land]).all()
    tc = (True, False, -1.0, -1.0, 0.0)  # (a people that knows crops, and a den people, do not barter)
    assert not lad.barters(fa, tc) and not lad.barters(dn, t) and lad.barters(hu, t)
    df, *_, bf = lad.line(fa, tc, None, np.full(n, 1e4))
    assert bf is None and np.array_equal(df, lad.line(fa, tc, None)[0])
    assert lad.line(dn, t, None, np.full(n, 1e4))[-1] is None
    assert not lad.farmers_near().any()  # (nobody present yet: no farmers near)


def test_den_people_keeps_its_raid_share_between_refreshes(faketz):
    """PW-1407: a den people whose tech moves between the ladder's full refreshes is redone with the settled-near map of the last full
    refresh, so its raiding share stays (it used to drop to nothing until the next full refresh)."""
    from planet.lineages import ladder as LA
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"parents": ["stem"], "at": "1 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "farm", **base, "way": "farmer"}, {"id": "den", **base, "traits": ["denning"]}]}
    n = ps.grid.n
    ps.graze_npp = np.full(n, LA.GRAZE_REF)
    ps.npp = np.full(n, LA.NPP_REF)
    h = H.History(SP.parse(raw), ps, 1, goods={"fertile": np.ones(n), "grazing": np.ones(n), "fish": np.zeros(n)})
    lad, fa, dn = h.ladder, h.idx["farm"], h.idx["den"]
    h.p = np.zeros((len(h.lines), n))
    h.p[fa] = 10 * LA.EST  # (farmers everywhere: raiders have something to raid)
    lad.tech = lambda k, ago: (True, False, -1.0, -1.0, 0.0) if k == fa else (False, False, -1.0, -1.0, 0.0)
    lad.refresh(1.0, False, force=True)
    lad.refresh(1.0, False, force=True)  # (the first fills the farmers' shares and densities, the second reads them)
    raid0, dmap0 = lad.raid[dn].copy(), h._dmap[dn].copy()
    assert (raid0 > 0).all()
    t_new = (False, True, -1.0, -1.0, 0.0)  # (the den people learns herding between two full refreshes)
    lad.tech = lambda k, ago: t_new if k == dn else (True, False, -1.0, -1.0, 0.0)
    lad.refresh(1.0 - LA.REFRESH_KYR / 2, False)  # (not due: only the den line is redone)
    assert lad.state[dn] == t_new and np.array_equal(lad.raid[dn], raid0)
    d, *_ = lad.line(dn, t_new, lad._sn)
    assert np.allclose(h._dmap[dn], h.kx[dn] * d * lad.thin[dn]) and not np.allclose(h._dmap[dn], dmap0)
    assert np.allclose(lad.line(dn, t_new, None)[0], lad.line(dn, t_new, lad._sn)[0]) is False  # (the raids do change the density)


def test_published_ranges_are_optional_seeded_draws(faketz):
    """PW-1383: meta.draw_ranges draws the ladder's sourced numbers from their published ranges (ranges.py), seeded by the peoples
    seed. Off (the default): the fixed constants and the very same densities. On: inside the ranges, the same for a seed, others differ."""
    from planet.lineages import ladder as LA, ranges as RG
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    n = ps.grid.n
    rng = np.random.default_rng(3)
    ps.graze_npp = rng.uniform(0.1, 2.0, n) * LA.GRAZE_REF
    ps.npp = rng.uniform(0.1, 2.0, n) * LA.NPP_REF
    goods = {"fertile": rng.uniform(0, 1, n), "grazing": rng.uniform(0, 1, n), "fish": rng.uniform(0, 1, n)}
    base = {"parents": ["stem"], "at": "1 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}

    def build(seed, on):
        raw = {"meta": {"seed": seed, **({"draw_ranges": True} if on else {})}, "lineage": [
            {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
            {"id": "farm", **base, "way": "farmer"}]}
        return H.History(SP.parse(raw), ps, 1, goods=goods)

    def dens(h):
        return [h.ladder.line(h.idx["farm"], t, None)[0] for t in ((True, True, -1.0, -1.0, 2.0), (True, True, 2.0, 1.0, 5.0))]

    off, off2, on7, on7b, on8 = build(7, False), build(7, False), build(7, True), build(7, True), build(8, True)
    assert off.ladder.drawn == {} and off.ladder.v == {"forager_pow": LA.FORAGER_POW, "fish_top": LA.FISH_TOP, "garden": LA.GARDEN,
                                                       "plough": tuple(LA.PLOUGH), "nomad": LA.NOMAD, "rich_t": LA.RICH_T}
    assert all(np.array_equal(a, b) for a, b in zip(dens(off), dens(off2)))
    d = on7.ladder.drawn
    assert set(d) == set(RG.RANGES) and all(r.lo <= d[k] <= r.hi for k, r in RG.RANGES.items())
    assert on7.ladder.v["plough"] == (d["plough_0"], d["plough_1"], d["plough_2"]) and d["plough_0"] < d["plough_1"] < d["plough_2"]
    assert on7.ladder.drawn == on7b.ladder.drawn and all(np.array_equal(a, b) for a, b in zip(dens(on7), dens(on7b)))
    assert on8.ladder.drawn != d
    assert not all(np.array_equal(a, b) for a, b in zip(dens(on7), dens(off)))
    raw = _raw()
    raw["meta"]["draw_ranges"] = True
    h2, res2, pres2 = H.simulate(SP.parse(raw), ps, tries=1)
    run2 = json.loads((O.save(h2, res2, pres2, name="test draws") / "run.json").read_text())  # (the run says which numbers it drew)
    assert run2["meta"]["draw_ranges"] is True and run2["meta"]["tree"]["meta"]["draw_ranges"] is True
    assert run2["meta"]["range_draws"] == {k: round(x, 6) for k, x in RG.draw(2).items()}  # (the tree's seed is 2)
    seeds = [RG.draw(s) for s in range(40)]  # (every name moves across seeds, and stays in range)
    assert all(len({round(x[k], 9) for x in seeds}) > 30 for k in RG.RANGES)
    assert all(r.lo <= x[k] <= r.hi for x in seeds for k, r in RG.RANGES.items())


def test_nomads_and_settled_compete_less(faketz):
    """Owner on PW-936: a nomadic people and a settled one share country more readily (spec.WAY_MOBILE, NOMAD_COEXIST),
    both ways; two herding peoples still compete in full."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    base = {"parents": ["stem"], "at": "1 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "farm", **base, "way": "farmer"}, {"id": "herd", **base, "way": "pastoral_nomad"},
        {"id": "herd2", **base, "way": "pastoral_nomad"}, {"id": "farm2", **base, "way": "farmer"}]}
    h = H.History(SP.parse(raw), ps, 1)
    raw2 = {**raw, "lineage": [{**l, "way": "farmer"} if "way" in l else l for l in raw["lineage"]]}
    h0 = H.History(SP.parse(raw2), ps, 1)
    f, n, n2, f2 = (h.idx[x] for x in ("farm", "herd", "herd2", "farm2"))
    for x, y in ((f, n), (n, f)):
        assert np.isclose(h.alpha[x, y], h0.alpha[x, y] * (1 - SP.NOMAD_COEXIST)) and h0.alpha[x, y] > 0
    assert np.isclose(h.alpha[n, n2], h0.alpha[n, n2]) and np.isclose(h.alpha[f, f2], h0.alpha[f, f2])


# ---- PW-965: the sapiens node and the "continues as animals" end of a stem ------------------------------------------------


def _stem_raw(**kw) -> dict:
    return {"meta": {"name": "t"}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", **kw},
        {"id": "a", "parents": ["stem"], "at": "2 Myr"},
        {"id": "b", "parents": ["stem"], "at": "1 Myr"}]}


def test_sapiens_node_and_animal_end_parse_and_round_trip():
    from planet.lineages import spec as SP
    t = SP.parse(_stem_raw(sapient="4 Myr", animals=True))
    assert t.lines["stem"].sapient_kyr == 4000 and t.lines["stem"].animals_end
    assert t.lines["a"].sapient_kyr is None and not t.lines["a"].animals_end  # (not inherited by the kinds)
    t2 = SP.parse(SP.to_raw(t))
    assert t2.lines["stem"].sapient_kyr == 4000 and t2.lines["stem"].animals_end


def test_sapiens_node_and_animal_end_validation():
    from planet.lineages import spec as SP
    with pytest.raises(ValueError, match="before its kinds split"):
        SP.parse(_stem_raw(sapient="1.5 Myr"))
    with pytest.raises(ValueError, match="sapient"):
        SP.parse(_stem_raw(sapient="12 Myr"))
    with pytest.raises(ValueError, match="animals = true"):
        SP.parse(_stem_raw(animals=True, persists=True))
    with pytest.raises(ValueError, match="animals = true"):
        SP.parse(_stem_raw(animals=True, extinct="1 Myr"))


def test_animal_end_changes_no_simulated_line():
    """The marker is not simulated: the same tree with and without it has the same lines, ends and techs-eligible peoples."""
    from planet.lineages import spec as SP
    a, b = SP.parse(_stem_raw()), SP.parse(_stem_raw(sapient="4 Myr", animals=True))
    assert [(l.id, l.ago_kyr, l.extinct_kyr, l.persists, l.megafauna, l.children) for l in a.order()] == \
        [(l.id, l.ago_kyr, l.extinct_kyr, l.persists, l.megafauna, l.children) for l in b.order()]
    assert [l.id for l in a.leaves()] == [l.id for l in b.leaves()]  # (the stem still ends at its last split)


def test_samples_dragons_have_one_node_and_animal_end():
    from planet.lineages import spec as SP
    for f in ("dnd", "seven_meals"):
        t = SP.load(f"planet/lineages/samples/{f}.toml")
        d = t.lines["draconic"]
        assert d.animals_end and d.sapient_kyr is not None and 2500 < d.sapient_kyr < d.ago_kyr  # before the chromatic/metallic split
        assert not any(t.lines[i].sapient_kyr or t.lines[i].animals_end for i in ("chromatic_dragon", "metallic_dragon", "red_dragon"))
        assert d not in t.leaves()  # (the animals are no line of the tree: nothing for peoples, techs or megafauna to count)


# ---- lane 78: life stages (PW-1148, PW-1147), portals in force (PW-1150) and wandering --------------------------------
def test_life_tables_give_canon_paced_generations_and_rates():
    from planet.lineages import life_history as LH
    hu = LH.table(*LH.HUMAN)
    f = hu["by_era"]["forager"]
    assert hu["stage_end"] == [1.0, 18.0, 45.0, 80.0]
    assert 26 < f["T"] < 30 and abs(f["R0"] - 3.5) < 0.01 and 0.5 < f["adult_share"] < 0.6  # (Gurven & Kaplan's l15 0.57)
    # a gentler schedule (fewer children die) raises r; the schedules are Gurven & Kaplan's rows
    assert hu["by_era"]["horticulturalist"]["r"] > f["r"]
    kob = LH.table(6, 120, "brood", None, "harsh")["by_era"]["forager"]
    elf = LH.table(100, 750, "slow", (100, 200))["by_era"]["forager"]
    dw = LH.table(50, 350, "mammal", (50, 100))["by_era"]["forager"]
    rh = LH.r_human()
    assert kob["r"] / rh > 2 and kob["adult_share"] < 0.3  # brood breeders, harsh survival
    assert elf["r"] / rh < 0.2 and 120 < elf["T"] < 170 and 0.3 < dw["r"] / rh < 0.5
    with pytest.raises(ValueError):
        LH.table(10, 50, "eggs")


def test_life_history_and_arrival_fields_parse_inherit_and_round_trip():
    raw = _mode_raw(portal_mode="wandering", portals=3, growth_rates=True, wave_kyr=1.5)
    rows = {r["id"]: r for r in raw["lineage"]}
    rows["stem"].update(adult_yr=12, lifespan_yr=50, breeding="brood", survival="harsh")
    rows["elf"].update(adult_yr=100, lifespan_yr=750, breeding="slow", fertile_yr=[100, 200], founders=1e6, waves=3, portals=2,
                       plane="feywild")
    t = SP.parse(raw)
    assert t.lines["human"].adult_yr == 12 and t.lines["human"].breeding == "brood"  # (a split inherits its life history)
    e = t.lines["elf"]
    assert (e.founders, e.waves, e.portal_n, e.plane, e.fertile_yr) == (1e6, 3, 2, "feywild", (100.0, 200.0))
    assert t.growth_rates and t.portal_mode == "wandering" and t.wave_kyr == 1.5
    b = SP.parse(SP.to_raw(t))
    assert (b.lines["elf"].founders, b.lines["elf"].plane, b.lines["stem"].breeding, b.growth_rates) == (1e6, "feywild", "brood", True)
    from planet.lineages import life_history as LH
    assert abs(LH.generation_yr(e) - LH.table(100, 750, "slow", (100, 200))["by_era"]["forager"]["T"]) < 1e-9
    for who, bad in (("elf", {"founders": 0}), ("ork", {"adult_yr": 10})):
        r2 = _mode_raw()
        {x["id"]: x for x in r2["lineage"]}[who].update(bad)
        with pytest.raises(ValueError):
            SP.parse(r2)
    r2 = _mode_raw()  # (an arrival's fields left on a row whose origin changed, as the workbench leaves them: ignored, not refused)
    {x["id"]: x for x in r2["lineage"]}["ork"].update(founders=10, waves=2, portals=2, plane="feywild")
    o = SP.parse(r2).lines["ork"]
    assert (o.founders, o.waves, o.portal_n, o.plane) == (None, 1, None, "beyond")


def test_an_arrival_in_force_founds_its_people_at_several_portals_in_waves(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = _mode_raw(portal_mode="random", portals=3, wave_kyr=1.0)
    {x["id"]: x for x in raw["lineage"]}["elf"].update(founders=2e6, waves=2)
    h = H.History(SP.parse(raw), ps, 1)
    h.dens[[i for i, l in enumerate(h.lines) if not l.megafauna]] = 5.0 if 'farm' in h.idx else 2.0  # (PW-1275: no world, no ladder: the number the test needs)
    h.run()
    log = h.wave_log["elf"]
    assert len(log) == 2 and log[0]["portals"] >= 2 and log[0]["people"] == 1e6
    assert log[0]["carried"] >= 0.9e6  # (each portal's share founded in full)
    assert any(e["kind"] == "wave" for e in h.events)


def test_wandering_thinnings_drift_open_and_close(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = _mode_raw(portal_mode="wandering", portals=2, portal_open_kyr=3, portal_drift_kmkyr=300)
    h = H.History(SP.parse(raw), ps, 1)
    h.run()
    assert h.started.get("elf") is not None
    log = h.portal_report()["beyond"]
    assert any("opened_kyr" in x for x in log) and any("closed_kyr" in x for x in log)
    P = h._planes["beyond"]
    t = {"pos": P["thin"][0]["pos"], "born": 10.0}
    a, b = h._thin_cell(P, t, 10.0), h._thin_cell(P, t, 0.0)
    d = np.arccos(np.clip(h.grid.centers[a] @ h.grid.centers[b], -1, 1)) * H.R_KM
    assert d < 3000 + 2 * h.cell_km  # (300 km/kyr x 10 kyr along a small circle about the pole: at most 3000 km)
    assert h.portal_cells() == []


def test_growth_rates_off_by_default_and_x_one_without_canon_ages(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = _mode_raw(growth_rates=True)
    {x["id"]: x for x in raw["lineage"]}["ork"].update(adult_yr=12, lifespan_yr=50)
    h = H.History(SP.parse(raw), ps, 1)
    h.run()
    assert h.growth_x(h.idx["human"]) == 1.0 and h.growth_x(h.idx["ork"]) > 1.3
    assert set(h.life_eras["ork"]) <= {"forager", "horticulturalist", "agrarian"}
    h2 = H.History(SP.parse(_mode_raw()), ps, 1)
    h2.run()
    assert h2.growth_x(h2.idx["human"]) == 1.0


def test_fit_decides_the_contest_and_martial_peoples_press_harder(faketz):
    """Lane 83 (owner D20, PW-1180 A): where two peoples suit a cell alike, the narrower (the specialist) presses harder (breadth^-1/2);
    the one the cell suits better presses harder there; a martial people (spec contest) harder still; all within x FIT_CLIP."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 3}, "lineage": [
        {"id": "broad", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "narrow", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000], "contest": 1.5}]}
    tree = SP.parse(raw)
    assert tree.lines["narrow"].demo("contest") == 1.5 and tree.lines["broad"].demo("contest") == 1.0
    m = SP.parse({"lineage": [{"id": "m", "origin": "root", "at": "1 kyr", "traits": ["martial"]}]})
    assert m.lines["m"].demo("contest") == 1.5
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "z", "origin": "root", "at": "1 kyr", "contest": 0}]})
    h = H.History(tree, ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    n = h.grid.n
    b, s = h.idx["broad"], h.idx["narrow"]
    Kb, Ks = np.ones(n), np.where(np.arange(n) < n // 4, 1.0, 0.0)
    h._note_K(b, Kb)
    h._note_K(s, Ks)
    idx = np.arange(n // 4)
    assert (h._fit_w(s, Ks, np.array([b]), idx) < 1).all() and (h._fit_w(b, Kb, np.array([s]), idx) > 1).all()
    narrow_on_broad = h._fit_w(b, Kb, np.array([s]), idx)[0, 0]
    assert narrow_on_broad == pytest.approx(min(H.FIT_CLIP, 1.5 * np.sqrt(n / (n // 4))))
    h._martial[s] = 1.0
    assert h._fit_w(b, Kb, np.array([s]), idx)[0, 0] == pytest.approx(np.sqrt(n / (n // 4)))
    h._note_K(s, 0.5 * Ks)  # (the cells suit it half as well: it presses half as hard there, its breadth halved too)
    assert h._fit_w(b, Kb, np.array([s]), idx)[0, 0] == pytest.approx(0.5 * np.sqrt(n / (0.5 * (n // 4))))


def test_den_peoples_prefer_den_ground_but_live_on_poor_ground(faketz):
    """PW-1382 (Daniel 11-02: prefer den ground, never rely on it): a denning people's habitat is a plain people's everywhere; its
    density is x1 on the best den ground and keeps half (1 - the trait's den) where the land has no caves, shelters or ground to dig,
    never zero; other peoples do not read the den ground. dens.fitness: karst best, plain ground with nothing to dig 0."""
    from planet.lineages import dens as DN
    from planet.lineages import ladder as LA
    from planet import surface as SU
    from planet.landform import HILLS, KARST
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    env = ps.fields(0.0, variability=False)
    tags = H._tags(ps.grid, env)
    plain = SP.Lineage("p", temp_c=(-20, 40), rain_mm=(1, 9000))
    den = SP.Lineage("d", temp_c=(-20, 40), rain_mm=(1, 9000), traits=["denning"])
    assert np.allclose(H.capacity(den, env, tags), H.capacity(plain, env, tags))  # (the habitat: never cut)
    lay = {"surface_rock": np.array([SU.LIMESTONE, SU.SHALE, SU.GRANITE, SU.SHALE]), "landform": np.array([KARST, HILLS, HILLS, HILLS]),
           "loess": np.array([0.0, 0.0, 0.0, 5.0])}
    f = lambda k: np.asarray(lay[k], float) if k in lay else np.zeros(4)  # noqa: E731
    fit = DN.fitness(f, np.array([0.0, 0.0, 9.0, 0.0]), np.zeros(4), np.ones(4, bool))
    assert fit[0] == pytest.approx(DN.KARST) and fit[1] == 0.0 and fit[2] == pytest.approx(DN.SHELTER_OTHER)
    assert fit[3] == pytest.approx(DN.LOESS_X)
    base = {"parents": ["stem"], "at": "1 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "hunt", **base, "way": "forager"}, {"id": "den", **base, "traits": ["denning"]}]}
    n = ps.grid.n
    ps.graze_npp, ps.npp = np.full(n, LA.GRAZE_REF), np.full(n, LA.NPP_REF)
    fit = np.where(np.arange(n) % 2 == 0, 0.0, 1.0)  # (every other cell the best den ground, the rest none)
    h = H.History(SP.parse(raw), ps, 1, goods={"fertile": np.zeros(n), "grazing": np.zeros(n), "fish": np.zeros(n), "den": fit})
    th = h.ladder.thin[h.idx["den"]]
    assert np.allclose(th[fit == 1], 1.0) and np.allclose(th[fit == 0], 1.0 - SP.TRAITS["denning"]["den"]) and th.min() >= 0.5
    assert np.allclose(h.ladder.thin[h.idx["hunt"]], 1.0)
    h.ladder.refresh(1.0, False, force=True)
    dd = h._dmap[h.idx["den"]]
    assert (dd[fit == 0] > 0).all() and np.allclose(dd[fit == 0], 0.5 * dd[fit == 1].mean())  # (poor den ground: half, never none)


def test_a_split_founds_by_its_parent_s_last_land(faketz):
    """PW-1184: a split whose parent holds nothing founds by the parent's last land (exp(-d / FOUNDER_KM)), not at its best
    habitat anywhere."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_raw()), ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    step = h.steps[-1]
    env = step.get()
    tags = H._tags(h.grid, env)
    g = h.grid
    a = h.tree.lines["a"]
    K = H.capacity(a, env, tags)
    last = tags["land"] & (g.lon > 100) & (g.lon < 140) & (np.abs(g.lat) < 20)
    far = tags["land"] & (np.abs(g.lon) < 50)
    assert last.any() and K[far].max() >= K[last].max() * 0.9
    assert h._origin_fallback(a, step, env, tags, K, "parent gone: near its last land", near=last)
    cell = h.origins["a"]["cell"]
    assert g.lon[cell] > 85  # (on the east continent, by the last land; the west one is as good but far)


def _mega_raw():
    """A worldwide flying megafauna stem (the dragons) with a walking people split from it (the kobolds)."""
    return {"meta": {"name": "t", "seed": 2}, "lineage": [
        {"id": "wyrm", "origin": "root", "at": "30 kyr", "megafauna": True, "explore": 0.3, "insularity": 0.85, "sea_share": 0.02,
         "temp_c": [-10, 40], "rain_mm": [50, 6000], "traits": ["flies", "insular"]},
        {"id": "kin", "parents": ["wyrm"], "at": "20 kyr", "temp_c": [5, 30], "rain_mm": [100, 5000], "traits": ["hardy"]},
        {"id": "wyrmling", "parents": ["wyrm"], "at": "15 kyr", "megafauna": True}]}


def test_a_people_of_a_megafauna_stem_takes_no_demography_from_it():
    """Lane 83b: the dragons' explore and insularity are a handful of solitary fliers' numbers, not a people's: a people split from a
    megafauna stem takes them from its own traits; a megafauna child still inherits them."""
    t = SP.parse(_mega_raw())
    assert t.lines["kin"].demos()["explore"] == SP.demography(["hardy"])["explore"]
    assert t.lines["kin"].demos()["insularity"] == SP.DEMO_DEFAULT["insularity"]
    assert t.lines["wyrmling"].demos()["insularity"] == 0.85 and t.lines["wyrmling"].demos()["explore"] == 0.3


def test_a_people_of_a_megafauna_stem_founds_where_its_own_country_lies(faketz):
    """Lane 83b: a split of a worldwide megafauna stem founds as an arrival settles: its landmass drawn by the founders its own country
    (free room) would carry, not by the stem's range; the stem's range at the spot is cleared, as for any one-spot split (D20)."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_mega_raw()), ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    h.active = {l.id: False for l in h.lines}
    step = h.steps[-1]
    env = step.get()
    tags = H._tags(h.grid, env)
    h._corr_now = None
    h.p[h.idx["wyrm"]][tags["land"]] = 0.5
    h.active["wyrm"] = True
    kin = h.tree.lines["kin"]
    K = H.capacity(kin, env, tags)
    cell, why = h._origin_split(kin, step, env, tags, K, np.ones(h.grid.n))
    assert "megafauna stem" in why and K[cell] > 0.3
    held = h.p[h.idx["kin"]] > 0
    assert held.any() and not (h.p[h.idx["wyrm"]][held] > 0).any()


def test_pioneers_and_jumps_count_megafauna_land_as_free(faketz):
    """Lane 83b: a cell only megafauna hold is free country to a people's pioneers and jumps (the dragons hardly take room from the
    peoples); to another megafauna kind it is taken, as before."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_mega_raw()), ps, 1)
    L = h.lines
    h.p = np.zeros((len(L), h.grid.n))
    h._native = np.arange(len(L))
    h._nat_set = set(range(len(L)))
    h._ppl_set = {i for i in h._nat_set if not L[i].megafauna}
    h.p[h.idx["wyrm"]][:10] = 1.0
    h._pm = h.p >= 0.12
    h._cnt = h._pm.sum(0, dtype=np.int16)
    h._cntp = h._pm[sorted(h._ppl_set)].sum(0, dtype=np.int16)
    assert (h._taken_cnt(h.tree.lines["kin"])[:10] == 0).all()
    assert (h._taken_cnt(h.tree.lines["wyrmling"])[:10] == 1).all()
    h.p[h.idx["kin"]][5:15] = 1.0
    h._sync(h.idx["kin"])
    assert (h._cntp[5:15] == 1).all() and (h._cnt[5:10] == 2).all()


def test_a_people_that_filled_its_patch_pushes_founders_out(faketz):
    """Lane 83b (PW-920): a hemmed-in people sends out founders when rivals crowd it or when it has filled the land it holds; a narrow
    people alone on its patch of country used to have no push at all."""
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_raw()), ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    k = h.idx["a"]
    K = np.full(h.grid.n, 0.8)
    held = np.zeros(h.grid.n, bool)
    held[:20] = True
    h.p[k][held] = 0.8
    assert h._jump_push(k, K, K.copy(), held) == pytest.approx(1.0)  # (filled, no rival: full push)
    h.p[k][held] = 0.2
    assert h._jump_push(k, K, K.copy(), held) == pytest.approx(0.25)  # (a quarter filled)
    room = np.full(h.grid.n, 0.2)
    assert h._jump_push(k, K, room, held) == pytest.approx(1.0)  # (crowded to its room by rivals)


def test_a_new_people_is_founded_at_a_few_sites_spread_over_one_landmass(faketz, monkeypatch):
    """Lane 97 (owner D27): a root or a split is founded at FOUND_SITES seed sites on its origin's landmass, within FOUND_SPREAD jump
    lengths of the first and clear of each other, the founders' area shared among them; with one site, the one blob of before."""
    from planet.lineages.history import params as PM
    from planet.lineages.gridops import dist_km
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_raw()), ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    env = h.steps[-1].get()
    g, k, line = h.grid, h.idx["a"], h.tree.lines["a"]
    K = np.where(env["land"], 0.8, 0.0)
    cell = int(np.flatnonzero(env["land"] & (np.abs(g.lon) < 15) & (np.abs(g.lat) < 15))[0])
    monkeypatch.setattr(PM, "FOUND_SPREAD", 6.0)  # (the test grid's cells are ~1,000 km: a spread of a few cells)
    blob, sites = h._found_spread(line, k, cell, K.copy(), K, K > 0.12, 2, env)
    assert len(sites) == PM.FOUND_SITES == 3 and sites[0] == cell
    ll, _ = g.components(env["land"])
    d0 = dist_km(g, float(g.lat[cell]), float(g.lon[cell]))
    assert all(ll[c] == ll[cell] for c in sites) and all(d0[c] <= PM.FOUND_SPREAD * PM.JUMP_KM for c in sites)
    assert min(dist_km(g, float(g.lat[a]), float(g.lon[a]))[b] for a in sites for b in sites if a != b) > 2 * h.cell_km
    h.p[k][:] = 0
    one = h._seed_blob(k, cell, K, K > 0.12, 2).sum()
    assert 0.3 * one <= blob.sum() <= 1.5 * one  # (the founders' area shared among the sites, about as before)
    monkeypatch.setattr(PM, "FOUND_SITES", 1)
    h.p[k][:] = 0
    blob1, sites1 = h._found_spread(line, k, cell, K.copy(), K, K > 0.12, 2, env)
    assert sites1 == [cell] and blob1.sum() == one




def _raider_raw():
    return {"meta": {"name": "r", "seed": 2, "mixing_start": "3 kyr"}, "lineage": [
        {"id": "stem", "origin": "root", "at": "30 kyr", "temp_c": [5, 30], "rain_mm": [100, 5000]},
        {"id": "kob", "parents": ["stem"], "at": "20 kyr", "adult_yr": 6, "lifespan_yr": 120, "breeding": "brood", "survival": "harsh"},
        {"id": "folk", "parents": ["stem"], "at": "20 kyr", "adult_yr": 18, "lifespan_yr": 80},
        {"id": "dw", "parents": ["stem"], "at": "20 kyr"},
        {"id": "hill", "origin": "group", "parents": ["dw"], "at": "10 kyr"},
        {"id": "mix", "origin": "hybrid", "parents": ["dw", "folk"], "at": "8 kyr"}],
        "wish": [{"a": "folk", "b": "kob", "want": "apart", "weight": 1.0}]}


def test_raid_losses_scale_a_raiders_canon_losses_only():
    """Lane 97 (D25 B, lane 85's table): R x the harsh excess; kobold-like lines keep 0.65 / 0.31 at R 1.5 / 2, normal survival 1."""
    from planet.lineages import life_history as LH
    t = SP.parse(_raider_raw())
    kob, folk = t.lines["kob"], t.lines["folk"]
    assert kob.raids and not folk.raids
    assert LH.harsh_kept(kob, "forager", 1.0) == 1.0 and LH.harsh_kept(kob, "forager", 0.7) == 1.0
    assert LH.harsh_kept(kob, "forager", 1.5) == pytest.approx(0.65, abs=0.02)
    assert LH.harsh_kept(kob, "forager", 2.0) == pytest.approx(0.31, abs=0.02)
    assert LH.harsh_kept(folk, "forager", 2.0) == 1.0


def test_the_brakes_cut_a_raider_on_a_hostile_border_and_when_hemmed_in(faketz):
    """Lane 97 (D25): on a border with a people that hates it a raider keeps less of its habitat than at home; hemmed in (no free
    country next door) it loses more to in-fighting; a people of normal survival has no raid or in-fighting loss; meta.raiders 0: off."""
    import types
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_raider_raw()), ps, 1)
    g, L = h.grid, h.lines
    h.p = np.zeros((len(L), g.n))
    h.active = {l.id: True for l in L}
    h.crops = None
    h._growth_setup()
    h._counter_setup()
    env = h.steps[-1].get()
    h._land_now = env["land"]
    kb, fk = h.idx["kob"], h.idx["folk"]
    land = np.flatnonzero(env["land"])
    h.p[kb][land[:200]] = 0.8
    h.p[fk][land[180:400]] = 0.8
    h._pm = h.p >= 0.12
    h._cntp = h._pm.sum(0, dtype=np.int16)
    h._deep_now = False
    step = types.SimpleNamespace(epoch="recent", ago=1.0, dt=0.1)
    K = np.where(env["land"], 0.8, 0.0)
    assert h.rule.hostility[kb, fk] == pytest.approx(1.0) and h.rule.hostility[kb, h.idx["dw"]] == 0.0
    h.rule.hem[kb] = 0.0
    Kb = h._brake(L[kb], kb, K, step, env, None)
    F = h.rule.frontier(kb)
    border, home = int(np.argmax(np.where(h._pm[kb], F, -1))), int(np.argmin(np.where(h._pm[kb], F, 9)))
    assert F[border] > 0.3 and F[home] == 0.0
    assert Kb[border] < Kb[home] <= K[home] + 1e-12
    h.rule.hem[kb] = 1.0
    Kh = h._brake(L[kb], kb, K, step, env, None)
    assert Kh[home] / K[home] <= 0.66  # (R 1.5 from in-fighting alone: 0.65, and a little war-torn land)
    assert set(h.lost["kob"]) >= {"raid", "feud"} and h.lost["kob"]["feud"] > 0
    Kf = h._brake(L[fk], fk, K, step, env, None)
    assert "raid" not in h.lost.get("folk", {}) and np.all(Kf <= K + 1e-12)
    h.tree.raiders, h.tree.war = 0.0, 0.0
    assert np.array_equal(h._brake(L[kb], kb, K, step, env, None), K)


def _brake_setup(faketz):
    import types
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(_raider_raw()), ps, 1)
    g, L = h.grid, h.lines
    h.p = np.zeros((len(L), g.n))
    h.active = {l.id: True for l in L}
    h.crops = None
    h._growth_setup()
    h._counter_setup()
    env = h.steps[-1].get()
    h._land_now = env["land"]
    h._deep_now = False
    step = types.SimpleNamespace(epoch="recent", ago=1.0, dt=0.1)
    return h, env, step


def _sync_pm(h):
    h._pm = h.p >= 0.12
    h._cntp = h._pm.sum(0, dtype=np.int16)
    h._cnt = h._cntp
    h.rule._Fc = None


def test_in_fighting_rises_with_a_peoples_own_fill_and_circumscription(faketz):
    """Lane 101 (PW-1240 B, owner D31): every people fights itself, humans too, more as it fills its land (a thinly spread people
    fights less) and as it is circumscribed: free good country next door bars nothing, others' land bars SOCIAL_Q, unlivable country
    fully. meta.war 0 switches it off."""
    from planet.lineages.history import params as HP
    h, env, step = _brake_setup(faketz)
    L = h.lines
    kb, fk = h.idx["kob"], h.idx["folk"]
    land = np.flatnonzero(env["land"])
    K = np.where(env["land"], 0.8, 0.0)
    h.tree.raiders = 0.0
    for k in (kb, fk):  # (a raider and a people of normal survival alike)
        h.p[:] = 0.0
        h.p[k][land[:200]] = 0.8
        _sync_pm(h)
        h.rule.hem[k] = 1.0
        full = h._brake(L[k], k, K, step, env, None)
        h.p[k][land[:200]] = 0.2  # (the same land, a fifth as full: Chagnon's village before it grows to splitting size)
        thin = h._brake(L[k], k, K, step, env, None)
        c = land[10]
        assert thin[c] > full[c]
        assert full[c] / K[c] == pytest.approx(1.0 - HP.FEUD_CUT, abs=0.02)  # (full and fully circumscribed; a little war-torn land)
        assert h.lost[L[k].id]["feud"] > 0
    h.tree.war = 0.0
    assert np.array_equal(h._brake(L[fk], fk, K, step, env, None), K)  # (war and raiders off: no brakes at all)
    h.p[:] = 0.0
    h.p[kb][land[:50]] = 0.8
    _sync_pm(h)
    room = K.copy()
    h.rule.K0[kb] = K
    held = h.p[kb] >= 0.12
    open_c = h.rule.circumscribed(L[kb], kb, held, room, 0.0)
    ring = h._dilate(held, 1) & ~held & env["land"]
    h.p[fk][ring] = 0.8
    _sync_pm(h)
    ringed = h.rule.circumscribed(L[kb], kb, held, room, 0.0)
    assert open_c < ringed <= HP.SOCIAL_Q + (1 - HP.SOCIAL_Q) * float((~env["land"][h._dilate(held, 1) & ~held]).mean()) + 1e-9


def test_polities_swap_the_state_and_war_stand_ins_through_one_seam(faketz, monkeypatch):
    """PW-1280: the brakes read a state's pacification G, the hostile frontier F and in-fighting's circumscription C only through
    History.rule (history.rule.StandIns). A replacement Rule that answers 'no hostile frontier, full pacification, never hemmed in'
    takes away the raid, frontier-war and in-fighting cuts without any other change to the history."""
    from planet.lineages.history import counter as CT
    from planet.lineages.history.rule import StandIns

    class Peace(StandIns):
        def frontier(self, k):
            return np.zeros(self.h.grid.n)

        def pacification(self, k, step):
            return 0.0

        def circumscription(self, k):
            return 0.0

    h, env, step = _brake_setup(faketz)
    L = h.lines
    kb, fk = h.idx["kob"], h.idx["folk"]
    land = np.flatnonzero(env["land"])
    K = np.where(env["land"], 0.8, 0.0)
    h.p[kb][land[:200]] = 0.8
    h.p[fk][land[180:400]] = 0.8
    _sync_pm(h)
    assert isinstance(h.rule, StandIns) and CT.CounterMixin.Rule is StandIns
    h.rule.hem[kb] = 1.0
    stand_in = h._brake(L[kb], kb, K, step, env, None)
    monkeypatch.setattr(type(h), "Rule", Peace)
    h._counter_setup()
    assert type(h.rule) is Peace
    _sync_pm(h)
    peace = h._brake(L[kb], kb, K, step, env, None)
    held = h._pm[kb]
    assert (stand_in[held] < peace[held]).any() and np.allclose(peace[held], K[held])  # (kobolds of normal canon losses: R 1)


def test_a_brake_never_takes_a_peoples_land_outright(faketz, monkeypatch):
    """Lane 101 (PW-1240): at the raiders' dial x4 a hemmed-in raider on a hostile border keeps at least BRAKE_HOLD of its habitat on
    every cell it holds (lane 97's 5% of K fell under the hold, EST 0.12, and the raiders died out); off its land the brakes still cut."""
    from planet.lineages.history import params as HP
    from planet.lineages.spread import EST
    h, env, step = _brake_setup(faketz)
    L = h.lines
    kb, fk = h.idx["kob"], h.idx["folk"]
    land = np.flatnonzero(env["land"])
    K = np.where(env["land"], 0.8, 0.0)
    h.p[kb][land[:200]] = 0.8
    h.p[fk][land[150:400]] = 0.8
    _sync_pm(h)
    h.rule.hem[kb] = 1.0
    h.tree.raiders = 4.0
    Kb = h._brake(L[kb], kb, K, step, env, None)
    held = h._pm[kb]
    assert np.all(Kb[held] >= min(HP.BRAKE_HOLD, 0.8) - 1e-12) and HP.BRAKE_HOLD > 2 * EST - 1e-12
    assert (Kb[held] < K[held]).any()
    monkeypatch.setattr(HP, "BRAKE_HOLD", 0.0)
    assert (h._brake(L[kb], kb, K, step, env, None)[held] < EST).any()  # (the old floor on K alone)


def test_a_cull_sawtooth_averages_the_same_for_any_growth_rate():
    """Lane 85's arithmetic (D25 C): d = 0.6 recovering to 0.1 before the next cull averages (0.6 - 0.1) / ln 6 = 0.28, whatever x."""
    from planet.lineages.history import params as PM
    D, A = PM.CULL_D, PM.CULL_AGAIN
    for tau in (17.0, 450.0):
        t = np.linspace(0, tau * np.log(D / A), 20001)
        assert np.mean(D * np.exp(-t / tau)) == pytest.approx((D - A) / np.log(D / A), rel=1e-3)
    assert (D - A) / np.log(D / A) == pytest.approx(0.28, abs=0.005)


def test_old_enemies_hunt_each_other_on_their_border_as_story_only(faketz, monkeypatch):
    """Lane 97 (D26 B): a pair the tree names as enemies ('apart') logs 'hunt' events at cells where their lands meet; a pair
    without that wish never does, and the hunts change nobody's numbers. (The apart wish itself keeps the two apart on the coarse
    test grid, so the lands are set by hand.)"""
    import types
    from planet.lineages.gridops import nbr_reduce
    from planet.lineages.history import params as HP
    raw = {"meta": {"seed": 1},
           "lineage": [{"id": "a", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "b", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
                       {"id": "c", "appears": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000]}],
           "wish": [{"a": "a", "b": "b", "want": "apart"}]}
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(SP.parse(raw), ps, 1)
    g = h.grid
    land = np.flatnonzero(ps.fields(0.0, variability=False)["land"])
    h.p = np.zeros((3, g.n))
    h.p[h.idx["a"]][land[:150]] = 0.8
    h.p[h.idx["b"]][land[150:300]] = 0.8
    h.p[h.idx["c"]][land[300:450]] = 0.8
    h.active = {"a": True, "b": True, "c": True}
    h._pm = h.p >= H.EST
    A, B = h._pm[h.idx["a"]], h._pm[h.idx["b"]]
    border = (A & nbr_reduce(g, np.logical_or, B[g.nbr_idx])) | (B & nbr_reduce(g, np.logical_or, A[g.nbr_idx]))
    assert border.any()
    P0 = h.p.copy()
    monkeypatch.setattr(HP, "HUNT_PER_KYR", 50.0)  # (a hunt every step)
    for i in range(20):
        h._hunts(types.SimpleNamespace(epoch="recent", ago=2.0 - 0.1 * i, dt=0.1))
    hunts = [e for e in h.events if e["kind"] == "hunt"]
    assert len(hunts) == 20 and {e["line"] for e in hunts} <= {"a", "b"}
    at = {(round(float(g.lat[c]), 2), round(float(g.lon[c]), 2)) for c in np.flatnonzero(border)}
    assert all((e["lat"], e["lon"]) in at for e in hunts)  # (on the border between the enemies)
    assert not any("c" in e["text"].split() for e in hunts)  # (c, with no enmity, is never in one)
    assert np.array_equal(h.p, P0)  # (story only: nobody's numbers change)
    h.events = []
    h._hunts(types.SimpleNamespace(epoch="deep", ago=30.0, dt=0.1))
    monkeypatch.setattr(HP, "HUNT_PER_KYR", 0.0)
    h._hunts(types.SimpleNamespace(epoch="recent", ago=0.1, dt=0.1))
    assert not h.events  # (none in the deep epoch, none with the rate at 0)


def test_sea_hunters_eat_the_sea(faketz):
    """D28 B (lane 99): a dragon kind with the trait 'sea_hunter' adds the sea's food (megafauna.sea_food) to the land's; others do not;
    off (SEA_FOOD False) nobody does."""
    from planet.lineages import prey as PR
    from planet.lineages.history import megafauna as MG
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    raw = {"meta": {"seed": 1}, "lineage": [
        {"id": "stem", "origin": "root", "at": "10 Myr", "temp_c": [-20, 40], "rain_mm": [1, 9000]},
        {"id": "sea", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies", "sea_hunter"]},
        {"id": "land", "parents": ["stem"], "at": "5 Myr", "megafauna": True, "generation_yr": 200, "traits": ["flies"]}]}
    ps.graze_npp = np.full(ps.grid.n, 100.0)
    ps.forage = np.full(ps.grid.n, 2.0)
    ps.sea_npp = np.where(np.arange(ps.grid.n) % 2 == 0, 100.0, 0.0)
    h = H.History(SP.parse(raw), ps, 1)
    assert h.sea_food is not None and h.sea_food.max() > 0
    food = np.full(h.grid.n, 0.01)
    s, l = h.idx["sea"], h.idx["land"]
    assert np.allclose(MG.natural(h, s, None, food) - MG.natural(h, l, None, food), h.sea_food / (h.dragon_struct["cattle_yr"] * PR.HEAD_T))
    MG.SEA_FOOD = False
    try:
        h2 = H.History(SP.parse(raw), ps, 1)
        assert h2.sea_food is None and np.allclose(MG.natural(h2, s, None, food), MG.natural(h2, l, None, food))
    finally:
        MG.SEA_FOOD = True


def test_brief_people_range_takes_every_cell_it_lives_on(tmp_path):
    """PW-1269: `brief --people X` takes the presence table's cells for X (a kind that never leads has a range all the same);
    a run without the table falls back to where X leads or is second."""
    from types import SimpleNamespace
    from planet.grid import shared_grid
    from planet.lineages import brief as BR
    g = shared_grid(3)
    n = g.n
    k_lead, k_dragon = 0, 1
    lead = np.full(n, 255, np.uint8)
    lead[:200] = k_lead
    second = np.full(n, 255, np.uint8)
    second[100:150] = k_dragon  # (the dragons come second on 50 cells)
    frames = {"mix_lead": lead, "mix_second": second, "peoples_whole": lead, "peoples": lead}
    lived = np.arange(80, 400)  # (they live on 320 cells: in a table, the range)
    table = {"offsets": np.array([[0, 0, len(lived)]] * 2, np.uint32), "cells": lived.astype(np.uint32), "share": np.full(len(lived), 30, np.uint8)}
    mk = lambda pt: SimpleNamespace(idx={"folk": 0, "dragon": 1}, lines=[{"id": "folk"}, {"id": "dragon"}], g=g, ts=np.array([-5.0, 0.0]),
                                    f=lambda name, i: frames[name], presence_table=lambda: pt, dir=tmp_path)
    sel, cen, basis = BR.region_of_people(mk(table), "dragon", 0)
    assert sel.sum() == len(lived) and sel[lived].all() and cen is not None and "presence table" in basis
    sel_old = BR.region_of_people(mk(None), "dragon", 0)[0]  # (frame 0 of 2: the last frame also reads presence_present.bin)
    assert sel_old.sum() == 50 and sel_old[100:150].all()


def _sea_strip(gap_cells, era="renaissance"):
    """(lane 157) A line of cells: landmass A (0-2), gap_cells of sea, landmass B (3 cells), 100 km a cell; a crop Stock known on A."""
    from types import SimpleNamespace as NS
    from planet.lineages import animals as AN
    from planet.lineages import crop_defs as CD
    n = 3 + gap_cells + 3
    off = np.concatenate([[0], np.cumsum([(i > 0) + (i < n - 1) for i in range(n)])])
    idx = np.array([j for i in range(n) for j in (i - 1, i + 1) if 0 <= j < n])
    land = np.zeros(n, bool)
    land[:3] = land[-3:] = True
    lab = np.where(land, np.where(np.arange(n) < 3, 0, 1), -1)
    names = [{"name": "A", "area_mkm2": 5.0}, {"name": "B", "area_mkm2": 5.0}]
    h = NS(grid=NS(n=n, nbr_off=off, nbr_idx=idx, lat=np.zeros(n), lon=np.zeros(n)), cell_km=100.0, cross=NS(label=lab, names=names),
           _native=np.array([0, 1]), events=[], tree=NS(era=era), lines=[NS(id="a"), NS(id="b")])
    s = object.__new__(AN.Stock)
    s.h, s.a, s.rng = h, CD.BY_ID["maize"], np.random.default_rng(1)
    s.rd, s.route = np.where(np.arange(n) < 3, 1.0, 0.0), np.zeros(n, np.uint8)
    s.crossings, s.landed, s.n_crossed, s.took_up = [], set(), 0, {0: 5.0}
    coast = np.zeros(n, bool)
    coast[2] = coast[n - 3] = True
    sides = (np.where(np.arange(n) < 3, 1.0, 0.0), np.where(np.arange(n) >= n - 3, 1.0, 0.0))
    return s, {"land": land}, {"label": lab, "coast": coast}, land, sides


def test_crops_cross_open_sea_only_with_colonists_or_ocean_ships():
    """Lane 157: before the ocean-going ships a crop crosses long open sea only with colonists to their own land, and passes between
    peoples over a strait; the ships (the last 0.53 kyr of a renaissance or later present) carry it to anyone at once."""
    from types import SimpleNamespace as NS
    from planet.lineages import animals as AN
    assert not AN.ocean_ships("renaissance", 2.0) and not AN.ocean_ships("medieval", 0.1) and AN.ocean_ships("renaissance", 0.3)
    s, env, tags, land, (a, b) = _sea_strip(10)  # 1000 km of open sea, a seafaring people on A and another on B
    p, sea = np.stack([a, b]), np.array([0.6, 0.6])
    for _ in range(200):
        s._sail_crop(NS(ago=2.0), env, tags, p, land, sea, 0.5)
    assert s.n_crossed == 0  # (no trade with strangers over open sea in sailing ships)
    s._ocean(NS(ago=0.3), env, tags, p, land, sea)  # the ships go there and back: it lands at once
    assert (s.rd[b > 0] > 0).all() and s.crossings[-1]["craft"] == AN.OCEAN_SHIP
    s, env, tags, land, (a, b) = _sea_strip(10)
    p = np.stack([a + b, np.zeros(land.size)])  # the seafarers hold both shores: colonists take their gardens
    for _ in range(200):
        s._sail_crop(NS(ago=2.0), env, tags, p, land, sea, 0.5)
        if s.n_crossed:
            break
    assert s.n_crossed == 1 and s.crossings[0]["craft"] == "sailing ship"
    s, env, tags, land, (a, b) = _sea_strip(2)  # a 200 km strait: canoe trade between strangers, also after the planked boats
    p = np.stack([a, b])
    for _ in range(400):
        s._sail_crop(NS(ago=2.0), env, tags, p, land, np.array([0.1, 0.05]), 0.5)
        if s.n_crossed:
            break
    assert s.n_crossed == 1 and s.crossings[0]["craft"].startswith("canoe")


def _live_setup(faketz, monkeypatch, places=True):
    """Lane 183 (PW-1434): the brake set-up with polities in the history switched on, every tech known (a lent calendar), a farming
    people (folk) beside a small one it hates (the kobolds). `places`: the ledger's places grown first (_grow_places, the seats)."""
    from planet.lineages.history import params as HP, polity_live as PL
    from planet.lineages import polities as PO
    monkeypatch.setattr(HP, "POLITIES_LIVE", True)
    h, env, step = _brake_setup(faketz)
    assert type(h.rule) is PL.LivePolities
    import types  # (a lent calendar in place of the tech tree inside the history, history.tech_live)
    techs = ("villages", "chiefdoms", "proto_writing", "writing", "towns", "cities", "kingship", "law", "bronze", "iron")
    h.rule.tech = types.SimpleNamespace(known={l.id: {t: [100.0, "test", None] for t in techs} for l in h.lines}, step=lambda s: None,
                                        secs=0.0)
    monkeypatch.setattr(PO, "WAR_P", 1.0)
    monkeypatch.setattr(PO, "STATE_KM", 1.0)  # (each seat rules its own cell: neighbours border, so war has somewhere to act)
    h._farm_share[:] = 1.0
    h._era = ["agrarian"] * len(h.lines)
    h.dens[:] = 50.0
    h.dens[h.idx["kob"]] = 5.0  # (folk ten times as dense: their states far the stronger)
    h._dmap = None
    h._env_now = env
    land = np.flatnonzero(env["land"])
    fk, kb = h.idx["folk"], h.idx["kob"]
    h.p[fk][land[:300]] = 0.9
    h.p[kb][land[300:330]] = 0.9
    _sync_pm(h)
    h._linger = np.zeros((len(h.lines), h.grid.n), bool)
    from planet.lineages import landuse as LU  # (the land use's farmers, as a frame stores them: everyone farms here, as _farm_share)
    _fi = LU.frame_inputs
    monkeypatch.setattr(LU, "frame_inputs", lambda *a, **k: {**_fi(*a, **k), "farm": np.full(h.grid.n, 100, np.uint8)})
    if places:
        _grow_places(h)
    return h, env, step, land


def _grow_places(h):
    """PW-1596 (lane 281b): the live seats are the settlement ledger's places (town_cells, which need 'villages' first), founded over
    FOUND_STEPS and grown toward their size step by step: grow them from nothing on the peoples as they stand, 4 to 1.3 kyr ago."""
    import types
    h.rule._towns_st = None
    for ago in np.round(np.arange(4.0, 1.25, -0.1), 3):
        h.rule.end_step(types.SimpleNamespace(epoch="recent", ago=float(ago), dt=0.1, store=True))


def test_polities_in_the_history_seat_claim_and_conquer_with_the_winners_tolerance(faketz, monkeypatch):
    """PW-1434 (lane 183, round7.md): switched on, the history seats states from its own central places and they claim land (war is
    polities.war_v0 itself, tested there); the peoples on land a war took fare by the winner's hostility: the kobolds folk hate are
    expelled, but never more than FATE_MAX of their heads in one step, and a tolerant winner keeps them. Off by default."""
    import types
    from planet.lineages.history import params as HP, polity_live as PL
    assert HP.POLITIES_LIVE is False
    h, env, step, land = _live_setup(faketz, monkeypatch)
    fk, kb = h.idx["folk"], h.idx["kob"]
    for ago in (1.2, 1.1, 1.0, 0.9):
        h.rule.begin_step(types.SimpleNamespace(epoch="recent", ago=ago, dt=0.1))
        _sync_pm(h)
    R = h.rule
    assert R.steps and R.steps[0]["states"] >= 1 and R.owner is not None and (R.owner >= 0).any()
    # the peoples on land a war took fare by the winner's hostility to them: the kobolds folk hate are expelled (FATE_CUT), but never
    # more than FATE_MAX of their heads in one step; folk's own people keep their land
    R.att.x[kb] = np.array([0.5, 1.0])  # (the kobolds resist: at least as warlike as any winner here, D61 submit-or-resist)
    kob0, folk0 = h.p[kb].copy(), h.p[fk].copy()
    cells = np.flatnonzero((h.p[kb] > 0) | (h.p[fk] > 0))
    R.k += 1
    fates = R._fates({"line": fk, "people": "folk"}, cells, R._heads()[2])
    assert fates["kob"][0] in ("expelled", "razed") and fates["kob"][1] > 0 and "folk" not in fates  # (no other land: lost either way, PW-1496)
    lost = 1.0 - h.p[kb].sum() / kob0.sum()
    assert 0 < lost <= PL.FATE_MAX + 1e-9 and np.array_equal(h.p[fk], folk0)
    monkeypatch.setattr(PL, "FATE_AT", (2.0, 3.0))  # (a tolerant winner keeps them)
    R.k += 1
    kob1 = h.p[kb].copy()
    assert R._fates({"line": fk, "people": "folk"}, cells, R._heads()[2])["kob"] == ["kept", 0, 0] and np.array_equal(h.p[kb], kob1)
    # the seam reads the live polities: pacified where a state rules, not on unruled land
    G = R.pacification(fk, types.SimpleNamespace(ago=0.9))
    ruled = R.owner >= 0
    assert np.all(G[~ruled] == 1.0) and np.all(G[ruled] < 1.0)
    doc = R.doc()
    assert doc["steps"] and doc["polities"] and "inside the history" in doc["calendar"]


def test_live_confederation_bands_a_peoples_villages_beside_a_foreign_state(faketz, monkeypatch):
    """PW-1583 (lane 241, round16.md): the history has the read-out's step 1b. A people with kings, law and writing but no city seats
    a confederation (a state, with the stacked reach, WIDE_BY) at one of its places when its own people in its places within a state's
    reach number a city's worth and a foreign state held land within that reach last step. Not without the foreign state, and not
    with too few people."""
    from planet.lineages import polities as PO
    h, env, step, land = _live_setup(faketz, monkeypatch)
    R, g = h.rule, h.rule.g
    fk, kb = h.idx["folk"], h.idx["kob"]
    lm = np.asarray(env["land"], bool)
    c0 = next(int(c) for c in land if lm[R.idx[R.off[c]:R.off[c + 1]]].all() and R.off[c + 1] - R.off[c] >= 5)
    nb = R.idx[R.off[c0]:R.off[c0 + 1]]
    monkeypatch.setattr(PO, "STATE_KM", 1.5 * float(R.ekm[R.off[c0]:R.off[c0 + 1]].max()))  # (a state's reach: c0's ring)
    lead = np.full(g.n, -1, np.int64)
    lead[[c0, *nb[:3].tolist()]] = fk
    lead[nb[3:]] = kb
    peopled = lead >= 0
    R.owner = np.where(lead == kb, 0, -1)  # (last step: the kobolds' state held the rest of the ring)
    R.ruling, R.tier_of = [{"key": f"c{int(nb[3])}", "cell": int(nb[3]), "people": "kob", "line": kb, "tier": "state"}], ["state"]
    city_min = 10000.0
    z = np.zeros(len(R.idx))
    args = (1.0, R.k, peopled, z, ~lm, np.zeros(g.n, bool), city_min)
    # (PW-1671: the ledger's places, town_cells' two slots per cell: four chief places of folk, villages of 3,000: no city, 12,000 in
    # all; the kobolds' cells hold no place)
    place = np.stack([np.where(lead == fk, 0.3 * city_min, 0.0), np.zeros(g.n)])
    holder = np.stack([lead, np.full(g.n, -1, np.int64)])
    got = R._confederations([], place, holder, *args)
    assert len(got) == 1 and got[0]["people"] == "folk" and got[0]["tier"] == "state" and got[0]["confed"] and got[0]["heads"] == 12000
    assert got[0]["key"] in {f"c{c}" for c in np.flatnonzero(lead == fk)}
    R.tier_of = ["chiefdom"]  # (no foreign state beside them: nothing to band together against)
    assert R._confederations([], place, holder, *args) == []
    R.tier_of = ["state"]
    assert R._confederations([], place * 0.8, holder, *args) == []  # (9,600: short of a city's worth)
    # a people's places on a cell sum over both slots (as the read-out sums its sites): 9,600 in chief places + 2,400 in a second
    # people's own place of folk on one of them is a city's worth again
    holder2 = holder.copy()
    holder2[1, c0] = fk
    place2 = place * 0.8
    place2[1, c0] = 0.24 * city_min
    got = R._confederations([], place2, holder2, *args)
    assert len(got) == 1 and got[0]["people"] == "folk" and got[0]["heads"] == 12000


def test_live_central_places_read_the_ledgers_site_factor(faketz, monkeypatch):
    """PW-1587 (lane 245): the history's central places are sized and chosen as the ledger's (settlements._site_factor): a harbour
    beside a cell that is a coast now makes its town bigger and the best of its ring on even ground; a harbour inland counts for nothing.
    Without a world every cell is an ordinary site (1). PW-1671 (lane 281c): the places are town_cells' (the ledger's rule on the
    history's inputs, which the seats and the confederations read), grown from nothing over the same steps with and without the harbour."""
    from planet.lineages import settlements as SE
    h, env, step, land = _live_setup(faketz, monkeypatch, places=False)
    R = h.rule
    assert all(not np.any(R.W[k]) for k in ("harbour", "river_nav", "fresh_water", "pass"))  # (the stand-in pass has no world: no site layers)
    lm = np.asarray(env["land"], bool)
    deg = np.diff(R.off)
    folk = h.p[h.idx["folk"]] > 0
    coast = [int(c) for c in np.flatnonzero(lm & folk) if (~lm[R.idx[R.off[c]:R.off[c + 1]]]).any()
             and (lm & folk)[R.idx[R.off[c]:R.off[c + 1]]].sum() >= 3]
    inland = next(int(c) for c in np.flatnonzero(lm & folk) if lm[R.idx[R.off[c]:R.off[c + 1]]].all() and deg[c] >= 5)
    c0 = coast[0]
    sea0 = next(int(x) for x in R.idx[R.off[c0]:R.off[c0 + 1]] if not lm[x])

    def grown():
        _grow_places(h)
        st = R._towns_st
        return np.where(st["act"][0], st["pop"][0], 0.0)
    base = grown()
    R.W["harbour"][inland] = 3.0  # (PW-1640: the layer marks the harbour water; a harbour marked on land counts for nothing)
    assert np.array_equal(grown(), base)
    R.W["harbour"][sea0] = 3.0  # (the shore beside harbour water reads it)
    pop = grown()
    ring = R.idx[R.off[c0]:R.off[c0 + 1]]
    assert pop[c0] >= SE.CONST["TOWN_MIN"][0] and np.all(pop[ring] < pop[c0])  # (the harbour is a town, the best of its ring)
    assert pop[c0] > base[c0] * (1 + 0.5 * SE.CONST["SITE_HARBOUR"][3])  # (x the site factor, as the ledger)


def test_live_refugees_skip_land_their_people_has_already_left(faketz, monkeypatch):
    """PW-1583 (lane 241): a people cut twice in one step (two conquests) has heads left on the books of a cell its presence has
    left (under EST after the first cut). The refugees of the second expulsion go only to cells it still holds, so the heads moved
    stay finite (they were NaN: 0/0 on the emptied cell)."""
    h, env, step, land = _live_setup(faketz, monkeypatch)
    R = h.rule
    kb = h.idx["kob"]
    taken, gone_cell, home = land[300:305], int(land[305]), land[306:330]
    hk = R._heads()[2][kb].copy()
    h.p[kb][gone_cell] = 0.0  # (the first conquest this step emptied it; hk still counts it)
    moved = R._refuge(kb, hk, taken, np.zeros(R.g.n, bool), 100.0)
    assert np.isfinite(moved) and np.isfinite(h.p[kb]).all() and h.p[kb][gone_cell] == 0.0


def test_a_live_state_seat_is_hemmed_in_over_its_own_two_rings(faketz, monkeypatch):
    """PW-1594 (lane 248, round18.md): with polities in the history, how hemmed in a state seat is reads the seat's own two rings, as
    the read-out (polities._hemmed): free land of its own people bars nothing, land only other peoples hold bars SOCIAL_Q, a high peak
    bars fully; not the people's whole border."""
    from planet.lineages import polities as PO
    from planet.lineages.history import params as HP
    from planet.lineages.seafood import rings_for
    h, env, step, land = _live_setup(faketz, monkeypatch)
    R = h.rule
    fk, kb = h.idx["folk"], h.idx["kob"]
    L = np.asarray(env["land"], bool)
    ice = np.zeros(h.grid.n, bool)
    el = np.where(L, np.asarray(env["elevation"], float), 0.0)
    folk = h.p[fk] > 0
    rings = PO._rings(h.grid, rings_for(h.grid, PO.HEMMED_KM))
    c = next(int(c) for c in land[:300] if L[rings[int(c)]].all() and folk[rings[int(c)]].all() and (el[rings[int(c)]] < 3000).all())
    ring = rings[c]
    assert sorted(R.r2b[R.r2off[c]:R.r2off[c + 1]].tolist()) == sorted(ring.tolist() + [c])
    R.hem[fk] = 1.0  # (the people's whole border, which the state test no longer reads)
    assert R._hem_local(c, fk, "folk", 1.0, L, ice, el) == 0.0
    a, b = ring[:4], ring[4]
    h.p[fk][a] = 0.0
    h.p[kb][a] = 0.9
    el[b] = 3500.0
    assert R._hem_local(c, fk, "folk", 1.0, L, ice, el) == pytest.approx((4 * HP.SOCIAL_Q + 1.0) / len(ring))


def test_live_conquest_harshness_reads_the_winners_attitudes(faketz, monkeypatch):
    """PW-1481 / PW-1465 (lane 201, round10.md; Daniel D54): the history keeps each people's attitudes (attitudes.Attitudes, stepped
    each century), and a conquered people's fate reads the winner's: harshness 1 - tolerance x (1 - old enmity). With no old quarrel a
    tolerant winner keeps them and an intolerant one expels them; a more aggressive winner cuts harder."""
    import types
    from planet.lineages.history import polity_live as PL
    h, env, step, land = _live_setup(faketz, monkeypatch)
    R = h.rule
    fk, kb = h.idx["folk"], h.idx["kob"]
    for ago in (1.2, 1.1, 1.0):
        R.begin_step(types.SimpleNamespace(epoch="recent", ago=ago, dt=0.1))
        _sync_pm(h)
    assert fk in R.att.x and kb in R.att.x and R.att_ago == 1.0
    att = R.doc()["attitudes"]
    assert str(fk) in att["cultures"] and att["cultures"][str(fk)]["people"] == "folk"
    R.hostility[fk, kb] = 0.0  # (no old quarrel: only the winner's own temperament)
    R.att.x[kb] = np.array([0.5, 1.0])  # (the kobolds resist: at least as warlike as any winner here, D61 submit-or-resist)
    cells = np.flatnonzero(h.p[kb] > 0)
    p0 = h.p[kb][cells].copy()
    monkeypatch.setattr(PL, "FATE_MAX", 1.0)
    out = {}
    for ta in ((0.95, 0.3), (0.1, 0.3), (0.1, 0.6)):
        h.p[kb][cells] = p0
        R.att.x[fk] = np.array(ta)
        R.k += 1
        out[ta] = R._fates({"line": fk, "people": "folk"}, cells, R._heads()[2])["kob"]
    assert out[(0.95, 0.3)] == ["kept", 0, 0]
    assert out[(0.1, 0.3)][0] == "expelled" and out[(0.1, 0.6)][0] == "razed"  # (PW-1496: a martial winner razes)
    assert 0 < out[(0.1, 0.3)][1] < out[(0.1, 0.6)][1]
    R.hostility[fk, kb] = 0.5  # (an old quarrel: a very tolerant winner keeps them, a middling plain one thins as the old rule, an
    # intolerant one expels; a middling martial one expels too, PW-1487)
    for ta, want in (((0.95, 0.5), "kept"), ((0.5, 0.3), "thinned"), ((0.1, 0.4), "expelled"), ((0.1, 0.5), "razed"), ((0.5, 0.5), "razed")):
        h.p[kb][cells] = p0
        R.att.x[fk] = np.array(ta)
        R.k += 1
        assert R._fates({"line": fk, "people": "folk"}, cells, R._heads()[2])["kob"][0] == want


def test_expelled_peoples_move_to_their_nearest_free_land_and_a_martial_winner_razes(faketz, monkeypatch):
    """PW-1496 (Daniel D61 C, round12.md): an expulsion by a winner below the martial mark (aggression AGG_MID) moves the cut share to
    the same people's nearest land the winner does not rule, by its existing density, so the people keeps its heads; at or above the
    mark the share is lost (razed); with no such land the expelled are lost; a thinning is always a loss. A people less warlike than
    the winner submits and is kept (D61, Genghis Khan's terms)."""
    import types
    from planet.lineages.history import polity_live as PL
    h, env, step, land = _live_setup(faketz, monkeypatch)
    R = h.rule
    fk, kb = h.idx["folk"], h.idx["kob"]
    for ago in (1.2, 1.1, 1.0):
        R.begin_step(types.SimpleNamespace(epoch="recent", ago=ago, dt=0.1))
        _sync_pm(h)
    R.hostility[fk, kb] = 0.0
    monkeypatch.setattr(PL, "FATE_MAX", 1.0)
    R.att.x[kb] = np.array([0.5, 1.0])  # (the kobolds resist: at least as warlike as any winner here, D61 submit-or-resist)
    kob = np.flatnonzero(h.p[kb] >= PL.EST)
    assert len(kob) >= 4
    h.p[kb] = np.where(h.p[kb] >= PL.EST, np.minimum(h.p[kb], 0.3), h.p[kb])  # (room to take the refugees in)
    p0 = h.p[kb].copy()
    cells = kob[: len(kob) // 2]
    ruled = np.zeros(h.grid.n, bool)
    ruled[cells] = True

    def run(ta):
        h.p[kb] = p0.copy()
        R.att.x[fk] = np.array(ta)
        R.k += 1
        hd = R._heads()[2]
        before = float(hd[kb].sum())
        f = R._fates({"line": fk, "people": "folk"}, cells, hd, ruled)["kob"]
        return f, before, float(R._heads()[2][kb].sum())

    f, b, a = run((0.1, 0.4))  # (intolerant, plain: drives them out)
    assert f[0] == "expelled" and f[2] > 0 and f[1] <= 1 and abs(a - b) <= 1e-6 * b + 1
    assert np.all(h.p[kb][cells] <= p0[cells]) and (h.p[kb][~ruled] >= p0[~ruled]).all() and (h.p[kb][~ruled] > p0[~ruled]).any()
    f, b, a = run((0.1, 0.6))  # (intolerant, martial: razes)
    assert f[0] == "razed" and f[1] > 0 and f[2] == 0 and a < b and np.array_equal(h.p[kb][~ruled], p0[~ruled])
    ruled[:] = False
    ruled[kob] = True  # (the winner rules all its land: nowhere to go, the expelled are lost)
    f, b, a = run((0.1, 0.4))
    assert f[0] == "expelled" and f[1] > 0 and f[2] == 0 and a < b
    R.hostility[fk, kb] = 0.3  # (a thinning is a loss, whatever the aggression)
    ruled[:] = False
    ruled[cells] = True
    f, b, a = run((0.5, 0.3))
    assert f[0] == "thinned" and f[1] > 0 and f[2] == 0
    R.att.x[kb] = np.array([0.5, 0.2])  # (a less warlike people submits and is kept, even by a martial, intolerant winner)
    monkeypatch.setattr(PL, "REVOLT", False)
    f, b, a = run((0.1, 0.6))
    assert f == ["submitted", 0, 0] and a == b and np.array_equal(h.p[kb], p0)
    assert R.submissions == [] and R.revolts == []  # (REVOLT off: nothing kept)
    # PW-1513 (D67 B, switch REVOLT): a submitted people that seats its own polity on its ruler's land, while the ruler stands, has
    # risen; the same ruler's next taking finds it unable to submit again, and the fate is the winner's attitudes then
    monkeypatch.setattr(PL, "REVOLT", True)
    f, b, a = run((0.1, 0.6))
    assert f == ["submitted", 0, 0] and R.submitted == {"kob": {"folk"}}
    c = int(cells[0])
    R.owner = np.full(h.grid.n, -1, np.int64)
    R.owner[c] = 0
    R.ruling = [{"key": "c-folk", "people": "folk", "cell": int(kob[-1]), "tier": "state"}]
    rebel = {"key": f"c{c}", "people": "kob", "cell": c, "tier": "chiefdom"}
    R._risings([rebel], {"c-folk": 1, rebel["key"]: 0}, 0.9)
    assert R.revolts == [[0.9, "kob", "folk", c]] and ("kob", "folk") in R.revolted
    f, b, a = run((0.1, 0.6))  # (retaken by the same martial, intolerant ruler: razed, as it would have been)
    assert f[0] == "razed" and f[1] > 0 and a < b and R.punished[-1][1:4] == ["kob", "folk", "razed"]
    f, b, a = run((0.1, 0.6))  # (once punished, the mark is spent: it may submit again)
    assert f == ["submitted", 0, 0]
    R.submitted, R.revolted = {"kob": {"folk"}}, {}
    R._risings([rebel], {rebel["key"]: 0}, 0.8)  # (the ruler's polity no longer stands: no rising against it)
    assert ("kob", "folk") not in R.revolted


def test_aggression_makes_an_intolerant_conqueror_harsher_not_a_tolerant_one():
    """PW-1487 (Daniel D59 C, round11.md): aggression raises a winner's harshness in proportion to its intolerance. A martial,
    intolerant winner expels even a people it has no quarrel with; a martial, tolerant one (Cyrus) still keeps it; a plain winner
    (aggression AGG_HARSH) is as harsh as its tolerance alone says, as before."""
    from planet.lineages.history import polity_live as PL
    fate = lambda z: "kept" if z < PL.FATE_AT[0] else ("thinned" if z < PL.FATE_AT[1] else "expelled")  # noqa: E731
    assert fate(PL.harshness(0.0, 0.36, 0.60)) == "expelled"  # (round 10's orcs, seed 10: thinned there)
    assert fate(PL.harshness(0.0, 0.80, 0.80)) == "kept"  # (a tolerant horde)
    assert fate(PL.harshness(0.3, 0.75, 0.60)) == "kept"  # (a tolerant martial winner keeps even a mild old enemy)
    for tol in (0.2, 0.5, 0.8):
        assert PL.harshness(0.2, tol, PL.AGG_HARSH) == 0.2 + PL.TOL_X * (0.5 - tol)  # (plain winner: the old rule)
        assert PL.harshness(0.2, tol, 0.7) > PL.harshness(0.2, tol, 0.4)
    assert PL.harshness(0.2, 1.0, 0.9) == PL.harshness(0.2, 1.0, 0.1)  # (fully tolerant: aggression does not move it)
    lift = lambda tol: PL.harshness(0.0, tol, 0.8) - PL.harshness(0.0, tol, 0.3)  # noqa: E731
    assert lift(0.1) > lift(0.5) > lift(0.9) > 0


def test_campaign_budget_is_a_fixed_range_or_the_states_own_radius_times_mobility():
    """PW-1478 (Daniel D56 B plus Rome, round11.md): an expedition reaches CAMPAIGN_KM (1,000 km) or, for a state larger than that,
    its own radius (EXTENT_X x sqrt(area / pi)); x2 for nomads and pastoral nomads."""
    import math
    from planet.lineages import invasions as IV
    assert IV.campaign_budget(0.2e6, 1.0) == IV.CAMPAIGN_KM == 1000.0  # (a small state: the fixed range)
    assert IV.campaign_budget(0.2e6, IV.mobility({"traits": ["nomadic"]})) == 2000.0
    rome = IV.campaign_budget(5.0e6, 1.0)  # (Rome at AD 117, Taagepera 1979)
    assert math.isclose(rome, math.sqrt(5.0e6 / math.pi)) and 1200 < rome < 1300
    assert IV.campaign_budget(5.0e6, 2.0) == 2 * rome


def test_live_polities_send_a_strong_rows_expedition_across_a_gap(faketz, monkeypatch):
    """PW-1479 (lane 201, round10.md): with polities in the history on, a strong invasion row reaches victims across unruled land as
    the read-out does (polities._expedition, the same code): only within the campaign budget (invasions.campaign_budget, which both
    paths read; here 1 km and no radius term, too short, against 1e5 km), and the read-out says why not when it falls short."""
    import types
    from planet.lineages import invasions as IV, polities as PO
    h, env, step, land = _live_setup(faketz, monkeypatch, places=False)
    R = h.rule
    g = h.grid
    fk, kb = h.idx["folk"], h.idx["kob"]
    env = dict(env, land=np.ones(g.n, bool), ice=np.zeros(g.n), elevation=np.zeros(g.n))  # (all flat land: the gap is open country)
    h._env_now, h._land_now = env, env["land"]
    c = np.asarray(g.centers, float)
    sp = float(np.median(R.ekm)) / PO.R_EARTH_KM  # (one cell spacing, radians)
    ang = lambda a: np.arccos(np.clip(c @ c[a], -1, 1))  # noqa: E731
    a0 = int(land[0])
    d0 = ang(a0)
    b0 = int(np.argmin(np.abs(d0 - 14 * sp)))
    h.p[:] = 0.0
    h.p[fk][d0 < 6 * sp] = 0.9
    h.p[kb][ang(b0) < 3 * sp] = 0.9
    h.dens[kb] = 50.0
    h._dmap = None
    _sync_pm(h)
    rows = IV.clean([{"id": "r", "who": {"people": "folk"}, "whom": {"people": "kob"}, "from_kyr": 1.0, "to_kyr": 0.6, "strength": "strong"}])[0]
    p0, logs = h.p.copy(), {}
    for km in (1.0, 1e5):
        monkeypatch.setattr(IV, "CAMPAIGN_KM", km)
        monkeypatch.setattr(IV, "EXTENT_X", 0.0 if km == 1.0 else IV.EXTENT_X)
        h.p[:] = p0
        _sync_pm(h)
        R.__init__(h)
        R.tech = types.SimpleNamespace(known={l.id: {t: [100.0, "test", None] for t in ("villages", "chiefdoms", "proto_writing", "writing",
                                                                                         "towns", "cities", "kingship", "law")}
                                              for l in h.lines}, step=lambda s: None, secs=0.0)
        _grow_places(h)  # (the seats: the ledger's places on these peoples)
        h.p[:] = p0
        _sync_pm(h)
        R.inv_in, R.inv_rows, R.inv_log = rows, IV.hook_rows(rows, R, 0.1), [IV.new_log()]
        for ago in (1.2, 1.1, 1.0, 0.9, 0.8, 0.7):
            R.begin_step(types.SimpleNamespace(epoch="recent", ago=ago, dt=0.1))
            _sync_pm(h)
        logs[km] = R.inv_log[0]
    assert logs[1.0]["took"] == [] and logs[1.0]["exped"] == [] and logs[1.0]["exped_fail"] > 0  # (too short)
    lg = logs[1e5]
    assert lg["took"] and lg["exped"] and lg["exped"][0]["km"] > 0 and "winner_id" in lg["exped"][0]
    doc = R.doc()
    assert doc["invasions"][0]["log"]["took"] and doc["constants"]["CAMPAIGN_KM"] == 1e5


def test_the_tech_tree_runs_inside_the_history_when_polities_do(faketz, monkeypatch):
    """PW-1466 (lane 192, round8.md): with polities in the history on, the tech tree runs step by step inside it (history.tech_live)
    and the run's meta.techtree is that calendar written out; the live polities' gates read it. Off, the tree is built after the run."""
    from planet.lineages.history import params as HP, polity_live as PL
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    monkeypatch.setattr(HP, "POLITIES_LIVE", True)
    h, res, pres = H.simulate(SP.parse(_raw()), ps, tries=1)
    assert type(h.rule) is PL.LivePolities and h.rule.tech.cal is not None
    cal = h.rule.tech.cal
    assert cal.step == len(cal.grid)  # (the history's last step is the present: every step of the tree has run)
    live = {lid: dict(kn) for lid, kn in cal.known.items()}
    assert any(live.values())
    out = O.save(h, res, pres, name="live tech")
    tt = json.loads((out / "run.json").read_text())["meta"]["techtree"]
    assert "inside_history" in tt and tt["known"] == json.loads(json.dumps(live))
    assert h.rule.knows(next(l for l, kn in live.items() if kn), next(iter(next(kn for kn in live.values() if kn))), 0.0)
    monkeypatch.setattr(HP, "POLITIES_LIVE", False)
    h0, res0, pres0 = H.simulate(SP.parse(_raw()), ps, tries=1)
    assert not hasattr(h0.rule, "tech")
    assert "inside_history" not in json.loads((O.save(h0, res0, pres0, name="after-run tech") / "run.json").read_text())["meta"]["techtree"]


def test_the_live_tree_reads_the_live_seats_as_its_town_footprint(faketz, monkeypatch):
    """PW-1472 (lane 195, round9.md): with D52's town arm E switched on (a test override; D53 is the owner's call) and polities in the
    history on, the tree inside the history reads each people's town cells from the history's own central places (no ledger yet), so
    E acts there and nothing warns; a people whose towns go has none from then."""
    import warnings
    from planet.lineages import techtree as TT
    from planet.lineages.history import tech_live as TL
    T0 = TT.load()
    monkeypatch.setattr(TT, "load", lambda path=None: {**T0, "defaults": {**T0["defaults"], "contact_arms": "E"}})
    h, env, step, land = _live_setup(faketz, monkeypatch, places=False)
    R = h.rule
    for kn in R.tech.known.values():
        kn["villages"] = [100.0, "test", None]  # (the ledger's tiers: villages first, no towns without them)
    h._linger = np.zeros(h.p.shape, bool)  # (as History.run sets it: no contact hybrid living on)
    h._lu_sh = np.array([[1.0, 0.0, 0.0]] * len(h.lines))  # (the land use's farmers, as the set-up's farm share: all farm)
    first = R.town_cells(2.0)  # (PW-1608: the sites are the ledger's, founded over FOUND_STEPS and grown toward their size)
    for ago in (1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1):
        R.town_cells(ago)
    cells = R.town_cells(1.0)
    assert not first and R.town_cells(1.0) is cells  # (nothing founded on the first step; a second call in one step counts nothing new)
    assert cells.get("folk", 0) > 0 and "kob" not in cells  # (folk's dense farmers hold towns; the kobolds' few heads do not)
    h.started, h.ended = {l.id: 40.0 for l in h.lines}, {}  # (as History.run keeps them)
    with warnings.catch_warnings():
        warnings.filterwarnings("error", message=".*town footprint")  # (no "need a town footprint" warning)
        lt = TL.LiveTech(h)
        assert lt.arms == "E" and lt.towns is not None
        lt.note_towns(1.0, cells)
        lt.note_towns(0.9, {})
        c = TT.Calendar(lt.lines(), seed=1, T=lt.T, towns=lt.towns, arms=lt.arms)
    assert c.towns is lt.towns and TT.town_cells_at(c.towns["folk"], 1.0) == cells["folk"]
    assert TT.town_cells_at(c.towns["folk"], 0.9) == 0 and TT.town_cells_at(c.towns["folk"], 1.1) == 0
    monkeypatch.setattr(TT, "load", lambda path=None: {**T0, "defaults": {**T0["defaults"], "contact_arms": ""}})  # (arms off: no footprint is kept, nothing counted)
    assert TL.LiveTech(h).towns is None


def test_the_live_town_count_holds_a_frames_inputs_until_the_next(faketz, monkeypatch):
    """PW-1612: the ledger reads each step from the stored frame at or before it; the live count likewise takes its inputs only on a
    step that stores a frame (fresh) and keeps them on the steps between, whatever the peoples do meanwhile."""
    out = []
    for gone in (False, True):
        h, env, step, land = _live_setup(faketz, monkeypatch, places=False)
        R = h.rule
        for kn in R.tech.known.values():
            kn["villages"] = [100.0, "test", None]
        h._linger = np.zeros(h.p.shape, bool)
        h._lu_sh = np.array([[1.0, 0.0, 0.0]] * len(h.lines))
        R.town_cells(2.0)
        if gone:
            h.p = np.zeros_like(h.p)  # (everyone gone after the frame: the steps between still read the frame's people)
        for ago in (1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1):
            R.town_cells(ago, fresh=False)
        out.append(R.town_cells(1.0, fresh=False))
    assert out[0].get("folk", 0) > 0 and out[1] == out[0]


def test_the_live_town_count_is_taken_at_the_end_of_a_step(faketz, monkeypatch):
    """PW-1612 B: the live town count is taken at the end of a step, on the state the step ends with (what a frame stored at that
    step holds, as the ledger reads it), not at its start; the tree reads it from the next step."""
    import types
    h, env, step, land = _live_setup(faketz, monkeypatch)
    R = h.rule
    seen = []
    R.tech = types.SimpleNamespace(known=R.tech.known, step=lambda s: None, secs=0.0, towns={"_cell_km2": 1.0},
                                   note_towns=lambda ago, cells: seen.append((ago, cells)))
    monkeypatch.setattr(R, "_step", lambda s: None)
    monkeypatch.setattr(R, "_attitudes", lambda s: None)
    monkeypatch.setattr(R, "town_cells", lambda ago, fresh=True: {"folk": int(h.p[h.idx["folk"]].sum() > 0), "fresh": fresh})
    s = types.SimpleNamespace(epoch="recent", ago=1.0, dt=0.1, store=True)
    R.begin_step(s)
    assert seen == []  # (nothing counted at the start)
    h.p[h.idx["folk"]] = 0.0  # (the peoples move during the step: folk gone)
    R.end_step(s)
    assert seen == [(1.0, {"folk": 0, "fresh": True})]


def test_the_live_tree_maps_regions_as_the_after_run_tree(faketz, monkeypatch):
    """PW-1597 R (lane 265, round22.md): the live tree's region learners read the after-run tree's landmass map (today's sea takes
    the nearest landmass, demes.landmass_rank) and the presence as a frame stores it (peoples as wholes, established cells, whole %)."""
    from planet.lineages.history import tech_live as TL
    from planet.lineages.spread import EST
    h, env, step, land = _live_setup(faketz, monkeypatch)
    h.started, h.ended = {l.id: 40.0 for l in h.lines}, {}
    h._linger = np.zeros(h.p.shape, bool)
    lt = TL.LiveTech(h)
    lm, lab = lt.landmass(), np.asarray(h.cross.label)
    assert (lm >= 0).all() and (lm[lab >= 0] == lab[lab >= 0]).all()
    fk = h.idx["folk"]
    h.p[fk][land[300]] = EST / 2  # (a thin fringe: not established, not stored)
    P = h.presence_stored()
    assert P[fk][land[300]] == 0 and P[fk][land[0]] == 0.9


def test_live_polities_know_the_dragons_as_the_read_out_does():
    """Lane 281b (PW-1596): the history's dragon realms are seated for the same peoples as the read-out's (_Run.dragons: 'dragon' in
    the id and the trait 'flies'). Before, the live test read the trait as a knob (l.trait("flies", 0.0): always 0), so the history
    seated no dragon realm at all."""
    from planet.lineages.history import polity_live as PL
    t = LR.load_tree("dnd")
    live = {l.id for l in t.lines.values() if PL.is_dragon(l)}
    readout = {l.id for l in t.lines.values() if "dragon" in l.id and "flies" in (l.traits or [])}
    assert live == readout and {"red_dragon", "gold_dragon"} <= live and "dragonborn" not in live


def _gc_km(g, a, b):
    la, lo = np.radians(np.asarray(g.lat)), np.radians(np.asarray(g.lon))
    c = np.sin(la[a]) * np.sin(la[b]) + np.cos(la[a]) * np.cos(la[b]) * np.cos(lo[a] - lo[b])
    return 6371.0 * np.arccos(np.clip(c, -1, 1))


def test_dragon_cultures_cut_a_range_as_the_demes_and_cultures_cut_a_dragon_kind():
    """Lane 281d (PW-1687 B, round27.md): inside the history a dragon people's cultures are cut by the demes' and the cultures engine's
    own rules for a dragon kind. Regions: pieces within a dragon's reach (megafauna.LINK_KM, over land and sea) are one, farther ones
    apart, a piece under demes.MIN_KM2 goes with the nearest. Cultures: the first range is one founding culture, however many regions;
    a region settled later is its parent's until it has stayed apart demes.PERSIST stored frames and cultures.t_apart, then a culture
    of its own under a key it keeps; two cultures on neighbouring cells merge, the younger into the older, after MERGE_CONTACT_KYR x
    (1 - cohesion) side by side."""
    from planet.grid import shared_grid
    from planet.lineages.history import polity_live as PL
    from planet.lineages.history.megafauna import LINK_KM
    from planet.lineages import demes as DE, cultures as CU
    from planet.lineages.seafood import cells_for, rings_for
    g = shared_grid(5)
    D = PL.DragonCultures(g, {"x": 0.9})
    assert D.r_link == rings_for(g, LINK_KM / 2) and D.min_cells == cells_for(g, DE.MIN_KM2) > 1
    a = 0
    d = _gc_km(g, a, np.arange(g.n))
    blob = lambda c, km: _gc_km(g, c, np.arange(g.n)) <= km  # noqa: E731
    near = int(np.argmin(np.abs(d - 0.6 * LINK_KM)))  # (a gap of well under LINK_KM between the two: one region)
    far = int(np.argmin(np.abs(d - 5 * LINK_KM)))  # (far beyond it: a region of its own)
    held = blob(a, 400) | blob(near, 300) | blob(far, 400)
    lab, n = PL.dragon_regions(g, held, D.r_link, D.min_cells)
    assert n == 2 and lab[a] == lab[near] == 0 and lab[far] == 1 and (lab[held] >= 0).all() and (lab[~held] < 0).all()
    tiny = int(np.argmin(np.abs(d - 3 * LINK_KM)))  # (one cell alone, under MIN_KM2: the nearest region's, no region of its own)
    held2 = held.copy()
    held2[tiny] = True
    lab2, n2 = PL.dragon_regions(g, held2, D.r_link, D.min_cells)
    assert n2 == 2 and lab2[tiny] in (0, 1)
    keys = lambda r: [k_ for k_, _ in r]  # noqa: E731
    assert keys(D.step(0, "x", held, 5.0, 0.5, True, 0.6)) == ["dx"]  # (the first range: one founding culture, two regions)
    third = int(np.argmin(np.abs(d - 10 * LINK_KM)))
    held3 = held | blob(third, 400)
    seen, ago = [], 4.5
    for _ in range(6):
        r = D.step(0, "x", held3, ago, 0.5, True, CU.T_APART_KYR["stone age"])
        seen.append((ago, keys(r), {k_: len(c) for k_, c in r}))
        ago -= 0.5
    assert [s[1] for s in seen[:3]] == [["dx"]] * 3 and seen[0][2]["dx"] == int(held3.sum())  # (a piece: its parent's for now)
    assert seen[3][1] == ["dx", "dx.1"] and seen[5][1] == ["dx", "dx.1"]  # (four stored frames apart, past t_apart: its own)
    bridge = blob(third, 400) | blob(far, 400)  # (the two meet: neighbouring cells, then one merged culture, the older's)
    path = np.zeros(g.n, bool)
    for t in np.linspace(0, 1, 600):
        v = (1 - t) * np.asarray(g.centers)[third] + t * np.asarray(g.centers)[far]
        path[int(np.argmax(np.asarray(g.centers) @ (v / np.linalg.norm(v))))] = True
    held4 = held3 | bridge | path
    r1 = D.step(0, "x", held4, 1.5, 0.1, False, 0.6)
    r2 = D.step(0, "x", held4, 1.4, 0.1, False, 0.6)
    assert keys(r1) == ["dx", "dx.1"] and keys(r2) == ["dx"] and len(r2[0][1]) == int(held4.sum())


def test_live_dragon_people_seats_a_realm_per_culture(faketz, monkeypatch):
    """Lane 281d (PW-1687 B, round27.md): a dragon people seats one realm per culture in the history (the read-out's one per dragon
    culture), its cultures cut as the demes and cultures engine cut a dragon kind (DragonCultures), keyed by the culture and the same
    key from step to step: the first range is one realm however scattered; a region settled far away later is a realm of its own
    once apart demes.PERSIST stored frames and cultures.t_apart (the stone age's 0.6 kyr). Lane 281c had one per people (4-6 realms
    against the read-out's 16-26); before that one per connected piece (290-310 against 22-25, keys moving every step)."""
    import types
    from planet.lineages import cultures as CU
    h, env, step, land = _live_setup(faketz, monkeypatch)
    R = h.rule
    g = h.grid
    kb = h.idx["kob"]
    R.dragons = [kb]  # (the kobolds stand in for a dragon people: hoards known)
    R.tech.known["kob"]["hoards"] = [100.0, "test", None]
    a = int(land[310])
    d = _gc_km(g, a, land)
    b = int(land[np.argmax(d)])  # (the land farthest away: another region)
    c = int(land[np.argmax(np.minimum(d, _gc_km(g, b, land)))])  # (far from both: a third, settled later)
    assert min(_gc_km(g, a, b), _gc_km(g, a, c), _gc_km(g, b, c)) > 2 * 1500.0
    h.p[kb][:] = 0.0
    h.p[kb][[a, b]] = 0.9
    _sync_pm(h)
    seen = []
    for i in range(11):
        ago = round(2.0 - 0.1 * i, 3)
        if i == 2:
            h.p[kb][c] = 0.9  # (a new region, far from the others)
        st = types.SimpleNamespace(epoch="recent", ago=ago, dt=0.1, store=True)
        h.rule.begin_step(st)
        _sync_pm(h)
        seen.append((ago, sorted(k for k in R.founded if k.startswith("d"))))
        h.rule.end_step(st)  # (the cultures are cut on the frame the step stores; the polities read them from the next step on)
    assert seen[0][1] == [] and seen[1][1] == ["dkob"]  # (the founding culture: one realm, two regions)
    late = [a_ for a_, s in seen if "dkob.1" in s]
    assert late and max(late) == pytest.approx(1.8 - CU.T_APART_KYR["stone age"] - 0.1, abs=1e-6)


def test_live_frontier_counts_hostile_co_subjects_only_across_a_border(faketz, monkeypatch):
    """Lane 183: under one ruler, the hostile peoples living inside its land are co-subjects (no frontier); on unruled land the
    stand-in's frontier holds."""
    h, env, step, land = _live_setup(faketz, monkeypatch)
    fk = h.idx["folk"]
    R = h.rule
    F0 = R.frontier(fk).copy()
    R.owner = np.zeros(h.grid.n, np.int64)  # (one polity rules everything)
    R.tier_of = ["state"]
    R.ruling = [{"people": "folk"}]
    R._Fc = None
    assert F0.any() and not R.frontier(fk).any()
    R.owner[:] = -1
    R._Fc = None
    assert np.allclose(R.frontier(fk), F0)


def test_war_dials_aggression_troubles_and_refugees(faketz, monkeypatch):
    """Lane 259 (PW-1172): war-torn land scales with meta.war_early / war_late blended by tech level, a people's war_x and the
    `aggressive` trait's x2; seeded times of troubles multiply the hazard for a step and log an event; the people war drives off that
    step push refugees (counter._refugee, dispersal._refugees), a loss it has settled under does not; war_x round-trips the spec."""
    from planet.lineages.history import params as HP
    from planet.lineages.history import megafauna as MG
    raw = _raider_raw()
    raw["lineage"][1]["war_x"] = 0.5
    t = SP.parse(raw)
    assert t.lines["kob"].war_x == 0.5 and t.lines["folk"].war_x == 1.0 and SP.parse(SP.to_raw(t)).lines["kob"].war_x == 0.5
    with pytest.raises(ValueError):
        SP.parse({**raw, "lineage": [{**r, "war_x": -1} if r["id"] == "folk" else r for r in raw["lineage"]]})
    ag = SP.parse({**_raider_raw(), "lineage": [{**r, "traits": ["aggressive"]} if r["id"] == "folk" else r for r in _raider_raw()["lineage"]]})
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    ha = H.History(ag, ps, 1)
    ha._counter_setup()
    assert ha._war_a[ha.idx["folk"]] == HP.AGGRESSIVE_X and ha._war_a[ha.idx["kob"]] == 1.0
    h, env, step = _brake_setup(faketz)
    L = h.lines
    kb, fk = h.idx["kob"], h.idx["folk"]
    land = np.flatnonzero(env["land"])
    K = np.where(env["land"], 0.8, 0.0)
    h.tree.raiders = 0.0
    h.p[kb][land[:200]] = 0.8
    h.p[fk][land[180:400]] = 0.8
    _sync_pm(h)
    h.rule.hem[:] = 0.0
    monkeypatch.setattr(HP, "TROUBLE_SHARE", 0.0)
    monkeypatch.setattr(HP, "WAR_N0", 1e9)  # (the frontier term alone: the war hazard is linear in the dials below saturation)
    h._brake(L[kb], kb, K, step, env, None)
    base = h.lost["kob"]["war"]
    assert 0 < base < 0.5 * HP.LAND_Q
    h._war_a[kb] *= 2.0  # (as the aggressive trait does)
    h._brake(L[kb], kb, K, step, env, None)
    assert h.lost["kob"]["war"] == pytest.approx(2 * base, rel=0.05)
    h._war_a[kb] /= 2.0
    lev = MG.tech_level(h.tree.era, step.ago)
    h.tree.war_early, h.tree.war_late = 0.0, 2.0
    assert h._war_era(step) == pytest.approx(2.0 * lev)
    h.tree.war_early = h.tree.war_late = 0.0
    h._brake(L[kb], kb, K, step, env, None)
    assert h.lost.get("kob", {}).get("war", 0.0) == 0.0
    h.tree.war_early = h.tree.war_late = 1.0
    # times of troubles: certain this step, the hazard x TROUBLE_X, an event, and the people driven off push refugees
    monkeypatch.setattr(HP, "TROUBLE_SHARE", 1e6)
    monkeypatch.setattr(HP, "TROUBLE_H", 0.0)
    n0 = len(h.events)
    Kt = h._brake(L[kb], kb, K, step, env, None)
    assert h.lost["kob"]["war"] > 2 * base
    assert h.troubles_n["kob"] == 1 and any(e["kind"] == "troubles" for e in h.events[n0:])
    assert h._refugee[kb] > 0 and h._refugees(kb) == pytest.approx(HP.REFUGEE_Q * h._refugee[kb])
    monkeypatch.setattr(HP, "TROUBLE_SHARE", 0.0)
    h.p[kb] = np.minimum(h.p[kb], Kt)
    _sync_pm(h)
    h._brake(L[kb], kb, K, step, env, None)
    assert h._refugee[kb] == 0.0  # (a loss it has settled under drives no one off)
