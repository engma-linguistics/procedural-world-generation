"""The peoples history: one try of a tree of lineages through the three time scales."""

from __future__ import annotations

import time
import zlib

import numpy as np

from ...geo import R_KM, cell_area_km2
from .. import compose as CP
from .. import contacts as CT
from .. import landuse as LU
from .. import prey as PR
from .. import recent as R
from .. import spec as SP
from ..animals import Animals
from ..crops import Crops
from ..crossing import Crossings, corridor
from ..spread import EST
from .cities import CitiesMixin
from .competition import CompetitionMixin
from .contact import ContactMixin
from .dispersal import DispersalMixin
from .events import EventsMixin
from .frame import FrameMixin
from .groups import GroupsMixin
from .growth import GrowthMixin
from .habitat import HabitatMixin, niche_overlap, same_way
from .origins import OriginsMixin
from . import megafauna as MG
from . import params as PM
from .params import (PEOPLE_PROD, ALPHA_CLOSED, AMONG_TOLERANCE, HOP_EVERY_KYR, MEGAFAUNA_PUSH,
                     MVP_EVERY_KYR, NEAR_TOLERANCE)
from .peoples import PeoplesMixin
from .portals import PortalsMixin
from .steps import StepsMixin
from .tags import _tags, needs_chains


class History(EventsMixin, StepsMixin, HabitatMixin, OriginsMixin, PortalsMixin, GroupsMixin, CompetitionMixin, DispersalMixin,
              ContactMixin, CitiesMixin, PeoplesMixin, FrameMixin, GrowthMixin):
    def __init__(self, tree: SP.Tree, ps: R.Pass, seed: int, deep_every: int = 1, glacial_every: float = 4.0,
                 goods: dict | None = None, knobs: dict | None = None):
        self.tree, self.ps, self.grid = tree, ps, ps.grid
        self.knobs = knobs or {}  # lane 78: {people id: {"density": x}}, the share bands' nudges (history.bands)
        self.goods = goods  # the world's goods (land.goods), or None: the [[use]] table then has no effect
        self._land_m: dict[str, tuple] = {}
        self._pres = None  # (the present epoch's env and tags, for the land-use normaliser)
        self._portals = None  # (the arrivals' portals, portal_cells)
        self._K_now: dict[int, np.ndarray] = {}  # (each line's habitat this step, and the contact value: the composition's reach)
        self._L: dict[int, np.ndarray] = {}  # (niche learning, PW-1155: reset by run)
        self._learn_in: dict[int, tuple] = {}
        self._env_now = None
        self._Lm = None  # (the learned acceptance of every line, lines x cells, float32; made on first use; _L's rows are its views)
        self._dAT = None  # (habitat._learned_load: the pairs' coefficients with the ways counted alike, less their own)
        self._K_own: dict[int, np.ndarray] = {}  # (a megafauna kind's habitat without ecological release, PW-1024: its own country, for its target)
        self._corr_now = None
        self._tags_now = None
        self._deg = np.diff(self.grid.nbr_off)
        self.contacts = None  # (contacts.Contacts, made by run: the contact record, PW-727)
        g = self.grid
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.cell_km = g.spacing * R_KM
        self.cell_mkm2 = cell_area_km2(g.n) / 1e6
        self.lines = tree.order()
        # (a generator per line, seeded from the run seed and the line's id: no line's draws depend on how many others are alive, so a
        # marine line, or a parent kept alive by one, leaves the land peoples' draws as they were, PW-779)
        self._lrng = {l.id: np.random.default_rng((seed, 779, zlib.crc32(l.id.encode()))) for l in self.lines}
        self.idx = {l.id: k for k, l in enumerate(self.lines)}
        self.alpha = np.zeros((len(self.lines),) * 2)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay:
                    self.alpha[self.idx[a.id], self.idx[b.id]] = niche_overlap(a, b, tree)
        # closed-country extra competition: alpha + (1 - contact) x terr (alpha_eff -> ALPHA_CLOSED for alike ways)
        self.terr = np.zeros_like(self.alpha)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay:
                    i, j = self.idx[a.id], self.idx[b.id]
                    self.terr[i, j] = max(0.0, ALPHA_CLOSED - self.alpha[i, j]) * same_way(a, b)
        # marine lines (coast, sea) compete with each other, not with land peoples: they only share the coast (PW-775)
        mar = np.array([l.marine for l in self.lines])
        if mar.any():
            across = mar[:, None] != mar[None, :]
            self.alpha[across] = 0.0
            self.terr[across] = 0.0
        # a group and its people (and its sister groups) are one people with one capacity (lane 83, PW-1205 A): per cell its lines
        # together hold at most the habitat of the way of life the land suits best (each line feels its kin in full, alpha 1, no
        # closed-country term, no fit weight), so a people's ways of life split its land and its people instead of stacking on them
        self._kin = np.zeros((len(self.lines), len(self.lines)), bool)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay and (a.group_of or b.group_of) \
                        and tree.people_of(a.id) == tree.people_of(b.id):
                    i, j = self.idx[a.id], self.idx[b.id]
                    self.alpha[i, j] = 1.0
                    self.terr[i, j] = 0.0
                    self._kin[i, j] = True
        self._groups = {l.id: [self.idx[x] for x in tree.groups_of(l.id)] for l in self.lines}
        self.cohab = CP.cohabitation(tree, self.lines, self.idx)  # (who lives beside whom: the cells' composition, PW-689)
        self.share_traits = {k: np.array([float(l.body[k]) for l in self.lines]) for k in tree.share_traits()}
        self.dens = np.array([MG.pressed_density(l, tree) if l.megafauna else l.demo("density") for l in self.lines])
        for lid, kn in self.knobs.items():  # (a share band's nudge: the people's own density, its groups' with it; history.bands)
            if kn.get("density", 1.0) != 1.0 and lid in self.idx:
                for j in [self.idx[lid], *self._groups.get(lid, [])]:
                    self.dens[j] *= kn["density"]
        # (dragons, the flying megafauna: one per meta.dragon_km2 where peoples press them, owner PW-923, PW-957; the true giants, the rest
        # of the megafauna: one per meta.giant_km2, PW-963; both user options. Away from the peoples they keep nearer their natural
        # density (meta.megafauna_natural: from the prey, PW-966, or from mass): MG.local_density, read through dens_at. The competition
        # below takes the pressed value)
        self._dmap = None  # (the peoples' density per cell, PW-974: PR.people_fields; set below, once the dens are known)
        MG.setup(self)  # (dens_nat, the prey field; _press and _prey: the peoples' pressure and the prey, per cell, at the start of the step)
        F = PR.people_fields(self.lines, lambda l: LU.shares(tree, l), getattr(ps, "graze_npp", None), getattr(ps, "forage", None),
                               getattr(ps, "npp", None))
        self._dens0 = self.dens.copy()  # (the tree's numbers: a farming people's at its own way of life; history.growth's era sets dens)
        self._Fprod = F if (F is not None and PEOPLE_PROD) else None
        if F is not None and PEOPLE_PROD:
            self._dmap = self.dens[:, None] * F  # (static: the present's land; the deep epoch, whose plates lay elsewhere, keeps the number)
        mega = np.array([l.megafauna for l in self.lines])
        for b in self.lines:  # megafauna press the peoples hardly at all: a handful of dragons does not hold a country against its farmers (PW-855);
            if b.megafauna:  # among themselves they compete at their niche overlap (red dragons and fire giants on the volcanoes, PW-924)
                self.alpha[~mega, self.idx[b.id]] *= MEGAFAUNA_PUSH
                self.terr[~mega, self.idx[b.id]] *= MEGAFAUNA_PUSH
        mob = np.array([SP.WAY_MOBILE.get(l.way, 0.0) if l.way else 0.0 for l in self.lines])  # nomads overlap more (spec.WAY_MOBILE)
        nm = np.where((mob[:, None] > 0) != (mob[None, :] > 0), 1 - SP.NOMAD_COEXIST * np.maximum(mob[:, None], mob[None, :]), 1.0)
        self.alpha *= nm
        self.terr *= nm
        riv = np.array([l.rivalry for l in self.lines])  # (metallic dragons coexist more readily with other megafauna: weaker competition
        rv = np.where(mega[:, None] & mega[None, :], riv[:, None] * riv[None, :], 1.0)  # both ways, among megafauna only: coexistence, not numbers, PW-924)
        self.alpha *= rv
        self.terr *= rv
        # each line's rivals: the lines whose presence enters its competition
        self._crowd = np.zeros(len(self.lines))  # (each line's crowding at its last step; reset by run)
        self._among = np.zeros((len(self.lines),) * 2, bool)  # (pairs of an 'among' wish, PW-889)
        for w in tree.wishes:  # peoples wished near each other tolerate each other (they share a border); 'among', more (they share cells)
            if w.want in ("near", "among") and w.a in self.idx and w.b in self.idx:
                f = 1 - (NEAR_TOLERANCE if w.want == "near" else AMONG_TOLERANCE) * min(w.weight, 1.0)
                # (a people named in a wish counts with its groups, PW-665)
                for i in [self.idx[w.a], *self._groups[w.a]]:
                    for j in [self.idx[w.b], *self._groups[w.b]]:
                        for x, y in ((i, j), (j, i)):
                            self.alpha[x, y] *= f
                            self.terr[x, y] *= f
                            if w.want == "among":
                                self._among[x, y] = True
        self.alpha[self._kin] = 1.0  # (one capacity among kin, whatever the nomads' overlap or a wish: PW-1205)
        self.terr[self._kin] = 0.0
        self._chains = needs_chains(tree)
        self._aT, self._tT = np.ascontiguousarray(self.alpha.T), np.ascontiguousarray(self.terr.T)  # (how each rival feels line k: column k)
        self._Kmat = np.zeros((len(self.lines), g.n))  # (each line's habitat at its last step: its rivals' coexistence shares, params.COEXIST)
        self._breadth = np.ones(len(self.lines))  # (its fit and breadth then: the contest, params.FIT_Q)
        self._Fmat = np.zeros((len(self.lines), g.n))
        self._fit_now: dict[int, np.ndarray] = {}
        self._martial = np.array([1.0 if l.megafauna or l.overlay else l.demo("contest") for l in self.lines])  # (each line's martial strength in the contest, spec contest, lane 83)
        self._rivals = [np.flatnonzero((self.alpha[i] != 0) | (self.terr[i] != 0)) for i in range(len(self.lines))]
        self.steps = self._steps(glacial_every)
        self.events: list[dict] = []
        self.origins: dict[str, dict] = {}
        self.tracks: dict[str, list] = {l.id: [] for l in self.lines}
        self.cross = Crossings(self.grid, self.steps[-1].get(), self.cell_km, self.cell_mkm2, getattr(ps, "world_seed", None),
                            getattr(ps, "world_names", None))
        self.flow = getattr(ps, "flow", None)
        self.animals: Animals | None = None  # (made in run(): the domesticated animals, animals.py)
        self.crops: Crops | None = None  # (made in run(): the cultivated plants, crops.py)

    def run(self, progress=lambda f, msg: None) -> dict:
        g, L = self.grid, self.lines
        self.p = np.zeros((len(L), g.n))
        self.active = {l.id: False for l in L}
        self.started, self.ended = {}, {}
        self.crossings_n: dict[str, int] = {}
        self.jumps_n: dict[str, int] = {}  # (overland jumps, PW-920)
        self._hop_dt = np.zeros(len(L))
        self._mvp_dt = np.zeros(len(L))
        self._div_dt = np.zeros(len(L))
        self._native = np.array([i for i, x in enumerate(L) if not x.overlay and not x.marine], np.int64)  # (land peoples: the sea ones leave the animals, crops and counts as they were)
        self._nat_set = set(self._native.tolist())
        # (lane 83b: ...and the peoples among them: a cell only megafauna hold is free country for a people's pioneers and jumps; the
        # dragons are a handful per country and hardly take room from the peoples, MEGAFAUNA_PUSH, so their range is not 'taken')
        self._ppl_set = {i for i in self._nat_set if not L[i].megafauna}
        self.faded: dict[str, int] = {}  # patches faded below the viable population, per line
        self._living = {x.id for x in self.tree.leaves()}
        self._refuged: set[str] = set()
        self._last_meet: dict[str, np.ndarray] = {}  # contact hybrids: where their parents last met
        self._apart: set[str] = set()  # ...and those whose parents no longer meet anywhere
        self._lingered: set[str] = set()
        self._unborn: set[str] = set()  # ...and those never born: their parents' young are absorbed into a parent people, or none (PW-752)
        self._linger = np.zeros((len(L), g.n), bool)  # cells a contact hybrid holds on its own
        self._budget = np.zeros(len(L))
        self._crowd = np.zeros(len(L))  # (each line's crowding at its last step, pressure.crowding: the squeeze that drives integration, PW-889)
        self._Kmat = np.zeros((len(L), g.n))  # (each line's habitat at its last step: its rivals' coexistence shares, params.COEXIST)
        self._Fmat = np.zeros((len(L), g.n))  # (...its fit, and breadth, the fit's sum: the contest, params.FIT_Q, lane 83)
        self._breadth = np.ones(len(L))
        self._fit_now: dict[int, np.ndarray] = {}
        self._last_held: dict[int, np.ndarray] = {}  # (a line's last land when it ended: a split whose parent is gone founds by it, PW-1184)
        self._mref = np.zeros(len(L))  # (each line's lagged range mass: its momentum, pressure.surge)
        self._L: dict[int, np.ndarray] = {}  # (each learning line's learned acceptance per cell, float32, PW-1155: habitat._learn)
        self._Lm = None
        self._learn_in: dict[int, tuple] = {}  # (...and its preference K0 and body limit T this step, from _K)
        self.contacts = CT.Contacts(self)
        self.animals = Animals(self) if (self.tree.animals is None or self.tree.animals or self.tree.animals_force) else None
        self.crops = Crops(self) if (self.tree.crops is None or self.tree.crops or self.tree.crops_force) else None
        self._growth_setup()
        frames = []
        nsteps = len(self.steps)
        t0 = time.time()
        for si, step in enumerate(self.steps):
            env = step.get()
            deep = step.epoch == "deep"
            tags = _tags(g, env, self._chains, self._volcanic(deep))  # (the plates have moved since: no present rivers or shelves then)
            tags["corridor"] = corr = corridor(tags, env, None if deep else self.flow,
                                               None if deep else env["land"] & (self.cross.label < 0))
            self._corr_now = corr
            self._tags_now = tags
            self._env_now = env
            Ks = {}
            self._land_now = env["land"]  # (the peoples' pressure on the megafauna this step, PW-957)
            self._deep_now = deep
            self._dens_memo = None
            self._ago_now = step.ago  # (the peoples' means against the megafauna follow the era, MG.means, PW-1068)
            self._press = MG.pressure(self, self.p, env["land"]) if any(x.megafauna for x in L) else None
            self._kill = MG.kill(self, self.p, env["land"]) if self._press is not None else None
            if self._press is not None:  # (lane 90: the overkill's clock, PW-1000; the deep epoch's food budget, PW-1062)
                MG.note_settled(self, self.p, step.ago)
                if deep:
                    MG.deep_budget(self, self.p, env["land"])
            self._prey, self._food, _ = MG.prey_and_food(self, self.p, self._press, tags, self._kill) if self._press is not None and not deep else (None, None, None)
            self._start_due(step, env, tags, Ks)
            if self.animals is not None:
                self.animals.step(step, env, tags, self.p, self._native)
            if self.crops is not None:
                self.crops.step(step, env, tags, self.p, self._native)
            self._note_eras(step)  # (each people's mortality schedule: forager, horticulturalist, agrarian; history.growth)
            self._waves(step, env, tags, Ks)  # (an arrival's later waves, and the wandering portals: history.portals)
            mix = self._mix_ramp(step.ago)
            self._pm = self.p >= EST  # (who holds what at the start of the step, and the count over the natives: kept up to date as each line moves, _sync)
            self._cnt = self._pm[self._native].sum(0, dtype=np.int16)
            self._cntp = self._pm[sorted(self._ppl_set)].sum(0, dtype=np.int16)
            order = [l for l in L if self.active[l.id]]
            keys = {l.id: self._lrng[l.id].random() for l in order}  # (the order: a random key per line from its own generator)
            order.sort(key=lambda l: (l.marine, keys[l.id]))
            for l in order:
                self._advance(l, step, env, tags, corr, mix, Ks)
            if step.store or si == nsteps - 1:
                frames.append(self._frame(step, env))
            if si % 25 == 0:
                progress(si / nsteps, f"step {si}/{nsteps} ({step.epoch}, {step.ago:g} kyr ago)")
        self.runtime = time.time() - t0
        return {"frames": frames, "present": self.p.copy()}

    def _advance(self, l, step, env, tags, corr, mix, Ks):
        """One step of one living line: habitat, competition, spread, crossings, the viable-population fade, a refuge."""
        deep = step.epoch == "deep"
        k = self.idx[l.id]
        if l.extinct_kyr is not None and step.ago <= l.extinct_kyr + 1e-9:
            if (self.p[k] >= EST).any():
                self._last_held[k] = self.p[k] >= EST
            self.p[k][:] = 0
            self.active[l.id] = False
            self.ended[l.id] = step.ago
            self._event(step.ago, "extinct", l, f"{l.label()} dies out")
            self._sync(k)
            return
        K = Ks.get(l.id)
        if K is None:
            K = self._K(l, env, tags, step)
        self._K_now[k] = K  # (the composition's reach: where a people could live, CP.reach)
        self._note_K(k, K)
        if l.overlay and l.origin == "hybrid":
            self._hybrid(l, k, K, step)
            return
        if l.cities:  # (a people's minority in others' cities, PW-889)
            self._city(l, k, step)
            return
        held0 = self.p[k] >= EST  # (its land at the step's start: kept if it ends now, PW-1184)
        self.p[k] = np.minimum(self.p[k], K)
        self.p[k][self.p[k] < EST] = 0
        if l.group_of and not deep:
            self._div_dt[k] += step.dt
            if self._div_dt[k] >= HOP_EVERY_KYR:
                self._diverge(l, k, env, tags, step)
                self._sync(self.idx[l.group_of])  # (it moved some of its people's range over to the group)
                self._div_dt[k] = 0.0
        room, crowd = self._compete(l, k, K, step, tags, corr, mix, deep)
        self._crowd[k] = crowd
        self._disperse(l, k, K, room, crowd, step, env, tags)
        self._sail(l, k, K, room, crowd, step, env, tags)
        self._jump(l, k, K, room, step, env, tags)
        if l.megafauna:
            MG.scatter(self, l, k, K, step, env)
        if not l.overlay and not l.marine:
            self._mvp_dt[k] += step.dt
            if self._mvp_dt[k] >= MVP_EVERY_KYR or deep:
                self._viable(l, k, self._mvp_dt[k], step)
                self._mvp_dt[k] = 0.0
        if PM.LEARN:  # (PW-1155: niche learning at the edges of its range)
            self._learn(l, k, step, tags)
        self._hold_out(l, k, K, step)
        if not (self.p[k] > EST).any() and not l.overlay:
            if held0.any():
                self._last_held[k] = held0
            self.active[l.id] = False
            self.ended[l.id] = step.ago
            self._event(step.ago, "extinct", l, f"{l.label()} dies out (no habitat left)")
        self._sync(k)
