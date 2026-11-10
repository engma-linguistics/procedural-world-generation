"""Place-naming habits per language family (PW-1658) and the Common's English renderings (PW-1654), language lane 15.

**Habits.** Real families name places differently, and that is much of why their maps sound different. Every proto lect
draws a naming habit from six templates, taken as patterns and never as Earth words (every form comes from the lect's own
words and grammar):
- `suffix` (English-like): a specific then a generic that wears down into an ending (tun > -ton, burh > -bury): enclosure,
  house, field, fort, market; a ford or bridge on a river; a founder in the genitive (Grimsby) or 'X's people' (Hastings,
  -ingas).
- `prefix` (Welsh/Gaelic-like): the generic first: holy enclosure + founder (Llan-), river mouth + the river (Aber-/Inver-),
  head 'hill' (Pen-), fort (Caer-).
- `possessive` (Slavic-like): an enclosure (-grad/-gorod) after an adjective (Novgorod); the founder's name with a
  possessive-adjective suffix and no generic at all (Krakow); 'X's descendants' (Katowice); the river's name made an
  adjective (-sk).
- `construct` (Arabic-like): generic first, then a frozen article and the specific, 'X of the Y' (Jabal Tariq, Ras, Wadi,
  Dar, Bab, Madinat); the generics stay whole and transparent.
- `feature` (Japanese-like): places named for the land: mountain, river, island, cape, field after a plain word, the
  generic's first consonant voiced in the compound (rendaku: -kawa > -gawa).
- `locative` (Bantu-like): a locative class prefix on the root (Swahili pa-/ku-/mu-), the land's class (Buganda) for the
  people's own root.
A head-final proto draws from the first, third and fifth (spec-first), a head-first one from the others (generic-first);
a lect with live noun classes favours `locative`. The proto also draws its own weights over the template's generics and
specifics; each later lect inherits its parent's habit and now and then (HABIT_DRIFT per lect) changes one thing: a generic
falls out of use, a new one comes in from another template's pool, or one grows commoner. So sisters share most of their
generics and a family is recognisable from its map. A generic older than SUFFIX_KYR / the template's wear wears down to
one syllable (an ending, or a prefix like Llan-); the `construct` and `locative` habits keep theirs whole.

**English Common (PW-1654, owner ruling 11-10: on by default).** Every settlement and feature also gets `english`: its
meaning rendered as an English compound, the way Tolkien gives Westron as English (Hobbiton, Bywater) and Imladris as
Rivendell: English's own generics (enclosure > -ton/-worth/-hay, house > -ham/-stead, field > -field/-ley, fort > -bury/
-borough, market > Chipping-/-wick, a founder > Grim's + generic: Grimsby-style). Names are unique per region (a qualifier,
Great / Little / Upper / Nether..., tells two apart) and never read as an English slur (romanize.offensive).

Deterministic: draws come from the caller's names._rng streams. Taste calls are module constants (for the owner)."""
from __future__ import annotations

import unicodedata
import zlib

import numpy as np

from . import grammar as GR
from . import lexicon as LX
from . import romanize as RO

