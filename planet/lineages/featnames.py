"""Feature names (PW-1656) and the map's labels (PW-1655): peaks, ranges, capes, bays, islands, lakes, seas and regions of a peoples
run, each named by the people who lived there first, kept or renamed as later peoples came, and the labels the viewer draws.

Read-out over a finished peoples run with languages (languages.json): `build(run_dir)` returns the features doc, `write(run_dir)`
saves it as features.json beside run.json (the language pass's own `planet languages`/`planet make` call it after languages.json;
`planet features <run>` adds it to an older run). `labels(run_dir, polities)` is what GET /api/maplabels answers: the features plus
the continents, the states and the towns, each with its English Common name and its local name.

Where the words come from: the languages already name every deme's main river and lake (names.demes[d].places, PW-972: kept as
heard by newcomers, P2) and every settlement (names.demes[d].settlements, renamed when its holders change); those are reused as
they are. The other features are coined here from the stored lexicons (languages.json lects: each lect's own word for MOUNTAIN,
HILL, ISLAND, HEAD/NOSE (a cape, by the lect's coast habit), MOUTH (a bay), SEA, LAKE, plus an adjective fitting the place: white
for ice, cold for the far north...), joined in the lect's adjective order, spelled in its book spelling (diacritics dropped), and
put into the English Common with planet/language/placenames.english (PW-1654), the same rendering the towns use.
This is a thin adapter outside planet/language (owned by another session): it calls only its public functions
(placenames.english, placenames.EN_ADJ, romanize.title_name, output.load) and reads the stored doc; it does not re-hear a substrate
name through the listener's ears (names._hear is private), so a kept name keeps its namer's spelling.

How long names last (the ticket's durability): each feature's land is walked through the language frames (20 kyr ago to now,
every 0.5 kyr). Its holder at a frame is the deme leading most of its cells (for a sea or a bay: the coast around it). The first
holder names it. A later holder of the same language family inherits the name (it evolves with the language: said now in the
holder's own words); a holder of another family keeps it as heard with the chance KEEP[kind], else renames it. Rivers keep theirs
longest (the languages' rule: always kept, P2), then lakes and seas, ranges, peaks, islands, capes and bays, then regions; towns
are renamed most (their holders rename them in the language pass). Every feature carries `named_by` (lect and people), `kyr`
(when its present name was given, kyr ago), `layer` ('own' / 'inherited' / 'substrate') and `names` (each name it has had).
"""
from __future__ import annotations

import json
import re
import unicodedata
import zlib
from pathlib import Path

import numpy as np

from .. import store as S
from ..grid import shared_grid

FORMAT = "procgen-features/1"
NONE = 65535
R_KM = 6371.0
KEEP = {"river": 1.0, "lake": 0.9, "sea": 0.85, "range": 0.8, "peak": 0.7, "island": 0.65, "cape": 0.55, "bay": 0.55,
        "region": 0.35}  # chance a holder of another language family keeps a feature's name (else renames it)
HEAD = {"peak": ("MOUNTAIN", "HILL", "STONE"), "range": ("MOUNTAIN", "HILL", "STONE"), "island": ("ISLAND", "LAND"),
        "cape": ("NOSE", "HEAD"), "bay": ("MOUTH", "SEA"), "sea": ("SEA", "WATER"), "lake": ("LAKE", "WATER"),
        "region": ("LAND",)}
MODS = {"peak": ("BIG", "HIGH", "BLACK", "RED", "OLD", "STONE"), "range": ("LONG", "BLACK", "RED", "BIG", "OLD", "HIGH"),
        "island": ("LONG", "GREEN", "BLACK", "RED", "SMALL", "OLD"), "cape": ("LONG", "BLACK", "RED", "WHITE", "STONE", "HIGH"),
        "bay": ("DEEP", "GREEN", "BLACK", "SALT", "SMALL", "LONG"), "sea": ("BLACK", "WHITE", "GREEN", "DEEP", "BIG", "SALT"),
        "lake": ("BLACK", "WHITE", "DEEP", "COLD", "GREEN", "LONG")}
RENAME_PER_KYR = {"river": 0.0, "lake": 0.004, "sea": 0.004, "range": 0.01, "peak": 0.025, "island": 0.03, "cape": 0.035, "bay": 0.035,
                  "region": 0.05}  # chance per kyr its own holders rename it anyway (a new hero's or a god's name, a new town on it)
