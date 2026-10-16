"""Real-Earth reference data, mapped onto the icosphere grid.

Used by tools/earth_check.py to run the climate model on Earth's actual
geography and compare it with observations.

Sources (all downloaded once, then cached under data/earth/; ~25 MB, plus
~390 MB of HydroSHEDS for the Earth world's rivers)
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

River heights (the Earth world's lakes, earth_outlets; PW-236)
    HydroSHEDS v1 (Lehner, Verdin & Jarvis 2008, Eos 89(10), 93-94), 30"
    global: hydrologically conditioned flow directions (hyd_glo_dir_30s,
    83 MB) and the void-filled SRTM DEM (hyd_glo_dem_30s, 306 MB), 84 N to
    56 S, LZW GeoTIFFs (read by _tiff, numpy + numba only):
      https://data.hydrosheds.org/file/hydrosheds-v1-dir/hyd_glo_dir_30s.zip
      https://data.hydrosheds.org/file/hydrosheds-v1-dem/hyd_glo_dem_30s.zip
    Free to use with attribution (HydroSHEDS licence). Kept as downloaded
    (raw_hydrosheds_*_30s.zip, ~390 MB, most of data/earth); only the
    per-level hydrosheds_L{level}.npz is read once it is built (~1 min).

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
Moisture budget (tools/moisture_budget.py)
    NCEP/NCAR Reanalysis 1, 1991-2020 monthly long-term means of the surface
    latent heat flux (evaporation = flux / 2.5e6 J/kg), precipitation rate and
    precipitable water, whole netCDF-4 files (~1 MB each) from
      https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/
    (NC_FILES; PSL's OPeNDAP server and its ERDDAP mirrors rate-limit). A
    reanalysis: its evaporation runs ~10% high and its E - P doesn't close.
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
and its ice isn't afloat (inland basins below sea level such as the Caspian
count as sea). Ice is afloat where the bedrock is below the sea and the ice
surface stands no higher than flotation's freeboard, (1 - 917/1028) x (ice
surface - bedrock): the shelves (Ross, Ronne-Filchner, Amery; ~1.05 million
km2 of ETOPO1's samples), which become sea of the sea floor's depth. A cell
is land if its land fraction >= 0.5. Then:
  surface = weighted mean of the ice-surface height over the cell's land
            samples (sea cells: mean depth over sea samples, <= -1 m)
  ice     = weighted mean of (ice surface - bedrock) over land samples, i.e.
            real ice thickness from ETOPO1 (Greenland + Antarctica; mountain
            glaciers are not in ETOPO1 and get 0), but only where >= 50% of
            the cell's land is ice covered (else 0: the model turns any cell
            with ice > 0 into EF, which would ice over Greenland's coast)
  ice_frac  that ice-covered share of the cell's land
  elev    = surface - ice: the true bed (PW-354). The model treats
            `elev` as bare ground and adds `ice` itself, so elev + ice ==
            surface. Where the bedrock is below sea level (West Antarctica,
            central Greenland) the cell is land by its ice: land is
            geo.is_land(elev, ice) (elev > 0 or ice > 0, PW-307), never
            elev > 0. (Before PW-354 the bed was floored at 1 m and the ice
            thinned to keep the surface, and the shelves were land.)
Observed fields are sampled (nearest pixel) at each cell centre:
  obs_koppen    KOPPEN id (-1 where Kottek has no land), As -> Aw
  obs_temp, obs_t_warm, obs_t_cold   NCEP 2 m, annual mean / warmest / coldest month (C),
                interpolated at sea level and moved to the cell's height at 6.5 C/km
  obs_precip, obs_p_jul, obs_p_jan   GPCC land (mm/yr; NaN over sea/Antarctica);
                p_jul is the Apr-Sep rate, p_jan the Oct-Mar rate (as the model)
  obs_gpcp      GPCP annual precipitation, land + ocean (mm/yr)

Soils check data (SoilGrids WRB, GLiM parent rock, LGM ice; tools/soil_check.py): sources, licences and
citations sit next to each loader below (earth_soilgrids, earth_glim, earth_lgm_ice).

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
from numba import njit, prange

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "earth"
CACHE_VERSION = 5  # (5: the true bed under the ice, shelves sea; PW-354)
RHO_I, RHO_W = 917.0, 1028.0  # ice, sea water (kg/m3; as timezoom.py)

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
# Whole netCDF-4 files (read with tools/h5_reader), for the moisture budget (tools/moisture_budget.py):
# NCEP/NCAR reanalysis 1991-2020 long-term monthly means, NOAA PSL (public domain; ~1 MB each):
# surface latent heat flux (W/m2, upward > 0: evaporation), precipitation rate (kg/m2/s) and the
# column's precipitable water (kg/m2). (PSL's OPeNDAP server and its ERDDAP mirrors rate-limit.)
PSL_FILES = "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/"
NC_FILES = {
    "ncep_lhtfl": (PSL_FILES + "surface_gauss/lhtfl.sfc.mon.ltm.1991-2020.nc", "lhtfl"),
    "ncep_prate": (PSL_FILES + "surface_gauss/prate.sfc.mon.ltm.1991-2020.nc", "prate"),
    "ncep_pwat": (PSL_FILES + "surface/pr_wtr.eatm.mon.ltm.1991-2020.nc", "pr_wtr"),
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
    if key in NC_FILES:
        from tools.h5_reader import read_variable
        from tools.tiff_reader import BytesSource
        url, var = NC_FILES[key]
        t0 = time.time()
        src = BytesSource(_get(url))
        print(f"  {key}: {len(src.data) / 1e6:.1f} MB from {url.split('/')[2]} in {time.time() - t0:.0f}s")
        return {"val": read_variable(src, var), "lat": read_variable(src, "lat"), "lon": read_variable(src, "lon")}
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
    # land: ground or grounded ice above the sea. ETOPO1's ice surface also
    # covers the floating shelves (Ross, Ronne-Filchner...), whose "bedrock"
    # is the sea floor beneath them; ice is afloat where its surface stands
    # no higher than flotation's freeboard, (1 - rho_i / rho_w) x its
    # thickness (as the time zoom's sheets, timezoom.py), and those samples
    # are sea of the floor's depth (the climate makes its own sea ice)
    afloat = (s > 0) & (b < 0) & (s <= (1 - RHO_I / RHO_W) * (s - b))
    land = (s > 0) & ~afloat
    s = np.where(afloat, b, s)
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
    # the true bed under the ice (PW-354): below sea level under much of West
    # Antarctica and central Greenland, land by its ice (geo.is_land, PW-307)
    elev = surface - ice_t
    low = is_land & (ice_t <= 0) & (elev < 1)  # (ice-free land: a mean of heights > 0, kept above the sea)
    elev[low] = 1.0
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


def land_of(d: dict) -> np.ndarray:
    """The land of earth_on_grid's dict: ground above the sea or under ice
    (geo.is_land; the bed under the ice is the true one, below the sea in
    West Antarctica and central Greenland: PW-354)."""
    from planet.geo import is_land
    return is_land(d["elev"], d["ice"])


def koppen_agreement(grid, koppen, obs_koppen, elev, ice=None) -> dict:
    """The Earth Koppen score, one definition for earth_check, scorecard and
    the tests: over the model's land (geo.is_land(elev, ice)) outside Antarctica (lat >
    -60) where Kottek has a land class, the share of the *area* (true cell
    areas) whose model class matches the observed one: "group" (main group
    A-E) and "exact" (full code), in %. "group_cells" is the unweighted
    share of cells, which the test floor and scorecard quoted before
    2026-10-14 (within ~0.1 point of "group" at level 6)."""
    from planet import climate
    from planet.geo import is_land
    k, obs = np.asarray(koppen, int), np.asarray(obs_koppen, int)
    group = np.array([c[1][0] for c in climate.KOPPEN])
    m = is_land(elev, ice) & (grid.lat > -60) & (obs >= 0) & (obs < len(group)) & (obs != climate.SEA_CLASS)
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
# river-conditioned outlet heights (the Earth world's lakes, PW-236)
# --------------------------------------------------------------------------
HYDROSHEDS_URL = "https://data.hydrosheds.org/file/hydrosheds-v1-{0}/hyd_glo_{0}_30s.zip"
OUTLET_CACHE_VERSION = 3


def _tiff(path: Path) -> tuple[np.ndarray, tuple[float, float, float], float | None]:
    """The image of a tiled, LZW-compressed (or uncompressed) single-band
    GeoTIFF inside a zip (HydroSHEDS'), its (west, north, pixel size) in
    degrees and its no-data value. Just enough TIFF for those files (numpy
    and numba only)."""
    import struct
    with zipfile.ZipFile(path) as zf:
        raw = zf.read(next(n for n in zf.namelist() if n.endswith(".tif")))
    bo = "<" if raw[:2] == b"II" else ">"
    assert struct.unpack(bo + "H", raw[2:4])[0] == 42, "BigTIFF not supported"
    off = struct.unpack(bo + "I", raw[4:8])[0]
    sizes = {1: 1, 2: 1, 3: 2, 4: 4, 11: 4, 12: 8, 16: 8}
    codes = {1: "B", 2: "c", 3: "H", 4: "I", 11: "f", 12: "d", 16: "Q"}
    tags = {}
    for k in range(struct.unpack(bo + "H", raw[off:off + 2])[0]):
        tag, typ, cnt = struct.unpack(bo + "HHI", raw[off + 2 + 12 * k: off + 10 + 12 * k])
        at = off + 10 + 12 * k
        if sizes[typ] * cnt > 4:
            at = struct.unpack(bo + "I", raw[at:at + 4])[0]
        v = struct.unpack(f"{bo}{cnt}{codes[typ]}", raw[at:at + sizes[typ] * cnt])
        tags[tag] = b"".join(v).decode().strip("\0") if typ == 2 else v
    w, h, bits = tags[256][0], tags[257][0], tags[258][0]
    tw, th = tags[322][0], tags[323][0]
    comp, pred = tags[259][0], tags.get(317, (1,))[0]
    assert comp in (1, 5) and pred == 1, (comp, pred)
    kind = {1: "u", 2: "i", 3: "f"}[tags.get(339, (1,))[0]]
    out = _untile(np.frombuffer(raw, np.uint8), np.array(tags[324], np.int64), np.array(tags[325], np.int64),
                  w, h, tw, th, bits // 8, comp == 5)
    img = out.view(np.dtype(f"{bo}{kind}{bits // 8}")).reshape(h, w)
    scale, tie = tags[33550], tags[33922]
    nodata = float(tags[42113]) if 42113 in tags else None
    return img, (tie[3] - tie[0] * scale[0], tie[4] + tie[1] * scale[1], scale[0]), nodata


@njit(cache=True)
def _lzw(src, out):
    """TIFF LZW decoding of src into out; returns the bytes written."""
    prefix = np.full(4096, -1, np.int32)
    suffix = np.zeros(4096, np.uint8)
    first = np.zeros(4096, np.uint8)
    length = np.ones(4096, np.int32)
    for i in range(256):
        suffix[i] = i
        first[i] = i
    nbits, pos, width, nxt, prev, o = src.shape[0] * 8, 0, 9, 258, -1, 0
    while pos + width <= nbits:
        b = pos >> 3
        v = (np.int64(src[b]) << 16) | (np.int64(src[b + 1]) << 8 if b + 1 < src.shape[0] else 0) | \
            (np.int64(src[b + 2]) if b + 2 < src.shape[0] else 0)
        code = (v >> (24 - (pos & 7) - width)) & ((1 << width) - 1)
        pos += width
        if code == 257:
            break
        if code == 256:
            width, nxt, prev = 9, 258, -1
            continue
        if prev >= 0:
            if nxt >= 4096:
                break
            prefix[nxt] = prev
            suffix[nxt] = first[code] if code < nxt else first[prev]
            first[nxt] = first[prev]
            length[nxt] = length[prev] + 1
            nxt += 1
        n = length[code]
        if o + n > out.shape[0]:
            break
        c = code
        for k in range(n - 1, -1, -1):
            out[o + k] = suffix[c]
            c = prefix[c]
        o += n
        prev = code
        if nxt >= (1 << width) - 1 and width < 12:
            width += 1
    return o


@njit(cache=True, parallel=True)
def _untile(raw, offs, counts, w, h, tw, th, bps, lzw):
    out = np.zeros(w * h * bps, np.uint8)
    across = (w + tw - 1) // tw
    for t in prange(offs.shape[0]):
        buf = np.zeros(tw * th * bps, np.uint8)
        src = raw[offs[t]:offs[t] + counts[t]]
        if lzw:
            _lzw(src, buf)
        else:
            buf[:src.shape[0]] = src[:buf.shape[0]]
        y0, x0 = (t // across) * th, (t % across) * tw
        for y in range(min(th, h - y0)):
            nx = min(tw, w - x0) * bps
            a = ((y0 + y) * w + x0) * bps
            out[a:a + nx] = buf[y * tw * bps:y * tw * bps + nx]
    return out


@njit(cache=True)
def _down(dirs, p, nx):
    """The pixel an ESRI-coded flow direction (1 E, 2 SE, 4 S, ... 128 NE)
    sends p's water to, -1 for none (a sink, the sea, no data)."""
    ny = dirs.shape[0] // nx
    d = dirs[p]
    y, x = p // nx, p % nx
    if d == 1:
        x += 1
    elif d == 2:
        x, y = x + 1, y + 1
    elif d == 4:
        y += 1
    elif d == 8:
        x, y = x - 1, y + 1
    elif d == 16:
        x -= 1
    elif d == 32:
        x, y = x - 1, y - 1
    elif d == 64:
        y -= 1
    elif d == 128:
        x, y = x + 1, y - 1
    else:
        return -1
    if y < 0 or y >= ny:
        return -1
    return y * nx + x % nx


@njit(cache=True)
def _accumulate_dirs(dirs, nx):
    """Upstream pixels of each pixel (itself included) along the flow
    directions, and the inland sink its water ends in (a dir-0 pixel not
    joined through others to the sea, 255), -1 for the sea."""
    n = dirs.shape[0]
    indeg = np.zeros(n, np.uint8)
    for p in range(n):
        d = _down(dirs, p, nx)
        if d >= 0:
            indeg[d] += 1
    acc = np.ones(n, np.int32)
    queue = np.empty(n, np.int32)
    k = 0
    for p in range(n):
        if indeg[p] == 0:
            queue[k] = p
            k += 1
    t = 0
    while t < k:
        p = queue[t]
        t += 1
        d = _down(dirs, p, nx)
        if d >= 0:
            acc[d] += acc[p]
            indeg[d] -= 1
            if indeg[d] == 0:
                queue[k] = d
                k += 1
    # the sea's edge: sinks (0) joined through other sinks to the sea (255);
    # the rest are inland sinks
    ny = n // nx
    coast = np.zeros(n, np.bool_)
    k = 0
    for p in range(n):
        if dirs[p] == 0:
            y, x = p // nx, p % nx
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if not coast[p] and 0 <= y + dy < ny and dirs[(y + dy) * nx + (x + dx) % nx] == 255:
                        coast[p] = True
                        queue[k] = p
                        k += 1
    while k > 0:
        k -= 1
        p = queue[k]
        y, x = p // nx, p % nx
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= y + dy < ny:
                    q = (y + dy) * nx + (x + dx) % nx
                    if dirs[q] == 0 and not coast[q]:
                        coast[q] = True
                        queue[k] = q
                        k += 1
    # each pixel's water ends where its directions do (downstream first)
    order = queue
    k = 0
    indeg[:] = 0
    for p in range(n):
        d = _down(dirs, p, nx)
        if d >= 0:
            indeg[d] += 1
    for p in range(n):
        if indeg[p] == 0:
            order[k] = p
            k += 1
    t = 0
    while t < k:
        d = _down(dirs, order[t], nx)
        t += 1
        if d >= 0:
            indeg[d] -= 1
            if indeg[d] == 0:
                order[k] = d
                k += 1
    sink = np.full(n, -1, np.int32)
    for t in range(k - 1, -1, -1):
        p = order[t]
        d = _down(dirs, p, nx)
        if d >= 0:
            sink[p] = sink[d]
        elif dirs[p] == 0 and not coast[p]:
            sink[p] = p
    return acc, sink


@njit(cache=True)
def _main_stem_heights(dirs, acc, dem, cell, nx, ncell, nodata):
    """Per cell: its main river (the pixel with the most upstream pixels,
    followed upstream through the biggest donor while still in the cell) is
    traced to where it enters the cell; the lowest ground along it from
    there up to its source is the height of the river where it enters
    (a river doesn't run uphill, so the dams a gorge leaves in the DEM are
    cut down to the river upstream of them). NaN where no pixel."""
    n = dirs.shape[0]
    ny = n // nx
    top = np.full(ncell, -1, np.int64)
    for p in range(n):
        c = cell[p]
        if c >= 0 and (top[c] < 0 or acc[p] > acc[top[c]]):
            top[c] = p
    out = np.full(ncell, np.nan)
    for c in range(ncell):
        p = top[c]
        if p < 0:
            continue
        inside = True
        low = np.inf
        while True:
            if inside and cell[p] != c:
                inside = False
            if not inside and dem[p] != nodata:
                low = min(low, dem[p])
            # the biggest donor
            y, x = p // nx, p % nx
            best, ba = -1, 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy = y + dy
                    if (dy or dx) and 0 <= yy < ny:
                        q = yy * nx + (x + dx) % nx
                        if acc[q] > ba and _down(dirs, q, nx) == p:
                            best, ba = q, acc[q]
            if best < 0:
                break
            if inside and cell[best] != c and dem[p] != nodata:
                low = min(low, dem[p])  # the entry pixel itself
            p = best
        if np.isfinite(low):
            out[c] = low
        elif dem[p] != nodata:
            out[c] = dem[p]  # a cell whose river rises inside it: its source
    return out, top


def _outlet_build(grid) -> np.ndarray:
    files = {}
    for key in ("dir", "dem"):
        f = DATA / f"raw_hydrosheds_{key}_30s.zip"
        if not f.exists():
            DATA.mkdir(parents=True, exist_ok=True)
            f.write_bytes(_get(HYDROSHEDS_URL.format(key), timeout=1800))
        files[key] = f
    dirs, (west, north, px), _ = _tiff(files["dir"])
    dem, geo, nodata = _tiff(files["dem"])
    assert dem.shape == dirs.shape and np.allclose(geo, (west, north, px))
    ny, nx = dirs.shape
    dirs, dem = np.ascontiguousarray(dirs).ravel(), np.ascontiguousarray(dem).ravel().astype(np.int16)
    valid = np.isin(dirs, (1, 2, 4, 8, 16, 32, 64, 128, 0))  # (0: a sink or the river's mouth)
    cell = np.full(ny * nx, -1, np.int32)
    lon = west + px * (0.5 + np.arange(nx))
    for y in range(ny):  # pixel centres -> nearest cell, a row at a time
        m = valid[y * nx:(y + 1) * nx]
        if m.any():
            la = np.full(m.sum(), north - px * (y + 0.5))
            cell[y * nx:(y + 1) * nx][m] = grid.locate(_unit(la, lon[m]))
    acc, sink = _accumulate_dirs(dirs, nx)
    out, top = _main_stem_heights(dirs, acc, dem, cell, nx, grid.n, np.int16(nodata))
    m = cell >= 0
    share = np.bincount(cell[m], sink[m] >= 0, grid.n) / np.maximum(np.bincount(cell[m], minlength=grid.n), 1)
    # each cell's closed basin: the sink most of its inland pixels end in
    m &= sink >= 0
    key, cnt = np.unique(cell[m].astype(np.int64) * (ny * nx) + sink[m], return_counts=True)
    c, sk = np.divmod(key, ny * nx)
    o = np.lexsort((-cnt, c))
    c, sk = c[o], sk[o]
    first = np.r_[True, c[1:] != c[:-1]]
    basin = np.full(grid.n, -1, np.int64)
    basin[c[first]] = sk[first]
    # (not where the cell's main river reaches the sea: the lower Murray
    # crosses the Mallee, whose own ground drains to sinks)
    basin[(top >= 0) & (sink[np.maximum(top, 0)] < 0)] = -1
    return {"river": out, "inland": share, "basin": basin}


def hydrosheds_rivers(grid) -> dict:
    """Per cell, from HydroSHEDS (Lehner, Verdin & Jarvis 2008: 30"
    hydrologically conditioned flow directions and the void-filled SRTM
    DEM, 84 N - 56 S, ~390 MB, downloaded once):
      river   m, the height of the cell's main river where it enters the
              cell: the pixel with the most upstream area, followed up its
              biggest tributary to where it comes in; its height there is
              the lowest ground along it from there up to its source (a
              river doesn't run uphill, so a gorge too narrow for the DEM
              doesn't dam it). NaN where no pixel (south of 56 S).
      inland  share of the cell's pixels whose water ends inland (in a
              closed basin) rather than in the sea
      basin   the closed basin most of those end in (its sink pixel), -1
              where none or where the cell's main river reaches the sea
    Cached as data/earth/hydrosheds_L{level}.npz."""
    f = DATA / f"hydrosheds_L{grid.level}.npz"
    if f.exists():
        z = np.load(f)
        if int(z["version"]) == OUTLET_CACHE_VERSION and len(z["river"]) == grid.n:
            return {k: z[k] for k in ("river", "inland", "basin")}
    out = _outlet_build(grid)
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, version=OUTLET_CACHE_VERSION, **out)
    return out


