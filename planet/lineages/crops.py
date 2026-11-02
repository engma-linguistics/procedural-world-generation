"""Domesticated plants (PW-721): the staple crops, each first cultivated somewhere, carried by farmers (and by canoe) and
adding to what farming can feed. The constants are one table, `crop_defs.TABLE`, in the animals' row shape; the machinery
(`animals.Stock`: a drawn date, a homeland on the wild range, a front over peopled land, crossings by boat) is the same,
so this is `Animals` with another table and these differences:
  - who first cultivates a crop: farmers (their farm share) and hunters / foragers on the range (the `forage` share, PW-718);
  - several homelands per world: a landmass that already has a first cultivation is less likely to get another
    (`PENALTY` per crop already there), so wheat, rice, maize and the tubers come from different lands where there are any;
  - seed goes by every craft (size 0), faster over land (about 1 km/yr);
  - a people takes a crop up (knows it) once the crop has stood on a fifth of its land for LAG_KYR / propensity (PW-1373 B): farming
    peoples at once, hunting peoples ~10x slower, its first cultivators at once (the share of its land it then farms is the land's:
    lineages.ladder);
  - a known crop adds farm capacity where it can be grown (`grow`: the wild range's climate windows widened, past where it
    grew wild) x the people's adoption (share of its land where the crop is known x its propensity) x its farm share;
  - `crop_know` per cell (0..1): how much of a staple diet the crops known and growable there make (landuse.py scales the
    cropland by it: no fields without a crop to sow).
Stored per frame as two uint64 bit-flag layers `crop_wild` and `crop_known` (bit i = crop_defs.TABLE[i]).
"""

from __future__ import annotations

import numpy as np

from . import crop_defs as CD
from .animals import TOOK_UP, Animals, Stock
from .spread import EST

PENALTY = 0.35  # x per other first cultivation already on a landmass (a landmass with one is a third as likely again)
K_CAP = 0.8  # the most that crops together add to a farming people's capacity
GROWN_MIN = 0.25  # the crop is "known" in a cell (the stored layer) where it is known and can be grown (grow range >= this)
# a people knows a crop (takes it up: lineages.ladder farms its land) once the crop has stood on animals.TOOK_UP of its land...
LAG_KYR = 0.4  # ...for LAG_KYR / propensity ** LAG_POW kyr (PW-1373 B, owner 11-02): a people inclined to farm (propensity ~1) at once, a
LAG_POW = 1.0  # hunting people (0.1) ~10x slower (4 kyr). LAG: the Baltic and Scandinavian foragers beside the first farmers took ~1-1.5 kyr
#                (Zvelebil & Rowley-Conwy 1984's availability phase; a forager's propensity is ~0.25 here). LAG_POW 0.7 makes it 5x.


def learn_lag(prop) -> np.ndarray:
    """Per line, kyr: how long a crop must stand on TOOK_UP of a people's land before the people takes it up (inf: propensity 0)."""
    p = np.asarray(prop, float)
    return np.where(p > 0, LAG_KYR / np.maximum(p, 1e-9) ** LAG_POW, np.inf)


