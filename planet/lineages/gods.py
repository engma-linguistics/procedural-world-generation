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

Faiths you write (PW-1430): authored.json in the run (read_authored) holds faiths Daniel wrote in the viewer: a name, a founding culture,
people or place, a year, named gods with their domains, and whether it spreads. Each is founded under the same rules, at the first frame
from its year on at which its founder is on the map and has gods (spirit ritual): the founding culture takes the new faith (its old one
may end, "no followers left"), gains the named gods as its leading beings (its own gods stay, as after a conversion), and from then on
drifts, fades, splits into daughters, merges and converts its neighbours (if it spreads) like any faith. One that cannot take hold
(no such culture, a year after the present, a founder that died out first) says why in the read-out (doc "authored"). The expensive
part (the land per culture per frame: inputs()) does not depend on the faiths, so a change re-runs only replay(): seconds, not the
peoples.
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
PLACE_KM = 400.0  # JUDGEMENT: a faith written at a place is founded by the culture nearest it, if one is this close
R_KM = 6371.0  # (the place distance on the grid's unit sphere; the planets are Earth-sized, PW-443 for others)
AUTHORED_FILE = "authored.json"
AUTHORED_FORMAT = "procgen-authored/2"  # (/2: the invasions you schedule, PW-1433)
AUTHORED_MAX, AUTHORED_GODS_MAX = 40, BEING_MAX  # (a sane cap per run and per faith)


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
    __slots__ = ("id", "w", "dev", "ind", "born", "culture", "how", "parent", "fused", "status", "ended", "end", "into", "hist", "top0", "high", "faith", "name")

    def __init__(self, id_, w, born, culture, how, parent=None):
        self.id, self.w, self.born, self.culture, self.how, self.parent = id_, w, born, culture, how, parent
        self.dev, self.ind = 0.5, 0.05
        self.fused: list = []
        self.status, self.ended, self.end, self.into = "living", None, None, None
        self.hist: list = []
        self.top0 = DOMAINS[int(np.argmax(w))]
        self.high = False
        self.faith = None
        self.name = None  # (a god Daniel named, PW-1430)


