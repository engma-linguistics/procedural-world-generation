"""The portals arrivals from outside the world come through (PW-697), in force (PW-1150), and wandering (lane 78).

- random / sites: portals placed once per try on today's land (portal_cells).
- wandering: each plane (an arrival's `plane`: the Feywild...) touches the world at "thinnings", points fixed in the plane's own frame,
  which slides over the world as a rigid rotation about a seeded pole (meta.portal_drift_kmkyr): the hotspot pattern turned round
  (tectonics.volcanism.hotspots: plumes fixed in the mantle while the plates slide over them). A thinning opens (a Poisson birth, as a
  plume's: the plane keeps about meta.portals open), stays open U(0.4, 1.6) x meta.portal_open_kyr (a plume's life is drawn so), is
  placed on the 'sites' scores with ~100 km of scatter (a plume rises on mantle.plume_odds plus a 100 km offset) and drifts with its
  plane; it lets the plane's arrivals through where it stands over land they can live on (within PORTAL_KM), then closes.
- An arrival's `founders` (people, in all its waves) come `waves` times, meta.wave_kyr apart, split over the portals it comes
  through (`portals`, else meta.portals); each portal's share holds the country round it until it carries that many (founding.py).
Arrivals only come in; nothing goes out.
"""

from __future__ import annotations

import zlib

import numpy as np

from ...geo import R_KM, arc_km
from ...tectonics.plates import rotation
from ..spread import EST as EST_
from .founding import found_people
from .gridops import _depth
from .params import PORTAL_FAR_KM, PORTAL_KM, PORTAL_SEP_KM, PORTAL_WAIT_KYR, SCATTER_KM


