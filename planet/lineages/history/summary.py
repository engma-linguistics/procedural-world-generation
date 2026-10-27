"""The present's summary of a history: per people, mixing zones, landmasses, wishes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .. import spec as SP
from ..crossing import corridor
from ..spread import EST
from .params import APART_CONTESTED, NEAR_SCORE_KM
from ..gridops import nbr_reduce
from .habitat import capacity
from .tags import _tags

if TYPE_CHECKING:
    from .model import History


def present_summary(h: History, P: np.ndarray) -> dict:
    g, tree = h.grid, h.tree
    out = {"lines": {}, "mixing_zones": [], "wishes": [], "animals": h.animals.summary(P) if h.animals is not None else None,
           "crops": h.crops.summary(P) if h.crops is not None else None}
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
        if l.group_of:
            out["lines"][l.id]["group_of"] = l.group_of
        if l.overlay and l.origin == "hybrid":  # (the land it holds as a people of its own, its parents apart)
            out["lines"][l.id]["own_mkm2"] = round(float((h._linger[k] & sel).sum() * h.cell_mkm2), 2)
        # numbers: the people (presence x density x area), by present-day landmass
        pc = h.population(k, P)
        lm = h.cross.label
        by = np.bincount(lm[(lm >= 0) & (pc > 0)], weights=pc[(lm >= 0) & (pc > 0)], minlength=len(h.cross.names))
        top = np.argsort(-by)[:6]
        d = l.demos()
        out["lines"][l.id].update(population=int(pc.sum()), density=round(d["density"], 4),
                                  band_km2=round(SP.BAND / d["density"], 1),
                                  by_landmass={str(int(m)): int(by[m]) for m in top if by[m] >= 1},
                                  faded_patches=h.faded.get(l.id, 0))
    natives = np.array([not l.overlay and not l.marine for l in h.lines])  # (the land peoples: the sea ones do not mix or hold land)
    Pw = h.rollup(np.where(natives[:, None], P, 0))  # (peoples as wholes: a people mixing with its own groups is one people)
    mix = (Pw >= 0.25).sum(0) >= 2
    env = h.steps[-1].get()
    tags = _tags(g, env, h._chains, h._volcanic())
    corr = corridor(tags, env, h.flow)
    land = tags["land"]
    out["mixing"] = {"area_mkm2": round(float(mix.sum() * h.cell_mkm2), 2),
                     "land_share": round(float(mix[land].mean()), 3) if land.any() else 0.0,
                     # share of corridor land (contact >= 0.7) and of closed land (< 0.4) that is mixed
                     "in_corridors": round(float(mix[land & (corr >= 0.7)].mean()), 3) if (land & (corr >= 0.7)).any() else None,
                     "corridor_share": round(float((corr[land] >= 0.7).mean()), 3) if land.any() else 0.0,
                     "in_closed": round(float(mix[land & (corr < 0.4)].mean()), 3) if (land & (corr < 0.4)).any() else None}
    held = (np.where(natives[:, None], P, 0) >= EST).any(0)
    lm = h.cross.label
    out["landmasses"] = [{**nm, "held_share": round(float(held[(lm == nm["rank"]) & land].mean()), 2)
                          if ((lm == nm["rank"]) & land).any() else 0.0}
                         for nm in h.cross.names if nm["area_mkm2"] >= 0.05][:30]
    out["empty_continents"] = [nm["name"] for nm in out["landmasses"] if nm["kind"] == "continent" and nm["held_share"] < 0.05]
    # who found each landmass first (any native people, at its origin or on arrival), and who came after
    for nm in out["landmasses"]:
        arr = sorted(((r["ago_kyr"], lid, r) for lid, got in h.cross.reached.items()
                      for m, r in got.items() if m == nm["rank"] and not h.tree.lines[lid].overlay), key=lambda x: -x[0])
        nm["discovered"] = ({"by": arr[0][1], "ago_kyr": arr[0][0], "how": arr[0][2]["how"],
                             **({"gap_km": arr[0][2]["gap_km"]} if "gap_km" in arr[0][2] else {})} if arr else None)
        # (the first of today's peoples to get there: the stems found most land in deep time)
        now = [x for x in arr if x[1] in out["lines"]]
        nm["settled_by"] = ({"by": now[0][1], "ago_kyr": now[0][0], "how": now[0][2]["how"],
                             **({"gap_km": now[0][2]["gap_km"]} if "gap_km" in now[0][2] else {})} if now else None)
        nm["arrivals"] = [{"by": lid, "ago_kyr": a, "how": r["how"]} for a, lid, r in arr[:12]]
        nm["population"] = {lid: v["by_landmass"][str(nm["rank"])] for lid, v in out["lines"].items()
                            if str(nm["rank"]) in v.get("by_landmass", {})}
    lab, n = g.components(mix)
    for z in range(n):
        sel = lab == z
        if sel.sum() < 3:
            continue
        who = [l.id for k, l in enumerate(h.lines) if natives[k] and (Pw[k][sel] >= 0.25).mean() > 0.2]
        c = g.centers[sel].mean(0)
        c /= np.linalg.norm(c)
        out["mixing_zones"].append({"cells": int(sel.sum()), "area_mkm2": round(float(sel.sum() * h.cell_mkm2), 2),
                                    "lat": round(float(np.degrees(np.arcsin(c[2]))), 1),
                                    "lon": round(float(np.degrees(np.arctan2(c[1], c[0]))), 1), "lines": who})
    out["mixing_zones"].sort(key=lambda z: -z["cells"])
    out["mixing_zones"] = out["mixing_zones"][:20]
    out["wishes"] = wish_scores(h, P, tags)
    out["peoples"] = people_rollup(h, P, out["lines"])
    # lines that should be alive at the present (leaves not set to die out) but aren't
    out["lost"] = [l.id for l in tree.leaves() if l.extinct_kyr is None and l.id not in out["lines"]]
    # (an 'apart' wish whose niches rarely meet has nothing to keep apart: left out of the average, PW-682;
    # wish_score_raw: every wish, an 'apart' scored as 1 - closeness, as before)
    cw = [w for w in out["wishes"] if w.get("contested", True)]
    out["wish_score"] = round(sum(w["score"] * w["weight"] for w in cw) / max(sum(w["weight"] for w in cw), 1e-9), 3) if cw else None
    out["wish_score_raw"] = round(sum(w.get("raw", w["score"]) * w["weight"] for w in out["wishes"]) /
                                  max(sum(w["weight"] for w in out["wishes"]), 1e-9), 3) if out["wishes"] else None
    out["wishes_counted"] = len(cw)
    return out


def people_rollup(h: History, P: np.ndarray, lines: dict) -> dict:
    """Per people with groups (PW-665): the people as a whole, its own row and its groups' rows together:
    area and patches of their joint range, population and by-landmass numbers summed, each part's share."""
    out = {}
    g = h.grid
    for l in h.lines:
        gs = h.tree.groups_of(l.id)
        if not gs:
            continue
        parts = [x for x in [l.id, *gs] if x in lines]
        if not parts:
            continue
        sel = h.whole(l.id, P) >= EST
        _, n = g.components(sel) if sel.any() else (None, 0)
        pop = sum(lines[x].get("population", 0) for x in parts)
        by: dict[str, int] = {}
        for x in parts:
            for m, v in lines[x].get("by_landmass", {}).items():
                by[m] = by.get(m, 0) + v
        out[l.id] = {"groups": gs, "living": parts, "area_mkm2": round(float(sel.sum() * h.cell_mkm2), 2),
                     "patches": int(n), "population": int(pop),
                     "by_landmass": dict(sorted(by.items(), key=lambda x: -x[1])[:6]),
                     "shares": {x: round(lines[x].get("population", 0) / max(pop, 1), 3) for x in parts}}
    return out