class Faith:
    __slots__ = ("id", "origin", "founded", "parent", "how", "core", "ended", "end", "members", "track", "changes", "events", "name", "authored", "spreads")

    def __init__(self, id_, origin, founded, how, core, parent=None):
        self.id, self.origin, self.founded, self.how, self.core, self.parent = id_, origin, founded, how, core, parent
        self.ended, self.end = None, None
        self.members: set = set()
        self.track: list = []
        self.changes: list = []
        self.events: list = []
        self.name, self.authored, self.spreads = None, None, True


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
        self.counts = {"founded": 0, "schisms": 0, "conversions": 0, "core_changes": 0, "authored": 0}
        self.closed: set = set()  # faiths that take no converts (authored, "stays closed")

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
        self.counts[{"founded": "founded", "authored": "authored"}.get(how, "schisms")] += 1
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
                if x in done or x not in self.faith_of or y not in self.faith_of or self.faith_of[x] == self.faith_of[y] or self.faith_of[y] in self.closed:
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

    def found_authored(self, c: int, ago: float, spec: dict) -> int:
        """A faith Daniel wrote (PW-1430), founded in culture c now: c takes it (as a conversion: its own gods stay, the named ones lead,
        and it does not break away by drift); the old faith may end. spec: clean_authored's form. Returns the faith id."""
        gods = [(g["name"], [d for d in g["domains"] if d in DOMAINS]) for g in spec.get("gods") or []]
        gods = [(n, ds) for n, ds in gods if ds]
        L = self.lead(c)
        core = gods[0][1][0] if gods else (DOMAINS[int(np.argmax(L.w))] if L else "ancestors")
        old = self.faith_of.get(c)
        f = self._found_faith(c, ago, core, "authored")
        F = self.faiths[f]
        F.name, F.authored, F.spreads = spec["name"], spec["id"], bool(spec.get("spreads", True))
        if not F.spreads:
            self.closed.add(f)
        self._join(c, f, ago)
        self.converted.add(c)
        self.off.pop(c, None)
        ind = L.ind if L else 0.05
        for b in self.by.get(c, []):  # (the named gods lead: the old ones step down a little)
            b.dev = min(b.dev, 0.95)
        for k, (name, ds) in enumerate(gods):
            w = np.zeros(len(DOMAINS))
            w[[DOMAINS.index(d) for d in ds]] = 1.0
            b = self._new(w / w.sum(), ago, c, "authored")
            b.name, b.dev, b.ind = name, 1.0 - 0.01 * k, ind
            b.hist.append([round(float(ago), 3), round(float(ind), 3), DOMAINS[int(np.argmax(b.w))]])
            self._ev(ago, "birth", f"written in: {name} in culture {c}", being=b.id, culture=c)
        if old is not None:
            F.events.append([round(float(ago), 3), "founded", c, old])
            self._check_end(old, ago, "no followers left")
        return f

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

    def frame(self, ago: float, cultures: dict[int, dict], contacts=None, where: dict | None = None, found=None):
        """One frame. cultures: culture id -> {"sal": salience array, "know": set of techs, "place": str} for each culture with cells
        and a people that has spirit_ritual (the rest have no gods yet). contacts: pairs of cultures in touch this frame (faith spread);
        where: culture -> (cells, sum of their unit vectors) (the faiths' track). found: [(culture, authored spec)] founded this frame
        (after the cultures' own gods are tended; each spec's "faith" is set to its new faith's id)."""
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
        for c, spec in found or ():
            if c in cultures:
                spec["faith"] = self.found_authored(c, ago, spec)
        if dt > 0:
            self._schisms(ago, dt)
            self._conversions(ago, dt, contacts)
        self.faith_track(ago, where)

    def _dedupe(self, c: int, ago: float):
        """Beings of one culture that have come to be the same fuse (the older keeps its id)."""
        bs = sorted(self.by.get(c, []), key=lambda b: b.id)
        for i, a in enumerate(bs):
            if a.status != "living" or a.name:
                continue
            for b in bs[i + 1:]:
                if b.status == "living" and not b.name and _cos(a.w, b.w) >= SAME_COS:  # (a named god keeps its name: never fused away)
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
    role = label(w, b.ind)
    bound = f"{FEATURE[top[0][0]]}{' of ' + pl if pl else ''}" if b.ind < 0.3 else None
    return {"id": b.id, "label": f"{b.name}, {role}" if b.name else role, "name": b.name, "role": role, "born_kyr": round(float(b.born), 3), "culture": b.culture, "how": b.how, "parent": b.parent, "fused": b.fused,
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


def inputs(run_dir: Path, techtree: dict | None = None) -> dict:
    """The part of derive() that reads the run: per used frame, the cultures with gods and their land (salience), their contacts and
    centres, who is on the map, and the culture ends to apply. It does not depend on the gods mode or the authored faiths, so the server
    keeps it and re-runs only replay() after an edit. techtree: a fresh techtree.build to use instead of the run's stored one."""
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
    dm = json.loads((run_dir / m["demes"]["file"]).read_text())  # noqa: F841 (read as before: a run without demes fails here, not later)
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
    agos = [max(0.0, -f["t"]) for f in run["frames"]]
    win = doc.get("from_kyr", 300.0)
    use = [j for j, a in enumerate(agos) if a <= win + 1e-9 and (j + 1 == len(agos) or agos[j + 1] < a)]
    U = np.asarray(g.centers, float)  # (unit vectors: the faiths' centres)
    src, dst = np.asarray(g.nbr_src), np.asarray(g.nbr_idx)
    seen: set = set()
    gone = {c["id"]: c["ended_kyr"] for c in C if c["end"] in ("merged", "died out") and c["ended_kyr"] is not None}
    ended = sorted((c for c in C if c["id"] in gone), key=lambda c: -c["ended_kyr"])
    def died_by(c, at):  # (PW-1313: a culture that merges into one that had already died out dies with it: its gods do not live on in a dead culture)
        return C[c]["end"] == "died out" and C[c]["ended_kyr"] is not None and C[c]["ended_kyr"] >= at - 1e-9
    endev = [("merge", e["id"], res(e["into"], e["ended_kyr"]), e["ended_kyr"])
             if e["end"] == "merged" and e["into"] is not None and not died_by(res(e["into"], e["ended_kyr"]), e["ended_kyr"])
             else ("died", e["id"], None, e["ended_kyr"]) for e in ended]
    ei = 0
    frames = []
    for j in use:
        ago = agos[j]
        elev, ice = T.frame(run, arr, "elevation", j).astype(float), T.frame(run, arr, "ice", j).astype(float)
        env = {nm: T.frame(run, arr, nm, j).astype(float) for nm in ("precipitation", "climate", "tree_cover")}
        env["elevation"], env["ice"], env["land"] = elev, ice, is_land(elev, ice)
        tags = _tags(g, env, chains=False, volcanic=volc)
        biome_class(env, tags)
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
        # PW-1313: a culture that has ended (died out, or merged into one that has itself ended) keeps no cells after its end: the
        # presence lags the culture's record, and a dead culture's cells would found new gods that never fade
        on = cul >= 0
        if on.any():
            dead = np.array([gone.get(int(c), -1.0) >= ago - 1e-9 for c in np.unique(cul[on])])
            if dead.any():
                bad = np.unique(cul[on])[dead]
                on &= ~np.isin(cul, bad)
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
        ends = []
        while ei < len(endev) and endev[ei][3] >= ago - 1e-9:  # (the frame's culture ends and merges, before its beings are tended)
            ends.append(endev[ei])
            ei += 1
        cur: dict[int, dict] = {}
        first = []
        present = np.flatnonzero(n).tolist()
        for c in present:
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
                if par is not None:
                    first.append((c, res(par, ago), u["name"]))
            cur[c] = {"sal": sal, "know": kn}
        uv = np.stack([np.bincount(cul, weights=U[cell, k], minlength=nC) for k in range(3)], 1) if cur else None
        frames.append({"j": j, "ago": ago, "ends": ends, "first": first, "cur": cur, "contacts": contacts(g.n, cell, cul, src, dst, nC),
                       "where": {c: (int(n[c]), uv[c]) for c in cur} if cur else None, "present": {c: int(n[c]) for c in present},
                       "cell": cell.astype(np.int32), "cul": cul.astype(np.int32)})
    return {"C": C, "res": res, "known": known, "win": win, "seed": int(m.get("seed") or 0), "frames": frames, "after": endev[ei:],
            "U": U, "lines": {k: v.get("name", k) for k, v in lines.items()}, "secs": round(time.time() - t0, 1)}


def derive(run_dir: Path, mode: str = MODE_DEFAULT, techtree: dict | None = None, authored: list | None = None) -> dict:
    """gods.json of a stored peoples run that has cultures (read-only). techtree: a fresh techtree.build to use instead of the run's
    stored one (a run made before the faith nodes lacks them: gods_mode and the faith techs are read from it). authored: the faiths
    written in (PW-1430); None reads the run's authored.json."""
    if authored is None:
        authored = read_authored(run_dir)["faiths"]
    return replay(inputs(run_dir, techtree), mode, authored)


def replay(inp: dict, mode: str = MODE_DEFAULT, authored: list | None = None) -> dict:
    """The gods and faiths from inputs(): the Pantheons fed frame by frame, the authored faiths founded when their founders are there."""
    t0 = time.time()
    C, res, known, win = inp["C"], inp["res"], inp["known"], inp["win"]
    place = {c["id"]: c.get("place") for c in C}
    P = Pantheons(mode, inp["seed"])
    specs, notes = clean_authored(authored or [], len(C), set(inp["lines"]), strict=False)
    todo = [dict(s, faith=None, why=None, took=None) for s in specs]
    for s in todo:
        if s["ago_kyr"] < -1e-9:
            s["took"], s["why"] = False, "its year is after the present"
        elif s["ago_kyr"] > win + 1e-9:
            s["note"] = f"its year is before the religion's window ({win:g} kyr): founded at the window's start, when its founder had gods"
    frames = inp["frames"]
    for fr in frames:
        ago = fr["ago"]
        for kind, c, into, at in fr["ends"]:
            P.merge(c, into, at) if kind == "merge" else P.died(c, at)
        for c, par, name in fr["first"]:
            if P.by.get(par):
                P.split(c, par, ago, name)
        found = []
        for s in todo:
            if s["took"] is None and min(s["ago_kyr"], win) >= ago - 1e-9:
                c = _founder(s, fr, inp)
                if c is not None:
                    found.append((c, s))
        P.frame(ago, fr["cur"], fr["contacts"], fr["where"], found)
        for c, s in found:
            s["took"], s["culture_now"], s["founded_kyr"] = True, c, round(float(ago), 3)
            if s.get("first_why") and min(s["ago_kyr"], win) - ago > 0.5:
                s["note"] = (s.get("note") + "; " if s.get("note") else "") + f"it took hold later than asked: at first {s['first_why']}"
        for s in todo:
            if s["took"] is None and s["why"]:
                s.setdefault("first_why", s["why"])
    for kind, c, into, at in inp["after"]:  # (ends after the last frame's pass)
        P.merge(c, into, at) if kind == "merge" else P.died(c, at)
    for s in todo:
        if s["took"] is None:
            s["took"] = False
            s["why"] = "never took hold: " + (s["why"] or "its founder was never on the map with gods")
    docs = [being_doc(P, b, place) for b in P.beings]
    faiths = faith_docs(P, C)
    cl = {}
    for b in docs:
        cl.setdefault(b["culture"], []).append(b["id"])
    out = {"format": "procgen-gods/1", "gods_mode": mode, "from_kyr": win, "domains": list(DOMAINS), "groups": {k: list(v) for k, v in GROUPS.items()},
           "constants": {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float))} | {"tiers": dict(TIERS)},
           "beings": docs, "events": P.events, "faiths": {"rule": FAITH_RULE, "list": faiths},
           "frames": [[fr["j"], round(float(fr["ago"]), 3)] for fr in frames],
           "cultures": {str(c): {"name": C[c]["name"], "people": C[c]["people"], "beings": ids,
                                 "living": [i for i in ids if docs[i]["status"] == "living"],
                                 "faiths": P.fhist.get(c, []), "faith_now": P.faith_of.get(c),
                                 "ritual_since_kyr": (known.get(C[c]["people"]) or {}).get("spirit_ritual", [None])[0]} for c, ids in cl.items()},
           "authored": {"rule": AUTHORED_RULE, "faiths": [authored_readout(s, faiths, C) for s in todo], "problems": notes},
           "summary": summary(docs, mode, round(inp.get("secs", 0.0) + time.time() - t0, 1)) | {"faiths": {**P.counts, "ever": len(faiths),
                                                                                                     "living": sum(f["ended_kyr"] is None for f in faiths)}}}
    return out


