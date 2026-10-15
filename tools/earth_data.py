"""Real-Earth reference data, mapped onto the icosphere grid.

Used by tools/earth_check.py to run the climate model on Earth's actual
geography and compare it with observations.

Sources (all downloaded once, then cached under data/earth/; ~25 MB total)
---------------------------------------------------------------------------
Elevation
    ETOPO1 Global Relief Model (Amante & Eakins 2009, NOAA NGDC,
    doi:10.7289/V5C8276M), 1 arc-minute, two variants:
      "Bedrock"     - base of the ice sheets          (ERDDAP id etopo1_bedrock)
      "Ice Surface" - top of Greenland/Antarctic ice  (ERDDAP id etopo1_ice)
    Fetched through NOAA's ERDDAP server as OPeNDAP binary (.dods) with a
    stride of 10, i.e. a 1/6 degree point-sampled grid (1081 x 2161):
      https://upwell.pfeg.noaa.gov/erddap/griddap/etopo1_bedrock.dods?z[0:10:10800][0:10:21600]
    (upwell redirects to the PacIOOS ERDDAP mirror, which is fine.)
    Licence: US-government public domain ("may be used and redistributed
    for free"; cite Amante & Eakins 2009).

Observed Koppen-Geiger classes
    Kottek, Grieser, Beck, Rudolf & Rubel (2006), "World Map of the
    Koppen-Geiger climate classification updated", Meteorol. Z. 15, 259-263.
    0.5 degree ASCII, 1951-2000 climate (CRU TS2.1 temperature, GPCC VASClimO
    precipitation); includes Antarctica (all EF).
      https://koeppen-geiger.vu-wien.ac.at/data/Koeppen-Geiger-ASCII.zip
    Free for scientific use with citation. Kottek uses the same C/D boundary
    (coldest month -3 C) and the same aridity thresholds as planet/climate.py,
    so its classes are directly comparable. Its "As" class (dry-summer
    savanna) has no counterpart in the model and is scored as Aw.

Observed precipitation
    GPCC Full Data Reanalysis v2018, 1.0 deg monthly long-term mean
    (land only; Schneider et al.), ERDDAP id noaa_psl_7959_51e3_b7dd.
    GPCP v2.3 combined land+ocean, 2.5 deg monthly long-term mean 1991-2020
    (mm/day; Adler et al. 2018), from NOAA PSL THREDDS (the ERDDAP copies of
    the GPCP/CMAP climatologies have a broken precip variable):
      https://psl.noaa.gov/thredds/dodsC/Datasets/gpcp/precip.mon.ltm.1991-2020.nc
Observed temperature
    NCEP/NCAR Reanalysis 1, 2 m air temperature 1981-2010 monthly long-term
    mean (T62 Gaussian grid, ~1.9 deg; Kalnay et al. 1996), ERDDAP id
    noaa_psl_4835_64f9_2242. Reanalysis, so expect ~1-2 C local biases,
    worst over high/steep terrain; fine for zonal means.
All NOAA PSL data: "may be used and redistributed for free"; cite NOAA PSL.

Potential natural vegetation (tools/veg_check.py)
    Ramankutty & Foley (1999), "Estimating historical changes in global land
    cover: croplands from 1700 to 1992", Global Biogeochem. Cycles 13, 997.
    The vegetation that would be there without people, 15 classes, 5'
    ESRI ASCII grid (0.5 MB), SAGE / University of Wisconsin:
      https://sage-public-files.s3.amazonaws.com/global-potential-vegetation/glpotveg_5min.asc.gz
    Mapped as each cell's most common class (earth_potveg).
    (MODIS NPP, tree cover and GFED burned area need large downloads or an
    Earthdata login: the vegetation check uses published global numbers.)

Mapping to the grid
-------------------
Every ETOPO1 sample (1/6 deg) is assigned to its nearest icosphere cell with
cos(lat) area weights. A sample is land if its *ice surface* height is > 0
(so ice shelves count as land, and inland basins below sea level such as the
Caspian count as sea). A cell is land if its land fraction >= 0.5. Then:
  surface = weighted mean of the ice-surface height over the cell's land
            samples (sea cells: mean depth over sea samples, <= -1 m)
  ice     = weighted mean of (ice surface - bedrock) over land samples, i.e.
            real ice thickness from ETOPO1 (Greenland + Antarctica; mountain
            glaciers are not in ETOPO1 and get 0), but only where >= 50% of
            the cell's land is ice covered (else 0: the model turns any cell
            with ice > 0 into EF, which would ice over Greenland's coast)
  ice_frac  that ice-covered share of the cell's land
  elev    = surface - ice, floored at 1 m on land cells. The model treats
            `elev` as bare ground and adds `ice` itself, so elev + ice ==
            surface. Where the bedrock is below sea level (West Antarctica,
            central Greenland) the floor keeps the cell land and `ice` is
            reduced to keep elev + ice == surface. Approximate, but the
            model only uses surface height (temperature) and ice > 0.
Observed fields are sampled (nearest pixel) at each cell centre:
  obs_koppen    KOPPEN id (-1 where Kottek has no land), As -> Aw
  obs_temp, obs_t_warm, obs_t_cold   NCEP 2 m, annual mean / warmest / coldest month (C),
                interpolated at sea level and moved to the cell's height at 6.5 C/km
  obs_precip, obs_p_jul, obs_p_jan   GPCC land (mm/yr; NaN over sea/Antarctica);
                p_jul is the Apr-Sep rate, p_jan the Oct-Mar rate (as the model)
  obs_gpcp      GPCP annual precipitation, land + ocean (mm/yr)

Usage:
  PYTHONPATH=. uv run python tools/earth_data.py [--level 6]   # build cache
  from tools.earth_data import earth_on_grid; d = earth_on_grid(grid)
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "earth"
CACHE_VERSION = 4

ERDDAP = [
    "https://upwell.pfeg.noaa.gov/erddap/griddap/",
    "https://pae-paha.pacioos.hawaii.edu/erddap/griddap/",
    "https://coastwatch.pfeg.noaa.gov/erddap/griddap/",
]
KOTTEK_URL = "https://koeppen-geiger.vu-wien.ac.at/data/Koeppen-Geiger-ASCII.zip"

# name -> (ERDDAP dataset id, variable, index constraint)
RASTERS = {
    "etopo_bed": ("etopo1_bedrock", "z", "[0:10:10800][0:10:21600]"),
    "etopo_ice": ("etopo1_ice", "z", "[0:10:10800][0:10:21600]"),
    "gpcc": ("noaa_psl_7959_51e3_b7dd", "precip", "[0:1:11][0:1:179][0:1:359]"),
    "gpcp": ("https://psl.noaa.gov/thredds/dodsC/Datasets/gpcp/precip.mon.ltm.1991-2020.nc",
             "precip", "[0:1:11][0:1:71][0:1:143]"),
    "ncep_t2m": ("noaa_psl_4835_64f9_2242", "air", "[0:1:11][0:1:93][0:1:191]"),
    # clouds (earth_clouds): ship-observed cloudiness in oktas (ICOADS 2.5 enhanced, 2 deg,
    # 1981-2010 long-term mean) and the reanalysis' total cloud cover (%)
    "icoads_cldc": ("noaa_psl_1a7e_ae27_207f", "cldc", "[0:1:11][0:1:89][0:1:179]"),
    "ncep_tcdc": ("https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/other_gauss/"
                  "tcdc.eatm.mon.ltm.1991-2020.nc", "tcdc", "[0:1:11][0:1:93][0:1:191]"),
}
CRU_SUNP_URL = "https://crudata.uea.ac.uk/cru/data/hrg/tmc/grid_10min_sunp.dat.gz"
CLOUD_CACHE_VERSION = 1


# --------------------------------------------------------------------------
# downloading
# --------------------------------------------------------------------------
def _get(url: str, timeout: float = 300) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "procgen-world-earth-check"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.URLError as e:
        # Python's CA bundle can't verify some servers that the system curl
        # (macOS keychain) can, e.g. the Vienna Koppen site; fall back to curl
        if shutil.which("curl") is None:
            raise
        print(f"  urllib failed ({e.reason}); retrying with curl")
        return subprocess.run(["curl", "-sSfL", "-m", str(int(timeout)), url],
                              check=True, capture_output=True).stdout


_DTYPES = {"Float32": ">f4", "Float64": ">f8", "Int32": ">i4", "UInt32": ">u4",
           "Int16": ">i4", "UInt16": ">u4"}  # DAP2 sends 16-bit ints as 32-bit


def parse_dods(raw: bytes) -> list[tuple[str, np.ndarray]]:
    """Minimal OPeNDAP DAP2 binary (.dods) reader for numeric arrays/grids.
    Returns (name, array) in the order they appear (grid array, then maps)."""
    k = raw.index(b"\nData:\n")
    dds, body = raw[:k].decode("ascii", "replace"), raw[k + 7:]
    decls = re.findall(r"^\s*(Float32|Float64|Int32|UInt32|Int16|UInt16)\s+(\w+)((?:\[[^\]]+\])+);",
                       dds, re.M)
    out, pos = [], 0
    for typ, name, dims in decls:
        shape = tuple(int(x) for x in re.findall(r"=\s*(\d+)\]", dims))
        n1, n2 = np.frombuffer(body, ">u4", 2, pos)
        assert n1 == n2 == int(np.prod(shape)), (name, n1, shape)
        pos += 8
        dt = np.dtype(_DTYPES[typ])
        out.append((name, np.frombuffer(body, dt, n1, pos).reshape(shape).astype(dt.newbyteorder("="))))
        pos += n1 * dt.itemsize
    return out


def _fetch_raster(key: str) -> dict:
    ds, var, idx = RASTERS[key]
    q = f"{ds}.dods?{var}{idx}".replace("[", "%5B").replace("]", "%5D")
    bases = [""] if ds.startswith("https://") else ERDDAP
    err = None
    for base in bases:
        try:
            t0 = time.time()
            raw = _get(base + q)
            arrs = dict(parse_dods(raw))
            print(f"  {key}: {len(raw) / 1e6:.1f} MB from {base or ds.split("/")[2]} in {time.time() - t0:.0f}s")
            return {"val": arrs[var], "lat": arrs.get("latitude", arrs.get("lat")),
                    "lon": arrs.get("longitude", arrs.get("lon"))}
        except Exception as e:  # try the next mirror
            err = e
    raise RuntimeError(f"could not download {key}: {err}")


def raster(key: str) -> dict:
    """Cached raw lat/lon raster: dict(val, lat, lon)."""
    f = DATA / f"raw_{key}.npz"
    if not f.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        r = _fetch_raster(key)
        if key.startswith("etopo"):
            r["val"] = np.round(r["val"]).astype(np.int16)
        else:
            r["val"] = r["val"].astype(np.float32)
        np.savez_compressed(f, **r)
    z = np.load(f)
    return {k: z[k] for k in z.files}


# Kottek codes; index = id stored in raw_kottek.npz. "As" is kept here and
# folded into Aw when converted to the model's KOPPEN ids.
KOTTEK_CODES = ["Af", "Am", "As", "Aw", "BWh", "BWk", "BSh", "BSk", "Csa", "Csb", "Csc",
                "Cwa", "Cwb", "Cwc", "Cfa", "Cfb", "Cfc", "Dsa", "Dsb", "Dsc", "Dsd",
                "Dwa", "Dwb", "Dwc", "Dwd", "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF"]


def kottek() -> np.ndarray:
    """(360, 720) int8 index into KOTTEK_CODES, row 0 = 89.75 N, col 0 = 179.75 W;
    -1 where there is no land."""
    f = DATA / "raw_kottek.npz"
    if not f.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        zf = zipfile.ZipFile(io.BytesIO(_get(KOTTEK_URL)))
        txt = zf.read(zf.namelist()[0]).decode("ascii").split("\n")[1:]
        g = np.full((360, 720), -1, np.int8)
        lut = {c: i for i, c in enumerate(KOTTEK_CODES)}
        for line in txt:
            p = line.split()
            if len(p) != 3:
                continue
            la, lo = float(p[0]), float(p[1])
            g[int((90 - la) / 0.5), int((lo + 180) / 0.5)] = lut[p[2]]
        np.savez_compressed(f, cls=g)
    return np.load(f)["cls"]


def kottek_to_model_ids() -> np.ndarray:
    from planet.climate import KOPPEN
    ids = {code: i for i, code, _, _ in KOPPEN}
    return np.array([ids["Aw" if c == "As" else c] for c in KOTTEK_CODES])


# --------------------------------------------------------------------------
# mapping onto the grid
# --------------------------------------------------------------------------
def _unit(lat_deg, lon_deg):
    la, lo = np.radians(lat_deg), np.radians(lon_deg)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def _sample(r: dict, lat: np.ndarray, lon: np.ndarray, val: np.ndarray | None = None):
    """Nearest-pixel lookup of a regular(ish) lat/lon raster at points.
    Works for any monotonic lat axis (incl. Gaussian) and lon in 0..360 or +-180."""
    v = r["val"] if val is None else val
    yi, xi = _pixel(r, lat, lon)
    return v[..., yi, xi]


def _pixel(r: dict, lat: np.ndarray, lon: np.ndarray):
    """(row, column) of the raster pixel nearest to each point (see _sample)."""
    rl, ro = r["lat"].astype(float), r["lon"].astype(float)
    order = np.argsort(rl)
    j = np.searchsorted(rl[order], lat).clip(1, len(rl) - 1)
    j = np.where(np.abs(rl[order][j - 1] - lat) < np.abs(rl[order][j] - lat), j - 1, j)
    yi = order[j]
    lo = np.mod(lon - ro[0], 360.0)
    dlon = 360.0 / len(ro) if ro[-1] - ro[0] < 359.9 else (ro[1] - ro[0])
    xi = np.round(lo / dlon).astype(int) % len(ro)
    xi = np.minimum(xi, len(ro) - 1)
    return yi, xi


def _bilinear(r: dict, val: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Bilinear interpolation of a lat/lon raster (..., lat, lon) at points
    (monotonic lat axis incl. Gaussian, regular periodic lon). Beyond the
    first/last latitude row the edge row is used."""
    rl, ro = r["lat"].astype(float), r["lon"].astype(float)
    order = np.argsort(rl)
    rl, v = rl[order], val[..., order, :]
    j = np.searchsorted(rl, lat).clip(1, len(rl) - 1)
    fy = np.clip((lat - rl[j - 1]) / (rl[j] - rl[j - 1]), 0, 1)
    dlon = ro[1] - ro[0]
    x = np.mod(lon - ro[0], 360.0) / dlon
    x0 = np.floor(x).astype(int) % len(ro)
    x1 = (x0 + 1) % len(ro)
    fx = x - np.floor(x)
    a = v[..., j - 1, x0] * (1 - fx) + v[..., j - 1, x1] * fx
    b = v[..., j, x0] * (1 - fx) + v[..., j, x1] * fx
    return a * (1 - fy) + b * fy


