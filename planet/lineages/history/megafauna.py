"""Megafauna as counted animals (PW-924): dragons and the true giants, a handful per pocket of their own country.

Densities follow body mass. Damuth (1981, Nature 290:699) found population density falling as M^-0.75 across mammals;
Carbone & Gittleman (2002, Science 295:2273) found carnivores far sparser again, ~10,000 kg of prey supporting ~90 kg of a
carnivore. For a ~20 t dragon, Damuth's line gives ~0.05 per km2 for a herbivore of that mass; an apex hunter sits two to
three orders lower, ~1 per 1,000-10,000 km2 (the tree's `density`, set by the density trial PW-923). Giants (a few tonnes,
omnivores living off herds and farms) sit near ~1 per 100-500 km2, in steadings of 5-20.

They live long (dragons ~200 yr a generation, giants 50-80 yr), so few of them persist: their patches' viable number is
smaller (History.line_mvp), and pockets within flight or long range of each other are one population (linked_pockets).
They are exempt from the peoples' 300-cell range target and the remnant check: their target is to be present in most of
the world's suitable country for their kind (`suitable_reached`). Breeding is not modelled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..gridops import nbr_reduce
from ..spread import EST

if TYPE_CHECKING:
    from .model import History

LINK_KM = {"flies": 1500.0, "walks": 800.0}  # pockets this close are one population: a dragon's flight, a giant's range (JUMP_KM)
SUITABLE = 0.5  # a cell is suitable country for a kind where its habitat suitability (History._suit) is at least this
TARGET_SHARE = 0.5  # the target: at least this share of the suitable country lies in patches the kind reaches
COUNTRY = {"wetland": "swamp", "forest": "forest", "jungle": "jungle", "volcanic": "volcano country", "mountain": "mountains",
           "tundra": "tundra", "desert": "desert", "hills": "hills", "coast": "coast", "steppe": "steppe", "island": "island",
           "open": "open country", "shore": "coast", "sea": "sea"}


def link_km(line) -> float:
    return LINK_KM["flies" if "flies" in line.traits else "walks"]


def linked_pockets(h: History, held: np.ndarray, km: float) -> tuple[np.ndarray, int]:
    """Components of `held`, joining pockets within `km` of each other (over land and sea): the held cells are grown by half
    the reach, the grown mask labelled, and the labels read back on the held cells (as grid.components: -1 outside, count)."""
    g = h.grid
    grown = held.copy()
    for _ in range(max(1, int(round(0.5 * km / h.cell_km)))):
        grown |= nbr_reduce(g, np.logical_or, grown[g.nbr_idx])
    lab, _ = g.components(grown)
    lab = np.where(held, lab, -1)
    used = np.unique(lab[held])
    remap = np.full(int(lab.max()) + 2 if held.any() else 1, -1)
    remap[used] = np.arange(len(used))
    return np.where(held, remap[np.maximum(lab, 0)], -1), len(used)


def _country(line, tags: dict, sel: np.ndarray) -> str:
    best, word = 0.0, None
    for t in [*line.prefers, "wetland", "forest", "jungle", "desert", "tundra", "volcanic", "mountain", "hills", "coast", "steppe"]:
        if t in tags and isinstance(tags[t], np.ndarray) and tags[t].dtype == bool:
            s = float(tags[t][sel].mean())
            if s > best + 0.05 or (word is None and s > 0):
                best, word = s, COUNTRY.get(t, t)
    if line.marine:
        return "coastal sea"
    return word if best >= 0.25 else "country"


def groups_note(line, n: int) -> str:
    lo, hi = line.group_size or (1.0, 1.0)
    if hi <= 3:
        return "solitary" if n <= 1 else ("a mated pair" if n == 2 else "mostly solitary, now and then a pair with young")
    mean = 0.5 * (lo + hi)
    st = max(1, int(round(n / mean)))
    return f"{st} steading{'s' if st > 1 else ''} of ~{max(int(lo), int(round(n / st)))}"


def summary(h: History, P: np.ndarray, tags: dict) -> dict:
    """Per megafauna line alive at the present: the count, its pockets (each with a count, place, country and groups),
    counts by landmass, and the target (share of its suitable country reached)."""
    g, out = h.grid, {}
    area = h.cell_mkm2 * 1e6
    S = h._suit() if getattr(h, "_K_now", None) else None
    lm, names = h.cross.label, {nm["rank"]: nm["name"] for nm in h.cross.names}
    for k, l in enumerate(h.lines):
        if not l.megafauna:
            continue
        held = P[k] >= EST
        if not held.any():
            continue
        rng = np.random.default_rng((h.seed, 924, k))
        exp = np.where(held, P[k], 0.0) * h.dens[k] * area
        lab, n = g.components(held)
        pockets = []
        for z in range(n):
            sel = lab == z
            e = float(exp[sel].sum())
            c = int(np.floor(e) + (rng.random() < e - np.floor(e)))  # (counts, not means: unbiased rounding of the expected number)
            if c <= 0:
                continue
            v = g.centers[sel].mean(0)
            v /= np.linalg.norm(v)
            m = lm[sel]
            m = m[m >= 0]
            land = int(np.bincount(m).argmax()) if m.size else None
            pockets.append({"count": c, "expected": round(e, 2), "cells": int(sel.sum()), "km2": int(round(sel.sum() * area)),
                            "lat": round(float(np.degrees(np.arcsin(v[2]))), 1), "lon": round(float(np.degrees(np.arctan2(v[1], v[0]))), 1),
                            "country": _country(l, tags, sel), "landmass": land, "landmass_name": names.get(land),
                            "groups": groups_note(l, c)})
        pockets.sort(key=lambda p: -p["count"])
        by: dict[str, int] = {}
        for p in pockets:
            if p["landmass"] is not None:
                by[str(p["landmass"])] = by.get(str(p["landmass"]), 0) + p["count"]
        r = {"count": int(sum(p["count"] for p in pockets)), "pockets": len(pockets), "per_km2": round(float(h.dens[k]), 6),
             "one_per_km2": int(round(1.0 / max(h.dens[k], 1e-12))), "generation_yr": l.generation_yr,
             "group_size": list(l.group_size) if l.group_size else None,
             "by_landmass": dict(sorted(by.items(), key=lambda x: -x[1])), "pocket_list": pockets}
        if S is not None and not l.marine:
            suit = S[k] >= SUITABLE
            if suit.any():
                sl, sn = g.components(suit)
                hit = np.zeros(sn, bool)
                hit[np.unique(sl[suit & held])] = True
                r["suitable_km2"] = int(round(suit.sum() * area))
                r["suitable_reached"] = round(float(hit[sl[suit]].mean()), 2)
                r["target_met"] = bool(r["suitable_reached"] >= TARGET_SHARE)
        out[l.id] = r
    return out


def line_text(lid: str, name: str, r: dict, n: int = 3) -> str:
    """One line for the report and the brief: '~12 black dragons in 9 pockets (1 per 5,000 km2): 2 in the swamp at 3.1, 10.2 ...'."""
    tops = "; ".join(f"{p['count']} in the {p['country']} at {p['lat']:g}, {p['lon']:g}"
                     + (f" ({p['landmass_name']})" if p.get("landmass_name") else "") for p in r["pocket_list"][:n])
    tgt = f", in {round(100 * r['suitable_reached'])}% of their country" if "suitable_reached" in r else ""
    return f"~{r['count']} {name} in {r['pockets']} pockets (1 per {r['one_per_km2']:,} km²{tgt}): {tops}"