def _founder(s: dict, fr: dict, inp: dict) -> int | None:
    """The culture that founds an authored faith in this frame, or None (s["why"] says why not, for the read-out)."""
    C, cur, pres, res = inp["C"], fr["cur"], fr["present"], inp["res"]
    when = fr["ago"]
    if s.get("culture") is not None:
        c0 = s["culture"]
        c = res(c0, when)
        x = C[c0]
        if c in cur:
            if c != c0:
                s["note"] = f"{x['name']} had merged into {C[c]['name']}, which founded it"
            return c
        if x["born_kyr"] is not None and x["born_kyr"] < when - 1e-9:
            s["why"] = f"{x['name']} did not exist yet (it began {x['born_kyr']:g} kyr ago)"
        elif C[c]["end"] == "died out" and C[c]["ended_kyr"] is not None and C[c]["ended_kyr"] >= when - 1e-9:
            s["why"] = f"{C[c]['name']} had died out ({C[c]['ended_kyr']:g} kyr ago) before it had gods"
            s["took"] = False
        elif c in pres:
            s["why"] = f"{C[c]['name']}'s people had no spirit ritual yet (no ritual, no gods)"
        else:
            s["why"] = f"{C[c]['name']} was not on the map"
        return None
    cand = [c for c in pres if s.get("people") is None or C[c]["people"] == s["people"]]
    who = inp["lines"].get(s.get("people"), s.get("people"))
    if s.get("place") is not None:
        lat, lon = map(math.radians, s["place"])
        p = np.array([math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)])
        cell, cul = fr["cell"], fr["cul"]
        ok = np.isin(cul, cand) if s.get("people") is not None else np.ones(len(cul), bool)
        if not ok.any():
            s["why"] = f"no {who} on the map" if who else "nobody on the map"
            return None
        d = inp["U"][cell[ok]] @ p
        k = int(np.argmax(d))
        km = math.acos(max(-1.0, min(1.0, float(d[k])))) * R_KM
        if km > PLACE_KM:
            s["why"] = f"no {(who + ' ') if who else ''}culture within {PLACE_KM:g} km of the place (the nearest was {km:,.0f} km away)"
            return None
        c = int(cul[ok][k])
        if c not in cur:
            s["why"] = f"{C[c]['name']}, at the place, had no spirit ritual yet (no ritual, no gods)"
            return None
        return c
    withg = [c for c in cand if c in cur]
    if not withg:
        s["why"] = (f"the {who} had no spirit ritual yet (no ritual, no gods)" if cand else f"no {who} on the map")
        return None
    return max(withg, key=lambda c: (pres[c], -c))  # (no place: the people's largest culture with gods)