def _build(grid) -> dict:
    n = grid.n
    bed, ice = raster("etopo_bed"), raster("etopo_ice")
    lat, lon = bed["lat"].astype(float), bed["lon"].astype(float)
    if abs(lon[-1] - lon[0] - 360) < 1e-6:  # drop duplicated 180 E column
        lon, b, s = lon[:-1], bed["val"][:, :-1], ice["val"][:, :-1]
    else:
        b, s = bed["val"], ice["val"]
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    w = np.cos(np.radians(LA)).ravel()
    # poles: one row of 2160 identical points; keep their tiny weight sane
    w = np.maximum(w, 1e-4)
    pts = _unit(LA.ravel(), LO.ravel())
    cell = grid.locate(pts)
    b, s = b.ravel().astype(float), s.ravel().astype(float)
    land = s > 0
    W = np.bincount(cell, w, n)
    Wl = np.bincount(cell, w * land, n)
    frac = Wl / np.maximum(W, 1e-12)
    surf_l = np.bincount(cell, w * land * s, n) / np.maximum(Wl, 1e-12)
    ice_l = np.bincount(cell, w * land * np.maximum(s - b, 0), n) / np.maximum(Wl, 1e-12)
    Ws = W - Wl
    surf_s = np.bincount(cell, w * ~land * s, n) / np.maximum(Ws, 1e-12)
    is_land = frac >= 0.5
    surface = np.where(is_land, surf_l, np.minimum(surf_s, -1.0))
    # ice-covered share of the land (ice thicker than 10 m, above ETOPO's
    # bed/surface rounding noise); the model makes every cell with ice > 0
    # an ice cap, so only cells that are mostly ice get any
    icy = np.bincount(cell, w * land * (s - b > 10), n) / np.maximum(Wl, 1e-12)
    ice_t = np.where(is_land & (icy >= 0.5), ice_l, 0.0)
    elev = surface - ice_t
    low = is_land & (elev < 1)
    elev[low] = 1.0
    ice_t[low] = np.maximum(surface[low] - 1.0, 0.0)
    # a land cell with no ETOPO samples can't happen at level <= 8 (1/6 deg
    # sampling is denser than the grid); guard anyway
    assert W.min() > 0, "cell without ETOPO samples: level too fine for the 1/6 deg cache"

    clat, clon = grid.lat, grid.lon
    out = dict(elev=elev.astype(np.float32), ice=ice_t.astype(np.float32),
               surface=surface.astype(np.float32), land_frac=frac.astype(np.float32),
               ice_frac=icy.astype(np.float32))

    # Kottek Koppen at cell centres (nearest 0.5 deg pixel)
    k = kottek()
    yi = np.clip(((90 - clat) / 0.5).astype(int), 0, 359)
    xi = np.clip(((clon + 180) / 0.5).astype(int), 0, 719)
    kc = k[yi, xi].astype(int)
    out["obs_koppen"] = np.where(kc >= 0, kottek_to_model_ids()[np.maximum(kc, 0)], -1).astype(np.int16)

    def seasonal(monthly, scale):  # (12, n) -> annual, Apr-Sep, Oct-Mar (per yr)
        m = monthly * scale
        ann = m.sum(0)
        jul = m[3:9].sum(0) * 2
        jan = (m[:3].sum(0) + m[9:].sum(0)) * 2
        return ann, jul, jan

    g = raster("gpcc")
    gv = np.where(np.abs(g["val"]) > 1e30, np.nan, g["val"])
    a, j_, n_ = seasonal(_sample(g, clat, clon, gv), 1.0)  # mm/month
    out["obs_precip"], out["obs_p_jul"], out["obs_p_jan"] = (x.astype(np.float32) for x in (a, j_, n_))

    p = raster("gpcp")
    pv = np.where(np.abs(p["val"]) > 1e30, np.nan, p["val"])
    days = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])[:, None]
    out["obs_gpcp"] = (_sample(p, clat, clon, pv) * days).sum(0).astype(np.float32)

    t = raster("ncep_t2m")
    tv = np.where(np.abs(t["val"]) > 1e30, np.nan, t["val"]) - 273.15
    # The reanalysis is a ~1.9 deg grid on its own smooth terrain: sampled
    # as is, a cell on a steep range gets its pixel's temperature at the
    # pixel's mean height, and the model (which follows each cell's height)
    # differs from it in a cell-to-cell speckle of several C over the Andes
    # and Himalaya (PW-040). So: bring each pixel to sea level with the
    # model's lapse rate (6.5 C/km) from its mean height (ETOPO surface,
    # sea as 0), interpolate that smooth field bilinearly to the cell, and
    # take it back up to the cell's own height.
    ny, nx = tv.shape[-2:]
    ty, tx = _pixel(t, LA.ravel(), LO.ravel())
    pix = ty * nx + tx
    z_pix = (np.bincount(pix, w * np.maximum(s, 0.0), ny * nx)
             / np.maximum(np.bincount(pix, w, ny * nx), 1e-12)).reshape(ny, nx)
    t_sl = tv + 6.5e-3 * z_pix[None]
    tm = _bilinear(t, t_sl, clat, clon) - 6.5e-3 * np.maximum(surface, 0.0)[None, :]
    out["obs_temp"] = tm.mean(0).astype(np.float32)
    out["obs_t_warm"] = tm.max(0).astype(np.float32)
    out["obs_t_cold"] = tm.min(0).astype(np.float32)
    return out