def earth_closed(grid) -> np.ndarray:
    """Each land cell's closed basin, -1 where none: where HydroSHEDS
    drains at least half of the cell inland and its main river too, the
    basin (sink) most of it ends in (hydrosheds_rivers). hydrology.rivers_and_lakes keeps each one
    closed (its `closed`)."""
    h = hydrosheds_rivers(grid)
    return np.where((h["inland"] >= 0.5) & land_of(earth_on_grid(grid)), h["basin"], -1)  # (basin -1: open)


def earth_outlets(grid) -> np.ndarray:
    """Each land cell's river-conditioned outlet height, m (NaN where none):
    hydrosheds_rivers' river height, the outlet hydrology.lakes cuts a
    river's valley down to. A cell's mean height (~100 km of ground) stands
    as a dam where a river runs through it in a gorge narrower than the cell
    (the Lena below Yakutia, the Amur, the Danube's Iron Gates, the
    Yangtze's Three Gorges, the Columbia); the river itself runs at its own
    height. The DEM has lakes at their surface, so a real lake's outlet
    stands at its level and its basin keeps its water. None in the closed
    basins (earth_closed): their hollows are kept, and they keep their
    water whatever their neighbours' rivers do (walled off).
    (ETOPO1 can't give this, even at its full 1': filled, it still dams the
    Iron Gates at 250 m where the Danube runs at ~65.)"""
    h = hydrosheds_rivers(grid)
    return np.where(land_of(earth_on_grid(grid)) & (earth_closed(grid) < 0), h["river"], np.nan)


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


