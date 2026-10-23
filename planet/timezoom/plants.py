"""The time zoom's vegetation (PW-450): the run's model (planet.vegetation, its cheap variant, as
earth.update_vegetation) grown on each full climate, warm-started from the last, and its feedbacks:

- local, as in the run (climate.compute's veg): forests give more of their rain back to the air (Budyko w)
  and hide the lying snow (the surface's albedo, climate.albedo_warming). A full climate feels the plants
  grown on the one before; the plants grown on it then correct its albedo warming at once (the rain's
  part waits for the next full climate), so a glacial's forest-to-tundra shift isn't a refresh late.
- global (p.veg 'on'): the planet's albedo change from the plants' change since the start, at the current
  snow cover (the snow's own change is a fast feedback, inside the climate's sensitivity; ice that
  replaces them is the ice albedo's), x veg_toa to the top of the atmosphere, x veg_lambda to C, in dTg
  (Forcing, lagged veg_lag). Earth's LGM: ~-1.1 W/m2 (Köhler et al. 2010), mostly boreal forest turning
  to snow-covered tundra.

At the start the plants are grown to balance with the start climate (the full model, then the climate
again with them, then the cheap model), so an unforced zoom's plants and climate stay where they are.
Migration (PW-213): beside that, a second cover follows the same potentials in real years (the run's
cover equations, stepped one cell per step: vegetation._step's mig), so that a tree takes new ground only
beside a stand of its own, at p.veg_speed (m/yr; the step is one cell over it), and keeps its seeds only where
it still is. It is what the frames store (tree_cover) and a finished world starts from. It does not
feed back on the climate (that stays the first cover's: PW-471's glacial index and the ice are parked), and it
is grown over the 10 kyr before each full climate, on that climate's potentials; its frames wait for it.
The rivers' floodplains aren't modelled here (no flow: the wetland share comes from the lakes-free ground).
"""

from __future__ import annotations

import math
import time

import numpy as np

from .. import climate
from .. import vegetation as V
from ..geo import R_KM
from ..grid import Grid
from ..tectonics.params import Params
from .params import TZParams

# latitude belts of the diagnostics (deg; north to south)
SUBSTEPS = 12  # (a migration step of ~500 yr in this many, so a young stand grows up in it: vegetation.equilibrium)
BELTS = ((60, 90), (45, 60), (30, 45), (-30, 30), (-90, -30))


def neutral(n: int, tune: dict) -> dict:
    """A vegetation.feedback that gives the climate's reference surface (the albedo and Budyko w the
    temperature curve stands for: what climate.compute assumes with veg=None), for the land under ice."""
    t = tune
    m = (t["snow_albedo"] - t["albedo_snow_ref"]) / (t["snow_albedo"] - t["albedo_ref"])
    return dict(woody=np.full(n, t["veg_w_ref"]), deep=np.zeros(n), lai=np.zeros(n),
                albedo=np.full(n, t["albedo_ref"]), mask=np.full(n, m))


def _where(mask: np.ndarray, a: dict, b: dict) -> dict:
    return {k: np.where(mask, a[k], b[k]) for k in a}