CAPS = {"peak": 80, "range": 40, "island": 80, "cape": 50, "bay": 40, "sea": 18, "lake": 60, "region": 40, "river": 80}
PEAK_M, RANGE_M, RANGE_CELLS = 1500.0, 1400.0, 8
SPACING_KM = {"peak": 350.0, "cape": 500.0, "bay": 500.0}


# ------------------------------------------------------------------ small helpers
def _rng(seed, *key) -> np.random.Generator:
    return np.random.default_rng([int(seed) & 0xFFFFFFFF] + [zlib.crc32(str(k).encode()) for k in key])


def book(roman: str) -> str:
    """The book spelling of a stored word: diacritics and apostrophes dropped (names are spelled so in the languages' book form)."""
    s = unicodedata.normalize("NFD", roman or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.replace("'", "").replace("’", "").replace(" ", "")


_SYL = re.compile(r"[^aeiouy]*[aeiouy]+", re.I)


def clip(s: str, keep: int = 2) -> str:
    """At most `keep` syllables of a part of a name (the vowel groups, with what follows up to the next onset), so compounds stay
    short as the languages' own names do (names._clip clips at two)."""
    m = list(_SYL.finditer(s))
    if len(m) <= keep:
        return s
    end = m[keep - 1].end()
    rest = s[end:m[keep].start()] if keep < len(m) else ""
    return s[:end] + rest[:1]


def _km(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return R_KM * np.arccos(np.clip(a @ b, -1.0, 1.0))


def _spaced(cands: list[int], centers: np.ndarray, min_km: float, cap: int) -> list[int]:
    out: list[int] = []
    for c in cands:
        if all(_km(centers[o], centers[c]) >= min_km for o in out):
            out.append(c)
            if len(out) >= cap:
                break
    return out


def _middle(cells: np.ndarray, centers: np.ndarray) -> int:
    """The cell of a region nearest its mean direction (its label's place)."""
    m = centers[cells].mean(axis=0)
    m /= max(np.linalg.norm(m), 1e-12)
    return int(cells[int(np.argmax(centers[cells] @ m))])


# ------------------------------------------------------------------ the languages, as stored
class Tongues:
    """The stored lects of a languages.json, by deme: who said what when."""

    def __init__(self, lang: dict):
        self.lects = {l["id"]: l for l in lang.get("lects") or []}
        self.by_deme: dict[int, list[dict]] = {}
        for l in self.lects.values():
            if l.get("deme") is not None:
                self.by_deme.setdefault(int(l["deme"]), []).append(l)
        self.living = {d: next((l for l in ls if l.get("end") is None), None) for d, ls in self.by_deme.items()}
        self.by_family: dict[str, list[dict]] = {}
        for l in self.lects.values():
            if l.get("end") is None and l.get("lexicon"):
                self.by_family.setdefault(str(l.get("family_true")), []).append(l)
        self.habits = ((lang.get("names") or {}).get("habits") or {})

    def at(self, deme: int, kyr: float) -> dict | None:
        """The lect deme spoke `kyr` ago (its living lect when none was born by then)."""
        ls = self.by_deme.get(int(deme)) or []
        here = [l for l in ls if float(l.get("born_kyr") or 0) >= kyr - 1e-9 and (l.get("died_kyr") is None or float(l["died_kyr"]) < kyr)]
        if here:
            return min(here, key=lambda l: float(l["born_kyr"]))
        return self.living.get(int(deme)) or (ls[0] if ls else None)

    def family(self, l: dict | None) -> str | None:
        return None if l is None else str(l.get("family_true"))

    def wordy(self, l: dict, concepts) -> dict | None:
        """A lect that has a word for one of `concepts`: l itself, else the living lect of its deme, else a living sister in its family
        (a dead lect keeps only its core words)."""
        xs = (l, self.living.get(int(l["deme"])) if l.get("deme") is not None else None, *self.by_family.get(self.family(l), []))
        for c in concepts:  # (the first concept wins over the nearer lect: a sea is a 'sea' in a sister's words before 'water' in its own)
            for x in xs:
                if x and c in (x.get("lexicon") or {}):
                    return x
        return None


def _word(l: dict, c: str) -> dict | None:
    return (l.get("lexicon") or {}).get(c)


def coin(T: Tongues, l: dict, kind: str, mods: tuple, rng, key) -> dict | None:
    """A feature name in lect l's words: its head word for the kind (a cape takes the lect's coast habit, 'head' or 'nose'), an
    adjective drawn from `mods` (the first ones fit the place best), in the lect's adjective order; and the Common's English."""
    from ..language.placenames import EN_ADJ, english
    from ..language.romanize import title_name
    heads = HEAD[kind]
    if kind == "cape" and "head" in ((T.habits.get(l["id"]) or {}).get("coast") or ()):
        heads = ("HEAD", "NOSE")
    src = T.wordy(l, heads)
    if src is None:
        return None
    hc = next(c for c in heads if _word(src, c))
    head = _word(src, hc)
    ms = [c for c in mods if _word(src, c)]
    mc = None
    if ms and (kind != "lake" or rng.random() < 0.8):
        mc = ms[0] if rng.random() < 0.5 else ms[int(rng.integers(len(ms)))]
    parts = [(hc, head)] if mc is None else [(mc, _word(src, mc)), (hc, head)]
    if mc is not None and ((src.get("typology") or {}).get("adjective") == "NA"):
        parts = parts[::-1]
    roman = title_name("".join(clip(book(w["roman"])) for _c, w in parts).lower())
    full = title_name("".join(w["roman"] for _c, w in parts))
    gloss = "the " + " ".join(c.lower().split(" (")[0] for c in ([mc] if mc else []) + [hc])
    if kind == "range":
        en = f"The {EN_ADJ.get(mc, (mc or 'High').title())} Mountains"
        how = f"{(mc or 'high').lower()} + Mountains"
    elif kind == "sea" and hc == "SEA":
        en, how = english({"generic": "SEA", "spec": {"kind": "adj", "concept": mc} if mc else {}}, f"{kind}{key}")
        en = ("The " + en) if mc else "The Sea"
    else:
        en, how = english({"generic": hc, "spec": {"kind": "adj", "concept": mc} if mc else {}}, f"{kind}{key}")
    return {"local": roman, "local_full": full, "ipa": "".join(w["ipa"] for _c, w in parts), "gloss": gloss,
            "parts": [c for c, _w in parts], "english": en, "english_how": how, "lect_words": src["id"]}


# ------------------------------------------------------------------ the land
class Land:
    """The run's present land and sea, its leading demes over the language window, and the features found on it."""

    def __init__(self, run_dir: Path, lang: dict):
        self.dir = Path(run_dir)
        self.run = json.loads((self.dir / "run.json").read_text())
        self.meta = self.run["meta"]
        self.seed = int(self.meta.get("seed") or 0)
        self.g = shared_grid(int(self.meta.get("level", 7)))
        L = S.read_layers(self.dir, self.run["layers"], ["elevation", "ice", "demes"])
        ts = [round(-float(f["t"]), 3) for f in self.run["frames"]]
        self.now = len(ts) - 1
        from ..geo import is_land
        self.elev = np.asarray(L["elevation"][self.now], float)
        self.ice = np.asarray(L["ice"][self.now], float)
        self.land = np.asarray(is_land(self.elev, self.ice, self.g), bool)
        fk = [float(k) for k in (lang.get("frames_kyr") or [])] or [20.0 - 0.5 * i for i in range(41)]
        idx = {k: i for i, k in enumerate(ts)}
        self.frames = [(k, idx[round(k, 3)]) for k in fk if round(k, 3) in idx]
        self.demes = L["demes"]
        self.cell_km2 = 4 * np.pi * R_KM ** 2 / self.g.n
        oc, _n = self.g.components(~self.land)
        sizes = np.bincount(oc[oc >= 0])
        self.ocean = (oc == int(np.argmax(sizes))) if len(sizes) else np.zeros(self.g.n, bool)

    def holders(self, cells: np.ndarray) -> list[tuple[float, int | None]]:
        """(kyr ago, the deme leading most of these cells) at each language frame, oldest first."""
        out = []
        for k, rf in self.frames:
            v = np.asarray(self.demes[rf][cells]).astype(np.int64)
            v = v[v != NONE]
            out.append((k, int(np.bincount(v).argmax()) if len(v) else None))
        return out

    def ring(self, cells) -> np.ndarray:
        cells = np.atleast_1d(np.asarray(cells, np.int64))
        nb = np.concatenate([self.g.nbr_idx[self.g.nbr_off[c]:self.g.nbr_off[c + 1]] for c in cells]) if len(cells) else cells
        return np.unique(np.concatenate([cells, nb]))

    def ll(self, c: int) -> tuple[float, float]:
        return round(float(self.g.lat[c]), 2), round(float(self.g.lon[c]), 2)

    # -------------------------------------------------------------- finding the features
    def peaks(self) -> list[dict]:
        nbmax = self.g.nbr_max_in(self.elev, np.ones(self.g.n, bool))
        c = np.flatnonzero(self.land & (self.elev >= PEAK_M) & (self.elev > nbmax))
        c = c[np.argsort(-self.elev[c], kind="stable")].tolist()
        out = []
        for cell in _spaced(c, self.g.centers, SPACING_KM["peak"], CAPS["peak"]):
            m = ("WHITE", "COLD") if self.ice[cell] > 0 or self.elev[cell] > 4500 else MODS["peak"]
            out.append({"kind": "peak", "cell": cell, "size": float(self.elev[cell]), "elev_m": int(self.elev[cell]),
                        "catch": self.ring(cell), "mods": m + MODS["peak"] if m != MODS["peak"] else m,
                        "heads": ("MOUNTAIN",) if self.elev[cell] >= 2500 else ("HILL", "MOUNTAIN")})
        return out

    def ranges(self) -> list[dict]:
        lab, n = self.g.components(self.land & (self.elev >= RANGE_M))
        if not n:
            return []
        sz = np.bincount(lab[lab >= 0], minlength=n)
        out = []
        for r in np.argsort(-sz, kind="stable")[:CAPS["range"]]:
            if sz[r] < RANGE_CELLS:
                break
            cells = np.flatnonzero(lab == r)
            top = int(cells[np.argmax(self.elev[cells])])
            iced = (self.ice[cells] > 0).mean() > 0.3
            out.append({"kind": "range", "cell": _middle(cells, self.g.centers), "size": float(sz[r] * self.cell_km2), "cells": int(sz[r]),
                        "top_m": int(self.elev[top]), "catch": cells, "mods": (("WHITE",) if iced else ()) + MODS["range"]})
        return out

    def islands(self, continents: list[dict]) -> list[dict]:
        lab, n = self.g.components(self.land)
        sz = np.bincount(lab[lab >= 0], minlength=n)
        big = min([m["area_mkm2"] for m in continents] or [1e9]) * 1e6 * 0.6 / self.cell_km2
        order = [int(r) for r in np.argsort(-sz, kind="stable") if 2 <= sz[r] < big]
        out = []
        for r in order[:CAPS["island"]]:
            cells = np.flatnonzero(lab == r)
            c = _middle(cells, self.g.centers)
            lat = abs(float(self.g.lat[c]))
            m = (("WHITE", "COLD") if lat > 60 else ("COLD",) if lat > 50 else ("GREEN",) if lat < 25 else ()) + \
                (("BIG",) if sz[r] >= 40 else ("SMALL",) if sz[r] <= 4 else ()) + MODS["island"]
            out.append({"kind": "island", "cell": c, "size": float(sz[r] * self.cell_km2), "cells": int(sz[r]), "catch": cells, "mods": m})
        return out

    def coasts(self) -> tuple[list[dict], list[dict]]:
        oc = self.ocean.astype(float)
        sea2 = self.g.nbr_mean(self.g.nbr_mean(oc))
        lab, n = self.g.components(self.land)
        sz = np.bincount(lab[lab >= 0], minlength=n)
        coast = self.land & (self.g.nbr_max_in(oc, np.ones(self.g.n, bool)) > 0)
        capes = np.flatnonzero(coast & (sea2 >= 0.6) & (sz[np.maximum(lab, 0)] >= 30))
        capes = capes[np.argsort(-sea2[capes], kind="stable")].tolist()
        bays = np.flatnonzero(self.ocean & (sea2 <= 0.45) & (self.g.nbr_max_in(oc, np.ones(self.g.n, bool)) > 0))
        bays = bays[np.argsort(sea2[bays], kind="stable")].tolist()
        cs = [{"kind": "cape", "cell": c, "size": float(sea2[c]), "catch": self.ring(c), "mods": MODS["cape"]}
              for c in _spaced(capes, self.g.centers, SPACING_KM["cape"], CAPS["cape"])]
        bs = []
        for c in _spaced(bays, self.g.centers, SPACING_KM["bay"], CAPS["bay"]):
            catch = self.ring(c)
            bs.append({"kind": "bay", "cell": c, "size": float(1 - sea2[c]), "catch": catch[self.land[catch]], "mods": MODS["bay"]})
        return cs, bs

    def seas(self) -> list[dict]:
        cells = np.flatnonzero(self.ocean)
        if not len(cells):
            return []
        X = self.g.centers[cells]
        far = np.full(len(cells), -2.0)  # farthest-point seeds: the oceans' parts, spread evenly
        seeds = [int(np.argmax(np.abs(self.g.lat[cells]) < 1e9))]
        for _ in range(CAPS["sea"] - 1):
            far = np.maximum(far, X @ X[seeds[-1]])
            seeds.append(int(np.argmin(far)))
        own = np.argmax(X @ X[seeds].T, axis=1)
        e = self.g.edges
        out = []
        region = np.full(self.g.n, -1)
        region[cells] = own
        for k in range(len(seeds)):
            mine = cells[own == k]
            a, b = e[:, 0], e[:, 1]
            shore = np.unique(np.concatenate([b[(region[a] == k) & self.land[b]], a[(region[b] == k) & self.land[a]]]))
            c = _middle(mine, self.g.centers)
            lat = abs(float(self.g.lat[c]))
            m = (("WHITE", "COLD") if lat > 60 else ("GREEN",) if lat < 20 else ()) + MODS["sea"]
            out.append({"kind": "sea", "cell": c, "size": float(len(mine) * self.cell_km2), "cells": int(len(mine)),
                        "catch": shore, "mods": m, "coast_cells": int(len(shore))})
        return out


# ------------------------------------------------------------------ naming through time
def walk(land: Land, T: Tongues, f: dict, key) -> dict | None:
    """Name a feature through the language frames (see the module doc): its names, oldest first, and the one in use now."""
    kind = f["kind"]
    if not len(f["catch"]):
        return None
    hist = land.holders(f["catch"])
    names, cur_fam, sayer, k_prev = [], None, None, None
    for i, (k, d) in enumerate(hist):
        if d is None:
            continue
        l = T.at(d, k)
        if l is None:
            continue
        fam = T.family(l)
        if not names:
            names.append({"kyr": k, "deme": d, "lect": l["id"], "people": l.get("people"), "how": "named"})
        elif fam == cur_fam and _rng(land.seed, "drift", kind, key, i).random() < RENAME_PER_KYR[kind] * (k_prev - k):
            names.append({"kyr": k, "deme": d, "lect": l["id"], "people": l.get("people"), "how": "renamed by its own people"})
        elif fam != cur_fam:
            if _rng(land.seed, "keep", kind, key, i).random() < KEEP[kind]:
                names[-1].setdefault("kept_by", []).append([k, l.get("people")])
            else:
                names.append({"kyr": k, "deme": d, "lect": l["id"], "people": l.get("people"), "how": "renamed"})
        cur_fam, sayer = fam, (d, l)
        k_prev = k
    if not names or sayer is None:
        return None
    rng = _rng(land.seed, "coin", kind, key)
    out = []
    for n in names:
        namer = T.lects[n["lect"]]
        c = coin(T, namer, kind, f.get("mods") or MODS.get(kind, ()), rng, key) if kind != "peak" else \
            coin(T, namer, kind, f["mods"], rng, key) if "heads" not in f else _coin_peak(T, namer, f, rng, key)
        if c is None:
            continue
        if out and out[-1]["local"] == c["local"]:  # (a people renaming it as it was: no new name)
            continue
        out.append({**n, **c})
    if not out:
        return None
    last = out[-1]
    d_now, l_now = sayer
    living = T.living.get(d_now) or l_now
    if T.family(living) == T.family(T.lects[last["lect"]]):  # (inherited: said now in the holder's own words)
        c = (coin(T, living, kind, f.get("mods") or MODS.get(kind, ()), _rng(land.seed, "coin", kind, key), key) if "heads" not in f
             else _coin_peak(T, living, f, _rng(land.seed, "coin", kind, key), key))
        if c is not None and c["parts"] == last["parts"]:
            last = {**last, **c}
        layer = "own" if last["lect"] == living["id"] or T.lects[last["lect"]].get("deme") == living.get("deme") else "inherited"
    else:
        layer = "substrate"
    lat, lon = land.ll(f["cell"])
    rec = {"kind": kind, "id": f"{kind}:{key}", "lat": lat, "lon": lon, "size": round(float(f["size"]), 3),
           "english": last["english"], "english_how": last["english_how"], "local": last["local"], "local_full": last["local_full"],
           "ipa": last["ipa"], "gloss": last["gloss"], "said_by": living["id"], "said_by_people": living.get("people"),
           "named_by": last["lect"], "named_by_people": last.get("people"), "kyr": float(last["kyr"]), "layer": layer,
           "names": [[float(n["kyr"]), n["english"], n["local"], n["lect"], n.get("people"), n["how"]] for n in out]}
    for k in ("elev_m", "top_m", "cells"):
        if k in f:
            rec[k] = f[k]
    return rec


def _coin_peak(T, l, f, rng, key):
    save = HEAD["peak"]
    try:
        HEAD["peak"] = tuple(f["heads"]) + tuple(h for h in save if h not in f["heads"])
        return coin(T, l, "peak", f["mods"], rng, key)
    finally:
        HEAD["peak"] = save


def _lang_places(lang: dict) -> tuple[dict, dict]:
    """The languages' own names of rivers and lakes ({(kind, id): place record}, the first deme that names it) and each deme's
    places by kind."""
    water, by_deme = {}, {}
    for d, x in ((lang.get("names") or {}).get("demes") or {}).items():
        for p in x.get("places") or []:
            by_deme.setdefault(int(d), {}).setdefault(p["kind"], p)
            if p["kind"] in ("river", "lake") and p.get("id") is not None:
                water.setdefault((p["kind"], int(p["id"])), p)
    return water, by_deme


def build(run_dir, lang: dict | None = None) -> dict:
    """The features doc of a peoples run with languages (see the module doc)."""
    from ..language import output as LO
    run_dir = Path(run_dir)
    if lang is None:
        lang = LO.load(run_dir / "languages.json", sidecars=False)
    T = Tongues(lang)
    land = Land(run_dir, lang)
    pres = (land.meta.get("present") or {}).get("landmasses") or []
    conts = [m for m in pres if m.get("kind") == "continent"]
    feats: list[dict] = []
    found = {"peak": land.peaks(), "range": land.ranges(), "island": land.islands(conts), "sea": land.seas()}
    found["cape"], found["bay"] = land.coasts()
    for kind in ("sea", "range", "peak", "island", "cape", "bay"):
        for i, f in enumerate(found[kind]):
            r = walk(land, T, f, i)
            if r:
                feats.append(r)
    # the named islands of the history (present landmasses that are no continent) keep their names: the nearest island found
    lmn = (lang.get("names") or {}).get("landmasses") or {}
    isl = [x for x in feats if x["kind"] == "island"]
    for m in pres:
        if m.get("kind") == "continent" or not m.get("called") or not isl:
            continue
        u = _unit(m["lat"], m["lon"])
        best = min(isl, key=lambda x: -float(_unit(x["lat"], x["lon"]) @ u) + abs(np.log(max(x["size"], 1) / max(m["area_mkm2"] * 1e6, 1))))
        if float(_unit(best["lat"], best["lon"]) @ u) < np.cos(1500 / R_KM):
            continue
        ln = lmn.get(m["called"]) or {}
        tod = ln.get("today") or {}
        best.update({"english": m["called"], "english_how": "the history's name for it", "local": tod.get("roman") or ln.get("roman") or best["local"],
                     "gloss": ln.get("gloss") or best["gloss"], "named_by_people": ln.get("people") or best["named_by_people"],
                     "named_by": ln.get("named_by") or best["named_by"], "kyr": float(ln.get("kyr") or best["kyr"]), "layer": "substrate" if tod else best["layer"],
                     "history_name": True})
        best["names"] = [[best["kyr"], best["english"], best["local"], best["named_by"], best["named_by_people"], "named"]]
        isl.remove(best)
    # rivers and lakes: the languages' own names (kept longest: P2), placed where the landscape puts them
    water, by_deme = _lang_places(lang)
    ls = lang.get("landscape") or {}
    for kind, key in (("river", "rivers"), ("lake", "lakes")):
        items = sorted((ls.get(key) or {}).values(), key=lambda v: -(v.get("flow") or v.get("cells") or 0))
        n = 0
        for v in items:
            p = water.get((kind, int(v["id"])))
            if p is None or n >= CAPS[kind]:
                continue
            n += 1
            namer = T.lects.get(p.get("named_by")) or {}
            feats.append({"kind": kind, "id": f"{kind}:{v['id']}", "lat": v["lat"], "lon": v["lon"],
                          "size": float(v.get("flow") or v.get("cells") or 0), "cells": v.get("cells"),
                          "english": p.get("english"), "english_how": p.get("english_how"), "local": p.get("roman"),
                          "local_full": p.get("roman_full"), "ipa": p.get("ipa"), "gloss": p.get("gloss"), "said_by": p.get("lect"),
                          "said_by_people": (T.lects.get(p.get("lect")) or {}).get("people"), "named_by": p.get("named_by"),
                          "named_by_people": namer.get("people"), "kyr": float(p["kyr"]) if p.get("kyr") is not None else None,
                          "layer": "substrate" if p.get("substrate_of") else "own",
                          "names": [[p.get("kyr"), p.get("english"), p.get("roman"), p.get("named_by"), namer.get("people"), "named"]]})
    feats += _regions(land, T, lang, by_deme)
    _unique(feats)
    return {"format": FORMAT, "run": land.run.get("id"), "keep": KEEP, "features": feats, "ages": ages(feats, lang)}


def _unique(feats: list[dict]) -> None:
    """Coined English names told apart within a rough region (30 degrees of latitude by 40 of longitude; the seas over the whole
    world), the bigger feature keeping the plain name: placenames.unique_english (Great Whitefell, The Inner Green Sea). The
    languages' river and lake names are left as the languages give them."""
    from ..language.placenames import unique_english
    recs = sorted((f for f in feats if f["kind"] not in ("river", "lake")), key=lambda f: (f["kind"], -f["size"]))
    unique_english(recs, lambda f: f["kind"] if f["kind"] == "sea" else (f["kind"] if f["kind"] in ("range", "region") else "land",
                                                                       round(f["lat"] / 30), round(f["lon"] / 40)))
    for f in recs:
        if f["names"]:
            f["names"][-1][1] = f["english"]


def _unit(lat, lon) -> np.ndarray:
    la, lo = np.radians(float(lat)), np.radians(float(lon))
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def _regions(land: Land, T: Tongues, lang: dict, by_deme: dict) -> list[dict]:
    """The lands of the living cultures (their largest deme's 'land' name, names.demes[d].places), at the middle of their land now."""
    cp = land.dir / "cultures.json"
    if not cp.exists():
        return []
    C = json.loads(cp.read_text()).get("cultures") or []
    lead = np.asarray(land.demes[land.now]).astype(np.int64)
    cells_of: dict = {}
    for c, d in enumerate(lead.tolist()):
        if d != NONE:
            cells_of.setdefault(d, []).append(c)
    rows = []
    for cu in C:
        if cu.get("end") is not None:
            continue
        ds = [d for d in cu.get("demes") or [] if d in cells_of]
        if not ds:
            continue
        d = max(ds, key=lambda x: len(cells_of[x]))
        p = (by_deme.get(int(d)) or {}).get("land")
        if not p:
            continue
        cells = np.asarray([c for x in ds for c in cells_of[x]])
        rows.append((len(cells), cu, d, p, cells))
    rows.sort(key=lambda r: -r[0])
    out = []
    for n, cu, d, p, cells in rows[:CAPS["region"]]:
        c = _middle(cells, land.g.centers)
        lat, lon = land.ll(c)
        l = T.living.get(int(d)) or {}
        k = min(float(cu.get("born_kyr") or 20.0), 20.0)
        out.append({"kind": "region", "id": f"region:{cu['id']}", "lat": lat, "lon": lon, "size": float(n * land.cell_km2), "cells": n,
                    "english": p.get("english"), "english_how": p.get("english_how"), "local": p.get("roman"), "local_full": p.get("roman_full"),
                    "ipa": p.get("ipa"), "gloss": p.get("gloss"), "said_by": l.get("id"), "said_by_people": l.get("people"),
                    "named_by": p.get("named_by"), "named_by_people": l.get("people"), "kyr": k, "layer": "own",
                    "names": [[k, p.get("english"), p.get("roman"), p.get("named_by"), l.get("people"), "named"]]})
    return out


def ages(feats: list[dict], lang: dict | None = None) -> dict:
    """Median age (kyr since the present name was given) per kind; towns from the languages' settlement names (PW-1656's check:
    rivers > mountains > towns)."""
    by: dict = {}
    for f in feats:
        if f.get("kyr") is not None:
            by.setdefault(f["kind"], []).append(float(f["kyr"]))
    for x in (((lang or {}).get("names") or {}).get("demes") or {}).values():
        for s in x.get("settlements") or []:
            if s.get("kyr") is not None and s.get("tier") in ("town", "city"):
                by.setdefault("town", []).append(float(s["kyr"]))
    return {k: {"n": len(v), "median_kyr": round(float(np.median(v)), 2)} for k, v in sorted(by.items())}


def write(run_dir, lang: dict | None = None) -> dict:
    """Builds and saves features.json beside run.json; the doc's summary (counts and ages)."""
    doc = build(run_dir, lang)
    S.write_atomic(Path(run_dir) / "features.json", json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
    counts: dict = {}
    for f in doc["features"]:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    return {"counts": counts, "ages": doc["ages"]}


def lines_for_report(sm: dict) -> list[str]:
    c = ", ".join(f"{v} {k}s" for k, v in sm["counts"].items())
    a = "; ".join(f"{k} {v['median_kyr']:g} kyr" for k, v in sm["ages"].items())
    return [f"features (PW-1656): {c}", f"median age of the names now in use: {a}"]


# ------------------------------------------------------------------ the map's labels (PW-1655)
def labels(run_dir, polities: dict | None = None, lang: dict | None = None, feats: dict | None = None) -> dict:
    """What the viewer labels: {labels: [{kind, id, lat, lon, size, english, local, from_kyr?, to_kyr?, names?}, ...]}: the
    continents (the history's names and what the people there call them now), the seas and features (features.json, made here when
    the run has none), the states (their capital's name, PW-1436; with the span each name was in use) and the towns and cities
    (from founding to abandonment)."""
    from ..language import output as LO
    from . import nameslot as NS
    run_dir = Path(run_dir)
    if lang is None:
        lang = LO.load(run_dir / "languages.json", sidecars=False) if (run_dir / "languages.json").exists() else {}
    if feats is None:
        fp = run_dir / "features.json"
        feats = json.loads(fp.read_text()) if fp.exists() else (build(run_dir, lang) if lang else {"features": []})
    meta = json.loads((run_dir / "run.json").read_text())["meta"] if (run_dir / "run.json").exists() else {}
    out = []
    lmn = (lang.get("names") or {}).get("landmasses") or {}
    for m in (meta.get("present") or {}).get("landmasses") or []:
        if m.get("kind") != "continent" or not m.get("called"):
            continue
        ln = lmn.get(m["called"]) or {}
        out.append({"kind": "continent", "id": f"continent:{m['rank']}", "lat": m["lat"], "lon": m["lon"], "size": m["area_mkm2"] * 1e6,
                    "english": m["called"], "local": (ln.get("today") or {}).get("roman") or ln.get("roman") or m["called"],
                    "named_by_people": ln.get("people"), "kyr": ln.get("kyr")})
    for f in feats.get("features") or []:
        out.append({k: f.get(k) for k in ("kind", "id", "lat", "lon", "size", "english", "local", "gloss", "named_by", "named_by_people",
                                           "said_by_people", "kyr", "layer", "names")})
    pn, en = NS.place_names(lang), NS.place_english(lang)
    sp = run_dir / "settlements.json"
    if sp.exists():
        for s in json.loads(sp.read_text()).get("sites") or []:
            if s.get("tier_peak") not in ("town", "city") or s.get("kind") == "mine" or s["id"] not in pn:
                continue  # (a town the languages left unnamed keeps its gloss, 'the south-west of Trojanel': not written on the map)
            out.append({"kind": "city" if s["tier_peak"] == "city" else "town", "id": f"site:{s['id']}", "lat": s["lat"], "lon": s["lon"],
                        "size": float(s.get("peak_pop") or 0), "english": en.get(s["id"]) or s.get("place"), "local": pn.get(s["id"]) or s.get("place"),
                        "from_kyr": s.get("founded_kyr"), "to_kyr": s.get("abandoned_kyr")})
    for p in (polities or {}).get("polities") or []:
        cap = p.get("capital") or {}
        if cap.get("lat") is None or p.get("tier_peak") == "chiefdom":  # (the chiefdoms, thousands, stay unlabelled)
            continue
        if p.get("name_from") == "gloss" and p.get("kind") != "dragon":  # (a capital the languages left unnamed: 'West of Simath (gnomes) 424')
            continue
        site = cap.get("site")
        loc, eng = pn.get(int(site)) if site is not None else None, en.get(int(site)) if site is not None else None
        spans = [[float(a), re.sub(r" \d+$", "", n.replace(loc, eng, 1) if loc and eng else n), re.sub(r" \d+$", "", n)] for a, n in (p.get("names") or [[p.get("founded_kyr"), p.get("name")]])]
        out.append({"kind": "state", "id": f"state:{p['id']}", "lat": cap["lat"], "lon": cap["lon"], "size": float(p.get("peak_cells") or 0),
                    "english": spans[-1][1] if spans else p.get("name"), "local": p.get("name"), "names": spans, "tier": p.get("tier_peak"),
                    "from_kyr": p.get("founded_kyr"), "to_kyr": p.get("fell_kyr")})
    return {"run": meta.get("id") or run_dir.name, "labels": out}