def cell_areas(grid) -> np.ndarray:
    """Spherical area of each cell (sr), triangle fan from the centre."""
    k = max(len(c) for c in grid.cell_corners)
    idx = np.array([c + [c[-1]] * (k - len(c)) for c in grid.cell_corners])
    a = grid.centers[:, None, :]
    b = grid.corners[idx]
    c = grid.corners[np.roll(idx, -1, axis=1)]
    num = np.abs(np.einsum("nkj,nkj->nk", a, np.cross(b, c)))
    den = 1 + np.einsum("nkj,nkj->nk", a, b) + np.einsum("nkj,nkj->nk", b, c) + np.einsum("nkj,nkj->nk", c, a)
    return (2 * np.arctan2(num, den)).sum(1)


def koppen_agreement(grid, koppen, obs_koppen, elev) -> dict:
    """The Earth Koppen score, one definition for earth_check, scorecard and
    the tests: over the model's land (elev > 0) outside Antarctica (lat >
    -60) where Kottek has a land class, the share of the *area* (true cell
    areas) whose model class matches the observed one: "group" (main group
    A-E) and "exact" (full code), in %. "group_cells" is the unweighted
    share of cells, which the test floor and scorecard quoted before
    2026-10-14 (within ~0.1 point of "group" at level 6)."""
    from planet import climate
    k, obs = np.asarray(koppen, int), np.asarray(obs_koppen, int)
    group = np.array([c[1][0] for c in climate.KOPPEN])
    m = (np.asarray(elev) > 0) & (grid.lat > -60) & (obs >= 0) & (obs < len(group)) & (obs != climate.SEA_CLASS)
    w = cell_areas(grid)[m]
    gm, go = group[k[m]], group[obs[m]]
    return {"group": 100 * float(w[gm == go].sum() / w.sum()), "exact": 100 * float(w[k[m] == obs[m]].sum() / w.sum()),
            "group_cells": 100 * float((gm == go).mean())}


