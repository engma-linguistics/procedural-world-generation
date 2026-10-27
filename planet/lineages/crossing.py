"""Sea crossings and contact corridors for the peoples' history.

Crossings, three ways (docs/proposals/lineages.md, "Sea crossings"):
- land bridges: nothing here. Every epoch's land is that epoch's own (the time zoom's
  surface above its sea level), so a strait that falls dry at a glacial low stand is walked
  over by the ordinary spread; the history only names it (an event) when a line first
  reaches a present-day landmass that way.
- short hops: the spread's per-trait sea factor (spec.TRAITS 'sea'; boats over straits late for a
  people with a sea share >= spec.SHORT_HOP_SHARE), a few cells.
- long crossings: a Poisson chance per step for each landmass a line doesn't hold yet,
  rate x dt x exp(-gap / L) summed over the line's ways of crossing (spec.HOPS: rafting on
  drift for anyone, rare; coastal canoes; swimming; flying; boats, late, by the people's sea share,
  spec.BOATS; every way but the raft x the people's exploration and will to leave home). The boats are the craft ladder
  (animal_defs.craft_ladder), the same as for the animals: canoes, planked boats, sailing ships, each with its date, reach and the sea
  share a people needs to man it (PW-720). The gap is
  the sea distance from the line's own coast (a sea-only BFS), so island chains are stepping
  stones. A landing needs habitat and room there.

Corridors: a 0..1 'contact' value per cell (open lowland, coasts, river valleys high; deep
forest, mountains, deserts away from rivers, islands, ice low). Competition is scaled by it:
in closed country the incumbent excludes newcomers (peoples stay distinct), in corridors it
relaxes, most of all during the late mixing.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from .. import names as NM
from . import animal_defs as AD
from . import spec as SP


@njit(cache=True)
def sea_gap(src, land, nbr_off, nbr_idx, maxd):
    """Sea cells crossed from the src cells (coastal land) to each land cell reached, through sea
    only (a land cell is a landing, not expanded). -1: not reached within maxd sea cells."""
    n = land.shape[0]
    d = np.full(n, -1, np.int64)
    q = np.empty(n, np.int64)
    h, t = 0, 0
    for i in range(n):
        if src[i]:
            d[i] = 0
            q[t] = i
            t += 1
    while h < t:
        i = q[h]
        h += 1
        if d[i] >= maxd:
            continue
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            if d[j] >= 0:
                continue
            if land[j]:
                if not land[i]:  # a landing (from the sea)
                    d[j] = d[i]
            else:
                d[j] = d[i] + 1
                q[t] = j
                t += 1
    return d


def hop_mult(line: SP.Lineage) -> float:
    """How readily a people's frontier sets out over the sea at all: x 2 explore x (1.25 - 0.5 insularity)
    (1 at the defaults, 0.5 and 0.5; spec.DEMOGRAPHY)."""
    return 2.0 * line.demo("explore") * (1.25 - 0.5 * line.demo("insularity"))


def modes(line: SP.Lineage, ago_kyr: float) -> list[tuple[str, float, float]]:
    """(way, rate per kyr, length scale km) of the line's ways of crossing open sea at that time: the raft for
    anyone; its traits' ways (spec.HOPS) and boats by its sea share (spec.BOATS, way 'seafaring'), x hop_mult."""
    out = []
    m = hop_mult(line)
    for way in ("raft", *line.traits):
        h = SP.HOPS.get(way)
        if h and (h[2] is None or ago_kyr <= h[2] + 1e-9):
            out.append((way, h[0] * (1.0 if way == "raft" else m), h[1]))
    share = line.demo("sea_share")
    craft = AD.craft_for_people(share, ago_kyr)  # (PW-720: canoes, planked boats and sailing ships, as for the animals: their dates, reaches and crews)
    if craft is not None:
        out.append(("seafaring", SP.BOATS[0] * share / SP.BOATS_FULL * m, craft[1]))
    return out


def short_hop(line: SP.Lineage) -> float:
    """The spread's sea factor for boats over straits (from spec.LATE_SEA_KYR ago): 0.75 at a sea share of
    BOATS_FULL (a few cells), less below, none under SHORT_HOP_SHARE."""
    share = line.demo("sea_share")
    return 0.0 if share < SP.SHORT_HOP_SHARE else 0.75 * min(1.0, share / SP.BOATS_FULL) ** 0.5


SHELF_CONTACT = 0.7  # exposed continental shelf at a low stand: flat coastal plain crossed by the rivers' lower courses


def corridor(tags: dict, env: dict, flow: np.ndarray | None, shelf: np.ndarray | None = None) -> np.ndarray:
    """Contact value 0..1 per land cell: how easily peoples meet and live side by side there.
    shelf: land of this epoch that is sea at the present (the world's river field, the present's,
    has no rivers there; the exposed shelves were low plains crossed by them: Doggerland, Beringia, Sunda)."""
    land = tags["land"]
    rain = env["precipitation"]
    trees = env.get("tree_cover", np.zeros(len(rain)))
    elev = tags["elev"]
    c = np.full(len(rain), 0.3)
    c = np.where(tags["open"], np.where(elev < 800, 0.5, 0.4), c)  # plains, steppe, savanna: open, not roads
    c = np.where(tags["coast"], np.maximum(c, 0.8), c)
    river = np.zeros(len(rain), bool)
    if flow is not None and land.any():
        f = np.where(land, flow, 0)
        thr = np.quantile(f[land], 0.92)
        river = land & (f >= max(thr, 1e-9))
        c = np.where(river, np.maximum(c, 0.9), c)
    if shelf is not None:
        c = np.where(shelf & land, np.maximum(c, SHELF_CONTACT), c)
    c = np.where(trees >= 60, np.minimum(c, np.where(river | tags["coast"], 0.6, 0.25)), c)  # deep forest
    c = np.where((rain < 200) & ~river, np.minimum(c, 0.2), c)  # desert away from water
    c = np.where(tags["mountain"], np.minimum(c, np.where(river, 0.4, 0.15)), c)  # basins behind ranges
    c = np.where(tags["island"], np.minimum(c, 0.3), c)
    c = np.where(env["ice"] > 0.5, 0.1, c)
    return np.where(land, c, 0.0)