HABIT_DRIFT = 0.12   # chance a lect changes one thing in its parent's habit
SUFFIX_KYR = 3.0     # a generic this old (divided by the template's wear) wears down to one syllable
TEMPLATES = {
    # order: where the generic stands ("spec_first" or "generic_first"); wear: how fast it erodes (0: never)
    "suffix": dict(order="spec_first", wear=1.0, like="English",
                   generics={"FENCE": 1.0, "HOUSE": 0.8, "FIELD": 0.6, "WALL (OF HOUSE)": 0.45, "MARKET": 0.25,
                             "VILLAGE": 0.3},
                   river={"FORD": 1.4, "BRIDGE": 0.5}, hill={"HILL": 0.6}, coast={"MOUTH": 0.4},
                   specific={"founder": 0.35, "people_of": 0.15, "adj": 0.25, "nature": 0.25}),
    "prefix": dict(order="generic_first", wear=0.6, like="Welsh/Gaelic",
                   generics={"TEMPLE": 0.9, "FENCE": 0.4, "WALL (OF HOUSE)": 0.7, "HOUSE": 0.4},
                   river={"MOUTH": 1.6}, hill={"HEAD": 1.2}, coast={"MOUTH": 0.6, "HEAD": 0.5},
                   specific={"founder": 0.4, "river": 0.3, "adj": 0.15, "nature": 0.15}),
    "possessive": dict(order="spec_first", wear=0.5, like="Slavic",
                       generics={"FENCE": 1.0, "TOWN": 0.5, "WALL (OF HOUSE)": 0.3},
                       river={}, hill={"HILL": 0.3}, coast={},
                       specific={"possessive": 0.35, "descendants": 0.25, "adj": 0.25, "river_adj": 0.15}),
    "construct": dict(order="generic_first", wear=0.0, like="Arabic", article=True,
                      generics={"TOWN": 1.0, "HOUSE": 0.6, "DOOR": 0.4, "MARKET": 0.3},
                      river={"VALLEY": 1.0, "RIVER": 0.4}, hill={"MOUNTAIN": 1.4}, coast={"HEAD": 1.0},
                      specific={"founder": 0.35, "abstract": 0.2, "adj": 0.25, "nature": 0.2}),
    "feature": dict(order="spec_first", wear=0.3, like="Japanese", rendaku=True,
                    generics={"FIELD": 0.8, "PLAIN": 0.6, "VALLEY": 0.5, "FOREST": 0.3},
                    river={"RIVER": 1.6}, hill={"MOUNTAIN": 1.6}, coast={"ISLAND": 0.8, "NOSE": 0.8},
                    specific={"adj": 0.4, "nature": 0.5, "founder": 0.1}),
    "locative": dict(order="generic_first", wear=0.0, like="Bantu", locative=True,
                     generics={}, river={}, hill={}, coast={},
                     specific={"founder": 0.3, "nature": 0.3, "river": 0.2, "people": 0.2}),
}
SPEC_FIRST = ("suffix", "possessive", "feature")
GEN_FIRST = ("prefix", "construct", "locative")
CLASS_LOCATIVE = 3.0   # weight of `locative` for a proto with live noun classes (0.4 without)
ADJ = ("NEW", "OLD", "BIG", "SMALL", "WHITE", "RED", "BLACK", "HIGH", "LOW", "GOOD", "LONG", "GREEN", "COLD")
NATURE = ("TREE", "STONE", "WOOD", "SAND", "BIRD", "DEER", "WOLF", "BEAR", "FOX", "SPRING (OF WATER)", "FLOWER", "GRASS",
          "SNOW", "FISH", "SALT (FOOD)", "OX", "HORSE", "CROW", "EAGLE", "THORN", "ASH")
ABSTRACT = ("PEACE", "GOD", "HOLY", "LIGHT (RADIATION)", "SUN", "STAR")
HIGH_TIER = {"WALL (OF HOUSE)": 2.0, "TOWN": 2.0, "MARKET": 1.5}   # a city's generic leans to these

# ------------------------------------------------------------------------------------------------- the English Common
EN_GENERIC = {
    "FENCE": ("ton", "worth", "hay"), "TOWN": ("ton", "borough"), "VILLAGE": ("thorpe", "wick", "by"),
    "HOUSE": ("ham", "stead", "by"), "FIELD": ("field", "ley"), "PLAIN": ("field", "ley"),
    "WALL (OF HOUSE)": ("bury", "borough", "chester"), "MARKET": ("wick", "Chipping "), "FORD": ("ford",),
    "BRIDGE": ("bridge",), "HILL": ("don", "hill"), "HEAD": ("head",), "MOUNTAIN": ("fell", "horn"),
    "MOUTH": ("mouth",), "TEMPLE": ("minster", "kirk"), "DOOR": ("gate",), "VALLEY": ("dale", "combe"),
    "ISLAND": ("ey", "holm"), "NOSE": ("ness",), "RIVER": ("burn", "water"), "WATER": ("water",),
    "FOREST": ("wood", "hurst"), "LAKE": ("mere",), "SEA": (" Sea",), "SPRING (OF WATER)": ("well",),
    "LAND": ("land", "mark"), "EARTH (SOIL)": ("land",), "GROUND": ("land",),
}
EN_PLACE = ("stow", "stead")   # 'place' with no generic word: Krak's place, the place of X
EN_ADJ = {"NEW": "New", "OLD": "Ald", "BIG": "Mickle", "SMALL": "Little", "WHITE": "White", "RED": "Red", "BLACK": "Black",
          "HIGH": "High", "LOW": "Nether", "GOOD": "Fair", "LONG": "Long", "GREEN": "Green", "COLD": "Cold", "WARM": "Warm",
          "SALTY": "Salt", "STONE": "Stone"}