def earth_on_grid(grid) -> dict:
    """Earth elevation/ice (model inputs) and observations on `grid`, cached
    as data/earth/L{level}.npz."""
    f = DATA / f"L{grid.level}.npz"
    if f.exists():
        z = np.load(f)
        if int(z["version"]) == CACHE_VERSION and len(z["elev"]) == grid.n:
            return {k: z[k] for k in z.files if k != "version"}
    out = _build(grid)
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, version=CACHE_VERSION, **out)
    return out


def cru_sunshine() -> dict:
    """CRU CL 2.0 (New et al. 2002) mean monthly sunshine, % of the possible
    (day length) hours, 1961-90, on a 10' grid of land points (no Antarctica):
    dict(lat, lon, val (n, 12))."""
    f = DATA / "raw_cru_sunp.npz"
    if not f.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        import gzip
        txt = gzip.decompress(_get(CRU_SUNP_URL)).decode("ascii")
        a = np.loadtxt(io.StringIO(txt), dtype=np.float32)
        np.savez_compressed(f, lat=a[:, 0], lon=a[:, 1], val=a[:, 2:14])
    z = np.load(f)
    return {k: z[k] for k in z.files}


def _cloud_build(grid) -> dict:
    n = grid.n
    clat, clon = grid.lat, grid.lon

    def halves(m):  # (12, n) monthly -> Apr-Sep mean, Oct-Mar mean
        return m[3:9].mean(0), np.concatenate([m[:3], m[9:]]).mean(0)

    out = {}
    c = raster("icoads_cldc")
    cv = np.where(~np.isfinite(c["val"]) | (np.abs(c["val"]) > 100), np.nan, c["val"]) / 8.0
    for k, v in zip(("obs_cloud_sea_jul", "obs_cloud_sea_jan"), halves(_sample(c, clat, clon, cv))):
        out[k] = v.astype(np.float32)
    t = raster("ncep_tcdc")
    tv = np.where(np.abs(t["val"]) > 1e30, np.nan, t["val"]) / 100.0
    for k, v in zip(("obs_cloud_ncep_jul", "obs_cloud_ncep_jan"), halves(_bilinear(t, tv, clat, clon))):
        out[k] = v.astype(np.float32)
    s = cru_sunshine()
    cell = grid.locate(_unit(s["lat"].astype(float), s["lon"].astype(float)))
    w = np.cos(np.radians(s["lat"].astype(float)))
    W = np.bincount(cell, w, n)
    m = np.stack([np.bincount(cell, w * s["val"][:, i], n) for i in range(12)]) / np.maximum(W, 1e-12) / 100.0
    m[:, W <= 0] = np.nan
    for k, v in zip(("obs_sun_jul", "obs_sun_jan"), halves(m)):
        out[k] = v.astype(np.float32)
    return out


