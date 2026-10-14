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
                   and where they hold lakes (else they are filled flat).
  layers           (attribute) the world layers the class reads, interpolated
                   over its own cells into Ctx.prm (DERIVED: hardness of the
                   exposed and next strata, granite; DEFAULTS for layers a
                   world lacks).
  axis             (attribute) 'band' / 'gradient': the class gets Ctx.frames,
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

Levels are one per zoom (zone_level(), a class's median e*, a zone-wide
period): flat-lying beds are horizontal, and a level that varied across the
land faster than its rivers fall would meet them with cliffs from below.

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
  escarpment     one band 0.8 e* deep below the escarpment cells' level e*
                 (their median in the zoom), with a 0.75 cliff: the plateau
                 stays, the land in front of it steps down to a lowland
                 (Drakensberg, Western Ghats). The class rule puts the scarp at
                 its retreat distance from the rifted coast; valleys below e*
                 make the re-entrants of headward retreat, and the rivers
                 crossing it fall over it.
  caprock        hard caps (strata_top_km, 40-400 m, at most twice the
                 land's height above its drainage, so benches show on low
                 land too) over soft slopes, endlessly repeated down from the
                 85th percentile of the land: plateau, mesas, buttes and
                 stepped benches (Grand Staircase); relief 1.5x deeper. A
                 dip (strata_dip, downhill) tilts them into asymmetric
                 cuestas (scarps facing up-dip, long dip slopes).
  lava plateau   stacked flows: steps of ~60-150 m (a package of flows at
                 zoom pixels; at least 0.8x the height above the drainage,
                 and VISIBLE_PX pixels wide on the zone's median slope)
                 under a flat top (90th percentile, relief x 0.3): stair-
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
    tilt: tuple | None = None  # (tx, ty) m/km: the bedding drops along (tx, ty)
    face: float = 0.08  # the share of a band its cliff rises over (bench_map)


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
    cache: dict = field(default_factory=dict)

    def noise(self, wavelength, octaves, k):
        """fbm ~N(0, 1)-ish at `wavelength` km (seed offset k)."""
        return ZK.fbm(self.Pk, wavelength, octaves, 0.5, self.seed + k) / 0.17

    def zone_level(self, h, q):
        """The q-th percentile of h over the class's own land (weight > 0.5;
        else wherever it weighs): one level for the whole zoom. Flat-lying
        beds are horizontal: levels that varied across the land would tilt
        them, and a river gentler than the tilt would meet each cliff from
        below."""
        on = self.land & (self.w > 0.5)
        if on.sum() < 10:
            on = self.land & (self.w > 0)
        return float(np.percentile(h[on], q)) if on.any() else float(np.max(h))

    def zone_relief(self, h):
        """m: the class's typical height above its drainage (set by
        Landforms.remap; else the spread of h about its local mean)."""
        if self.relief_m is not None:
            return self.relief_m
        on = self.land & (self.w > 0.5)
        if not on.any():
            return 50.0
        return float(np.mean(np.abs(h - self.local_top(h, 0.3 * self.sp, 0.0))[on]))

    def zone_slope(self, h):
        """m/km: the median slope of h over the class's own land."""
        on = self.land & (self.w > 0.5)
        if on.sum() < 10:
            return 0.0
        gy, gx = np.gradient(h.reshape(self.ny, self.nx), self.res)
        return float(np.median(np.hypot(gx, gy).ravel()[on]))

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
             "gradient": {"thick": (4.0, 1.0), "elev": (4.0, 1.0), "converging": (4.0, 2.0), "class": (4.0, 0.3)}}


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


GORGE_Q, GORGE_MIN_M = 100.0, 30.0  # m^3/s, m: a river this big falling this far over a landform's cliff...
GORGE_KM, GORGE_MAX_KM, GORGE_GRAD = 3.0, 12.0, 2.0  # ... retreats into a gorge GORGE_KM sqrt(Q / 1000) long


def scarp_gorges(z, rec, q, w, nx, ny, res, fixed):
    """Falls over a landform's cliffs retreat upstream, as designed falls'
    lips do (zoom.knickpoints), into a gorge: where a river of at least
    GORGE_Q m^3/s drops GORGE_MIN_M within 3 px (class weight w > 0.5),
    its bed is lowered from the foot upstream for GORGE_KM x sqrt(Q / 1000
    m^3/s) km (at most GORGE_MAX_KM, and not past the next cliff up),
    rising GORGE_GRAD m/km, the fall now at the gorge's head; walls as for
    cut(). Returns (z, number of gorges)."""
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
        return z, 0
    z = z.copy()
    src = np.zeros(n, bool)
    done = np.zeros((ny, nx), bool)
    count = 0

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
        count += 1
    if count:
        g = GAP_GRAD * min(1.0, (0.5 / res) ** 0.5)
        z = np.where(fixed, z, lower_envelope(z, src, g, nx, ny, res))
    return z, count


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


class Escarpment(Synth):
    """Great escarpment: one band below the escarpment cells' level e*,
    over a moderately flattened plateau."""
    layers = ("elevation",)
    line = True
    STEP = (0.8, 200.0, 1500.0)  # band height: fraction of e*, clipped to (m)

    def _level(self, cx):
        """e*: the escarpment cells' level, one for the zoom (a level varying
        along the margin faster than its rivers fall would meet them with
        the scarp from below)."""
        on = (cx.w > 0.5) & cx.land
        v = cx.prm["elevation"][on] if on.any() else cx.prm["elevation"]
        return max(float(np.median(v)), 1.0)

    def _step(self, cx):
        return float(np.clip(self.STEP[0] * self._level(cx), self.STEP[1], self.STEP[2]))

    def relief(self, cx):
        return 1.2, 1.0

    def strata(self, cx, h):
        return Strata(self._level(cx), self._step(cx), bands=1, cliff=0.75, power=2.0, top_k=1.0, face=0.015)


