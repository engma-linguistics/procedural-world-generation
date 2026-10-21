"""The stepping loop of the time zoom (see the package docstring for the model).

simulate() builds a _Sim and runs, per step:

  1. forcing:   orbit -> insolation anomaly; Forcing.update -> global dT (the glacial index's cooling)
  2. climate:   a full climate every climate_every kyr, blended in between
  3. surface:   the ice surface's climate (prepare_surface), one year of mass balance (year)
  4. record:    a frame every `every` kyr
  5. dynamics:  new-ice balance (new_ice_rates), balance + flow (balance_and_flow),
                glacial carving (carve), the sea (sea: shelves, calving), isostasy, sea level
"""

from __future__ import annotations

import math
import time
from dataclasses import asdict

import numpy as np

from .. import climate
from .. import icemass as M
from .. import store as S
from ..grid import Grid
from ..orbit import BAND_DEG, BAND_LAT, insolation, orbit_at, orbit_phases, reference_orbit
from ..tectonics.isostasy import ice_load
from .cycle import NAMES, Index, cooling, cycling_latitude, snowline_land
from .events import cycling_ice_sun
from .fields import ClimateFields
from .forcing import Forcing, orbit_k
from .geometry import geometry
from .ice import above_flotation, shelf_cover, shelf_step, shelf_viable
from .kernels import climate_step, dilate, glacial_erosion, sia_flow
from ..surface import COVER_SHOWS
from .params import LAYERS, RHO_I, RHO_W, TZParams


