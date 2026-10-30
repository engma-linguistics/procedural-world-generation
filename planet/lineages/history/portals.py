"""The portals arrivals from outside the world come through (PW-697)."""

from __future__ import annotations

import numpy as np

from ...geo import arc_km
from .params import PORTAL_SEP_KM
from .gridops import _depth


class PortalsMixin:
    def portal_cells(self) -> list[dict]:
        """The portals the arrivals from outside come through (meta.portal_mode random | sites, meta.portals; PW-697):
        chosen once per try on today's land, at least PORTAL_SEP_KM apart. 'random': any ice-free land. 'sites': the
        tree's portal_sites in turn, shuffled: the deepest part of the largest forest, the middle of the largest desert,
        a coral reef coast, the foot of a volcanic cone (land beside young volcanic ground)."""
        if self._portals is not None:
            return self._portals
        tree, g = self.tree, self.grid
        env, tags = self.present()
        land = tags["land"]
        out: list[dict] = []
        if tree.portal_mode == "off" or not land.any():
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
