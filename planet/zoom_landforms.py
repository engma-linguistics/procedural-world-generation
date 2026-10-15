"""Landform synthesis in the regional zoom (PW-010..012): each coarse cell's
landform class (landform.py) turns into its own kind of terrain.

Class dispatch
--------------
SYNTH maps a landform class id to a synthesiser (a Synth subclass). A
synthesiser overrides the hooks it needs (the defaults contribute nothing);
the dispatcher (Landforms) blends what they return by the class's weight w_k:

  target(cx, h)    metres added to the zoom's target surface before the
                   landscape pass (and before its coarse-mean correction):
                   the structure the drainage organises around (rivers in
                   the strike valleys and grabens, round the domes).
  relief(cx)       (A, G): how the finished landscape's relief is reshaped
                   around its drainage. Each pixel's height above the first
                   channel down its receivers, d, becomes D (1 - exp(-A d /
                   dref)) with D = G (1+A)/A dref (dref: d's local mean): flat
                   interfluves over steep valley walls (a plateau and its
                   canyons), G x as deep. Integrated down the drainage
                   (relief_along()), so channels keep their height and every
                   pixel stays above its receiver.
  shape(cx, h)     metres added to the reshaped surface: the structure
                   itself, sharp (fault blocks, folds, domes). Synth.gaps:
                   rivers >= GAP_Q keep their graded beds through it.
  strata(cx, h)    a Strata: how hard beds turn the reshaped surface into
                   benches and scarps (bench_map()), as h + sum_k w_k (z_k - h).
                   A channel crossing a cliff falls over it.
  basins(cx),      0..1 per pixel: where the class's closed depressions stay
  lakes(cx)        closed (not breached, but for rivers >= zoom.BASIN_THROUGH_Q)
                   and where they may hold water: whether one does is its
                   water balance's call (basin_lakes(), PW-167: full lakes
                   spilling into the next, closed lakes below the spill, dry
                   flats; the rest are filled flat).
  overlay(cx, h,   metres added to the finished land after the final
          fin)     drainage (Landforms.finish): a veneer the rivers no longer
                   reshape (dunes; karst's dolines, poljes, towers), kept off
                   streams >= overlay_q, mean-neutral over ~a cell; with
                   `ponds`, its pits below the water table (the first flowing
                   river down the drainage) hold water.
  sinks(cx)        0..1: where streams under SINK_Q x this sink (karst; an
                   erg's wadis): their valleys dry, the water resurging at
                   springs where they leave the class.
  layers           (attribute) the world layers the class reads, interpolated
                   over its own cells into Ctx.prm (DERIVED: hardness of the
                   exposed and next strata, granite; DEFAULTS for layers a
                   world lacks).
  zoned            (attribute) the class gets Ctx.zone (zone_stats(), PW-148):
                   per pixel the statistics of its connected zone on the
                   whole coarse grid, so its levels are the same in every
                   zoom that sees it.
  axis             (attribute) 'band' / 'gradient' / 'wind': the class gets Ctx.frames,
                   planet-fixed structural patches with their own strike
                   (build_frames): ~200 km Voronoi patches of a jittered 3D
                   lattice, the strike of each read from the coarse cells
                   around its centre, blended over ~18 km at their edges
                   (where faults and folds die out: relay ramps, fold noses).
                   Deterministic in planet coordinates, like the noise.

The strata also tell the designed falls (zoom.knickpoints / staircase) about
the plateau: plateau() is where a top bed holds the ground up (the
staircase may stand that high), scarps() where a single scarp (the
escarpment) is: a designed reach crossing it takes its main fall there, the
river running on the plateau down to the lip.

Weights: a class's weight is the Gaussian-kernel share of its cells around
each pixel (sigma half a cell, over the projected cell centres, as the
zoom's other coarse fields), roughened by noise and sharpened by a
smoothstep: classes blend over ~20-40 km, with no hexagon or cell-edge seam.
Narrow classes (the escarpment, the rift: a band one or two cells wide) get
a lower threshold. Where weights add up to more than 1, the class that
landform.classify ranks first keeps its weight (PRIORITY).

In zoom.build, after the landscape pass and creep: remap() on the drainage
of the crept surface (not on glaciers, lake rims and outflows, nor within a
few km of the designed falls' courses, whose staircase is the river's);
then any sill left across a flow path is cut through (cut(): breach(), the
cut widened into a gap a few pixels wide; inside the classes' reach, not
across closed basins), each coarse cell's mean restored by a smooth
correction weighted to where the classes are, falls over the classes' cliffs
retreated into gorges (scarp_gorges()), and the result cut again. In the
final drainage the classes' closed basins become lakes or flats.

Levels are one per zone (PW-148): a class's connected region of cells on
the whole coarse grid (zone_stats()), not the zoom's own pixels, so two
overlapping zooms put each bench at the same height. Flat-lying beds are
horizontal: a level that varied across the land faster than its rivers fall
would meet them with cliffs from below; the caprock's and lava plateau's
anchor and period are constant over the zone; the escarpment's e* is a
smooth field of the zone's cells within ~ZONE_LOCAL_KM (it follows the
margin's height along a long escarpment).

Bench map (bench_map(), shared by batch 1). Anti-aliased (Landforms._bench):
each cliff spans at least FACE_PX pixels across, and where a band is
narrower than BAND_MIN_PX (a steep valley side) the benches fade out rather
than stipple it.
------------------------------------------
Hard beds over soft, read along a stratigraphic height s = h + tilt.x (the
bedding dips by `tilt` m/km; none for flat-lying strata): above `anchor` the
top bed (relief scaled by top_k: a plateau); below it `bands` benches each
`period` m high: from the bench (the top of the bed below) a soft slope
steepening upwards (power), then the hard bed's face, cliff x period. Below
the last band the land is left alone; endless benches are shifted so the
land keeps its level on average. A channel crossing a cliff drops over it:
a waterfall with the bench above as its plateau; a valley cut below a level
lets the scarp retreat up it (re-entrants, crenulated scarps); a hill above
a level in front of it becomes a mesa or butte.

Batch 1 (PW-010):
  escarpment     one band 0.8 e* deep below the escarpment zone's level e*
                 (its cells' median around), with a 0.75 cliff: the plateau
                 stays, the land in front of it steps down to a lowland
                 (Drakensberg, Western Ghats). The class rule puts the scarp at
                 its retreat distance from the rifted coast; valleys below e*
                 make the re-entrants of headward retreat, and the rivers
                 crossing it fall over it.
  caprock        hard caps (the zone's strata_top_km, 40-400 m, at most 1.5x
                 the zone's typical relief, so benches show on low land too)
                 over soft slopes, endlessly repeated down from the zone's
                 85th percentile of elevation: plateau, mesas, buttes and
                 stepped benches (Grand Staircase); relief 1.5x deeper. A
                 dip (strata_dip, downhill) tilts them into asymmetric
                 cuestas (scarps facing up-dip, long dip slopes).
  lava plateau   stacked flows: steps of >= 110 m (a package of flows at
                 zoom pixels; 0.65x the zone's typical relief) under a flat
                 top (the zone's 95th percentile, relief x 0.3): stair-
                 stepped valley sides (Deccan, Columbia River).

Batch 2 (PW-011), on the target and shape hooks:
  fold belt      FoldBelt: parallel folds across the shortening (the strike
                 from the thickened crust, high ground and a converging
                 boundary), fold_wavelength apart, amplitude from the dip;
                 young belts stand as whaleback anticlines (Zagros), old
                 ones as hogbacks of the hard beds closing round plunging
                 noses (Valley and Ridge); trellis drainage, water gaps.
  rift           Rift: tilted fault blocks 10-30 km wide along the rift's
                 band, scarps on one side, back-tilts, flat sediment-filled
                 half-grabens (lakes in a wet climate); throw from
                 rift_strain (ln beta) and age, facing flipping between
                 patches.
  shield         Shield: a flattened plain with granite domes and
                 inselbergs; recently glaciated (glaciated_myr): domes
                 ground down, rock basins with lakes.

Batch 3 (PW-012), on the overlay and sinks hooks:
  karst          Karst: small streams sink (dry valleys, springs); dolines
                 and poljes (temperate, Dinaric) or towers on a flattened
                 corrosion plain (wet tropics, Guilin); ponds where pits
                 reach the water table; limestone vs dolomite (purity).
  dune field     Dunes: an overlay on the land, type from the seasons' sand
                 drift (sand_drift, RDP/DP): transverse ridges / barchans,
                 linear, star; spacing and height from the sand's
                 thickness; patches oriented by the drift ('wind' frames).
  coastal plain  CoastalPlain: a smoothed plain sloping to the sea, rivers
                 wandering over its micro-relief, low cuestas where its beds
                 dip seaward (a shift by the coarse coast distance); barrier
                 islands, lagoons and marshes on its wave-dominated coasts
                 are drawn with the coastline (zoom.build).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numba import njit, prange

from . import landform as LF
from . import zoom_kernels as ZK
from .geo import R_KM

# how well each rock (surface.ROCKS id) holds a lip or stands as a ridge (0..1);
# zoom.KP_RESIST is this table
RESIST = {0: 0.8, 1: 0.9, 2: 0.8, 3: 0.4, 4: 0.85, 5: 1.0, 6: 0.75, 7: 0.7, 8: 0.2, 9: 0.1, 10: 0.3,
          11: 1.0, 12: 0.95, 13: 0.9, 14: 0.85, 15: 0.5}


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


@dataclass
class Strata:
    """A bench map's parameters, per pixel (arrays or scalars; see bench_map())."""
    anchor: np.ndarray
    period: np.ndarray
    bands: float = np.inf
    cliff: float | np.ndarray = 0.5
    power: float | np.ndarray = 2.0
    top_k: float | np.ndarray = 1.0
    tilt: tuple | None = None  # (tx, ty) m/km: the bedding drops along (tx, ty)...
    origin: tuple = (0.0, 0.0)  # ... from (ox, oy) km (zoom plane; a planet-fixed point: the zone's own)
    shift: np.ndarray | None = None  # m added to s (beds whose height follows a planet-fixed field)
    amp: float | np.ndarray = 1.0  # how much of the bench map's change applies (0: the land as it is)
    face: float = 0.08  # the share of a band its cliff rises over (bench_map)

    def height(self, h, px, py):
        """The stratigraphic height s the bench map reads: h, plus the tilt
        and shift."""
        s = h if self.shift is None else h + self.shift
        if self.tilt is None:
            return s
        return s + self.tilt[0] * (px - self.origin[0]) + self.tilt[1] * (py - self.origin[1])


def bench_map(s, anchor, period, bands=np.inf, cliff=0.5, power=2.0, top_k=1.0, face=0.08):
    """Benches and cliffs of hard beds over soft, as a function of the
    stratigraphic height s (m; all per pixel). Above `anchor`: anchor +
    (s - anchor) x top_k. Band j (0 = the highest) spans [anchor - (j+1) P,
    anchor - j P): from its bottom (the bench of the bed below) the land
    rises (1 - cliff) P u^power (u: 0 -> 1 up the band), then the hard bed's
    face, cliff x P, over its top `face`. Below `bands` bands, z = s; with
    endless bands, all of it is shifted up by the bands' mean lowering, so
    the land keeps its level on average. Monotone and continuous in s."""
    P = np.maximum(period, 1.0)
    d = (anchor - s) / P
    j = np.floor(d)
    u = 1.0 - (d - j)
    # (the face takes the band's top `face`: steep, but a slope, not a one-pixel step that aliases)
    z = anchor - (j + 1) * P + P * ((1 - cliff) * u ** power + cliff * smoothstep(1 - face, 1.0, u))
    z = np.where(j < bands, z, s)
    z = np.where(s >= anchor, anchor + (s - anchor) * top_k, z)
    if np.isinf(bands):  # (endless benches: shifted so that on average they neither lift nor lower the land)
        z = z + P * (0.5 - (1 - cliff) / (power + 1) - cliff * face / 2)
    return z