EN_NOUN = {"SPRING (OF WATER)": "Well", "SALT (FOOD)": "Salt", "PEACE": "Frith", "GOD": "Gods", "HOLY": "Holy",
           "LIGHT (RADIATION)": "Light", "WOOD": "Wood", "TREE": "Tree"}
EN_QUALIFIERS = ("Great", "Little", "Upper", "Nether", "East", "West", "North", "South", "Long", "Old", "Market", "Church",
                 "High", "Low", "Bishop's", "King's", "Kirk", "Stony")
_VOWELS = set("aeiouy")
_CLASHING = ({"Great", "Little", "Mickle"}, {"Upper", "Nether", "High", "Low"}, {"Old", "Ald", "New"},
             {"Kirk", "Church", "Minster"}, {"Long", "Short"})


def _w(lect, c):
    from .names import _word
    return _word(lect, c)


def _pick(rng, weights: dict) -> str | None:
    ks = sorted(k for k, v in weights.items() if v > 0)
    if not ks:
        return None
    p = np.array([weights[k] for k in ks], float)
    return ks[int(rng.choice(len(ks), p=p / p.sum()))]


def _h(*key) -> int:
    return zlib.crc32(":".join(map(str, key)).encode())


def anglicize(roman: str, max_letters: int = 7) -> str:
    """A local name as an English reader would take it into a compound: diacritics, apostrophes and odd letters dropped,
    runs of one letter cut to two, clipped after its second vowel group when long (Grimr > Grim), capitalized."""
    d = unicodedata.normalize("NFD", roman or "")
    s = "".join(ch for ch in d if not unicodedata.combining(ch)).lower()
    s = "".join(ch for ch in s if "a" <= ch <= "z")
    for a, b in (("zj", "j"), ("dj", "j"), ("dzh", "j"), ("tsh", "ch"), ("dz", "z")):
        s = s.replace(a, b)
    out = []
    for ch in s:
        if out and out[-1] == ch and ch not in "lse":
            continue   # (doubled letters once: rr > r, uu > u; ll, ss, ee as English writes them)
        if ch == "h" and out and out[-1] not in _VOWELS and out[-1] not in "sctpw":
            continue   # (an h after a consonant is no English digraph: rh > r, kh > k)
        if ch not in _VOWELS and len(out) >= 2 and out[-1] not in _VOWELS and out[-2] not in _VOWELS \
                and not (out[-1] == "h"):
            continue   # (no three consonants in a row)
        out.append(ch)
    s = "".join(out)
    if len(s) > max_letters:
        groups, i, cut = 0, 0, len(s)
        while i < len(s):
            if s[i] in _VOWELS:
                groups += 1
                while i < len(s) and s[i] in _VOWELS:
                    i += 1
                if groups == 2:
                    cut = i + (1 if i < len(s) and s[i] not in _VOWELS else 0)
                    break
                continue
            i += 1
        s = s[:max(3, min(cut, max_letters + 2))]
    return s[:1].upper() + s[1:] if s else ""


def _en_word(c: str) -> str:
    if c in EN_ADJ:
        return EN_ADJ[c]
    if c in EN_NOUN:
        return EN_NOUN[c]
    try:
        g = LX.concept_info(c).gloss
    except Exception:  # noqa: BLE001
        g = c.lower()
    g = g.split(" (")[0].split(" or ")[0].strip()
    return g[:1].upper() + g[1:]


def _fuse(spec: str, gen: str) -> str:
    """'Grims' + 'by' > Grimsby; a prefix generic (Chipping ) stands first; ' Sea' stays apart; a doubled letter at the
    seam is kept once when three would meet."""
    if gen.endswith(" "):
        return gen + spec
    if gen.startswith(" "):
        return spec + gen
    if spec and gen and spec[-1].lower() == gen[0].lower() and (gen[0] == "s" or len(spec) > 1 and
                                                                 spec[-2].lower() == spec[-1].lower()):
        gen = gen[1:]   # (Grims + stead > Grimstead; no three letters alike at the seam)
    return spec + gen