class _Sim:
    """The state of one time zoom and its steps. Arrays (H, bed, smb, ...)
    are updated in place; sl (m, sea level change since the start) is rebound."""

    def __init__(self, src: dict, kyr: float, step: float, every: float, p: TZParams):
        self.src, self.p, self.step = src, p, step
        g: Grid = src["grid"]
        self.g, n = g, g.n
        self.n = n
        self.G = geometry(g)
        self.area = self.G["area"]
        self.north = g.lat >= 0
        self.band = np.clip(((g.lat + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
        self.tilt = float(src["tilt"])
        earth = src["source_run"] == "earth"
        self.ph = orbit_phases(p, int(src["seed"]) * 1000 + int(round(src["at"])), earth)
        self.ref_orb = reference_orbit(p, self.tilt, self.ph, earth)
        self.q_ref = insolation(*self.ref_orb)
        # polar amplification of a global temperature change (as climate.compute: 0.5x tropics .. 1.5x poles)
        self.amp = climate.temperature(g, np.zeros(n), 0.5, 1.5)
        self.flt = 1 - RHO_I / RHO_W
        self.gamma = 2 * p.flow_a * p.enhancement * (RHO_I * 9.81) ** 3 / 5
        # an ice shelf's spreading, h' = -c h^4 (Weertman 1957), confined by its buttressing (strain rate x (1 - K)^3)
        self.c_shelf = p.flow_a * (RHO_I * 9.81 * self.flt / 4) ** 3 * (1 - p.buttress) ** 3

        # state: bedrock relative to the starting sea level, its ice-free rest
        # height (the start is taken as isostatically settled), ice, sea level
        elev0 = np.asarray(src["elev"], float)
        self.H = np.maximum(np.asarray(src["ice"], float), 0.0)  # (grounded: also where its load pressed the bed below the sea)
        self.bed = elev0.copy()
        self.bed_rest = self.bed + self.load(np.where(self.bed + self.H > self.flt * self.H, self.H, 0.0))  # (a shelf doesn't load it)
        self.sl = 0.0
        self.ocean_area = float(self.area[(elev0 <= 0) & (self.H <= 0)].sum())
        self.V0 = float((self.H * self.area).sum())
        self.bed0 = self.bed.copy()
        # glacial carving (PW-037): m of bed eroded and of till dropped so far, the debris in the ice (m of
        # rock per cell), the bed's settled response to the net rock removed (m, flexure); per step: the
        # erosion, sia_flow's speed x time (m; raw and at most the bed's yield stress), the debris melt
        # dropped within the flow, the thawed share of the bed; kyr the bed was thawed under the ice, km it slid
        self.rock = src.get("bedrock") or {"cover_m": np.zeros(n), "erod_cover": np.ones(n), "erod_base": np.ones(n)}
        (self.cut, self.till, self.debris, self.rock_iso, self.cut_step, self.u_dt, self.ul_dt, self.w_dt,
         self.dropped, self.wet, self.wet_kyr, self.slide_km) = (np.zeros(n) for _ in range(12))
        self.Vaf0 = self.above_flotation(0.0)
        self.dT_run = float(src["dT"])

        self.fields = ClimateFields(g, src, p, self.tilt, self.dT_run, self.area, self.H)

        self.out = {k: [] for k in LAYERS}
        self.frames, self.series, self.flows = [], [], []  # flows: accumulation, ablation, calving, NH net (Gt/yr) per step
        self.budget = {"smb": 0.0, "calved": 0.0, "shelf_melt": 0.0}  # m3 of ice gained / lost (calved: all the sea
        # took, the shelves' melt from below included)
        self.n_steps = int(round(kyr / step))
        # the glacial index (cycle.py): set up after the first full climate (setup_index); I is 0 until then
        self.forcing = Forcing(p, step)
        self.index: Index | None = None
        self.glacial: dict = {}
        self.s_no = 0
        self.keep = max(1, int(round(every / step)))
        self.refresh = max(1, int(round(p.climate_every / step)))
        # the year's results (climate_step's outputs; f_snow: summer brightness)
        self.smb, self.t_ann, self.t_warm, self.t_cold, self.p_scale, self.f_snow = (np.zeros(n) for _ in range(6))
        self.nsub_total = 0
        self.i65 = int(np.argmin(np.abs(BAND_LAT - 65)))
        self.anchor = np.zeros(n)  # C, per-cell correction of the ice surface's climate (see start_anchor)

    # ---- the state ------------------------------------------------------

    def load(self, h):
        return ice_load(self.g, h, self.p.iso_ratio, self.p.flex_km)

    def above_flotation(self, sl):
        # (the reference bed moves with the carving: a deeper basin isn't sea water the ice holds)
        ref = self.bed0 + self.till - self.cut + self.rock_iso if self.p.carving else self.bed0
        return above_flotation(self.H, self.bed, ref, self.area, sl)

    def drop(self, x) -> None:
        """Debris x (m per cell) melts out of the ice onto the bed as till (already out of `debris`)."""
        self.till += x
        self.bed += x
        self.bed_rest += x

    def grounded_ice(self):
        H, bed = self.H, self.bed
        return np.where((H > 0) & (bed + H > self.sl + self.flt * H), H, 0.0)

    def grounded_surface(self):
        """Surface height above the current sea level (ice included where
        grounded; the sea floor elsewhere) and the grounded-ice mask."""
        H, bed = self.H, self.bed
        grounded = (H > 0) & (bed + H > self.sl + self.flt * H)
        surf = np.where(grounded, bed + H, bed) - self.sl
        return surf, grounded

    # ---- a step's climate -----------------------------------------------

    def prepare_surface(self, dTg: float) -> None:
        """The step's ice surface and its climate offsets (self.land, ice_g,
        bare_land, dt_wet, dt_base, f_ice, f_alb, damp)."""
        g, p, H, F = self.g, self.p, self.H, self.fields
        surf, grounded = self.grounded_surface()
        land = surf > 0
        self.land = land
        self.dt_wet = self.amp * (dTg - F["dTg0"])
        # A margin cell (ice next to ice-free land) is a slope from the bare edge up to its inner
        # neighbour: its snow and melt are those of the sheet's edge (edge_h thick, as the main run's
        # margins), not of its mean thickness (~1 km at ~110 km cells, the grid's cliff-like margin),
        # which would keep it as cold as the interior and let the sheet creep onto warm land.
        ice_g = np.where(grounded, H, 0.0)
        self.ice_g = ice_g
        self.bare_land = land & (ice_g <= 1.0)
        margin = (ice_g > 1.0) & (np.add.reduceat(self.bare_land[g.nbr_idx], g.nbr_off[:-1]) > 0)
        h_sfc = np.where(margin, np.minimum(ice_g, p.edge_h), ice_g)
        surf_eff = np.where(margin, surf - (ice_g - h_sfc), surf)
        self.dt_base = -climate.LAPSE * (np.maximum(surf_eff, 0) - F["s0"]) + self.dt_wet
        self.f_ice = np.clip(h_sfc / p.albedo_h, 0, 1)
        self.f_alb = np.clip(ice_g / p.snow_h, 0, 1)  # perennial snow is bright from the start
        # (the ice surface's own summer damping, icemass.sheet_cover; on ice only: bare ground's seasonal
        # snow gets none, as the run's new-cap rule, PW-275)
        self.damp = p.summer_damp * np.where(ice_g > 1.0, M.sheet_cover(g, ice_g), 0.0)

    def year(self, dt_b, dq_) -> None:
        """One (orbit-averaged) year of the surface mass balance and temperatures at every cell."""
        p, F = self.p, self.fields
        # bright snow absorbs little of an insolation change, but the air over it also brings
        # what the surroundings absorbed: the response is mixed over an air mass (orbit_k)
        self.k_orb = k_orb = orbit_k(self.g, self.land, self.f_snow, p)  # (also the new front's, new_ice_rates)
        # (the start's correction of the ice-surface climate, only where ice lies: start_anchor)
        climate_step(self.land, self.north, F["t_mean"] + self.anchor * self.f_alb, F["half"], F["p_jul"],
                     F["p_jan"], dt_b, self.dt_wet, k_orb, self.band, dq_, self.f_ice, self.f_alb,
                     p.ice_cool, self.damp, p.melt_hold, p.bare_share, p.snow_w,
                     p.pdd_sigma, p.ddf_snow, p.ddf_ice, p.refreeze, p.precip_k, self.smb, self.t_ann,
                     self.t_warm, self.t_cold, self.p_scale, self.f_snow)

    def setup_index(self) -> None:
        """The glacial index (cycle.py) from the first full climate: the land poleward of the planet's
        snowline sets the cycling latitude (whose summer sun paces the index), the glacial cooling and the
        glacial maximum's sea-level target (a diagnostic: sheet_h of ice over that land)."""
        p, g, F, area = self.p, self.g, self.fields, self.area
        surf, grounded = self.grounded_surface()
        t_sl = F["t_mean"] + climate.LAPSE * np.maximum(surf, 0)
        cold = snowline_land(surf > 0, np.where(grounded, self.H, 0.0), t_sl)
        share = float(area[cold].sum() / area.sum())
        self.index = Index(p, self.step, self.n_steps, self.tilt, self.ph, cycling_latitude(g.lat, area, cold))
        self.forcing.index, self.forcing.cool = self.index, cooling(p, share)
        target = p.sheet_h * RHO_I / RHO_W * float(area[cold].sum()) / max(self.ocean_area, 1.0)
        self.glacial = {"snowline_land_share": round(share, 4), "cooling_c": round(self.forcing.cool, 2),
                        "target_m": round(target, 1)}

    def start_anchor(self, iced) -> np.ndarray:
        """A cooling (C, all year) of the ice surface's climate on the
        starting ice and a few rings around it (p.anchor). It corrects the
        climate model over ice, so it applies where ice lies (in full from
        snow_h): it goes with the ice when that melts back and comes back
        where the ice readvances (PW-035: it used to cool the cell for the
        whole time zoom, so bare ground left by the starting ice stayed
        cooled, and ring cells were cooled before any ice reached them):
          obs      Earth: the model's warmest month on the ice (its bare
                   climate under icemass's ice surface) cooled to the
                   observed one where that is colder (the climate model's
                   ice-free summers are far too warm over Antarctica, ~+6 C
                   at its coast against ~-5 C observed, PW-039), so the
                   real sheets keep their real margins (Greenland's
                   ablation zone stays);
          balance  the smallest cooling (0.5 C steps) that lets snow outlast
                   the summer on every starting ice cell (no ablation zone);
          none     a run's ice is already this mass balance's extent at the
                   mean orbit (earth.ice_sheets).
        At most anchor_max. Needs the step's surface (prepare_surface)."""
        p, g, src, n, anchor = self.p, self.g, self.src, self.n, self.anchor
        dt_b = self.dt_base
        mode = p.anchor if p.anchor != "auto" else ("obs" if "obs" in src else "none")
        z = np.zeros_like(self.q_ref)
        if mode == "none" or not iced.any():
            return np.zeros(n)
        if mode == "obs":
            if "obs" not in src:
                raise SystemExit("anchor=obs needs observations (only the Earth source has them)")
            self.year(dt_b, z)
            obs = src["obs"]["t_warm"]
            fix = iced & np.isfinite(obs)
            anchor[fix] = np.clip(obs[fix] - self.t_warm[fix], -p.anchor_max, 0.0)
        elif mode == "balance":
            todo = iced.copy()
            for off in np.arange(0.0, p.anchor_max + 1e-9, 0.5):
                anchor[todo] = -off  # (the cells still melting try the next step; rain isn't changed)
                self.year(dt_b, z)
                todo &= self.smb < 0
                if not todo.any():
                    break
        else:
            raise SystemExit(f"anchor must be obs, balance, none or auto, not {p.anchor!r}")
        # a climate bias is regional: spread it a few rings beyond the ice
        # (each new cell: the mean of its corrected neighbours), so ice
        # flowing out of its starting cells doesn't meet a different climate
        a = anchor.copy()
        has = iced.copy()
        src_ = g.nbr_src
        for _ in range(p.anchor_rings):
            tot = np.bincount(src_, weights=np.where(has, a, 0.0)[g.nbr_idx], minlength=n)
            cnt = np.bincount(src_, weights=has[g.nbr_idx].astype(float), minlength=n)
            new = ~has & (cnt > 0)
            a[new] = tot[new] / cnt[new]
            has |= new
        return a

    # ---- frames ---------------------------------------------------------

    def record(self, t_kyr, orb, dq65, dTg) -> None:
        F = self.fields
        surf, grounded = self.grounded_surface()
        land = surf > 0
        ice = np.where(grounded, self.H, 0.0)
        precip = 0.5 * (F["p_jul"] + F["p_jan"]) * self.p_scale
        k = climate.koppen(surf, self.t_ann, self.t_warm, self.t_cold, precip, F["p_jul"] * self.p_scale,
                           F["p_jan"] * self.p_scale, self.g.lat, np.where(land, ice, 0.0))
        for name, v in (("elevation", surf), ("ice", ice), ("temperature", self.t_ann), ("climate", k),
                        ("glacial_erosion", self.cut), ("glacial_till", self.till)):
            self.out[name].append(S.encode(v, LAYERS[name]))
        vol = float((self.H * self.area).sum())
        self.frames.append({"t": round(t_kyr, 3), "stats": self.stats(t_kyr, surf, ice, vol, orb, dq65, dTg)})

    def stats(self, t_kyr, surf, ice, vol, orb, dq65, dTg) -> dict:
        src, sl, F = self.src, self.sl, self.fields
        land = surf > 0
        lab, nlab = self.g.components(land)
        sizes = np.bincount(lab[lab >= 0], minlength=1) if nlab else np.array([0])
        return {"t": round(t_kyr, 3), "plates": int(len(np.unique(src["static"]["plate"]))),
                "land_pct": round(100 * land.mean(), 1), "landmasses": int((sizes >= 3).sum()),
                "largest_landmass_pct": round(100 * sizes.max() / self.n, 1), "max_elev_m": int(surf.max()),
                "global_temp_c": round(14.5 + self.dT_run + dTg, 2),
                "sea_level_m": round(src["sea_level"] + sl, 1), "sea_level_change_m": round(sl, 2),
                "ice_pct": round(100 * float((ice > 1).mean()), 2),
                "ice_volume_mkm3": round(vol / 1e15, 3),
                "ice_sea_equiv_mkm3": round(self.above_flotation(sl) / 1e15, 3),  # m3 of sea water the ice holds
                "max_ice_m": int(ice.max()),
                "obliquity": round(orb[0], 3), "eccentricity": round(orb[1], 4),
                "perihelion": round(orb[2], 1), "precession_index": round(orb[1] * math.sin(math.radians(orb[2])), 4),
                "insol_65n_jul_anom": round(dq65, 1), "dT_global": round(dTg, 2),
                "ice_age": NAMES[self.index.modes[self.s_no]] if self.index else NAMES[0],
                "glacial_index": round(self.forcing.I, 3),
                "overturning_north_sv": round(F["moc_sv"][0], 1),
                "overturning_south_sv": round(F["moc_sv"][1], 1),
                "mean_speed_cmyr": 0, "max_speed_cmyr": 0}

    # ---- a step's dynamics ----------------------------------------------

    def new_ice_rates(self, dq, dt):
        """The mass balance rate (m/yr) per cell, the cells the ice flows
        over or beside (near: 2 rings) and their indices."""
        g, p, n, F = self.g, self.p, self.n, self.fields
        land, north, band = self.land, self.north, self.band
        near = dilate(self.H > 0, g.nbr_off, g.nbr_idx, 2)
        active = np.flatnonzero(near)
        rate = np.where(land, self.smb, 0.0)
        # the bare land beside a sheet: the ice the flow brings onto it over the step is the sheet's new edge,
        # bright and edge_h high (as the main run tests a new margin, earth.ablation_zone), not bare ground
        # (PW-366: as bare ground's dark, low surface it melted as it arrived and the sheets couldn't advance)
        front = self.bare_land & dilate(self.ice_g > 1.0, g.nbr_off, g.nbr_idx, 1)
        if front.any():
            fi = np.flatnonzero(front)
            sub = [np.zeros(len(fi)) for _ in range(6)]
            climate_step(land[fi], north[fi], (F["t_mean"] + self.anchor)[fi], F["half"][fi],
                         F["p_jul"][fi], F["p_jan"][fi], self.dt_base[fi] - climate.LAPSE * p.edge_h,
                         self.dt_wet[fi], self.k_orb[fi], band[fi], dq,
                         np.full(len(fi), min(p.edge_h / p.albedo_h, 1.0)), np.ones(len(fi)), p.ice_cool,
                         p.summer_damp * M.sheet_cover(g, np.ones(n))[fi], p.melt_hold,
                         p.bare_share, p.snow_w, p.pdd_sigma, p.ddf_snow, p.ddf_ice, p.refreeze, p.precip_k, *sub)
            rate[fi] = sub[0]
        return rate, near, active

    def balance_and_flow(self, rate, near, active, dt):
        """1) mass balance (not below zero thickness) and 2) flow: on the ice and the rings around it the
        balance acts within the flow's sub-steps (sia_flow), so a margin's melt and the flow that feeds it
        act together; elsewhere (bare ground, a new snow cap) at once. Returns (dv: m3 of ice gained per
        cell, sea0: open sea or shelf at the step's start, H_pre: the ice before the shelves' step)."""
        g, p, H, bed, sl, flt, area, G = self.g, self.p, self.H, self.bed, self.sl, self.flt, self.area, self.G
        h_new = np.where(self.land & ~near, np.maximum(H + self.smb * dt, 0.0), H)
        dv = (h_new - H) * area
        H[:] = h_new
        sea0 = (sl - bed > 0) & ~((H > 0) & (bed + H > sl + flt * H))  # open sea or shelf at the step's start
        H_pre = H.copy()
        if len(active):
            # (a shelf holds back a grounded front's flow across its grounding line as it does its calving)
            gr0 = (H > 0) & ~sea0
            nb_sea0 = np.add.reduceat(sea0[g.nbr_idx], g.nbr_off[:-1]) > 0
            hold = p.buttress * shelf_cover(g, gr0 & nb_sea0, sea0, np.where(sea0, H, 0.0), p)
            applied = np.zeros(self.n)
            self.u_dt[:] = 0.0
            self.ul_dt[:] = 0.0
            self.w_dt[:] = 0.0
            self.dropped[:] = 0.0
            self.nsub_total += sia_flow(H, bed, sl, active, g.nbr_off, g.nbr_idx, G["dist"], G["elen"], G["ux"],
                                        G["uy"], G["uz"], area, self.gamma, p.d_cap, dt, p.cfl, flt, G["d2min"],
                                        hold, rate, applied, self.debris, self.u_dt, self.ul_dt, self.w_dt, p.tau_y,
                                        self.dropped)
            if p.carving:
                self.drop(self.dropped)
            dv += applied * area
            H_pre += applied  # (the shelf's inflow below is the flow's alone)
        self.budget["smb"] += float(dv.sum())
        return dv, sea0, H_pre

    def carve(self, active, dt) -> None:
        """2b) glacial carving (PW-037): the sliding ice erodes its bed (the cover, and till laid down before,
        while they last; then the basement) and takes the rock along (kernels.glacial_erosion)."""
        p, g, rock = self.p, self.g, self.rock
        soft = rock["cover_m"] + self.till - self.cut > 1000.0 * COVER_SHOWS
        glacial_erosion(self.H, self.bed, self.sl, self.flt, active, g.nbr_off, g.nbr_idx, self.ul_dt, self.w_dt, self.t_ann,
                        np.maximum(self.smb, 0.0), p.geo_flux, p.slide_share,
                        np.where(soft, rock["erod_cover"], rock["erod_base"]), p.glacial_k, p.glacial_l, p.adverse,
                        dt, p.calve_depth, self.cut_step, self.wet)
        e = self.cut_step[active]
        self.cut[active] += e
        self.debris[active] += e
        self.bed[active] -= e
        self.bed_rest[active] -= e
        self.wet_kyr[active] += self.wet[active] * self.step
        self.slide_km[active] += p.slide_share * self.wet[active] * self.ul_dt[active] / 1000.0

    def rock_isostasy(self) -> None:
        """The lithosphere's settled response to the rock the ice moved (relaxing like the ice load's)."""
        new = climate.smooth(self.g, self.p.rock_ratio * (self.cut - self.till), self.p.flex_km)
        self.bed_rest += new - self.rock_iso
        self.rock_iso[:] = new

    def sea(self, sea0, H_pre, dt):
        """3) the sea (PW-367): the ice the flow carried past the grounding line over the step is an ice
        shelf: it spreads (confined by the same buttressing it gives) and melts from below where the sea
        is warm; what then floats stays as a shelf where the air over it lets one stand, and breaks up
        elsewhere; grounded marine fronts calve where they face open water. Returns the ice lost (m per cell)."""
        g, p, H, bed, area, F = self.g, self.p, self.H, self.bed, self.area, self.fields
        depth = self.sl - bed
        lost = np.zeros(self.n)
        H3 = H.copy()  # (the debris in ice the sea takes, by melt, break-up or calving, drops to the sea floor there)
        sea0 &= (H_pre > 0) | (H > 0)  # (the sea cells with ice in them)
        if sea0.any():
            q = (H - H_pre) / dt
            # (the water under a shelf: the sea's winter surface water, which sinks under it; a cold sea's is at
            # freezing, so its shelf hardly melts)
            melt = p.melt_k * np.maximum(F["sst_w"] - climate.FREEZE, 0.0)
            h, out_, gone = shelf_step(H_pre[sea0], q[sea0], melt[sea0], self.c_shelf, dt)
            H[sea0] = h
            lost[sea0] += out_ + gone
            self.budget["shelf_melt"] += float((gone * area[sea0]).sum())
        floating = (H > 0) & (H * RHO_I < depth * RHO_W)
        stays = np.where(floating, shelf_viable(self.t_ann, p), 1.0)  # (t_ann: this step's year, over the sea too)
        lost += H * (1.0 - stays)
        H *= stays
        grounded = (H > 0) & ~floating
        marine = grounded & (depth > 0)
        if marine.any():
            sea = (depth > 0) & ~grounded
            nb_sea = np.add.reduceat(sea[g.nbr_idx], g.nbr_off[:-1]) > 0
            front = marine & (nb_sea | (depth > p.calve_depth))
            # (a front calves only where it faces open water, not a shelf)
            covered = shelf_cover(g, front, sea, np.where(sea, H, 0.0), p)
            frac = np.exp(-p.calving * (1.0 - covered) * depth * dt / np.sqrt(area))
            lost += np.where(front, H * (1 - frac), 0.0)
            H[front] *= frac[front]
        if p.carving:
            x = np.where(H < H3, self.debris * (1.0 - H / np.maximum(H3, 1e-9)), 0.0)
            self.debris -= x
            self.drop(x)
        self.budget["calved"] += float((lost * area).sum())
        return lost

    def isostasy(self) -> None:
        """4) the bed relaxes toward its settled dip under the ice (a shelf floats: it doesn't load the bed)."""
        self.bed += (self.bed_rest - self.load(self.grounded_ice()) - self.bed) * (1 - math.exp(-self.step / self.p.iso_tau))

    def sea_level(self) -> None:
        """5) sea level from the ice volume (what the ice holds depends a little on the sea level itself)."""
        for _ in range(3):
            self.sl = -(self.above_flotation(self.sl) - self.Vaf0) / self.ocean_area

    def dynamics(self, dq) -> None:
        """The ice's change over one step."""
        dt = self.step * 1000.0  # yr
        gt = RHO_I / 1e12 / dt  # m3 per step -> Gt per yr
        rate, near, active = self.new_ice_rates(dq, dt)
        dv, sea0, H_pre = self.balance_and_flow(rate, near, active, dt)
        if self.p.carving and len(active):
            self.carve(active, dt)
        lost = self.sea(sea0, H_pre, dt)
        area = self.area
        self.flows.append((float(dv[dv > 0].sum()) * gt, float(-dv[dv < 0].sum()) * gt,
                           float((lost * area).sum()) * gt, float(dv[self.north].sum()) * gt))
        self.isostasy()
        self.sea_level()

    # ---- the loop -------------------------------------------------------

    def run(self, progress, t_start) -> None:
        p, step, F = self.p, self.step, self.fields
        H, area = self.H, self.area
        for s_no in range(self.n_steps + 1):
            t_kyr = s_no * step
            self.s_no = s_no
            # forcing: the orbit's insolation anomaly, and the global temperature change (the glacial index's
            # cooling, cycle.py, and the plants')
            orb = orbit_at(t_kyr, p, self.tilt, self.ph)
            dq = insolation(*orb) - self.q_ref
            dTg = self.forcing.update(s_no)
            # climate fields: a full climate every `refresh` steps, blended in between
            if s_no % self.refresh == 0:
                surf, grounded = self.grounded_surface()
                F.refresh(t_kyr, dTg, surf, grounded, H, self.forcing.co2)
                if p.carving and s_no:
                    self.rock_isostasy()
                self.forcing.veg_target = F.plants.dT_target
                if self.index is None:
                    self.setup_index()
            F.blend((s_no % self.refresh) / self.refresh)
            self.prepare_surface(dTg)
            if s_no == 0:
                self.f_snow[:] = self.f_alb  # (the starting ice: snow-covered)
                self.anchor[:] = self.start_anchor(H > 0)
            self.year(self.dt_base, dq)
            if s_no % self.keep == 0:
                self.record(t_kyr, orb, float(dq[self.i65, 3] + dq[self.i65, 4]) / 2, dTg)
            self.series.append((t_kyr, self.sl, float((H * area).sum()) / 1e15, dTg, *orb))
            if s_no == self.n_steps:
                break
            self.dynamics(dq)
            if progress and (s_no + 1) % max(1, self.n_steps // 20) == 0:
                msg = (f"{t_kyr + step:7.1f} kyr  sea level {self.sl:7.1f} m  ice {100 * (H > 1).mean():5.2f}%  "
                       f"dT {dTg:+5.2f}  [{time.time() - t_start:.0f}s]")
                if callable(progress):  # e.g. the server's job progress: (fraction done, message)
                    progress((s_no + 1) / self.n_steps, " ".join(msg.split()))
                else:
                    print("  " + msg, flush=True)


def simulate(src: dict, kyr: float = 1000.0, step: float = 0.5, every: float = 2.0,
             params: TZParams | None = None, progress=False) -> dict:
    """Run the time zoom in memory. progress: True prints a line every 5%,
    or a function(fraction, message) gets them. Returns {"frames": [per-frame dicts:
    t (kyr), stats], "data": {layer: (frames, n) arrays}, "series": per-step
    sea level / ice volume / orbit, "params", "runtime_s"}."""
    t_start = time.time()
    p = params or TZParams()
    s = _Sim(src, kyr, step, every, p)
    s.run(progress, t_start)
    H, area, F = s.H, s.area, s.fields
    ice_cycle = cycling_ice_sun(s.g, area, s.frames, s.out["ice"], s.ref_orb)
    cyc = {**s.index.summary(), **s.glacial}
    return {"frames": s.frames, "data": {k: np.stack(v) for k, v in s.out.items()}, "ice_cycle": ice_cycle, "cycle": cyc,
            "series": np.array(s.series), "flows": np.array(s.flows), "params": asdict(p), "phases": s.ph.tolist(),
            "budget": {**s.budget, "V0": s.V0, "V_end": float((H * area).sum()), "ocean_area": s.ocean_area,
                       "Vaf0": s.Vaf0, "Vaf_end": s.above_flotation(s.sl)},
            "state": {"H": H, "bed": s.bed, "sl": s.sl, "smb": s.smb, "t_warm": s.t_warm, "t_ann": s.t_ann,
                      "p_scale": s.p_scale, "f_snow": s.f_snow, "p_ann": 0.5 * (F["p_jul"] + F["p_jan"]),
                      "cut": s.cut, "till": s.till, "debris": s.debris, "rock_iso": s.rock_iso, "wet_kyr": s.wet_kyr,
                      "slide_km": s.slide_km},
            "anchor": s.anchor.copy(),
            "runtime_s": round(time.time() - t_start, 1), "compute_s": round(F.compute_s, 1),
            "veg_s": round(F.plants.time_s, 1), "veg": F.plants.series,
            "substeps": s.nsub_total}
