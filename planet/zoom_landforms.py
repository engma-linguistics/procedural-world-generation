"""Landform synthesis in the regional zoom (PW-010..012): each coarse cell's
landform class (landform.py) turns into its own kind of terrain.

Class dispatch
--------------
SYNTH maps a landform class id to a synthesiser (a Synth subclass). A
synthesiser overrides the hooks it needs (the defaults contribute nothing);
the dispatcher (Landforms) blends what they return by the class's weight w_k:

  target(cx, h)    metres added to the zoom's target surface before the
                   landscape pass (and before its coarse-mean correction):
                   shapes the landscape is built around (tilted blocks,
                   domes, a flattened plain: for PW-011/012; unused in batch 1).
  relief(cx)       (A, G): how the finished landscape's relief is reshaped
                   around its drainage. Each pixel's height above the first
                   channel down its receivers, d, becomes D (1 - exp(-A d /
                   dref)) with D = G (1+A)/A dref (dref: d's local mean): flat
                   interfluves over steep valley walls (a plateau and its
                   canyons), G x as deep. Integrated down the drainage
                   (relief_along()), so channels keep their height and every
                   pixel stays above its receiver.
  strata(cx, h)    a Strata: how hard beds turn the reshaped surface into
                   benches and scarps (bench_map()), as h + sum_k w_k (z_k - h).
                   A channel crossing a cliff falls over it.
  layers           (attribute) the world layers the class reads, interpolated
                   over its own cells into Ctx.prm.

The strata also tell the designed falls (zoom.knickpoints / staircase) about
the plateau: plateau() is where a top bed holds the ground up (the
staircase may stand that high), scarps() where a single scarp (the
escarpment) is: a designed reach crossing it takes its main fall there, the
river running on the plateau down to the lip.

Weights: a class's weight is the Gaussian-kernel share of its cells around
each pixel (sigma half a cell, over the projected cell centres, as the
zoom's other coarse fields), roughened by noise and sharpened by a
smoothstep: classes blend over ~20-40 km, with no hexagon or cell-edge seam.
Narrow classes (the escarpment: a band one or two cells wide) get a lower
threshold. Where weights add up to more than 1 they are scaled down.

In zoom.build, after the landscape pass and creep: remap() on the drainage
of the crept surface (not on glaciers, lake rims and outflows, nor within a
few km of the designed falls' courses, whose staircase is the river's);
then any sill left across a flow path is cut through (breach(), inside the
classes' reach), each coarse cell's mean restored by a smooth correction
weighted to where the classes are, and the result breached again.

Levels are one per zoom (zone_level(), a class's median e*, a zone-wide
period): flat-lying beds are horizontal, and a level that varied across the
land faster than its rivers fall would meet them with cliffs from below.

Bench map (bench_map(), shared by batch 1)
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
                 zoom pixels; at least 0.8x the height above the drainage)
                 under a flat top (90th percentile, relief x 0.3): stair-
                 stepped valley sides (Deccan, Columbia River).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numba import njit

from . import landform as LF
from . import zoom_kernels as ZK


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


class Synth:
    """A landform class's synthesiser (see the module docstring). Override
    the hooks a class needs; the defaults contribute nothing."""
    layers: tuple = ()  # world layers interpolated over the class's cells into Ctx.prm
    line = False  # a narrow class (landform.LINES): wider, lower weight threshold
    sigma = 0.5  # x cell spacing: the Gaussian kernel its layers are interpolated with

    def target(self, cx: Ctx, h: np.ndarray):
        return None

    def relief(self, cx: Ctx) -> tuple | None:
        return None

    def strata(self, cx: Ctx, h: np.ndarray) -> Strata | None:
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

    def relief(self, cx):
        return 1.5, 1.25

    def strata(self, cx, h):
        # (flows are ~10-50 m; at zoom pixels the steps seen are packages of
        # them, at least ~ a third of the valleys' depth)
        P = max(float(np.clip(self.FLOW_M * (cx.res / 2.0) ** 0.3, 60.0, 150.0)), self.RELIEF * cx.zone_relief(h))
        anchor = cx.zone_level(h, 90)
        return Strata(anchor, P, cliff=0.55, power=1.5, top_k=0.3)


RELIEF_KM = 20.0  # relief hooks: the scale of d's local mean


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


SYNTH = {LF.ESCARPMENT: Escarpment(), LF.CAPROCK: Caprock(), LF.LAVA_PLATEAU: LavaPlateau()}


class Landforms:
    """The landform classes around a zoom: their weights and parameters per
    pixel, and the blended hooks. build() returns None where no class with a
    synthesiser is near (the zoom is then exactly as without this pass)."""

    def __init__(self, ctxs: dict):
        self.ctxs = ctxs  # class id -> Ctx (with its w and prm)

    @classmethod
    def build(cls, L, sel, cx, cy, land_c, px, py, Pk, sp, res, nx, ny, seed, land, base, interp):
        """L: the world's layers; sel: the coarse cells around the region
        (cx, cy: their projected centres, land_c: land); interp(vals, wts,
        sigma): the zoom's Gaussian interpolation onto the pixels."""
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
                cols.append(np.asarray(L[name], float)[sel])
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
        tot = np.zeros(len(px))
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
            tot += c.w
            ctxs[k] = c
        over = np.maximum(tot, 1.0)
        for c in ctxs.values():
            c.w = c.w / over
        return cls(ctxs)

    def weight(self) -> np.ndarray:
        """Total weight of the synthesised classes per pixel."""
        return sum(c.w for c in self.ctxs.values())

    def target(self, h) -> np.ndarray | None:
        dz = None
        for k, c in self.ctxs.items():
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
            zk = bench_map(sv, st.anchor, st.period, st.bands, st.cliff, st.power, st.top_k, st.face)
            out += w * (zk - sv)
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

    def remap(self, h, mask, rec=None, order=None, channel=None):
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
        return self._bench(z, mask)

    def stats(self) -> dict:
        """% of land pixels each class shapes (weight > 0.5), by class key."""
        land = next(iter(self.ctxs.values())).land
        n = max(int(land.sum()), 1)
        return {LF.CLASSES[k][1]: round(100 * float(((c.w > 0.5) & land).sum()) / n, 1) for k, c in self.ctxs.items()}