AUTHORED_RULE = ("A faith you write is founded at the first stored moment from its year on at which its founder (the culture; else the "
                 "people's culture nearest the place, or its largest; else the culture nearest the place, within "
                 f"{PLACE_KM:g} km) is on the map and has gods (spirit ritual). That culture takes it as a conversion: its own gods stay, the "
                 "named gods lead, its old faith may end. After that it lives under the same rules as every faith: its gods drift toward the "
                 "land, may fade, are copied into daughter cultures and fuse at merges; it wins neighbours only if it spreads and its "
                 f"leading god is at least {CONVERT_MIN:g} individuated (temples).")


def clean_authored(faiths, n_cultures: int, peoples: set, strict: bool = True) -> tuple[list, list]:
    """Authored faiths in a checked form: [{id, name, culture, people, place, ago_kyr, year_text, gods: [{name, domains}], spreads}].
    strict: raise ValueError at the first problem (the POST); else skip what is broken and say so (a hand-edited file never crashes
    the read-out). Returns (faiths, problems)."""
    out, notes = [], []

    def bad(msg):
        if strict:
            raise ValueError(msg)
        notes.append(msg)
    if not isinstance(faiths, list):
        bad("faiths must be a list")
        return out, notes
    if len(faiths) > AUTHORED_MAX:
        bad(f"at most {AUTHORED_MAX} faiths")
        faiths = faiths[:AUTHORED_MAX]
    ids: set = set()
    for i, f in enumerate(faiths):
        if not isinstance(f, dict):
            bad(f"faith {i + 1}: not an object")
            continue
        nm = str(f.get("name") or "").strip()[:80]
        if not nm:
            bad(f"faith {i + 1}: it needs a name")
            continue
        fid = str(f.get("id") or f"a{i + 1}")[:40]
        while fid in ids:
            fid += "x"
        try:
            ago = float(f.get("ago_kyr"))
        except (TypeError, ValueError):
            ago = float("nan")
        if not math.isfinite(ago):
            bad(f"{nm}: its year could not be read")
            continue
        c = f.get("culture")
        if c is not None:
            if isinstance(c, bool) or not isinstance(c, (int, float)) or int(c) != c or not 0 <= int(c) < n_cultures:
                bad(f"{nm}: no culture {c} in this run")
                continue
            c = int(c)
        pe = f.get("people") or None
        if pe is not None and pe not in peoples:
            bad(f"{nm}: no people {pe} in this run")
            continue
        pl = f.get("place")
        if pl is not None:
            try:
                lat, lon = float(pl[0]), float(pl[1])
                if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90):
                    raise ValueError
                pl = [round(lat, 3), round((lon + 180.0) % 360.0 - 180.0, 3)]
            except (TypeError, ValueError, IndexError, KeyError):
                bad(f"{nm}: its place must be [latitude, longitude]")
                continue
        if c is None and pe is None and pl is None:
            bad(f"{nm}: pick a founding culture or people, or a place")
            continue
        gods = []
        for k, g in enumerate(f.get("gods") or []):
            if not isinstance(g, dict):
                continue
            gn = str(g.get("name") or "").strip()[:60] or f"god {k + 1}"
            ds = [d for d in (g.get("domains") or []) if isinstance(d, str) and d in DOMAINS]
            unknown = [d for d in (g.get("domains") or []) if d not in DOMAINS]
            if unknown:
                bad(f"{nm}: {gn}: unknown domains {unknown} (they are: {', '.join(DOMAINS)})")
                if strict:
                    continue
            if not ds:
                bad(f"{nm}: {gn} needs at least one domain")
                continue
            gods.append({"name": gn, "domains": list(dict.fromkeys(ds))[:4]})
        if not gods:
            bad(f"{nm}: it needs at least one named god with a domain")
            continue
        if len(gods) > AUTHORED_GODS_MAX:
            bad(f"{nm}: at most {AUTHORED_GODS_MAX} gods")
            gods = gods[:AUTHORED_GODS_MAX]
        ids.add(fid)
        out.append({"id": fid, "name": nm, "culture": c, "people": pe, "place": pl, "ago_kyr": round(ago, 6),
                    "year_text": str(f.get("year_text") or "")[:60], "gods": gods, "spreads": bool(f.get("spreads", True))})
    return out, notes


