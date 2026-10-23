"""Peoples through the three time scales: habitat, origins, spread, competition, late mixing.

Epochs: the source run's keyframes (deep, Myr), the glacial time zoom's frames (kyr),
the recent pass (centuries). Design: docs/proposals/lineages.md.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import R_KM, is_land
from . import recent as R
from . import spec as SP
from .spread import EST, nearest_label, rings, spread

CONVERGE = 400  # passes at a deep (Myr) step: ranges fill what is connected
FARM_KYR = 6.0  # agricultural lines speed up from then
MIX_DROP = 0.6  # competition falls by this share by the present (from mixing_start)
PALETTE = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c",
           "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1",
           "#000075", "#a9a9a9", "#ff7f50", "#7fffd4", "#dc143c", "#00bfff", "#adff2f", "#ff69b4", "#cd853f"]


# -- epochs ----------------------------------------------------------------------------------------
@dataclass
class Step:
    ago: float  # kyr before present (of this step's state)
    dt: float  # kyr since the previous step
    epoch: str  # deep | glacial | recent
    store: bool
    get: object  # () -> env dict
    stats: dict = field(default_factory=dict)


def _tags(grid, env: dict) -> dict:
    """Place tags of an epoch (PLACES) and Köppen ids, shared by every line."""
    land = env["land"] & ~(env["ice"] > 0.5)
    sea = ~env["land"]
    no, ni = grid.nbr_off, grid.nbr_idx
    src = grid.nbr_src
    sea_nbr = np.zeros(grid.n, bool)
    np.logical_or.at(sea_nbr, src, sea[ni])
    elev = np.maximum(env["elevation"] - env["ice"], 0)
    dh = np.zeros(grid.n)
    np.maximum.at(dh, src, np.abs(elev[ni] - elev[src]))
    lab, k = grid.components(env["land"])
    sizes = np.bincount(lab[lab >= 0], minlength=k) if k else np.zeros(0)
    island = np.zeros(grid.n, bool)
    if k:
        small = sizes < max(3, 0.004 * env["land"].sum())
        island = env["land"] & (lab >= 0) & small[np.maximum(lab, 0)]
    trees = env.get("tree_cover", np.zeros(grid.n))
    rain = env["precipitation"]
    mountain = land & ((elev > 1500) | (dh > 700))
    return {"land": land, "coast": land & sea_nbr, "island": island, "mountain": mountain,
            "lowland": land & (elev < 500), "inland": land & ~sea_nbr, "forest": land & (trees >= 35),
            "open": land & (trees < 20) & (rain > 200), "wetland": land & (elev < 300) & (rain > 1600),
            "elev": elev, "label": lab, "sizes": sizes}


def _soft(x, lo, hi, soft):
    return np.clip(np.minimum((x - (lo - soft)) / soft, ((hi + soft) - x) / soft), 0, 1)


def capacity(line: SP.Lineage, env: dict, tags: dict) -> np.ndarray:
    """Carrying capacity K in [0, 1] of a line's own habitat."""
    w = line.trait("widen", 1.0)
    lo, hi = line.temp_c
    mid, half = (lo + hi) / 2, (hi - lo) / 2 * w
    K = _soft(env["temperature"], mid - half, mid + half, 4.0 * w)
    rlo, rhi = line.rain_mm
    lr = np.log2(np.maximum(env["precipitation"], 1.0))
    K = K * _soft(lr, np.log2(max(rlo, 1)) - (w - 1), np.log2(max(rhi, 1)) + (w - 1), 1.0 * w)
    if line.elev_m:
        K = K * _soft(tags["elev"], line.elev_m[0], line.elev_m[1], 600.0 * w)
    cl = env["climate"].astype(int)

    def has(tag):
        if tag in SP.PLACES:
            return tags[tag]
        ids = SP.GROUPS.get(tag) or [SP.KOPPEN_CODES.index(tag)]
        return np.isin(cl, ids)

    if line.prefers:
        match = np.zeros(len(K), bool)
        for t in line.prefers:
            match |= has(t)
        K = K * np.where(match, 1.0, 0.4)
    for t in line.avoids:
        K = K * np.where(has(t), 0.25, 1.0)
    cb = line.trait("coast", 0.0)
    if cb:
        K = K * np.where(tags["coast"], 1.0, 1.0 - cb)
    mb = line.trait("mountain", 0.0)
    if mb:
        K = K * np.where(tags["mountain"], 1.0, 1.0 - mb)
    ob = line.trait("open", 0.0)
    if ob:
        K = K * np.where(tags["open"], 1.0, 1.0 - ob)
    return np.where(tags["land"], np.clip(K, 0, 1), 0.0)