def earth_clouds(grid) -> dict:
    """Observed clouds and sunshine on `grid` (fractions 0..1; NaN where the
    source has no data), as July (Apr-Sep) and January (Oct-Mar) half-year means:
      obs_cloud_sea_*   ICOADS 2.5 ship-observed cloudiness (oktas / 8), 2 deg, 1981-2010:
                        the surface observer's total cloud, over the sea
      obs_cloud_ncep_*  NCEP/NCAR reanalysis total cloud cover, 1991-2020 (a model's clouds,
                        too few over the stratocumulus decks; land + sea)
      obs_sun_*         CRU CL 2.0 sunshine duration, share of the possible hours, land
    Cached as data/earth/clouds_L{level}.npz."""
    f = DATA / f"clouds_L{grid.level}.npz"
    if f.exists():
        z = np.load(f)
        if int(z["version"]) == CLOUD_CACHE_VERSION and len(z["obs_sun_jul"]) == grid.n:
            return {k: z[k] for k in z.files if k != "version"}
    out = _cloud_build(grid)
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, version=CLOUD_CACHE_VERSION, **out)
    return out


# --------------------------------------------------------------------------
# potential natural vegetation (the vegetation check, tools/veg_check.py)
# --------------------------------------------------------------------------
POTVEG_URL = "https://sage-public-files.s3.amazonaws.com/global-potential-vegetation/glpotveg_5min.asc.gz"
POTVEG_CLASSES = [  # Ramankutty & Foley (1999), ids 1..15
    "tropical evergreen forest/woodland", "tropical deciduous forest/woodland",
    "temperate broadleaf evergreen forest/woodland", "temperate needleleaf evergreen forest/woodland",
    "temperate deciduous forest/woodland", "boreal evergreen forest/woodland", "boreal deciduous forest/woodland",
    "evergreen/deciduous mixed forest/woodland", "savanna", "grassland/steppe", "dense shrubland",
    "open shrubland", "tundra", "desert", "polar desert/rock/ice"]