def authored_readout(s: dict, faiths: list, C: list) -> dict:
    """One authored faith for the viewer: what was asked, whether it took hold (and why not), and how it has fared."""
    r = {k: s.get(k) for k in ("id", "name", "culture", "people", "place", "ago_kyr", "year_text", "gods", "spreads")}
    r |= {"took_hold": bool(s.get("took")), "faith": s.get("faith"), "founded_kyr": s.get("founded_kyr"), "why": s.get("why") if not s.get("took") else None,
          "note": s.get("note"), "founded_in": s.get("culture_now"),
          "founded_in_name": C[s["culture_now"]]["name"] if s.get("culture_now") is not None else None}
    if s.get("took") and s.get("faith") is not None:
        F = faiths[s["faith"]]
        won = sum(e[1] == "converted" for e in F["events"])
        top = max((t[5] for t in F["track"]), default=0.0)
        if not s["spreads"]:
            spread = "stays closed: it takes no converts"
        elif won:
            spread = f"won {won} culture{'s' if won != 1 else ''} by conversion"
        elif top < CONVERT_MIN:
            spread = (f"has not spread: its leading god reached {top:.2f} individuation, and a faith spreads only from {CONVERT_MIN:g} "
                      "(its people needs temples)")
        else:
            spread = f"has not spread: no neighbour of another faith at least {CONVERT_GAP:g} less organised took it up (a chance per contact)"
        r |= {"spread": spread, "ended_kyr": F["ended_kyr"], "end": F["end"], "cultures_now": len(F["cultures_now"]), "cultures_ever": len(F["cultures_ever"])}
    return r