# --------------------------------------------------------------------------
# soils check (PW-314; tools/soil_check.py, docs/proposals/soils.md section 7)
# --------------------------------------------------------------------------
# SoilGrids 2.0 WRB most probable group
#   Poggio, de Sousa, Ribeiro, Hengl, Heuvelink et al. (2021), "SoilGrids 2.0:
#   producing soil information for the globe with quantified spatial
#   uncertainty", SOIL 7, 217-240, doi:10.5194/soil-7-217-2021. ISRIC - World
#   Soil Information. Licence: CC BY 4.0 (cite the paper and ISRIC).
#   The 250 m product is a 172800 x 67200 byte raster (30 WRB reference soil
#   groups, 255 = no data); its overview file is a BigTIFF of deflate-compressed
#   128 px tiles with 4 levels (43200 x 16800, 10800 x 4200, 2700 x 1050,
#   675 x 263). Level 1 (2 arc-minutes, ~3.7 km, 2.5 MB of tiles) is read by HTTP
#   range requests (tools/tiff_reader.py) and cached whole, with its legend
#   (group names from MostProbable.qml), as raw_soilgrids_wrb.npz.
SOILGRIDS_URL = "https://files.isric.org/soilgrids/latest/data/wrb/MostProbable.vrt.ovr"
SOILGRIDS_QML = "https://files.isric.org/soilgrids/latest/data/wrb/MostProbable.qml"
SOILGRIDS_LEVEL = 1
SOILGRIDS_TOP = 83.99916720  # latitude of the top edge (the VRT geotransform); x starts at -180
SOILGRIDS_NODATA = 255
SOILGRIDS_CACHE_VERSION = 1


