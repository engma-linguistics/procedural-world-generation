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
- Conversion (PW-1477, rates sourced in docs/review/culture/attitudes/round1.md): a culture takes another faith whole, as an event in
  continuous time, along one of three links: an ordinary neighbour whose leading god is at least CONVERT_MIN individuated (temples)
  and CONVERT_GAP above its own (TAU_CONVERT); a missionary neighbour (a faith that seeks converts: written so, or a moralizing high
  god's faith with MISSION_P's chance) when its own faith is not missionary and MISSION_GAP less organised (TAU_MISSION); or its
  rulers (a state, empire or dragon realm of the polities read-out whose ruling culture holds the faith), at a rate set by the
  ruler's religious tolerance (attitudes.py, PW-904, PW-1520: TAU_FORCED to TAU_TOLERANT; ETHNIC_RULE x for a faith that is not missionary). A
  neighbour's pull is x the share of the taker's border facing it and x the taker's religious tolerance x the faith's appeal (its organisation and its fit to the taker's life, appeal(), PW-1520); a ruler's x the share of the
  taker's land it rules. The convert takes a copy of the converter's leading god (how = "converted"), keeping its own old beings
  (syncretism), and the church that converted it holds it (`held`) against faiths no better organised. A converted culture does not
  break away by drift (its old gods leading again would otherwise undo every conversion within SCHISM_KYR); it can still convert
  again, and its daughter cultures can break away.
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
GODS_FORMAT = "procgen-gods/3"  # (/2: each culture's faith shares and the states' and peoples' roll-ups, PW-1489; /3: the religious tolerance, towns and a faith's appeal, PW-1520)
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
CONVERT_MIN, CONVERT_GAP = 0.45, 0.15  # JUDGEMENT: an ordinary faith spreads only from an organised one (temples) to a less individuated one
# Spread rates (PW-1477; sources and checks: docs/review/culture/attitudes/round1.md). A culture converts as a whole, with a hazard per
# kyr from each neighbour (or ruler) that may convert it; the times below are the e-folding (mean waiting) times of one such link.
TAU_CONVERT = 2.0  # kyr, JUDGEMENT within the sourced scale: an ordinary faith (no missionaries) wins a neighbour over a millennium or two, ten times slower than a missionary one (it was 30 kyr: PW-1477)
TAU_MISSION = 0.2  # kyr, sourced scale, judged point: Stark 1996's ~40 %/decade (Fousek et al. 2018: 34 %/decade) takes a population from 1 % to a majority in ~110-130 years; one link's mean wait ~two centuries
MISSION_MIN = 0.2  # JUDGEMENT: a missionary faith needs some organisation (burial's tier: keepers of the rites), not temples
MISSION_GAP = 0.05  # JUDGEMENT: and wins only a culture whose own leading god is at least this much less individuated (no faith is left for one no better organised; CONVERT_GAP is 0.15)
MISSION_IND = 0.7  # JUDGEMENT: a faith may turn missionary once one of its cultures' leading god is this individuated (past kingship's 0.6: the moralizing high god)
MISSION_P = 0.5  # JUDGEMENT: the chance (a seeded draw per faith, once) that such a faith seeks converts; the rest stay ethnic faiths
RECEPT_MID = 0.5  # JUDGEMENT: a culture takes a neighbour's faith at x (its tolerance / RECEPT_MID): 0..2, the insular resist (attitudes.py)
TAU_FORCED = 0.03  # kyr, sourced: forced conversion by a ruler with no tolerance takes a generation (Saxon wars 772-804, 32 years; Lithuania 1387-1413, 26 years)
TAU_TOLERANT = 2.0  # kyr, JUDGEMENT on the sourced side: a fully tolerant ruler barely pushes its faith (Cyrus's restored gods; the Mongols' tolerance, their khans taking their subjects' faiths instead)
# a ruler's push: tau = TAU_FORCED^(1 - tolerance) x TAU_TOLERANT^tolerance (log between them): tolerance 0.6 gives ~0.37 kyr, Bulliet 1979's
# Islamic rule (no forced conversion; a tax on unbelievers): ~40 % Muslim two centuries after the conquest, ~80 % in three to four
SHARE_EDGES = 6  # (a cell two cultures share counts as its six edges between them: touch())
ETHNIC_RULE = 0.1  # JUDGEMENT on a sourced contrast: rulers of a faith that seeks no converts push it at a tenth of the rate (the polytheist empires returned their subjects' gods to their temples, as Cyrus did at Babylon; forced conversion is the exclusive, missionary faiths' habit: the Saxons, Castile 1502)
# Minority faiths (PW-1489; docs/review/culture/faiths/minorities1.md). Each culture holds a share of each faith; its faith (faith_of, the
# majority) is still flipped by the conversion events above, which are the moment the newcomer passes half (Bulliet 1979's conversion
# curve: an S-curve, ~10 % Muslim in the Umayyad period, ~40 % by the mid-9th century, almost all by the end of the 11th). Between events a
# share follows the logistic of the same links: every link that may convert a culture to a faith (or, once it holds that faith, every
# neighbour and ruler of its own faith) grows that faith's share at k = rate x SHARE_SPAN, taken from the other faiths in proportion.
SHARE_SEED = 0.01  # sourced scale: a faith reaching a culture starts with its first converts, 1 % (Stark 1996: ~1,000 Christians in 40 AD to ~6 million, 10 %, by 300 AD at ~40 %/decade)
SHARE_SPAN = math.log((1.0 - SHARE_SEED) / SHARE_SEED)  # (so a link's mean wait, 1/rate, carries a share from SHARE_SEED to half: TAU_MISSION's own reading of Stark)
SHARE_PLATEAU = 0.10  # sourced: before a culture tips, a pressing faith's converts level off at ~10 % (Bulliet's Umayyad-period plateau, ~10 % of non-Arab subjects, before the Abbasid take-off); the event is the take-off. (The conversion event is memoryless: a share that kept climbing to half while the event had not come would contradict it)
ASSIM_RULE = 0.1  # JUDGEMENT on the sourced rulers' scale: a culture's own faith presses its minorities as an ethnic ruler of it would (ETHNIC_RULE x a ruler's push at the culture's own tolerance): ~2.5 kyr at tolerance 0.5, ~0.5 kyr intolerant, ~15 kyr at 0.9, so a remnant fades over a millennium or two unless the culture is tolerant (the dhimmi Christians of Egypt and Syria stayed large for centuries) or something keeps pressing it
SHARE_MIN = 0.005  # a minority under half a percent is folded into the culture's faith (too few to name)
SHARE_TOP = 4  # the faiths a culture or a state lists by name; the rest are pooled as "others"
# A faith's appeal (PW-1520): a neighbour's pull (contact or missionaries; a ruler's push is force and is not asked) is x appeal(): its organisation
# x its fit to the taker's life. No new tuned number: the reference is the top faith tier, the contest is even.
ORG_REF = TIERS[0][1]  # (0.9, the moralizing high god: the organisation the sourced rates TAU_MISSION (Stark's church) are for)
FIT_W = 0.5  # JUDGEMENT: a better- or worse-fitting god moves the pull by up to half either way, never to nothing: a faith is its church and its promise as much as its god's domain (an even contest of fits is 1)
APPEAL_ORG, APPEAL_FIT = True, True  # (switches, for the lane's before/after measures and the tests)
RULE_TIERS = ("state", "empire", "dragon realm")  # JUDGEMENT: a chiefdom (a town and its cell) pushes no faith; dragons are sapient and rule as any
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


def _settled_fit(w: np.ndarray, sal: np.ndarray) -> float:
    """A being's fit to a land once it has settled there (PW-1520): _drift's end point, each group's weight moved onto that group's
    salient domains (a sea god taken inland becomes a rain god), dotted with the salience. A foreign god fits as well as its groups
    do: a sky god serves under any sky, a sea god only where there is water."""
    f = 0.0
    for idx in GROUP_IDX.values():
        s = sal[idx]
        if s.sum() > 1e-6:
            f += float(w[idx].sum()) * float(s @ s) / float(s.sum())
    return f


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
    __slots__ = ("id", "origin", "founded", "parent", "how", "core", "ended", "end", "members", "track", "changes", "events", "name", "authored", "spreads",
                 "missionary", "decided")

    def __init__(self, id_, origin, founded, how, core, parent=None):
        self.id, self.origin, self.founded, self.how, self.core, self.parent = id_, origin, founded, how, core, parent
        self.ended, self.end = None, None
        self.members: set = set()
        self.track: list = []
        self.changes: list = []
        self.events: list = []
        self.name, self.authored, self.spreads = None, None, True
        self.missionary, self.decided = False, False  # (PW-1477: it seeks converts; decided: its one draw is made)


class Pantheons:
    """The beings of every culture, followed frame by frame, oldest first. No I/O: feed it frames."""

    def __init__(self, mode: str = MODE_DEFAULT, seed: int = 0, lines: dict | None = None):
        from .attitudes import Attitudes
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
        self.counts = {"founded": 0, "schisms": 0, "conversions": 0, "core_changes": 0, "authored": 0, "by_contact": 0, "by_missionaries": 0, "by_rulers": 0}
        self.closed: set = set()  # faiths that take no converts (authored, "stays closed")
        self.seed = int(seed)
        self.held: dict = {}  # culture -> the individuation of the leading god of the church that converted it (PW-1477)
        self.held_f: dict = {}  # culture -> the faith it was converted to (held counts only while it keeps that faith)
        self.att = Attitudes(lines, seed)  # (PW-904: each culture's tolerance and aggression; a ruler's tolerance sets its push)
        self.comp: dict[int, dict] = {}  # culture -> {faith: share}, the shares summing to 1, its faith (faith_of) at least half (PW-1489)
        self.cells: dict[int, int] = {}  # culture -> its cells at the last frame (weights a merge's shares)
        self.sal: dict[int, np.ndarray] = {}  # culture -> its salience at the last frame (a faith's fit to its life, appeal(); PW-1520)
        self.share_counts = {"merge_capped": 0}

    # ---- minority faiths (PW-1489)
    def _comp_major(self, c: int, f: int | None, old: int | None, how: str):
        """c's shares when its faith goes from old to f. "flip" (a conversion): f passes half (Bulliet's midpoint) and the old faith
        stays as a minority; "rename" (founding, schism, a written faith, a merge or split taking a faith): the old faith's share becomes
        f's (the culture moves as a body; its minorities stay)."""
        if f is None:
            self.comp.pop(c, None)
            return
        s = self.comp.get(c)
        if not s or old is None:
            self.comp[c] = {f: 1.0}
            return
        if how == "rename":
            s[f] = s.get(f, 0.0) + s.pop(old, 0.0)
            return
        self._set_share(c, f, max(s.get(f, 0.0), 0.5))

    def _set_share(self, c: int, f: int, v: float):
        """c's share of f to v, the other faiths scaled to fill the rest."""
        s = self.comp[c]
        rest = 1.0 - s.get(f, 0.0)
        k = (1.0 - v) / rest if rest > 1e-12 else 0.0
        for g in s:
            s[g] *= k
        s[f] = v
        maj = self.faith_of.get(c)
        for g in [g for g, x in s.items() if x < SHARE_MIN and g != maj and g != f]:
            s[maj if maj is not None else f] += s.pop(g)

    def _pulls(self, contacts, rule) -> dict:
        """The pull of a culture's own faith on its minorities: {culture: rate per kyr}, from the culture itself (ASSIM_RULE), each neighbour of the same faith (as a
        link: x the share of its border facing it and its receptiveness, over TAU_MISSION or TAU_CONVERT) and its ruler of that faith
        (as _links). Only cultures that hold minorities."""
        mixed = {c for c, s in self.comp.items() if len(s) > 1 and c in self.faith_of}
        out: dict = {}
        if not mixed:
            return out
        guard: dict = {}  # (PW-1520: a ruler more tolerant than its subject shields the subject's minorities, over the share of its land it rules)
        for r, subs, _took in rule or ():
            for x, share in subs:
                if x in mixed and x != r and share > 0:
                    guard[x] = max(guard.get(x, 0.0), share * max(0.0, self.att.religious(r) - self.att.religious(x)))
        for x in mixed:  # (its own faith, as an ethnic ruler of it: ASSIM_RULE; under a more tolerant ruler, at the ruler's tolerance where it rules)
            tol = min(1.0, self.att.religious(x) + guard.get(x, 0.0))
            out[x] = ASSIM_RULE / (TAU_FORCED ** (1.0 - tol) * TAU_TOLERANT ** tol)
        wts = contacts if isinstance(contacts, dict) else None
        for a, b in contacts or ():
            if a not in mixed and b not in mixed:
                continue
            wab = wts[(a, b)] if wts is not None else (1.0, 1.0)
            for x, y, w in ((a, b, wab[0]), (b, a, wab[1])):
                f = self.faith_of.get(x)
                if x in mixed and w > 0 and f is not None and self.faith_of.get(y) == f and f not in self.closed:
                    tau = TAU_MISSION if self.faiths[f].missionary else TAU_CONVERT
                    out[x] = out.get(x, 0.0) + w * self.att.religious(x) / RECEPT_MID / tau
        for r, subs, _took in rule or ():
            fr = self.faith_of.get(r)
            if fr is None or fr in self.closed:
                continue
            tol = self.att.religious(r)
            rate = (1.0 if self.faiths[fr].missionary else ETHNIC_RULE) / (TAU_FORCED ** (1.0 - tol) * TAU_TOLERANT ** tol)
            for x, share in subs:
                if x in mixed and x != r and share > 0 and self.faith_of.get(x) == fr:
                    out[x] = out.get(x, 0.0) + rate * share
        return out

    def _shares(self, links: list, pulls: dict, dt: float):
        """Advance the shares by dt kyr under the links (_links: a faith that may convert a culture) and the pulls (_pulls): each pressed
        faith's share follows a logistic at rate x SHARE_SPAN, from at least SHARE_SEED: the culture's own faith toward all, a faith
        pressing it toward SHARE_PLATEAU (it passes that only by a conversion event, which takes it to half), and never so far that the
        culture's faith would fall under half. A share already over the plateau (an old faith's remnant) is not pressed further."""
        if dt <= 0:
            return
        k: dict = {}
        for r, x, f, _y, _how in links:
            if x in self.comp:
                k[(x, f)] = k.get((x, f), 0.0) + r
        for x, r in pulls.items():
            k[(x, self.faith_of[x])] = k.get((x, self.faith_of[x]), 0.0) + r
        for (x, f), r in sorted(k.items()):
            s, maj = self.comp[x], self.faith_of.get(x)
            v0 = max(s.get(f, 0.0), SHARE_SEED if f != maj else 0.0)
            cap = 1.0 if f == maj else SHARE_PLATEAU
            if v0 >= cap - 1e-12:
                if v0 > s.get(f, 0.0):
                    self._set_share(x, f, v0)
                continue
            v = cap / (1.0 + (cap - v0) / v0 * math.exp(-min(r * SHARE_SPAN * dt, 700.0)))  # (the logistic to cap: to the plateau, or to all)
            if f != maj:
                room = s.get(f, 0.0) + s.get(maj, 0.0) - 0.5  # (its own share, plus what the culture's faith holds over half)
                v = min(v, max(room, s.get(f, 0.0)))
            if v >= 1.0 - SHARE_MIN:
                v = 1.0
            self._set_share(x, f, v)

    def shares_doc(self, c: int) -> list:
        """c's faiths now, [[faith, share], ...]: its own faith first, then the largest SHARE_TOP - 1, then [None, the rest pooled]."""
        s = self.comp.get(c)
        if not s:
            return []
        maj = self.faith_of.get(c)
        rows = sorted(((f, v) for f, v in s.items() if v >= SHARE_MIN or f == maj), key=lambda kv: (kv[0] != maj, -kv[1], kv[0]))
        out = [[f, round(v, 4)] for f, v in rows[:SHARE_TOP]]
        rest = sum(v for _, v in rows[SHARE_TOP:])
        return out + ([[None, round(rest, 4)]] if rest > 0 else [])

    # ---- faiths (PW-1358)
    def _join(self, c: int, f: int | None, ago: float, how: str = "rename"):
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
        self._comp_major(c, f, old, how)
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

    def _decide_missions(self):
        """A faith whose leading god has become a moralizing high god (MISSION_IND) seeks converts with MISSION_P's chance: one seeded
        draw per faith, independent of every other draw (PW-1477). Faiths you write say so themselves."""
        for c, f in self.faith_of.items():
            F = self.faiths[f]
            if F.decided:
                continue
            L = self.lead(c)
            if L is not None and L.ind >= MISSION_IND:
                F.decided = True
                F.missionary = bool(np.random.default_rng((self.seed, 1477, F.id)).random() < MISSION_P)
                if F.missionary:
                    self._ev(self.prev, "missionary", f"faith {F.id} began to seek converts", faith=F.id)

    def _links(self, contacts, rule, t: float | None = None) -> list:
        """Every way a culture may take another faith now: [(rate per kyr, culture, faith, source culture, how)]. Neighbours (contacts)
        of an ordinary faith convert only from an organised one (CONVERT_MIN) at least CONVERT_GAP more individuated, over TAU_CONVERT;
        of a missionary faith, a culture of a faith that is not missionary and at least MISSION_GAP less individuated, over
        TAU_MISSION (the gap is over the culture's own leading god, or over the church that converted it, `held`); a ruler (rule:
        [(ruler culture, subject cultures, took)]) pushes its faith on its subjects over its tolerance's tau. Each is x the taker's
        receptiveness (its religious tolerance / RECEPT_MID) and, for a neighbour, x its faith's appeal() but the ruler's push, which is not asked; a neighbour's pull is x the share of the
        taker's border that faces it (touch(); contacts given as a plain set face fully), a ruler's push x the share of the subject
        culture's land it rules. A faith pulls only from its founding on (t: the time now, kyr ago)."""
        out = []
        wts = contacts if isinstance(contacts, dict) else None
        for a, b in sorted(contacts or ()):
            wab = wts[(a, b)] if wts is not None else (1.0, 1.0)
            for x, y, w in ((a, b, wab[0]), (b, a, wab[1])):
                fx, fy = self.faith_of.get(x), self.faith_of.get(y)
                if w <= 0 or fx is None or fy is None or fx == fy or fy in self.closed:
                    continue
                if t is not None and min(self.faiths[fy].founded, self.faiths[fx].founded) < t - 1e-9:  # (neither faith founded later)
                    continue
                lx, ly = self.lead(x), self.lead(y)
                if lx is None or ly is None:
                    continue
                gap = ly.ind - max(lx.ind, self.held.get(x, 0.0) if self.faith_of.get(x) == self.held_f.get(x) else 0.0)
                if self.faiths[fy].missionary and not self.faiths[fx].missionary:
                    if ly.ind < MISSION_MIN or gap < MISSION_GAP:
                        continue
                    out.append((w * self.att.religious(x) / RECEPT_MID * self.appeal(x, lx, ly) / TAU_MISSION, x, fy, y, "missionaries"))
                elif ly.ind >= CONVERT_MIN and gap >= CONVERT_GAP:
                    out.append((w * self.att.religious(x) / RECEPT_MID * self.appeal(x, lx, ly) / TAU_CONVERT, x, fy, y, "contact"))
        for r, subs, _took in rule or ():
            fr = self.faith_of.get(r)
            if fr is None or fr in self.closed or self.lead(r) is None:
                continue
            if t is not None and self.faiths[fr].founded < t - 1e-9:
                continue
            tol = self.att.religious(r)
            rate = (1.0 if self.faiths[fr].missionary else ETHNIC_RULE) / (TAU_FORCED ** (1.0 - tol) * TAU_TOLERANT ** tol)
            for x, share in subs:
                fx = self.faith_of.get(x)
                if x != r and share > 0 and fx not in (None, fr) and self.lead(x) is not None and (t is None or self.faiths[fx].founded >= t - 1e-9):
                    out.append((rate * share, x, fr, r, "rulers"))
        return out

    def appeal(self, x: int, lx: Being, ly: Being) -> float:
        """How strongly a neighbour's faith draws culture x (PW-1520), its own qualities as a faith: its organisation (the individuation
        of its leading god over ORG_REF: the sourced spread rates are a church's with a moralizing high god, a faith with only temples or
        keepers of the rites wins converts more slowly) x its fit to x's land and life (its leading god's settled fit to x's salience, _settled_fit,
        against x's own leading god's: 1 -/+ FIT_W, 1 when they fit alike). Missionary effort is the link's own pace (TAU_MISSION against
        TAU_CONVERT). A ruler's push is not asked: it is force, at the sourced rates."""
        org = min(1.0, ly.ind / ORG_REF) if APPEAL_ORG else 1.0
        sal = self.sal.get(x)
        if sal is None or not APPEAL_FIT:
            return org
        fy, fx = _settled_fit(ly.w, sal), _settled_fit(lx.w, sal)
        return org * (1.0 + FIT_W * (fy - fx) / (fy + fx) if fy + fx > 1e-12 else 1.0)

    def _convert(self, x: int, f: int, y: int, how: str, ago: float):
        lx, ly = self.lead(x), self.lead(y)
        old = self.faith_of[x]
        self._join(x, f, ago, "flip")
        self.converted.add(x)
        nb = self._new(ly.w.copy(), ago, x, "converted", ly.id)
        nb.dev = min(1.0, max(o.dev for o in self.by[x]) + 0.01)
        nb.ind = lx.ind
        self.held[x], self.held_f[x] = ly.ind, f  # (PW-1477: the church that converted it holds it: a faith no better organised than that one cannot take it back)
        self.off.pop(x, None)
        self.counts["conversions"] += 1
        self.counts["by_" + how] += 1
        tol = round(self.att.religious(y), 3) if how == "rulers" else None
        self.faiths[f].events.append([round(float(ago), 3), "converted", x, old, how])
        word = {"contact": "from", "missionaries": "from the missionaries of", "rulers": "under its rulers,"}[how]
        self._ev(ago, "conversion", f"culture {x} took faith {f} {word} culture {y}", culture=x, faith=f, faith_was=old, by=y, how=how,
                 **({"ruler_tolerance": tol} if tol is not None else {}))
        self._check_end(old, ago, "no followers left")

    def _conversions(self, ago: float, dt: float, contacts, rule_steps=(), step_kyr: float = 0.1):
        """The conversions between the last frame and this one, as events in continuous time (each link a hazard: the waiting time
        to the next conversion is exponential in the sum of the rates, and the links are worked out again after each one), so the
        rates hold whatever the frames' spacing. rule_steps: [(ago, rule)] of the polity steps in this interval; a step's rule holds
        for the century before its date."""
        if dt <= 0:
            return
        hi0 = ago + dt
        cuts = {hi0, ago}
        for s, _ in rule_steps:
            cuts.update(x for x in (s, s + step_kyr) if ago < x < hi0)
        pts = sorted(cuts, reverse=True)
        for hi, lo in zip(pts[:-1], pts[1:]):
            mid = 0.5 * (hi + lo)
            rule = next((r for s, r in rule_steps if s - 1e-9 <= mid <= s + step_kyr + 1e-9), None)
            t = hi
            while True:
                L = self._links(contacts, rule, t)
                pulls = self._pulls(contacts, rule)  # (PW-1489: the shares move with the same links between the events)
                if not L:
                    self._shares(L, pulls, t - lo)
                    break
                rates = np.array([l[0] for l in L])
                R = float(rates.sum())
                if R <= 0:
                    self._shares(L, pulls, t - lo)
                    break
                tn = t - float(self.rng.exponential(1.0 / R))
                self._shares(L, pulls, t - max(tn, lo))
                t = tn
                if t <= lo:
                    break
                k = int(np.searchsorted(np.cumsum(rates), self.rng.random() * R, side="right"))
                _, x, f, y, how = L[min(k, len(L) - 1)]
                self._convert(x, f, y, how, t)

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
        F.missionary, F.decided = F.spreads and bool(spec.get("missionary", F.spreads)), True  # (PW-1477: you say whether it seeks converts)
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
            self.comp[child] = dict(self.comp.get(parent) or {self.faith_of[parent]: 1.0})  # (its minorities too, PW-1489)
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
            self.comp[keep] = dict(self.comp.get(lose) or {self.faith_of[lose]: 1.0})
        elif keep in self.comp and lose in self.comp:  # (PW-1489: the merged culture holds both's shares, weighted by their land)
            wk, wl = float(self.cells.get(keep, 1)), float(self.cells.get(lose, 1))
            mix: dict = {}
            for c, w in ((keep, wk), (lose, wl)):
                for f, v in self.comp[c].items():
                    mix[f] = mix.get(f, 0.0) + v * w / (wk + wl)
            self.comp[keep] = mix
            maj = self.faith_of[keep]
            if mix.get(maj, 0.0) < 0.5:  # (the survivor's faith stays the merged culture's, as it always did: it keeps half)
                self.share_counts["merge_capped"] += 1
                self._set_share(keep, maj, 0.5)
            self.cells[keep] = int(wk + wl)
        self._leave(lose, ago, "its cultures ended")

    def died(self, c: int, ago: float):
        for b in list(self.by.get(c, [])):
            self._end(b, ago, "culture died out")
        self.by.pop(c, None)
        self._leave(c, ago, "its cultures ended")

    def frame(self, ago: float, cultures: dict[int, dict], contacts=None, where: dict | None = None, found=None, rule_steps=(), step_kyr: float = 0.1,
              urban: dict | None = None):
        """One frame. cultures: culture id -> {"sal": salience array, "know": set of techs, "place": str} for each culture with cells
        and a people that has spirit_ritual (the rest have no gods yet). contacts: pairs of cultures in touch this frame (faith spread);
        where: culture -> (cells, sum of their unit vectors) (the faiths' track). found: [(culture, authored spec)] founded this frame
        (after the cultures' own gods are tended; each spec's "faith" is set to its new faith's id). rule_steps: [(ago, [(ruler culture,
        subject cultures, took land by war)])] of the polity steps since the last frame (rule_table; PW-1477: rulers push their faith).
        urban: culture -> share of its people in towns and cities (urban_reader; PW-1520: raises its tolerances)."""
        dt = 0.0 if self.prev is None else max(self.prev - ago, 0.0)
        self.prev = ago
        for c, (n, _v) in (where or {}).items():
            self.cells[c] = int(n)
        for c, u in cultures.items():  # (attitudes, PW-904: every culture on the map with gods; a daughter starts from its parent)
            self.att.ensure(c, u.get("people", "?"), u.get("parent"))
        for _, rule in rule_steps:
            for r, subs, took in rule:
                self.att.ruled(r, len(subs))
                if took:
                    self.att.won(r)
                for x, _ in subs:
                    self.att.subject(x)
        for c, u in cultures.items():
            sal, bs = u["sal"], self.by.setdefault(c, [])
            self.sal[c] = sal
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
        n_in = {}
        for a, b in contacts or ():
            n_in[a] = n_in.get(a, 0) + 1
            n_in[b] = n_in.get(b, 0) + 1
        self.att.step(ago, dt, {c: u.get("people", "?") for c, u in cultures.items()}, n_in,
                      {c for c, f in self.faith_of.items() if self.faiths[f].missionary}, urban or {})
        if dt > 0:
            self._schisms(ago, dt)
            self._decide_missions()
            self._conversions(ago, dt, contacts, rule_steps, step_kyr)
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


def urban_reader(run_dir: Path, m: dict, n_cells: int):
    """The share of each culture's people living in towns and cities (PW-1520), from the settlement ledger (settlements.json: a site counts
    once it reaches its holder's town size, as trade._urban reads it) over the people on its cells (meta.eraq density x cell area).
    Returns urban(j, ago, cell, cul, nC) -> {culture: share} for a run frame j inside the land-use window, {} outside it; None when the
    run has no ledger or no land-use window (the cultures then count as rural)."""
    from .landuse import PEOPLE_SCALE
    from .settlements import pop_at
    eq, sm = m.get("eraq"), m.get("settlements")
    if not eq or not sm or "dens" not in (eq.get("layers") or {}) or not (Path(run_dir) / sm["file"]).exists():
        return None
    doc = json.loads((Path(run_dir) / sm["file"]).read_text())
    town = doc["tiers"]["town_min_by_stage"][-1]
    lo = min(doc["tiers"]["town_min_by_stage"])
    sites = [s for s in doc["sites"] if s.get("kind") not in ("mine", "pit") and s.get("peak_pop", 0) >= lo]
    lay = eq["layers"]["dens"]
    dens_all = np.fromfile(Path(run_dir) / lay["file"], np.uint8).reshape(lay["shape"])
    at = {j: i for i, j in enumerate(eq["frames"])}
    area = 4.0 * np.pi * R_KM ** 2 / n_cells

    def urban(j: int, ago: float, cell: np.ndarray, cul: np.ndarray, nC: int) -> dict:
        if j not in at or not len(cell):
            return {}
        heads = (np.exp2(dens_all[at[j]].astype(float) * PEOPLE_SCALE) - 1.0) * area
        pop = np.zeros(n_cells)
        for s in sites:
            t = town
            for a, tm, _ in s.get("bands") or []:
                if a >= ago - 1e-6:
                    t = tm
            p = pop_at(s, ago)
            if p >= t:
                pop[s["cell"]] += p
        w = 1.0 / np.bincount(cell, minlength=n_cells)[cell]  # (a cell two cultures share: each takes half its people and its towns)
        den = np.bincount(cul, weights=w * heads[cell], minlength=nC)
        num = np.bincount(cul, weights=w * pop[cell], minlength=nC)
        return {int(c): round(float(min(1.0, num[c] / den[c])), 4) for c in np.flatnonzero(den > 0)}
    return urban


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
    urban = urban_reader(run_dir, m, g.n)
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
            cur[c] = {"sal": sal, "know": kn, "people": u["people"], "parent": u.get("parent")}
        uv = np.stack([np.bincount(cul, weights=U[cell, k], minlength=nC) for k in range(3)], 1) if cur else None
        frames.append({"j": j, "ago": ago, "ends": ends, "first": first, "cur": cur, "contacts": touch(g.n, cell, cul, src, dst, nC),
                       "where": {c: (int(n[c]), uv[c]) for c in cur} if cur else None, "present": {c: int(n[c]) for c in present},
                       "cell": cell.astype(np.int32), "cul": cul.astype(np.int32),
                       "urban": urban(j, ago, cell, cul, nC) if urban is not None else {}})
    return {"C": C, "res": res, "known": known, "win": win, "seed": int(m.get("seed") or 0), "frames": frames, "after": endev[ei:],
            "U": U, "lines": {k: v.get("name", k) for k, v in lines.items()},
            "temperament": {k: {"traits": v.get("traits") or [], "demography": v.get("demography") or {}, "way": v.get("way")} for k, v in lines.items()},
            "secs": round(time.time() - t0, 1)}


def derive(run_dir: Path, mode: str = MODE_DEFAULT, techtree: dict | None = None, authored: list | None = None, rule: dict | None = None) -> dict:
    """gods.json of a stored peoples run that has cultures (read-only). techtree: a fresh techtree.build to use instead of the run's
    stored one (a run made before the faith nodes lacks them: gods_mode and the faith techs are read from it). authored: the faiths
    written in (PW-1430); None reads the run's authored.json. rule: rule_table() of its polities; None derives them (polities.py,
    with the invasions you scheduled) when the run has settlements, else no rulers."""
    A = read_authored(run_dir)
    if authored is None:
        authored = A["faiths"]
    inp = inputs(run_dir, techtree)
    if rule is None and (Path(run_dir) / "settlements.json").exists():
        from . import polities as PO
        rule = rule_table(PO.derive(Path(run_dir), invasions=A["invasions"]), inp["C"], inp["frames"])
    return replay(inp, mode, authored, rule)


def rule_table(po: dict, C: list, frames: list | None = None) -> dict:
    """Who rules whom at each polity step (PW-1477), from a polities doc (polities.derive): {"step_kyr", "steps": [[ago, [[ruler
    culture, [[subject culture, share of its land the polity holds], ...], took land by war this step], ...]], ...]}, oldest first,
    for the states, empires and dragon realms (RULE_TIERS) that have a ruling culture. Cultures are cultures.json ids, followed
    through their merges to that time. frames: inputs()["frames"], for the shares (each step reads the frame nearest it); without
    them every share is 1."""
    from .polities import _unpack
    by_uid = {c["uid"]: c["id"] for c in C if c.get("uid")}
    fagos = np.array([f["ago"] for f in frames]) if frames else None
    tot_at: dict = {}
    res = _resolver({"cultures": C})
    tiers = po.get("tiers") or ["chiefdom", "state", "empire", "dragon realm"]
    rec = po["polities"]
    took = {(pid, round(float(a), 3)) for r in rec for pid in (r["id"],) for a, *_ in r.get("took") or ()}
    steps, now = [], []
    last = min((float(st["ago"]) for st in po["steps"]), default=None)
    for st, mp in zip(po["steps"], po["maps"]):
        ago = float(st["ago"])
        rows = []
        for e in mp:
            pid, tier, subj = e[0], tiers[e[1]], e[3]
            if tier not in RULE_TIERS:
                continue
            rs = [u for a, u in rec[pid]["rulers"] if a >= ago - 1e-9]
            if not rs or rs[-1] not in by_uid:
                continue
            r = res(by_uid[rs[-1]], ago)
            subs = sorted({res(by_uid[u], ago) for u in subj if u in by_uid} - {r})
            if not subs:
                continue
            if fagos is not None:
                fi = int(np.argmin(np.abs(fagos - ago)))
                F = frames[fi]
                if fi not in tot_at:
                    tot_at[fi] = np.bincount(F["cul"], minlength=len(C))
                cells = np.asarray(_unpack(e[2]), np.int64)
                inside = np.isin(F["cell"], cells)
                here = np.bincount(F["cul"][inside], minlength=len(C))
                tot = tot_at[fi]
                subs = [[x, round(float(min(1.0, here[x] / tot[x])), 4) if tot[x] else 0.0] for x in subs]
                if ago == last:  # (PW-1489: who lives in each state now, for its faiths)
                    held = {int(x): int(here[x]) for x in np.flatnonzero(here)}
                    now.append({"id": pid, "name": rec[pid].get("name") or f"polity {pid}", "tier": tier, "color": rec[pid].get("color"),
                                "ruler": r, "cells": held})
            else:
                subs = [[x, 1.0] for x in subs]
            rows.append([r, subs, (pid, round(ago, 3)) in took])
        steps.append([ago, rows])
    steps.sort(key=lambda x: -x[0])
    return {"step_kyr": float(po.get("step_kyr") or 0.1), "steps": steps, "now": now}


def replay(inp: dict, mode: str = MODE_DEFAULT, authored: list | None = None, rule: dict | None = None) -> dict:
    """The gods and faiths from inputs(): the Pantheons fed frame by frame, the authored faiths founded when their founders are there.
    rule: rule_table() (rulers push their faith on their subjects, PW-1477); None: no rulers."""
    t0 = time.time()
    C, res, known, win = inp["C"], inp["res"], inp["known"], inp["win"]
    place = {c["id"]: c.get("place") for c in C}
    P = Pantheons(mode, inp["seed"], inp.get("temperament"))
    rsteps = (rule or {}).get("steps") or []
    step_kyr = float((rule or {}).get("step_kyr") or 0.1)
    ri = 0
    prev_ago = None
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
        here = []
        while ri < len(rsteps) and rsteps[ri][0] >= ago - 1e-9:  # (the polity steps since the last frame; earlier ones are skipped)
            if prev_ago is not None and rsteps[ri][0] < prev_ago - 1e-9:
                here.append((rsteps[ri][0], [(r, subs, tk) for r, subs, tk in rsteps[ri][1]]))
            ri += 1
        prev_ago = ago
        P.frame(ago, fr["cur"], fr["contacts"], fr["where"], found, here, step_kyr, fr.get("urban"))
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
    out = {"format": GODS_FORMAT, "gods_mode": mode, "from_kyr": win, "domains": list(DOMAINS), "groups": {k: list(v) for k, v in GROUPS.items()},
           "constants": {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float))} | {"tiers": dict(TIERS)},
           "beings": docs, "events": P.events, "faiths": {"rule": FAITH_RULE, "list": faiths},
           "frames": [[fr["j"], round(float(fr["ago"]), 3)] for fr in frames],
           "cultures": {str(c): {"name": C[c]["name"], "people": C[c]["people"], "beings": ids,
                                 "living": [i for i in ids if docs[i]["status"] == "living"],
                                 "faiths": P.fhist.get(c, []), "faith_now": P.faith_of.get(c), "shares": P.shares_doc(c),
                                 "ritual_since_kyr": (known.get(C[c]["people"]) or {}).get("spirit_ritual", [None])[0]} for c, ids in cl.items()},
           "shares": share_rollup(P, C, (rule or {}).get("now") or []),
           "authored": {"rule": AUTHORED_RULE, "faiths": [authored_readout(s, faiths, C) for s in todo], "problems": notes},
           "attitudes": P.att.doc() | {"rulers_known": bool(rsteps)},
           "summary": summary(docs, mode, round(inp.get("secs", 0.0) + time.time() - t0, 1)) | {"faiths": {**P.counts, "ever": len(faiths),
                                                                                                     "living": sum(f["ended_kyr"] is None for f in faiths)}}}
    return out


