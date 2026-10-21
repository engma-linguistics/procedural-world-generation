"""Game export (PW-100): tiles, class maps, splat weights, features, manifest, on a
synthetic level-4 world and a synthetic zoom (no simulation)."""

import json
import struct
import zlib

import numpy as np
import pytest

from planet import export as X
from planet import store as S
from planet.geo import R_KM
from planet.grid import build_grid
from planet.images import write_png
from planet.tectonics.volcanism import COLUMNS


def read_png(path):
    """The array of a PNG made by images.write_png (filter 0 only)."""
    b = path.read_bytes()
    assert b[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, ihdr = 8, b"", None
    while pos < len(b):
        n, tag = struct.unpack(">I4s", b[pos:pos + 8])
        body = b[pos + 8:pos + 8 + n]
        if tag == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    w, h, bits, ctype = ihdr[:4]
    ch = {0: 1, 2: 3, 6: 4}[ctype]
    raw = np.frombuffer(zlib.decompress(idat), np.uint8).reshape(h, 1 + w * ch * bits // 8)
    assert (raw[:, 0] == 0).all()
    a = raw[:, 1:]
    if bits == 16:
        a = a.reshape(h, w, 2).astype(np.uint16)
        return a[..., 0] * 256 + a[..., 1]
    return a.reshape(h, w) if ch == 1 else a.reshape(h, w, ch)


def assemble(layer, root, shape):
    out = None
    for f in layer["files"]:
        t = read_png(root / f["file"])
        if out is None:
            out = np.zeros(shape + t.shape[2:], t.dtype)
        out[f["y"]:f["y"] + f["height"], f["x"]:f["x"] + f["width"]] = t
    return out


def quiet(*a):
    pass


def test_png_modes(tmp_path):
    for img in (np.arange(12, dtype=np.uint8).reshape(3, 4),
                np.random.default_rng(1).integers(0, 255, (3, 4, 4), dtype=np.uint8),
                np.arange(12, dtype=np.uint16).reshape(3, 4) * 5000):
        write_png(tmp_path / "x.png", img)
        assert (read_png(tmp_path / "x.png") == img).all()


def test_splat_weights():
    z = np.zeros((1, 4))
    one = np.ones((1, 4))
    slope = np.array([[0.0, 60.0, 0.0, 0.0]])
    ice = np.array([[0.0, 0.0, 50.0, 0.0]])
    water = np.array([[0, 0, 0, 1]], np.uint8)
    w = X.splat_weights(slope, ice, 0.6 * one, 0.9 * one, 800 * one, 12 * one, z, water)
    assert w.dtype == np.uint8 and w.shape == (1, 4, 8)
    assert (w.sum(-1)[0, :3] == 255).all() and (w[0, 3] == 0).all()
    names = [n for n, _ in X.SPLAT]
    assert w[0, 0].argmax() == names.index("forest")
    assert w[0, 1].argmax() == names.index("rock")
    assert w[0, 2].argmax() == names.index("snow")
    dry = X.splat_weights(z, z, z, z, 50 + z, 25 + z, z, np.zeros((1, 4), np.uint8))
    assert dry[0, 0].argmax() == names.index("sand")


def test_river_lines_join_at_confluences():
    # 0 -> 2 -> 3 -> 4 (sea), 1 -> 2: lines 0-2, 1-2 and 2-3-4
    nxt = np.array([2, 2, 3, 4, -1])
    q = np.array([1.0, 2.0, 3.0, 3.0, 0.0])
    lines = X.river_lines(nxt, q, np.array([1, 1, 1, 1, 0], bool))
    assert sorted(tuple(r["nodes"]) for r in lines) == [(0, 2), (1, 2), (2, 3, 4)]
    assert {tuple(r["nodes"]): r["q"] for r in lines}[(2, 3, 4)] == 3.0


@pytest.fixture
def world(data_root):
    g = build_grid(4)
    lat, lon = np.radians(g.lat), np.radians(g.lon)
    elev = np.round(2500 * np.sin(3 * lon) * np.cos(2 * lat) - 400).astype(float)
    down = np.full(g.n, -1)
    for i in range(g.n):
        nb = g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]
        j = nb[np.argmin(elev[nb])]
        if elev[i] > 0 and elev[j] < elev[i]:
            down[i] = j
    L = {"elevation": elev, "ice": np.where(g.lat > 80, 40.0, 0.0), "biome": np.where(elev > 0, 9, 0),
         "vegetation": np.where(elev > 0, 12, 0), "surface_rock": np.full(g.n, 3), "tree_cover": np.full(g.n, 60.0),
         "plant_cover": np.full(g.n, 90.0), "precipitation": np.full(g.n, 900.0), "temperature": np.full(g.n, 12.0),
         "flooded": np.zeros(g.n), "flow": np.where(down >= 0, 0.2, 0.0), "downstream": down,
         "lake": (elev < -50) & (elev > -80)}
    meta = {"level": 4, "source_run": "r1", "t_myr": 12.0, "seed": 1, "sea_level_m": 3.0, "global_temp_c": 14.0,
            "volcano_columns": list(COLUMNS),
            "volcanoes": [[10.0, 20.0, 0, 1.0, 1, 1200, 0, 1500, 10.0, 100.0, 0, 0.0]], "hotspots": []}
    S.worlds_dir().mkdir(parents=True, exist_ok=True)
    (S.worlds_dir() / "tw1.json").write_text(json.dumps(
        {"format": "x", "name": "synthetic", "id": "tw1", "meta": meta,
         "layers": {k: np.asarray(v).tolist() for k, v in L.items()}}))
    return L


def test_export_world(world, data_root, tmp_path):
    out = X.export("tw1", tmp_path / "w", res=128, tile=64, overlap=1, cube=16, highlights=False, log=quiet)
    m = json.loads((out / "manifest.json").read_text())
    assert m["format"] == X.FORMAT and m["kind"] == "world" and m["source"]["world"]["source_run"] == "r1"
    assert m["sea_level_m"] == 0 and m["units"]["height"] == "m" and m["scale"]["planet_radius_km"] == R_KM
    eq = m["layouts"]["equirect"]
    assert (eq["width"], eq["height"]) == (128, 64) and eq["deg_per_px"] == 360 / 128
    hm = eq["layers"]["heightmap"]
    # 128 px in 64 px tiles sharing 1 px: columns start at 0, 63, 126 (the last is 2 px wide)
    assert sorted({f["x"] for f in hm["files"]}) == [0, 63, 126] and len(hm["files"]) == 3
    h = assemble(hm, out, (64, 128))
    lo, hi = hm["min_m"], hm["max_m"]
    elev = lo + h / 65535 * (hi - lo)
    assert abs(hm["metres_per_step"] - (hi - lo) / 65535) < 1e-3
    assert 0 <= hm["sea_level_value"] <= 65535
    assert elev.min() >= -2900 and elev.max() <= 2100 and elev.max() > 1500
    # sea level maps to the same value: the pixels the water map calls sea are at or below it
    water = assemble(eq["layers"]["water"], out, (64, 128))
    assert (h[water == 1] <= hm["sea_level_value"]).all() and set(np.unique(water)) <= {0, 1, 2} and (water == 2).any()
    # splat: 255 on land, 0 on water, over its two files
    s = np.concatenate([assemble(eq["layers"][f"splat_{i}"], out, (64, 128)) for i in range(2)], -1).astype(int)
    assert (s.sum(-1)[water == 0] == 255).all() and (s.sum(-1)[water > 0] == 0).all()
    assert assemble(eq["layers"]["biome"], out, (64, 128)).max() <= 9
    cube = m["layouts"]["cube"]
    assert set(cube["layers_by_face"]) == set(X.CUBE_FACES) and cube["size"] == 16
    pz = read_png(out / cube["layers_by_face"]["pz"]["heightmap"]["files"][0]["file"])
    assert pz.shape == (16, 16)
    geo = json.loads((out / "features.geojson").read_text())
    kinds = {f["properties"]["kind"] for f in geo["features"]}
    assert {"river", "lake", "volcano"} <= kinds
    for f in geo["features"]:
        pts = [f["geometry"]["coordinates"]] if f["geometry"]["type"] == "Point" else f["geometry"]["coordinates"]
        assert all(-90 <= p[1] <= 90 and -361 <= p[0] <= 361 for p in pts)
    v = next(f for f in geo["features"] if f["properties"]["kind"] == "volcano")
    assert v["geometry"]["coordinates"] == [20.0, 10.0] and v["properties"]["status"] == "active"
    r = [f for f in geo["features"] if f["properties"]["kind"] == "river"]
    assert r and all(f["properties"]["discharge_m3s"] >= X.RIVER_MIN_M3S["world"] for f in r)
    legend = json.loads((out / "legend.json").read_text())
    assert len(legend["splat"]) == 8 and eq["layers"]["splat_0"]["legend"] == "splat"


def test_export_world_untiled_raw(world, data_root, tmp_path):
    out = X.export("world:tw1", tmp_path / "w", res=64, tile=0, raw=True, highlights=False, log=quiet)
    m = json.loads((out / "manifest.json").read_text())
    f = m["layouts"]["equirect"]["layers"]["heightmap"]["files"]
    assert len(f) == 1 and f[0]["file"] == "heightmap.r16" and (out / f[0]["file"]).stat().st_size == 64 * 32 * 2
    assert (out / "water.png").exists()


@pytest.fixture
def zoom(data_root):
    ny, nx, res = 40, 60, 2.0
    yy, xx = np.mgrid[0:ny, 0:nx]
    elev = np.maximum(300 - 8.0 * (xx - 20) ** 2 / 20 + 0 * yy, -50).astype(np.float32)
    water = (elev <= 0).astype(np.uint8)
    water[30:33, 5:8] = 2
    rec = np.full((ny, nx), 4, np.uint8)  # everything flows east
    rec[:, -1] = 255
    q = np.where(yy == 10, 25.0, 0.0).astype(np.float32)
    layers = {"elevation": elev, "water": water, "discharge": q, "receiver": rec,
              "tree_cover": np.full((ny, nx), 50, np.uint8), "plant_cover": np.full((ny, nx), 80, np.uint8),
              "ice": np.zeros((ny, nx), np.float32), "lake_depth": np.where(water == 2, 4.0, 0.0).astype(np.float32),
              "biome": np.full((ny, nx), 9, np.uint8)}
    d = S.path_of("zoom", "tz1")
    d.mkdir(parents=True)
    layout = S.write_layers(d, layers, {k: {"units": "x", "description": k} for k in layers})
    meta = {"format": "procgen-zoom/2", "id": "tz1", "name": "tz", "created": "now", "seed": 1,
            "source_world": {"id": "w", "source_run": "r"}, "center": {"lat": 10.0, "lon": 20.0},
            "size_km": nx * res, "res_km": res, "nx": nx, "ny": ny, "layers": layout, "params": {},
            "projection": {"type": "azimuthal_equidistant", "lat0": 10.0, "lon0": 20.0, "planet_radius_km": R_KM,
                           "corners_latlon": {}},
            "stats": {"falls": [{"lat": 10.1, "lon": 20.1, "height_m": 40.0, "discharge_m3s": 30.0, "kind": "lip",
                                 "length_km": 2.0, "from_lake": False}],
                      "volcanoes": [], "deltas": []}}
    (d / "zoom.json").write_text(json.dumps(meta))
    return layers, res


def test_export_zoom(zoom, data_root, tmp_path):
    layers, res = zoom
    out = X.export("tz1", tmp_path / "z", tile=32, highlights=False, log=quiet)
    m = json.loads((out / "manifest.json").read_text())
    lay = m["layouts"]["native"]
    assert (lay["width"], lay["height"], lay["m_per_px"]) == (60, 40, 2000.0) and m["source"]["zoom"]["id"] == "tz1"
    hm = lay["layers"]["heightmap"]
    h = assemble(hm, out, (40, 60))
    e = hm["min_m"] + h / 65535 * (hm["max_m"] - hm["min_m"])
    assert np.abs(e - layers["elevation"]).max() <= hm["metres_per_step"] + 1
    assert len(hm["files"]) == 4
    # a river along row 10 flowing east to the sea at col 48, in metres from the zoom's centre
    loc = json.loads((out / "features_local.geojson").read_text())
    riv = [f for f in loc["features"] if f["properties"]["kind"] == "river"]
    assert len(riv) == 1
    c = np.array(riv[0]["geometry"]["coordinates"])
    assert len(c) == 49 and np.allclose(c[:, 1], (20 - 10 - 0.5) * 2000, atol=2)
    assert np.allclose(np.diff(c[:, 0]), 2000, atol=5) and abs(c[0, 0] - (0.5 - 30) * 2000) < 5
    assert abs(c[5, 2] - layers["elevation"][10, 5]) < 2 and loc["units"] == "m"
    assert {"river", "lake", "waterfall"} <= {f["properties"]["kind"] for f in loc["features"]}
    lake = next(f for f in loc["features"] if f["properties"]["kind"] == "lake")
    assert lake["properties"]["area_km2"] == 9 * res**2 and lake["properties"]["max_depth_m"] == 4.0
    geo = json.loads((out / "features.geojson").read_text())
    fall = next(f for f in geo["features"] if f["properties"]["kind"] == "waterfall")
    assert fall["geometry"]["coordinates"] == [20.1, 10.1] and "elevation_m" in fall["properties"]


def test_export_zoom_coarser_and_errors(zoom, data_root, tmp_path):
    out = X.export("zoom:tz1", tmp_path / "z2", res=4.0, tile=0, highlights=False, log=quiet)
    m = json.loads((out / "manifest.json").read_text())
    assert (m["layouts"]["native"]["width"], m["layouts"]["native"]["m_per_px"]) == (30, 4000.0)
    geo = json.loads((out / "features.geojson").read_text())
    assert any(f["properties"]["kind"] == "river" for f in geo["features"])
    with pytest.raises(SystemExit):
        X.export("tz1", tmp_path / "z3", cube=32, highlights=False, log=quiet)
    with pytest.raises(SystemExit):
        X.export("nope", tmp_path / "z4", log=quiet)


# --- projected maps (PW-477) -------------------------------------------------
@pytest.mark.parametrize("proj", ["equirect", "equal-earth", "mollweide", "laea", "aeqd", "ortho", "stereo"])
def test_export_world_projected(world, data_root, tmp_path, proj):
    from planet import projection as PJ
    from planet import world as W
    out = X.export("tw1", tmp_path / proj, res=96, tile=0, projection=proj, center="35,-100", highlights=False,
                   log=quiet)
    m = json.loads((out / "manifest.json").read_text())
    lay = m["layouts"]["map"]
    assert "equirect" not in m["layouts"] and lay["projection"] == proj and lay["center"] == {"lat": 35.0, "lon": -100.0}
    shape = (lay["height"], lay["width"])
    cov = assemble(lay["layers"]["coverage"], out, shape) > 0
    hm = lay["layers"]["heightmap"]
    h = assemble(hm, out, shape)
    water = assemble(lay["layers"]["water"], out, shape)
    assert lay["nodata"]["heights"] == 0 and hm["nodata"] == 0 and lay["nodata"]["ids"] == X.NODATA_ID
    assert (h[~cov] == 0).all() and (h[cov] >= 1).all()
    assert (water[~cov] == X.NODATA_ID).all() and (water[cov] < 3).all()
    if proj != "ortho" and proj != "stereo":
        assert 0.5 < cov.mean() <= 1.0
    # the centre pixel sees the centre point: smooth heights are near the nearest cell's (level-4 cells ~700 km)
    g = PJ.pixel_grid(PJ.Projection(proj, 35, -100), 96)
    mid = g["pts"].reshape(shape + (3,))[shape[0] // 2, shape[1] // 2]
    wd = W.load(S.find("world", "tw1"))
    near = wd["grid"].locate(mid[None])[0]
    e = hm["min_m"] + h[shape[0] // 2, shape[1] // 2] / 65535 * (hm["max_m"] - hm["min_m"])
    assert abs(e - wd["layers"]["elevation"][near]) < 900
    fm = json.loads((out / "features_map.geojson").read_text())
    assert fm["units"] == "m" and m["features"]["map_geojson"] == "features_map.geojson"
    for f in fm["features"]:
        pts = [f["geometry"]["coordinates"]] if f["geometry"]["type"] == "Point" else f["geometry"]["coordinates"]
        if f["geometry"]["type"] == "MultiLineString":
            pts = [p for r in pts for p in r]
        assert all(abs(p[0]) <= lay["x_range_m"][1] + 1 and abs(p[1]) <= lay["y_range_m"][1] + 1 for p in pts)


def test_export_world_regional_extent_and_classes(world, data_root, tmp_path):
    out = X.export("tw1", tmp_path / "r", res=40, tile=0, projection="laea", center="10,20", extent="3000km",
                   highlights=False, log=quiet)
    m = json.loads((out / "manifest.json").read_text())
    lay = m["layouts"]["map"]
    assert (lay["width"], lay["height"]) == (40, 40) and lay["extent_km"] == [3000.0, 3000.0]
    assert lay["x_range_m"][1] == pytest.approx(1.5e6) and "+proj=laea +lat_0=10 +lon_0=20" in lay["proj"]
    assert assemble(lay["layers"]["coverage"], out, (40, 40)).all()
    bio = assemble(lay["layers"]["biome"], out, (40, 40))
    assert set(np.unique(bio)) <= {0, 9}  # class maps are looked up, never blended
    f = json.loads((out / "features_map.geojson").read_text())["features"]
    v = next(f_ for f_ in f if f_["properties"]["kind"] == "volcano")
    assert v["geometry"]["coordinates"][:2] == pytest.approx([0, 0], abs=1)  # (10N 20E is the centre)
    assert m["provenance"]["args"]["projection"]["projection"] == "laea"
    with pytest.raises(SystemExit):
        X.export("tw1", tmp_path / "bad", projection="ortho", center="95,0", highlights=False, log=quiet)
    with pytest.raises(SystemExit):
        X.export("tw1", tmp_path / "bad2", extent="10 furlongs", highlights=False, log=quiet)


def test_export_zoom_projected(zoom, data_root, tmp_path):
    layers, res = zoom
    out = X.export("tz1", tmp_path / "zp", projection="aeqd", tile=0, highlights=False, log=quiet)
    m = json.loads((out / "manifest.json").read_text())
    lay = m["layouts"]["map"]
    assert (lay["width"], lay["height"]) == (60, 60) and lay["projection"] == "aeqd"
    cov = assemble(lay["layers"]["coverage"], out, (60, 60)) > 0
    hm = lay["layers"]["heightmap"]
    h = assemble(hm, out, (60, 60))
    e = hm["min_m"] + h / 65535 * (hm["max_m"] - hm["min_m"])
    # the 120 x 80 km zoom fills 40 of the 60 rows of its 120 km square map; the rest is nodata
    assert cov[10:50].mean() > 0.95 and not cov[:8].any() and not cov[52:].any()
    rows, cols = np.nonzero(cov[10:50])
    assert np.abs(e[10:50][rows, cols] - layers["elevation"][rows, cols]).max() < 30
    assert (h[~cov] == 0).all()
    fm = json.loads((out / "features_map.geojson").read_text())
    assert any(f["properties"]["kind"] == "river" for f in fm["features"])