class Plants:
    """The vegetation's state (cover nu and LAI per plant type) and its feedbacks."""

    def __init__(self, g: Grid, src: dict, p: TZParams, tilt: float, area: np.ndarray):
        self.g, self.p, self.tilt, self.area = g, p, tilt, area
        v = src.get("veg") or {}
        self.nu, self.lai = v.get("nu0"), None
        self.pco2_0 = float(v.get("pco2", V.CA_REF))  # ppm: the run's (climate.pco2) at the zoom's start
        self.unlocked = v.get("unlocked")
        # the CO2 part of dTg warms by co2_sensitivity per doubling, as the run's (earth.co2_term)
        self.co2_sens = float(src.get("params", {}).get("co2_sensitivity", Params().co2_sensitivity))
        self.tune = climate.TUNE
        self.neutral = neutral(g.n, self.tune)
        self.raw = None  # vegetation.feedback of the current plants (None: none grown yet)
        self.ref = None  # ... and of the start's
        self.land0 = None  # the start's land (ice included)
        self.dT_target = 0.0  # C: the global term's target (Forcing.veg)
        self.series: list = []
        self.time_s = 0.0
        self.every = 2.0  # kyr between frames (sim sets it)
        self.mig = None  # the migrating cover's state (NP, n, with the seeds), at t_last
        self.t_last = 0.0
        self.tree_at: dict = {}  # frame t (kyr) -> its tree cover (%, uint8), before the ice and sea masks
        self._last = None
        self.sun = climate.insolation(g.lat, tilt) * 1e6 / 86400.0  # W/m2 at the top of the atmosphere

    @property
    def on(self) -> bool:
        return self.p.veg != "off"

    def feedback(self, grounded: np.ndarray) -> dict | None:
        """climate.compute's veg: the current plants', the reference surface under grounded ice."""
        if self.raw is None:
            return None
        return _where(grounded, self.neutral, self.raw)

    def grow(self, c: dict, surf: np.ndarray, H_g: np.ndarray, co2_c: float, full: bool = False) -> None:
        t0 = time.time()
        v = V.model(self.g, surf, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], self.tilt,
                    c["cloud_jul"], c["cloud_jan"], ice=H_g, nu0=self.nu, lai0=None if full else self.lai,
                    pco2=self.pco2(co2_c), unlocked=self.unlocked, cheap=not full)
        self.nu, self.lai = v["eq"]["nu"], v["pot"]["lai"]
        self._last = v
        self.raw = V.feedback(self.nu, self.lai)
        self.tree = v["sm"]["tree"]
        self.time_s += time.time() - t0

    @staticmethod
    def pct(pot: dict, nu: np.ndarray) -> np.ndarray:
        return np.round(100 * V.tree_cover(pot, nu)).astype(np.uint8)

    def frame_times(self, t0: float, t1: float) -> list:
        """The frames' times in (t0, t1]."""
        e = self.every
        return [round(i * e, 3) for i in range(int(math.floor(t0 / e + 1e-9)) + 1, int(math.floor(t1 / e + 1e-9)) + 1)]

    def migrate(self, t1: float) -> None:
        """The migrating cover from t_last to t1 on the potentials just grown (self._last), keeping the tree
        cover at the frames in between."""
        t0, v = self.t_last, self._last
        self.t_last = t1
        if t1 <= t0:
            return
        times = self.frame_times(t0, t1)
        if self.p.veg_speed <= 0:  # (no limit: each frame is the balance with the climate)
            for f in times:
                self.tree_at[f] = self.pct(v["pot"], v["eq"]["nu"])
            self.mig = v["eq"]["nu_raw"]
            return
        t = time.time()
        n = max(1, round((t1 - t0) * 1000.0 / (self.g.spacing * R_KM * 1000.0 / self.p.veg_speed)))
        dt = (t1 - t0) * 1000.0 / n  # yr
        ks = sorted({min(n, max(1, round((f - t0) * 1000.0 / dt))) for f in times})
        eq = V.equilibrium(self.g, v["s"], v["pot"], v["fw"], v["land"], self.mig, steps=((n, dt),), migrate=V.SPREAD,
                           snaps=set(ks), substeps=SUBSTEPS)
        by_k = dict(zip(ks, eq["snaps"]))
        for f in times:
            self.tree_at[f] = self.pct(v["pot"], by_k[min(n, max(1, round((f - t0) * 1000.0 / dt)))])
        self.mig = eq["nu_raw"]
        self.mig_s = getattr(self, "mig_s", 0.0) + time.time() - t
        self.time_s += time.time() - t

    def glacial_bands(self, tree: np.ndarray, open_: np.ndarray, I: np.ndarray, lat: np.ndarray) -> dict:
        """The forest share of the ice-free land by latitude band at the glacial maxima (index within 0.15 of
        the highest, and over 0.5) and in the interglacials (index under 0.05), and the refugia (PW-103): the
        cells poleward of 40 deg that kept 30% tree cover through every frame of the glacial maxima."""
        area, out = self.area, {}
        for name, sel in (("glacial", (I >= max(I.max() - 0.15, 0.5))), ("interglacial", I <= 0.05)):
            idx = np.flatnonzero(sel)
            if not len(idx):
                continue
            bands = {}
            for a, b in ((60, 90), (50, 60), (40, 50), (30, 40), (15, 30), (-15, 15), (-40, -15), (-90, -40)):
                m = (lat >= a) & (lat < b)
                num = sum(float((tree[i] / 100.0 * area)[m & open_[i]].sum()) for i in idx)
                den = sum(float(area[m & open_[i]].sum()) for i in idx)
                bands[f"{a}..{b}"] = round(num / den, 3) if den else None
            out[name] = {"frames": int(len(idx)), "forest_share_by_lat": bands}
            if name == "glacial":
                keep = (np.abs(lat) >= 40) & (tree[idx] >= 30).all(0) & open_[idx].all(0)
                out[name]["refugia_cells"] = int(keep.sum())
                out[name]["refugia_mkm2"] = round(float(area[keep].sum()) / 1e12, 2)
        return out

    def finish(self, t_end: float) -> None:
        """The frames after the last full climate: the same potentials carried on to the end."""
        if self._last is not None:
            self.migrate(t_end)

    def pco2(self, co2_c: float) -> float:
        """The CO2 the plants feel, ppm, at the CO2 term co2_c (C) of dTg: the run's, co2_c / co2_sensitivity
        doublings away (PW-646)."""
        return self.pco2_0 * 2.0 ** (co2_c / self.co2_sens)

    def correct(self, c: dict, open_: np.ndarray, old: dict | None) -> None:
        """The climate c (computed with the plants old) given the current plants' albedo warming instead
        (in place, on open land)."""
        g, t = self.g, self.tune
        args = (g.lat, self.tilt, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"])
        sc = climate.snow_cover(*args, t)
        new_j, new_n = climate.albedo_warming(*args, self.raw, t, sc=sc)
        old_j, old_n = climate.albedo_warming(*args, self.neutral if old is None else old, t, sc=sc)
        north = g.lat >= 0
        dj, dn = new_j - old_j, new_n - old_n
        d_sum, d_win = np.where(north, dj, dn), np.where(north, dn, dj)
        c["t_warm"] = np.where(open_, c["t_warm"] + d_sum, c["t_warm"])
        c["t_cold"] = np.where(open_, c["t_cold"] + d_win, c["t_cold"])
        c["temp"] = np.where(open_, c["temp"] + 0.5 * (d_sum + d_win), c["temp"])

    def step(self, t_kyr: float, c: dict, surf: np.ndarray, grounded: np.ndarray, H: np.ndarray, co2_c: float,
             compute) -> dict:
        """The plants on the full climate c (computed with feedback(grounded)), and c corrected to them.
        At the start (no plants yet) they are grown to balance first; compute(veg) recomputes the climate."""
        H_g = np.where(grounded, H, 0.0)
        open_ = (surf > 0) & ~grounded
        if self.raw is None:  # the start: the full model, the climate again with it, then the cheap one
            self.land0 = surf > 0
            self.grow(c, surf, H_g, co2_c, full=True)
            self.mig, self.t_last = self._last["eq"]["nu_raw"], t_kyr
            self.tree_at[round(t_kyr, 3)] = self.pct(self._last["pot"], self._last["eq"]["nu"])
            c = compute(self.feedback(grounded))
            old = self.raw
            self.grow(c, surf, H_g, co2_c)
            self.correct(c, open_, old)
            self.ref = self.raw
        else:
            old = self.raw
            self.grow(c, surf, H_g, co2_c)
            self.migrate(t_kyr)
            self.correct(c, open_, _where(grounded, self.neutral, old))
        self.measure(t_kyr, c, open_)
        return c

    def measure(self, t_kyr: float, c: dict, open_: np.ndarray) -> None:
        """The global term (W/m2 at the top of the atmosphere, its C) and the local one (C, planet mean),
        the plants' change since the start at the current snow, by latitude belt."""
        g, t, area = self.g, self.tune, self.area
        A = float(area.sum())
        args = (g.lat, self.tilt, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"])
        sc = climate.snow_cover(*args, t)
        da = climate.surface_albedo(sc, self.raw, t) - climate.surface_albedo(sc, self.ref, t)
        # (only the start's land: a shelf the falling sea lays bare replaces the darker sea, not bare ground;
        # that is the sea level's albedo, not the plants')
        dF = np.where(open_ & self.land0, -self.p.veg_toa * (da * self.sun).mean(0), 0.0)  # W/m2 per cell
        F = float((dF * area).sum()) / A
        self.dT_target = self.p.veg_lambda * F if self.p.veg == "on" else 0.0
        nj, nn = climate.albedo_warming(*args, self.raw, t, sc=sc)
        rj, rn = climate.albedo_warming(*args, self.ref, t, sc=sc)
        loc = np.where(open_ & self.land0, 0.5 * (nj + nn - rj - rn), 0.0)
        belts = {f"{a}..{b}": round(float((dF * area)[(g.lat >= a) & (g.lat < b)].sum()) / A, 3) for a, b in BELTS}
        nh = open_ & (g.lat >= 45)
        self.series.append({"t": t_kyr, "F_wm2": round(F, 3), "dT_global": round(self.dT_target, 3),
                            "dT_local_mean": round(float((loc * area).sum()) / A, 3),
                            "dT_local_nh45_land": round(float((loc * area)[nh].sum() / max(area[nh].sum(), 1.0)), 3),
                            "F_belts": belts,
                            "tree_nh45_mkm2": round(float((self.tree * area)[nh].sum()) / 1e12, 2)})