@dataclass
class Ctx:
    """What a synthesiser sees: the zoom's raster and projection, its smooth
    coarse fields, and the class's own weight and parameters."""
    nx: int
    ny: int
    res: float  # km per pixel
    sp: float  # coarse cell spacing, km
    px: np.ndarray  # pixel x, y (km east, north of the centre)
    py: np.ndarray
    Pk: np.ndarray  # pixel positions on the planet (km), for noise
    seed: int  # noise seed base
    land: np.ndarray
    base: np.ndarray  # smooth coarse land elevation (m)
    downhill: tuple  # unit vector field (dx, dy) of the coarse land's regional downhill
    grad: np.ndarray  # m/km: the regional slope of the coarse land
    w: np.ndarray = None  # this class's weight
    prm: dict = field(default_factory=dict)  # this class's layers, interpolated over its own cells
    relief_m: float | None = None  # its mean height above the drainage (Landforms.remap)
    frames: Frames | None = None  # structural patches (Synth.axis)
    chan: np.ndarray | None = None  # the channels (Landforms.remap)
    zone: dict | None = None  # per pixel, its zone's statistics (Synth.zoned; zone_stats())
    cache: dict = field(default_factory=dict)

    def noise(self, wavelength, octaves, k):
        """fbm ~N(0, 1)-ish at `wavelength` km (seed offset k)."""
        return ZK.fbm(self.Pk, wavelength, octaves, 0.5, self.seed + k) / 0.17

    def zone_relief(self, h):
        """m: the class's typical height above its drainage (set by
        Landforms.remap; else the spread of h about its local mean)."""
        if self.relief_m is not None:
            return self.relief_m
        on = self.land & (self.w > 0.5)
        if not on.any():
            return 50.0
        return float(np.mean(np.abs(h - self.local_top(h, 0.3 * self.sp, 0.0))[on]))

    def local_top(self, h, radius_km, k=1.0):
        """A smooth 'interfluve level': the local mean + k standard deviations
        of h over a box of `radius_km` (land only)."""
        r = max(1, int(round(radius_km / self.res)))
        wm = self.land.reshape(self.ny, self.nx).astype(float)
        hh = np.maximum(h, 0).reshape(self.ny, self.nx)
        m = _box_mean(hh * wm, wm, r)
        v = _box_mean(hh * hh * wm, wm, r) - m * m
        return (m + k * np.sqrt(np.maximum(v, 0))).ravel()


def _box_mean(a, w, r):
    def box(x):
        c = np.cumsum(np.pad(x, ((r + 1, r), (0, 0)), mode="edge"), 0)
        x = c[2 * r + 1:] - c[:-2 * r - 1]
        c = np.cumsum(np.pad(x, ((0, 0), (r + 1, r)), mode="edge"), 1)
        return c[:, 2 * r + 1:] - c[:, :-2 * r - 1]
    return box(a) / np.maximum(box(w), 1e-9)


# ---------------------------------------------------------------------------
# Structural frames (PW-011): planet-fixed patches, each with its own strike
# ---------------------------------------------------------------------------
PATCH_KM = 300.0  # lattice of the patches' centres (Voronoi patches ~200 km across)
PATCH_BLEND = 0.06  # x PATCH_KM: neighbouring patches blend over this (fault tips, fold noses)


@njit(cache=True, inline="always")
def _u01(h, k):
    """The k-th 16-bit field of hash h, as a float in [0, 1)."""
    return float((h >> np.uint64(16 * k)) & np.uint64(0xFFFF)) / 65536.0


@njit(cache=True, parallel=True)
def worley2(P, cell, seed):
    """The two nearest feature points of a jittered 3D lattice (spacing
    `cell` km) to each point P (N, 3; km on the sphere), the feature points
    projected onto the sphere: (id1, id2 (hashes), c1, c2 (unit vectors),
    d1, d2 (km))."""
    n = P.shape[0]
    id1, id2 = np.zeros(n, np.int64), np.zeros(n, np.int64)
    c1, c2 = np.zeros((n, 3)), np.zeros((n, 3))
    d1, d2 = np.full(n, np.inf), np.full(n, np.inf)
    for i in prange(n):
        r = np.sqrt(P[i, 0] ** 2 + P[i, 1] ** 2 + P[i, 2] ** 2)
        bx, by, bz = np.floor(P[i, 0] / cell), np.floor(P[i, 1] / cell), np.floor(P[i, 2] / cell)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    ix, iy, iz = np.int64(bx) + dx, np.int64(by) + dy, np.int64(bz) + dz
                    h = ZK._hash(ix, iy, iz, seed)
                    fx = (ix + _u01(h, 0)) * cell
                    fy = (iy + _u01(h, 1)) * cell
                    fz = (iz + _u01(h, 2)) * cell
                    nf = np.sqrt(fx * fx + fy * fy + fz * fz)
                    ux, uy, uz = fx / nf, fy / nf, fz / nf
                    d = np.sqrt((P[i, 0] - r * ux) ** 2 + (P[i, 1] - r * uy) ** 2 + (P[i, 2] - r * uz) ** 2)
                    hid = np.int64(h >> np.uint64(2))
                    if d < d1[i]:
                        d2[i], id2[i], c2[i, 0], c2[i, 1], c2[i, 2] = d1[i], id1[i], c1[i, 0], c1[i, 1], c1[i, 2]
                        d1[i], id1[i], c1[i, 0], c1[i, 1], c1[i, 2] = d, hid, ux, uy, uz
                    elif d < d2[i] and hid != id1[i]:
                        d2[i], id2[i], c2[i, 0], c2[i, 1], c2[i, 2] = d, hid, ux, uy, uz
    return id1, id2, c1, c2, d1, d2


@njit(cache=True, parallel=True)
def domes(P, cell, seed, prob, r_km, hk, aspect, rmin):
    """Rock domes (bornhardts, inselbergs) at the feature points of a
    jittered 3D lattice (spacing `cell` km; each point a dome with
    probability prob): radius r_km = (lo, hi) km, height hk = (lo, hi) x
    the radius (m per m), elongated up to `aspect` along a random azimuth;
    domes smaller than rmin km are left out (unresolved). Each a steep-
    sided, round-topped (1 - q^2)^0.6 (q: elliptical radius / R). Returns the
    highest dome over each point P (N, 3; km), m."""
    n = P.shape[0]
    out = np.zeros(n)
    for i in prange(n):
        r = np.sqrt(P[i, 0] ** 2 + P[i, 1] ** 2 + P[i, 2] ** 2)
        bx, by, bz = np.floor(P[i, 0] / cell), np.floor(P[i, 1] / cell), np.floor(P[i, 2] / cell)
        best = 0.0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    ix, iy, iz = np.int64(bx) + dx, np.int64(by) + dy, np.int64(bz) + dz
                    h = ZK._hash(ix, iy, iz, seed)
                    if _u01(h, 3) >= prob:
                        continue
                    h2 = ZK._hash(ix, iy, iz, seed + 7)
                    R = r_km[0] + (r_km[1] - r_km[0]) * _u01(h2, 0) ** 1.5
                    if R < rmin:
                        continue
                    fx = (ix + _u01(h, 0)) * cell
                    fy = (iy + _u01(h, 1)) * cell
                    fz = (iz + _u01(h, 2)) * cell
                    nf = np.sqrt(fx * fx + fy * fy + fz * fz)
                    cx_, cy_, cz_ = fx / nf, fy / nf, fz / nf
                    ox, oy, oz = P[i, 0] - r * cx_, P[i, 1] - r * cy_, P[i, 2] - r * cz_
                    if ox * ox + oy * oy + oz * oz > (R * aspect) ** 2:
                        continue
                    # local east, north at the dome
                    ex, ey = -cy_, cx_
                    ne = np.sqrt(ex * ex + ey * ey) + 1e-12
                    ex, ey = ex / ne, ey / ne
                    nx_, ny_, nz_ = -cz_ * ey, cz_ * ex, cx_ * ey - cy_ * ex
                    a = ox * ex + oy * ey
                    b = ox * nx_ + oy * ny_ + oz * nz_
                    th = 6.283185307 * _u01(h2, 1)
                    s = 1.0 + (aspect - 1.0) * _u01(h2, 2)
                    a1 = a * np.cos(th) + b * np.sin(th)
                    a2 = -a * np.sin(th) + b * np.cos(th)
                    q = np.sqrt((a1 / (R * np.sqrt(s))) ** 2 + (a2 * np.sqrt(s) / R) ** 2)
                    if q >= 1.0:
                        continue
                    z = 1000.0 * R * (hk[0] + (hk[1] - hk[0]) * _u01(h2, 3)) * (1.0 - q * q) ** 0.6
                    if z > best:
                        best = z
        out[i] = best
    return out


@njit(cache=True, parallel=True)
def blobs(P, cell, seed, prob, r_km, aspect, rmin):
    """Features at the points of a jittered 3D lattice (spacing `cell` km;
    each point a feature with probability prob): ellipses of radius R in
    r_km = (lo, hi) km, elongated up to `aspect` along a random azimuth;
    features smaller than rmin km are left out (unresolved). Per point P
    (N, 3; km), of the feature it lies deepest in (the smallest q): q, its
    elliptical radius / R (inf: none near), the feature's id (a hash; -1),
    its R (km) and the angle of P around its centre (rad, in the feature's
    own frame)."""
    n = P.shape[0]
    qo, ido, ro, ao = np.full(n, np.inf), np.full(n, -1, np.int64), np.zeros(n), np.zeros(n)
    for i in prange(n):
        r = np.sqrt(P[i, 0] ** 2 + P[i, 1] ** 2 + P[i, 2] ** 2)
        bx, by, bz = np.floor(P[i, 0] / cell), np.floor(P[i, 1] / cell), np.floor(P[i, 2] / cell)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    ix, iy, iz = np.int64(bx) + dx, np.int64(by) + dy, np.int64(bz) + dz
                    h = ZK._hash(ix, iy, iz, seed)
                    if _u01(h, 3) >= prob:
                        continue
                    h2 = ZK._hash(ix, iy, iz, seed + 7)
                    R = r_km[0] + (r_km[1] - r_km[0]) * _u01(h2, 0) ** 1.5
                    if R < rmin:
                        continue
                    fx = (ix + _u01(h, 0)) * cell
                    fy = (iy + _u01(h, 1)) * cell
                    fz = (iz + _u01(h, 2)) * cell
                    nf = np.sqrt(fx * fx + fy * fy + fz * fz)
                    cx_, cy_, cz_ = fx / nf, fy / nf, fz / nf
                    ox, oy, oz = P[i, 0] - r * cx_, P[i, 1] - r * cy_, P[i, 2] - r * cz_
                    if ox * ox + oy * oy + oz * oz > (3.0 * R * aspect) ** 2:
                        continue
                    ex, ey = -cy_, cx_
                    ne = np.sqrt(ex * ex + ey * ey) + 1e-12
                    ex, ey = ex / ne, ey / ne
                    nx_, ny_, nz_ = -cz_ * ey, cz_ * ex, cx_ * ey - cy_ * ex
                    a = ox * ex + oy * ey
                    b = ox * nx_ + oy * ny_ + oz * nz_
                    th = 6.283185307 * _u01(h2, 1)
                    s = 1.0 + (aspect - 1.0) * _u01(h2, 2)
                    a1 = a * np.cos(th) + b * np.sin(th)
                    a2 = -a * np.sin(th) + b * np.cos(th)
                    q = np.sqrt((a1 / (R * np.sqrt(s))) ** 2 + (a2 * np.sqrt(s) / R) ** 2)
                    if q < qo[i]:
                        qo[i], ido[i], ro[i], ao[i] = q, np.int64(h2 >> np.uint64(2)), R, np.arctan2(a2, a1)
    return qo, ido, ro, ao


def hashf(*ints):
    """A uniform [0, 1) per element from integer arrays (vectorised hash)."""
    h = np.zeros(np.broadcast(*ints).shape, np.uint64)
    with np.errstate(over="ignore"):
        for k, a in enumerate(ints):
            a = np.asarray(a).astype(np.int64).astype(np.uint64)
            h = (h ^ (a * np.uint64(0x9E3779B185EBCA87 + 2 * k))) * np.uint64(0xBF58476D1CE4E5B9)
            h ^= h >> np.uint64(29)
    return (h >> np.uint64(40)).astype(float) / float(1 << 24)


def _basis(c):
    """Local (east, north) unit vectors at unit vectors c (m, 3)."""
    e = np.cross(np.array([0.0, 0.0, 1.0]), c)
    ne = np.linalg.norm(e, axis=1, keepdims=True)
    e = np.where(ne > 1e-9, e / np.maximum(ne, 1e-12), np.array([0.0, 1.0, 0.0]))
    return e, np.cross(c, e)


@dataclass
class Frames:
    """Planet-fixed structural patches over a zoom: each pixel's two
    nearest patches k[0], k[1] (indices into the patch table `patch`), its
    coordinates in their frames, u (km across the strike) and v (km along
    it), the blend alpha (0: all k[0]; 0.5 on the patches' boundary) and
    edge (0 on the boundary, 1 inside: faults and folds die out there).
    patch: per patch, 'id', 'r0'..'r3' (uniforms), the class's layers
    averaged over its cells around the patch centre, and 'axis_deg'."""
    k: tuple
    u: tuple
    v: tuple
    alpha: np.ndarray
    edge: np.ndarray
    patch: dict

    def blend(self, f):
        """sum_j w_j f(j) over the two patches (f(j) -> per pixel)."""
        return (1 - self.alpha) * f(0) + self.alpha * f(1)


