"""The peoples history: one try of a tree of lineages through the three time scales."""

from __future__ import annotations

import time
import zlib

import numpy as np

from ...geo import R_KM
from .. import compose as CP
from .. import contacts as CT
from .. import recent as R
from .. import spec as SP
from ..animals import Animals
from ..crops import Crops
from ..crossing import Crossings, corridor
from ..spread import EST
from .competition import CompetitionMixin
from .contact import ContactMixin
from .dispersal import DispersalMixin
from .events import EventsMixin
from .frame import FrameMixin
from .groups import GroupsMixin
from .habitat import HabitatMixin, niche_overlap, same_way
from .origins import OriginsMixin
from .params import (ALPHA_CLOSED, DENSITY_CLIP, DENSITY_PUSH, GROUP_KIN, HOP_EVERY_KYR, MEGAFAUNA_PUSH, MVP_EVERY_KYR,
                     NEAR_TOLERANCE)
from .peoples import PeoplesMixin
from .portals import PortalsMixin
from .steps import StepsMixin
from .tags import _tags, needs_chains


class History(EventsMixin, StepsMixin, HabitatMixin, OriginsMixin, PortalsMixin, GroupsMixin, CompetitionMixin, DispersalMixin,
              ContactMixin, PeoplesMixin, FrameMixin):
    def __init__(self, tree: SP.Tree, ps: R.Pass, seed: int, deep_every: int = 1, glacial_every: float = 4.0,
                 goods: dict | None = None):
        self.tree, self.ps, self.grid = tree, ps, ps.grid
        self.goods = goods  # the world's goods (land.goods), or None: the [[use]] table then has no effect
        self._land_m: dict[str, tuple] = {}
        self._pres = None  # (the present epoch's env and tags, for the land-use normaliser)
        self._portals = None  # (the arrivals' portals, portal_cells)
        self._K_now: dict[int, np.ndarray] = {}  # (each line's habitat this step, and the contact value: the composition's reach)
        self._corr_now = None
        self._tags_now = None
        self._deg = np.diff(self.grid.nbr_off)
        self.contacts = None  # (contacts.Contacts, made by run: the contact record, PW-727)
        g = self.grid
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.cell_km = g.spacing * R_KM
        self.cell_mkm2 = 4 * np.pi * R_KM ** 2 / g.n / 1e6
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
        # a group and its people (and its sister groups) are one people: they mix freely (GROUP_KIN, no exclusion)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay and (a.group_of or b.group_of) \
                        and tree.people_of(a.id) == tree.people_of(b.id):
                    i, j = self.idx[a.id], self.idx[b.id]
                    self.alpha[i, j] *= GROUP_KIN
                    self.terr[i, j] = 0.0
        self._groups = {l.id: [self.idx[x] for x in tree.groups_of(l.id)] for l in self.lines}
        self.cohab = CP.cohabitation(tree, self.lines, self.idx)  # (who lives beside whom: the cells' composition, PW-689)
        self.share_traits = {k: np.array([float(l.body[k]) for l in self.lines]) for k in tree.share_traits()}
        # numbers: a denser rival weighs more (DENSITY_PUSH)
        self.dens = np.array([l.demo("density") for l in self.lines])
        push = np.clip((self.dens[None, :] / self.dens[:, None]) ** DENSITY_PUSH, *DENSITY_CLIP)
        self.alpha *= push
        self.terr *= push
        mega = np.array([l.megafauna for l in self.lines])
        for b in self.lines:  # megafauna press the peoples hardly at all: a handful of dragons does not hold a country against its farmers (PW-855);
            if b.megafauna:  # among themselves they compete at their niche overlap (red dragons and fire giants on the volcanoes, PW-924)
                self.alpha[~mega, self.idx[b.id]] *= MEGAFAUNA_PUSH
                self.terr[~mega, self.idx[b.id]] *= MEGAFAUNA_PUSH
        riv = np.array([l.rivalry for l in self.lines])  # (metallic dragons coexist more readily: weaker competition both ways, PW-924)
        self.alpha *= riv[:, None] * riv[None, :]
        self.terr *= riv[:, None] * riv[None, :]
        # each line's rivals: the lines whose presence enters its competition
        for w in tree.wishes:  # peoples wished near each other tolerate each other (they share a border)
            if w.want == "near" and w.a in self.idx and w.b in self.idx:
                f = 1 - NEAR_TOLERANCE * min(w.weight, 1.0)
                # (a people named in a wish counts with its groups, PW-665)
                for i in [self.idx[w.a], *self._groups[w.a]]:
                    for j in [self.idx[w.b], *self._groups[w.b]]:
                        for x, y in ((i, j), (j, i)):
                            self.alpha[x, y] *= f
                            self.terr[x, y] *= f
        self._chains = needs_chains(tree)
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
        self.faded: dict[str, int] = {}  # patches faded below the viable population, per line
        self._living = {x.id for x in self.tree.leaves()}
        self._refuged: set[str] = set()
        self._last_meet: dict[str, np.ndarray] = {}  # contact hybrids: where their parents last met
        self._apart: set[str] = set()  # ...and those whose parents no longer meet anywhere
        self._lingered: set[str] = set()
        self._linger = np.zeros((len(L), g.n), bool)  # cells a contact hybrid holds on its own
        self._budget = np.zeros(len(L))
        self.contacts = CT.Contacts(self)
        self.animals = Animals(self) if (self.tree.animals is None or self.tree.animals or self.tree.animals_force) else None
        self.crops = Crops(self) if (self.tree.crops is None or self.tree.crops or self.tree.crops_force) else None
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
            Ks = {}
            self._start_due(step, env, tags, Ks)
            if self.animals is not None:
                self.animals.step(step, env, tags, self.p, self._native)
            if self.crops is not None:
                self.crops.step(step, env, tags, self.p, self._native)
            mix = self._mix_ramp(step.ago)
            self._pm = self.p >= EST  # (who holds what at the start of the step, and the count over the natives: kept up to date as each line moves, _sync)
            self._cnt = self._pm[self._native].sum(0, dtype=np.int16)
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
        if l.overlay and l.origin == "hybrid":
            self._hybrid(l, k, K, step)
            return
        self.p[k] = np.minimum(self.p[k], K)
        self.p[k][self.p[k] < EST] = 0
        if l.group_of and not deep:
            self._div_dt[k] += step.dt
            if self._div_dt[k] >= HOP_EVERY_KYR:
                self._diverge(l, k, env, tags, step)
                self._sync(self.idx[l.group_of])  # (it moved some of its people's range over to the group)
                self._div_dt[k] = 0.0
        room, crowd = self._compete(l, k, K, step, tags, corr, mix, deep)
        self._disperse(l, k, K, room, crowd, step, env, tags)
        self._sail(l, k, K, room, crowd, step, env, tags)
        self._jump(l, k, K, room, step, env, tags)
        if not l.overlay and not l.marine:
            self._mvp_dt[k] += step.dt
            if self._mvp_dt[k] >= MVP_EVERY_KYR or deep:
                self._viable(l, k, self._mvp_dt[k], step)
                self._mvp_dt[k] = 0.0
        self._hold_out(l, k, K, step)
        if not (self.p[k] > EST).any() and not l.overlay:
            self.active[l.id] = False
            self.ended[l.id] = step.ago
            self._event(step.ago, "extinct", l, f"{l.label()} dies out (no habitat left)")
        self._sync(k)