POTVEG_CACHE_VERSION = 1


def potveg_raw() -> dict:
    """Ramankutty & Foley (1999) global potential natural vegetation, 5
    arc-minute ESRI ASCII grid (0.5 MB gzipped, SAGE, University of
    Wisconsin): dict(val (2160, 4320) uint8, 0 = water / no data, 1..15
    POTVEG_CLASSES; lat, lon of the pixel centres)."""
    f = DATA / "raw_potveg.npz"
    if not f.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        import gzip
        txt = gzip.decompress(_get(POTVEG_URL)).decode("ascii").splitlines()
        head = {}
        k = 0
        while txt[k].split()[0].lower() in ("ncols", "nrows", "xllcorner", "yllcorner", "cellsize", "nodata_value"):
            key, v = txt[k].split()[:2]
            head[key.lower()] = float(v)
            k += 1
        val = np.loadtxt(txt[k:], dtype=np.float32)
        nod = head.get("nodata_value", -9999)
        val = np.where((val == nod) | (val < 0) | (val > 15), 0, val).astype(np.uint8)
        nr, nc, cs = int(head["nrows"]), int(head["ncols"]), head["cellsize"]
        lat = head["yllcorner"] + cs * (nr - 0.5 - np.arange(nr))
        lon = head["xllcorner"] + cs * (0.5 + np.arange(nc))
        np.savez_compressed(f, val=val, lat=lat, lon=lon)
    z = np.load(f)
    return {k: z[k] for k in z.files}