def soilgrids_wrb_raw() -> dict:
    """SoilGrids 2.0 WRB most probable group, one overview level: dict(val
    (4200, 10800) uint8, 255 = no data; lat, lon of the pixel centres; legend
    (30,) str, the WRB group name for each value 0..29)."""
    f = DATA / "raw_soilgrids_wrb.npz"
    if not f.exists():
        from tools.tiff_reader import HttpRange, read_ifds, read_image
        DATA.mkdir(parents=True, exist_ok=True)
        src = HttpRange(SOILGRIDS_URL)
        ifd = read_ifds(src)[SOILGRIDS_LEVEL]
        if ifd["bits"] != 8 or ifd["sample_format"] != 1:
            raise RuntimeError("SoilGrids overview is not the expected 8-bit raster; its layout changed")
        val = read_image(src, ifd)
        nr, nc = val.shape
        if not ((val <= 29) | (val == SOILGRIDS_NODATA)).all():
            raise RuntimeError("SoilGrids overview has unexpected values; its layout changed")
        qml = _get(SOILGRIDS_QML).decode("utf-8", "replace")
        legend = {int(v): lab for v, lab in re.findall(r'<paletteEntry[^>]*?value="(\d+)"[^>]*?label="([^"]+)"', qml)}
        if sorted(legend) != list(range(30)):
            raise RuntimeError("could not read the 30 group names from MostProbable.qml")
        dy, dx = 140.0 / nr, 360.0 / nc
        lat = SOILGRIDS_TOP - dy * (0.5 + np.arange(nr))
        lon = -180.0 + dx * (0.5 + np.arange(nc))
        np.savez_compressed(f, val=val, lat=lat, lon=lon, legend=np.array([legend[i] for i in range(30)]))
    z = np.load(f)
    return {k: z[k] for k in z.files}


