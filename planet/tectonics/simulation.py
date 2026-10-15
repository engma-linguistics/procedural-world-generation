"""The Simulation: its state, the time step, and the world view.

State
-----
Configuration (fixed for a run): grid, seed, params, dt, and what follows
from them (scale, cell_area, edge_len).

Everything else that changes is listed in Simulation.STATE, by group:
  clock      step_no, t
  plates     plates (a plates.Plates: every per-plate array) and owner
             (which plate's crust is on top in each world cell)
  features   hotspots (plumes), volcanoes (arc volcanoes and hotspot vents; volcanism.py)
  mantle     mantle, mantle_lid, mantle_eddies: the mantle's temperature
             anomaly, how long continent has covered it, and its smaller
             unresolved eddies (mantle.py), world frame
  boundary   w_boundary, w_trench: the plate boundaries of the last step,
             for snapshots
  earth      the earth system (earth.py): EARTH_STATE
  log        events, budget

Simulation.state() returns a deep copy of all of it, and
Simulation.from_state() / load_state() put it back: a run continued from
a saved state is bit-identical to one that never stopped (tests/test_state.py),
because each step's randomness depends only on (seed, step_no).

The world view (w_age, w_cont, w_thick, w_rock, w_cover, w_extra, w_rec,
w_lith, w_ref, w_elev, swell) is the plates' crust seen on the world grid. Between steps
it is always _world_view() of the state above, so it isn't part of it.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np

from ..grid import Grid
from . import crust, earth, events, mantle, motion, output, record, volcanism
from .crust import Column
from .isostasy import EXTRA, LIFT, MAX_KM, MIX, elevation, sediment_km
from .params import Params
from .plate_kernels import cleanup_ghosts, resolve
from .plates import Plates
from .setup import initial_state


@dataclass
class Simulation:
    grid: Grid
    seed: int
    params: Params = field(default_factory=Params)
    dt: float = 2.0

    # The earth system's state (earth.py). The climate fields come from
    # climate.compute, every params.climate_every Myr (None before the first).
    EARTH_STATE: ClassVar[tuple[str, ...]] = (
        "dT",  # C: global temperature offset from today's Earth
        "drift",  # C: its random part
        "co2",  # smoothed log ratio of volcanic CO2 sources to weathering sinks
        "refs",  # slow baselines of [source, sink] (None before the first step)
        "depth_ridge",  # m: mean ocean depth, smoothed over params.ridge_time (None before the first step)
        "depth_ref",  # m: slow baseline of depth_ridge (None before the first step)
        "sea_level", "sea_ice", "sea_tect",  # m: sea level = ice part + ocean-basin part
        "ice",  # m of land ice per cell
        "ice_sink",  # m the ice's load presses the bed down per cell (isostasy.ice_load; settled at once)
        "veg",  # ground cover by plants 0..1 per cell (vegetation.ground_cover; 0.0 before the first step)
        "veg_frac", "veg_lai",  # (NP, n) float32: cover and LAI of each plant functional type (None before)
        "npp",  # g C/m2/yr per cell
        "veg_type", "tree_cover",  # named vegetation type (vegetation.TYPES id), tree cover 0..1
        "flora",  # Myr each plant group appeared (vegetation.GROUPS; NaN: not yet)
        "veg_niche",  # each group's niche at the last climate update (vegetation.niches)
        "cloud_jul", "cloud_jan",  # 0..1 cloud cover per half-year (light for the plants)
        "removed",  # km of crust eroded per cell in the last step (feeds weathering)
        "climate_t",  # Myr: when the climate fields were computed
        "temp", "t_warm", "t_cold",  # C: annual mean, warmest and coldest month
        "precip", "p_jul", "p_jan",  # mm/yr: annual, July, January
        "runoff", "aet", "lake_evap",  # mm/yr
        "koppen",  # climate.KOPPEN id
        "wind", "current",  # (n, 3) annual-mean surface wind and ocean current
        "flow", "down",  # rivers of the last step: flow and next cell downstream (-1 at sea)
        "lake_kind", "lake_depth",  # lakes of the last step: hydrology lake_kind, m of water
    )
    # Everything that changes during a run (see the module docstring).
    STATE: ClassVar[tuple[str, ...]] = (
        "step_no", "t", "plates", "owner", "hotspots", "volcanoes", "w_boundary", "w_trench",
        "mantle", "mantle_lid", "mantle_eddies", *EARTH_STATE, "events", "budget")

    def __post_init__(self):
        self._configure()
        self._init_state()
        initial_state(self)
        self._world_view()
        mantle.init(self)
        # tidy up slivers left by the initial set-up before the clock starts
        events.absorb_slivers(self)
        self.events.clear()
        self._world_view()

    def _configure(self):
        """What follows from the grid."""
        g = self.grid
        self.scale = 2.0 ** (g.level - 5)  # widths below are tuned in level-5 cells
        self.cell_area = 4 * np.pi / g.n
        self.edge_len = g.spacing

    def _init_state(self):
        """Every STATE attribute, empty: no plates yet, no climate yet."""
        n = self.grid.n
        # clock
        self.step_no = 0
        self.t = 0.0
        # plates (filled in by setup.initial_state)
        self.plates = Plates.empty(n, len(EXTRA), next_label=self.params.n_plates)
        self.owner = np.zeros(n, np.int64)
        # features
        self.hotspots = []  # plumes, dicts: pos (mantle frame = world frame), born, life, strength, and
        #                     the vent they feed (id, label, ppos, run, gap, vent: volcanism.hotspots)
        self.volcanoes = []  # arc volcanoes and hotspot vents, dicts (volcanism module docstring)
        # boundaries of the last step
        self.w_boundary = np.zeros(n, np.int8)  # +1 converging, -1 diverging
        self.w_trench = np.zeros(n)  # m of trench depth (snapshot elevation)
        # the mantle under the plates (mantle.py), world frame
        self.mantle = np.zeros(n)  # temperature anomaly, ~+-1
        self.mantle_lid = np.zeros(n)  # running average of continental cover over it
        self.mantle_eddies = np.zeros(0)  # spherical-harmonic coefficients of its unresolved eddies
        # earth system (EARTH_STATE)
        self.dT, self.drift, self.co2, self.refs = 0.0, 0.0, 0.0, None
        self.depth_ridge = self.depth_ref = None
        # m, relative to an ice-free planet with the starting sea floor
        self.sea_level, self.sea_ice, self.sea_tect = 0.0, 0.0, 0.0
        self.ice = np.zeros(n)
        self.ice_sink = np.zeros(n)
        self.veg = 0.0
        self.veg_frac = self.veg_lai = None
        self.npp = np.zeros(n)
        self.veg_type = np.zeros(n, np.uint8)
        self.tree_cover = np.zeros(n)
        self.flora = [float("nan")] * 6
        self.veg_niche = np.zeros(6)
        self.cloud_jul = self.cloud_jan = None
        self.removed = np.zeros(n)
        self.climate_t = 0.0
        self.temp = self.t_warm = self.t_cold = None
        self.precip = self.p_jul = self.p_jan = None
        self.runoff = self.aet = self.lake_evap = None
        self.koppen = self.wind = self.current = None
        self.flow = np.zeros(n)
        self.down = np.full(n, -1, np.int64)
        self.lake_kind = np.zeros(n, np.int8)
        self.lake_depth = np.zeros(n)
        # log
        self.events: list[events.Event] = []
        self.budget = {}  # km x cells of continental crust gained (+) or lost (-), by process

    # ------------------------------------------------------------- state
    def state(self) -> dict:
        """A deep copy of everything that changes during the run: {name:
        value} for every name in STATE (numpy arrays, a Plates, plain
        lists/dicts/floats, None for climate fields not computed yet).
        (A checkpoint file can shrink it a lot: only plates.alive slots
        matter, and of their (P, n) arrays only the plates.owned cells.)"""
        return copy.deepcopy({name: getattr(self, name) for name in self.STATE})

    def load_state(self, state: dict):
        """Continue from a state() taken from a simulation with the same
        grid, seed, params and dt."""
        for name in self.STATE:
            setattr(self, name, copy.deepcopy(state[name]))
        self._world_view()

    @classmethod
    def from_state(cls, grid: Grid, seed: int, params: Params, dt: float, state: dict) -> "Simulation":
        """A simulation resumed from state() (without building the starting planet)."""
        sim = cls.__new__(cls)
        sim.grid, sim.seed, sim.params, sim.dt = grid, seed, params, dt
        sim._configure()
        sim.load_state(state)
        return sim

    # ------------------------------------------------------------- main loop
    def run(self, until_t: float, on_step=None):
        while self.t < until_t - 1e-9:
            self.step()
            if on_step:
                on_step(self)

    def step(self):
        """One time step. All randomness comes from default_rng([seed,
        step_no]), drawn in a fixed order: hotspots, volcanoes (both in
        _physics), then the forces, then rifts; plus side streams
        default_rng([seed, step_no, k]) for the global temperature's drift
        (k=1) and the volcanoes' own details (k=7, 8; volcanism.py)."""
        self.step_no += 1
        self.t = self.step_no * self.dt
        rng = np.random.default_rng([self.seed, self.step_no])

        # 1-2. move plates and pull
        self.plates.move(self.grid, self.dt)

        # 3. resolve ownership
        newc, stacked = self._resolve()

        # 4. boundaries, crust and surface, forces
        bd = motion.boundaries(self)
        mantle.update(self, bd)
        self._physics(bd, newc, stacked, rng)
        cell_forces = motion.forces(self, bd, rng)

        # 5. events
        vol0 = float((self.w_thick * self.w_cont).sum())
        events.sutures(self, bd)
        events.absorb_slivers(self)
        events.maybe_rift(self, cell_forces, rng)
        self._world_view()
        self.book("events", vol0, float((self.w_thick * self.w_cont).sum()), 1.0)
        volcanism.tend(self)  # volcanoes follow their crust, sink, erode, grow reefs

        # 6. climate, every climate_every Myr, on the ground as the events
        # left it: a keyframe shows the climate of the ground it shows, and
        # the next steps' erosion uses it
        if earth.climate_due(self) or self.step_no == 1:  # (the first step's ran mid-step too)
            self._climate(self.w_elev)

    def _climate(self, e):
        """Update the climate on elevation e (m above the current sea level).
        It moves the sea (land ice), so the world view's elevation follows."""
        sea0 = self.sea_level
        earth.update_climate(self, e)
        self.w_elev = self.w_elev - (self.sea_level - sea0)

    def _resolve(self):
        """Decide which plate owns each world cell (plate_kernels.resolve).
        Returns (new ocean floor mask, km of crust stacked by collisions)."""
        g, pl = self.grid, self.plates
        vol0 = float((self.w_thick * self.w_cont).sum())
        stacked = np.zeros(g.n)
        self.owner, newc = resolve(
            pl.alive, pl.idx, pl.owned, pl.age, pl.cont, pl.thick, pl.rock, pl.cover, pl.extra,
            pl.rec, pl.lith, record.blank(), self.owner, g.nbr_off, g.nbr_idx, pl.Q, g.centers, stacked)
        cleanup_ghosts(pl.alive, pl.owned, pl.Q, g.centers, self.owner, g.raster, g.nbr_off, g.nbr_idx)
        self._world_view()
        self.book("resolve", vol0, float((self.w_thick * self.w_cont).sum()), 1.0)
        return newc, stacked

    # ------------------------------------------------------------- physics
    def _physics(self, bd, newc, stacked, rng):
        """Crust, surface and climate on the world map for one step: a
        sequence of substeps on one Column (crust.py), written back to the
        plates at the end."""
        conv = np.clip(bd.conv, 0, 15)
        thermostat, shrink = crust.thermostats(self)
        growth = crust.arc_growth(self, bd, conv, thermostat)
        stretch = crust.rift_stretching(self, bd)
        head, apron, vents, dome = volcanism.hotspots(self, rng, bd)

        col = self._age(dome)
        plume = volcanism.cap_plumes(self, col, head, (3000.0, 2000.0))
        t0, col.t = col.t, col.t + plume * self.dt  # (provisionally, so the apron sees the head's lava)
        plume = plume + volcanism.cap_plumes(self, col, apron, volcanism.APRON_TOP, cont_share=1.0)
        col.t = t0
        plume = plume + vents  # (each vent capped itself)
        crust.add_arcs_and_plumes(self, col, growth, plume)
        edges = crust.inner_edges(self, col.cont)
        stack_add = crust.stack_collisions(self, col, stacked, edges)
        crust.accrete(self, bd, conv, col)
        crust.subduction_erosion(self, bd, conv, col, shrink)
        arcky = crust.arc_rock(self, col, growth)
        t0 = col.t.copy()  # (volcanoes edits it in place)
        col.t = volcanism.volcanoes(self, growth, col.t, rng)
        self.book("volcano", t0, col.t, col.cont)
        crust.stretch(self, col, stretch, plume, newc)
        squeezed = crust.flow_and_orogeny(self, col, edges, stack_add)

        # weather, ice, rivers, erosion, sediment
        # (the climate's random drift has its own stream: changes to how many
        # numbers the tectonics draws shouldn't reshuffle the climate history)
        earth.global_temperature(self, growth, int(newc.sum()), np.random.default_rng([self.seed, self.step_no, 1]))
        if self.precip is None:  # the first step: erosion needs a climate (later ones: step's end)
            self._climate(elevation(col.t, self.w_age, col.cont, col.rock, self.swell - self.sea_level,
                                    sediment_km(col.cover, col.x)))
        dep, lake = earth.erode(self, col)
        chem = earth.sediments(self, col, dep, lake)
        earth.bury(self, col)
        earth.reefs(self, col, dep, chem)
        col.rec[self.ice > 0, record.T_ICE] = self.t

        crust.coherence(self, col)
        born = crust.birth_and_cratons(self, col, arcky, squeezed)
        self._write_back(col, born)
        self._record_boundaries(bd, conv)

    def _age(self, dome):
        """Age every plate's crust by dt and unpack the world view into the
        Column the physics works on.

        Ageing acts on *every* cell of every plate, in the plate's own frame.
        (Doing it only on the cells currently visible on the world grid left
        the 10-20% momentarily unsampled cells un-aged: speckle.)"""
        pl = self.plates
        pl.age[pl.owned] += self.dt
        self._world_view()
        col = Column(t=self.w_thick, cover=self.w_cover, x=self.w_extra.copy(), cont=self.w_cont,
                     rock=self.w_rock.copy(), rec=self.w_rec.copy(), lith=self.w_lith.copy())
        # the swell rides off with the plate and subsides as the mantle under it cools
        col.x[:, LIFT] = np.maximum(col.x[:, LIFT] * np.exp(-self.dt / self.params.swell_time), dome)
        self.swell = col.x[:, LIFT]
        return col

    def _write_back(self, col, born):
        """Make the column the new world view and copy it to the plates.
        Crust is kept between 1 km and MAX_KM, and the sediment cover can't
        be thicker than the crust (its rock mix shrinks with it). The strata
        are made to add up to the final cover (record.reconcile)."""
        x = col.x
        self.w_cont = col.cont | born
        self.w_thick = np.clip(col.t, 1.0, MAX_KM)
        self.book("clip", col.t, self.w_thick, self.w_cont)
        self.w_cover = np.clip(col.cover, 0, self.w_thick)
        shrink = self.w_cover / np.maximum(col.cover, 1e-9)
        m = np.maximum(x[:, MIX] * shrink[:, None], 0)
        over = np.maximum(m.sum(1) / np.maximum(self.w_cover, 1e-9), 1.0)
        x[:, MIX] = m / over[:, None]
        self.w_extra = x
        self.w_rock = col.rock
        record.diagenesis(col.rec, col.lith)
        record.reconcile(col.rec, col.lith, self.w_cover, record.default_rock(self.w_cover, x[:, MIX]), self.t)
        self.w_rec, self.w_lith = col.rec, col.lith
        self.w_elev = elevation(self.w_thick, self.w_age, self.w_cont, self.w_rock, self.swell - self.sea_level,
                                sediment_km(self.w_cover, self.w_extra))
        self._scatter()

    def _record_boundaries(self, bd, conv):
        """Remember this step's plate boundaries and trenches for snapshots."""
        n = self.grid.n
        bnd = np.zeros(n, np.int8)
        conv_cells = np.concatenate([bd.a[bd.collision | bd.subduct], bd.b[bd.collision | bd.subduct]])
        bnd[bd.spreading] = -1
        bnd[conv_cells] = 1
        self.w_boundary = bnd
        trench = np.zeros(n)
        np.minimum.at(trench, bd.sinking, -350 * bd.at_trenches(conv))
        self.w_trench = np.maximum(trench, -4000)

    def book(self, what, before, after, cont):
        """Add the change in continental crust (km x level-5 cells) to the budget under `what`."""
        self.budget[what] = self.budget.get(what, 0.0) + float(np.sum((after - before) * cont)) / self.scale**2

    # ------------------------------------------------------------- world view
    def _world_view(self):
        """The plates' crust as seen on the world grid (the w_* arrays)."""
        pl = self.plates
        o, i = self.owner, np.arange(self.grid.n)
        r = pl.idx[o, i]
        self.w_age = pl.age[o, r]
        self.w_cont = pl.cont[o, r]
        self.w_thick = pl.thick[o, r]
        self.w_rock = pl.rock[o, r]
        self.w_cover = pl.cover[o, r]
        self.w_extra = pl.extra[o, r]
        self.w_rec = pl.rec[o, r]
        self.w_lith = pl.lith[o, r]
        self.swell = self.w_extra[:, LIFT]
        self.w_elev = elevation(self.w_thick, self.w_age, self.w_cont, self.w_rock, self.swell - self.sea_level,
                                sediment_km(self.w_cover, self.w_extra))
        self.w_ref = r

    def _scatter(self):
        """Write the world view back into the plates' frames."""
        pl = self.plates
        o, r = self.owner, self.w_ref
        pl.age[o, r] = self.w_age
        pl.cont[o, r] = self.w_cont
        pl.thick[o, r] = self.w_thick
        pl.rock[o, r] = self.w_rock
        pl.cover[o, r] = self.w_cover
        pl.extra[o, r] = self.w_extra
        pl.rec[o, r] = self.w_rec
        pl.lith[o, r] = self.w_lith

    # ------------------------------------------------------------- queries
    def bed(self) -> np.ndarray:
        """m above sea level of the ground, pressed down by the ice's load
        (w_elev is the crust's own height, which the long-term processes
        use: the load is gone ~10 kyr after its ice)."""
        return self.w_elev - self.ice_sink

    def land(self) -> np.ndarray:
        """Land: ground above sea level, or under grounded ice (all of the
        run's ice is grounded, even where its load pushes the bed below the sea)."""
        return (self.bed() > 0) | (self.ice > 0)

    def heat(self) -> float:
        """Mantle heat relative to today's (see earth.heat)."""
        return earth.heat(self.params, self.t)

    def target_fraction(self) -> float:
        """Share of the surface the continents are steered toward now."""
        return earth.target_fraction(self.params, self.t)

    def velocity(self) -> np.ndarray:
        """Tangent velocity of every cell (rad/Myr, world frame)."""
        return motion.velocity(self)

    def snapshot(self) -> output.Snapshot:
        return output.snapshot(self)

    def stats(self) -> dict:
        return output.stats(self)