def niche_overlap(a: SP.Lineage, b: SP.Lineage, tree: SP.Tree) -> float:
    """Competition between two lines: shared comfort ranges and ways of life, closer kin harder."""
    def ov(x, y, log=False):
        f = np.log2 if log else (lambda v: v)
        x0, x1, y0, y1 = f(max(x[0], 1e-3)), f(x[1]), f(max(y[0], 1e-3)), f(y[1])
        inter = max(0.0, min(x1, y1) - max(x0, y0))
        return inter / max(min(x1 - x0, y1 - y0), 1e-6) if inter > 0 else 0.0
    o = (0.2 + 0.8 * ov(a.temp_c, b.temp_c)) * (0.3 + 0.7 * ov(a.rain_mm, b.rain_mm, True))
    for t in ("flies", "swims", "mountain", "coastal", "subterranean"):
        if (t in a.traits) != (t in b.traits):
            o *= 0.6
    kin_a, kin_b = [a.id] + tree.ancestors(a.id), [b.id] + tree.ancestors(b.id)
    common = next((i for i, x in enumerate(kin_a) if x in kin_b), None)
    kin = 1.0 if common is not None and common <= 1 else 0.85 if common is not None else 0.7
    return float(np.clip(1.15 * o * kin, 0, 0.97))


