"""Coastal and shallow-sea life in the regional zoom (PW-188): coral reefs,
kelp forests, seagrass meadows, mangroves and salt marsh placed per pixel
on the zoom's own coastline and sea floor.

The world's rules (coastal.py) split into the water's or the climate's
part, interpolated from the coarse cells (coastal.environment: reef,
kelp_water, seagrass_water, mangrove_climate, salt_marsh_climate, the
mud and the light's attenuation Kd), and the place's part, from the pixel:
  reef        sea pixels shallower than the reefs' light depth (10% of the
              surface light, at most coastal.REEF_MAX_M); patches cover
              coastal.REEF_SHARE x the water's suitability of that floor.
              Plus the world's volcanoes' living reefs (zoom.volcanoes'
              fringing flats, barrier reefs and atoll rims).
  kelp        sea pixels above the kelp's light depth (1%, at most
              coastal.KELP_MAX_M) by a rocky shore: land rising ROCK_RISE m
              within ROCK_KM km, or hard rock at the shore (coastal.HARD_ROCKS),
              not muddy.
  seagrass    sea pixels above Duarte's depth limit, sheltered (the pixel's
              wave power), soft bottoms (not by a rocky shore), where no reef
              or kelp is.
  mangrove,   land pixels between the tides: low ground (below half the
  salt marsh  tidal range plus coastal.SETUP and SPRING_M) within TIDAL_KM
              of the sea and connected to it through such ground, or a
              sub-pixel fringe on the other shore pixels (their share below
              the high-tide line, heights exponentially distributed about
              the pixel's mean, as the globe's cells), sheltered and
              muddy (coastal.intertidal_habitat), warm enough for mangroves,
              else salt marsh (the climate's part).
The shoreface (shoreface(), PW-327, applied by zoom.build before the habitats):
  the sea floor off a sandy or muddy shore shoals to the coast along Dean's
  equilibrium profile h = A x^(2/3) (A = DEAN_A, fine sand) down to the
  closure depth (Houston 1995: ~6.75 x the mean significant wave height,
  from the pixel's wave power), then the inner shelf at SHELF_GRAD, until it
  meets the floor interpolated from the coarse cells; a rocky shore (land
  rising fast, or hard rock) keeps its deep water close in.
Reefs as terrain (PW-326): the reef pixels' floor is raised to a reef flat
  REEF_CREST_M below the sea (zoom.build keeps the cell means by deepening
  the rest of the shelf: the lagoons): patch reefs as above, plus a
  fringing reef along the shore of a shelf narrower than BARRIER_SHELF_KM
  (shore to the reefs' light depth) and a barrier reef along the outer edge
  of a wider one, each REEF_BAND_KM wide, broken by passes.
Each pixel is one habitat or none (layer `coastal_life`, LIFE): patches
from planet-fixed noise, so a pixel holds a habitat with the probability
its suitability gives (overlapping zooms agree). Mangrove and salt-marsh
pixels name the vegetation (vegetation.T "mangrove forest", "salt marsh").
"""

from __future__ import annotations

import math

import numpy as np

from .. import coastal as CL
from .. import vegetation as V
from . import kernels as ZK
from ..geo import R_KM

LIFE = {0: ("none", ""), 1: ("coral reef", "#ff6fa8"), 2: ("kelp forest", "#9a7b2a"),
        3: ("seagrass meadow", "#3fbf6a"), 4: ("mangrove", "#14d2b0"), 5: ("salt marsh", "#e3d65a")}
REEF, KELP, SEAGRASS, MANGROVE, SALT_MARSH = 1, 2, 3, 4, 5
TIDAL_KM = 30.0  # km: tidal creeks reach this far inland at most (the pixel must also lie between the tides)
SPRING_M = 0.5  # m: spring tides and surges reach this far above the mean high-water line
ROCK_KM = 3.0  # km: a rocky shore's land rises ...
ROCK_RISE = (30.0, 150.0)  # ... this much within ROCK_KM (from not to fully rocky)
PATCH_KM = {REEF: 6.0, KELP: 4.0, SEAGRASS: 8.0, MANGROVE: 3.0}  # km: the patches' size
FIELDS = ("reef", "kelp_water", "seagrass_water", "mud", "kd", "mangrove_climate", "salt_marsh_climate",
          "tide_range", "wave_power")
