"""Emergent cultures, first cut (PW-670): demes that adapted to new country, or lived apart long enough, become cultures of their own.

Output only, like demes.py and settlements.py: reads a finished peoples run (demes.json, layers/demes.bin, groups_best, the terrain
frames, meta.techtree) and writes `cultures.json` and `meta.cultures`. Nothing in the history is read back or changed.
Design and grounding: docs/review/emergent-cultures/design.md.

- A culture is a deme or a run of demes along the deme tree. A people's first demes form its founding culture. A deme split
  off by niche learning (`split_adapted`) is a new culture at once. A deme cut off by a gap, a crossing or distance is a new
  culture once it has lived apart T_APART_KYR. Every other deme is its parent's culture.
- Inheritance: at its first frame a culture copies its parent culture's skills as they are then (a founding culture its
  people's spec). Its way of life, the shares of its people's groups on its cells (groups_best), is read at its first frame and now.
- Drift: sea craft and open-country lore move toward what its country rewards (the coast share of its cells / COAST_FULL;
  the steppe, desert and savanna share / OPEN_FULL), losing with TAU_LOSE_KYR and gaining with TAU_GAIN_KYR.
- Merging (PW-676, no cap): a culture whose last deme fused into another culture's deme merged into it. Two touching cultures
  of one people, with the same adaptation and main way of life, merge after MERGE_KYR of contact once the people knows a
  unifying technology whose reach (REACH_MKM2) holds both.
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
T_APART_KYR = 1.0  # a deme apart this long is a culture of its own (lexicostatistics: speech parts in ~0.5-0.7 kyr; margin)
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


def one_culture(tree: dict | None, lines: list[dict]) -> set[str]:
    """The kinds that keep one culture each, never fragmenting: the dragons (megafauna that fly, as history.megafauna.eco_mass tells
    them apart). They are sapient, but for now each kind is simply its own culture, along colour lines (owner 2026-10-31); their
    populations come and go too fast to read as cultures. The giants fragment like peoples (sapient in D&D; an owner question)."""
    mega = {r["id"] for r in (tree or {}).get("lineage", []) if r.get("megafauna")}
    return {l["id"] for l in lines if l["id"] in mega and "flies" in (l.get("traits") or [])}


def assign(demes: list[dict], whole: set | frozenset = frozenset()) -> tuple[list[Culture], np.ndarray]:
    """The cultures of a deme tree (demes.json `demes`, in id order: a parent before its children) and each deme's culture. A people
    in `whole` (one_culture) is one culture: all its demes share it."""
    out: list[Culture] = []
    dc = np.full(len(demes), -1, np.int64)
    founding: dict = {}
    kind: dict = {}
    for d in demes:
        par = d["parent"]
        if d["people"] in whole:
            if d["people"] not in kind:
                kind[d["people"]] = len(out)
                out.append(Culture(len(out), d["people"], None if par is None or dc[par] < 0 else int(dc[par]), "founding", d["born_kyr"], None))
            c = kind[d["people"]]
            dc[d["id"]] = c
            out[c].demes.append(d["id"])
            continue
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
        elif life >= T_APART_KYR - 1e-9:
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
                 biomes: tuple = ()):
        self.C, self.dc, self.lines = cultures, dc, lines
        self.ids = [l["id"] for l in lines]
        self.idx = {l["id"]: i for i, l in enumerate(lines)}
        self.cell_km2 = cell_km2
        self.rd = _reach_dates(known)
        self.gain_from = {k: {p: max([float(kn[t][0]) for t in ts if t in kn], default=None) for p, kn in (known or {}).items()}
                          for k, ts in GAIN_NEEDS.items()}  # (skill -> people -> kyr ago it could first gain it; None never)
        self.open_ids = np.array([i for i, b in enumerate(biomes) if b in OPEN_CLASSES], np.int64)
        self.biomes = biomes
        cnt = np.diff(nbr_off)
        a = np.repeat(np.arange(len(cnt)), cnt)
        b = np.asarray(nbr_idx)
        keep = a < b
        self.ea, self.eb = a[keep], b[keep]  # (each neighbour pair once)
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

    def frame(self, ago: float, deme: np.ndarray, groups: np.ndarray, coast: np.ndarray, biome: np.ndarray):
        """One frame: deme (the leading people's deme per cell, NONE none), groups (groups_best, 255 none), coast (land with a sea
        neighbour), biome (class index per cell, -1 sea)."""
        nC = len(self.C)
        dt = 0.0 if self.prev is None else max(self.prev - ago, 0.0)
        self.prev = ago
        lut = np.array([self.resolve(int(self.dc[d]), ago) if self.dc[d] >= 0 else -1 for d in range(len(self.dc))] + [-1], np.int64)
        dl = np.where(deme == NONE, len(self.dc), deme).astype(np.int64)
        cmap = lut[np.minimum(dl, len(self.dc))]
        on = cmap >= 0
        cc = cmap[on]
        cells = np.bincount(cc, minlength=nC)
        coastc = np.bincount(cc, weights=coast[on].astype(float), minlength=nC)
        openc = np.bincount(cc, weights=np.isin(biome[on], self.open_ids).astype(float), minlength=nC)
        nb = max(len(self.biomes), 1)
        bh = np.bincount(cc * nb + np.clip(biome[on], 0, nb - 1), minlength=nC * nb).reshape(nC, nb)
        gk = cc * 256 + groups[on].astype(np.int64)
        gu, gn = np.unique(gk, return_counts=True)
        ways: dict[int, dict] = {}
        for k, n in zip(gu.tolist(), gn.tolist()):
            c, gi = divmod(k, 256)
            p = self.idx[self.C[c].people]
            w = self.ids[gi] if gi < len(self.ids) and self.group_of[gi] == p else self.C[c].people  # (no group of its own: its people's old ways)
            ways.setdefault(c, {})
            ways[c][w] = ways[c].get(w, 0) + n
        for c in np.flatnonzero(cells).tolist():
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
                if u.sea is not None:
                    u.sea = _step(u.sea, fs if gs else min(fs, u.sea), dt)
                u.open = _step(u.open, fo if go else min(fo, u.open), dt)
            u.ways, u.fit_sea, u.fit_open = wsh, fs, fo
            u.country = self.biomes[int(bh[c].argmax())] if self.biomes else None
            u.last_ago = ago
            u.series.append((round(ago, 3), n, None if u.sea is None else round(u.sea, 3), round(u.open, 3)))
            if n > u.peak:
                u.peak = n
        for u in self.C:
            u.cells_now = int(cells[u.id]) if u.id < nC else 0
        self._contacts(ago, cmap, cells, dt)

    def _contacts(self, ago, cmap, cells, dt):
        a, b = cmap[self.ea], cmap[self.eb]
        m = (a >= 0) & (b >= 0) & (a != b)
        lo, hi = np.minimum(a[m], b[m]), np.maximum(a[m], b[m])
        nC = len(self.C)
        pairs = set(np.unique(lo * nC + hi).tolist())
        now = {}
        gone = set()
        for k in sorted(pairs, key=lambda k: cells[k // nC] + cells[k % nC]):
            x, y = self.C[k // nC], self.C[k % nC]
            if x.people != y.people or x.adapted != y.adapted or not x.ways or not y.ways or next(iter(x.ways)) != next(iter(y.ways)):
                continue
            area = (cells[x.id] + cells[y.id]) * self.cell_km2 / 1e6
            if area > _reach(self.rd.get(x.people), ago):
                continue
            key = (x.id, y.id)
            now[key] = self.contact[key] + dt if key in self.contact else 0.0  # (the time since the pair first qualified)
            if now[key] >= MERGE_KYR - 1e-9 and x.id not in gone and y.id not in gone:
                keep, lose = (x, y) if x.born >= y.born else (y, x)
                lose.merged_at, lose.into = round(ago, 3), keep.id
                lose.ended, lose.end = round(ago, 3), "merged"
                self.merges.append({"ago_kyr": round(ago, 3), "culture": lose.id, "into": keep.id, "why": "states", "area_mkm2": round(float(area), 2),
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


def document(cultures: list[Culture], dc: np.ndarray, doc: dict, lines: list[dict], merges: list[dict], cell_km2: float, secs: float = 0.0) -> dict:
    from .demes import _colors
    idx = {l["id"]: l for l in lines}
    D = doc["demes"]
    names: dict[str, int] = {}
    per: dict[str, int] = {}
    out = []
    held = np.zeros(len(cultures), np.int64)  # (cells its living demes hold now, as leading or second people: a culture that leads nowhere)
    for d in D:
        if d["ended_kyr"] is None and d["cells_now"] and dc[d["id"]] >= 0:
            c = int(dc[d["id"]])
            while cultures[c].end == "merged" and cultures[c].into is not None:
                c = cultures[c].into
            held[c] += d["cells_now"]
    for u in cultures:
        l = idx[u.people]
        per[u.people] = per.get(u.people, 0) + 1
        alive = [D[d] for d in u.demes if D[d]["ended_kyr"] is None and D[d]["cells_now"]]
        big = max(alive or [D[d] for d in u.demes], key=lambda d: (d["cells_now"], d["peak_cells"]))
        place = big.get("place")
        pn = _short_people(l)
        nm = f"{u.adapted + ' ' if u.adapted else ''}{'first ' if u.how == 'founding' else ''}{pn}" + (f" of {place}" if place else "")
        names[nm] = names.get(nm, 0) + 1
        if names[nm] > 1:
            nm += f" ({names[nm]})"
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
            "id": u.id, "people": u.people, "n": per[u.people], "name": nm, "how": u.how,
            "parent": u.parent, "parent_people": par.people if par else None,
            "born_kyr": round(u.born, 3), "own_from_kyr": round(u.born - T_APART_KYR, 3) if u.how == "apart" else round(u.born, 3),
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
    by = {}
    for x in out:
        b = by.setdefault(x["people"], {"cultures": 0, "alive": 0, "founding": 0, "adapted": 0, "apart": 0, "merged": 0, "died_out": 0})
        b["cultures"] += 1
        b["alive"] += x["end"] is None
        b[x["how"]] += 1
        b["merged"] += x["end"] == "merged"
        b["died_out"] += x["end"] == "died out"
    for m in merges:
        m["text"] = f"{out[m['culture']]['name']} merged into {out[m['into']]['name']} (one state's reach, {m['area_mkm2']} Mkm2)"
    cdoc = {"format": "procgen-cultures/1", "from_kyr": doc.get("from_kyr"), "frames": doc.get("frames"), "cultures": out,
            "merges": merges, "deme_culture": dc.tolist()}
    summary = {"file": "cultures.json", "count": len(out), "alive": sum(x["end"] is None for x in out), "merges": len(merges), "by_people": by,
               "generated_in_s": round(secs, 1),
               "constants": {"t_apart_kyr": T_APART_KYR, "coast_full": COAST_FULL, "open_full": OPEN_FULL, "tau_lose_kyr": TAU_LOSE_KYR,
                             "tau_gain_kyr": TAU_GAIN_KYR, "merge_kyr": MERGE_KYR, "reach_mkm2": dict(REACH_MKM2)}}
    return {"doc": cdoc, "summary": summary}


def _thin(s: list, k: int) -> list:
    return s if len(s) <= k else [s[int(round(i))] for i in np.linspace(0, len(s) - 1, k)]


def derive(run_dir: Path) -> dict:
    """The cultures of a stored peoples run that has demes: {"doc": cultures.json, "summary": meta.cultures}."""
    from .history.habitat import BIOMES, biome_class
    t0 = time.time()
    run_dir = Path(run_dir)
    names = ("elevation", "ice", "climate", "demes", "groups_best")
    run, arr = T.load_frames(run_dir, names)
    m = run["meta"]
    doc = json.loads((run_dir / m["demes"]["file"]).read_text())
    lines = m["lineages"]
    g = shared_grid(m["level"])
    cell_km2 = 4 * np.pi * 6371.0 ** 2 / g.n
    cultures, dc = assign(doc["demes"], one_culture(m.get("tree"), lines))
    dr = Drift(cultures, dc, lines, g.nbr_off, g.nbr_idx, cell_km2, (m.get("techtree") or {}).get("known"), BIOMES)
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
        dr.frame(agos[j], np.asarray(arr["demes"][j]), np.asarray(arr["groups_best"][j]), coast, biome)
    finish(cultures, dc, doc["demes"])
    return document(cultures, dc, doc, lines, dr.merges, cell_km2, time.time() - t0)


def write(run_dir: Path, out_dir: Path | None = None, report: bool = True) -> dict:
    """Adds cultures.json and meta.cultures to a peoples run (or, with out_dir, writes cultures.json there and leaves the run
    untouched: a read-only look at a protected run); returns meta.cultures."""
    run_dir = Path(run_dir)
    d = derive(run_dir)
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        S.write_atomic(out_dir / "cultures.json", json.dumps(d["doc"], separators=(",", ":")))
        (out_dir / "summary.json").write_text(json.dumps(d["summary"], indent=1))
        return d["summary"]
    S.write_atomic(run_dir / "cultures.json", json.dumps(d["doc"], separators=(",", ":")))
    S.update_meta(run_dir, lambda run: run["meta"].__setitem__("cultures", d["summary"]))
    if report:
        with open(run_dir / "run.txt", "a") as f:
            f.write("\n".join(lines_for_report(d["summary"], d["doc"])) + "\n")
    return d["summary"]


def lines_for_report(sm: dict, doc: dict) -> list[str]:
    L = ["", f"## Cultures (PW-670, first cut): {sm['count']} in all, {sm['alive']} alive, {sm['merges']} merged by states ({sm['generated_in_s']} s)"]
    for p, b in sorted(sm["by_people"].items(), key=lambda x: -x[1]["alive"]):
        if b["alive"]:
            L.append(f"  {p:<18} {b['alive']:>3} alive of {b['cultures']:>3}: {b['adapted']} adapted, {b['apart']} apart; "
                     f"{b['merged']} merged, {b['died_out']} died out")
    alive = sorted((x for x in doc["cultures"] if x["end"] is None), key=lambda x: -x["cells_now"])
    L.append("  -- the largest now")
    L += [f"  {x['name']:<58} {x['cells_now']:>5} cells, since {x['born_kyr']:g} kyr ({x['how']}){'; ' + '; '.join(x['changes']) if x['changes'] else ''}"
          for x in alive[:16]]
    return L