SHARE_RULE = ("Each culture holds a share of each faith. Its faith (the one named everywhere else) is its majority: a culture is converted "
              "when a newcomer faith passes half (Bulliet's conversion curve), and the old faith stays on as a minority. Between conversions "
              "a faith grows within a culture along an S-curve, from its first converts (1 %) to about a tenth (Bulliet's plateau before the "
              "take-off), at the pace of the neighbour, missionaries or ruler pressing it; once a culture holds a faith, the culture itself (faster the less tolerant it is) and its neighbours and rulers of that faith "
              "win over the minorities that remain, over a millennium or two; a ruler more tolerant of other faiths than its subjects shields their minorities (the protected faiths of the caliphates). Daughter cultures carry their parent's minorities; merged cultures pool "
              "theirs by land (the survivor's faith keeps at least half). States and peoples: their cultures' shares weighted by land.")


def _mix(parts) -> list:
    """[(weight, {faith: share})] pooled: [[faith, share], ...] largest first, the first SHARE_TOP, then [None, the rest]."""
    tot: dict = {}
    W = sum(w for w, _ in parts)
    if W <= 0:
        return []
    for w, s in parts:
        for f, v in s.items():
            tot[f] = tot.get(f, 0.0) + v * w / W
    rows = sorted(tot.items(), key=lambda kv: (-kv[1], kv[0]))
    rest = sum(v for _, v in rows[SHARE_TOP:])
    return [[f, round(v, 4)] for f, v in rows[:SHARE_TOP]] + ([[None, round(rest, 4)]] if rest > 1e-4 else [])