# -- the history -----------------------------------------------------------------------------------
class History:
    def __init__(self, tree: SP.Tree, ps: R.Pass, seed: int, deep_every: int = 1, glacial_every: float = 4.0):
        self.tree, self.ps, self.grid = tree, ps, ps.grid
        g = self.grid
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.cell_km = g.spacing * R_KM
        self.cell_mkm2 = 4 * np.pi * R_KM ** 2 / g.n / 1e6
        self.lines = tree.order()
        self.idx = {l.id: k for k, l in enumerate(self.lines)}
        self.alpha = np.zeros((len(self.lines),) * 2)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay:
                    self.alpha[self.idx[a.id], self.idx[b.id]] = niche_overlap(a, b, tree)
        self.steps = self._steps(glacial_every)
        self.events: list[dict] = []
        self.origins: dict[str, dict] = {}
        self.tracks: dict[str, list] = {l.id: [] for l in self.lines}

    def _steps(self, glacial_every) -> list[Step]:
        ps, out = self.ps, []
        oldest = max(l.ago_kyr for l in self.lines)
        m = ps.run["meta"]
        now = ps.now
        # deep: the source run's keyframes before the time zoom's start
        if m.get("source_run") and m["source_run"] != "earth" and oldest > now:
            src = S.find_run(m["source_run"])
            run, arr = T.load_frames(src, ("elevation", "ice", "temperature", "precipitation", "climate", "tree_cover"))
            ts = np.array([f["t"] for f in run["frames"]])
            at = m["at_myr"]
            agos = (at - ts) * 1000 + now
            keep = np.flatnonzero((ts < at - 1e-6) & (agos <= oldest + 4000))
            if len(keep) and agos[keep].max() < oldest and keep.min() > 0:
                keep = np.r_[keep.min() - 1, keep]
            prev = None
            # a step at each keyframe, at each line's time between them (on the nearest keyframe's
            # world: 4 Myr keyframes would otherwise lump every split of those 4 Myr into one step)
            # and at the time zoom's start
            evs = sorted({l.ago_kyr for l in self.lines if now < l.ago_kyr <= agos[keep].max()} if len(keep) else set())
            sched = sorted({(float(agos[k]), int(k)) for k in keep} | {(float(a), int(keep[np.argmin(np.abs(agos[keep] - a))]))
                                                                        for a in evs} | {(float(now), int(keep[-1]))},
                           key=lambda x: -x[0]) if len(keep) else []
            for ago_k, k in sched:
                def get(k=k, run=run, arr=arr):
                    f = {n: T.frame(run, arr, n, k).astype(float) for n in ("elevation", "ice", "temperature",
                                                                               "precipitation", "climate")}
                    f["tree_cover"] = T.frame(run, arr, "tree_cover", k).astype(float) if "tree_cover" in arr else np.zeros(len(f["ice"]))
                    f["land"] = is_land(f["elevation"], f["ice"])
                    f["elevation"] = np.where(f["ice"] > 0, np.maximum(f["elevation"], 0) + f["ice"], f["elevation"])
                    return f
                if prev is not None and prev - ago_k < 1e-6:
                    continue
                out.append(Step(ago_k, 4000.0 if prev is None else float(prev - ago_k), "deep", True, get,
                                {**run["frames"][k]["stats"], "epoch": "deep"}))
                prev = ago_k
        # glacial: the time zoom's frames before the recent window
        rstart = now + ps.start
        tz_ts = ps.ts[(ps.ts < rstart - 1e-6) & (now - ps.ts <= oldest + 2)]
        prev = out[-1].ago if out else None
        last_store = None
        for t in tz_ts:
            ago = now - t
            st = last_store is None or (last_store - ago) >= glacial_every - 1e-6
            if st:
                last_store = ago
            k = int(np.argmin(np.abs(ps.ts - t)))
            out.append(Step(float(ago), 2.0 if prev is None else float(prev - ago), "glacial", st,
                            lambda t=t: ps.fields(t - now, variability=False),
                            {**ps.run["frames"][k]["stats"], "epoch": "glacial"}))
            prev = ago
        # recent: century steps with the variability
        e = ps.params.every
        for t in ps.steps:
            ago = -float(t)
            st = abs(round(t / e) * e - t) < 1e-6
            out.append(Step(ago, ps.params.step if prev is not None else ps.params.step, "recent", st,
                            lambda t=float(t): ps.fields(t), {**ps.stats(float(t)), "epoch": "recent"}))
            prev = ago
        return out

    # -- origins ---------------------------------------------------------------------------------
    def _noise(self):
        return np.exp(0.5 * self.rng.gumbel(size=self.grid.n))

    def _place_mult(self, line, tags):
        m = np.ones(self.grid.n)
        for w in self.tree.wishes:
            if w.a == line.id and w.want in SP.PLACES:
                m = m * np.where(tags[w.want], 1 + 0.5 * w.weight, 1 - 0.25 * min(w.weight, 1))
        return m

    def _seed_blob(self, k, cell, K, mask, r):
        g = self.grid
        blob = rings(int(cell), mask | (np.arange(g.n) == cell), r, g.nbr_off, g.nbr_idx) & (K > EST)
        blob[cell] = True
        self.p[k][blob] = np.maximum(self.p[k][blob], np.clip(K[blob], 0.3, 1))
        return blob

    def _origin(self, line, step, env, tags, K):
        g, k = self.grid, self.idx[line.id]
        noise = self._noise()
        why = "habitat"
        if line.origin in ("root", "arrival"):
            score = K * self._place_mult(line, tags) * noise
            if line.origin == "arrival":  # a newcomer whose hybrids are wanted comes near the other parent
                for h in self.tree.lines.values():
                    if h.origin == "hybrid" and line.id in h.parents:
                        other = [q for q in h.parents if q != line.id][0]
                        if self.active.get(other):
                            score = score * (0.2 + self._dilate(self.p[self.idx[other]] > EST, 3))
            if line.place:
                la, lo = np.radians(line.place)
                c = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
                d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
                score = score * np.exp(-(d / 600.0) ** 2) + 1e-9 * (d < 300)
                why = "given place"
            cell = int(np.argmax(score))
            if K[cell] <= EST:
                cell = int(np.argmax(np.where(tags["land"], K + 1e-6, 0) * noise))
                why += " (poor habitat)"
            self._seed_blob(k, cell, K, K > EST, 3)
        elif line.origin == "split":
            pk = self.idx[line.parents[0]]
            P = self.p[pk] > EST
            if not P.any():
                return self._origin_fallback(line, step, env, tags, K, "parent gone")
            lab, n = g.components(P)
            sizes = np.bincount(lab[P], minlength=n)
            big = int(np.argmax(sizes))
            edge = np.zeros(g.n, bool)
            np.logical_or.at(edge, g.nbr_src, ~P[g.nbr_idx])
            iso = np.where(P & (lab != big), 3.0, np.where(edge & P, 1.5, 1.0))
            # within the parent's range, or a short way beyond it (a daughter taking a new niche next door)
            near = self._dilate(P, 4) & tags["land"]
            score = np.where(P, (K + 0.02) * iso, np.where(near, 0.6 * K, 0)) * self._place_mult(line, tags) \
                * self._wish_near(line) * noise
            cell = int(np.argmax(score))
            why = ("isolated part of the parent's range" if lab[cell] != big else
                   "edge of the parent's range" if edge[cell] else "inside the parent's range") if P[cell] \
                else "beside the parent's range (new niche)"
            blob = self._seed_blob(k, cell, K, K > EST, 2)
            self.p[pk][blob & P] = 0.0
        elif line.origin == "hybrid":
            a, b = (self.p[self.idx[q]] for q in line.parents)
            O = np.minimum(a, b)
            if O.max() < EST:
                return False  # the parents haven't met yet: wait
            if line.contact:
                self.p[k] = np.where(O >= EST, O, 0.0)
                cell = int(np.argmax(O * noise))
                why = "where the parents meet"
            else:
                cell = int(np.argmax(O * (K + 0.05) * noise))
                self._seed_blob(k, cell, np.maximum(K, O), O > EST, 2)
                why = "where the parents meet (a people of its own)"
        else:  # template
            H = np.max([self.p[self.idx[q]] for q in line.parents], axis=0)
            if H.max() < EST:
                return False
            cells = []
            for _ in range(max(1, line.sites)):
                cell = int(np.argmax(np.where(H > EST, H, 0) * self._noise()))
                cells.append(cell)
                self.p[k][rings(cell, H > EST, 1, g.nbr_off, g.nbr_idx)] = 0.5
            cell = cells[0]
            why = f"{len(cells)} incursion sites in the hosts' range"
        self._record_origin(line, step, cell, why)
        return True

    def _origin_fallback(self, line, step, env, tags, K, why):
        k = self.idx[line.id]
        cell = int(np.argmax(K * self._noise()))
        self._seed_blob(k, cell, K, K > EST, 3)
        self._record_origin(line, step, cell, why)
        return True

    def _record_origin(self, line, step, cell, why):
        g = self.grid
        self.origins[line.id] = {"cell": int(cell), "lat": round(float(g.lat[cell]), 2), "lon": round(float(g.lon[cell]), 2),
                                 "ago_kyr": round(step.ago, 3), "wanted_kyr": line.ago_kyr, "epoch": step.epoch, "why": why}
        verb = {"root": "arises", "split": f"splits from {line.parents[0] if line.parents else '?'}", "arrival": "arrives",
                "hybrid": f"appears where {' and '.join(line.parents)} meet", "template": f"appears among {', '.join(line.parents)}"}
        self.events.append({"ago_kyr": round(step.ago, 3), "kind": line.origin, "line": line.id,
                            "text": f"{line.label()} {verb[line.origin]} ({why})", "lat": self.origins[line.id]["lat"],
                            "lon": self.origins[line.id]["lon"]})

    def _wish_near(self, line):
        m = np.ones(self.grid.n)
        for w in self.tree.wishes:
            if w.a == line.id and w.b and self.active.get(w.b):
                pb = self._smooth(self.p[self.idx[w.b]])
                m = m * ((1 + w.weight * pb) if w.want == "near" else (1 - 0.6 * min(w.weight, 1) * pb))
        return m

    def _dilate(self, m, r):
        g = self.grid
        m = m.copy()
        for _ in range(r):
            m2 = m.copy()
            np.logical_or.at(m2, g.nbr_src, m[g.nbr_idx])
            m = m2
        return m

    def _smooth(self, x):
        g = self.grid
        s = np.zeros(g.n)
        np.add.at(s, g.nbr_src, x[g.nbr_idx])
        return np.maximum(x, s / np.diff(g.nbr_off))

    def _end_parent(self, line, step):
        """After its last split: the parent's remaining range is shared among its children."""
        g, k = self.grid, self.idx[line.id]
        P = self.p[k] > EST
        lab = np.full(g.n, -1, np.int64)
        kids = [c for c in self.tree.living_children(line.id) if self.active.get(c)]
        for ci, c in enumerate(kids):
            lab[self.p[self.idx[c]] > EST] = ci
        if kids and P.any():
            near = nearest_label(lab, P | (lab >= 0), g.nbr_off, g.nbr_idx)
            for ci, c in enumerate(kids):
                sel = P & (near == ci)
                kc = self.idx[c]
                self.p[kc][sel] = np.maximum(self.p[kc][sel], self.p[k][sel])
        self.p[k][:] = 0
        self.active[line.id] = False
        self.ended[line.id] = step.ago

    # -- the loop --------------------------------------------------------------------------------
    def run(self, progress=lambda f, msg: None) -> dict:
        g, L = self.grid, self.lines
        self.p = np.zeros((len(L), g.n))
        self.active = {l.id: False for l in L}
        self.started, self.ended = {}, {}
        budget = np.zeros(len(L))
        frames = []
        nsteps = len(self.steps)
        t0 = time.time()
        for si, step in enumerate(self.steps):
            env = step.get()
            tags = _tags(g, env)
            Ks = {}
            # events due by this step, oldest first (lines older than the history start at its first step)
            for l in L:
                if l.id in self.started or l.ago_kyr < step.ago - 1e-9:
                    continue
                if l.extinct_kyr is not None and step.ago <= l.extinct_kyr:
                    self.started[l.id] = step.ago
                    continue
                K = Ks[l.id] = self._K(l, env, tags, step)
                if self._origin(l, step, env, tags, K):
                    self.started[l.id] = step.ago
                    self.active[l.id] = True
                    if l.parent:
                        par = self.tree.lines[l.parent]
                        if not par.persists and self.tree.living_children(par.id) and all(c in self.started for c in self.tree.living_children(par.id)) and self.active.get(par.id):
                            self._end_parent(par, step)
            mix = self._mix_ramp(step.ago)
            order = [l for l in L if self.active[l.id]]
            self.rng.shuffle(order)
            for l in order:
                k = self.idx[l.id]
                if l.extinct_kyr is not None and step.ago <= l.extinct_kyr + 1e-9:
                    self.p[k][:] = 0
                    self.active[l.id] = False
                    self.ended[l.id] = step.ago
                    self.events.append({"ago_kyr": round(step.ago, 3), "kind": "extinct", "line": l.id,
                                        "text": f"{l.label()} dies out", "lat": None, "lon": None})
                    continue
                K = Ks.get(l.id)
                if K is None:
                    K = self._K(l, env, tags, step)
                if l.overlay and l.origin == "hybrid":
                    a, b = (self.p[self.idx[q]] for q in l.parents)
                    O = np.minimum(a, b)
                    self.p[k] = np.where(O >= EST, O, 0.0)
                    continue
                self.p[k] = np.minimum(self.p[k], K)
                self.p[k][self.p[k] < EST] = 0
                if l.overlay:  # template: within its hosts, no competition
                    room = K
                else:
                    a = self.alpha[k] * (1 - MIX_DROP * mix * self._mixf(l))
                    if "agricultural" in l.traits and step.ago <= FARM_KYR:
                        a = a * 0.5
                    room = np.clip(K - a @ self.p, 0, None)
                speed = l.speed_kmyr * l.trait("speed", 1.0) * (2.0 if "agricultural" in l.traits and step.ago <= FARM_KYR else 1.0)
                if step.epoch == "deep":
                    passes = CONVERGE
                else:
                    budget[k] += speed * step.dt * 1000 / self.cell_km
                    passes = int(budget[k])
                    budget[k] -= passes
                if passes > 0:
                    sea = l.trait("sea", 0.0)
                    if step.ago <= SP.LATE_SEA_KYR:
                        sea = max(sea, l.trait("late_sea", 0.0))
                    relief = l.trait("relief", 0.6)
                    ice = env["ice"] > 0.5
                    enter = np.where(ice, 0.6 if "flies" in l.traits else 0.3, 0.5 + 0.5 * np.minimum(1, K / 0.3))
                    land_any = env["land"]
                    spread(self.p[k], room, enter, tags["elev"], relief, sea, land_any, g.nbr_off, g.nbr_idx, min(passes, CONVERGE))
                if not (self.p[k] > EST).any() and not l.overlay:
                    self.active[l.id] = False
                    self.ended[l.id] = step.ago
                    self.events.append({"ago_kyr": round(step.ago, 3), "kind": "extinct", "line": l.id,
                                        "text": f"{l.label()} dies out (no habitat left)", "lat": None, "lon": None})
            if step.store or si == nsteps - 1:
                frames.append(self._frame(step, env))
            if si % 25 == 0:
                progress(si / nsteps, f"step {si}/{nsteps} ({step.epoch}, {step.ago:g} kyr ago)")
        self.runtime = time.time() - t0
        return {"frames": frames, "present": self.p.copy()}

    def _K(self, l, env, tags, step):
        if l.overlay and l.origin == "template":
            return np.max([self.p[self.idx[q]] for q in l.parents], axis=0) * np.where(tags["land"], 1.0, 0)
        K = capacity(l, env, tags) * self._place_mult(l, tags)
        K = K * self._wish_near(l)
        if l.extinct_kyr is not None:  # dwindles toward its end
            span = min(0.3 * (l.ago_kyr - l.extinct_kyr), 20.0)
            if span > 0 and step.ago < l.extinct_kyr + span:
                K = K * max(0.0, (step.ago - l.extinct_kyr) / span)
        return np.clip(K, 0, 1)

    def _mix_ramp(self, ago):
        ms = self.tree.mixing_start_kyr
        return 0.0 if ago >= ms or ms <= 0 else 1 - ago / ms

    def _mixf(self, l):
        return l.trait("mix", 1.0)

    def _frame(self, step, env) -> dict:
        natives = np.array([not l.overlay for l in self.lines])
        P = np.where(natives[:, None], self.p, 0)
        dom = np.where(P.max(0) >= EST, P.argmax(0), 255).astype(np.uint8)
        mixn = (P >= 0.25).sum(0).astype(np.uint8)
        O = np.where(~natives[:, None], self.p, 0)
        ov = np.where(O.max(0) >= EST, O.argmax(0), 255).astype(np.uint8)
        areas = {l.id: round(float((self.p[k] >= EST).sum() * self.cell_mkm2), 2)
                 for k, l in enumerate(self.lines) if self.active[l.id]}
        for l in self.lines:
            k = self.idx[l.id]
            sel = self.p[k] >= EST
            if sel.any():
                v = (self.grid.centers[sel] * self.p[k][sel, None]).sum(0)
                v /= np.linalg.norm(v) or 1
                self.tracks[l.id].append([round(step.ago, 3), round(float(np.degrees(np.arcsin(v[2]))), 2),
                                          round(float(np.degrees(np.arctan2(v[1], v[0]))), 2), areas.get(l.id, 0)])
        return {"ago": step.ago, "epoch": step.epoch, "env": env, "peoples": dom, "peoples_mix": mixn,
                "peoples_share": np.round(np.where(dom < 255, P.max(0), 0) * 100).astype(np.uint8),
                "peoples_overlay": ov, "stats": {**step.stats, "peoples": areas}}


