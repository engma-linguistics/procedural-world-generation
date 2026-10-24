"""Lineages lane (docs/proposals/lineages.md): the recent pass and the peoples' history,
on a small fake time zoom (level 3) in a temporary store."""

from __future__ import annotations

import json

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
from planet.lineages import output as O  # noqa: E402
from planet.lineages import run as LR  # noqa: E402
from planet.lineages import spec as SP  # noqa: E402


def _raw():
    return {"meta": {"name": "t", "seed": 2, "mixing_start": "3 kyr"}, "lineage": [
        {"id": "stem", "origin": "root", "at": "30 kyr", "temp_c": [5, 30], "rain_mm": [100, 5000]},
        {"id": "a", "parents": ["stem"], "at": "20 kyr"},
        {"id": "b", "parents": ["stem"], "at": "15 kyr", "traits": ["swims"]},
        {"id": "fey", "origin": "arrival", "at": "10 kyr", "place": [0, 120]},
        {"id": "half", "origin": "hybrid", "parents": ["a", "fey"], "at": "8 kyr"},
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
    assert run["meta"]["phase"] == "lineages" and run["frames"][-1]["t"] == 0
    assert [l["id"] for l in run["meta"]["lineages"]] == [l.id for l in h.lines]
    _, arr = T.load_frames(out, ("peoples",))
    assert arr["peoples"].shape[0] == len(run["frames"])


def test_a_stem_cut_off_from_its_children_carries_on_as_one_of_them(faketz):
    """PW-677: when a stem ends, the part of its range joined to no child (another landmass) goes to the child
    whose niche suits it, instead of vanishing with the stem."""
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
    h.p[h.idx["a"]][west] = 1.0  # the child 'a' lives on the west continent only; 'b' is not yet alive
    h.active["stem"] = h.active["a"] = True
    h._end_parent(h.tree.lines["stem"], step, env, tags)
    assert not (h.p[h.idx["stem"]] > 0).any()
    assert (h.p[h.idx["a"]][east] > H.EST).mean() > 0.5  # the cut-off east stock carried on as 'a'


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
                       {"id": "ab", "origin": "hybrid", "parents": ["a", "b"], "at": "20 kyr"}]}
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
                        "density": 1e-5, "traits": ["insular"]},
                       {"id": "g2", "parents": ["g"], "at": "10 kyr"},
                       {"id": "f", "origin": "root", "at": "30 kyr", "temp_c": [-20, 40], "rain_mm": [1, 9000],
                        "traits": ["agricultural", "seafaring"], "band_km2": 2.5}]}
    t = SP.parse(raw)
    assert t.lines["g2"].demo("density") == 1e-5 and t.lines["g"].demo("insularity") == SP.DEMOGRAPHY["insular"]["insularity"]
    assert t.lines["f"].demo("density") == 10.0 and t.lines["f"].demo("sea_share") == 0.6
    assert SP.parse(SP.to_raw(t)).lines["g2"].density == 1e-5
    assert C.hop_mult(t.lines["f"]) > 2 * C.hop_mult(t.lines["g"])
    with pytest.raises(ValueError):
        SP.parse({"lineage": [{"id": "x", "origin": "root", "at": "1 kyr", "sea_share": 2}]})
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h = H.History(t, ps, 1)
    h.p = np.zeros((len(h.lines), h.grid.n))
    h.faded = {}
    env = ps.fields(0.0, variability=False)
    k = h.idx["g"]
    big = env["land"] & (np.abs(h.grid.lon) < 50)
    small = env["land"] & (h.grid.lon < -100) & (h.grid.lon > -140)  # the fake island
    h.p[k][big | small] = 0.5
    h._viable(t.lines["g"], k, 4.0, None)
    assert (h.p[k][big] == 0.5).all() and not (h.p[k][small] > 0).any()
    pop = h.population(k)
    assert abs(pop.sum() - 0.5 * big.sum() * 1e-5 * h.cell_mkm2 * 1e6) < 1e-6 * pop.sum()
    _, _, pres = H.simulate(t, ps, tries=1)
    assert pres["lines"]["f"]["population"] > 100 * pres["lines"].get("g2", {"population": 1})["population"]
    first = [m for m in pres["landmasses"] if m["discovered"]]
    assert first and all(m["discovered"]["by"] in t.lines for m in first)


def test_groups_within_a_people(faketz):
    """PW-665: a group is a way of life within a people (origin 'group', group_of): it inherits what it leaves
    out (demography too), never ends its people, appears where its own niche beats its people's, mixes with it
    as kin (no closed-country exclusion), keeps a range of its own, and rolls up into its people in the summaries."""
    raw = {"meta": {"name": "g", "seed": 3},
           "lineage": [{"id": "orc", "origin": "root", "at": "30 kyr", "temp_c": [0, 18], "rain_mm": [1, 9000], "density": 1.5},
                       {"id": "warm_orc", "origin": "group", "group_of": "orc", "at": "10 kyr", "temp_c": [16, 32]},
                       {"id": "elf", "origin": "root", "at": "30 kyr", "temp_c": [0, 18], "rain_mm": [1, 9000]},
                       {"id": "half", "origin": "hybrid", "parents": ["orc", "elf"], "at": "5 kyr"}],
           "wish": [{"a": "elf", "b": "orc", "want": "apart"}]}
    t = SP.parse(raw)
    g = t.lines["warm_orc"]
    assert g.origin == "group" and g.group_of == "orc" and t.groups_of("orc") == ["warm_orc"] and t.people_of("warm_orc") == "orc"
    assert g.demo("density") == 1.5 and g.rain_mm == (1.0, 9000.0) and t.lines["orc"].children == []
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
    assert h.alpha[i, j] < H.niche_overlap(g, t.lines["orc"], t)  # (kin: GROUP_KIN of the overlap)
    h, res, pres = H.simulate(t, ps, tries=1)
    assert "orc" not in h.ended and "warm_orc" in h.origins
    assert h.origins["warm_orc"]["why"].startswith("where its way of life")
    P = res["present"]
    po, pg = P[h.idx["orc"]] >= H.EST, P[h.idx["warm_orc"]] >= H.EST
    assert po.any() and pg.any()
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