class Crossings:
    """Per history: the present-day landmasses (to name where a line got to) and the arrivals."""

    def __init__(self, grid, present_env: dict, cell_km: float, cell_mkm2: float, seed=None, overrides: dict | None = None):
        self.g, self.cell_km = grid, cell_km
        land = present_env["land"]
        lab, k = grid.components(land)
        sizes = np.bincount(lab[lab >= 0], minlength=k)
        order = np.argsort(-sizes)
        rank = np.empty(k, np.int64)
        rank[order] = np.arange(k)
        self.label = np.where(lab >= 0, rank[np.maximum(lab, 0)], -1)  # 0 = the largest
        self.names = []
        given = NM.landmass_names(seed, len(order), overrides) if seed is not None else None  # (the world's own names, PW-853; the owner's, PW-867)
        for r, i in enumerate(order):
            sel = lab == i
            a = sizes[i] * cell_mkm2
            c = grid.centers[sel].mean(0)
            c /= np.linalg.norm(c) or 1
            la, lo = np.degrees(np.arcsin(c[2])), np.degrees(np.arctan2(c[1], c[0]))
            kind = "continent" if a >= 5 else "large island" if a >= 0.3 else "island"
            ns = "N" if la >= 0 else "S"
            ew = "E" if lo >= 0 else "W"
            self.names.append({"rank": r, "kind": kind, "area_mkm2": round(float(a), 2),
                               "lat": round(float(la), 1), "lon": round(float(lo), 1),
                               "name": f"the {kind} of {given[r]} ({a:.2g} Mkm²)" if given else
                               f"the {kind} at {abs(la):.0f}°{ns} {abs(lo):.0f}°{ew} ({a:.2g} Mkm²)",
                               "called": given[r] if given else None})
        self.reached: dict[str, dict[int, dict]] = {}  # line -> landmass -> first arrival

    def note(self, line_id: str, held: np.ndarray, ago: float, how: str, events: list, label: str,
             gap_km: float | None = None):
        """Record the present-day landmasses the line holds now and didn't before."""
        got = self.reached.setdefault(line_id, {})
        lm = np.unique(self.label[held & (self.label >= 0)])
        first = not got
        for m in lm:
            m = int(m)
            if m in got:
                continue
            got[m] = {"ago_kyr": round(ago, 3), "how": "origin" if first else how,
                      **({"gap_km": round(gap_km)} if gap_km is not None and not first else {})}
            if not first and self.names[m]["area_mkm2"] >= 0.05:
                verb = {"overland": "spreads overland (the land was joined then) to", "land bridge": "walks over a land bridge to", "strait": "crosses a strait to",
                        "raft": "is carried on drift across the sea to", "coastal": "paddles along the coast to",
                        "swims": "swims across the sea to", "flies": "flies across the sea to",
                        "seafaring": "sails across the sea to", "jump": "moves far off (crowded at home) to"}.get(how, f"reaches ({how})")
                gap = f" ({gap_km:.0f} km of open sea)" if gap_km else ""
                events.append({"ago_kyr": round(ago, 3), "kind": "crossing", "line": line_id,
                               "text": f"{label} {verb} {self.names[m]['name']}{gap}",
                               "lat": self.names[m]["lat"], "lon": self.names[m]["lon"]})

    def hop(self, line: SP.Lineage, p: np.ndarray, K: np.ndarray, room: np.ndarray, env: dict, tags: dict,
            ago: float, dt: float, rng, est: float, pull: np.ndarray | None = None):
        """Long sea crossings in this step: returns [(cell, way, gap_km)] of the landings made. `pull`: per-cell multiplier on the landing
        chance and place (history._partner_pull: a people whose contact hybrid is wanted lands by its partner, PW-861)."""
        ms = modes(line, ago)
        if not ms or dt <= 0:
            return []
        g = self.g
        held = p >= est
        src = held & tags["coast"]
        if not src.any():
            return []
        land = env["land"]
        Lmax = max(m[2] for m in ms)
        maxd = int(min(6 * Lmax / self.cell_km, 200))
        d = sea_gap(src, land, g.nbr_off, g.nbr_idx, maxd)
        lab = tags["label"]  # (this epoch's land components, history._tags)
        heldc = np.unique(lab[held & (lab >= 0)])
        cand = land & (d > 0) & (K > est) & (room > est) & (lab >= 0) & ~np.isin(lab, heldc)
        if not cand.any():
            return []
        km = d * self.cell_km
        rates = np.zeros(g.n)
        best_way = np.zeros(g.n, np.int64)
        best_r = np.zeros(g.n)
        for wi, (_, rate, L) in enumerate(ms):
            r = rate * np.exp(-km / L)
            rates += r
            better = r > best_r
            best_way[better] = wi
            best_r[better] = r[better]
        w = np.where(cand, rates * np.minimum(K, room), 0.0)
        if pull is not None:
            w = w * pull
        out = []
        for c in np.unique(lab[cand]):
            sel = cand & (lab == c)
            cell = int(np.flatnonzero(sel)[np.argmax(w[sel])])
            lam = w[cell] * dt
            if lam > 0 and rng.random() < 1 - np.exp(-lam):
                out.append((cell, ms[int(best_way[cell])][0], float(km[cell])))
        return out
