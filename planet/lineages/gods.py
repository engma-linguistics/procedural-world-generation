"""Gods as a lect-like tree per culture (PW-1306, religion epic PW-1308; supersedes PW-907). Output only, like cultures.py.

Reads a finished peoples run (cultures.json, demes.json, layers/demes_all.bin or demes.bin, the terrain frames, meta.techtree) and writes
`gods.json`. Nothing in the history is read back or changed, and the history is identical in every gods mode: the mode changes only
the readout words and the spell flag (no miracle feedback in v2).

The model (the religion doc's round 1; every number marked JUDGEMENT is a first guess, not a source):
- A being has a weight vector over DOMAINS (20 of them, in five groups: water, sky, land, life, human), a devotion (how well it still
  fits its people's life: 0..1) and an individuation (0 = a spirit bound to one feature of the land, 1 = a named person-god).
- A culture (cultures.py: a deme or a run of demes) has 3-15 beings once its people knows spirit_ritual (BEING_MIN..BEING_MAX; no
  ritual, no gods: faith-made, so no pre-sapient gods). Each frame the culture's land and way of life give a salience per domain
  (salience()); a being's weight moves toward the salient domains OF ITS OWN GROUP, with e-folding TAU_DRIFT (slower than the cultures'
  skills, ritual is conservative): an inland-sea god becomes a rain god, slowly, because "sea" and "rain" are both water.
- Born: a domain salient (>= BORN_SAL) for BORN_KYR with no being on it gets a new being.
- Split: a culture born of another copies the parent's beings (new ids, `parent` = the original): cousins that drift apart.
- Merge (syncretism): when two cultures merge (cultures.json merges), the lost culture's beings fuse with the most alike of the
  survivor's (cosine >= FUSE_COS; the weights are averaged by devotion) or are carried in as they are.
- Fade: a being whose devotion stays under FADE_DEV is dropped; all of a culture's beings fade when it dies out (in `absolute` mode
  they stay `dormant`: they exist unworshipped).
- Individuation rises with the people's faith techs (techtree: spirit_ritual, burial, temples, kingship, moralizing_high_god): the
  most devoted being goes furthest; only it takes the moralizing high god. A being above SPELL_IND grants spells (not in belief_only).
- Names wait for PW-986: a being is labelled by its domains and its rank ("the god of sea and storm").

Faiths (PW-1358): a faith is its own record, not a culture. JUDGEMENT throughout, readout only (the history is untouched):
- Founded: a culture that first gets beings by itself (spirit ritual, no parent with gods) founds a faith; its core is the culture's
  most salient domain then.
- Inherited: a culture born of another keeps its parent's faith; a merge leaves the survivor's faith (the lost culture leaves its own).
- Schism: a culture whose most devoted being has had another top domain than its faith's core for SCHISM_KYR breaks off as a new faith
  (parent = the old one); a faith's last culture does not break off, the faith's core just moves (a change, logged).
- Conversion: two cultures in contact (sharing or bordering cells in a frame) of different faiths; if the neighbour's leading being is at
  least CONVERT_MIN individuated (temples) and CONVERT_GAP above this culture's, it converts with probability 1 - exp(-dt/TAU_CONVERT):
  it takes the neighbour's faith and a copy of its leading being (how = "converted"), keeping its own old beings (syncretism). A converted
  culture does not break away by drift (its old gods leading again would otherwise undo every conversion within SCHISM_KYR); it can
  still convert again, and its daughter cultures can break away.
- A faith with no culture left ends: "no followers left" when its last culture converted or broke away, else "its cultures ended".
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

from .techtree import GODS_MODES  # noqa: E402
MODE_DEFAULT = "faith_made"
GROUPS = {
    "water": ("sea", "river", "rain", "flood"),
    "sky": ("sky", "sun", "storm"),
    "land": ("mountain", "fire", "forest", "desert"),
    "life": ("herd", "hunt", "harvest", "fertility"),
    "human": ("hearth", "smithing", "death", "war", "ancestors"),
}
DOMAINS = tuple(d for g in GROUPS.values() for d in g)
GROUP_OF = {d: g for g, ds in GROUPS.items() for d in ds}
GROUP_IDX = {g: [DOMAINS.index(d) for d in ds] for g, ds in GROUPS.items()}
FEATURE = {"sea": "the sea", "river": "the great river", "rain": "the rains", "flood": "the flood plain", "sky": "the open sky",
           "sun": "the sun", "storm": "the storm", "mountain": "the mountains", "fire": "the fire mountain", "forest": "the forest",
           "desert": "the desert", "herd": "the herds", "hunt": "the hunt", "harvest": "the fields", "fertility": "the springs of life",
           "hearth": "the hearth", "smithing": "the forge", "death": "the dead lands", "war": "the war-road", "ancestors": "the graves"}
TAU_DRIFT = 6.0  # kyr, JUDGEMENT: weights move toward the land's salience this slowly (cultures.TAU_GAIN_KYR is 3: ritual is conservative)
TAU_DEV = 10.0  # kyr, JUDGEMENT: a being's devotion follows its fit this slowly
TAU_IND = 3.0  # kyr, JUDGEMENT: individuation follows the faith techs
BEING_MIN, BEING_MAX = 3, 15  # the doc: 3-15 beings per deme
BORN_SAL, BORN_KYR = 0.45, 1.0  # JUDGEMENT: a domain this salient for this long with no being on it is born a being
FIT_FULL = 0.3  # a fit (sum of weight x salience) this high is full devotion
FADE_DEV = 0.05  # JUDGEMENT: devotion under this and the being is dropped
COVER_W = 0.15  # a domain a being already carries this much of is covered: no new being is born on it
SAME_COS = 0.97  # two beings of one culture this alike are one (they fuse)
FUSE_COS = 0.6  # JUDGEMENT: two beings at least this alike fuse when their cultures merge
SPELL_IND = 0.5  # JUDGEMENT: only beings this individuated grant spells (the doc: only above a threshold)
# individuation ceilings by faith tech, JUDGEMENT (the doc: it rises with the faith nodes the people holds)
TIERS = (("moralizing_high_god", 0.9), ("kingship", 0.6), ("temples", 0.45), ("burial", 0.2), ("spirit_ritual", 0.1))
COAST_FULL, RIVER_FULL, MOUNT_FULL, FOREST_FULL, OPEN_FULL, DESERT_FULL, WET_FULL, VOLC_FULL = 0.25, 0.15, 0.2, 0.5, 0.5, 0.3, 0.5, 0.05
RIVER_Q = 0.92  # the top 8 % of land by flow is a river (as crossing.corridor)
WAY_WORDS = (("farm", "harvest"), ("herd", "herd"), ("nomad", "herd"), ("seafar", "sea"), ("hunt", "hunt"), ("arctic", "hunt"))
NONE = 65535
SCHISM_KYR = 20.0  # JUDGEMENT: a culture's leading being this long off its faith's core and the culture breaks away
CONVERT_MIN, CONVERT_GAP = 0.45, 0.15  # JUDGEMENT: a faith spreads only from an organised one (temples) to a less individuated one
TAU_CONVERT = 30.0  # kyr, JUDGEMENT: per contact, the e-folding time of a conversion


def _c(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


def salience(f: dict, know: set, ways: dict | None = None, traits: tuple = ()) -> np.ndarray:
    """Per-domain salience 0..1 (DOMAINS order) of a culture's land and life. f: shares (0..1) of its cells that are coast, river,
    mountain, desert, forest, wet (jungle or wetland), open (steppe, savanna, plain), tundra, volcanic, island, lowland. know: the
    techs its people knows then. ways: way of life -> share. All the scales are JUDGEMENT; the point is the ordering and that
    each follows from the land (the doc: coast, rivers, mountains, deserts, the herds and fields) or the way of life."""
    g = lambda k: float(f.get(k, 0.0))  # noqa: E731
    way = {"harvest": 0.0, "herd": 0.0, "sea": 0.0, "hunt": 0.0}
    for w, sh in (ways or {}).items():
        for word, key in WAY_WORDS:
            if word in w:
                way[key] += sh
                break
    farm = _c(way["harvest"] + (0.3 if "cultivation" in know else 0.0))
    herd = _c(way["herd"] + (0.3 if "herding" in know else 0.0)) * _c(0.4 + g("open") / OPEN_FULL)
    sea = _c(g("coast") / COAST_FULL + 0.5 * g("island")) * (1.0 if "seafaring" in traits or "coastal" in traits or "swims" in traits else 0.7)
    river = _c(g("river") / RIVER_FULL)
    s = {
        "sea": _c(sea + 0.3 * way["sea"]),
        "river": river,
        "rain": _c(g("wet") / WET_FULL + 0.4 * farm),
        "flood": _c(river * (0.5 * g("lowland") + g("wet")) * 2.0),
        "sky": _c(g("open") / OPEN_FULL + 0.5 * g("tundra") / 0.3),
        "sun": _c(max(g("desert") / DESERT_FULL, 0.7 * g("tundra") / 0.3)),
        "storm": 0.6 * _c(max(g("coast") / COAST_FULL, g("open") / OPEN_FULL, g("mountain") / MOUNT_FULL)),
        "mountain": _c(g("mountain") / MOUNT_FULL),
        "fire": _c(g("volcanic") / VOLC_FULL + (0.15 if "fire_control" in know else 0.0)),
        "forest": _c(g("forest") / FOREST_FULL),
        "desert": _c(g("desert") / DESERT_FULL),
        "herd": herd,
        "hunt": _c(0.7 - 0.5 * farm + way["hunt"]),
        "harvest": farm,
        "fertility": _c(0.25 + 0.4 * max(farm, herd)),
        "hearth": _c(0.35 + 0.3 * g("tundra") / 0.3),
        "smithing": 0.8 if "iron" in know else 0.6 if ("bronze" in know or "copper" in know) else 0.0,
        "death": _c((0.3 if "burial" in know else 0.1) + (0.2 if "war_chariot" in know or "bronze" in know else 0.0)),
        "war": _c(0.15 + (0.45 if "aggressive" in traits else 0.0) + (0.3 if "kingship" in know else 0.0)),
        "ancestors": 0.35 if "burial" in know else 0.1,
    }
    return np.array([s[d] for d in DOMAINS], float)


def tier(know: set, high_god: bool = True) -> float:
    """The individuation ceiling of the faith techs a people holds; without the high god, none goes past kingship's."""
    return max([v for k, v in TIERS if k in know and (high_god or k != "moralizing_high_god")], default=0.0)