def test_peoples_change_the_land_from_their_ways_of_life():
    """PW-662: shares come from the [[use]] table, not names; fields, pasture, fire and woods follow the people."""
    from planet.lineages import landuse as LU
    t = SP.load(LR.tree_path("dnd"))
    s = {k: LU.shares(t, t.lines[k]) for k in ("human_farmer", "human_herder", "steppe_orc", "dwarf")}
    assert s["human_farmer"]["farm"] == 1 and s["human_herder"]["herd"] == 1 and s["steppe_orc"]["herd"] == 1
    assert sum(s["dwarf"].values()) == 0  # (miners eat nothing the land grows here: no clearing)
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
    assert b("human_herder")["milk"] and b("steppe_orc")["milk"] and not b("human")["milk"] and not b("human_farmer")["milk"]
    assert set(b("tabaxi")["toxic"]) == {"alliums", "theobromine"} and b("human")["toxic"] == []
    assert dnd.lines["tabaxi"].body_given == {}  # (inherited from the feline stem, not given)
    assert SP.parse(SP.to_raw(dnd)).lines["steppe_orc"].body == b("steppe_orc")
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
    dnd = SP.load(LR.SAMPLES / "dnd.toml")
    assert 0 < dnd.lines["human_herder"].body["milk"] < 1 and dnd.share_traits() == ["milk"]
    assert "60% digest milk as adults" in SP.body_notes(dnd.lines["human_herder"].body)
    assert SP.parse(SP.to_raw(dnd)).lines["human_herder"].body["milk"] == dnd.lines["human_herder"].body["milk"]
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


def _animal_tree(animals=("horse",), force=(), mode="fantasy"):
    raw = {"meta": {"name": "h", "seed": 3, "mixing_start": "3 kyr", "mode": mode, "animals": list(animals), "animals_force": list(force),
                    "animals_at": {"horse": "9 kyr", "dog": "20 kyr", "great_elk": "9 kyr"}}, "lineage": [
        {"id": "herd", "origin": "root", "at": "30 kyr", "temp_c": [-5, 35], "rain_mm": [50, 6000], "traits": ["nomadic"], "real": True},
        {"id": "farm", "origin": "root", "at": "30 kyr", "temp_c": [-5, 35], "rain_mm": [50, 6000], "traits": ["agricultural"], "real": True}],
        "use": [{"by": "nomadic", "good": "grazing"}, {"by": "agricultural", "good": "fertile"}]}
    return SP.parse(raw)


def test_horses_are_tamed_where_herders_meet_the_wild_range_and_riding_spreads(faketz, monkeypatch):
    import dataclasses
    from planet.lineages import animal_defs as AD
    wild = lambda env, tags, land: np.where(land & (np.abs(env["temperature"] - 12) < 8), 0.9, 0.0)  # noqa: E731
    horse = dataclasses.replace(AD.BY_ID["horse"], wild=wild)
    monkeypatch.setattr(AD, "TABLE", tuple(horse if a.id == "horse" else a for a in AD.TABLE))
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=1))
    h, res, pres = H.simulate(_animal_tree(), ps, tries=1)
    hs = pres["animals"]["stocks"]["horse"]
    t = hs["tamed"][0]
    assert t["line"] == "herd" and t["first"] and t["ago_kyr"] <= hs["date_drawn_kyr"] + 1e-6 and hs["wild_mkm2"] > 0
    assert hs["known_mkm2"] > 0 and hs["users_share"]["herd"] > 0.5  # herders ride across their land
    assert hs["propensity"]["herd"] == 1.0 and hs["propensity"]["farm"] < hs["propensity"]["herd"]
    assert any(e["kind"] == "animals" for e in h.events) and not hs["fantasy"]
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
        {"id": "half", "origin": "hybrid", "parents": ["human", "elf"], "at": "2 kyr"},
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
    assert real.mode == "real" and set(real.lines) == {"archaic_human", "human", "human_farmer", "human_herder", "human_nomad",
                                                       "human_seafarer", "human_arctic"}
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
    assert {"crop_wild", "crop_known"} <= run["layers"].keys() and run["layers"]["crop_known"]["dtype"] == "uint16"
    assert any(e["kind"] == "crops" for e in h.events) and "first to cultivate wheat and barley" in run["meta"]["lineages"][h.idx["farm"]]["story"]
    assert "Crops (PW-721)" in (out / "run.txt").read_text()


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