def earth_potveg(grid) -> np.ndarray:
    """Each cell's most common (area-weighted) Ramankutty & Foley class
    over its pixels (0: no land pixel), cached as data/earth/potveg_L{level}.npz."""
    f = DATA / f"potveg_L{grid.level}.npz"
    if f.exists():
        z = np.load(f)
        if int(z["version"]) == POTVEG_CACHE_VERSION and len(z["potveg"]) == grid.n:
            return z["potveg"]
    r = potveg_raw()
    LA, LO = np.meshgrid(r["lat"], r["lon"], indexing="ij")
    v = r["val"].ravel()
    m = v > 0
    cell = grid.locate(_unit(LA.ravel()[m], LO.ravel()[m]))
    w = np.cos(np.radians(LA.ravel()[m]))
    votes = np.bincount(cell * 16 + v[m], w, grid.n * 16).reshape(grid.n, 16)
    out = np.where(votes.sum(1) > 0, np.argmax(votes, 1), 0).astype(np.uint8)
    np.savez_compressed(f, version=POTVEG_CACHE_VERSION, potveg=out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--level", type=int, default=6)
    a = ap.parse_args()
    from planet.grid import build_grid
    t0 = time.time()
    grid = build_grid(a.level)
    d = earth_on_grid(grid)
    land = d["elev"] > 0
    print(f"level {a.level}: {grid.n} cells, land {land.mean():.1%}, "
          f"ice cells {(d['ice'] > 0).sum()}, max surface {d['surface'].max():.0f} m, "
          f"{time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
