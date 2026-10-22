"""The slowly refreshed climate fields: a full climate.compute every
climate_every kyr, blended between refreshes."""

from __future__ import annotations

import time

import numpy as np

from .. import climate
from .. import icemass as M
from ..grid import Grid
from .params import RHO_I, RHO_W, TZParams
from .plants import Plants


class ClimateFields:
    """The current monthly-climate fields (t_mean, half, p_jul, p_jan, s0,
    dTg0, sst_w ...: self[name]), the overturning's state and the fresh-water
    bookkeeping between full climates."""

    def __init__(self, g: Grid, src: dict, p: TZParams, tilt: float, dT_run: float, area: np.ndarray,
                 H0: np.ndarray):
        self.g, self.src, self.p, self.tilt, self.dT_run, self.area = g, src, p, tilt, dT_run, area
        self.f: dict = {}
        self.compute_s = 0.0
        self._melt_ref = {"H": H0.copy(), "t": 0.0}
        self.plants = Plants(g, src, p, tilt, area)

    def __getitem__(self, key: str):
        return self.f[key]

    def meltwater(self, t_kyr: float, H: np.ndarray):
        """Fresh water from the ice the sheets have lost since the last full
        climate (m/yr of water per cell, where they thinned; the net loss
        over the planet, nothing while they grow). The ocean's overturning
        feels it (climate.compute's melt)."""
        ref, area = self._melt_ref, self.area
        yrs = (t_kyr - ref["t"]) * 1000.0
        dv = (H - ref["H"]) * area
        ref.update(H=H.copy(), t=t_kyr)
        loss = np.maximum(-dv, 0.0)
        net = max(-float(dv.sum()), 0.0)
        if yrs <= 0 or net <= 0 or loss.sum() <= 0:
            return None
        return RHO_I / RHO_W * loss * (net / loss.sum()) / area / yrs

    def refresh(self, t_kyr: float, dTg: float, surf: np.ndarray, grounded: np.ndarray, H: np.ndarray,
                co2: float = 0.0, cold: np.ndarray | None = None) -> None:
        """A full climate on the current surface and global temperature, and the plants grown on it
        (plants.py; co2: the CO2 term of dTg, C; cold: the share of each ice cell's summer its surface
        stays frozen, the share of its air that is the sheet's cold air: icemass.air_mass)."""
        fields_, g, pl = self.f, self.g, self.plants
        melt, moc0 = self.meltwater(t_kyr, H), fields_.get("moc")

        def compute(veg):
            t0 = time.time()
            # (the overturning carries on from the last full climate's state; the air over the ice is the
            # sheets' own, carried along the winds: ice_air)
            c = climate.compute(g, surf, self.dT_run + dTg, self.tilt, melt=melt, moc_start=moc0,
                                ice_air=np.where(grounded, H, 0.0), veg=veg, ice_cold=cold)
            self.compute_s += time.time() - t0
            return c

        c = compute(pl.feedback(grounded) if pl.on else None)
        if pl.on:
            c = pl.step(t_kyr, c, surf, grounded, H, co2, compute)
        fields_["moc"] = c["moc_state"]
        fields_["moc_sv"] = (float(c["overturning"][g.lat >= 0].sum()), float(c["overturning"][g.lat < 0].sum()))
        if self.p.baseline == "obs" and "bias" not in fields_:
            fields_["bias"] = self.obs_bias(c, H)
        tw, tc, pj, pn = c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"]
        gw, gc = c["ground"][0], c["ground"][1]
        if "bias" in fields_:
            b = fields_["bias"]
            tw, tc, pj, pn = tw + b["t_warm"], tc + b["t_cold"], pj * b["p_jul"], pn * b["p_jan"]
            gw, gc = gw + b["t_warm"], gc + b["t_cold"]
        new = dict(t_mean=0.5 * (tw + tc), half=0.5 * np.maximum(tw - tc, 0), p_jul=pj, p_jan=pn,
                   # (each cell's own response to the orbit: its bare ground's or the sea's seasons, PW-459)
                   k_own=M.seasonal_k(g.lat, gw, gc, self.tilt),
                   # (how much of the air over each ice cell is the sheets' own, as the climate just counted it)
                   air=M.air_mass(g, np.where(grounded, H, 0.0), cold=cold),
                   s0=np.maximum(surf, 0), dTg0=dTg, sst_w=np.minimum(c["sst_jul"], c["sst_jan"]),
                   # (the cold half-year's wind, the dust's: January in the north, July in the south)
                   wind_w=np.where((g.lat >= 0)[:, None], c["wind_jan"], c["wind_jul"]))
        # the steps until the next refresh blend from the last one to this one, so the climate
        # (snowfall above all) changes smoothly instead of jumping at each refresh
        fields_["prev"], fields_["next"] = fields_.get("next", new), new
        fields_.update(new)

    def blend(self, w: float) -> None:
        """The climate fields a share w (0..1) of the way from the last full climate to the newest."""
        a, b = self.f["prev"], self.f["next"]
        self.f.update({k: (1 - w) * a[k] + w * b[k] for k in b})

    def obs_bias(self, c: dict, H: np.ndarray) -> dict:
        """Observed minus modelled climate at the start (temperatures: a
        difference, rain: a ratio), where observed and not under the
        starting ice (the model's own ice-sheet climate is used there)."""
        if "obs" not in self.src:
            raise SystemExit("baseline=obs needs observations (only the Earth source has them)")
        o, w = self.src["obs"], 1 - np.clip(H / self.p.albedo_h, 0, 1)
        b = {}
        for k in ("t_warm", "t_cold"):
            b[k] = np.where(np.isfinite(o[k]), o[k] - c[k], 0.0) * w
        for k in ("p_jul", "p_jan"):
            r = np.clip(o[k] / np.maximum(c[k], 1.0), 0.2, 5.0)
            b[k] = np.where(np.isfinite(o[k]), r ** w, 1.0)
        return b
