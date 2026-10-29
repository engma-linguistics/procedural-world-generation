"""Opt-in long-run diagnostics for the ice and the global temperature (PW-555 stage 0).

Off unless a caller sets `sim.diag = Recorder(...)` (tools/ice_diag.py does). It only reads the
simulation's state, never changes it and draws no random numbers, so a run with it on is bit-identical
to one without (tests/test_ice_diag.py). It records:

- every step (`steps`): the global temperature's parts (earth.global_temperature): dT, its target and
  the terms in it (the drift, the CO2 term as it is counted, levelling off toward +-CO2_MAX, and what it would be
  without that, the ice albedo term, the offset), the CO2 index, the volcanic source and the weathering
  sink against their references, the share of the land under ice (which doesn't weather), sea
  level and its two parts (the ice's, sea_ice, and the ocean basins', sea_tect), the iced share;
- every climate update (`updates`): the global climate (mean temperature, rain, rain on the ice,
  frozen sea share, the land poleward of the snowline, the land's Koppen B and hot-desert shares and
  mean rain), how many passes the ice's fixed point took,
  and every ice sheet's budget at the ice it settled to: area, volume (m of sea level), mean and
  highest surface, centroid latitude and its most equatorward cell, the snow it gains where its
  balance is positive, the melt where it is negative, what the sea takes at its coast
  (earth.coast_cost), and the net. A sheet in deficit (net < 0) that the run keeps is a sheet that the
  equilibrium rule holds up by its own height, not by its budget (docs/review/ice-v2-review.md, root
  cause 2): those are what keep a cold era from ending;
- optionally (`fields=True`) the fields of every climate update (ice, surface mass balance, warmest
  month on the bare ground, rain), as float16, for maps.

Units: budgets in m of sea level per kyr (positive = the sea falls), volumes in m of sea level, as
sea_ice: -0.9 x the ice's volume over the ocean's area. Cost: one extra mass balance per climate
update (~0.3-1 s at L6); the steps' records are a few numbers.
"""

from __future__ import annotations

import numpy as np

from .. import climate, icemass, kernels
from ..geo import R_KM
from . import output

ARID = [k for k, c, _, _ in climate.KOPPEN if c.startswith("B")]  # Koppen group B ids
BWH = next(k for k, c, _, _ in climate.KOPPEN if c == "BWh")
TOP_SHEETS = 12  # sheets recorded per update (the largest by area); the rest are summed as "other"