# -- the present ------------------------------------------------------------------------------------
def present_summary(h: History, P: np.ndarray) -> dict:
    g, tree = h.grid, h.tree
    out = {"lines": {}, "mixing_zones": [], "wishes": []}
    pres = P >= EST
    src, dst = g.nbr_src, g.nbr_idx
    for k, l in enumerate(h.lines):
        sel = pres[k]
        if not sel.any():
            continue
        lab, n = g.components(sel)
        sizes = np.sort(np.bincount(lab[sel], minlength=n))[::-1]
        nb = {}
        for j, m in enumerate(h.lines):
            if j != k and pres[j].any():
                touch = int((sel[src] & pres[j][dst]).sum())
                if touch:
                    nb[m.id] = touch
        tr = h.tracks[l.id][-1] if h.tracks[l.id] else None
        out["lines"][l.id] = {"area_mkm2": round(float(sel.sum() * h.cell_mkm2), 2), "patches": int(n),
                              "largest_patch_share": round(float(sizes[0] / sizes.sum()), 2),
                              "centroid": tr[1:3] if tr else None,
                              "neighbours": dict(sorted(nb.items(), key=lambda x: -x[1])[:8]), "overlay": l.overlay}
    natives = np.array([not l.overlay for l in h.lines])
    mix = (np.where(natives[:, None], P, 0) >= 0.25).sum(0) >= 2
    lab, n = g.components(mix)
    for z in range(n):
        sel = lab == z
        if sel.sum() < 3:
            continue
        who = [l.id for k, l in enumerate(h.lines) if natives[k] and (P[k][sel] >= 0.25).mean() > 0.2]
        c = g.centers[sel].mean(0)
        c /= np.linalg.norm(c)
        out["mixing_zones"].append({"cells": int(sel.sum()), "area_mkm2": round(float(sel.sum() * h.cell_mkm2), 2),
                                    "lat": round(float(np.degrees(np.arcsin(c[2]))), 1),
                                    "lon": round(float(np.degrees(np.arctan2(c[1], c[0]))), 1), "lines": who})
    out["mixing_zones"].sort(key=lambda z: -z["cells"])
    out["mixing_zones"] = out["mixing_zones"][:20]
    out["wishes"] = wish_scores(h, P)
    out["wish_score"] = round(sum(w["score"] * w["weight"] for w in out["wishes"]) /
                              max(sum(w["weight"] for w in out["wishes"]), 1e-9), 3) if out["wishes"] else None
    return out