def _within(g, mask: np.ndarray, cell_km: float) -> np.ndarray:
    """Cells within NEAR_SCORE_KM of the mask."""
    near = mask.copy()
    for _ in range(max(1, int(round(NEAR_SCORE_KM / cell_km)))):
        near = near | nbr_reduce(g, np.logical_or, near[g.nbr_idx])
    return near


def _niche_closeness(h: History, w, tags: dict) -> float:
    """Share of a's habitat (own niche at the present, K >= 0.25, its groups' too) within NEAR_SCORE_KM of b's
    habitat: how close the two would sit with no wish and no competition."""
    env = h.steps[-1].get()

    def hab(lid):
        ids = [lid, *h.tree.groups_of(lid)]
        return np.any([capacity(h.tree.lines[x], env, tags) >= 0.25 for x in ids], axis=0) & (tags["land"] | tags["sea"])
    ha, hb = hab(w.a), hab(w.b)
    if not ha.any() or not hb.any():
        return 0.0
    return float(_within(h.grid, hb, h.cell_km)[ha].mean())


def wish_scores(h: History, P: np.ndarray, tags: dict | None = None) -> list[dict]:
    g = h.grid
    if tags is None:
        tags = _tags(g, h.steps[-1].get(), h._chains, h._volcanic())
    out = []
    for w in h.tree.wishes:
        a = h.whole(w.a, P) >= EST  # (a people with groups: as a whole)
        if not a.any():
            out.append({**vars(w), "score": 0.0, "note": "a is gone"})
            continue
        if w.want in SP.PLACES:
            # half: how much of that kind of place the line holds (half of it is full marks); half: how much
            # of its range is there, against how common the place is (8x its share of the land, at most 1/2)
            t = tags[w.want] & tags["land"]
            if not t.any():
                out.append({**vars(w), "score": 0.0, "note": f"no {w.want} on this world"})
                continue
            base = t.sum() / max(tags["land"].sum(), 1)
            cover, share = float(a[t].mean()), float(t[a].mean())
            s = 0.5 * min(1.0, cover / 0.5) + 0.5 * min(1.0, share / min(0.5, 8 * base))
        else:
            b = h.whole(w.b, P) >= EST
            near = _within(g, b, h.cell_km)
            close = float(near[a].mean()) if b.any() else 0.0
            if w.want == "near":
                s = min(1.0, 2.5 * close)
                # (PW-699: as 'apart', a 'near' wish counts only where the two niches can reach each other)
                base = _niche_closeness(h, w, tags)
                if base < APART_CONTESTED:
                    out.append({**vars(w), "score": round(s, 3), "baseline": round(base, 3), "contested": False, "raw": round(s, 3),
                                "note": "niches rarely meet: not counted"})
                    continue
                out.append({**vars(w), "score": round(s, 3), "baseline": round(base, 3), "contested": True, "raw": round(s, 3)})
                continue
            else:
                # apart: against what the niches alone would give (the share of a's habitat within reach of b's
                # habitat, both before competition); a pair whose niches hardly meet has nothing to keep apart
                base = _niche_closeness(h, w, tags)
                if base < APART_CONTESTED:
                    out.append({**vars(w), "score": round(1.0 - close, 3), "baseline": round(base, 3), "contested": False, "raw": round(1.0 - close, 3),
                                "note": "niches rarely meet: not counted"})
                    continue
                s = float(np.clip(1.0 - close / base, 0.0, 1.0))
                out.append({**vars(w), "score": round(s, 3), "baseline": round(base, 3), "contested": True, "raw": round(1.0 - close, 3),
                            "closeness": round(close, 3)})
                continue
        out.append({**vars(w), "score": round(s, 3)})
    return out