class PortalsMixin:
    def _site_scores(self, tags) -> dict:
        """The 'sites' kinds' scores on the present land (forest depth, desert depth, reef coast, the foot of a volcano)."""
        tree, g = self.tree, self.grid
        land = tags["land"]
        scores = {}
        if "forest" in tree.portal_sites:
            scores["forest"] = _depth(g, tags["forest"])
        if "desert" in tree.portal_sites:
            scores["desert"] = _depth(g, tags["desert"])
        if "reef" in tree.portal_sites and self.goods is not None and "coral" in self.goods:
            scores["reef"] = np.where(land, np.asarray(self.goods["coral"], float), 0.0)
        if "volcano" in tree.portal_sites and tags["volcanic"].any():
            v = tags["volcanic"]
            foot = self._dilate(v, 2) & land & ~v
            scores["volcano"] = foot * (1.0 + self._dilate(v, 1) * 0.5)
        return scores

    def portal_cells(self) -> list[dict]:
        """The portals the arrivals from outside come through (meta.portal_mode random | sites, meta.portals; PW-697):
        chosen once per try on today's land, at least PORTAL_SEP_KM apart. 'random': any ice-free land. 'sites': the
        tree's portal_sites in turn, shuffled: the deepest part of the largest forest, the middle of the largest desert,
        a coral reef coast, the foot of a volcanic cone (land beside young volcanic ground). 'wandering': none fixed (_open_now)."""
        if self._portals is not None:
            return self._portals
        tree, g = self.tree, self.grid
        env, tags = self.present()
        land = tags["land"]
        out: list[dict] = []
        if tree.portal_mode in ("off", "wandering") or not land.any():
            self._portals = out
            return out
        noise = self.rng.random(g.n)
        free = land.copy()

        def pick(score, kind):
            sc = np.where(free, score, 0.0)
            if sc.max() <= 0:
                return False
            c = int(np.argmax(sc + 1e-6 * noise * (sc > 0)))
            out.append({"cell": c, "kind": kind, "lat": round(float(g.lat[c]), 2), "lon": round(float(g.lon[c]), 2)})
            d = arc_km(g.centers @ g.centers[c])
            free[d < PORTAL_SEP_KM] = False
            return True

        if tree.portal_mode == "random":
            for _ in range(tree.portals):
                if not pick(land * 1.0, "random"):
                    break
        else:
            scores = self._site_scores(tags)
            kinds = [k for k in tree.portal_sites if k in scores]
            if not kinds:  # (none of those places on this world: anywhere)
                kinds = ["random"]
                scores["random"] = land * 1.0
            order = [kinds[i] for i in self.rng.permutation(len(kinds))]
            for i in range(tree.portals):
                for k in order[i % len(order):] + order[:i % len(order)]:  # (this kind first, any other if it has no room left)
                    if pick(scores[k], k):
                        break
        self._portals = out
        return out

    # -- wandering thinnings ----------------------------------------------------------------------------
    def _plane(self, name: str, ago: float) -> dict:
        """A plane's state (wandering mode), made the first time it is asked for: its drift pole and rate, and a full set of
        thinnings of mixed ages (as volcanism.hotspots starts with a full set of plumes)."""
        planes = self.__dict__.setdefault("_planes", {})
        if name in planes:
            return planes[name]
        rng = np.random.default_rng((self.seed, 1150, zlib.crc32(name.encode())))
        pole = rng.normal(size=3)
        pole /= np.linalg.norm(pole)
        n_open = max([self.tree.portals] + [l.portal_n or 0 for l in self.lines if l.origin == "arrival" and l.plane == name])
        P = {"name": name, "pole": pole, "omega": self.tree.portal_drift_kmkyr / R_KM, "rng": rng, "n": n_open, "thin": [], "seq": 0,
             "ago": ago, "log": []}
        planes[name] = P
        for _ in range(n_open):
            life = rng.uniform(0.4, 1.6) * self.tree.portal_open_kyr
            self._thin_born(P, ago + rng.uniform(0, life), life, ago)
        return P

    def _thin_born(self, P: dict, born: float, life: float, now: float):
        """A new thinning of plane P, born `born` kyr ago, placed (at `now`) on the site scores (or any land) with scatter."""
        g, rng = self.grid, P["rng"]
        env, tags = self.present()
        sc = self._site_scores(tags) if self.tree.portal_sites else {}
        w = sum(sc.values()) if sc else None
        w = np.asarray(w if w is not None and np.max(w) > 0 else tags["land"] * 1.0, float) + 1e-3 * tags["land"]
        c = int(rng.choice(g.n, p=w / w.sum()))
        v = g.centers[c] + rng.normal(size=3) * SCATTER_KM / R_KM
        v /= np.linalg.norm(v)
        # (the frame position: un-rotate by the drift since its birth, so that at `born` it stood where it was placed at `now`)
        v = rotation(P["pole"] * P["omega"] * (born - now)).T @ v
        P["thin"].append({"id": P["seq"], "pos": v, "born": born, "life": life, "opened": False})
        P["seq"] += 1

    def _thin_cell(self, P: dict, t: dict, ago: float) -> int:
        """The cell a thinning stands over `ago` kyr before the present (its plane's rotation since its birth)."""
        v = rotation(P["pole"] * P["omega"] * (t["born"] - ago)) @ t["pos"]
        return int(self.grid.locate(v[None])[0])

    def _plane_step(self, P: dict, step):
        """Births and closings of plane P's thinnings up to this step (a Poisson rate keeping about P['n'] open)."""
        dt = max(P["ago"] - step.ago, 0.0)
        if dt > 0:
            rng = P["rng"]
            for _ in range(int(rng.poisson(P["n"] * dt / self.tree.portal_open_kyr))):
                life = rng.uniform(0.4, 1.6) * self.tree.portal_open_kyr
                self._thin_born(P, step.ago + rng.uniform(0, dt), life, step.ago)
            P["ago"] = step.ago
        keep = []
        for t in P["thin"]:
            if t["born"] - t["life"] > step.ago:  # (closed)
                if t["opened"]:
                    P["log"].append({"id": t["id"], "closed_kyr": round(float(t["born"] - t["life"]), 3)})
                continue
            keep.append(t)
        P["thin"] = keep

    def _open_now(self, plane: str, step) -> list[dict]:
        """The plane's thinnings open at this step, as portals: [{cell, kind, lat, lon, id}]."""
        P = self._plane(plane, step.ago)
        self._plane_step(P, step)
        g, out = self.grid, []
        for t in P["thin"]:
            if t["born"] + 1e-9 >= step.ago:
                c = self._thin_cell(P, t, step.ago)
                out.append({"cell": c, "kind": f"thinning to the {plane}", "id": t["id"], "lat": round(float(g.lat[c]), 2),
                            "lon": round(float(g.lon[c]), 2)})
                if not t["opened"]:
                    t["opened"] = True
                    P["log"].append({"id": t["id"], "opened_kyr": round(float(t["born"]), 3), "lat": out[-1]["lat"], "lon": out[-1]["lon"]})
        return out

    # -- arrivals through the portals ---------------------------------------------------------------------
    def _portals_for(self, line, step) -> list[dict]:
        return self._open_now(line.plane, step) if self.tree.portal_mode == "wandering" else self.portal_cells()

    def _wave_share(self, line) -> float | None:
        if line.founders is None:
            return None
        return line.founders / max(1, line.waves)

    def _land_wave(self, line, k, K, noise, step, pull=None, first=True):
        """One wave of an arrival through the portals it can live near (PW-697, PW-1150): at each within PORTAL_KM of country it can
        hold (static portals: else the nearest within PORTAL_FAR_KM), at most its portal count. Returns [(cell, kind)] seeded; with
        `founders` each portal's share is founded in full (found_people), else the first portal's patch is left to the caller (today's)
        and the others hold 3 rings."""
        g = self.grid
        near, far = [], []
        for pt in self._portals_for(line, step):
            d = arc_km(g.centers @ g.centers[pt["cell"]])
            ok = (d < PORTAL_KM) & (K > EST_)
            if ok.any():
                near.append((int(np.argmax(np.where(ok, K * noise, 0))), pt["kind"]))
                continue
            if self.tree.portal_mode != "wandering":
                ok = (d < PORTAL_FAR_KM) & (K > EST_)
                if ok.any():
                    far.append((float(d[ok].min()), int(np.argmax(np.where(ok, K * noise * np.exp(-d / 1000), 0))), pt["kind"]))
        if not near and far:
            f = min(far)
            near = [(f[1], f[2])]
        if not near:
            return []
        if pull is not None:  # (the portal nearest the other parent first: PW-852)
            near.sort(key=lambda x: -pull[x[0]])
        if line.portal_n is not None:
            near = near[:line.portal_n]
        share = self._wave_share(line)
        if share is not None:
            each = share / len(near)
            got = 0.0
            for c, _ in near:
                _, carried = found_people(self, k, c, K, each, PORTAL_KM)
                got += min(carried, each)
            self.__dict__.setdefault("wave_log", {}).setdefault(line.id, []).append(
                {"ago_kyr": round(float(step.ago), 3), "portals": len(near), "people": int(share), "carried": int(got)})
        else:
            for c, _ in (near if not first else near[1:]):
                self._seed_blob(k, c, K, K > EST_, 3)
            self.__dict__.setdefault("wave_log", {}).setdefault(line.id, []).append(
                {"ago_kyr": round(float(step.ago), 3), "portals": len(near), "people": None})
        return near

    def _through_portals(self, line, k, K, noise, pull, step):
        """The first wave of an arrival (from origins._origin_new): (cell, why, seeded) through the portals; False to wait for a
        wandering thinning over land it can live on (up to PORTAL_WAIT_KYR, then None: its best habitat, as without portals); None
        when there are no portals."""
        if self.tree.portal_mode == "off":
            return None
        if self.tree.portal_mode != "wandering" and not self.portal_cells():
            return None
        near = self._land_wave(line, k, K, noise, step, pull, first=True)
        if not near:
            if self.tree.portal_mode == "wandering" and step.ago > line.ago_kyr - PORTAL_WAIT_KYR:
                return False
            return None
        self.__dict__.setdefault("_wave_due", {})[line.id] = [step.ago - i * self.tree.wave_kyr for i in range(1, line.waves)]
        why = f"through {'a portal' if len(near) == 1 else str(len(near)) + ' portals'} ({', '.join(sorted({f[1] for f in near}))})"
        return near[0][0], why, line.founders is not None

    def _waves(self, step, env, tags, Ks):
        """An arrival's later waves (PW-1150), when due, through the portals open then; and the planes' thinnings (wandering)."""
        if self.tree.portal_mode == "wandering":
            for name in {l.plane for l in self.lines if l.origin == "arrival"} & set(self.__dict__.get("_planes", {})):
                self._open_now(name, step)  # (keeps the planes' births and closings, and their log, going to the present)
        due = self.__dict__.get("_wave_due")
        if not due:
            return
        for lid, agos in list(due.items()):
            if not agos or agos[0] < step.ago - 1e-9:
                continue
            l = self.tree.lines[lid]
            k = self.idx[lid]
            if not self.active.get(lid):
                due[lid] = []
                continue
            K = self._K(l, env, tags, step)
            near = self._land_wave(l, k, K, self._noise(l), step, None, first=False)
            if near:
                agos.pop(0)
                self._sync(k)
                self._event_at(step.ago, "wave", l, f"another wave of {l.label()} comes through "
                               f"{'a portal' if len(near) == 1 else str(len(near)) + ' portals'}", near[0][0])
            elif step.ago < agos[0] - PORTAL_WAIT_KYR:  # (no open portal over its land for that long: the wave does not come)
                agos.pop(0)

    def portal_report(self) -> dict | None:
        """The run's portals for the output: the fixed ones, or each plane's thinnings (opened, closed, where)."""
        if self.tree.portal_mode == "wandering":
            return {name: P["log"] for name, P in self.__dict__.get("_planes", {}).items()}
        return None