def wish_scores(h: History, P: np.ndarray) -> list[dict]:
    g = h.grid
    env = h.steps[-1].get()
    tags = _tags(g, env)
    out = []
    for w in h.tree.wishes:
        a = P[h.idx[w.a]] >= EST
        if not a.any():
            out.append({**vars(w), "score": 0.0, "note": "a is gone"})
            continue
        if w.want in SP.PLACES:
            s = float(tags[w.want][a].mean())
        else:
            b = P[h.idx[w.b]] >= EST
            near = b.copy()
            for _ in range(3):  # within 3 cells of b
                near2 = near.copy()
                np.logical_or.at(near2, g.nbr_src, near[g.nbr_idx])
                near = near2
            close = float(near[a].mean()) if b.any() else 0.0
            s = min(1.0, 2.5 * close) if w.want == "near" else 1.0 - close
        out.append({**vars(w), "score": round(s, 3)})
    return out


def simulate(tree: SP.Tree, ps: R.Pass, tries: int = 4, progress=lambda f, msg: None) -> tuple[History, dict, dict]:
    """Best of `tries` seeds by the wishes' score (one try without wishes)."""
    best = None
    n = tries if tree.wishes else 1
    scores = []
    for k in range(n):
        h = History(tree, ps, tree.seed * 1000 + k)
        res = h.run(lambda f, msg, k=k: progress((k + f) / n, f"try {k + 1}/{n}: {msg}"))
        pres = present_summary(h, res["present"])
        sc = pres["wish_score"] if pres["wish_score"] is not None else 0.0
        scores.append(round(sc, 3))
        if best is None or sc > best[2]["wish_score"] + 1e-9:
            best = (h, res, pres)
    best[2]["tries"] = scores
    return best