def share_rollup(P: Pantheons, C: list, now: list) -> dict:
    """The faiths of each state (rule_table()["now"]: its cells by culture) and each people (its living cultures by their cells at the
    last frame), from the cultures' shares (PW-1489)."""
    states = []
    for e in now:
        parts = [(n, P.comp[c]) for c, n in e["cells"].items() if c in P.comp]
        if parts:
            states.append({"id": e["id"], "name": e["name"], "tier": e["tier"], "color": e["color"], "ruler": e["ruler"],
                           "cells": int(sum(n for n, _ in parts)), "faiths": _mix(parts)})
    states.sort(key=lambda x: -x["cells"])
    by: dict = {}
    for c, s in P.comp.items():
        by.setdefault(C[c]["people"], []).append((P.cells.get(c, 1), s))
    mixed = [s for s in P.comp.values() if len(s) > 1]
    return {"rule": SHARE_RULE, "states": states, "peoples": {p: _mix(v) for p, v in sorted(by.items())},
            "summary": {"cultures": len(P.comp), "with_minority": len(mixed),
                        "minority_over_10": sum(1 for c, s in P.comp.items() if any(v > 0.10 for f, v in s.items() if f != P.faith_of.get(c))), **P.share_counts}}


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
                 "named gods lead, its old faith may end. After that it lives under the same rules as every faith: its gods drift toward the land, may fade, are copied into daughter cultures and fuse at merges. "
                 f"If it is missionary it wins neighbours whose faith is not missionary and no more organised (from {MISSION_MIN:g} individuation, about "
                 f"{TAU_MISSION * 1000:g} years a link); if it only spreads, like any faith, from temples ({CONVERT_MIN:g}) over about {TAU_CONVERT:g} kyr; "
                 "and its cultures' rulers push it on their subjects.")