NEEDS = ("sst", "sst_jul", "sst_jan", "salinity", "wave_power", "tide_range", "warm_month", "cold_month",
         "precipitation", "downstream", "flow")  # the world layers coastal.environment needs
SEA_FIELDS = {"reef", "kelp_water", "seagrass_water", "mud", "kd", "tide_range", "wave_power"}


REEF_CREST_M = (1.0, 3.0)  # m: a reef's flat top lies this far below the sea (the run's reefs build to -5 m; the crest higher)
REEF_BAND_KM = 1.0  # km: fringing and barrier reefs this wide (at least a pixel)
BARRIER_SHELF_KM = 15.0  # km: a shelf this wide (shore to the reefs' light depth) has a barrier reef at its edge
REEF_PASS_KM = 8.0  # km: the reef bands' gaps (passes) come in patches this big ...
REEF_BAND_COVER = 0.85  # ... the bands covering this share of a fully suitable coast
REEF_BUDGET_KM = 20.0  # km: the bands' share of the shelf within this is taken off the patch reefs'
DEAN_A = 0.1  # m^(1/3): Dean's (1991) profile scale for fine sand (~0.2 mm): 10 m at 1 km, 21 m at 3 km
CLOSURE_HS = 6.75  # the closure depth over the mean annual significant wave height (Houston 1995)
CLOSURE_M = (3.0, 25.0)  # m: ... within these
WAVE_T = 8.0  # s: the waves' period, for their height from the power (deep water: P = rho g^2 H^2 T / 64 pi)
SHELF_GRAD = 1.5  # m/km: the inner shelf beyond the closure depth (~1:700) ...
SHELF_KM = 6.0  # km: ... fading into the coarse cells' floor over this far beyond it


def window_max(a: np.ndarray, r: int) -> np.ndarray:
    """Max over a (2r+1)^2 square around each pixel (2-D a; the edges see only what's inside)."""
    out = a.copy()
    for axis in (0, 1):
        src = np.pad(out, [(r, r) if k == axis else (0, 0) for k in (0, 1)], constant_values=-np.inf)
        n = a.shape[axis]
        for s in range(2 * r + 1):
            out = np.maximum(out, src[s:s + n] if axis == 0 else src[:, s:s + n])
    return out


def _uniform(Pk: np.ndarray, km: float, res: float, seed: int) -> np.ndarray:
    """~uniform 0..1 planet-fixed noise with patches ~km across."""
    octaves = max(1, int(math.ceil(math.log2(max(km / (2 * res), 1.0)))) + 1)
    z = ZK.fbm(Pk, km, octaves, 0.5, seed) / 0.17
    return 0.5 * (1 + _erf(z / math.sqrt(2)))


def _erf(x: np.ndarray) -> np.ndarray:
    # Abramowitz & Stegun 7.1.26 (|error| < 1.5e-7)
    s = np.sign(x)
    x = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-x * x)
    return s * y