class Recorder:
    def __init__(self, fields: bool = False, top: int = TOP_SHEETS):
        self.fields_on, self.top = fields, top
        self.steps: list[dict] = []
        self.updates: list[dict] = []
        self.fields: dict[str, list] = {"t": [], "ice": [], "smb": [], "t_warm": [], "precip": []}

    def as_dict(self) -> dict:
        return {"steps": self.steps, "updates": self.updates}

    # ----------------------------------------------------------- every step
    def temperature(self, sim, source, sink, ice_frac, co2_term, albedo_term, target) -> None:
        """From earth.global_temperature, with its own numbers: this step's raw volcanic source and
        weathering sink (model units), the iced share it counted, the CO2 term as counted (clipped)
        and the ice albedo term (C, negative = cooling), and the target dT relaxes toward."""
        from .earth import earth_ice, ghg_conc, ghg_forcing, ghg_icefree, star_forcing
        p = sim.params
        rel = (sim.rates / sim.refs) if sim.rates is not None else np.ones(2)
        free = ghg_icefree(sim, ice_frac, earth_ice(sim.grid.level))
        self._pending = {
            "t": round(float(sim.t), 3), "dT": round(float(sim.dT), 3), "target": round(float(target), 3),
            "drift": round(float(sim.drift), 3), "co2": round(float(sim.co2), 3), "co2_term": round(float(co2_term), 3),
            "co2_term_free": round(p.co2_sensitivity / np.log(2.0) * float(sim.co2), 3), "albedo_term": round(float(albedo_term), 3),
            "offset": p.climate_offset,
            "star": round(star_forcing(p, sim.t) + float(sim.star_ctl), 3), "star_ctl": round(float(sim.star_ctl), 3),
            "ghg": round(ghg_forcing(p, sim.t, float(sim.dT), free), 3),
            "ch4_ppb": round(ghg_conc(p, sim.t, float(sim.dT), free)[0], 1),
            "ice_share": round(float(sim.ice_share if sim.ice_share is not None else 0.0), 3), "source_raw": float(source), "sink_raw": float(sink),
            "plume_src": round(float(getattr(sim, "plume_src", 0.0)), 6),
            "src": round(float(rel[0]), 4), "sink": round(float(rel[1]), 4), "ice_frac": round(float(ice_frac), 4),
            **self._sink_parts(sim)}

    @staticmethod
    def _sink_parts(sim) -> dict:
        """The weathering sink split into its parts (PW-572), so that sink = supply x temperature factor x
        plant factor exactly: the ice-free land's share of the surface (w_area), the erosion supply from
        it (w_supply, model units, as sink_raw), the supply-weighted plant factor (w_plant) and the
        temperature factor weighted by supply and plants (w_temp); and, to see what the factors read, the
        supply-weighted local temperature (w_T, C) and runoff (w_q, mm/yr) and the mean erosion rate of
        the eroding land (w_rate, km/Myr = mm/yr). Also the sink's bare-ground share (w_bare), its CO2
        log-slope (w_a) and, in the spin-up, the supply-weighted plant factor of the reference's potential
        vegetation (w_pot)."""
        from . import earth
        land = sim.land()
        w, supply, warm, plants, bare = earth.weathering(sim, land)
        s, sp = float(supply.sum()), float((supply * plants).sum())
        free = land & (sim.ice <= 0)
        out = {"w_area": round(float(free.mean()), 4), "w_supply": s / sim.scale**2,
               "w_plant": round(sp / s, 4) if s > 0 else None, "w_temp": round(float(w.sum()) / sp, 4) if sp > 0 else None}
        if w.sum() > 0:  # the sink's share on bare ground and its CO2 log-slope there (earth.co2_law, v1-finish-11)
            out["w_bare"] = round(float(bare.sum() / w.sum()), 4)
            out["w_a"] = round(earth.co2_slope(float(np.exp(sim.co2)), out["w_bare"]), 4)
        if sim.npp_pot is not None and s > 0:  # (spin-up: the reference's potential plants)
            out["w_pot"] = round(float((supply * earth.plant_factor(sim.npp_pot)).sum()) / s, 4)
        if s > 0 and sim.temp is not None:
            out["w_T"] = round(float((supply * sim.temp).sum()) / s, 2)
            out["w_q"] = round(float((supply * sim.runoff).sum()) / s, 1) if sim.runoff is not None else None
        out["w_rate"] = round(s / max(int(free.sum()), 1) / sim.dt_now, 5)
        return out

    def step(self, sim) -> None:
        """At the end of each step (the caller's on_step): the step's temperature record plus the
        sea level as the step left it and the land under ice (which doesn't weather)."""
        land = sim.land()
        iced_land = float((land & (sim.ice > 0)).sum()) / max(int(land.sum()), 1)
        rec = dict(getattr(self, "_pending", None) or {"t": round(float(sim.t), 3)})
        rec.update({"dT_end": round(float(sim.dT), 3), "iced_land": round(iced_land, 4),
                    "sea_level": round(float(sim.sea_level), 2), "sea_ice": round(float(sim.sea_ice), 2),
                    "sea_tect": round(float(sim.sea_tect), 2), "sea_cont": round(float(sim.sea_cont), 2),
                    "land": round(float(land.mean()), 4)})
        rec.update(output.habitability(sim))  # (what the finish moment reads: highlights.finish_moment, PW-866)
        self._pending = None
        self.steps.append(rec)

    # ----------------------------------------------------- climate updates
    def climate_update(self, sim, land, e, c, marine, info) -> None:
        """After earth.ice_sheets: land, e (the bed's land view and height), c (climate.compute's
        result), marine (earth.marine_view), info (ice_sheets' info: passes)."""
        from . import earth
        g = sim.grid
        ice = np.where(land, sim.ice, 0.0)
        area_km2 = sim.cell_area * R_KM**2
        ocean_km2 = max(float((~land).sum()) * area_km2, 1.0)
        sle = -0.9 / ocean_km2 * area_km2  # m of sea level per m of ice on one cell (negative: the sea falls)
        t_warm, t_cold, _ = c["ground"]
        iced = ice > 0
        rec = {"t": round(float(sim.t), 3), "dT": round(float(sim.dT), 3), "passes": int(info.get("passes", 0)),
               "temp": round(float(np.mean(sim.temp)), 3), "precip": round(float(np.mean(sim.precip)), 1),
               "precip_ice": round(float(sim.precip[iced].mean()), 1) if iced.any() else 0.0,
               "sea_frozen": round(float(((~land) & (c["sea_ice_growth"] > 0.05)).sum()) / max(int((~land).sum()), 1), 4),
               "sea_ice": round(float(sim.sea_ice), 2), "sea_tect": round(float(sim.sea_tect), 2),
               "iced_lat_min": round(float(np.abs(g.lat[iced]).min()), 2) if iced.any() else None,
               "iced_lat_max": round(float(np.abs(g.lat[iced]).max()), 2) if iced.any() else None}
        # the plants at the last update (one climate step behind): tree cover over land, and over the wet
        # equatorial lowland (|lat| < 10 deg, > 2000 mm/yr, below 500 m: the hard check of PW-806/812)
        tc = np.asarray(sim.tree_cover, float)
        wet = output.wet_eq_lowland(g.lat, land, sim.precip, e)
        rec["trees"] = round(100 * float(tc[land].mean()), 2) if land.any() else 0.0
        rec["wet_eq_trees"] = round(100 * float(tc[wet].mean()), 2) if wet.any() else None
        rec["wet_eq_cells"] = int(wet.sum())
        rec["pco2"] = round(float(climate.pco2(sim.co2)), 1)
        # the dry land (PW-015): Koppen B and hot desert (BWh) shares of the land, and the land's mean rain
        kp = climate.koppen(e, sim.temp, sim.t_warm, sim.t_cold, sim.precip, sim.p_jul, sim.p_jan, g.lat, sim.ice)[land]
        rec["arid_pct"] = round(100 * float(np.isin(kp, ARID).mean()), 2) if land.any() else None
        rec["bwh_pct"] = round(100 * float((kp == BWH).mean()), 2) if land.any() else None
        rec["land_precip"] = round(float(sim.precip[land].mean()), 1) if land.any() else None
        # land poleward of the snowline, ice-free and iced (the glacial index's cooling share, PW-538)
        smb0, _ = icemass.balance(g.lat, land, t_warm, t_cold, sim.p_jul, sim.p_jan, 0.0, 0.0, tilt=sim.params.tilt)
        rec["snow_land"] = round(float((land & (smb0 > 0)).sum()) / max(int(land.sum()), 1), 4)
        rec["snow_land_free"] = round(float((land & (smb0 > 0) & ~iced).sum()) / max(int(land.sum()), 1), 4)
        sheets = []
        if iced.any():
            cover = icemass.sheet_cover(g, ice)
            smb, _ = icemass.balance(g.lat, land, t_warm, t_cold, sim.p_jul, sim.p_jan, ice, cover,
                                     tilt=sim.params.tilt)
            calve, _ = earth.coast_cost(sim, land, e, marine)
            lab, nk = kernels.components(iced, g.nbr_off, g.nbr_idx)
            k = np.maximum(lab, 0)
            w = iced.astype(float)

            def tot(f):
                return np.bincount(k, weights=f * w, minlength=nk)

            # m/yr of ice x cells -> m of sea level per kyr (x 1000 yr), signs: + = the sea falls
            to_sl = -sle * 1000.0 * 0.917  # (smb is m of ice: x 0.917 to water, as the sea's -0.9)
            acc, mel, sea = tot(np.maximum(smb, 0)) * to_sl, tot(np.maximum(-smb, 0)) * to_sl, tot(calve) * to_sl
            cnt = tot(np.ones(g.n))
            vol = tot(ice) * -sle
            lat = tot(g.lat) / np.maximum(cnt, 1)
            surf = np.where(iced, e + ice, -np.inf)
            hmax = np.full(nk, -np.inf)
            np.maximum.at(hmax, k[iced], surf[iced])
            latmin = np.full(nk, 90.0)
            np.minimum.at(latmin, k[iced], np.abs(g.lat[iced]))
            msurf = tot(np.where(iced, e + ice, 0.0)) / np.maximum(cnt, 1)
            order = np.argsort(-cnt)
            for j in order[:self.top]:
                sheets.append({"cells": int(cnt[j]), "area_pct_land": round(100 * cnt[j] / max(int(land.sum()), 1), 2),
                               "vol_m": round(float(vol[j]), 2), "lat": round(float(lat[j]), 1),
                               "lat_min": round(float(latmin[j]), 1), "surf_mean": round(float(msurf[j])),
                               "surf_max": round(float(hmax[j])), "acc": round(float(acc[j]), 4),
                               "melt": round(float(mel[j]), 4), "sea": round(float(sea[j]), 4),
                               "net": round(float(acc[j] - mel[j] - sea[j]), 4)})
            rest = order[self.top:]
            rec["other"] = {"sheets": int(len(rest)), "vol_m": round(float(vol[rest].sum()), 2),
                            "net": round(float((acc - mel - sea)[rest].sum()), 4)}
            rec["budget"] = {"acc": round(float(acc.sum()), 4), "melt": round(float(mel.sum()), 4),
                             "sea": round(float(sea.sum()), 4), "net": round(float((acc - mel - sea).sum()), 4),
                             "deficit_vol_m": round(float(vol[(acc - mel - sea) < 0].sum()), 2)}
            if self.fields_on:
                self._fields(sim, ice, smb, t_warm)
        elif self.fields_on:
            self._fields(sim, ice, np.zeros(g.n), t_warm)
        rec["sheets"] = sheets
        self.updates.append(rec)

    def _fields(self, sim, ice, smb, t_warm):
        f = self.fields
        f["t"].append(float(sim.t))
        f["ice"].append(ice.astype(np.float16))
        f["smb"].append(np.asarray(smb, float).astype(np.float16))
        f["t_warm"].append(np.asarray(t_warm, float).astype(np.float16))
        f["precip"].append(np.asarray(sim.precip, float).astype(np.float16))

    def save_fields(self, path) -> None:
        if self.fields["t"]:
            np.savez_compressed(path, **{k: np.asarray(v) for k, v in self.fields.items()})