def earth_soilgrids(grid) -> dict:
    """SoilGrids WRB group per grid cell: the area-weighted (cos latitude) most
    common group over the cell's pixels. dict(wrb (n,) uint8, 255 = no data
    (sea, ice, rock outcrops SoilGrids leaves out); cover (n,) float32, the
    share of the cell's pixels with data; legend). Cached as
    data/earth/soilgrids_wrb_L{level}.npz."""
    f = DATA / f"soilgrids_wrb_L{grid.level}.npz"
    if f.exists():
        z = np.load(f)
        if int(z["version"]) == SOILGRIDS_CACHE_VERSION and len(z["wrb"]) == grid.n:
            return {"wrb": z["wrb"], "cover": z["cover"], "legend": z["legend"]}
    r = soilgrids_wrb_raw()
    votes = np.zeros((grid.n, 32))
    allw = np.zeros(grid.n)
    lon = r["lon"]
    for a in range(0, len(r["lat"]), 150):  # rows in bands, to keep memory low
        v = r["val"][a:a + 150].ravel()
        LA, LO = np.meshgrid(r["lat"][a:a + 150], lon, indexing="ij")
        w = np.cos(np.radians(LA)).ravel()
        cell = grid.locate(_unit(LA.ravel(), LO.ravel()))
        allw += np.bincount(cell, w, grid.n)
        m = v != SOILGRIDS_NODATA
        votes += np.bincount(cell[m] * 32 + v[m], w[m], grid.n * 32).reshape(grid.n, 32)
    tot = votes.sum(1)
    out = np.where(tot > 0, np.argmax(votes, 1), SOILGRIDS_NODATA).astype(np.uint8)
    cover = (tot / np.maximum(allw, 1e-12)).astype(np.float32)
    np.savez_compressed(f, version=SOILGRIDS_CACHE_VERSION, wrb=out, cover=cover, legend=r["legend"])
    return {"wrb": out, "cover": cover, "legend": r["legend"]}