def _spread(d: int, sal: np.ndarray) -> np.ndarray:
    """Weights of a new being on domain d: 0.7 on it, 0.3 over its group by salience."""
    w = np.zeros(len(DOMAINS))
    idx = GROUP_IDX[GROUP_OF[DOMAINS[d]]]
    s = sal[idx] + 1e-3
    w[idx] = 0.3 * s / s.sum()
    w[d] += 0.7
    return w / w.sum()


def _drift(w: np.ndarray, sal: np.ndarray, dt: float) -> np.ndarray:
    """Each group's mass moves onto that group's salient domains."""
    k = 1.0 - math.exp(-dt / TAU_DRIFT)
    t = w.copy()
    for idx in GROUP_IDX.values():
        s = sal[idx]
        if s.sum() > 1e-6:
            t[idx] = w[idx].sum() * s / s.sum()
    w2 = w + (t - w) * k
    return w2 / w2.sum()


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def label(w: np.ndarray, ind: float) -> str:
    top = [DOMAINS[i] for i in np.argsort(-w)[:2] if w[i] > 0.15] or [DOMAINS[int(np.argmax(w))]]
    what = " and ".join(top)
    if ind < 0.3:
        return f"spirit of {FEATURE[top[0]]}"
    if ind < 0.5:
        return f"power of {what}"
    if ind < 0.7:
        return f"god of {what}"
    return f"person-god of {what}"