def english(meaning: dict, key) -> tuple[str, str]:
    """(English Common name, how it was made) from a name's meaning: {generic: concept | None, spec: {kind, concept |
    name | english}}; the choice among a generic's English endings is fixed by `key` (a site or feature id)."""
    gen_c = meaning.get("generic")
    sp = meaning.get("spec") or {}
    kind = sp.get("kind")
    opts = EN_GENERIC.get(gen_c or "", ())
    gen = opts[_h("g", key) % len(opts)] if opts else ""
    if kind in ("founder", "possessive", "people_of", "descendants", "people", "river", "river_adj"):
        stem = sp.get("english") or anglicize(sp.get("name") or "")
    elif kind in ("adj", "nature", "abstract"):
        stem = _en_word(sp.get("concept") or "")
    else:
        stem = ""
    if kind in ("founder", "possessive") and stem:
        stem = stem if stem.endswith("s") else stem + "s"
        how = f"{sp.get('name') or stem}'s"
    elif kind in ("people_of", "descendants") and stem:
        how = f"{sp.get('name') or stem}'s people"
        stem = stem + "ing" if kind == "people_of" else stem + "ings"
        if kind == "descendants":
            return stem, f"{how} (Hastings-style)"
    else:
        how = stem.lower() if stem else ""
    if not gen:
        gen = EN_PLACE[_h("p", key) % len(EN_PLACE)]
        what = "place"
    else:
        what = (LX.concept_info(gen_c).gloss.split(" (")[0] if gen_c else "") or "place"
        what = {"wall": "fort", "fence": "enclosure", "head": "headland", "nose": "cape", "temple": "holy enclosure",
                "door": "gate"}.get(what, what)
    if not stem:
        name = gen.strip().capitalize() if not gen.endswith(" ") else gen.strip()
        return name, f"-{gen.strip()} '{what}'"
    name = _fuse(stem, gen)
    return name[:1].upper() + name[1:], f"{how} + -{gen.strip()} '{what}'"


def unique_english(recs: list, region_of) -> None:
    """Make every record's `english` unique within its region (`region_of(rec)`), in place: a later duplicate takes a
    qualifier (Great, Little, Upper, Nether...: Great Newton) and a spelling the guard flags takes another ending or a
    qualifier. Records come in priority order (the first keeps the plain name). One river, lake or site keeps one name
    in every deme on it, chosen free in every region those demes are in."""
    def fid_of(r):
        return (r.get("kind"), r.get("id")) if r.get("id") is not None and r.get("kind") in ("river", "lake") else \
            ("site", r.get("site")) if r.get("site") is not None else None   # (a site two demes hold: one Common name)
    regions: dict = {}   # fid -> every region a record of it is in
    for r in recs:
        if r.get("english") and fid_of(r) is not None:
            regions.setdefault(fid_of(r), set()).add(region_of(r))
    seen: dict = {}
    same: dict = {}   # fid -> the English name it took (and how)
    for r in recs:
        en = r.get("english")
        if not en:
            continue
        fid = fid_of(r)
        if fid is not None and fid in same:
            r["english"], r["english_how"] = same[fid]
            continue
        regs = regions.get(fid) or {region_of(r)}
        takens = [seen.setdefault(g, set()) for g in sorted(regs, key=str)]
        cand = en
        i = 0
        while any(cand.lower() in t for t in takens) or RO.offensive(cand.replace(" ", "")) is not None:
            if i < len(EN_QUALIFIERS):
                q = EN_QUALIFIERS[(_h("q", r.get("site"), r.get("id"), en) + i) % len(EN_QUALIFIERS)]
                i += 1
                if any(q in g and any(en.startswith(x) for x in g) for g in _CLASHING):
                    continue   # (no 'Great Littlecombe')
                cand = f"{q} {en}"
                if RO.offensive(en.replace(" ", "")) is not None:
                    cand = f"{q} {RO.unoffend(en)}"
            else:
                cand = f"{en} {i - len(EN_QUALIFIERS) + 2}"
                i += 1
        if cand != en:
            note = f"'{cand.split(' ')[0]}' added to tell it from another {en}"
            r["english_how"] = f"{r['english_how']}; {note}" if r.get("english_how") else note
        r["english"] = cand
        for t in takens:
            t.add(cand.lower())
        if fid is not None:
            same[fid] = (cand, r.get("english_how"))