# GLiM parent rock
#   Hartmann & Moosdorf (2012), "The new global lithological map database
#   GLiM: A representation of rock properties at the Earth surface", Geochem.
#   Geophys. Geosyst. 13, Q12004, doi:10.1029/2012GC004370. Gridded to 0.5 deg
#   (dominant first-level class per cell; 38 kB zip), PANGAEA
#   doi:10.1594/PANGAEA.788537. Licence: CC BY 3.0 (cite the paper and dataset).
GLIM_URL = "https://hdl.handle.net/10013/epic.39939.d001"  # the PANGAEA zip
GLIM_CLASSES = ["su", "vb", "ss", "pb", "sm", "sc", "va", "mt", "pa", "vi", "wb", "py", "pi", "ev", "nd", "ig"]
# GLiM first-level class (ids 1..16, GLIM_CLASSES order; index 0 = none) -> planet.surface.ROCKS id, -1 where
# there is no rock (water bodies, no data, ice and glaciers). A parent-rock guess for soils, not the world's
# rock layer:
#   su unconsolidated sediments -> sediment      vb basic volcanics    -> flood basalt
#   ss siliciclastic sediments  -> sandstone     pb basic plutonics    -> hotspot basalt (mafic)
#   sm mixed sediments          -> shale         sc carbonates         -> limestone
#   va acid volcanics           -> tuff          mt metamorphics       -> metamorphic belt
#   pa acid plutonics           -> granite       vi intermediate volc. -> arc
#   py pyroclastics             -> tuff          pi intermediate plut. -> arc
#   ev evaporites               -> evaporite
GLIM_TO_ROCK = np.array([-1, 3, 13, 7, 1, 8, 6, 15, 4, 11, 2, -1, 15, 2, 9, -1, -1], np.int8)
GLIM_CACHE_VERSION = 1


