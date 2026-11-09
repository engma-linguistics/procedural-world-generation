"""Emergent cultures (PW-670, round 2): demes that adapted to new country, or lived apart long enough, become cultures of their own.

Output only, like demes.py and settlements.py: reads a finished peoples run (demes.json, layers/demes.bin, groups_best, the terrain
frames, meta.techtree) and writes `cultures.json` and `meta.cultures`. Nothing in the history is read back or changed.
Design and grounding: docs/review/emergent-cultures/design.md.

- A culture is a deme or a run of demes along the deme tree. A people's first demes form its founding culture. A deme split
  off by niche learning (`split_adapted`) is a new culture at once. A deme cut off by a gap, a crossing or distance is a new
  culture once it has lived apart `t_apart(era)`: T_APART_KYR by the people's era when it split (meta.techtree). Every other
  deme is its parent's culture. Who is apart is the demes' call: demes.py cuts each kind by its own reach (a walker's, a
  seafarer's, a flier's, a dragon's or giant's LINK_KM), so this module has no distance logic of its own.
- Inheritance: at its first frame a culture copies its parent culture's skills as they are then (a founding culture its
  people's spec). Its way of life, the shares of its people's groups on its cells (groups_best), is read at its first frame and now.
- Drift: sea craft and open-country lore move toward what its country rewards (the coast share of its cells / COAST_FULL;
  the steppe, desert and savanna share / OPEN_FULL), losing with TAU_LOSE_KYR and gaining with TAU_GAIN_KYR. A kind's cohesion
  (0..1, the tree's per-line `cohesion`, inherited; dragons strong, giants medium, peoples none) pulls the target that far toward
  its kind's mean: one tongue and shared mores across a kind.
- Demes overlap (lane 109): on a run with the presence table every people's demes are read (demes_all), so a culture's cells are
  all the cells its people lives in, over or beside other peoples; an older run gives the leading people's demes only (demes.bin).
- Merging (PW-676, no cap): a culture whose last deme fused into another culture's deme merged into it. Two touching sister
  cultures (one people, the same adaptation and main way of life) merge after MERGE_CONTACT_KYR x (1 - cohesion) side by side,
  or after MERGE_KYR once the people knows a unifying technology whose reach (REACH_MKM2) holds both.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import is_land
from ..grid import shared_grid

# judgement calls and their grounding: docs/review/emergent-cultures/design.md
T_APART_KYR = {"stone age": 0.6, "bronze age": 0.45, "classical": 0.3, "medieval": 0.2, "renaissance": 0.15, "industrial": 0.15}
# a deme apart this long, by its people's era when it split, is a culture of its own. Renaissance: settler colonies were told apart
# in ~120-175 yr (Cape Dutch a stable dialect by ~1775; "Americanism" coined 1781, 174 yr after Jamestown; Quebec cut off in 1760). Stone
# age: speech parts into separate tongues in ~0.5-0.7 kyr (lexicostatistics). Between: a judgement. Frames are 0.5 kyr apart near the
# present and 4 kyr in the glacial pass, so a split is seen at frame resolution: a deme counts once its life spans t_apart
ERA_SHARE = 0.25  # a people is in an era once it knows this share of the era's techs (meta.techtree; the stone age from the start)
MERGE_CONTACT_KYR = 1.0  # sister cultures touching this long merge (x (1 - cohesion)); longer than t_apart, so a brief meeting
# does not undo a split
COAST_FULL = 0.25  # coast share of a culture's cells at which sea craft is fully rewarded
OPEN_FULL = 0.5  # steppe, desert and savanna share at which open-country lore (herding, moving with the herds) is
TAU_LOSE_KYR = 1.0  # e-folding of a skill its country no longer rewards (Rivers 1912 via Henrich 2004: canoes lost on islands)
TAU_GAIN_KYR = 3.0  # ...and of one it newly rewards (the Banks Islanders' slow, crude re-learning; Tasmania never)
HELD, LOST = 0.5, 0.25  # a skill is held at HELD or more; lost if held at the founding and under LOST now (gained: the reverse)
MERGE_KYR = 1.0  # contact under one reach before two sister cultures merge
REACH_MKM2 = (("law", 5.0), ("cities", 1.0))  # a people's unifying technology -> the most land (both cultures) it can hold as one
OPEN_CLASSES = ("savanna", "desert", "steppe")
GAIN_NEEDS = {"sea": ("rafts", "canoes", "bark_canoes", "reed_boats", "skin_boats", "plank_boats"), "open": ("herding",)}  # (a skill is gained
# only once the people knows one of these, meta.techtree.known: no boats, no new sea craft; no herds, no herding lore)
BODY = {"flies", "swims", "mountain", "hardy", "subterranean", "denning", "sea_hunter"}  # (the kind's own: never drift)
SERIES_KEEP = 24
NONE = 65535


def culture_uid(people: str, how: str, born: float, founding_deme: dict) -> str:
    """A culture's stable uid (PW-1283) before de-duplication ('+' appended to a repeat, in culture order): its people, how and when it
    began and where its founding deme was. uids() rebuilds them for a cultures.json made before PW-1283."""
    return f"{people}:{how}:{born:.3f}:{founding_deme.get('lat') or 0:.1f}:{founding_deme.get('lon') or 0:.1f}"


def uids(doc: dict, demes_doc: dict) -> list[str]:
    """Each culture's uid in cultures.json order: its stored one, else built as derive() builds it (an older run's cultures.json)."""
    D, seen, out = demes_doc["demes"], set(), []
    for c in doc["cultures"]:
        u = c.get("uid")
        if not u:
            u = culture_uid(c["people"], c["how"], c["born_kyr"], D[c["demes"][0]])
            while u in seen:
                u += "+"
        seen.add(u)
        out.append(u)
    return out


class Culture:
    __slots__ = ("id", "people", "demes", "parent", "how", "born", "adapted", "ended", "end", "into", "sea0", "open0", "sea", "open",
                 "ways0", "ways", "started", "last_ago", "series", "peak", "cells_now", "country", "fit_sea", "fit_open", "merged_at")

    def __init__(self, id_, people, parent, how, born, adapted):
        self.id, self.people, self.parent, self.how, self.born, self.adapted = id_, people, parent, how, born, adapted
        self.demes: list[int] = []
        self.ended = self.end = self.into = self.merged_at = None
        self.sea0 = self.open0 = self.sea = self.open = None
        self.ways0 = self.ways = None
        self.started = False
        self.last_ago = None
        self.series: list = []
        self.peak = 0
        self.cells_now = 0
        self.country = None
        self.fit_sea = self.fit_open = None


def cohesion(tree: dict | None, tree_name: str | None = None) -> dict[str, float]:
    """id -> the kind's cohesion (0..1): the tree's per-line `cohesion`, inherited from the first parent where not given (spec's rule),
    0 where no line above gives it. A stored tree that gives none anywhere (a run made before the key existed) takes the values of the
    preset of the same name (samples/*.toml); the rest of its tree is as it was run."""
    rows = {r["id"]: r for r in (tree or {}).get("lineage", [])}
    given = {k: float(r["cohesion"]) for k, r in rows.items() if "cohesion" in r}
    if not given and tree_name:
        import tomllib
        for f in sorted((Path(__file__).parent / "samples").glob("*.toml")):
            t = tomllib.loads(f.read_text())
            if (t.get("meta") or {}).get("name") == tree_name:
                given = {r["id"]: float(r["cohesion"]) for r in t.get("lineage", []) if "cohesion" in r and r["id"] in rows}
                break
    out: dict[str, float] = {}

    def get(k, seen=()):
        if k not in out:
            par = (rows.get(k) or {}).get("parents") or []
            v = given[k] if k in given else get(par[0], seen + (k,)) if par and par[0] in rows and par[0] not in seen else 0.0
            out[k] = min(1.0, max(0.0, v))
        return out[k]

    for k in rows:
        get(k)
    return out


def eras(techtree: dict | None) -> dict[str, list]:
    """people -> [(kyr ago, era index)] of the eras it reached (ERA_SHARE of an era's techs known), oldest first; the stone age always."""
    from .techtree import ERAS
    tt = techtree or {}
    era = {t["id"]: t.get("era", "stone age") for t in tt.get("techs", [])}
    tot = {e: sum(1 for v in era.values() if v == e) for e in ERAS}
    out = {}
    for p, kn in (tt.get("known") or {}).items():
        r = [(float("inf"), 0)]
        for i, e in enumerate(ERAS[1:], 1):
            when = sorted((float(v[0]) for t, v in kn.items() if era.get(t) == e), reverse=True)
            need = int(np.ceil(ERA_SHARE * tot[e])) if tot[e] else 0
            if need and len(when) >= need:
                r.append((when[need - 1], i))
        out[p] = r
    return out


def t_apart(era_list: list | None, ago: float) -> float:
    """The time apart that makes a culture, for a people at that time (its era then; the stone age's without a techtree)."""
    from .techtree import ERAS
    i = max([e for when, e in era_list if when >= ago - 1e-9], default=0) if era_list else 0
    return T_APART_KYR[ERAS[i]]


def assign(demes: list[dict], era_of: dict | None = None) -> tuple[list[Culture], np.ndarray]:
    """The cultures of a deme tree (demes.json `demes`, in id order: a parent before its children) and each deme's culture. era_of:
    people -> eras() list (None: the stone age's time apart for all). (Round 2's rule that a cohesive kind's later first demes rejoin
    its first culture is gone, lane 109: it made up for dragons dropping out of frames that kept only each cell's two leading
    peoples; the demes now see every people wherever it lives, and a kind that really died out and came back is a new culture.)"""
    out: list[Culture] = []
    dc = np.full(len(demes), -1, np.int64)
    founding: dict = {}
    era_of = era_of or {}
    for d in demes:
        par = d["parent"]
        same = par is not None and demes[par]["people"] == d["people"]
        life = d["born_kyr"] - (d["ended_kyr"] if d["ended_kyr"] is not None else 0.0)
        if not same or d["how"] in ("first", "from_people"):
            key = (d["people"], round(d["born_kyr"], 3))
            if key not in founding:
                founding[key] = len(out)
                out.append(Culture(len(out), d["people"], None if par is None or dc[par] < 0 else int(dc[par]), "founding", d["born_kyr"], d.get("adapted")))
            c = founding[key]
        elif d["how"] == "split_adapted":
            c = len(out)
            out.append(Culture(c, d["people"], int(dc[par]), "adapted", d["born_kyr"], d.get("adapted")))
        elif life >= t_apart(era_of.get(d["people"]), d["born_kyr"]) - 1e-9:
            c = len(out)
            pa = out[int(dc[par])].adapted
            out.append(Culture(c, d["people"], int(dc[par]), "apart", d["born_kyr"], d.get("adapted") if d.get("adapted") != pa else pa))
        else:
            c = int(dc[par])
        dc[d["id"]] = c
        out[c].demes.append(d["id"])
    return out, dc


def _reach_dates(known: dict) -> dict:
    """people -> [(kyr ago known, reach Mkm2)] for its unifying technologies."""
    out = {}
    for p, k in (known or {}).items():
        r = [(float(k[t][0]), a) for t, a in REACH_MKM2 if t in k]
        if r:
            out[p] = r
    return out


def _reach(rd: list | None, ago: float) -> float:
    return max([a for when, a in rd if when >= ago - 1e-9], default=0.0) if rd else 0.0


def _step(v, fit, dt):
    tau = TAU_LOSE_KYR if fit < v else TAU_GAIN_KYR
    return fit + (v - fit) * float(np.exp(-dt / tau))


class Drift:
    """Follows the cultures through the frames, oldest first: inheritance at a culture's first frame, drift, contact merges."""

    def __init__(self, cultures: list[Culture], dc: np.ndarray, lines: list[dict], nbr_off, nbr_idx, cell_km2: float, known: dict | None = None,
                 biomes: tuple = (), coh: dict | None = None):
        self.C, self.dc, self.lines = cultures, dc, lines
        self.coh = coh or {}  # (people -> cohesion 0..1)
        self.ids = [l["id"] for l in lines]
        self.idx = {l["id"]: i for i, l in enumerate(lines)}
        self.cell_km2 = cell_km2
        self.rd = _reach_dates(known)
        self.gain_from = {k: {p: max([float(kn[t][0]) for t in ts if t in kn], default=None) for p, kn in (known or {}).items()}
                          for k, ts in GAIN_NEEDS.items()}  # (skill -> people -> kyr ago it could first gain it; None never)
        self.open_ids = np.array([i for i, b in enumerate(biomes) if b in OPEN_CLASSES], np.int64)
        self.biomes = biomes
        self.nbr_off, self.nbr_idx = np.asarray(nbr_off, np.int64), np.asarray(nbr_idx, np.int64)
        self.people_of = np.array([self.idx[u.people] for u in cultures] + [0], np.int64)  # (culture -> its people's line index)
        self.contact: dict[tuple, float] = {}
        self.merges: list[dict] = []
        self.prev = None
        self.group_of = np.full(len(lines) + 256, -1, np.int64)  # (line index -> the people index it is a group of)
        for i, l in enumerate(lines):
            if l.get("group_of") in self.idx:
                self.group_of[i] = self.idx[l["group_of"]]

    def resolve(self, c: int, ago: float) -> int:
        while self.C[c].merged_at is not None and self.C[c].merged_at >= ago - 1e-9:
            c = self.C[c].into
        return c

    def _can_gain(self, skill: str, people: str, ago: float) -> bool:
        w = self.gain_from[skill].get(people)
        return w is not None and w >= ago - 1e-9

    def _root(self, c: Culture):
        l = self.lines[self.idx[c.people]]
        dem = l.get("demography") or {}
        tr = l.get("traits") or []
        boats = l.get("realm", "land") == "land" and not ({"flies", "swims"} & set(tr))  # (a flier or a swimmer needs no boat: no sea craft)
        return (float(dem.get("sea_share") or 0.0) if boats else None), 1.0 if "nomadic" in tr else 0.0

    def frame(self, ago: float, cell: np.ndarray, deme: np.ndarray, groups: np.ndarray, coast: np.ndarray, biome: np.ndarray):
        """One frame: (cell, deme) pairs, every people's deme on each of its cells (the run's demes_all; on a run without it, the
        leading people's deme per cell), groups (groups_best per cell, 255 none), coast (land with a sea neighbour), biome (class
        index per cell, -1 sea)."""
        nC = len(self.C)
        dt = 0.0 if self.prev is None else max(self.prev - ago, 0.0)
        self.prev = ago
        lut = np.array([self.resolve(int(self.dc[d]), ago) if self.dc[d] >= 0 else -1 for d in range(len(self.dc))] + [-1], np.int64)
        dl = np.where(deme == NONE, len(self.dc), deme).astype(np.int64)
        ce = lut[np.minimum(dl, len(self.dc))]
        on = ce >= 0
        cc, at = ce[on], np.asarray(cell, np.int64)[on]
        cells = np.bincount(cc, minlength=nC)
        coastc = np.bincount(cc, weights=coast[at].astype(float), minlength=nC)
        openc = np.bincount(cc, weights=np.isin(biome[at], self.open_ids).astype(float), minlength=nC)
        nb = max(len(self.biomes), 1)
        bh = np.bincount(cc * nb + np.clip(biome[at], 0, nb - 1), minlength=nC * nb).reshape(nC, nb)
        gk = cc * 256 + groups[at].astype(np.int64)
        gu, gn = np.unique(gk, return_counts=True)
        ways: dict[int, dict] = {}
        for k, n in zip(gu.tolist(), gn.tolist()):
            c, gi = divmod(k, 256)
            p = self.idx[self.C[c].people]
            w = self.ids[gi] if gi < len(self.ids) and self.group_of[gi] == p else self.C[c].people  # (no group of its own: its people's old ways)
            ways.setdefault(c, {})
            ways[c][w] = ways[c].get(w, 0) + n
        live = np.flatnonzero(cells).tolist()
        mean: dict[str, list] = {}  # (people -> [cells, x open, cells with sea craft, x sea] over its cultures: the kind's mean)
        for c in live:
            u = self.C[c]
            if u.started and self.coh.get(u.people, 0.0) > 0:
                m = mean.setdefault(u.people, [0.0, 0.0, 0.0, 0.0])
                m[0] += cells[c]
                m[1] += cells[c] * u.open
                if u.sea is not None:
                    m[2] += cells[c]
                    m[3] += cells[c] * u.sea
        for c in live:
            u = self.C[c]
            n = int(cells[c])
            fs, fo = min(1.0, coastc[c] / n / COAST_FULL), min(1.0, openc[c] / n / OPEN_FULL)
            wsh = {k: round(v / n, 3) for k, v in sorted(ways.get(c, {}).items(), key=lambda x: -x[1])}
            if not u.started:
                u.started = True
                par = self.C[u.parent] if u.parent is not None else None
                if par is not None and par.started and par.people == u.people:
                    u.sea0, u.open0 = par.sea, par.open
                else:
                    u.sea0, u.open0 = self._root(u)
                u.sea, u.open, u.ways0 = u.sea0, u.open0, wsh
            else:
                gs, go = self._can_gain("sea", u.people, ago), self._can_gain("open", u.people, ago)
                k = self.coh.get(u.people, 0.0)
                m = mean.get(u.people)
                if u.sea is not None:
                    ts = fs if gs else min(fs, u.sea)
                    if m and m[2] > 0:
                        ts = (1 - k) * ts + k * m[3] / m[2]  # (cohesion: the kind's mean pulls the target that far)
                    u.sea = _step(u.sea, ts, dt)
                to = fo if go else min(fo, u.open)
                if m and m[0] > 0:
                    to = (1 - k) * to + k * m[1] / m[0]
                u.open = _step(u.open, to, dt)
            u.ways, u.fit_sea, u.fit_open = wsh, fs, fo
            u.country = self.biomes[int(bh[c].argmax())] if self.biomes else None
            u.last_ago = ago
            u.series.append((round(ago, 3), n, None if u.sea is None else round(u.sea, 3), round(u.open, 3)))
            if n > u.peak:
                u.peak = n
        for u in self.C:
            u.cells_now = int(cells[u.id]) if u.id < nC else 0
        self._contacts(ago, at, cc, cells, dt)

    def _touching(self, at: np.ndarray, cc: np.ndarray) -> set:
        """The pairs of cultures of one people on neighbouring cells (lo * nC + hi), from the (cell, culture) pairs: demes overlap,
        so a cell holds one culture per people living there."""
        nC, n = len(self.C), len(self.nbr_off) - 1
        if not len(cc):
            return set()
        pk = self.people_of[cc] * n + at
        o = np.argsort(pk, kind="stable")
        ks, kc = pk[o], cc[o]
        st = self.nbr_off[at]
        deg = self.nbr_off[at + 1] - st
        rep = np.repeat(np.arange(len(at)), deg)
        pos = np.arange(int(deg.sum())) - np.repeat(np.cumsum(deg) - deg, deg) + st[rep]
        q = self.people_of[cc[rep]] * n + self.nbr_idx[pos]
        w = np.minimum(np.searchsorted(ks, q), len(ks) - 1)
        hit = ks[w] == q
        a, b = cc[rep][hit], kc[w][hit]
        m = a < b
        return set(np.unique(a[m] * nC + b[m]).tolist())

    def _contacts(self, ago, at, cc, cells, dt):
        nC = len(self.C)
        pairs = self._touching(at, cc)
        now = {}
        gone = set()
        for k in sorted(pairs, key=lambda k: cells[k // nC] + cells[k % nC]):
            x, y = self.C[k // nC], self.C[k % nC]
            if x.people != y.people or x.adapted != y.adapted or not x.ways or not y.ways or next(iter(x.ways)) != next(iter(y.ways)):
                continue
            area = (cells[x.id] + cells[y.id]) * self.cell_km2 / 1e6
            key = (x.id, y.id)
            now[key] = self.contact[key] + dt if key in self.contact else 0.0  # (the time since the pair first touched as sisters)
            state = area <= _reach(self.rd.get(x.people), ago) and now[key] >= MERGE_KYR - 1e-9
            side = now[key] >= MERGE_CONTACT_KYR * (1.0 - self.coh.get(x.people, 0.0)) - 1e-9
            if (state or side) and x.id not in gone and y.id not in gone:
                keep, lose = (x, y) if x.born >= y.born else (y, x)
                lose.merged_at, lose.into = round(ago, 3), keep.id
                lose.ended, lose.end = round(ago, 3), "merged"
                self.merges.append({"ago_kyr": round(ago, 3), "culture": lose.id, "into": keep.id, "why": "states" if state else "contact", "area_mkm2": round(float(area), 2),
                                    "contact_kyr": round(now[key], 3)})
                gone |= {x.id, y.id}
                del now[key]
        self.contact = now


def finish(cultures: list[Culture], dc: np.ndarray, demes: list[dict]):
    """Ends from the demes: a culture none of whose demes lives ends when its last one did; it merged into the culture its last deme
    fused into (else it died out). Contact merges already set theirs."""
    for u in cultures:
        if u.end is not None:
            continue
        mem = [demes[d] for d in u.demes]
        if any(d["ended_kyr"] is None for d in mem):
            continue
        last = min(mem, key=lambda d: d["ended_kyr"])
        u.ended = last["ended_kyr"]
        tgt = int(dc[last["into"]]) if last.get("end") == "fused" and last.get("into") is not None else None
        if tgt is not None and tgt != u.id:
            while cultures[tgt].into is not None and cultures[tgt].merged_at is not None and cultures[tgt].merged_at >= u.ended:
                tgt = cultures[tgt].into
            u.end, u.into = "merged", tgt
        else:
            u.end = "died out"
    for u in cultures:  # (a culture is alive only if it holds cells now)
        if u.end is None and u.last_ago is not None and u.last_ago > 1e-9:
            u.ended, u.end = u.last_ago, "died out"


def _verdict(v0, v):
    if v0 is None or v is None:
        return None
    if v0 >= HELD and v < LOST:
        return "lost"
    if v0 < LOST and v >= HELD:
        return "gained"
    return "kept" if v >= HELD else "never had" if v0 < HELD and v < HELD else "fading"


def _short_people(l: dict) -> str:
    return (l.get("name") or l["id"]).split(" (")[0]


def document(cultures: list[Culture], dc: np.ndarray, doc: dict, lines: list[dict], merges: list[dict], cell_km2: float, secs: float = 0.0,
             coh: dict | None = None) -> dict:
    coh = coh or {}
    from .demes import _colors
    idx = {l["id"]: l for l in lines}
    D = doc["demes"]
    per: dict[str, int] = {}
    out = []
    held = np.zeros(len(cultures), np.int64)  # (cells its living demes hold now, as leading or second people: a culture that leads nowhere)
    for d in D:
        if d["ended_kyr"] is None and d["cells_now"] and dc[d["id"]] >= 0:
            c = int(dc[d["id"]])
            while cultures[c].end == "merged" and cultures[c].into is not None:
                c = cultures[c].into
            held[c] += d["cells_now"]
    uids: set[str] = set()
    for u in cultures:
        l = idx[u.people]
        f0 = D[u.demes[0]]  # (the founding deme: the earliest id, and a deme's id order is its birth order)
        uid = culture_uid(u.people, u.how, u.born, f0)
        while uid in uids:
            uid += "+"
        uids.add(uid)
        per[u.people] = per.get(u.people, 0) + 1
        alive = [D[d] for d in u.demes if D[d]["ended_kyr"] is None and D[d]["cells_now"]]
        big = max(alive or [D[d] for d in u.demes], key=lambda d: (d["cells_now"], d["peak_cells"]))
        place = big.get("place")
        pn = _short_people(l)
        nm = f"{u.adapted + ' ' if u.adapted else ''}{'first ' if u.how == 'founding' else ''}{pn}" + (f" of {place}" if place else "")
        trs = list(l.get("traits") or [])
        ways0, ways = u.ways0 or {}, u.ways or {}
        w0 = next(iter(ways0), None)
        w1 = next(iter(ways), None)
        par = cultures[u.parent] if u.parent is not None else None
        founded = w0 if w0 and w0 != u.people else None
        ch = []
        if u.adapted and (par is None or par.adapted != u.adapted):
            ch.append(f"took to {u.adapted} country")
        vs, vo = _verdict(u.sea0, u.sea), _verdict(u.open0, u.open)
        if vs in ("lost", "gained", "fading"):
            ch.append(f"{vs} the sea craft{' of its founders' if vs != 'gained' else ''} ({u.sea0:.2f} -> {u.sea:.2f})")
        if vo in ("lost", "gained", "fading"):
            ch.append(f"{vo} open-country herding lore ({u.open0:.2f} -> {u.open:.2f})")
        if w0 and w1 and w0 != w1:
            nmw = lambda w: idx[w]["name"] if w in idx and w != u.people else f"the old ways of the {pn}"  # noqa: E731
            ch.append(f"took up the ways of the {nmw(w1)}" if w0 == u.people else f"founded mostly by {nmw(w0)}, now mostly {nmw(w1)}")
        out.append({
            "id": u.id, "uid": uid, "people": u.people, "n": per[u.people], "name": nm, "how": u.how,
            "parent": u.parent, "parent_people": par.people if par else None,
            "born_kyr": round(u.born, 3), "cohesion": coh.get(u.people, 0.0),
            "ended_kyr": u.ended, "end": u.end, "into": u.into,
            "demes": u.demes, "adapted": u.adapted, "founded_by": founded, "place": place, "lat": big.get("lat"), "lon": big.get("lon"),
            "country_now": u.country, "cells_now": u.cells_now if u.end is None else 0, "cells_held_now": int(held[u.id]) if u.end is None else 0,
            "area_mkm2": round((max(u.cells_now, int(held[u.id])) if u.end is None else u.peak) * cell_km2 / 1e6, 3), "peak_cells": u.peak,
            "last_seen_kyr": u.last_ago,
            "traits": {"body": [t for t in trs if t in BODY], "cultural": [t for t in trs if t not in BODY],
                       "sea_craft": None if u.sea is None else {"start": round(u.sea0, 3), "now": round(u.sea, 3), "fit_now": round(u.fit_sea, 3), "verdict": vs},
                       "open_country": None if u.open is None else {"start": round(u.open0, 3), "now": round(u.open, 3), "fit_now": round(u.fit_open, 3), "verdict": vo},
                       "ways_start": ways0, "ways_now": ways},
            "changes": ch,
            "series": [list(x) for x in _thin(u.series, SERIES_KEEP)],
        })
    for x, c in zip(out, _colors(out, lines)):
        x["color"] = c
    from .nameslot import gloss_names, people_short
    for x, nm in zip(out, gloss_names(out, people_short(lines))):  # (PW-1249: distinct names, no "(7)"; the names slot's fallback)
        x["name"] = nm
    by = {}
    for x in out:
        b = by.setdefault(x["people"], {"cultures": 0, "alive": 0, "founding": 0, "adapted": 0, "apart": 0, "merged": 0, "died_out": 0})
        b["cultures"] += 1
        b["alive"] += x["end"] is None
        b[x["how"]] += 1
        b["merged"] += x["end"] == "merged"
        b["died_out"] += x["end"] == "died out"
    for m in merges:
        why = f"one state's reach, {m['area_mkm2']} Mkm2" if m["why"] == "states" else f"side by side {m['contact_kyr']:g} kyr"
        m["text"] = f"{out[m['culture']]['name']} merged into {out[m['into']]['name']} ({why})"
    cdoc = {"format": "procgen-cultures/1", "from_kyr": doc.get("from_kyr"), "frames": doc.get("frames"), "cultures": out,
            "merges": merges, "deme_culture": dc.tolist()}
    summary = {"file": "cultures.json", "count": len(out), "alive": sum(x["end"] is None for x in out), "merges": len(merges),
               "merges_by": {w: sum(m["why"] == w for m in merges) for w in ("contact", "states")}, "by_people": by,
               "generated_in_s": round(secs, 1),
               "constants": {"t_apart_kyr": T_APART_KYR, "coast_full": COAST_FULL, "open_full": OPEN_FULL, "tau_lose_kyr": TAU_LOSE_KYR,
                             "tau_gain_kyr": TAU_GAIN_KYR, "merge_kyr": MERGE_KYR, "merge_contact_kyr": MERGE_CONTACT_KYR,
                             "era_share": ERA_SHARE, "reach_mkm2": dict(REACH_MKM2), "cohesion": {k: v for k, v in coh.items() if v > 0}}}
    return {"doc": cdoc, "summary": summary}


def _thin(s: list, k: int) -> list:
    return s if len(s) <= k else [s[int(round(i))] for i in np.linspace(0, len(s) - 1, k)]


def derive(run_dir: Path, demes: dict | None = None) -> dict:
    """The cultures of a stored peoples run that has demes: {"doc": cultures.json, "summary": meta.cultures}. demes: a fresh
    demes.derive result ({"layer", "all", "doc"}) to use instead of the run's stored demes (a read-only look with today's demes).
    Every people's demes (demes_all, with the run's presence table) where the run has them, else the leading people's (demes.bin)."""
    from .output import read_presence
    from .history.habitat import BIOMES, biome_class
    t0 = time.time()
    run_dir = Path(run_dir)
    names = ("elevation", "ice", "climate", "groups_best") + (("demes",) if demes is None else ())
    run, arr = T.load_frames(run_dir, names)
    m = run["meta"]
    if demes is None:
        doc = json.loads((run_dir / m["demes"]["file"]).read_text())
        fa = (m["demes"].get("all") or {}).get("file")
        allv = np.fromfile(run_dir / fa, dtype="<u2") if fa and (run_dir / fa).exists() else None
    else:
        doc = demes["doc"]
        arr["demes"] = demes["layer"]
        allv = demes.get("all")
    pt = read_presence(run_dir, m) if allv is not None else None
    if pt is not None and len(pt["cells"]) != len(allv):
        pt = None
    lines = m["lineages"]
    g = shared_grid(m["level"])
    cell_km2 = 4 * np.pi * 6371.0 ** 2 / g.n
    coh = cohesion(m.get("tree"), m.get("tree_name"))
    cultures, dc = assign(doc["demes"], eras(m.get("techtree")))
    dr = Drift(cultures, dc, lines, g.nbr_off, g.nbr_idx, cell_km2, (m.get("techtree") or {}).get("known"), BIOMES, coh)
    agos = [max(0.0, -f["t"]) for f in run["frames"]]
    win = doc.get("from_kyr", 300.0)
    use = [j for j, a in enumerate(agos) if a <= win + 1e-9 and (j + 1 == len(agos) or agos[j + 1] < a)]  # (as demes.derive)
    no_sea = np.zeros(g.n, bool)
    for j in use:
        elev, ice = T.frame(run, arr, "elevation", j).astype(float), T.frame(run, arr, "ice", j).astype(float)
        land = is_land(elev, ice)
        sea_n = np.add.reduceat((~land)[g.nbr_idx].astype(np.int64), g.nbr_off[:-1]) > 0 if len(g.nbr_idx) else no_sea
        coast = land & sea_n
        env = {"climate": T.frame(run, arr, "climate", j)}
        biome = biome_class(env, {"land": land, "elev": elev})
        if pt is not None:  # (every people's demes, overlapping: lane 109)
            a, b = int(pt["offsets"][j, 0]), int(pt["offsets"][j, -1])
            cell, deme = pt["cells"][a:b].astype(np.int64), allv[a:b]
        else:
            lead = np.asarray(arr["demes"][j])
            cell = np.flatnonzero(lead != NONE)
            deme = lead[cell]
        dr.frame(agos[j], cell, deme, np.asarray(arr["groups_best"][j]), coast, biome)
    finish(cultures, dc, doc["demes"])
    return document(cultures, dc, doc, lines, dr.merges, cell_km2, time.time() - t0, coh)


def write(run_dir: Path, out_dir: Path | None = None, report: bool = True, redemes: bool = False) -> dict:
    """Adds cultures.json and meta.cultures to a peoples run (or, with out_dir, writes cultures.json there and leaves the run
    untouched: a read-only look at a protected run); returns meta.cultures. redemes (with out_dir only): cut the demes afresh in
    memory first (today's demes.py; never written) instead of reading the run's stored ones."""
    run_dir = Path(run_dir)
    if redemes and out_dir is None:
        raise ValueError("redemes needs out_dir: redo the run's demes with `planet demes` instead")
    dem = None
    if redemes:
        from . import demes as DM
        dem = DM.derive(run_dir)
    d = derive(run_dir, dem)
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        S.write_atomic(out_dir / "cultures.json", json.dumps(d["doc"], separators=(",", ":")))
        (out_dir / "summary.json").write_text(json.dumps(d["summary"], indent=1))
        if dem is not None:
            S.write_atomic(out_dir / "demes.json", json.dumps(dem["doc"], separators=(",", ":")))
            (out_dir / "demes_summary.json").write_text(json.dumps(dem["summary"], indent=1))
        return d["summary"]
    S.write_atomic(run_dir / "cultures.json", json.dumps(d["doc"], separators=(",", ":")))
    S.update_meta(run_dir, lambda run: run["meta"].__setitem__("cultures", d["summary"]))
    if report:
        with open(run_dir / "run.txt", "a") as f:
            f.write("\n".join(lines_for_report(d["summary"], d["doc"])) + "\n")
    return d["summary"]


def _kv(d: dict | None) -> str:
    return ", ".join(f"{v} {k}" for k, v in (d or {}).items())


def lines_for_report(sm: dict, doc: dict) -> list[str]:
    L = ["", f"## Cultures (PW-670): {sm['count']} in all, {sm['alive']} alive, {sm['merges']} merged ({_kv(sm.get('merges_by'))}; {sm['generated_in_s']} s)"]
    for p, b in sorted(sm["by_people"].items(), key=lambda x: -x[1]["alive"]):
        if b["alive"]:
            L.append(f"  {p:<18} {b['alive']:>3} alive of {b['cultures']:>3}: {b['adapted']} adapted, {b['apart']} apart; "
                     f"{b['merged']} merged, {b['died_out']} died out")
    alive = sorted((x for x in doc["cultures"] if x["end"] is None), key=lambda x: -x["cells_now"])
    L.append("  -- the largest now")
    L += [f"  {x['name']:<58} {x['cells_now']:>5} cells, since {x['born_kyr']:g} kyr ({x['how']}){'; ' + '; '.join(x['changes']) if x['changes'] else ''}"
          for x in alive[:16]]
    return L