# ------------------------------------------------------------------------------------------------------------ habits
class Habits:
    """Naming habits down the lect tree (see the module doc). `P` is names._Pass, `PN` personal.Personal."""

    def __init__(self, P, PN):
        self.P, self.PN = P, PN
        self._h: dict = {}

    def rng(self, *key):
        from .names import _rng
        return _rng(self.P.seed, "habit", *key)

    def _fresh(self, lect, rng) -> dict:
        from .personal import _head_final
        g = getattr(lect, "grammar", None)
        classes = g is not None and getattr(g, "class_system", None) is not None
        pool = SPEC_FIRST if _head_final(lect) else GEN_FIRST
        w = {t: 1.0 for t in pool}
        if "locative" in w:
            w["locative"] = CLASS_LOCATIVE if classes else 0.4
        t = _pick(rng, w)
        T = TEMPLATES[t]
        jit = lambda d: {k: round(float(v * np.exp(rng.normal(0.0, 0.45))), 3) for k, v in sorted(d.items())}  # noqa: E731
        return {"template": t, "origin": lect.id, "generics": jit(T["generics"]), "river": jit(T["river"]),
                "hill": jit(T["hill"]), "coast": jit(T["coast"]), "specific": jit(T["specific"]), "changes": []}

    def _drift(self, h: dict, lect, rng) -> dict:
        h = {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v) for k, v in h.items()}
        r = rng.random()
        slot = ("generics", "river", "hill", "coast")[int(rng.integers(4))]
        d = h[slot]
        if r < 0.35 and len(d) > 1:   # a generic falls out of use
            k = sorted(d)[int(rng.integers(len(d)))]
            d.pop(k)
            what = f"stopped using {k.lower()}"
        elif r < 0.7:                  # a new generic comes in (from another template's pool for that slot)
            pool = sorted({k for T in TEMPLATES.values() for k in T[slot]} - set(d))
            if not pool:
                return h
            k = pool[int(rng.integers(len(pool)))]
            d[k] = round(float(0.5 * np.exp(rng.normal(0.0, 0.3))), 3)
            what = f"took up {k.lower()}"
        else:                          # one grows commoner
            if not d:
                return h
            k = sorted(d)[int(rng.integers(len(d)))]
            d[k] = round(d[k] * 2.0, 3)
            what = f"{k.lower()} commoner"
        h["changes"] = h["changes"] + [[lect.id, what, round(float(lect.born_kyr), 3)]]
        return h

    def habit(self, lect) -> dict:
        if lect.id in self._h:
            return self._h[lect.id]
        h = None
        for x in self.PN.chain(lect):
            if x.id in self._h:
                h = self._h[x.id]
                continue
            rng = self.rng(x.id)
            if h is None:
                h = self._fresh(x, rng)
            elif rng.random() < HABIT_DRIFT:
                h = self._drift(h, x, rng)
            self._h[x.id] = h
        return h

    def summary(self, lect) -> dict:
        h = self.habit(lect)
        top = lambda d, n=4: [k.split(" (")[0].lower() for k, _v in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]  # noqa: E731
        T = TEMPLATES[h["template"]]
        return {"template": h["template"], "like": T["like"], "order": T["order"], "origin": h["origin"],
                "generics": top(h["generics"]), "river": top(h["river"], 2), "hill": top(h["hill"], 2),
                "coast": top(h["coast"], 2), "specific": top(h["specific"], 4), "changes": h["changes"][-3:]}

    # ------------------------------------------------------------------ one name
    def generic(self, lect, site, ctx: dict, rng) -> str | None:
        """The generic concept a lect's habit takes for this site (None: the habit names it without one)."""
        h = self.habit(lect)
        w = dict(h["generics"])
        for slot in ("river", "hill", "coast"):
            if ctx.get(slot):
                for k, v in h[slot].items():
                    w[k] = w.get(k, 0.0) + v
        if site.get("tier_now") == "city":
            w = {k: v * HIGH_TIER.get(k, 1.0) for k, v in w.items()}
        w = {k: v for k, v in w.items() if _w(lect, k) is not None}
        return _pick(rng, w)

    def coin(self, namer, site, ctx: dict, rng, river=None, people_root=None) -> dict | None:
        """A settlement name in `namer` after its habit: {form, gloss, meaning, eroded, how}. `river`: the site's river name
        as the namer says it ({form, english, roman}) when it stands on one; `people_root`: the people's own root."""
        from .names import _join, _repair
        from .personal import _gloss
        h = self.habit(namer)
        t = h["template"]
        T = TEMPLATES[t]
        age = float(site.get("founded_kyr") or 0.0)
        spw = dict(h["specific"])
        if river is None:
            spw.pop("river", None)
            spw.pop("river_adj", None)
        if people_root is None:
            spw.pop("people", None)
        kind = _pick(rng, spw) or "adj"
        spec, sgloss, smeaning = self._specific(namer, kind, rng, river, people_root)
        if spec is None and kind != "adj":
            kind = "adj"
            spec, sgloss, smeaning = self._specific(namer, kind, rng, river, people_root)
        gen_c = None if T.get("locative") or kind in ("possessive", "descendants") else self.generic(namer, site, ctx, rng)
        if gen_c is None and not T.get("locative") and kind not in ("possessive", "descendants"):
            gen_c = next((c for c in ("TOWN", "VILLAGE", "HOUSE", "FENCE") if _w(namer, c) is not None), None)
        generic, eroded = None, False
        if gen_c is not None:
            generic = tuple(_w(namer, gen_c).form)
            if T["wear"] > 0 and age * T["wear"] >= SUFFIX_KYR:
                generic, eroded = tuple(LX.clip(generic, 1)), True
        how = T["like"]
        if T.get("locative"):
            pre = self._locative(namer)
            base = spec if spec is not None else tuple(_w(namer, "LAND").form) if _w(namer, "LAND") else None
            if base is None:
                return None
            form = _repair(namer, tuple(pre) + tuple(base)) if pre else tuple(base)
            gloss = f"the place of {sgloss}" if sgloss else "the place"
            frame = "locative class prefix" if pre else "bare root"
        elif kind in ("possessive", "descendants"):
            if spec is None:
                return None
            form, gloss, frame = spec, sgloss, kind
        elif generic is None:   # (no generic word at all: the specific alone)
            if spec is None:
                return None
            form, gloss, frame = spec, f"the {sgloss}" if not sgloss.endswith("'s") else f"{sgloss} (place)", "bare specific"
        elif spec is None:
            form, gloss, frame = generic, f"the {_gloss(gen_c)}", "generic"
        else:
            if T.get("rendaku"):
                generic = self._rendaku(namer, generic)
            if T["order"] == "spec_first":
                f = tuple(LX.clip(tuple(spec), 2)) + tuple(generic)
            else:
                art = self._article(namer) if T.get("article") else ()
                f = tuple(generic) + tuple(art) + tuple(LX.clip(tuple(spec), 2))
            from .names import _name_caps
            cap = _name_caps(namer)[1] + (1 if T.get("article") else 0)
            if LX.syllables(f) > cap:
                f = _join(namer, generic, spec)
            form = _repair(namer, f)
            gl = _gloss(gen_c)
            gloss = f"{sgloss} {gl}" if sgloss.endswith("'s") else (
                f"the {gl} of {'the ' if kind == 'nature' else ''}{sgloss}" if T["order"] == "generic_first" and kind != "adj" else f"the {sgloss} {gl}")
            frame = ("construct with the article" if T.get("article") and self._article(namer) else
                     "generic first" if T["order"] == "generic_first" else "generic last")
        return {"form": tuple(form), "gloss": gloss, "eroded": eroded, "how": how, "frame": frame,
                "meaning": {"generic": gen_c, "spec": smeaning, "frame": frame, "template": t}}

    def _specific(self, lect, kind, rng, river, people_root):
        """(form, gloss, meaning) of the specific part: a founder's name (bare, in the genitive, 'X's people', possessive,
        descendants), a river's name, an adjective, a thing of nature, an abstract word, the people's root."""
        from .personal import _gloss
        g = getattr(lect, "grammar", None)
        if kind in ("founder", "people_of", "possessive", "descendants"):
            pn = self.PN.for_lect_cached(lect)
            gv = [x for x in (pn or {}).get("given", []) if x.get("ipa")]
            if not gv:
                return None, None, None
            x = gv[int(rng.integers(len(gv)))]
            from .percepts import from_ipa
            f = tuple(from_ipa(x["ipa"].replace(" ", "")))
            name = x["roman"]
            if kind == "founder":
                gen = g.gram("GEN", bound=True) if g is not None else None
                if gen is not None and gen.form:
                    f = tuple(GR._attach(f, tuple(gen.form), gen.side))
                return f, f"{name}'s", {"kind": "founder", "name": name}
            if kind == "people_of":
                mk = self._people_marker(lect)
                if mk is None:
                    return None, None, None
                return tuple(LX.clip(f, 2)) + tuple(mk), f"{name}'s people's", {"kind": "people_of", "name": name}
            if kind == "possessive":
                suf = self._affix(lect, "like") or self._gen(lect)
                if suf is None:
                    return None, None, None
                return tuple(LX.clip(f, 2)) + tuple(suf), f"{name}'s (town)", {"kind": "possessive", "name": name}
            dim = self._affix(lect, "little") or ()
            mk = self._people_marker(lect) or ()
            if not dim and not mk:
                return None, None, None
            return (tuple(LX.clip(f, 2)) + tuple(dim) + tuple(mk), f"{name}'s descendants",
                    {"kind": "descendants", "name": name})
        if kind in ("river", "river_adj"):
            f = tuple(LX.clip(tuple(river["form"]), 2))
            if kind == "river_adj":
                suf = self._affix(lect, "like")
                if suf is None:
                    return None, None, None
                f = f + tuple(suf)
            return f, f"the {river['roman']}" + (" (river)'s" if kind == "river_adj" else ""), \
                {"kind": kind, "name": river["roman"], "english": river.get("stem")}
        if kind == "people":
            return tuple(people_root[0]), f"the {people_root[1]}", {"kind": "people", "name": people_root[1]}
        pool = {"adj": ADJ, "nature": NATURE, "abstract": ABSTRACT}.get(kind, ADJ)
        ok = [c for c in pool if _w(lect, c) is not None]
        if not ok:
            return None, None, None
        c = ok[int(rng.integers(len(ok)))]
        return tuple(_w(lect, c).form), _gloss(c), {"kind": kind, "concept": c}

    # ------------------------------------------------------------------ grammar bits
    @staticmethod
    def _affix(lect, meaning):
        a = (getattr(getattr(lect, "lexicon", None), "affixes", {}) or {}).get(meaning)
        return tuple(a[0]) if a and a[0] else None

    @staticmethod
    def _gen(lect):
        g = getattr(lect, "grammar", None)
        gr = g.gram("GEN", bound=True) if g is not None else None
        return tuple(gr.form) if gr is not None and gr.form else None

    @staticmethod
    def _people_marker(lect):
        from .names import _marker
        gr = _marker(getattr(lect, "grammar", None))
        if gr is not None and gr.form and gr.level != GR.FREE:
            return tuple(gr.form)
        w = _w(lect, "PEOPLE")
        return tuple(LX.clip(tuple(w.form), 1)) if w is not None else None

    @staticmethod
    def _article(lect):
        g = getattr(lect, "grammar", None)
        gr = g.gram("DEF") if g is not None else None
        if gr is not None and gr.form:
            return tuple(gr.form)
        w = _w(lect, "THAT")
        return tuple(LX.clip(tuple(w.form), 1)) if w is not None else ()

    @staticmethod
    def _locative(lect):
        """The prefix that makes a place: the place noun class, else a bound locative or place gram, else the 'place'
        derivational affix, else the first syllable of the word for land."""
        g = getattr(lect, "grammar", None)
        if g is not None:
            cs = getattr(g, "class_system", None)
            if cs is not None:
                c = cs.by_group("place")
                gr = g.by_id(c.gram_id) if c else None
                if gr is not None and gr.live and gr.form:
                    return tuple(gr.form)
            for fn in ("LOC", "PLACE"):
                gr = g.gram(fn, bound=True)
                if gr is not None and gr.form:
                    return tuple(gr.form)
        a = Habits._affix(lect, "place")
        if a:
            return a
        w = _w(lect, "LAND")
        return tuple(LX.clip(tuple(w.form), 1)) if w is not None else ()

    @staticmethod
    def _rendaku(lect, generic):
        """Voice the generic's first consonant in a compound when the lect has the voiced counterpart (-kawa > -gawa)."""
        from dataclasses import replace
        if not generic:
            return generic
        s0 = generic[0]
        if getattr(s0, "kind", "V") != "C" or getattr(s0, "voice", 1) or getattr(s0, "manner", 99) not in (0, 1, 2):
            return generic
        v = replace(s0, voice=1)
        try:
            from .names import _segs
            if v not in set(_segs(lect)):
                return generic
        except Exception:  # noqa: BLE001
            return generic
        return (v,) + tuple(generic[1:])