def glim_raw() -> dict:
    """GLiM v1.0 at 0.5 deg: dict(val (360, 720) uint8, 0 = no data / water /
    ice, 1..16 GLIM_CLASSES; lat, lon of the pixel centres; classes)."""
    f = DATA / "raw_glim.npz"
    if not f.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(_get(GLIM_URL))) as z:
            names = {n.lower(): n for n in z.namelist()}
            asc = z.read(names["glim_wgs84_0point5deg.txt.asc"]).decode("ascii").splitlines()
            cls = z.read(names["classnames.txt"]).decode("ascii")
        got = sorted((int(i), c) for i, c in re.findall(r'^\d+;(\d+);[\d.]+;"(\w+)"', cls, re.M))
        if [c for _, c in got] != GLIM_CLASSES:
            raise RuntimeError(f"GLiM class names changed: {got}")
        head, k = {}, 0
        while asc[k].split()[0].lower() in ("ncols", "nrows", "xllcorner", "yllcorner", "cellsize", "nodata_value"):
            key, v = asc[k].split()[:2]
            head[key.lower()] = float(v)
            k += 1
        a = np.loadtxt(asc[k:], dtype=np.float32)
        nr, nc, cs = int(head["nrows"]), int(head["ncols"]), head["cellsize"]
        if a.shape != (nr, nc):
            raise RuntimeError("GLiM grid shape is not what its header says")
        val = np.where((a >= 1) & (a <= 16), a, 0).astype(np.uint8)
        lat = head["yllcorner"] + cs * (nr - 0.5 - np.arange(nr))
        lon = head["xllcorner"] + cs * (0.5 + np.arange(nc))
        np.savez_compressed(f, val=val, lat=lat, lon=lon, classes=np.array(GLIM_CLASSES))
    z = np.load(f)
    return {k: z[k] for k in z.files}


def earth_glim(grid) -> np.ndarray:
    """Parent-rock id (planet.surface.ROCKS, via GLIM_TO_ROCK) per cell: the most
    common (area-weighted) over the 0.5 deg GLiM pixels in it, -1 where it has
    none (sea, ice, water, and cells smaller than a pixel at L8+ that hold no
    pixel centre). Cached as data/earth/glim_L{level}.npz."""
    f = DATA / f"glim_L{grid.level}.npz"
    if f.exists():
        z = np.load(f)
        if int(z["version"]) == GLIM_CACHE_VERSION and len(z["rock"]) == grid.n:
            return z["rock"]
    r = glim_raw()
    LA, LO = np.meshgrid(r["lat"], r["lon"], indexing="ij")
    rock = GLIM_TO_ROCK[r["val"].astype(int)].ravel()
    m = rock >= 0
    cell = grid.locate(_unit(LA.ravel()[m], LO.ravel()[m]))
    w = np.cos(np.radians(LA.ravel()[m]))
    votes = np.bincount(cell * 16 + rock[m], w, grid.n * 16).reshape(grid.n, 16)
    out = np.where(votes.sum(1) > 0, np.argmax(votes, 1), -1).astype(np.int8)
    np.savez_compressed(f, version=GLIM_CACHE_VERSION, rock=out)
    return out


