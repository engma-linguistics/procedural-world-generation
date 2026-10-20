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
The rivers' floodplains aren't modelled here (no flow: the wetland share comes from the lakes-free ground).
"""

from __future__ import annotations

import time

import numpy as np

from .. import climate
from .. import vegetation as V
from ..grid import Grid
from ..tectonics.params import Params
from .params import TZParams

# latitude belts of the diagnostics (deg; north to south)
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
        self.co2_0 = float(v.get("co2", 0.0))
        self.unlocked = v.get("unlocked")
        # the run's CO2 index is its temperature term over co2_sensitivity (earth.global_temperature)
        self.co2_sens = float(src.get("params", {}).get("co2_sensitivity", Params().co2_sensitivity))
        self.tune = climate.TUNE
        self.neutral = neutral(g.n, self.tune)
        self.raw = None  # vegetation.feedback of the current plants (None: none grown yet)
        self.ref = None  # ... and of the start's
        self.land0 = None  # the start's land (ice included)
        self.dT_target = 0.0  # C: the global term's target (Forcing.veg)
        self.series: list = []
        self.time_s = 0.0
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
                    co2=self.co2_0 + co2_c / self.co2_sens, unlocked=self.unlocked, cheap=not full)
        self.nu, self.lai = v["eq"]["nu"], v["pot"]["lai"]
        self.raw = V.feedback(self.nu, self.lai)
        self.tree = v["sm"]["tree"]
        self.time_s += time.time() - t0

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
            c = compute(self.feedback(grounded))
            old = self.raw
            self.grow(c, surf, H_g, co2_c)
            self.correct(c, open_, old)
            self.ref = self.raw
        else:
            old = self.raw
            self.grow(c, surf, H_g, co2_c)
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