def place(world: dict, fr, Pk: np.ndarray, px: np.ndarray, py: np.ndarray, nx: int, ny: int, res: float,
          size_km: float, seed: int, h: np.ndarray, water: np.ndarray, glacier: np.ndarray, d_sea: np.ndarray,
          surface_rock: np.ndarray | None = None, volcano_reef: np.ndarray | None = None) -> dict:
    """The zoom's coastal life. h: elevation (m; sea floor < 0), water (0
    land, 1 sea, 2 lake), glacier (bool), d_sea (km from land pixels to the
    sea), surface_rock (ROCKS ids), volcano_reef (bool: zoom.volcanoes' reef
    pixels); all flat (ny*nx). Returns {"layer": coastal_life (uint8, LIFE),
    "stats": km^2 of each habitat}."""
    from .vegetation import _sel
    g, L, meta = world["grid"], world["layers"], world["meta"]
    npx = nx * ny
    if not all(k in L for k in NEEDS):  # (a world without the sea's layers: hand-made in tests)
        return {"layer": np.zeros(npx, np.uint8), "stats": {LIFE[k][0]: 0 for k in LIFE if k},
                "reef_top": np.full(npx, np.nan), "shelf": np.zeros(npx, bool), "reef_forms": {}}
    pf = (meta.get("vegetation") or {}).get("pfts")
    unlocked = None if pf is None else np.array([c in pf for c in V.CODES])
    env = CL.environment(g, L, meta, unlocked)
    env["tide_range"] = np.asarray(L["tide_range"], float)
    env["wave_power"] = np.asarray(L["wave_power"], float)
    sel = _sel(g, fr, size_km)
    cx, cy = fr.to_plane(g.centers[sel])
    sea_c = np.asarray(L["elevation"], float)[sel] <= 0
    vals = np.column_stack([env[k][sel] for k in FIELDS])
    wts = np.column_stack([sea_c if k in SEA_FIELDS else np.ones(len(sel)) for k in FIELDS]).astype(float)
    f, _ = ZK.gauss_interp(px, py, cx, cy, vals, wts, 0.5 * g.spacing * R_KM)
    f = {k: np.nan_to_num(f[:, j]) for j, k in enumerate(FIELDS)}
    sea = water == 1
    land = (water == 0) & ~glacier
    depth = np.where(sea, -h, 0.0)
    kd = np.maximum(f["kd"], CL.KD_CLEAR)
    # a rocky shore: land rising ROCK_RISE within ROCK_KM, or hard rock at the shore, not muddy
    r = max(1, int(round(ROCK_KM / res)))
    hl = np.where(water == 0, np.maximum(h, 0.0), 0.0).reshape(ny, nx)
    rise = window_max(hl, r).ravel()
    rocky = CL.ramp(rise, *ROCK_RISE)
    if surface_rock is not None:
        hard = (np.isin(surface_rock, CL.HARD_ROCKS) & (water == 0)).reshape(ny, nx).astype(float)
        rocky = np.maximum(rocky, CL.HARD_ROCK * window_max(hard, r).ravel())
    rocky *= 1 - f["mud"]
    out = np.zeros(npx, np.uint8)
    S = int(seed) * 1_000_003 + 17 + 5_003
    u = {k: _uniform(Pk, km, res, S + 101 * k) for k, km in PATCH_KM.items()}
    # the sea floor: reefs, then kelp, then seagrass
    z_reef = np.minimum(CL.light_depth(kd, CL.REEF_LIGHT), CL.REEF_MAX_M)
    shelf = sea & (depth <= z_reef)
    # reefs as terrain (PW-326): along the shelf's own geometry, a fringing
    # reef along the shore of a narrow shelf, a barrier reef along the outer
    # edge of a wide one (the lagoon behind it), patch reefs in between: as
    # many fewer as the bands take of the shelf around (REEF_BUDGET_KM), so the
    # reefs keep the world's share
    x_shore = np.maximum(ZK.inside_distance(sea, nx, ny, False) - 0.5, 0.0) * res
    d_deep = ZK.inside_distance(~(sea & ~shelf), nx, ny, False) * res
    band = max(REEF_BAND_KM, res)
    wide = x_shore + d_deep >= BARRIER_SHELF_KM
    u_band = _uniform(Pk, REEF_PASS_KM, res, S + 707)
    # (a band a pixel wide on pixels coarser than it: as many of them as its area fills)
    ok = shelf & (u_band < REEF_BAND_COVER * f["reef"] * min(1.0, REEF_BAND_KM / res))
    fringing = ok & ~wide & (x_shore <= band)
    barrier = ok & wide & (d_deep <= band) & (x_shore > 2 * band)
    r_b = max(1, int(round(REEF_BUDGET_KM / res)))
    taken = _box_mean((fringing | barrier).reshape(ny, nx).astype(float), shelf.reshape(ny, nx).astype(float),
                      r_b).ravel()
    patch = shelf & ~fringing & ~barrier & (u[REEF] < CL.REEF_SHARE * f["reef"] - taken)
    reef = patch | fringing | barrier
    volc = np.zeros(npx, bool)
    if volcano_reef is not None:
        volc = sea & volcano_reef & (depth <= CL.REEF_MAX_M)
        reef |= volc
    out[reef] = REEF
    # their tops: a reef flat REEF_CREST_M below the sea (the volcanoes' reefs are their own terrain)
    top = reef & ~volc
    crest = REEF_CREST_M[0] + (REEF_CREST_M[1] - REEF_CREST_M[0]) * _uniform(Pk, 2.0 * res, res, S + 709)
    reef_top = np.where(top, -np.minimum(crest, depth), np.nan)
    cell_ = res * res
    forms = {"fringing": round(float((fringing & ~volc).sum() * cell_)),
             "barrier": round(float((barrier & ~volc).sum() * cell_)),
             "patch": round(float((patch & ~fringing & ~barrier & ~volc).sum() * cell_))}
    z_kelp = np.minimum(CL.light_depth(kd, CL.KELP_LIGHT), CL.KELP_MAX_M)
    kelp = sea & (out == 0) & (depth <= z_kelp) & (u[KELP] < f["kelp_water"] * rocky)
    out[kelp] = KELP
    seag = sea & (out == 0) & (depth <= CL.seagrass_depth(kd)) & (
        u[SEAGRASS] < f["seagrass_water"] * CL.sea_shelter(f["wave_power"], rocky))
    out[seag] = SEAGRASS
    # between the tides: low ground the tide reaches from the sea (connected to it through ground
    # below the high-tide line), and a sub-pixel fringe on the other shore pixels; mangroves, else
    # salt marsh
    hw = 0.5 * f["tide_range"] + CL.SETUP
    low = land & (h <= hw + SPRING_M) & (d_sea <= TIDAL_KM)
    lab, _ = ZK.label_components(sea | low, nx, ny)
    flooded = low & np.isin(lab, np.unique(lab[sea]))
    sp = np.pad(sea.reshape(ny, nx), 1)
    shore = land & (sp[:-2, 1:-1] | sp[2:, 1:-1] | sp[1:-1, :-2] | sp[1:-1, 2:]).ravel()
    share = np.where(flooded, 1.0, np.where(shore, 1 - np.exp(-hw / np.maximum(h, 0.5)), 0.0))
    p = share * CL.intertidal_habitat(f["wave_power"], f["mud"])
    pm, ps = p * f["mangrove_climate"], p * f["salt_marsh_climate"]
    um = u[MANGROVE]
    out[land & (um < pm)] = MANGROVE
    out[land & (um >= pm) & (um < pm + ps)] = SALT_MARSH
    cell = res * res
    stats = {LIFE[k][0]: round(float((out == k).sum() * cell)) for k in LIFE if k}
    return {"layer": out, "stats": stats, "reef_top": reef_top, "shelf": shelf, "reef_forms": forms}