# Last Glacial Maximum ice cover (21 ka)
#   Shao, Y., Anhaeuser, A., Elble, T., et al., "Global Kilometer-Resolution
#   Dataset of Boundary Conditions for Climate Simulations of the Last Glacial
#   Maximum", Zenodo, doi:10.5281/zenodo.14506525, file ice_30s.nc (24.5 MB;
#   variable ice_cover_boolean, 30 arc-second global grid, 1 = ice).
#   Reconstruction (checked 2026-10-15 against the record's Dataset_Description.pdf,
#   Sec. 2): the mask is NOT an independent reconstruction. It is the binary 1 degree
#   PMIP3 LGM ice-cover map ("no ice data finer than 1 degree are available"),
#   bilinearly interpolated to 30 arc-seconds; ice_cover_boolean then draws each
#   pixel as ice with probability equal to that interpolated fraction. So the
#   effective resolution is 1 degree and the extent is the PMIP3 protocol ice sheet
#   (the PMIP3/CMIP5 LGM ice sheet is a composite of three groups' reconstructions,
#   the ANU ice model, ICE-6G v1.02 and GLAC-1 (the PMIP3 21k ice-sheet wiki); only
#   two cover Antarctica. Abe-Ouchi et al. 2015, Geosci. Model Dev. 8, 3621,
#   doi:10.5194/gmd-8-3621-2015. The PDF itself does not name the members). The record has no
#   paper DOI; cite the Zenodo dataset (Shao, Anhaeuser, Elble, Ludwig, Schlueter,
#   Ulbrich, Williams, Xia).
#   Licence: CC BY 4.0 (cite the dataset). netCDF-4, so read with the small HDF5
#   reader in tools/h5_reader.py (no h5py), by range requests, and averaged
#   30 x 30 pixels on the fly to 0.25 deg ice fractions (raw_lgm_ice.npz, ~0.3 MB).
#   Considered and not used: ICE-6G_C 21 ka (Peltier et al. 2015; University of
#   Toronto data page): no licence is stated and the server's TLS chain does not
#   verify with a stock CA store; Ehlers & Gibbard limits (Elsevier booksite
#   shapefiles): licence unclear.
LGM_URL = "https://zenodo.org/records/14506525/files/ice_30s.nc"
LGM_BLOCK = 30
LGM_CACHE_VERSION = 1


def lgm_ice_raw() -> dict:
    """Observed LGM (21 ka) ice cover on a 0.25 deg grid: dict(frac (720, 1440)
    float16, the ice share of each pixel 0..1; lat (south to north), lon of the
    pixel centres)."""
    f = DATA / "raw_lgm_ice.npz"
    if not f.exists():
        from tools.h5_reader import read_variable
        from tools.tiff_reader import BytesSource
        DATA.mkdir(parents=True, exist_ok=True)
        src = BytesSource(_get(LGM_URL))  # one 24.5 MB download (Zenodo throttles many small range requests)
        frac = read_variable(src, "ice_cover_boolean", block=LGM_BLOCK)
        lat = read_variable(src, "lat").reshape(-1, LGM_BLOCK).mean(1)
        lon = read_variable(src, "lon").reshape(-1, LGM_BLOCK).mean(1)
        if frac.shape != (len(lat), len(lon)) or not 0 <= frac.min() <= frac.max() <= 1:
            raise RuntimeError("LGM ice file is not the expected 0/1 raster; its layout changed")
        np.savez_compressed(f, frac=frac.astype(np.float16), lat=lat, lon=lon)
    z = np.load(f)
    return {k: z[k] for k in z.files}


def earth_lgm_ice(grid) -> np.ndarray:
    """Share of each cell under LGM ice (0..1, area-weighted mean of the 0.25
    deg pixels in it). Cached as data/earth/lgm_ice_L{level}.npz."""
    f = DATA / f"lgm_ice_L{grid.level}.npz"
    if f.exists():
        z = np.load(f)
        if int(z["version"]) == LGM_CACHE_VERSION and len(z["ice"]) == grid.n:
            return z["ice"]
    r = lgm_ice_raw()
    LA, LO = np.meshgrid(r["lat"], r["lon"], indexing="ij")
    cell = grid.locate(_unit(LA.ravel(), LO.ravel()))
    w = np.cos(np.radians(LA.ravel()))
    num = np.bincount(cell, w * r["frac"].astype(np.float64).ravel(), grid.n)
    den = np.bincount(cell, w, grid.n)
    out = (num / np.maximum(den, 1e-12)).astype(np.float32)
    np.savez_compressed(f, version=LGM_CACHE_VERSION, ice=out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--level", type=int, default=6)
    a = ap.parse_args()
    from planet.grid import build_grid
    t0 = time.time()
    grid = build_grid(a.level)
    d = earth_on_grid(grid)
    land = land_of(d)
    print(f"level {a.level}: {grid.n} cells, land {land.mean():.1%}, "
          f"ice cells {(d['ice'] > 0).sum()} ({((d['ice'] > 0) & (d['elev'] <= 0)).sum()} on a bed below the sea), max surface {d['surface'].max():.0f} m, "
          f"{time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