class Being:
    __slots__ = ("id", "w", "dev", "ind", "born", "culture", "how", "parent", "fused", "status", "ended", "end", "into", "hist", "top0", "high", "faith")

    def __init__(self, id_, w, born, culture, how, parent=None):
        self.id, self.w, self.born, self.culture, self.how, self.parent = id_, w, born, culture, how, parent
        self.dev, self.ind = 0.5, 0.05
        self.fused: list = []
        self.status, self.ended, self.end, self.into = "living", None, None, None
        self.hist: list = []
        self.top0 = DOMAINS[int(np.argmax(w))]
        self.high = False
        self.faith = None


class Faith:
    __slots__ = ("id", "origin", "founded", "parent", "how", "core", "ended", "end", "members", "track", "changes", "events")

    def __init__(self, id_, origin, founded, how, core, parent=None):
        self.id, self.origin, self.founded, self.how, self.core, self.parent = id_, origin, founded, how, core, parent
        self.ended, self.end = None, None
        self.members: set = set()
        self.track: list = []
        self.changes: list = []
        self.events: list = []


class Pantheons:
    """The beings of every culture, followed frame by frame, oldest first. No I/O: feed it frames."""

    def __init__(self, mode: str = MODE_DEFAULT, seed: int = 0):
        if mode not in GODS_MODES:
            raise ValueError(f"gods_mode must be one of {GODS_MODES}")
        self.mode = mode
        self.beings: list[Being] = []
        self.by: dict[int, list[Being]] = {}  # culture -> its living beings
        self.events: list[dict] = []
        self.unmet: dict[tuple, float] = {}
        self.prev: float | None = None
        self.faiths: list[Faith] = []
        self.faith_of: dict[int, int] = {}  # culture -> its faith now
        self.fhist: dict[int, list] = {}  # culture -> [[ago, faith or None], ...], oldest first
        self.off: dict[int, float] = {}  # culture -> kyr its leading being has been off its faith's core
        self.converted: set = set()  # cultures that took their faith by conversion (they do not break away by drift)
        self.rng = np.random.default_rng((int(seed), 1358))
        self.counts = {"founded": 0, "schisms": 0, "conversions": 0, "core_changes": 0}

    # ---- faiths (PW-1358)
    def _join(self, c: int, f: int | None, ago: float):
        old = self.faith_of.get(c)
        if old == f:
            return
        if old is not None:
            self.faiths[old].members.discard(c)
        if f is None:
            self.faith_of.pop(c, None)
        else:
            self.faith_of[c] = f
            self.faiths[f].members.add(c)
        self.fhist.setdefault(c, []).append([round(float(ago), 3), f])

    def _leave(self, c: int, ago: float, why: str):
        old = self.faith_of.get(c)
        self._join(c, None, ago)
        if old is not None:
            self._check_end(old, ago, why)

    def _check_end(self, f: int, ago: float, why: str):
        F = self.faiths[f]
        if not F.members and F.ended is None:
            F.ended, F.end = round(float(ago), 3), why
            self._ev(ago, "faith_end", f"faith {f} ended: {why}", faith=f)

    def _found_faith(self, c: int, ago: float, core: str, how: str = "founded", parent: int | None = None) -> int:
        F = Faith(len(self.faiths), c, round(float(ago), 3), how, core, parent)
        self.faiths.append(F)
        self.counts["founded" if how == "founded" else "schisms"] += 1
        self._ev(ago, "faith", f"faith {F.id} {how} in culture {c} ({core})", faith=F.id, culture=c, parent=parent)
        return F.id

    def lead(self, c: int) -> Being | None:
        bs = self.by.get(c) or []
        return min(bs, key=lambda b: (-b.dev, b.id)) if bs else None

    def _schisms(self, ago: float, dt: float):
        new: dict = {}
        for c in sorted(self.faith_of):
            f, L = self.faith_of[c], self.lead(c)
            if L is None or c in self.converted:
                continue
            dom = DOMAINS[int(np.argmax(L.w))]
            F = self.faiths[f]
            if dom == F.core:
                self.off.pop(c, None)
                continue
            self.off[c] = self.off.get(c, 0.0) + dt
            if self.off[c] < SCHISM_KYR:
                continue
            self.off.pop(c, None)
            if len(F.members) <= 1:  # (its only culture: the faith itself changes)
                F.changes.append([round(float(ago), 3), F.core, dom])
                F.core = dom
                self.counts["core_changes"] += 1
                continue
            key = (f, dom)
            if key not in new:
                new[key] = self._found_faith(c, ago, dom, "schism", f)
            self._join(c, new[key], ago)
            self._check_end(f, ago, "no followers left")

    def _conversions(self, ago: float, dt: float, contacts):
        if dt <= 0 or not contacts:
            return
        p = 1.0 - math.exp(-dt / TAU_CONVERT)
        done: set = set()
        for a, b in sorted(contacts):
            for x, y in ((a, b), (b, a)):
                if x in done or x not in self.faith_of or y not in self.faith_of or self.faith_of[x] == self.faith_of[y]:
                    continue
                lx, ly = self.lead(x), self.lead(y)
                if lx is None or ly is None or ly.ind < CONVERT_MIN or ly.ind - lx.ind < CONVERT_GAP:
                    continue
                if self.rng.random() >= p:
                    continue
                done.add(x)
                old, f = self.faith_of[x], self.faith_of[y]
                self._join(x, f, ago)
                self.converted.add(x)
                nb = self._new(ly.w.copy(), ago, x, "converted", ly.id)
                nb.dev = min(1.0, max(o.dev for o in self.by[x]) + 0.01)
                nb.ind = lx.ind
                self.off.pop(x, None)
                self.counts["conversions"] += 1
                self.faiths[f].events.append([round(float(ago), 3), "converted", x, old])
                self._ev(ago, "conversion", f"culture {x} took faith {f} from culture {y}", culture=x, faith=f, faith_was=old, by=y)
                self._check_end(old, ago, "no followers left")

    def faith_track(self, ago: float, where: dict | None = None):
        """One sample per living faith: [ago, cultures, cells, lat, lon, leading individuation, core]. where: culture -> (cells,
        sum of their unit vectors)."""
        for F in self.faiths:
            if F.ended is not None or not F.members:
                continue
            if F.track and abs(F.track[-1][0] - ago) < 0.5:
                continue
            n, v = 0, np.zeros(3)
            for c in F.members:
                if where and c in where:
                    n += where[c][0]
                    v = v + where[c][1]
            lat = lon = None
            if n and np.linalg.norm(v) > 0:
                u = v / np.linalg.norm(v)
                lat, lon = round(math.degrees(math.asin(max(-1.0, min(1.0, u[2])))), 2), round(math.degrees(math.atan2(u[1], u[0])), 2)
            ind = max((self.lead(c).ind for c in F.members if self.lead(c) is not None), default=0.0)
            F.track.append([round(float(ago), 3), len(F.members), int(n), lat, lon, round(float(ind), 3), F.core])

    def _new(self, w, ago, c, how, parent=None) -> Being:
        b = Being(len(self.beings), w, ago, c, how, parent)
        b.faith = self.faith_of.get(c)
        self.beings.append(b)
        self.by.setdefault(c, []).append(b)
        return b

    def _ev(self, ago, kind, text, **kw):
        self.events.append({"ago_kyr": round(float(ago), 3), "kind": kind, "text": text, **kw})

    def _end(self, b: Being, ago, why, into=None):
        if b.status != "living":
            return
        b.status = "dormant" if (why == "culture died out" and self.mode == "absolute") else ("merged" if into is not None else "faded")
        b.ended, b.end, b.into = round(float(ago), 3), why, into
        self.by[b.culture] = [x for x in self.by.get(b.culture, []) if x is not b]

    def split(self, child: int, parent: int, ago: float, name: str = ""):
        """A culture born of another copies its beings (cousins) and keeps its faith."""
        if parent in self.faith_of and child not in self.faith_of:
            self._join(child, self.faith_of[parent], ago)
        for p in list(self.by.get(parent, [])):
            self._new(p.w.copy(), ago, child, "split", p.id).dev = p.dev
            self.by[child][-1].ind = p.ind
        if self.by.get(child):
            self._ev(ago, "split", f"{len(self.by[child])} beings copied from {parent} to {name or child}", culture=child, parent=parent)

    def merge(self, lose: int, keep: int, ago: float):
        """Syncretism: the lost culture's beings fuse with the most alike of the survivor's, or are carried in."""
        for b in list(self.by.get(lose, [])):
            mates = self.by.get(keep, [])
            best = max(mates, key=lambda m: _cos(m.w, b.w), default=None)
            if best is not None and _cos(best.w, b.w) >= FUSE_COS:
                tot = best.dev + b.dev + 1e-9
                best.w = (best.w * best.dev + b.w * b.dev) / tot
                best.w /= best.w.sum()
                best.ind = max(best.ind, b.ind)
                best.fused.append(b.id)
                self._end(b, ago, "fused", best.id)
                self._ev(ago, "merge", f"being {b.id} fused into {best.id} (cultures {lose} -> {keep})", being=b.id, into=best.id)
            else:
                self.by[lose].remove(b)
                b.culture = keep
                self.by.setdefault(keep, []).append(b)
                self._ev(ago, "carry", f"being {b.id} carried into culture {keep}", being=b.id)
        self.by.pop(lose, None)
        if keep not in self.faith_of and lose in self.faith_of:
            self._join(keep, self.faith_of[lose], ago)
        self._leave(lose, ago, "its cultures ended")

    def died(self, c: int, ago: float):
        for b in list(self.by.get(c, [])):
            self._end(b, ago, "culture died out")
        self.by.pop(c, None)
        self._leave(c, ago, "its cultures ended")

    def frame(self, ago: float, cultures: dict[int, dict], contacts=None, where: dict | None = None):
        """One frame. cultures: culture id -> {"sal": salience array, "know": set of techs, "place": str} for each culture with cells
        and a people that has spirit_ritual (the rest have no gods yet). contacts: pairs of cultures in touch this frame (faith spread);
        where: culture -> (cells, sum of their unit vectors) (the faiths' track)."""
        dt = 0.0 if self.prev is None else max(self.prev - ago, 0.0)
        self.prev = ago
        for c, u in cultures.items():
            sal, bs = u["sal"], self.by.setdefault(c, [])
            if not bs:  # (founded: the BEING_MIN most salient domains; a culture with no faith yet founds one)
                if c not in self.faith_of:
                    self._join(c, self._found_faith(c, ago, DOMAINS[int(np.argmax(sal))]), ago)
                for d in np.argsort(-sal)[:BEING_MIN]:
                    b = self._new(_spread(int(d), sal), ago, c, "founded")
                    self._ev(ago, "birth", f"founded: {label(b.w, 0.05)} in culture {c}", being=b.id, culture=c)
                continue
            for b in bs:
                if dt > 0:
                    b.w = _drift(b.w, sal, dt)
                    fit = float(b.w @ sal)
                    k = 1.0 - math.exp(-dt / TAU_DEV)
                    b.dev += (min(1.0, fit / FIT_FULL) - b.dev) * k
            self._dedupe(c, ago)
            bs = self.by[c]
            covered = {d for d in range(len(DOMAINS)) if any(b.w[d] >= COVER_W for b in bs)}
            for d, s in enumerate(sal):
                key = (c, d)
                if s >= BORN_SAL and d not in covered and len(bs) < BEING_MAX:
                    self.unmet[key] = self.unmet.get(key, 0.0) + dt
                    if self.unmet[key] >= BORN_KYR:
                        b = self._new(_spread(d, sal), ago, c, "born")
                        self._ev(ago, "birth", f"born: {label(b.w, 0.05)} in culture {c}", being=b.id, culture=c)
                        self.unmet.pop(key)
                        covered.add(d)
                else:
                    self.unmet.pop(key, None)
            for b in list(bs):
                if b.dev < FADE_DEV and len(bs) > 1:
                    self._end(b, ago, "no worshippers left to fit")
                    self._ev(ago, "fade", f"{label(b.w, b.ind)} faded (culture {c})", being=b.id)
            bs = self.by[c]
            if dt > 0 and bs:  # individuation: the most devoted being goes furthest
                lead = min(bs, key=lambda b: (-b.dev, b.id))
                top = tier(u["know"], True)
                rest = tier(u["know"], False)
                k = 1.0 - math.exp(-dt / TAU_IND)
                for b in bs:
                    b.high = b is lead
                    goal = (top if b.high else rest) * (0.5 + 0.5 * b.dev / max(lead.dev, 1e-9))
                    b.ind += (goal - b.ind) * k
            for b in bs:
                if not b.hist or abs(b.hist[-1][0] - ago) >= 0.5:
                    b.hist.append([round(float(ago), 3), round(float(b.ind), 3), DOMAINS[int(np.argmax(b.w))]])
        if dt > 0:
            self._schisms(ago, dt)
            self._conversions(ago, dt, contacts)
        self.faith_track(ago, where)

    def _dedupe(self, c: int, ago: float):
        """Beings of one culture that have come to be the same fuse (the older keeps its id)."""
        bs = sorted(self.by.get(c, []), key=lambda b: b.id)
        for i, a in enumerate(bs):
            if a.status != "living":
                continue
            for b in bs[i + 1:]:
                if b.status == "living" and _cos(a.w, b.w) >= SAME_COS:
                    tot = a.dev + b.dev + 1e-9
                    a.w = (a.w * a.dev + b.w * b.dev) / tot
                    a.w /= a.w.sum()
                    a.ind, a.dev = max(a.ind, b.ind), max(a.dev, b.dev)
                    a.fused.append(b.id)
                    self._end(b, ago, "fused", a.id)

    def living(self) -> list[Being]:
        return [b for b in self.beings if b.status == "living"]

    def grants_spells(self, b: Being) -> bool:
        """belief_only: nothing is real, no spells. faith_made: a living being above the threshold. absolute: any being above it."""
        if self.mode == "belief_only" or b.ind < SPELL_IND:
            return False
        return b.status == "living" or (self.mode == "absolute" and b.status == "dormant")