def rocky_shore(h: np.ndarray, land: np.ndarray, surface_rock: np.ndarray | None, nx: int, ny: int,
                res: float) -> np.ndarray:
    """0..1 per pixel: a rocky shore nearby (within ROCK_KM): land rising
    ROCK_RISE m, or hard rock (coastal.HARD_ROCKS) at the shore."""
    r = max(1, int(round(ROCK_KM / res)))
    hl = np.where(land, np.maximum(h, 0.0), 0.0).reshape(ny, nx)
    rocky = CL.ramp(window_max(hl, r).ravel(), *ROCK_RISE)
    if surface_rock is not None:
        hard = (np.isin(surface_rock, CL.HARD_ROCKS) & land).reshape(ny, nx).astype(float)
        rocky = np.maximum(rocky, CL.HARD_ROCK * window_max(hard, r).ravel())
    return rocky


def closure(wave_kw_m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The shoreface's closure depth (m: CLOSURE_HS x the waves' mean
    significant height, from their power) and its distance off the shore
    on Dean's profile (km)."""
    hs = np.sqrt(64 * np.pi * 1000.0 * np.maximum(wave_kw_m, 0.0) / (1025.0 * 9.81**2 * WAVE_T))
    hc = np.clip(CLOSURE_HS * hs, *CLOSURE_M)
    return hc, (hc / DEAN_A) ** 1.5 / 1000.0