def clean_authored(faiths, n_cultures: int, peoples: set, strict: bool = True) -> tuple[list, list]:
    """Authored faiths in a checked form: [{id, name, culture, people, place, ago_kyr, year_text, gods: [{name, domains}], spreads,
    missionary}] (missionary, PW-1477: it seeks converts; a faith saved before it was asked is missionary when it spreads).
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
                    "year_text": str(f.get("year_text") or "")[:60], "gods": gods, "spreads": bool(f.get("spreads", True)),
                    "missionary": bool(f.get("spreads", True)) and bool(f.get("missionary", f.get("spreads", True)))})
    return out, notes


def authored_readout(s: dict, faiths: list, C: list) -> dict:
    """One authored faith for the viewer: what was asked, whether it took hold (and why not), and how it has fared."""
    r = {k: s.get(k) for k in ("id", "name", "culture", "people", "place", "ago_kyr", "year_text", "gods", "spreads", "missionary")}
    r |= {"took_hold": bool(s.get("took")), "faith": s.get("faith"), "founded_kyr": s.get("founded_kyr"), "why": s.get("why") if not s.get("took") else None,
          "note": s.get("note"), "founded_in": s.get("culture_now"),
          "founded_in_name": C[s["culture_now"]]["name"] if s.get("culture_now") is not None else None}
    if s.get("took") and s.get("faith") is not None:
        F = faiths[s["faith"]]
        won = sum(e[1] == "converted" for e in F["events"])
        top = max((t[5] for t in F["track"]), default=0.0)
        ways = {}
        for e in F["events"]:
            if e[1] == "converted":
                ways[e[4] if len(e) > 4 else "contact"] = ways.get(e[4] if len(e) > 4 else "contact", 0) + 1
        how = ", ".join(f"{n} {dict(contact='from neighbours', missionaries='by its missionaries', rulers='under its rulers')[k]}" for k, n in sorted(ways.items()))
        if not s["spreads"]:
            spread = "stays closed: it takes no converts"
        elif won:
            spread = f"won {won} culture{'s' if won != 1 else ''} by conversion ({how})"
        elif s.get("missionary", True) and top < MISSION_MIN:
            spread = f"has not spread: its leading god reached {top:.2f} individuation, and missionaries need {MISSION_MIN:g} (burial rites)"
        elif s.get("missionary", True):
            spread = "has not spread: no neighbour of a faith that is not missionary and no more organised took it up yet (a chance per link)"
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
              f"god has turned to another domain than its faith's core for {SCHISM_KYR:g} kyr breaks away as a new faith. A culture takes another "
              "faith in three ways, each a chance in time (the mean wait of one link): from a neighbour whose leading god is at least "
              f"{CONVERT_MIN:g} individuated (temples) and {CONVERT_GAP:g} more than its own (about {TAU_CONVERT:g} kyr); from the missionaries of a "
              f"neighbouring faith that seeks converts, when its own is not missionary and no more organised (about {TAU_MISSION * 1000:g} years); "
              f"or from its rulers, who push their faith on their subjects (a generation, {TAU_FORCED * 1000:g} years, for a ruler with no "
              f"tolerance; {TAU_TOLERANT:g} kyr for a fully tolerant one). The neighbours' pull is faster on a tolerant culture. A faith seeks "
              f"converts when you write it so, or (a {MISSION_P:g} chance, once) when its leading god becomes a moralizing high god. A convert "
              "takes a copy of the converting faith's leading god and does not break away by drift after; a faith with no cultures left ends.")


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


def touch(n_cells: int, cell: np.ndarray, cul: np.ndarray, src: np.ndarray, dst: np.ndarray, nC: int) -> dict:
    """The pairs of contacts() with how much each faces the other (PW-1477): {(a, b): (share of a's border facing b, share of b's
    facing a)}. A culture's border is every grid edge from its cells to a cell it does not hold (another culture's, empty land or the
    sea: the sea is a border no one preaches across); a cell it shares with another culture counts as SHARE_EDGES edges between them."""
    out: dict = {}
    if not len(cell):
        return out
    lab = np.full(n_cells, -1, np.int64)
    lab[cell] = cul
    a, b = lab[src], lab[dst]
    held = np.zeros(n_cells, bool)
    held[cell] = True
    e = (a >= 0) & (a != b)
    border = np.bincount(a[e], minlength=nC).astype(float)
    f = e & (b >= 0)
    pair = a[f] * nC + b[f]
    o = np.lexsort((cul, cell))
    cs, us = cell[o], cul[o]
    same = (cs[1:] == cs[:-1]) & (us[1:] != us[:-1])
    sa, sb = us[:-1][same], us[1:][same]
    pair = np.concatenate([pair, np.repeat(sa * nC + sb, SHARE_EDGES), np.repeat(sb * nC + sa, SHARE_EDGES)])
    border += SHARE_EDGES * (np.bincount(sa, minlength=nC) + np.bincount(sb, minlength=nC))
    k, n = np.unique(pair, return_counts=True)
    cnt = {(int(x // nC), int(x % nC)): int(m) for x, m in zip(k, n)}
    for (x, y), m in cnt.items():
        lo, hi = min(x, y), max(x, y)
        if (lo, hi) in out:
            continue
        wlo = cnt.get((lo, hi), 0) / max(border[lo], 1.0)
        whi = cnt.get((hi, lo), 0) / max(border[hi], 1.0)
        out[(lo, hi)] = (round(min(1.0, wlo), 4), round(min(1.0, whi), 4))
    return out


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
                    "color": faith_color(F.id), "authored": F.authored, "spreads": F.spreads, "missionary": F.missionary,
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