def read_authored(run_dir: Path) -> dict:
    """A run's authored.json (PW-1430): {"format", "gods_mode", "faiths": [...]}; empty when there is none or it cannot be read."""
    f = Path(run_dir) / AUTHORED_FILE
    try:
        d = json.loads(f.read_text())
        if not isinstance(d, dict):
            raise ValueError
    except (OSError, ValueError):
        d = {}
    mode = d.get("gods_mode") if d.get("gods_mode") in GODS_MODES else None
    return {"format": AUTHORED_FORMAT, "gods_mode": mode, "faiths": d.get("faiths") if isinstance(d.get("faiths"), list) else [],
            "invasions": d.get("invasions") if isinstance(d.get("invasions"), list) else []}


def write_authored(run_dir: Path, faiths: list, gods_mode: str | None, n_cultures: int, peoples: set, invasions: list | None = None) -> dict:
    """Check and save a run's authored.json (the server's POST /api/authored, at Daniel's request); returns what was saved. It holds
    all of Daniel's choices for the run: the gods mode, the faiths he wrote and the invasions he scheduled (PW-1433, invasions.clean:
    strict on shape only; None keeps the saved ones)."""
    from .. import store as S
    from . import invasions as IV
    if gods_mode is not None and gods_mode not in GODS_MODES:
        raise ValueError(f"gods_mode must be one of {GODS_MODES}")
    clean, _ = clean_authored(faiths, n_cultures, peoples, strict=True)
    inv, _ = IV.clean(read_authored(run_dir)["invasions"] if invasions is None else invasions, strict=invasions is not None)
    d = {"format": AUTHORED_FORMAT, "gods_mode": gods_mode, "faiths": clean, "invasions": inv}
    S.write_atomic(Path(run_dir) / AUTHORED_FILE, json.dumps(d, indent=1))
    return d


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
        out.append({"id": F.id, "name": F.name or f"the {F.core} {word.get(F.how, 'faith')} of {oc['name']}", "how": F.how, "parent": F.parent,
                    "color": faith_color(F.id), "authored": F.authored, "spreads": F.spreads,
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