def _axis_tensor(X, Y, w, v, sp):
    """Doubled-angle strike vector (cos 2t, sin 2t) x coherence of a field v
    over cells at X, Y (km) weighted w: the strike runs across the dominant
    direction of v's differences between neighbouring cells (a structure
    tensor: sign-free, robust to noise)."""
    ii, jj = np.triu_indices(len(X), 1)
    dx, dy = X[jj] - X[ii], Y[jj] - Y[ii]
    dl = np.hypot(dx, dy)
    nb = (dl > 1e-6) & (dl < 1.6 * sp)
    if nb.sum() < 6:
        return np.zeros(2)
    wp = np.sqrt(w[ii[nb]] * w[jj[nb]]) * ((v[jj] - v[ii])[nb] / dl[nb]) ** 2
    ux, uy = dx[nb] / dl[nb], dy[nb] / dl[nb]
    T = np.array([[np.sum(wp * ux * ux), np.sum(wp * ux * uy)], [np.sum(wp * ux * uy), np.sum(wp * uy * uy)]])
    ev, evec = np.linalg.eigh(T)
    if ev[1] <= 1e-12:
        return np.zeros(2)
    t = np.arctan2(evec[0, 1], -evec[1, 1])  # (across the gradient)
    return (ev[1] - ev[0]) / (ev[1] + ev[0]) * np.array([np.cos(2 * t), np.sin(2 * t)])


def _band_tensor(X, Y, w):
    """Doubled-angle vector x elongation of the cells X, Y weighted w (their long axis)."""
    if w.sum() < 1.0:
        return np.zeros(2)
    mx, my = np.sum(w * X) / w.sum(), np.sum(w * Y) / w.sum()
    cv = np.array([[np.sum(w * (X - mx) ** 2), np.sum(w * (X - mx) * (Y - my))],
                   [np.sum(w * (X - mx) * (Y - my)), np.sum(w * (Y - my) ** 2)]])
    ev, evec = np.linalg.eigh(cv)
    t = np.arctan2(evec[1, 1], evec[0, 1])
    return (ev[1] - ev[0]) / max(ev[1] + ev[0], 1e-9) * np.array([np.cos(2 * t), np.sin(2 * t)])


# strike cues (build_frames): (kernel x cell spacing, weight) per cue and axis kind
AXIS_CUES = {"band": {"class": (1.5, 3.0), "thick": (4.0, 0.5), "elev": (4.0, 0.5)},
             "gradient": {"thick": (4.0, 1.0), "elev": (4.0, 1.0), "converging": (4.0, 2.0), "class": (4.0, 0.3)},
             "wind": {"wind": (2.0, 1.0)}}


def build_frames(Pk, seed, cells, ind, vals: dict, cues: dict, sp, axis: str) -> Frames:
    """Structural patches for a class: Voronoi cells of a jittered lattice
    (PATCH_KM, boundaries warped), each with a strike read from the coarse
    cells around its centre (cells: unit vectors; ind: the class's
    indicator; cues: per cell 'thick' (crust thickness), 'elev' and
    'converging' (a converging plate boundary)), the cues' doubled angles
    averaged by their coherence (AXIS_CUES): for a 'band' class (the rift)
    mostly the long axis of its band of cells; for a 'gradient' one (the
    fold belt: folds run across the shortening) the trend of the thickened
    crust and the high ground, and of the converging boundary (the suture)
    when there is one near; a random strike where no cue says. The class's
    layers `vals` are averaged over its cells near each centre."""
    wamp = 0.12 * PATCH_KM
    wv = np.column_stack([ZK.fbm(Pk, 0.5 * PATCH_KM, 3, 0.5, seed + 301 + j) / 0.17 for j in range(3)])
    Pw = np.ascontiguousarray(Pk + wamp * wv)
    id1, id2, c1, c2, d1, d2 = worley2(Pw, PATCH_KM, np.int64(seed + 311))
    ids, first = np.unique(np.concatenate([id1, id2]), return_index=True)
    C = np.concatenate([c1, c2])[first]
    k1, k2 = np.searchsorted(ids, id1), np.searchsorted(ids, id2)
    e, nn = _basis(C)
    npch = len(ids)
    ax2 = np.zeros((npch, 2))
    out = {name: np.zeros(npch) for name in vals}
    for p in range(npch):
        d = np.arccos(np.clip(cells @ C[p], -1, 1)) * R_KM
        sig = 1.5 * sp
        m = d < 3.5 * sig
        w = np.exp(-0.5 * (d[m] / sig) ** 2)
        wi = w * ind[m]
        for name, v in vals.items():
            vv = v[m]
            out[name][p] = np.sum(wi * vv) / np.sum(wi) if wi.sum() > 1e-6 else (
                np.sum(w * vv) / max(np.sum(w), 1e-9))
        acc = np.zeros(2)
        for cue, (ks, wt) in AXIS_CUES[axis].items():
            m = d < 3 * ks * sp
            if m.sum() < 4:
                continue
            w = np.exp(-0.5 * (d[m] / (ks * sp)) ** 2)
            X = (cells[m] - C[p]) @ e[p] * R_KM
            Y = (cells[m] - C[p]) @ nn[p] * R_KM
            if cue == "class":
                acc += wt * _band_tensor(X, Y, w * ind[m])
            elif cue == "wind":  # (the sand's resultant drift direction over the class's cells)
                de, dn = cues["drift_e"][m], cues["drift_n"][m]
                a, mg = np.arctan2(dn, de), w * ind[m] * np.hypot(de, dn)
                if mg.sum() > 1e-9:
                    acc += wt * np.array([np.sum(mg * np.cos(2 * a)), np.sum(mg * np.sin(2 * a))]) / mg.sum()
            elif cue == "converging":
                b = cues["converging"][m] > 0
                if (w * b).sum() >= 2.0:
                    acc += wt * _band_tensor(X, Y, w * b)
            else:
                acc += wt * _axis_tensor(X, Y, w, cues[cue][m], sp)
        if np.hypot(*acc) > 0.05:
            t = 0.5 * np.arctan2(acc[1], acc[0])
        else:
            t = np.pi * hashf(ids[p] % 1000003, 5)
        ax2[p] = np.cos(t), np.sin(t)
    a3 = ax2[:, :1] * e + ax2[:, 1:] * nn  # along the strike
    n3 = np.cross(C, a3)  # across it
    out["id"] = ids
    out["centre"] = C
    for j in range(4):
        out[f"r{j}"] = hashf(ids % 2147483647, 11 + j)
    out["axis_deg"] = np.degrees(np.arctan2(ax2[:, 1], ax2[:, 0]))
    us, vs = [], []
    for kk in (k1, k2):
        off = Pk - R_KM * C[kk]
        us.append(np.einsum("ij,ij->i", off, n3[kk]))
        vs.append(np.einsum("ij,ij->i", off, a3[kk]))
    gap = d2 - d1
    b = PATCH_BLEND * PATCH_KM
    return Frames((k1, k2), tuple(us), tuple(vs), 0.5 * (1 - smoothstep(0, b, gap)), smoothstep(0, b, gap), out)


# ---------------------------------------------------------------------------
# Zones (PW-148): a class's bench levels from its whole connected zone
# ---------------------------------------------------------------------------
ZONE_RELIEF = (0.36, 25.0)  # the zoom's typical relief over a zone: a x its median elevation + b (m; cf. zoom's detail)
ZONE_LOCAL_KM = 200.0  # elev_local: the zone's cells within ~this of each cell (a Gaussian's sigma)


def _wmedian(v, w):
    o = np.argsort(v)
    c = np.cumsum(w[o])
    return float(v[o][np.searchsorted(c, 0.5 * c[-1])])


def zone_stats(grid, L, k, sel, cx, cy, px, py, to_plane, interp, sp) -> dict:
    """Per pixel, the statistics of its landform zone: the connected region
    of class k's land cells on the whole coarse grid (not only the cells
    around the zoom) that the nearest class-k cell belongs to. So a level
    computed from them is the same in every zoom that sees the zone: two
    overlapping zooms put the same bench at the same height. Keys:
    elev_p50/p85/p95 (m), top_km (median strata_top_km), dip (median
    strata_dip, deg), relief (ZONE_RELIEF: the zoom's typical relief
    there, m), ox, oy (km: the zone's reference cell on the zoom plane, the
    origin of tilted beds), id (the zone's label); and elev_local, a smooth
    field: at each of the class's cells the median elevation of its zone's
    cells around it (weights falling off over ZONE_LOCAL_KM), interpolated
    onto the pixels as the class's layers are (a level that follows a long
    escarpment's height along the margin, gently, and is still the same in
    every zoom)."""
    form = np.asarray(L["landform"])
    elev = np.asarray(L["elevation"], float)
    lab, nz = grid.components((form == k) & (elev > 0))
    mine = np.flatnonzero(lab[sel] >= 0)
    n = len(px)
    out = {key: np.zeros(n) for key in ("elev_p50", "elev_p85", "elev_p95", "top_km", "dip", "relief", "ox", "oy",
                                        "elev_local")}
    out["id"] = np.full(n, -1)
    if not len(mine):
        return out
    zs = np.unique(lab[sel][mine])
    top = np.asarray(L.get("strata_top_km", np.zeros(grid.n)), float)
    dip = np.asarray(L.get("strata_dip", np.zeros(grid.n)), float)
    tab = {}
    for z in zs:
        c = np.flatnonzero(lab == z)
        e = elev[c]
        ref = c[np.argmin(np.arccos(np.clip(grid.centers[c] @ grid.centers[c].mean(0) / max(
            np.linalg.norm(grid.centers[c].mean(0)), 1e-12), -1, 1)))]  # (the cell nearest the zone's centroid)
        ox, oy = to_plane(grid.centers[[ref]])
        p50, p85, p95 = np.percentile(e, [50, 85, 95])
        tab[z] = (p50, p85, p95, np.median(top[c]), np.median(dip[c]), ZONE_RELIEF[0] * p50 + ZONE_RELIEF[1],
                  float(ox[0]), float(oy[0]))
    # each pixel: the zone of the nearest class cell around the zoom
    ccx, ccy, cz = cx[mine], cy[mine], lab[sel][mine]
    near = np.zeros(n, np.int64)
    best = np.full(n, np.inf)
    for j0 in range(0, len(ccx), 256):
        d = (px[:, None] - ccx[None, j0:j0 + 256]) ** 2 + (py[:, None] - ccy[None, j0:j0 + 256]) ** 2
        a = np.argmin(d, 1)
        dm = d[np.arange(n), a]
        better = dm < best
        near[better], best[better] = a[better] + j0, dm[better]
    zp = cz[near]
    out["id"] = zp
    loc = np.zeros(len(mine))
    for j, c in enumerate(sel[mine]):
        zc = np.flatnonzero(lab == lab[c])
        d = np.arccos(np.clip(grid.centers[zc] @ grid.centers[c], -1, 1)) * R_KM
        m = d < 3 * ZONE_LOCAL_KM
        loc[j] = _wmedian(elev[zc][m], np.exp(-0.5 * (d[m] / ZONE_LOCAL_KM) ** 2))
    ind = np.zeros((len(sel), 1))
    ind[mine, 0] = 1.0
    vals = np.zeros((len(sel), 1))
    vals[mine, 0] = loc
    f, _ = interp(vals, ind, 0.5 * sp)
    out["elev_local"] = np.where(np.isfinite(f[:, 0]), f[:, 0], loc[near])
    for i, key in enumerate(("elev_p50", "elev_p85", "elev_p95", "top_km", "dip", "relief", "ox", "oy")):
        vals = np.array([tab[z][i] for z in zs])
        out[key] = vals[np.searchsorted(zs, zp)]
    return out


def snap(level, period):
    """level rounded to a whole number of periods above the sea: endless
    benches then have the same phase whatever level a zone's top bed is
    put at."""
    P = np.maximum(period, 1.0)
    return P * np.round(level / P)


@njit(cache=True)
def lower_envelope(z, src, grad, nx, ny, res):
    """min(z, the lowest src pixel's height + grad x distance): valley walls
    rising at `grad` m/km from the src pixels (a chamfer distance sweep,
    forward and back, twice)."""
    n = nx * ny
    f = np.full(n, np.inf)
    for i in range(n):
        if src[i]:
            f[i] = z[i]
    d1, d2 = grad * res, grad * res * 1.41421356
    for _ in range(2):
        for r in range(ny):
            for c in range(nx):
                i = r * nx + c
                v = f[i]
                if c > 0:
                    v = min(v, f[i - 1] + d1)
                if r > 0:
                    v = min(v, f[i - nx] + d1)
                    if c > 0:
                        v = min(v, f[i - nx - 1] + d2)
                    if c < nx - 1:
                        v = min(v, f[i - nx + 1] + d2)
                f[i] = v
        for r in range(ny - 1, -1, -1):
            for c in range(nx - 1, -1, -1):
                i = r * nx + c
                v = f[i]
                if c < nx - 1:
                    v = min(v, f[i + 1] + d1)
                if r < ny - 1:
                    v = min(v, f[i + nx] + d1)
                    if c < nx - 1:
                        v = min(v, f[i + nx + 1] + d2)
                    if c > 0:
                        v = min(v, f[i + nx - 1] + d2)
                f[i] = v
    out = z.copy()
    for i in range(n):
        if f[i] < out[i]:
            out[i] = f[i]
    return out


