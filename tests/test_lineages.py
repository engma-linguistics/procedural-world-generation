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
    assert {"elf", "human", "half_elf", "tiefling", "kobold", "aarakocra", "titan"} <= dnd.lines.keys()
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
    assert C.modes(walker, 1.0) == [("raft",) + SP.HOPS["raft"][:2]]
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