def being_doc(P: Pantheons, b: Being, place: dict | None = None) -> dict:
    w = b.w
    top = [(DOMAINS[i], round(float(w[i]), 3)) for i in np.argsort(-w)[:4] if w[i] > 0.02]
    pl = (place or {}).get(b.culture)
    name = label(w, b.ind)
    bound = f"{FEATURE[top[0][0]]}{' of ' + pl if pl else ''}" if b.ind < 0.3 else None
    return {"id": b.id, "label": name, "born_kyr": round(float(b.born), 3), "culture": b.culture, "how": b.how, "parent": b.parent, "fused": b.fused,
            "top": top, "individuation": round(float(b.ind), 3), "devotion": round(float(b.dev), 3), "bound_to": bound,
            "high": b.high, "status": b.status, "ended_kyr": b.ended, "end": b.end, "into": b.into,
            "grants_spells": P.grants_spells(b), "first_domain": b.top0, "faith": b.faith, "history": b.hist[:: max(1, len(b.hist) // 12)] if b.hist else []}


def _resolver(doc: dict):
    """culture -> the culture it stands in at a time, through the merges (a culture that ended as merged: cultures.json end/into/ended_kyr,
    which holds both the contact and state merges and the cultures whose last deme fused into another's)."""
    into = {c["id"]: (c["ended_kyr"], c["into"]) for c in doc["cultures"] if c["end"] == "merged" and c["into"] is not None and c["ended_kyr"] is not None}

    def res(c: int, ago: float) -> int:
        while c in into and into[c][0] >= ago - 1e-9:
            c = into[c][1]
        return c
    return res


def derive(run_dir: Path, mode: str = MODE_DEFAULT, techtree: dict | None = None) -> dict:
    """gods.json of a stored peoples run that has cultures (read-only). techtree: a fresh techtree.build to use instead of the run's
    stored one (a run made before the faith nodes lacks them: gods_mode and the faith techs are read from it)."""
    from .. import store as S
    from .. import timeline as T
    from ..geo import is_land
    from ..grid import shared_grid
    from . import land as LD
    from .history.habitat import biome_class
    from .history.tags import _tags
    from .output import read_presence
    t0 = time.time()
    run_dir = Path(run_dir)
    run, arr = T.load_frames(run_dir, ("elevation", "ice", "precipitation", "climate", "tree_cover"))
    m = run["meta"]
    doc = json.loads((run_dir / m["cultures"]["file"]).read_text())
    dm = json.loads((run_dir / m["demes"]["file"]).read_text())
    fa = (m["demes"].get("all") or {}).get("file")
    allv = np.fromfile(run_dir / fa, dtype="<u2") if fa and (run_dir / fa).exists() else None
    pt = read_presence(run_dir, m) if allv is not None else None
    if pt is not None and len(pt["cells"]) != len(allv):
        pt = None
    if pt is None:
        arr.update(S.read_layers(run_dir, run["layers"], ("demes",)))
    g = shared_grid(m["level"])
    tt = techtree or m.get("techtree") or {}
    known = tt.get("known") or {}
    lines = {l["id"]: l for l in m["lineages"]}
    goods = LD.goods(m.get("world")) if m.get("world") else None
    volc = np.asarray(goods["volcanic"], float) if goods and "volcanic" in goods else None
    flow = None
    if m.get("world"):
        try:
            flow = np.asarray(json.loads(S.find_world(m["world"]).read_text())["layers"].get("flow"), float)
        except (SystemExit, TypeError, KeyError):
            flow = None
    C = doc["cultures"]
    dc = np.asarray(doc["deme_culture"], np.int64)
    res = _resolver(doc)
    place = {c["id"]: c.get("place") for c in C}
    agos = [max(0.0, -f["t"]) for f in run["frames"]]
    win = doc.get("from_kyr", 300.0)
    use = [j for j, a in enumerate(agos) if a <= win + 1e-9 and (j + 1 == len(agos) or agos[j + 1] < a)]
    P = Pantheons(mode, int(m.get("seed") or 0))
    U = np.asarray(g.centers, float)  # (unit vectors: the faiths' centres)
    src, dst = np.asarray(g.nbr_src), np.asarray(g.nbr_idx)
    seen: set = set()
    ended = sorted((c for c in C if c["end"] in ("merged", "died out") and c["ended_kyr"] is not None), key=lambda c: -c["ended_kyr"])
    ei = 0
    for j in use:
        ago = agos[j]
        elev, ice = T.frame(run, arr, "elevation", j).astype(float), T.frame(run, arr, "ice", j).astype(float)
        env = {nm: T.frame(run, arr, nm, j).astype(float) for nm in ("precipitation", "climate", "tree_cover")}
        env["elevation"], env["ice"], env["land"] = elev, ice, is_land(elev, ice)
        tags = _tags(g, env, chains=False, volcanic=volc)
        biome = biome_class(env, tags)
        fl = np.zeros(g.n, bool)
        if flow is not None and tags["land"].any():
            f = np.where(tags["land"], flow, 0)
            fl = tags["land"] & (f >= max(np.quantile(f[tags["land"]], RIVER_Q), 1e-9))
        if pt is not None:
            a, b = int(pt["offsets"][j, 0]), int(pt["offsets"][j, -1])
            cell, deme = pt["cells"][a:b].astype(np.int64), allv[a:b]
        else:
            lead = np.asarray(arr["demes"][j])
            cell = np.flatnonzero(lead != NONE)
            deme = lead[cell]
        ok = deme != NONE
        cell, deme = cell[ok], deme[ok].astype(np.int64)
        cul = np.array([res(int(dc[d]), ago) if dc[d] >= 0 else -1 for d in deme], np.int64)
        on = cul >= 0
        cell, cul = cell[on], cul[on]
        nC = len(C)
        n = np.bincount(cul, minlength=nC).astype(float)
        feats = {
            "coast": tags["coast"], "river": fl, "mountain": tags["mountain"], "desert": tags["desert"],
            "forest": tags["forest"] | tags["jungle"], "wet": tags["jungle"] | tags["wetland"],
            "open": tags["open"] | tags["steppe"], "tundra": tags["tundra"], "volcanic": tags["volcanic"], "island": tags["island"],
            "lowland": tags["lowland"],
        }
        share = {k: np.bincount(cul, weights=v[cell].astype(float), minlength=nC) / np.maximum(n, 1) for k, v in feats.items()}
        # the events of this frame, oldest first: culture ends, merges (before the frame's beings are tended)
        while ei < len(ended) and ended[ei]["ended_kyr"] >= ago - 1e-9:
            e = ended[ei]
            if e["end"] == "merged" and e["into"] is not None:
                P.merge(e["id"], res(e["into"], e["ended_kyr"]), e["ended_kyr"])
            else:
                P.died(e["id"], e["ended_kyr"])
            ei += 1
        cur: dict[int, dict] = {}
        for c in np.flatnonzero(n).tolist():
            u = C[c]
            kn = {t for t, v in (known.get(u["people"]) or {}).items() if v[0] >= ago - 1e-9}
            if "spirit_ritual" not in kn:
                continue
            ln = lines.get(u["people"]) or {}
            tr = tuple(ln.get("traits") or ())
            sal = salience({k: float(v[c]) for k, v in share.items()}, kn, (u.get("traits") or {}).get("ways_now"), tr)
            if c not in seen:
                seen.add(c)
                par = u.get("parent")
                if par is not None and P.by.get(res(par, ago)):
                    P.split(c, res(par, ago), ago, u["name"])
            cur[c] = {"sal": sal, "know": kn}
        uv = np.stack([np.bincount(cul, weights=U[cell, k], minlength=nC) for k in range(3)], 1) if cur else None
        P.frame(ago, cur, contacts(g.n, cell, cul, src, dst, nC), {c: (int(n[c]), uv[c]) for c in cur} if cur else None)
    for e in ended[ei:]:  # (ends after the last frame's pass)
        P.merge(e["id"], res(e["into"], e["ended_kyr"]), e["ended_kyr"]) if e["end"] == "merged" and e["into"] is not None else P.died(e["id"], e["ended_kyr"])
    docs = [being_doc(P, b, place) for b in P.beings]
    faiths = faith_docs(P, C)
    cl = {}
    for b in docs:
        cl.setdefault(b["culture"], []).append(b["id"])
    out = {"format": "procgen-gods/1", "gods_mode": mode, "from_kyr": win, "domains": list(DOMAINS), "groups": {k: list(v) for k, v in GROUPS.items()},
           "constants": {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float))} | {"tiers": dict(TIERS)},
           "beings": docs, "events": P.events, "faiths": {"rule": FAITH_RULE, "list": faiths},
           "frames": [[j, round(float(agos[j]), 3)] for j in use],
           "cultures": {str(c): {"name": C[c]["name"], "people": C[c]["people"], "beings": ids,
                                 "living": [i for i in ids if docs[i]["status"] == "living"],
                                 "faiths": P.fhist.get(c, []), "faith_now": P.faith_of.get(c),
                                 "ritual_since_kyr": (known.get(C[c]["people"]) or {}).get("spirit_ritual", [None])[0]} for c, ids in cl.items()},
           "summary": summary(docs, mode, round(time.time() - t0, 1)) | {"faiths": {**P.counts, "ever": len(faiths),
                                                                                       "living": sum(f["ended_kyr"] is None for f in faiths)}}}
    return out


FAITH_RULE = ("A culture with no faith founds one when it first has gods; daughter cultures keep their parent's faith; a culture whose leading "
              f"god has turned to another domain than its faith's core for {SCHISM_KYR:g} kyr breaks away as a new faith; a culture in touch with "
              f"a culture of another faith whose leading god is at least {CONVERT_MIN:g} individuated (temples) and {CONVERT_GAP:g} more than its own "
              f"converts with chance 1 - exp(-dt/{TAU_CONVERT:g} kyr) per frame, taking a copy of that god (and does not break away by drift after); "
              "a faith with no cultures left ends.")


def contacts(n_cells: int, cell: np.ndarray, cul: np.ndarray, src: np.ndarray, dst: np.ndarray, nC: int) -> set:
    """Pairs (a < b) of cultures in touch in one frame: on one cell (overlapping peoples) or on neighbouring cells."""
    out: set = set()
    if not len(cell):
        return out
    o = np.lexsort((cul, cell))
    cs, us = cell[o], cul[o]
    same = (cs[1:] == cs[:-1]) & (us[1:] != us[:-1])
    lab = np.full(n_cells, -1, np.int64)
    lab[cell] = cul
    a, b = lab[src], lab[dst]
    e = (a >= 0) & (b >= 0) & (a != b)
    pa = np.concatenate([us[:-1][same], a[e]])
    pb = np.concatenate([us[1:][same], b[e]])
    key = np.unique(np.minimum(pa, pb) * nC + np.maximum(pa, pb))
    return {(int(k // nC), int(k % nC)) for k in key}


def faith_color(i: int) -> str:
    """A faith's colour: hues a golden angle apart, two lightnesses alternating."""
    import colorsys
    r, g, b = colorsys.hls_to_rgb((i * 0.381966) % 1.0, 0.55 if i % 2 else 0.68, 0.65)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def faith_docs(P: Pantheons, C: list) -> list:
    """The faiths as records: who founded them, when, from which faith, their cultures now and their track over time."""
    out = []
    word = {"founded": "faith", "schism": "schism"}
    for F in P.faiths:
        oc = C[F.origin]
        now = sorted(F.members) if F.ended is None else []
        bs = [b for b in P.beings if b.faith == F.id]
        lead = max((b for c in now for b in P.by.get(c, [])), key=lambda b: (b.ind, b.dev), default=None)  # (its cultures' most individuated god now)
        out.append({"id": F.id, "name": f"the {F.core} {word[F.how]} of {oc['name']}", "how": F.how, "parent": F.parent, "color": faith_color(F.id),
                    "origin_culture": F.origin, "origin_people": oc["people"], "founded_kyr": F.founded, "core": F.core,
                    "ended_kyr": F.ended, "end": F.end, "cultures_now": now, "peoples_now": sorted({C[c]["people"] for c in now}),
                    "cultures_ever": sorted({c for c, h in P.fhist.items() if any(x[1] == F.id for x in h)}),
                    "beings": [b.id for b in bs], "lead_being": lead.id if lead else None, "changes": F.changes, "events": F.events,
                    "track": F.track})
    return out


def summary(docs: list[dict], mode: str, secs: float = 0.0) -> dict:
    liv = [b for b in docs if b["status"] == "living"]
    return {"mode": mode, "beings": len(docs), "living": len(liv), "faded": sum(b["status"] == "faded" for b in docs),
            "merged": sum(b["status"] == "merged" for b in docs), "dormant": sum(b["status"] == "dormant" for b in docs),
            "spell_granting": sum(b["grants_spells"] for b in liv), "oldest_kyr": max((b["born_kyr"] for b in docs), default=None),
            "by_how": {h: sum(b["how"] == h for b in docs) for h in ("founded", "born", "split")}, "generated_in_s": secs}


def write(run_dir: Path, out_dir: Path | None = None, mode: str = MODE_DEFAULT, techtree: dict | None = None) -> dict:
    """gods.json into the run (or out_dir, leaving the run untouched); returns its summary."""
    from .. import store as S
    d = derive(Path(run_dir), mode, techtree)
    dest = Path(out_dir) if out_dir else Path(run_dir)
    dest.mkdir(parents=True, exist_ok=True)
    S.write_atomic(dest / "gods.json", json.dumps(d, separators=(",", ":")))
    return d["summary"]