class Caprock(Synth):
    """Caprock plateau, mesas, buttes and stepped benches; dipping: cuestas."""
    layers = ("strata_top_km", "strata_dip")
    CAP_M = (40.0, 400.0)  # the cap's cliff (m): strata_top_km, clipped
    CLIFF = 0.45  # the cap's share of each bench period (the rest: soft slope)
    RELIEF = 2.0  # x the zone's height above its drainage: at most this period, so benches show on low land too

    def _cap(self, cx):
        # (one for the zoom: the bench levels lie whole periods below the
        # anchor, so a period varying across the land would scatter them)
        on = (cx.w > 0.5) & cx.land
        v = cx.prm["strata_top_km"][on] if on.any() else cx.prm["strata_top_km"]
        return float(np.clip(1000 * np.median(v), *self.CAP_M))

    def relief(self, cx):
        return 1.5, 1.5

    def strata(self, cx, h):
        P = min(self._cap(cx) / self.CLIFF, max(self.RELIEF * cx.zone_relief(h), 60.0))
        anchor = cx.zone_level(h, 85)
        t = 1000 * np.tan(np.radians(cx.prm["strata_dip"]))  # m/km
        tilt = (t * cx.downhill[0], t * cx.downhill[1]) if np.any(t > 0.3) else None
        return Strata(anchor, P, cliff=self.CLIFF, power=2.0, top_k=0.5, tilt=tilt)


class LavaPlateau(Synth):
    """Traps: stacked flows under a flat top."""
    layers = ("strata_top_km",)
    FLOW_M = 110.0  # a flow package's step (m), at 2 km pixels
    RELIEF = 0.8  # x the zone's height above its drainage: at least this step
    VISIBLE_PX = 2.5  # ... and one step at least this many pixels wide on the zone's typical slope

    def relief(self, cx):
        return 1.5, 1.25

    def strata(self, cx, h):
        # (flows are ~10-50 m; at zoom pixels the steps seen are packages of
        # them, at least ~ a third of the valleys' depth)
        P = max(float(np.clip(self.FLOW_M * (cx.res / 2.0) ** 0.3, 60.0, 150.0)), self.RELIEF * cx.zone_relief(h),
                self.VISIBLE_PX * cx.res * cx.zone_slope(h))
        anchor = cx.zone_level(h, 90)
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
    layers = ("rift_strain", "landform_age", "elevation", "precipitation")
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
        return smoothstep(600.0, 1200.0, cx.prm["precipitation"])


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


def _dilate(m, r):
    out = m.copy()
    for dr in range(-r, r + 1):
        for dc in range(-r, r + 1):
            out |= np.roll(np.roll(m, dr, 0), dc, 1)
    return out


RELIEF_KM = 20.0  # relief hooks: the scale of d's local mean
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


# the classes in landform.classify's order (the first that holds wins there; here: keeps its weight)
PRIORITY = [LF.ARC_CLASS, LF.HOTSPOT_CLASS, LF.RIFT, LF.ESCARPMENT, LF.FOLD_BELT, LF.LAVA_PLATEAU, LF.DUNES, LF.KARST,
            LF.CAPROCK, LF.COASTAL_PLAIN, LF.SHIELD, LF.HILLS, LF.SEA]
SYNTH = {LF.ESCARPMENT: Escarpment(), LF.CAPROCK: Caprock(), LF.LAVA_PLATEAU: LavaPlateau(),
         LF.FOLD_BELT: FoldBelt(), LF.RIFT: Rift(), LF.SHIELD: Shield()}


# per-cell columns the synthesisers read besides the world's layers, and
# defaults for layers a world lacks (sliced before they existed)
DERIVED = {
    "hard_top": lambda L, sel: _resist(np.asarray(L["strata_top"])[sel]),
    "hard_next": lambda L, sel: _resist(np.asarray(L["strata_next"])[sel]),
    "granite": lambda L, sel: (np.asarray(L["strata_top"])[sel] == 11).astype(float),  # surface.GRANITE
}
DEFAULTS = {"rift_strain": 0.4, "glaciated_myr": LF.GLACIATED_NEVER, "crust_thickness": 35.0, "precipitation": 500.0,
            "plate_boundary": 0.0}


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
    def build(cls, L, sel, cx, cy, land_c, px, py, Pk, sp, res, nx, ny, seed, land, base, interp, centers):
        """L: the world's layers; sel: the coarse cells around the region
        (cx, cy: their projected centres, land_c: land; centers: their unit
        vectors); interp(vals, wts, sigma): the zoom's Gaussian
        interpolation onto the pixels."""
        if "landform" not in L:
            return None
        form = np.asarray(L["landform"])[sel]
        ks = [k for k in SYNTH if np.any((form == k) & land_c)]
        if not ks:
            return None
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
                "converging": _column(L, "plate_boundary", sel)}
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
            sv = z + (0.0 if st.tilt is None else st.tilt[0] * c.px + st.tilt[1] * c.py)
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
            out += w * fade * (zk - ss)
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
            sv = h + (0.0 if st.tilt is None else st.tilt[0] * c.px + st.tilt[1] * c.py)
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

    def stats(self) -> dict:
        """% of land pixels each class shapes (weight > 0.5), by class key."""
        land = next(iter(self.ctxs.values())).land
        n = max(int(land.sum()), 1)
        return {LF.CLASSES[k][1]: round(100 * float(((c.w > 0.5) & land).sum()) / n, 1) for k, c in self.ctxs.items()}