def shoreface_depth(x_km: np.ndarray, wave_kw_m: np.ndarray) -> np.ndarray:
    """m: the equilibrium sea floor's depth x_km off the shore: Dean's
    profile A x^(2/3) down to the closure depth, the inner shelf beyond it."""
    hc, xc = closure(wave_kw_m)
    x = np.maximum(x_km, 0.0)
    return np.where(x <= xc, DEAN_A * (1000.0 * x) ** (2 / 3), hc + SHELF_GRAD * (x - xc))


def _box_mean(a: np.ndarray, w: np.ndarray, r: int) -> np.ndarray:
    """Weighted mean of a over (2r+1)^2 windows (2-D a, w)."""
    def box(v):
        c = np.cumsum(np.pad(v, ((r + 1, r), (0, 0)), mode="edge"), 0)
        v = c[2 * r + 1:] - c[:-2 * r - 1]
        c = np.cumsum(np.pad(v, ((0, 0), (r + 1, r)), mode="edge"), 1)
        return c[:, 2 * r + 1:] - c[:, :-2 * r - 1]
    return box(a) / np.maximum(box(w), 1e-9)


def shoreface(h: np.ndarray, sea: np.ndarray, rocky: np.ndarray, wave_kw_m: np.ndarray, nx: int, ny: int,
              res: float, keep: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """The sea floor h with a shoreface (PW-327): no deeper than
    shoreface_depth() at the pixel's distance from the shore (the shore
    halfway to the nearest land pixel), out to the closure depth's distance,
    then fading into the floor h (the coarse cells': their shelves and
    slopes) over SHELF_KM; by 1 - the rockiness of the shore around (rocky
    on its land pixels, averaged along the coast: a cliffed coast keeps its
    deep water close in), and not where keep (0..1) holds the floor (the
    volcanoes' reefs and lagoons). Returns (h, reach: 0..1, the shoreface's
    extent, where the caller shouldn't put the cells' means back)."""
    x = np.maximum(ZK.inside_distance(sea, nx, ny, False) - 0.5, 0.25) * res
    z = np.minimum(-shoreface_depth(x, wave_kw_m), -0.5)
    _, xc = closure(wave_kw_m)
    span = max(SHELF_KM, 2 * res)
    t = np.clip(1 - (x - xc) / span, 0.0, 1.0)
    reach = t * t * (3 - 2 * t)
    s2 = sea.reshape(ny, nx)
    sp = np.pad(s2, 1)
    coast = ~s2 & (sp[:-2, 1:-1] | sp[2:, 1:-1] | sp[1:-1, :-2] | sp[1:-1, 2:])
    r = int(np.ceil((float(np.max(xc, initial=0.0)) + span) / res)) + 1
    rk = _box_mean(np.where(coast, rocky.reshape(ny, nx), 0.0), coast.astype(float), r).ravel()
    w = (1 - np.clip(rk, 0, 1)) * (1 - (0.0 if keep is None else keep)) * reach
    return np.where(sea, h + w * np.maximum(z - h, 0.0), h), np.where(sea, reach, 0.0)


def name_vegetation(layer: np.ndarray, vegetation: np.ndarray) -> np.ndarray:
    """The vegetation layer with mangrove and salt-marsh pixels named so."""
    v = np.asarray(vegetation).copy()
    v[layer == MANGROVE] = V.T["mangrove forest"]
    v[layer == SALT_MARSH] = V.T["salt marsh"]
    return v


def legend() -> list[dict]:
    return [{"id": k, "name": n, "color": c} for k, (n, c) in LIFE.items() if k]