GAP_GRAD, GAP_MIN_M = 400.0, 5.0  # m/km at 0.5 km pixels: the walls of a cut (see cut())


GORGE_Q, GORGE_MIN_M = 30.0, 30.0  # m^3/s (of runoff), m: a river this big falling this far over a landform's cliff...
GORGE_KM, GORGE_MAX_KM, GORGE_GRAD = 3.0, 12.0, 2.0  # ... retreats into a gorge GORGE_KM sqrt(Q / 1000) long


def scarp_gorges(z, rec, q, w, nx, ny, res, fixed):
    """Falls over a landform's cliffs retreat upstream, as designed falls'
    lips do (zoom.knickpoints), into a gorge: where a river of at least
    GORGE_Q m^3/s drops GORGE_MIN_M within 3 px (class weight w > 0.5),
    its bed is lowered from the foot upstream for GORGE_KM x sqrt(Q / 1000
    m^3/s) km (at most GORGE_MAX_KM, and not past the next cliff up),
    rising GORGE_GRAD m/km, the fall now at the gorge's head; walls as for
    cut(). Returns (z, gorges: [(pixel of the fall at its head, length km)])."""
    n = nx * ny
    up = np.full(n, -1)
    o = np.argsort(q, kind="stable")
    o = o[rec[o] >= 0]
    up[rec[o]] = o  # main donor (the biggest)
    r1 = np.where(rec >= 0, rec, np.arange(n))
    r2, r3 = r1[r1], r1[r1[r1]]
    drop = z - z[r3]
    step = z - z[r1]
    cand = np.flatnonzero((q >= GORGE_Q) & (w > 0.5) & (rec >= 0) & ~fixed & (drop >= GORGE_MIN_M))
    if not len(cand):
        return z, []
    z = z.copy()
    src = np.zeros(n, bool)
    done = np.zeros((ny, nx), bool)
    gorges = []

    def km(a, b):
        return res * (1.41421356 if (a % nx != b % nx and a // nx != b // nx) else 1.0)
    for i in cand[np.argsort(-step[cand])]:
        r0, c0 = divmod(int(i), nx)
        if done[r0, c0]:
            continue
        done[max(r0 - 4, 0):r0 + 5, max(c0 - 4, 0):c0 + 5] = True
        ch = [int(i), int(r1[i]), int(r2[i]), int(r3[i])]
        foot = next(c for c in ch[1:] if z[c] <= z[i] - 0.85 * drop[i])
        zf = float(z[foot])
        L = min(GORGE_KM * np.sqrt(q[i] / 1000.0), GORGE_MAX_KM)
        s, a, path = 0.0, int(i), []
        while a >= 0 and not fixed[a] and s <= L:
            path.append((a, s))
            b = int(up[a])
            if b < 0 or z[b] - z[a] > GORGE_MIN_M:  # (the next cliff up: the gorge stops below it)
                break
            s += km(a, b)
            a = b
        if len(path) < 2:
            continue
        for a, sa in path:
            z[a] = min(z[a], zf + GORGE_GRAD * (sa + res))
            src[a] = True
        src[foot] = True
        gorges.append((int(path[-1][0]), float(path[-1][1])))
    if gorges:
        g = GAP_GRAD * min(1.0, (0.5 / res) ** 0.5)
        z = np.where(fixed, z, lower_envelope(z, src, g, nx, ny, res))
    return z, gorges


def cut(z, rec, order, keep, nx, ny, res, fixed=None):
    """breach() (keep: pixels not lowered), then the cuts widened into
    gaps: walls rising from each pixel cut more than GAP_MIN_M at GAP_GRAD
    m/km (gentler on coarser pixels, so a cut is a few pixels wide: a water
    gap or a gorge, not a one-pixel slot), but not on `fixed` pixels (else
    keep); then breached again."""
    z0 = z.copy()
    z = breach(z, rec, order, keep)
    deep = (z0 - z) > GAP_MIN_M
    if deep.any():
        g = GAP_GRAD * min(1.0, (0.5 / res) ** 0.5)
        w = lower_envelope(z, deep, g, nx, ny, res)
        z = np.where(keep if fixed is None else fixed, z, w)
        z = breach(z, rec, order, keep)
    return z


class Synth:
    """A landform class's synthesiser (see the module docstring). Override
    the hooks a class needs; the defaults contribute nothing."""
    layers: tuple = ()  # world layers interpolated over the class's cells into Ctx.prm
    line = False  # a narrow class (landform.LINES): wider, lower weight threshold
    sigma = 0.5  # x cell spacing: the Gaussian kernel its layers are interpolated with
    axis: str | None = None  # structural patches (Ctx.frames): 'band' or 'gradient' strike (build_frames)
    gaps = False  # rivers (>= GAP_Q) keep their graded beds through the shape hook's structure (water gaps)
    zoned = False  # levels from the class's whole zone (Ctx.zone: zone_stats(), PW-148)

    def target(self, cx: Ctx, h: np.ndarray):
        return None

    def relief(self, cx: Ctx) -> tuple | None:
        return None

    def shape(self, cx: Ctx, h: np.ndarray):
        return None

    def strata(self, cx: Ctx, h: np.ndarray) -> Strata | None:
        return None

    def basins(self, cx: Ctx):
        """0..1 per pixel: where the class's closed depressions stay closed
        (not breached; filled flat, or lakes: lakes())."""
        return None

    def lakes(self, cx: Ctx):
        """0..1 per pixel: where the class's closed depressions hold water."""
        return None

    overlay_q = 3.0  # m^3/s: the overlay keeps off streams this big (and a little beside them)
    ponds = False  # the overlay's pits below the local base level (the water table) hold water

    def overlay(self, cx: Ctx, h: np.ndarray, fin: dict):
        """Metres added to the finished land after the final drainage
        (Landforms.finish): a veneer the rivers no longer reshape (dunes on
        the land, dolines, towers and poljes in karst). Kept off streams of
        overlay_q and more, and made mean-neutral over a few km (the cell
        means stay)."""
        return None

    def sinks(self, cx: Ctx):
        """0..1 per pixel: where streams sink underground (karst): streams
        under SINK_Q x this carry no water at the surface (dry valleys) and
        resurge where they leave it (springs)."""
        return None


class Escarpment(Synth):
    """Great escarpment: one band below the escarpment zone's level e*,
    over a moderately flattened plateau."""
    layers = ("elevation",)
    line = True
    zoned = True
    STEP = (0.8, 200.0, 1500.0)  # band height: fraction of e*, clipped to (m)

    def _level(self, cx):
        """e*: the median elevation of the escarpment zone's cells around
        (zone_stats' elev_local: smooth, following the margin's height over
        a few hundred km; a level varying along the margin faster than its
        rivers fall would meet them with the scarp from below)."""
        return np.maximum(cx.zone["elev_local"], 1.0)

    def _step(self, cx):
        return np.clip(self.STEP[0] * self._level(cx), self.STEP[1], self.STEP[2])

    def relief(self, cx):
        return 1.2, 1.0

    def strata(self, cx, h):
        return Strata(self._level(cx), self._step(cx), bands=1, cliff=0.75, power=2.0, top_k=1.0, face=0.015)


class Caprock(Synth):
    """Caprock plateau, mesas, buttes and stepped benches; dipping: cuestas."""
    layers = ("strata_top_km", "strata_dip")
    zoned = True
    CAP_M = (40.0, 400.0)  # the cap's cliff (m): strata_top_km, clipped
    CLIFF = 0.45  # the cap's share of each bench period (the rest: soft slope)
    RELIEF = 1.5  # x the zone's relief (zone_stats): at most this period, so benches show on low land too
    TOP = (85, 0.25)  # the top bed: the zone's 85th percentile of elevation + 0.25 x its relief

    def strata(self, cx, h):
        # (one period and anchor per zone: the bench levels lie whole periods
        # below the anchor, so a period varying across the land would scatter them)
        Z = cx.zone
        cap = np.clip(1000 * Z["top_km"], *self.CAP_M)
        P = np.minimum(cap / self.CLIFF, np.maximum(self.RELIEF * Z["relief"], 60.0))
        anchor = Z["elev_p85"] + self.TOP[1] * Z["relief"]
        t = 1000 * np.tan(np.radians(Z["dip"]))  # m/km
        tilt = (t * cx.downhill[0], t * cx.downhill[1]) if np.any(t > 0.3) else None
        return Strata(anchor, P, cliff=self.CLIFF, power=2.0, top_k=0.5, tilt=tilt, origin=(Z["ox"], Z["oy"]))


class LavaPlateau(Synth):
    """Traps: stacked flows under a flat top."""
    layers = ("strata_top_km",)
    zoned = True
    FLOW_M = 110.0  # a flow package's step (m), at least
    RELIEF = 0.65  # x the zone's relief (zone_stats): at least this step
    TOP = 0.6  # the flat top: the zone's 95th percentile of elevation + this x its relief

    def relief(self, cx):
        return 1.5, 1.25

    def strata(self, cx, h):
        # (flows are ~10-50 m; at zoom pixels the steps seen are packages of
        # them, a good part of the valleys' depth; where they come out
        # narrower than a pixel or two they fade out: Landforms._bench)
        Z = cx.zone
        P = np.maximum(self.FLOW_M, self.RELIEF * Z["relief"])
        anchor = Z["elev_p95"] + self.TOP * Z["relief"]
        return Strata(anchor, P, cliff=0.55, power=1.5, top_k=0.3)


class FoldBelt(Synth):
    """Fold-and-thrust belt: parallel folds along the strike (across the
    shortening), fold_wavelength apart, their amplitude from the beds' dip
    (lambda / 2 pi x tan dip), varying along each fold (culminations and
    plunging noses, en echelon from fold to fold). Young belts (landform_age
    < ~AGE_YOUNG) stand as the folds themselves: anticlines are whaleback
    ridges, synclines valleys (Zagros); older ones are worn down to the hard
    beds: the folded pile is read along a stratigraphic height s = h - F (F:
    the beds' offset), hard and soft beds alternating, each hard bed a
    hogback (a steep face towards the fold's core, a gentle dip slope away)
    where it crops out, closing round the plunging noses (Valley and Ridge).
    The ridges' relief from the land's height and the hardness contrast of
    the exposed stratum and the one below. In the target too (x TARGET), so
    the drainage runs along the strike valleys (trellis); the rivers that
    cross the ridges cut water gaps (cut())."""
    layers = ("fold_wavelength", "strata_dip", "landform_age", "elevation", "hard_top", "hard_next")
    axis = "gradient"
    gaps = True
    AGE_YOUNG = 15.0  # Myr: folds younger than this still stand as the topography
    TARGET = 0.6
    HARD = 0.4  # the hard beds' share of the folded pile

    def _z(self, cx, h):
        F, P = cx.frames, cx.frames.patch
        el = np.maximum(cx.prm["elevation"], 0.0)
        young = np.exp(-np.maximum(cx.prm["landform_age"], 0.0) / self.AGE_YOUNG)
        contrast = 0.5 + 0.5 * np.abs(cx.prm["hard_top"] - cx.prm["hard_next"])
        Ry = np.minimum(0.45 * el + 100.0, 1500.0)  # young: whaleback anticlines
        Ro = np.clip(0.35 * el + 120.0, 120.0, 700.0) * contrast  # old: hogbacks
        hf, dd = self.HARD, 0.12
        sea = cx.noise(60.0, 2, 401)  # (the axes wander a little)
        hs = cx.local_top(h, 3.0, 0.0)  # (the beds crop out along the land's smoothed height)

        def one(j):
            p = F.k[j]
            lam = np.maximum(P["fold_wavelength"][p], 3.0)
            dip = np.radians(np.clip(P["strata_dip"][p], 5.0, 70.0))
            A = 1000.0 * lam / (2 * np.pi) * np.tan(dip)  # m: the beds' fold amplitude
            u = F.u[j] + 0.15 * lam * sea
            Lp = lam * (5.0 + 4.0 * P["r1"][p])
            pts = np.ascontiguousarray(np.column_stack([u / lam, F.v[j] / Lp, np.full_like(u, 3.7) * P["r2"][p]]))
            E = np.clip(0.75 + 0.3 * ZK.fbm(pts, 1.0, 1, 0.5, cx.seed + 411) / 0.17, 0.05, 1.0)
            phi = 2 * np.pi * (u / lam + P["r0"][p])
            cph = np.cos(phi)
            zy = Ry * E * cph
            # old: the hard beds' outcrops, ns per limb (as many as the pixels resolve)
            ns = np.clip(np.floor(lam / 2 / (8 * cx.res)), 1, 2)
            Ps = 2 * A / ns
            s = hs - A * E * cph
            r = np.mod(s / Ps + P["r3"][p], 1.0)
            gs = A * E * 2 * np.pi / lam * np.abs(np.sin(phi)) + 20.0  # m/km: |grad s|
            e_raw = 1.5 * cx.res * gs / Ps
            e = np.clip(e_raw, 0.04, hf)
            prof = np.where(r < hf, smoothstep(0, e, r), np.exp(-(r - hf) / dd))
            mean = hf - e / 2 + dd * (1 - np.exp(-(1 - hf) / dd))
            zo = Ro * (prof - mean) * (1 - smoothstep(0.25, 0.45, e_raw))
            vis = smoothstep(3.0, 6.0, lam / cx.res)  # folds a few pixels across can't be drawn
            return vis * (young * zy + (1 - young) * zo)
        return F.blend(one) * (0.6 + 0.4 * F.edge)

    def relief(self, cx):
        return 0.7, 0.6

    def target(self, cx, h):
        return self.TARGET * self._z(cx, h)

    def shape(self, cx, h):
        # (on the finished land only the ridges are raised: the synclines and
        # strike valleys stay at the graded land, where the rivers run;
        # lowering them would leave closed troughs)
        z = self._z(cx, h)
        return 0.5 * (z + np.sqrt(z * z + 30.0 ** 2)) - 15.0


class Rift(Synth):
    """Fault-block rift: tilted blocks W ~ 10-30 km wide (narrower the more
    stretched), bounded by normal faults parallel to the rift's axis (the
    long axis of its band of cells; Frames 'band'): a steep fault scarp on
    one side, a gentle back-tilt down to the next fault on the other, the
    half-graben at its foot filled flat with sediment (the closed basins
    stay closed: basins(); lakes in a wet climate: lakes()). The throw from
    the stretching (rift_strain, ln beta) and the time since (landform_age:
    older scarps worn lower, basins fuller); the blocks' facing flips from
    patch to patch (accommodation zones), throws vary from block to block
    and die out at the patches' ends. In the target too (x TARGET), so the
    rivers run along the basins."""
    layers = ("rift_strain", "landform_age", "elevation")
    line = True
    axis = "band"
    TARGET = 0.5

    def _z(self, cx, h):
        F, P = cx.frames, cx.frames.patch
        lnb = np.maximum(cx.prm["rift_strain"], 0.0)
        age = np.maximum(cx.prm["landform_age"], 0.0)
        el = np.maximum(cx.prm["elevation"], 0.0)
        H = np.clip(2500.0 * (1 - np.exp(-lnb / 0.35)), 300.0, 2200.0) * (0.5 + 0.5 * np.exp(-age / 30.0))
        H = np.minimum(H, 400.0 + 1.5 * el)
        fill = 0.15 + 0.3 * (1 - np.exp(-age / 8.0))
        wig = cx.noise(40.0, 2, 421)

        def one(j):
            p = F.k[j]
            pid = P["id"][p] % 2147483647
            W = (12.0 + 16.0 * P["r1"][p]) * (1.15 - 0.3 * smoothstep(0.2, 1.2, P["rift_strain"][p]))
            W = np.clip(W, max(8.0, 6 * cx.res), 40.0)
            sg = np.where(P["r2"][p] < 0.5, -1.0, 1.0)
            x = sg * (F.u[j] + 0.07 * W * wig) / W + P["r3"][p]
            jb = np.floor(x)
            t = x - jb
            jb = jb.astype(np.int64)

            def block(b):
                pts = np.ascontiguousarray(np.column_stack([b * 3.1 + 0.37, F.v[j] / 45.0, np.full_like(x, 1.3)]))
                tip = np.clip(0.75 + 0.2 * ZK.fbm(pts, 1.0, 2, 0.5, cx.seed + 431) / 0.17, 0.2, 1.2)
                hb = H * (0.6 + 0.8 * hashf(b, pid, 1)) * tip
                tf = np.clip(fill + 0.2 * (hashf(b, pid, 2) - 0.5), 0.08, 0.6)
                return hb, tf
            hj, tf = block(jb)
            hn, tfn = block(jb + 1)
            e = np.clip(1.5 * cx.res / W, 0.03, 0.25)  # the fault scarp, at least ~1.5 px wide
            g = hj * np.maximum(np.minimum(t, 1 - e), tf)
            k = smoothstep(1 - e, 1.0, t)
            g = (1 - k) * g + k * hn * tfn
            # the half-graben's floor: sediment, flat (the land's texture filled in)
            fill_w = (1 - k) * smoothstep(tf + 0.1, tf, t)
            return g - hj * (1 + tf * tf) / 2, fill_w
        a, b = one(0), one(1)
        env = 0.4 + 0.6 * F.edge
        g = ((1 - F.alpha) * a[0] + F.alpha * b[0]) * env
        fw = ((1 - F.alpha) * a[1] + F.alpha * b[1]) * env
        cx.cache["floor"] = fw
        return g - fw * (h - cx.local_top(h, 4.0, 0.0))

    def relief(self, cx):
        return 0.7, 0.45

    def target(self, cx, h):
        return self.TARGET * self._z(cx, h)

    def shape(self, cx, h):
        return self._z(cx, h)

    def basins(self, cx):
        return np.ones(len(cx.land))

    def lakes(self, cx):
        # (the half-grabens' floors; whether a basin there fills is its water
        # balance's call: zoom_landforms.basin_lakes)
        if "floor" not in cx.cache:
            self._z(cx, cx.base)
        return smoothstep(0.15, 0.4, cx.cache["floor"])


class Shield(Synth):
    """Old shield: a low plain (relief flattened) with granite domes and
    inselbergs (bornhardts: steep-sided, round-topped rock domes 1-4 km
    across rising 100-400 m; more on granite than on gneiss), placed on a
    planet-fixed lattice, off the streams (in the target too, so the
    drainage goes round them). Where the record says the shield was under
    ice lately (glaciated_myr, decaying over GLACIATED_MYR) it is scoured:
    the domes ground down to whalebacks, the plain knobbly with rock basins
    that hold lakes (lake-dotted, deranged drainage: Canadian Shield)."""
    layers = ("glaciated_myr", "elevation", "granite")
    GLACIATED_MYR = 30.0
    DOME_KM = 14.0  # lattice spacing of the dome sites
    TARGET = 0.8

    def _glac(self, cx):
        return np.exp(-np.maximum(cx.prm["glaciated_myr"], 0.0) / self.GLACIATED_MYR)

    def _domes(self, cx):
        if "domes" not in cx.cache:
            z = domes(cx.Pk, self.DOME_KM, np.int64(cx.seed + 441), 0.4, np.array([0.8, 4.5]),
                      np.array([0.1, 0.3]), 2.2, 1.5 * cx.res)
            # (in fields: more on granite, some country nearly bare)
            field_ = smoothstep(-0.4, 0.5, cx.noise(60.0, 2, 442))
            k = (0.65 + 0.35 * cx.prm["granite"]) * (1 - 0.6 * self._glac(cx)) * field_
            cx.cache["domes"] = np.minimum(z, 500.0) * k
        return cx.cache["domes"]

    def relief(self, cx):
        return 1.0, 0.5

    def target(self, cx, h):
        return self.TARGET * self._domes(cx)

    def shape(self, cx, h):
        z = self._domes(cx)
        if cx.chan is not None:  # (off the streams: no dome across a river)
            near = _dilate(cx.chan.reshape(cx.ny, cx.nx), 1).ravel()
            z = np.where(near, 0.0, z)
        g = self._glac(cx)
        if np.any(g > 0.05):  # scoured: rock basins and knobs
            n = cx.noise(6.0, 3, 451)
            knob = cx.noise(2.5, 2, 452)
            z = z - g * (45.0 * smoothstep(0.45, 0.85, n) - 3.0 * knob)
        return z

    def basins(self, cx):
        return smoothstep(0.2, 0.5, self._glac(cx))

    def lakes(self, cx):
        return smoothstep(0.2, 0.5, self._glac(cx))


class Karst(Synth):
    """Karst on thick carbonate: the rain sinks into it and drains
    underground, so the surface has few rivers. Small streams sink
    (sinks(): Landforms.finish dries their valleys, springs where the water
    resurges at the karst's edge or into a big river; bigger, allogenic
    rivers cross it in gorges). The landscape is the overlay of solution
    forms on a planet-fixed lattice, by climate (Ctx.prm temperature and
    precipitation: tropical = TROPIC):
      temperate (Dinaric): a plateau (relief: flat tops, steep valleys)
        pocked with dolines (0.25-1.1 km across; down to the pixels the
        zoom resolves) and poljes, big flat-floored closed basins (5-25 km
        long) with steep sides;
      wet tropics (Guilin): a corrosion plain (relief flattened) with
        towers (0.6-2 km across, 60-250 m, steep-sided) and fewer dolines.
    Pits below the local base level (the first flowing river or the sea
    down the drainage: the water table) hold ponds and lakes (cenotes,
    flooded poljes). Limestone dissolves readily; dolomite (purity 0.5)
    makes half the forms, and sinks only the smaller streams. Towers and
    dolines are no deeper than the carbonate is thick."""
    layers = ("temperature", "precipitation", "strata_top_km", "purity")
    overlay_q = 30.0  # (the streams that still flow: SINK_Q)
    ponds = True
    TROPIC = ((16.0, 22.0), (900.0, 1400.0))  # C, mm/yr: tower karst above these
    DOLINE = (3.0, 0.35, (0.4, 1.3))  # lattice km, probability, radius km (the big ones: uvalas)
    POLJE = (40.0, 0.45, (2.5, 9.0))
    TOWER = (3.0, 0.45, (0.5, 1.2))
    BELOW_M = 5.0  # m: dolines and polje floors reach at most this far below the water table (ponds, flooded poljes)

    def _trop(self, cx):
        return (smoothstep(*self.TROPIC[0], cx.prm["temperature"])
                * smoothstep(*self.TROPIC[1], cx.prm["precipitation"]))

    def target(self, cx, h):
        # (the tropical corrosion plain: the sub-cell hills dissolved down to it)
        return -0.7 * self._trop(cx) * (h - cx.local_top(h, 0.2 * cx.sp, -0.5))

    def relief(self, cx):
        on = (cx.w > 0.5) & cx.land
        tr = float(np.mean(self._trop(cx)[on])) if on.any() else 0.0
        return 1.5 + 1.0 * tr, 0.8 - 0.55 * tr

    def sinks(self, cx):
        return cx.prm["purity"]

    def overlay(self, cx, h, fin):
        tr = self._trop(cx)
        pur = cx.prm["purity"]
        thick = 1000 * np.maximum(cx.prm["strata_top_km"], 0.0)
        res = cx.res
        out = np.zeros(len(h))
        st = cx.cache.setdefault("overlay_stats", {})
        # dolines: bowls about a quarter as deep as they are wide
        cell, prob, rr = self.DOLINE
        q, fid, R, _ = blobs(cx.Pk, cell, np.int64(cx.seed + 461), prob, np.array(rr), 1.6, 1.0 * res)
        on = q < 1
        dep = 1000 * R * (0.12 + 0.2 * hashf(np.maximum(fid, 0) % 2147483647, 1))
        dol = np.where(on, dep * (1 - np.minimum(q, 1.0) ** 2) ** 0.8, 0.0)
        # (no deeper than half the carbonate, and mostly above the water
        # table: the rock dissolves where the water drains down to it; a
        # quarter of them reach it (collapse dolines, cenotes: ponds))
        reach = self.BELOW_M * (hashf(np.maximum(fid, 0) % 2147483647, 6) < 0.25)
        above = 0.8 * np.maximum(h - fin["base"], 0.0) + reach
        dol = np.minimum(np.minimum(dol, 0.5 * thick), above) * pur * (1 - 0.6 * tr)
        out -= dol
        st["dolines"] = int(len(np.unique(fid[on & (dol > 5.0) & (cx.w > 0.5)])))
        # poljes: flat floors (alluvium) below the land around them, steep sides
        cell, prob, rr = self.POLJE
        q, fid, R, _ = blobs(cx.Pk, cell, np.int64(cx.seed + 463), prob, np.array(rr), 3.0, 3.0 * res)
        inside = smoothstep(1.0, 0.75, np.minimum(q, 2.0))
        pol = np.zeros(len(h))
        npol = 0
        for f in np.unique(fid[(q < 0.9) & (cx.w > 0.5)]):
            m = (fid == f) & (q < 1.0)
            core = (fid == f) & (q < 0.9)
            depth = (20.0 + 40.0 * hashf(np.array([f % 2147483647]), 2)[0])
            floor = max(np.percentile(h[core], 20) - depth, np.percentile(fin["base"][core], 50) - self.BELOW_M)
            pol[m] = np.minimum(floor - h[m], 0.0) * inside[m]
            npol += 1
        out += pol * pur * (1 - tr)
        st["poljes"] = npol
        # towers (fenglin): steep sides, rounded tops, on the plain
        cell, prob, rr = self.TOWER
        q, fid, R, _ = blobs(cx.Pk, cell, np.int64(cx.seed + 467), prob, np.array(rr), 1.4, 1.2 * res)
        on = q < 1
        Ht = 80.0 + 170.0 * hashf(np.maximum(fid, 0) % 2147483647, 3)
        tow = np.where(on, Ht * (1 - np.minimum(q, 1.0) ** 8) ** 0.4, 0.0)
        tow = np.minimum(tow, 0.8 * thick) * tr * np.sqrt(pur)
        out += tow
        st["towers"] = int(len(np.unique(fid[on & (tow > 30.0) & (cx.w > 0.5)])))
        return out


class Dunes(Synth):
    """Dune field (erg): dunes on top of the land, their type from the wind
    regime (sand_drift: the seasons' drift, Fryberger's RDP/DP) and the
    sand supply (the sand's thickness, strata_top_km):
      one wind all year (RDP/DP > ~0.8): transverse ridges across it,
        gentle upwind (stoss) slopes and steep lee faces, broken into
        crescentic barchans with horns pointing downwind where sand is
        short (interdune flats between);
      two winds at an angle (~0.25-0.75): linear (seif) dunes along the
        resultant drift, long and parallel;
      winds from many sides (< ~0.3): star dunes, tall peaks with arms.
    Spacing 1-3 km (more sand: bigger and further apart), heights a few %
    of the spacing (tens of m to ~150 m; star dunes higher). Planet-fixed
    patches (build_frames, 'wind': each patch's axis along the drift of the
    cells around it, its sign downwind). More arid (P / PET) and warmer: more active
    (frozen, snowy ground holds the sand: cold ergs half as high). On the
    finished land (an overlay: it doesn't flatten the hills under it; not
    on steep slopes nor across rivers). Crests at least MIN_PX pixels apart
    (the zoom draws the big dunes; spacing exaggerated up to 2x on coarse
    zooms, fading out beyond); the sand sheet buries the small hills (the
    target's sub-cell texture damped where there is sand)."""
    layers = ("strata_top_km", "aridity", "temperature", "drift_e", "drift_n", "drift_ratio")
    axis = "wind"
    LAMBDA_KM = (1.0, 3.0)  # crest spacing, little to much sand
    HEIGHT = (0.045, 0.05, 0.08)  # x spacing: transverse / barchan, linear, star
    STAR = (5.0, 0.75, (1.2, 2.2))  # star dunes: lattice km, probability, radius km
    overlay_q = 30.0  # (the rivers that cross the erg: SINK_Q; smaller wadis end in the sand)
    SAND_KM = (0.01, 0.35)  # the sand's thickness: little .. plenty (supply 0 .. 1)
    MIN_PX = 5.0  # crests at least this many pixels apart (finer ones exaggerated up to 2x, fading out beyond)

    def _supply(self, cx):
        return smoothstep(*self.SAND_KM, cx.prm["strata_top_km"])

    def sinks(self, cx):
        # (an ephemeral stream loses its water into the sand: it ends in the erg)
        return np.ones(len(cx.land))

    def target(self, cx, h):
        # (the sand sheet buries the small hills: the sub-cell texture damped
        # where there is sand; mountains and the coarse land stay)
        return -0.6 * self._supply(cx) * (h - cx.local_top(h, 0.2 * cx.sp, 0.0))

    def relief(self, cx):
        return 1.0, 0.6

    def overlay(self, cx, h, fin):
        F, P = cx.frames, cx.frames.patch
        res = cx.res
        supply = self._supply(cx)
        act = (smoothstep(0.2, 0.04, cx.prm["aridity"])  # (P / PET: the class needs < LF.DUNES_AI)
               * (0.5 + 0.5 * smoothstep(-8.0, 2.0, cx.prm["temperature"])))
        lam = self.LAMBDA_KM[0] + (self.LAMBDA_KM[1] - self.LAMBDA_KM[0]) * supply
        lamd = np.maximum(lam, self.MIN_PX * res)  # (drawn at least MIN_PX pixels apart: the big dunes, draas)
        vis = smoothstep(3.5, 2.0, lamd / lam)
        r = cx.prm["drift_ratio"]
        wT = smoothstep(0.7, 0.85, r)
        wS = smoothstep(0.35, 0.15, r)
        wL = np.clip(1.0 - wT - wS, 0.0, 1.0)
        nw = cx.noise(8.0, 2, 471)
        nb = cx.noise(5.0, 2, 472)
        nl = cx.noise(25.0, 2, 473)
        gap = 0.65 * (1 - supply)  # (little sand: crescents apart)
        Ls = lamd * (1.5 + 4.0 * supply)  # crest segment length

        def one(j):
            p = F.k[j]
            ax = np.radians(P["axis_deg"][p])
            sg = np.where(np.cos(ax) * P["drift_e"][p] + np.sin(ax) * P["drift_n"][p] < 0, -1.0, 1.0)
            v, u = sg * F.v[j], sg * F.u[j]  # (v: downwind)
            pid = P["id"][p] % 2147483647
            # transverse ridges / barchans: across the wind
            su = u / Ls + 0.12 * nb + P["r1"][p]
            si = np.floor(su)
            wseg = su - si - 0.5
            vb = v + 0.25 * lamd * nw + 0.4 * lamd * hashf(si.astype(np.int64), pid, 3) * (1 - supply)
            vb = vb - 0.7 * lamd * (2 * wseg) ** 2 * (0.3 + 0.7 * (1 - supply))  # (horns downwind)
            t = np.mod(vb / lamd + P["r0"][p], 1.0)
            prof = np.where(t < 0.58, (t / 0.58) ** 1.4, 1.0 - smoothstep(0.58, 0.66, t))
            seg = np.clip(1.0 - (2 * np.abs(wseg) / np.maximum(1 - gap, 0.2)) ** 2, 0.0, 1.0) ** 0.5
            zt = prof * seg
            # linear: along the resultant, symmetric, long
            tl = np.mod(u / lamd + P["r2"][p] + 0.15 * nw, 1.0)
            zl = smoothstep(0.4, 1.0, 1.0 - np.abs(2 * tl - 1)) * np.clip(0.75 + 0.45 * nl, 0.0, 1.0)
            return zt, zl
        a, b = one(0), one(1)
        # (between two patches the dunes switch over a narrow, wandering seam,
        # crests ending against it, rather than cross-hatching over the blend)
        al = smoothstep(0.42, 0.58, F.alpha + 0.12 * cx.noise(10.0, 2, 474))
        zt = (1 - al) * a[0] + al * b[0]
        zl = (1 - al) * a[1] + al * b[1]
        # star dunes: peaks with 3-5 arms
        cell, prob, rr = self.STAR
        q, fid, R, ang = blobs(cx.Pk, cell, np.int64(cx.seed + 475), prob, np.array(rr), 1.2, 0.6 * res)
        k = 3.0 + np.floor(3.0 * hashf(np.maximum(fid, 0) % 2147483647, 4))
        arm = 1.0 + 0.7 * np.cos(k * ang + 6.28 * hashf(np.maximum(fid, 0) % 2147483647, 5))
        zs = np.clip(1.0 - q / arm, 0.0, 1.0) ** 1.6 * np.isfinite(q)
        H = 1000.0 * lam * act * vis
        z = H * (wT * self.HEIGHT[0] * zt + wL * self.HEIGHT[1] * zl + wS * self.HEIGHT[2] * zs * (R / 1.7))
        # (not up steep slopes: the dunes ride on gentle ground, hills stick out)
        gy, gx = np.gradient(h.reshape(cx.ny, cx.nx), res)
        z = z * smoothstep(120.0, 40.0, np.hypot(gx, gy).ravel())
        st = cx.cache.setdefault("overlay_stats", {})
        on = (cx.w > 0.5) & cx.land
        if on.any():
            st["types"] = {"transverse_barchan": round(float(np.mean(wT[on])), 2),
                           "linear": round(float(np.mean(wL[on])), 2), "star": round(float(np.mean(wS[on])), 2)}
            st["spacing_km"] = round(float(np.mean(lam[on])), 2)
            st["max_height_m"] = round(float(np.max(z[on])), 0)
        return z


class CoastalPlain(Synth):
    """Coastal plain: a low plain sloping gently to the sea, smoothed (its
    hills flattened in the target, shallow valleys), with a few metres of
    micro-relief (old levees, scroll bars, beach ridges) that make its
    rivers wander; where the young beds dip seaward (more steeply than the
    land: a seaward-thickening wedge) and a hard bed lies over a soft one,
    low cuestas: ridges facing inland with long gentle backs to the sea
    (Atlantic and Gulf coastal plains). The beds' height follows the
    distance from the coarse coast (a planet-fixed field). Barrier islands,
    lagoons and marshes on its wave-dominated coasts are drawn with the
    coastline (zoom.build: coastal_barriers)."""
    layers = ("strata_dip", "hard_top", "hard_next", "coast_km")
    zoned = True
    CUESTA_M = 60.0  # the beds' period (m): ridges ~ 0.4 x this high
    DIP = (2.5, 8.0)  # m/km: the beds' seaward dip

    def target(self, cx, h):
        smooth = cx.local_top(h, 0.25 * cx.sp, 0.0)
        return -0.6 * (h - smooth) + 4.0 * cx.noise(8.0, 2, 481)

    def relief(self, cx):
        return 0.8, 0.5

    def strata(self, cx, h):
        t = np.clip(4000.0 * np.tan(np.radians(cx.prm["strata_dip"])), *self.DIP)
        contrast = np.clip(2.0 * (cx.prm["hard_top"] - cx.prm["hard_next"]), 0.0, 1.0)
        return Strata(cx.zone["elev_p95"], self.CUESTA_M, cliff=0.4, power=1.5, top_k=1.0, face=0.12,
                      shift=-t * cx.prm["coast_km"], amp=contrast)


def _dilate(m, r):
    out = m.copy()
    for dr in range(-r, r + 1):
        for dc in range(-r, r + 1):
            out |= np.roll(np.roll(m, dr, 0), dc, 1)
    return out


RELIEF_KM = 20.0  # relief hooks: the scale of d's local mean
SINK_Q = 30.0  # m^3/s: in karst (Synth.sinks = 1) streams under this sink underground
POND_M = 3.0  # m: an overlay's pit this far below the water table holds a pond
GAP_Q, GAP_KM = 30.0, 2.5  # m^3/s, km: rivers this big cut water gaps this wide (Synth.gaps)
FACE_PX, FACE_MAX = 1.2, 0.25  # a bench map's cliffs span at least FACE_PX pixels, at most FACE_MAX of a band
FACE_SMOOTH = 1  # px: ... along the stratigraphic height smoothed over this box radius
BAND_MIN_PX = (1.0, 2.0)  # ... and its benches fade out where a band is narrower than this (px)


@njit(cache=True)
def breach(z, rec, order, keep):
    """Lower each pixel to just below the lowest of its donors where it
    stands above one (walking down from the headwaters; order: outlets
    first): a sill the remap left across a flow path is cut through, as a
    river would, not filled into a lake. Pixels with keep=True stay."""
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        d = rec[i]
        if d >= 0 and not keep[d] and z[d] > z[i] - 1e-3:
            z[d] = z[i] - 1e-3
    return z


@njit(cache=True)
def relief_along(h, hc, rec, order, channel, wt, D, A, dref):
    """The relief hooks' reshaping, integrated down the drainage (order:
    outlets first): with d = h - hc (height above the drainage) and R(d) =
    (1 - wt) d + wt D (1 - exp(-A d / dref)), each pixel sits R_i(d_i) -
    R_i(d_r) above its receiver r (its own parameters for both, so it
    always stands above it); channels keep their height."""
    z = h.copy()
    for t in range(order.shape[0]):
        i = order[t]
        r = rec[i]
        if r < 0 or channel[i]:
            continue
        di = max(h[i] - hc[i], 0.0)
        dr = max(h[r] - hc[i], 0.0) if not channel[r] else 0.0
        if di < dr:
            di = dr
        Ri = (1 - wt[i]) * di + wt[i] * D[i] * (1 - np.exp(-A[i] * di / dref[i]))
        Rr = (1 - wt[i]) * dr + wt[i] * D[i] * (1 - np.exp(-A[i] * dr / dref[i]))
        z[i] = z[r] + max(Ri - Rr, 1e-3)
    return z


@njit(cache=True)
def drain_level(h, rec, order, channel):
    """Per pixel, the height of the first channel pixel down its receivers
    (itself on a channel; its own height at an outlet). order: outlets first."""
    hc = h.copy()
    for t in range(order.shape[0]):
        i = order[t]
        d = rec[i]
        if d >= 0 and not channel[i]:
            hc[i] = hc[d]
    return hc


@njit(cache=True)
def _next_basin(rec, order, lab):
    """Per pixel, the first closed depression (label) down its receivers
    other than its own (-1: none before an outlet). order: outlets first."""
    nxt = np.full(rec.shape[0], -1, np.int64)
    for t in range(order.shape[0]):
        i = order[t]
        r = rec[i]
        if r < 0:
            continue
        if lab[r] >= 0 and lab[r] != lab[i]:
            nxt[i] = lab[r]
        else:
            nxt[i] = nxt[r]
    return nxt


PLAYA_SHARE = 0.25  # a dry closed basin's flat floor: at least this share of the depression


def basin_lakes(h, filled, rec, order, dep_ok, can, src, loss, res, nx, ny, min_m, min_km2, full_km2):
    """Which of a landform's closed depressions hold water, by their water
    balance (PW-167). h: the surface; filled, rec, order: its priority flood
    (outlets first); dep_ok: where depressions count (active land, no ice);
    can: 0..1, where the classes let them hold water (Synth.lakes); src:
    water each pixel yields (runoff + inflow, km^2 m/yr); loss: a lake's net
    evaporation (open water minus the land's, m/yr). Each depression
    (filled - h > 0.2 m) gets its own catchment's water plus what the
    depressions above it spill (upstream first, so small ones overflow into
    chains). A depression at least min_m deep and min_km2 big where `can`
    holds:
      full    inflow >= loss x its area at the spill: a lake to the brim
              that passes the rest on (an open lake), if at least
              full_km2 big (a smaller full one silts up: filled flat);
      closed  else, a lake whose area A = inflow / loss (the level where
              the depression is that big; a salt lake), if A >= min_km2;
      playa   else a dry flat floor (PLAYA_SHARE of it) where its streams end.
    Every other depression is filled flat (its water passes on).
    Returns (surface: closed lakes at their level, playas at their floor,
    full lakes and the rest filled; lake: lake pixels (bed = surface -
    depth); depth; sink: closed lakes and playas, where rivers end; counts)."""
    n = nx * ny
    dep = np.where(dep_ok, filled - h, 0.0)
    lab, sizes = ZK.label_components(dep > 0.2, nx, ny)
    surf = np.where(dep_ok, np.maximum(h, filled), h)
    lake, depth, sink = np.zeros(n, bool), np.zeros(n), np.zeros(n, bool)
    counts = {"full": 0, "closed": 0, "playa": 0, "silted": 0}
    nb = len(sizes)
    if not nb:
        return surf, lake, depth, sink, counts
    on = lab >= 0
    L = lab[on]
    Q = ZK.accumulate(rec, order, src)
    qx = np.zeros(nb)
    np.maximum.at(qx, L, Q[on])
    nxt_px = _next_basin(rec, order, lab)
    # each depression's exit (its pixel with the most water) and the depression below it
    ex = np.full(nb, -1)
    idx = np.flatnonzero(on)
    o = np.lexsort((Q[idx], L))
    last = np.r_[np.flatnonzero(np.diff(L[o])), len(o) - 1]
    ex[L[o][last]] = idx[o][last]
    below = np.where(ex >= 0, nxt_px[np.maximum(ex, 0)], -1)
    direct = qx.copy()
    np.add.at(direct, below[below >= 0], -qx[below >= 0])
    area = sizes * res * res
    dmax = np.zeros(nb)
    np.maximum.at(dmax, L, dep[on])
    cmean = np.bincount(L, can[on], nb) / np.maximum(sizes, 1)
    lmean = np.bincount(L, loss[on], nb) / np.maximum(sizes, 1)
    cand = (dmax >= min_m) & (area >= min_km2) & (cmean > 0.5)
    spill = np.zeros(nb)
    for b in np.argsort(qx, kind="stable"):  # upstream first
        inflow = max(direct[b], 0.0) + spill[b]
        out = inflow
        if cand[b]:
            cap = lmean[b] * area[b]
            px_b = np.flatnonzero(lab == b)
            if inflow >= cap:
                if area[b] >= full_km2:
                    lake[px_b], depth[px_b] = True, dep[px_b]
                    counts["full"] += 1
                else:
                    counts["silted"] += 1
                out = inflow - cap
            else:
                out = 0.0
                hs = np.sort(h[px_b])
                a = inflow / max(lmean[b], 1e-9)
                if a >= min_km2:
                    k = min(int(np.ceil(a / (res * res))), len(hs))
                    lvl = hs[k - 1] + 1e-3
                    w = px_b[h[px_b] < lvl]
                    surf[px_b] = np.maximum(h[px_b], lvl)
                    lake[w], depth[w], sink[w] = True, lvl - h[w], True
                    counts["closed"] += 1
                else:
                    k = max(int(np.ceil(PLAYA_SHARE * len(hs))), 1)
                    lvl = hs[k - 1] + 1e-3
                    surf[px_b] = np.maximum(h[px_b], lvl)
                    sink[px_b[h[px_b] < lvl]] = True
                    counts["playa"] += 1
        if below[b] >= 0:
            spill[below[b]] += out
    return surf, lake, depth, sink, counts


# the classes in landform.classify's order (the first that holds wins there; here: keeps its weight)
PRIORITY = [LF.ARC_CLASS, LF.HOTSPOT_CLASS, LF.RIFT, LF.ESCARPMENT, LF.FOLD_BELT, LF.LAVA_PLATEAU, LF.DUNES, LF.KARST,
            LF.CAPROCK, LF.COASTAL_PLAIN, LF.SHIELD, LF.HILLS, LF.SEA]
SYNTH = {LF.ESCARPMENT: Escarpment(), LF.CAPROCK: Caprock(), LF.LAVA_PLATEAU: LavaPlateau(),
         LF.FOLD_BELT: FoldBelt(), LF.RIFT: Rift(), LF.SHIELD: Shield(),
         LF.KARST: Karst(), LF.DUNES: Dunes(), LF.COASTAL_PLAIN: CoastalPlain()}


# per-cell columns the synthesisers read besides the world's layers, and
# defaults for layers a world lacks (sliced before they existed)
def sand_drift(L, sel):
    """The sand's drift per cell (Fryberger): each season's wind u carries
    sand ~ |u|^3 along u (the world's July and January winds; the annual
    wind where it lacks them). Returns the resultant drift (east, north,
    mean of the seasons' |u|^2 u) and its directional steadiness RDP / DP
    (1: one wind all year; ~0.5: two winds at an angle; ~0: winds from
    opposite or many sides)."""
    pairs = [("wind_jul_e", "wind_jul_n"), ("wind_jan_e", "wind_jan_n")]
    if not all(k in L for p in pairs for k in p):
        pairs = [("wind_e", "wind_n")]
    if not all(k in L for p in pairs for k in p):
        z = np.zeros(len(sel))
        return z, z, np.ones(len(sel))
    de, dn, dp = np.zeros(len(sel)), np.zeros(len(sel)), np.zeros(len(sel))
    for e, nn in pairs:
        u, v = np.asarray(L[e], float)[sel], np.asarray(L[nn], float)[sel]
        s2 = u * u + v * v
        de, dn, dp = de + s2 * u / len(pairs), dn + s2 * v / len(pairs), dp + s2 ** 1.5 / len(pairs)
    return de, dn, np.where(dp > 1e-9, np.hypot(de, dn) / np.maximum(dp, 1e-9), 1.0)


DERIVED = {
    # the aridity index P / PET (landform.aridity; the world's own pet layer)
    "aridity": lambda L, sel: (np.asarray(L["precipitation"], float)[sel]
                               / np.maximum(np.asarray(L["pet"], float)[sel] if "pet" in L else 1000.0, 1.0)),
    "hard_top": lambda L, sel: _resist(np.asarray(L["strata_top"])[sel]),
    "hard_next": lambda L, sel: _resist(np.asarray(L["strata_next"])[sel]),
    "granite": lambda L, sel: (np.asarray(L["strata_top"])[sel] == 11).astype(float),  # surface.GRANITE
    # how readily the exposed carbonate dissolves: limestone 1, dolomite (less soluble) 0.5
    "purity": lambda L, sel: np.select([np.asarray(L["strata_top"])[sel] == 6, np.asarray(L["strata_top"])[sel] == 14],
                                       [1.0, 0.5], 0.0),  # surface.LIMESTONE, DOLOMITE
    "drift_e": lambda L, sel: sand_drift(L, sel)[0],
    "drift_n": lambda L, sel: sand_drift(L, sel)[1],
    "drift_ratio": lambda L, sel: sand_drift(L, sel)[2],
}
DEFAULTS = {"rift_strain": 0.4, "glaciated_myr": LF.GLACIATED_NEVER, "crust_thickness": 35.0, "precipitation": 500.0,
            "plate_boundary": 0.0, "temperature": 15.0}


def _resist(rock):
    return np.array([RESIST.get(int(r), 0.5) for r in rock], float)


def _column(L, name, sel):
    """The per-cell values of `name` over the coarse cells sel."""
    if name in DERIVED:
        return DERIVED[name](L, sel)
    if name in L:
        return np.asarray(L[name], float)[sel]
    return np.full(len(sel), float(DEFAULTS[name]))


class Landforms:
    """The landform classes around a zoom: their weights and parameters per
    pixel, and the blended hooks. build() returns None where no class with a
    synthesiser is near (the zoom is then exactly as without this pass)."""

    def __init__(self, ctxs: dict):
        self.ctxs = ctxs  # class id -> Ctx (with its w and prm)

    @classmethod
    def build(cls, L, sel, cx, cy, land_c, px, py, Pk, sp, res, nx, ny, seed, land, base, interp, grid, to_plane):
        """L: the world's layers on `grid`; sel: the coarse cells around the
        region (cx, cy: their projected centres, land_c: land);
        interp(vals, wts, sigma): the zoom's Gaussian interpolation onto the
        pixels; to_plane(unit vectors): the zoom's projection (km)."""
        centers = grid.centers[sel]
        if "landform" not in L:
            return None
        form = np.asarray(L["landform"])[sel]
        ks = [k for k in SYNTH if np.any((form == k) & land_c)]
        if not ks:
            return None
        if any("coast_km" in SYNTH[k].layers for k in ks):  # (km from the coarse coast, over land: planet-fixed)
            gl = np.asarray(L["elevation"]) > 0
            coast = gl & (np.add.reduceat((~gl)[grid.nbr_idx], grid.nbr_off[:-1]) > 0)
            L = {**L, "coast_km": np.minimum(LF.coast_km(grid, gl, coast), 2000.0)}
        cols, wts, spans = [], [], {}
        for k in ks:
            ind = ((form == k) & land_c).astype(float)
            spans[k] = (len(cols), SYNTH[k].layers)
            cols.append(ind)
            wts.append(np.ones_like(ind))
            for name in SYNTH[k].layers:
                cols.append(_column(L, name, sel))
                wts.append(ind)
        f, _ = interp(np.column_stack(cols), np.column_stack(wts), 0.5 * sp)
        for k in ks:  # (classes with their own kernel width: their parameters again)
            c0, names = spans[k]
            if SYNTH[k].sigma != 0.5 and names:
                f[:, c0 + 1:c0 + 1 + len(names)] = interp(np.column_stack(cols[c0 + 1:c0 + 1 + len(names)]),
                                                          np.column_stack(wts[c0 + 1:c0 + 1 + len(names)]),
                                                          SYNTH[k].sigma * sp)[0]
        # the coarse land's regional slope and its direction
        gy, gx = np.gradient(base.reshape(ny, nx), res)
        gx, gy = gx.ravel(), -gy.ravel()  # rows run south: d/dy (north) = -d/drow
        g = np.hypot(gx, gy)
        down = (-gx / np.maximum(g, 1e-9), -gy / np.maximum(g, 1e-9))
        ctxs = {}
        for j, k in enumerate(ks):
            c0, names = spans[k]
            share = np.nan_to_num(f[:, c0])
            c = Ctx(nx, ny, res, sp, px, py, Pk, seed, land, base, down, g)
            n = c.noise(0.5 * sp, 3, 70 + j)
            lo, hi = (0.08, 0.3) if SYNTH[k].line else (0.3, 0.6)
            c.w = smoothstep(lo, hi, share + 0.12 * n) * land
            c.prm = {name: f[:, c0 + 1 + i] for i, name in enumerate(names)}
            # (outside the class's cells' reach the parameters are NaN: weight 0 there)
            for v in c.prm.values():
                c.w = np.where(np.isfinite(v), c.w, 0.0)
            c.prm = {name: np.nan_to_num(v) for name, v in c.prm.items()}
            ctxs[k] = c
        # (where classes overlap, the one landform.classify ranks first keeps
        # its weight: a narrow escarpment or rift isn't diluted by the fold
        # belt or shield beside it)
        taken = np.zeros(len(px))
        for k in sorted(ctxs, key=PRIORITY.index):
            c = ctxs[k]
            c.w = np.minimum(c.w, np.maximum(1.0 - taken, 0.0))
            taken += c.w
        cues = {"thick": _column(L, "crust_thickness", sel), "elev": np.maximum(_column(L, "elevation", sel), 0.0),
                "converging": _column(L, "plate_boundary", sel), "drift_e": _column(L, "drift_e", sel),
                "drift_n": _column(L, "drift_n", sel)}
        for k, c in ctxs.items():
            if SYNTH[k].zoned:
                c.zone = zone_stats(grid, L, k, sel, cx, cy, px, py, to_plane, interp, sp)
        for j, (k, c) in enumerate(ctxs.items()):
            if SYNTH[k].axis and np.any(c.w > 0):
                ind = ((form == k) & land_c).astype(float)
                c.frames = build_frames(Pk, seed + 1009 * k, centers, ind,
                                        {name: _column(L, name, sel) for name in SYNTH[k].layers}, cues, sp,
                                        SYNTH[k].axis)
        return cls(ctxs)

    def weight(self) -> np.ndarray:
        """Total weight of the synthesised classes per pixel."""
        return sum(c.w for c in self.ctxs.values())

    def _sum(self, hook) -> np.ndarray:
        out = np.zeros(len(next(iter(self.ctxs.values())).land))
        for k, c in self.ctxs.items():
            if not np.any(c.w > 0):
                continue
            v = getattr(SYNTH[k], hook)(c)
            if v is not None:
                out += c.w * v
        return np.clip(out, 0.0, 1.0)

    def basins(self) -> np.ndarray:
        """0..1 per pixel: where closed depressions stay closed (Synth.basins)."""
        return self._sum("basins")

    def lakes(self) -> np.ndarray:
        """0..1 per pixel: where closed depressions hold lakes (Synth.lakes)."""
        return self._sum("lakes")

    def dominant(self) -> np.ndarray:
        """The class with the most weight at each pixel (0: none above 0.5)."""
        ks = list(self.ctxs)
        w = np.stack([self.ctxs[k].w for k in ks])
        best = np.argmax(w, 0)
        return np.where(w.max(0) > 0.5, np.array(ks)[best], 0)

    def target(self, h) -> np.ndarray | None:
        dz = None
        for k, c in self.ctxs.items():
            if not np.any(c.w > 0):
                continue
            d = SYNTH[k].target(c, h)
            if d is not None:
                dz = c.w * d if dz is None else dz + c.w * d
        return dz

    def _bench(self, z, mask):
        out = z.copy()
        for k, c in self.ctxs.items():
            st = SYNTH[k].strata(c, z)
            w = c.w * mask
            if st is None or not np.any(w > 0):
                continue
            sv = st.height(z, c.px, c.py)
            # Anti-aliasing: each cliff spans at least FACE_PX pixels across
            # (steep, but not a one-pixel step that aliases into a staircase
            # along the scarp), and where a band is narrower than a couple of
            # pixels (a steep valley side) the benches fade out rather than
            # stipple it.
            gy, gx = np.gradient(sv.reshape(c.ny, c.nx), c.res)
            gs = _box_mean(np.hypot(gx, gy), np.ones((c.ny, c.nx)), 1).ravel()
            bw = np.maximum(st.period, 1.0) / np.maximum(gs * c.res, 1e-6)  # px per band
            face = np.clip(FACE_PX / bw, st.face, FACE_MAX)
            fade = smoothstep(BAND_MIN_PX[0], BAND_MIN_PX[1], bw)
            # (the cliffs follow the smoothed stratigraphic height, the land's
            # texture added back: a scarp's line isn't jittered pixel by pixel)
            ss = _box_mean(sv.reshape(c.ny, c.nx), np.ones((c.ny, c.nx)), FACE_SMOOTH).ravel()
            if c.chan is not None:  # (but a river falls over the cliff in one step: a waterfall)
                face, fade = np.where(c.chan, st.face, face), np.where(c.chan, 1.0, fade)
                ss = np.where(c.chan, sv, ss)
            zk = bench_map(ss, st.anchor, st.period, st.bands, st.cliff, st.power, st.top_k, face)
            out += w * fade * st.amp * (zk - ss)
        return out

    def plateau(self, h) -> tuple:
        """Where each class's top bed holds the ground: (weight, level m) per
        pixel, the weight that of the classes whose stratigraphic height is
        above their anchor (on the top bed), the level their (weighted) anchor. Designed falls
        (zoom.staircase) may stand that high: the land steps up into the
        plateau above them."""
        w, lvl = np.zeros(len(h)), np.zeros(len(h))
        for k, c in self.ctxs.items():
            st = SYNTH[k].strata(c, h)
            if st is None or not np.any(c.w > 0):
                continue
            sv = st.height(h, c.px, c.py)
            on = c.w * (sv >= st.anchor)
            w += on
            lvl += on * st.anchor
        return w, np.where(w > 1e-6, lvl / np.maximum(w, 1e-6), 0.0)

    def scarps(self, h) -> tuple:
        """The single scarps (Strata with one band: the escarpment) per
        pixel: (weight, level of its top m, cliff height m). A designed
        reach crossing one gets its main fall there (zoom.build)."""
        w, lvl, hgt = np.zeros(len(h)), np.zeros(len(h)), np.zeros(len(h))
        for k, c in self.ctxs.items():
            st = SYNTH[k].strata(c, h)
            if st is None or st.bands != 1 or not np.any(c.w > 0):
                continue
            w += c.w
            lvl += c.w * st.anchor
            hgt += c.w * st.cliff * st.period
        ok = w > 1e-6
        return w, np.where(ok, lvl / np.maximum(w, 1e-6), 0.0), np.where(ok, hgt / np.maximum(w, 1e-6), 0.0)

    def remap(self, h, mask, rec=None, order=None, channel=None, mask_shape=None, q=None):
        """The finished surface h reshaped by the classes, blended by weight
        x mask (0..1). With the drainage (rec, order: outlets first; channel:
        the river pixels), first the relief hooks: each pixel's height above
        its drainage d (the first channel pixel down its receivers) becomes
        D (1 - exp(-A d / dref)) (dref: d's mean over RELIEF_KM; A: the
        hook's sharpness, G its gain; D = G dref (1 + A) / A: G x the
        mean height above the drainage; the mean is restored after): valleys cut
        steeply into flat interfluves (a plateau and its canyons), the
        channels and the order along every flow path kept (relief_along()). Then the strata hooks: bench_map() (the
        caller breaches any sill they leave across a flow path: breach())."""
        z = h
        if rec is not None:
            hc = drain_level(h, rec, order, channel)
            d = np.maximum(h - hc, 0.0)
            # (d against its local mean: the class sets the canyons' depth,
            # whatever the relief the landscape pass gave it)
            c0 = next(iter(self.ctxs.values()))
            rr = max(1, int(round(RELIEF_KM / c0.res)))
            wl = c0.land.reshape(c0.ny, c0.nx).astype(float)
            dref = np.maximum(_box_mean(d.reshape(c0.ny, c0.nx) * wl, wl, rr).ravel(), 2.0)
            wt, Aw, Gw = np.zeros(len(h)), np.zeros(len(h)), np.zeros(len(h))
            for k, c in self.ctxs.items():
                rl = SYNTH[k].relief(c)
                w = c.w * mask
                on = (c.w > 0.5) & c.land
                c.relief_m = float(np.mean(d[on])) * (rl[1] if rl else 1.0) if on.any() else None
                if rl is None or not np.any(w > 0):
                    continue
                wt += w
                Aw += w * rl[0]
                Gw += w * rl[1]
            ok = wt > 1e-6
            A = np.where(ok, Aw / np.maximum(wt, 1e-6), 1.0)
            G = np.where(ok, Gw / np.maximum(wt, 1e-6), 1.0)
            # (D = G (1+A)/A x dref: G x the mean height above the drainage, for
            # d spread exponentially about dref: the class shapes the relief,
            # flat tops over steep valley walls, deepening it by its gain G)
            D = G * dref * (1 + A) / A
            z = relief_along(h, hc, rec, order, channel, np.minimum(wt, 1.0), D, A, dref)
        # the shape hooks: fault blocks, folds, domes, on the reshaped surface
        gap = None
        for k, c in self.ctxs.items():
            c.chan = channel
            w = c.w * (mask if mask_shape is None else mask_shape)
            if not np.any(w > 0):
                continue
            dz = SYNTH[k].shape(c, z)
            if dz is None:
                continue
            if SYNTH[k].gaps and q is not None:
                # (the rivers keep their graded beds through the structure:
                # it rises beside them, a water gap, not a staircase of falls)
                if gap is None:
                    big = (q >= GAP_Q).reshape(-1)
                    dk = ZK.inside_distance(~big, c.nx, c.ny, False) * c.res
                    gap = smoothstep(0.5 * c.res, max(3 * c.res, GAP_KM), dk)
                dz = dz * gap
            z = z + w * dz
        return self._bench(z, mask)

    def finish(self, h, fin) -> dict:
        """After the final drainage (zoom.build), on the finished land
        (fin: rec, order (outlets first), q (m^3/s), water (sea and lakes),
        ice, active): the overlay hooks (Synth.overlay: dunes, dolines,
        towers, poljes), each made mean-neutral over ~a cell's width (the
        cell means stay) and kept off its streams; streams sink where the
        classes say (Synth.sinks: karst), their valleys dry, resurging at
        springs; the overlays' pits below the local base level hold ponds
        (Synth.ponds). Returns h, pond (mask), pond_depth (m), q, stats."""
        c0 = next(iter(self.ctxs.values()))
        nx, ny, res = c0.nx, c0.ny, c0.res
        q, rec, order = fin["q"], fin["rec"], fin["order"]
        free = fin["active"] & ~fin["water"] & ~fin["ice"]
        n = len(h)
        tot, pondw, pit = np.zeros(n), np.zeros(n), np.zeros(n)
        st = {}
        # streams that sink (karst): under SINK_Q x the class's sinks() they carry no water at the surface
        sk = np.zeros(n)
        for k, c in self.ctxs.items():
            v = SYNTH[k].sinks(c) if np.any(c.w > 0) else None
            if v is not None:
                sk = np.maximum(sk, c.w * v)
        dry = free & (sk > 0.25) & (q < SINK_Q * sk) & (q > 0)
        q2 = np.where(dry, 0.0, q)
        if dry.any():
            r = np.where(rec >= 0, rec, np.arange(n))
            wet_r = ~dry[r] & (rec >= 0)
            st["springs"] = int(np.sum(dry & wet_r & (q >= 1.0)))  # (where a sunk stream's water comes back)
            donor_wet = np.zeros(n, bool)
            np.logical_or.at(donor_wet, r[~dry & (q >= 1.0) & (rec >= 0)], True)
            st["sinks"] = int(np.sum(dry & donor_wet))  # (streams flowing in that sink: swallow holes)
            st["dry_valley_km"] = round(float(np.sum(dry & (q >= 1.0))) * res, 0)
        flow = q2 > 0
        # the water table: the first flowing river (or the sea, a lake) down the drainage
        fin = {**fin, "base": drain_level(h, rec, order, (q2 >= 1.0) | (rec < 0))}
        for k, c in self.ctxs.items():
            if not np.any(c.w > 0):
                continue
            dz = SYNTH[k].overlay(c, h, fin)
            if dz is None:
                continue
            near = ZK.inside_distance(~(flow & (q2 >= SYNTH[k].overlay_q)), nx, ny, False) * res
            m = c.w * free * smoothstep(0.5 * res, max(2.0 * res, 1.5), near)
            # (mean-neutral over ~a cell: the land under dunes and towers is
            # lowered by their mean, around dolines raised: the cell means stay)
            rr = max(1, int(round(0.25 * c.sp / res)))
            wl = (m > 0).reshape(ny, nx).astype(float)
            mean = _box_mean((m * dz).reshape(ny, nx), wl, rr).ravel()
            tot += m * dz - np.where(m > 0, mean, 0.0)
            if SYNTH[k].ponds:
                pondw = np.maximum(pondw, m)
                pit += m * np.minimum(dz, 0.0)
            if c.cache.get("overlay_stats"):
                st[LF.CLASSES[k][1]] = c.cache["overlay_stats"]
        h2 = np.where(free, np.maximum(h + tot, 0.5), h)
        pond, pdep = np.zeros(n, bool), np.zeros(n)
        if np.any(pondw > 0.5):
            hc = fin["base"]
            # (a pit's floor against the water table: both before the mean-neutral shift)
            pond = (pondw > 0.5) & free & (h + pit < hc - POND_M) & (pit < -POND_M)
            pdep = np.where(pond, np.minimum(hc - h - pit, -pit), 0.0)
            st["ponds"] = int(len(np.unique(ZK.label_components(pond, nx, ny)[0][pond]))) if pond.any() else 0
        return {"h": h2, "pond": pond, "pond_depth": np.where(pond, pdep, 0.0), "q": q2, "stats": st}

    def stats(self) -> dict:
        """% of land pixels each class shapes (weight > 0.5), by class key."""
        land = next(iter(self.ctxs.values())).land
        n = max(int(land.sum()), 1)
        return {LF.CLASSES[k][1]: round(100 * float(((c.w > 0.5) & land).sum()) / n, 1) for k, c in self.ctxs.items()}