class Crops(Animals):
    penalty = PENALTY

    def _make(self, tree) -> list:
        stocks = [Stock(self.h, a, a.id in tree.crops_force, tree.crops_at, self) for a in CD.resolve(tree.crops, tree.crops_force, tree.mode)]
        self.lag = [learn_lag(s.prop) for s in stocks]
        for s in stocks:
            s.stood = np.zeros(len(s.prop))
        return stocks

    def step(self, step, env, tags, p, native) -> None:
        if step.epoch == "deep":
            return
        self.ago = step.ago
        goods = self.h.goods
        if goods is not None and "fertile" in goods:  # the soil: the world's farmland (the plates have moved in the deep epochs)
            tags = {**tags, "soil": goods["fertile"]}
        pn = p[native]
        held = pn >= EST
        peopled = held.any(0)
        for s in self.stocks:
            s.step(step, env, tags, p, native, self.sea, peopled)
        W = np.where(held, pn, 0.0)
        tot = W.sum(1)
        ok = tot > 0
        den = np.where(ok, tot, 1.0)
        RD = np.stack([s.rd for s in self.stocks]) if self.stocks else np.zeros((0, W.shape[1]))
        sh = (W @ RD.T) / den[:, None] if len(RD) else np.zeros((len(native), 0))
        for j, s in enumerate(self.stocks):
            s.gk = np.clip(s.grow / 0.5, 0, 1) * (s.rd >= EST)  # (where it is known and grows, per step, for k_mult and know)
            s.share[:] = 0.0
            s.share[native] = np.where(ok, sh[:, j], 0.0)
            s.adopt[:] = s.share * s.prop
            if not s.tamed:
                continue
            on = (s.share >= TOOK_UP) & (s.prop > 0)
            s.stood[on] += step.dt  # (PW-1373 B: how long the crop has stood on a fifth of the people's land)
            first = {t["line"] for t in s.tamed}
            for k in np.flatnonzero(on):
                if int(k) not in s.took_up and (s.stood[k] >= self.lag[j][k] - 1e-9 or self.h.lines[k].id in first):
                    s.took_up[int(k)] = round(step.ago, 3)

    def speed_mult(self, k: int) -> float:
        return 1.0

    def k_mult(self, k: int):
        """Farm capacity added by the crops known where they grow (x the people's adoption and farm share)."""
        add = None
        for s in self.stocks:
            if s.adopt[k] <= 0 or s.sh["farm"][k] <= 0:
                continue
            t = (s.adopt[k] * s.sh["farm"][k] * s.a.k["farm"]) * s.gk
            add = t if add is None else add + t
        return 1.0 if add is None else 1.0 + np.minimum(add, K_CAP)

    def know(self) -> np.ndarray:
        """Per cell, 0..1: the staple crops known and growable there (weights summed, capped at 1)."""
        n = self.h.grid.n
        v = np.zeros(n)
        for s in self.stocks:
            v += s.a.weight * (s.rd >= EST) * np.clip(s.grow / 0.5, 0, 1)
        return np.minimum(v, 1.0)

    def present_cells(self) -> dict:
        """The present's per-cell crop facts, 0..1: `know` (above) and `straw` (the straw the staples leave, weighted by how much of
        a staple each is) for the cropland and the fuels (landuse.py, fuels.py)."""
        n = self.h.grid.n
        w, st = np.zeros(n), np.zeros(n)
        for s in self.stocks:
            x = s.a.weight * (s.rd >= EST) * np.clip(s.grow / 0.5, 0, 1)
            w += x
            st += x * s.a.straw
        return {"know": np.minimum(w, 1.0), "straw": np.where(w > 0, st / np.maximum(w, 1e-9), 0.0)}

    def frame_layers(self) -> dict:
        n = self.h.grid.n
        known, wild = np.zeros(n, np.uint64), np.zeros(n, np.uint64)
        for s in self.stocks:
            known |= (((s.rd >= EST) & (s.grow >= GROWN_MIN)) * (1 << s.a.bit)).astype(np.uint64)
            wild |= ((s.wild >= 0.35) * (1 << s.a.bit)).astype(np.uint64)
        return {"crop_known": known, "crop_wild": wild}

    def summary(self, P: np.ndarray) -> dict:
        h = self.h
        stocks = {s.a.id: s.summary(P) for s in self.stocks}
        for s in self.stocks:  # (where it is grown at the present, and the share of each people's farmland it holds)
            stocks[s.a.id]["grown_mkm2"] = round(float(((s.rd >= EST) & (s.grow >= 0.25)).sum() * h.cell_mkm2), 2)
            stocks[s.a.id]["straw"] = s.a.straw
            stocks[s.a.id]["weight"] = s.a.weight
        know = self.know()
        land = h.cross.label >= 0
        return {"mode": h.tree.mode, "stocks": stocks,
                "know_mean_peopled": round(float(know[land & (P.max(0) >= EST)].mean()) if (land & (P.max(0) >= EST)).any() else 0.0, 3)}
