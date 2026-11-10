"""Names (PW-972, architecture sections 7 and 11): endonyms, glossonyms, exonyms, place and river names, the Common and the
scholars' names, all built from each lect's own words through its grammar.

`build_names(result, run, rng_seed=None, landscape=None)` fills the `names` block of languages.json from history.generate's
result (living Lect objects, the shifts) and the run (reputation rows, deme landscape, mixed cities, contacts):

Codes follow the owner's taxonomy doc (rev 7) exactly (PATTERNS); a name's `pattern` is the doc's code and its `variant` the
generator's own label (VARIANT_CODE), since several variants share a code.

- **Endonyms** per people: a variant, drawn by weight (ENDONYM_WEIGHTS: 'people' E1 and 'real' E2 commonest; 'river_people'
  and 'river_name' E6 for peoples on a big river, 'original' E2 for the first settlers of their landmass, 'way' E8 from the
  way of life, 'totem' E9 when the people keeps a taboo on an animal, 'masters' E4 for a people that ruled another in a
  shift, 'speakers' E3, 'ancestor' E5, 'body' E9, 'many' E11 now and then). The form is the lect's own words with the
  grammar's people marker: a noun class or plural carries 'people' (Buganda / Baganda / Muganda / Luganda from
  `grammar.people_set`), otherwise the PEOPLE word heads a compound in the lect's head order. Every living lect of the
  people says the same variant with its own words (names.demes[d].name).
- **Exonyms** per reputation row (observer -> subject): `neighbour` -> X1, the first-met deme's own name heard through the
  observer's ears (X4 when the row was relayed by a third people: heard twice); `feared`/`despised` -> X5 'the enemies'
  after incursions or raids, else X3 'the mutes'; `exotic`/`edge` -> X8 by the direction they came from, X7 by their
  dwelling (cave, mountain, sea, river people) or their body (beak, teeth, horns, wings, size), X2 'the strangers' rarely.
  A 'speakers' (E3) people calls others X3 'mutes'.
- **Places** per living deme: the largest river (named by a lect that lived on it first, drawn by population; inherited
  words follow the lect, otherwise the old form is kept and heard by the newcomers: substrate, P2), the lake, the sea, a
  peak, the people's land; and its settlements (personal.py).
- **Personal names** per living lect (personal.py): a naming tradition inherited down the tree, given names old and new,
  bynames.
- **The Common**: the lect held by the most mixed cities (by heads), else the one with the most contacts.
- **Scholars' names** ('scholarly') for dead families: their oldest deme's river (else landmass) as the Common says it,
  with the Common's 'like' suffix ("the Ratalish languages").
- Spellings: `roman` is the book spelling, `roman_full` the workbench one (romanize.Orthography of the lect); a multi-word
  name capitalizes each word and joins a one- or two-letter particle with a hyphen (romanize.title_words).

Deterministic: every draw is `np.random.default_rng((seed, 972, crc32(key)))`. The taxonomy's etymologies are not
source-checked; only its patterns are used."""
from __future__ import annotations

import zlib

import numpy as np

from . import grammar as GR
from . import inventory as INV
from . import lexicon as LX
from . import profiles as PR
from . import romanize as RO
from .percepts import word_ipa

TICKET = 972
BIG_RIVER = 29600.0  # m^3/s (inputs.RIVER_FLOW units) above which a river is big enough to name a people (E4/E6; was 300
#                      flow units, ~29,600 m^3/s at L7, ~118,000 at L6; PW-820 units)
COAST_SHARE = 0.25  # share of a deme's cells on the coast for a sea name
PEAK_M = 1500.0  # highest cell for a peak name
MAX_SYLL = 4  # an ethnonym or place name root keeps to this many syllables (parts clipped to 2 first), in a language of
# the reference syllable space; both caps grow with the lexicon's length_scale (`_name_caps`), so a small-inventory
# language, whose words are longer, does not have its names clipped harder than its compounds

# The owner's taxonomy ("Ethnonyms: A Taxonomy for Culture Generation", rev 7): codes and meanings as the doc numbers them.
PATTERNS = {
    "E1": "'people' or 'humans'", "E2": "'real', 'true', 'ordinary' or 'original' people", "E3": "speakers of our language",
    "E4": "free, noble or high status", "E5": "legendary ancestor", "E6": "land, river or landscape",
    "E7": "position: border, middle, direction", "E8": "way of life, dwelling or gear", "E9": "physical trait or custom",
    "E10": "faith or covenant", "E11": "confederation or alliance", "E12": "adopted exonym or reclaimed insult",
    "X1": "first tribe or region met, used for the whole", "X2": "'foreigner' or 'other'", "X3": "mute or babbler",
    "X4": "relay borrowing through other languages", "X5": "'enemy'", "X6": "dynasty or state",
    "X7": "appearance, custom or dwelling as observed", "X8": "direction from the namer", "X9": "misattributed origin",
    "P1": "conquerors' name absorbed", "P2": "newcomers inherit the old inhabitants' name (substrate)",
    "P3": "exonym adopted as endonym", "P4": "constructed name", "P5": "rejection and renaming",
    "P6": "ethnonym becomes an ordinary word", "P7": "one root, split by borrowing", "P8": "parallel names by audience",
    "scholarly": "scholars' name for a dead family",
}
# The generator's variants (a name's `variant`) -> the doc's code (its `pattern`). Several variants share a code.
VARIANT_CODE = {"people": "E1", "real": "E2", "original": "E2", "speakers": "E3", "masters": "E4", "ancestor": "E5",
                "river_people": "E6", "river_name": "E6", "way": "E8", "body": "E9", "totem": "E9", "many": "E11",
                "met_first": "X1", "relay": "X4", "strangers": "X2", "mutes": "X3", "enemies": "X5", "by_body": "X7",
                "by_dwelling": "X7", "by_direction": "X8", "faith": "E10", "conquerors": "P1", "misattributed": "X9",
                "adopted": "E12"}
# a god's first domain (gods.json) -> the concept its people's faith name is built on (E10)
DOMAIN_CONCEPT = {"sea": "SEA", "river": "RIVER", "rain": "RAIN (PRECIPITATION)", "flood": "FLOOD", "sky": "SKY", "sun": "SUN",
                  "storm": "STORM", "mountain": "MOUNTAIN", "fire": "FIRE", "forest": "FOREST", "desert": "DESERT",
                  "herd": "HERD", "hunt": "HUNT", "harvest": "HARVEST", "fertility": "FERTILITY", "hearth": "HEARTH",
                  "smithing": "SMITHING", "death": "DEATH", "war": "WAR", "ancestors": "ANCESTORS"}
FAITH_W = (0.15, 0.6)  # E10 weight: base + this x the high god's individuation (rare, as the doc says: E9-E12 distinctive)
ENDONYM_WEIGHTS = {"people": 3.0, "real": 3.0, "speakers": 0.8, "ancestor": 0.5, "masters": 0.3, "body": 0.4,
                   "many": 0.4}  # always available; river_people, river_name, original, way, totem by context
WAY_CONCEPT = {"pastoral_nomad": ("HERD", "the herders"), "transhumant": ("HERD", "the herders"),
               "agro_pastoral": ("HERD", "the herders"), "fisher_forager": ("FISH", "the fishers"),
               "sea_nomad": ("FISH", "the fishers"), "farmer": ("SEED", "the sowers"), "horticulturalist": ("SEED", "the sowers"),
               "forager": ("ROOT", "the root-diggers")}
TRAIT_CONCEPT = {"hunter": ("HUNT", "the hunters"), "miner": ("STONE", "the stone-cutters"), "coastal": ("FISH", "the fishers"),
                 "sea_hunter": ("FISH", "the fishers")}
DIRECTION = {"north": "NORTH", "south": "SOUTH", "east": "EAST", "west": "WEST", "northeast": "NORTH", "northwest": "NORTH",
             "southeast": "SOUTH", "southwest": "SOUTH"}
RIVER_MODS = ("BLACK", "WHITE", "RED", "BIG", "LONG", "COLD", "STONE", "GOOD", "OLD")
PEAK_MODS = ("WHITE", "BIG", "OLD", "COLD", "STONE", "BLACK")
TABOO_ANIMAL = (("snake", "SNAKE"), ("eel", "SNAKE"), ("bear", "BEAR"), ("wolf", "WOLF"), ("deer", "DEER"), ("cervid", "DEER"),
                ("dog", "DOG"), ("bird", "BIRD"), ("fowl", "BIRD"), ("fish", "FISH"), ("horse", "HORSE"), ("cattle", "COW"))
RAID_WORDS = ("incursion", "displacement", "raid", "war", "driven out", "settled among")
# PW-1546 (names-spelling-gaps.md items 15, 16, 18-20): the taxonomy's processes over the run's history. The weights are
# taste calls (the doc's own weighting is "my judgment, not data"); each is listed in for-daniel.md.
GLOSSONYM_W = {"same": 0.75, "ours": 0.12, "place": 0.13}  # the language named from another root (Hittite nešili 'of Neša')
X9_W = 0.5           # weight of a misattributed origin among a thin-contact row's options (X2 0.35, X7 X8 1.0)
RELAY_CLIP = 0.35    # chance a relayed name of 4+ syllables keeps only its last two (Sioux < Naadowesiwag)
P1_TAKE = 0.6        # chance a deme that shifted to a ruling people's speech takes the rulers' name (France < Franks)
P3_ADOPT = 0.15      # chance a smaller people takes up the Common's name for itself (Hindu, Indonesia)
P5_REJECT = 0.5      # chance a people at least as numerous as its namer rejects an insulting exonym (Inuit over Eskimo)
P6_WORD = 0.3        # chance a long-feared or despised people's name becomes an ordinary word (vandal, slave)
P6_KYR = 1.0         # ... after at least this much contact (kyr)
SCHOLAR_W = {"river": 0.6, "reconstruction": 0.4}  # a dead family's scholars' name: its river, or its word for 'person' (Bantu)
LAND_MODS = ("BIG", "LONG", "WHITE", "OLD", "GOOD", "HIGH", "RED", "BLACK", "GREEN", "COLD", "WARM")
DISH_MAX = 3


def _rng(seed: int, *key) -> np.random.Generator:
    return np.random.default_rng((int(seed), TICKET, zlib.crc32(":".join(map(str, key)).encode())))


def _pick(rng, weights: dict) -> str:
    ks = sorted(k for k, v in weights.items() if v > 0)
    w = np.array([weights[k] for k in ks], float)
    return ks[int(rng.choice(len(ks), p=w / w.sum()))]


# ---------------------------------------------------------------------------------------------- words and spelling
def _gloss(concept: str) -> str:
    try:
        return LX.concept_info(concept).gloss.lower()
    except Exception:
        return concept.lower()


def _word(lect, concept: str):
    lx = getattr(lect, "lexicon", None)
    if lx is None:
        return None
    w = lx.get(concept)
    return w if w is not None and len(w.form) else None


def _first(lect, concepts) -> tuple[str | None, object]:
    for c in concepts:
        w = _word(lect, c)
        if w is not None:
            return c, w
    return None, None


_SPELL: dict = {}


def _segs(lect) -> list:
    try:
        return list(lect.segments())
    except Exception:
        return list(INV.segments(lect.inventory)) if getattr(lect, "inventory", None) is not None else []


def _roman_form(lect, form, book: bool = True) -> str:
    """A form's spelling in its lect: the book spelling (romanize book mode) by default; book=False the full house spelling
    (each name's `roman_full`, the workbench's)."""
    key = id(lect)
    sp = _SPELL.get(key)
    if sp is None or sp[0] is not lect:
        if getattr(lect, "lexicon", None) is not None and hasattr(lect, "segments"):
            from .output import orthography
            orth = orthography(lect)
        else:
            orth = RO.Orthography(_segs(lect), getattr(getattr(lect, "inventory", None), "allophones", None) or {},
                                  style=getattr(lect, "orth", None))
        sp = _SPELL[key] = (lect, orth)
    try:
        return sp[1].word(tuple(form), book=book)
    except Exception:
        return word_ipa(form)


def _roman_words(lect, words, book: bool = True) -> str:
    return RO.title_words([_roman_form(lect, w, book) for w in words])


def _hear(form, listener) -> tuple:
    """A form as the listener's lect hears and says it (profiles.hear_word, then the listener's phonotactic repair)."""
    inv = getattr(listener, "inventory", None)
    if inv is None:
        return tuple(form)
    heard = tuple(PR.hear_word(tuple(form), getattr(listener, "profile", None) or PR.HUMAN, INV.segments(inv)))
    try:
        rep = INV.repair(heard, inv)
    except Exception:
        rep = heard
    return tuple(rep or heard or form)


def _name_caps(lect) -> tuple[int, int]:
    """(syllables a part keeps, syllables a name keeps): 2 and MAX_SYLL times the lect's length scale (never less), the
    scale measured on its inventory when it has one (lexicon.length_scale), else the one its lexicon last stored."""
    inv = getattr(lect, "inventory", None)
    if inv is not None:
        sc = LX.length_scale(inv)
    else:
        sc = getattr(getattr(lect, "lexicon", None), "length_scale", 1.0) or 1.0
    sc = max(1.0, float(sc))
    return round(2 * sc), round(MAX_SYLL * sc)


def _clip(form, lect=None) -> tuple:
    return tuple(LX.clip(tuple(form), _name_caps(lect)[0] if lect is not None else 2))


def _join(lect, head, mod) -> tuple:
    """Compound of head and modifier in the lect's head order (grammar.compound), parts clipped to keep the name short
    (`_name_caps`: longer in a language with a small syllable space)."""
    h, m = _clip(head, lect), _clip(mod, lect)
    g = getattr(lect, "grammar", None)
    if g is not None:
        f = tuple(GR.compound(h, m, g))
    else:
        hf = getattr(getattr(lect, "lexicon", None), "head_first", False)
        f = h + m if hf else m + h
    cap = _name_caps(lect)[1]
    if LX.syllables(f) > cap:
        f = tuple(LX.clip(f, cap))
    return _repair(lect, f)


def _repair(lect, f) -> tuple:
    inv = getattr(lect, "inventory", None)
    if inv is None:
        return tuple(f)
    try:
        return tuple(INV.repair(tuple(f), inv) or f)
    except Exception:
        return tuple(f)


def _merge_steps(etym) -> list:
    """A word's etymology as [kyr, lect, process, ipa, gloss, note] steps, oldest first, a run of sound changes in one lect
    merged into one step (the last form)."""
    out: list = []
    for st in etym:
        row = [round(float(st.kyr), 3), st.lect, st.process, st.form, st.gloss, st.note]
        if out and st.process.startswith("sound_change:") and out[-1][2].startswith("sound_change") and out[-1][1] == st.lect:
            out[-1] = [row[0], st.lect, "sound_change:…", st.form, st.gloss, st.note]
        else:
            out.append(row)
    return out


def _ago(kyr: float) -> str:
    return "lately" if kyr < 0.25 else f"{kyr:g} kyr ago"


def _history_note(w) -> str:
    """The one thing worth saying about a word's past, in plain words ('' when it is simply old)."""
    now = _gloss(w.concept)
    steps = list(w.etym)
    for j in range(len(steps) - 1, -1, -1):
        st = steps[j]
        p = st.process.split(":", 1)
        if p[0] == "shift":
            prev = next((s.gloss for s in reversed(steps[:j]) if s.gloss), "")
            if prev and prev.lower() != now:
                return f"once '{prev.lower()}', {_ago(st.kyr)}"
        if p[0] == "borrow":
            return f"borrowed from {p[1] if len(p) > 1 else 'a neighbour'} {_ago(st.kyr)}"
        if p[0] == "substrate":
            return f"kept from the older speech {p[1] if len(p) > 1 else ''} {_ago(st.kyr)}".replace("  ", " ")
        if p[0] in ("derive", "compound", "coin", "taboo", "elaborate"):
            how = {"derive": "made", "compound": "compounded", "coin": "coined", "taboo": "a taboo word", "elaborate": "made"}[p[0]]
            return f"{how} {_ago(st.kyr)}"
        if p[0] == "proto":
            return ""
    return ""


def _part_plain(lect, w) -> str:
    note = _history_note(w)
    return f"{_roman_form(lect, w.form).lower()} '{_gloss(w.concept)}'" + (f" ({note})" if note else "")


def _marker(g):
    """The gram that carries 'people' (a noun class for people, else the plural), or None."""
    if g is None:
        return None
    cs = getattr(g, "class_system", None)
    if cs is not None:
        c = cs.by_group("people")
        gr = g.by_id(c.gram_id) if c else None
        if gr is not None and gr.live and gr.form:
            return gr
    gr = g.gram("PL")
    return gr if gr is not None and gr.form else None


# ---------------------------------------------------------------------------------------------- people names in one lect
def _people_name(lect, mods: list, gloss: str, variant: str, root_override=None, note: str = "") -> dict | None:
    """The people's name built from modifier words (Word objects; [] for E1) in one lect: the marker form when the grammar has
    one, else PEOPLE + modifiers. Returns {endonym fields..., set, parts, plain}."""
    g = getattr(lect, "grammar", None)
    mk = _marker(g)
    mods = [m for m in mods if m is not None]
    if root_override is not None:
        root = tuple(root_override)
    elif mods:  # (the last word heads the root compound: [BIRD, MOUTH] -> 'bird-mouth')
        root = _clip(mods[-1].form, lect)
        for m in reversed(mods[:-1]):
            root = _join(lect, root, m.form)
    else:  # E1: the word for person (a class or plural makes it 'the people') or the word for people itself
        _c, w = _first(lect, ("PERSON", "PEOPLE", "MAN") if mk is not None else ("PEOPLE", "PERSON", "MAN"))
        if w is None:
            return None
        root, mods = tuple(w.form), [w]
    parts = list(mods)
    if g is not None:
        s = GR.people_set(root, g, getattr(lect, "inventory", None), getattr(lect, "lexicon", None))
    else:
        s = {k: {"form": root, "words": [root], "ipa": word_ipa(root), "pattern": "bare root", "gloss": k} for k in
             ("person", "people", "land", "language")}
    if mk is None:  # (no class or plural to say 'people': PEOPLE heads a compound, and E1's person is the PERSON word)
        if root_override is not None or parts[0].concept not in ("PEOPLE", "PERSON", "MAN"):
            _c, head = _first(lect, ("PEOPLE", "PERSON", "MAN"))
            if head is not None:
                f = _join(lect, head.form, root)
                s["people"] = {"form": f, "words": [f], "ipa": word_ipa(f), "pattern": "compound with 'people'", "gloss": "the people"}
                parts = [head] + parts
        else:
            _c, pw = _first(lect, ("PERSON", "MAN"))
            f = tuple(pw.form) if pw is not None else root
            s["person"] = {"form": f, "words": [f], "ipa": word_ipa(f), "pattern": "the word for person", "gloss": "a person"}
    sset = {k: {"ipa": v["ipa"], "roman": _roman_words(lect, v["words"]), "roman_full": _roman_words(lect, v["words"], False),
                "how": v["pattern"]} for k, v in s.items()}
    ppl = s["people"]
    etym = [st for w in parts for st in _merge_steps(w.etym)]
    pattern = VARIANT_CODE.get(variant, variant)
    etym.append([None, lect.id, f"name:{pattern}", ppl["ipa"], gloss, note or ppl["pattern"]])
    roman = sset["people"]["roman"]
    if root_override is None:
        plain_parts = " + ".join(_part_plain(lect, w) for w in parts)
    else:
        plain_parts = " + ".join([note] + [_part_plain(lect, w) for w in parts])
    if mk is not None and "particle" not in ppl["pattern"] and ppl["pattern"] != "bare root":
        what = "the people class" if "class" in ppl["pattern"] else "the plural"
        plain_parts += f" + {'-' if mk.side == 'post' else ''}{_roman_form(lect, mk.form).lower()}{'-' if mk.side == 'pre' else ''}, {what}"
    elif "particle" in ppl["pattern"]:
        plain_parts += f" with the particle {_roman_form(lect, mk.form).lower()}"
    return {"ipa": ppl["ipa"], "roman": roman, "roman_full": sset["people"]["roman_full"], "gloss": gloss, "pattern": pattern,
            "variant": variant,
            "lect": lect.id, "parts": [w.concept for w in parts], "etym": etym, "set": sset, "root": root, "form": tuple(ppl["form"]),
            "plain": f"{roman}, '{gloss}': from {plain_parts}" if plain_parts else f"{roman}, '{gloss}'"}


def _english_feature(parts: list, key) -> tuple[str, str]:
    """A feature's Common English name (PW-1654) from its parts' concepts ([modifier, head] or [head], the head last):
    Blackwater, Whitemere, Coldfell; a sea apart (the White Sea)."""
    from .placenames import english
    head = parts[-1] if parts else None
    mod = parts[0] if len(parts) > 1 else None
    if head == "SEA":
        en, how = english({"generic": head, "spec": {"kind": "adj", "concept": mod} if mod else {}}, key)
        return ("The " + en if mod else "The Sea"), how
    return english({"generic": head, "spec": {"kind": "adj", "concept": mod} if mod else {}}, key)


def _public(n: dict | None) -> dict | None:
    if n is None:
        return None
    return {k: v for k, v in n.items() if k not in ("set", "root", "form")}


# ---------------------------------------------------------------------------------------------- the pass
class _Pass:
    def __init__(self, result: dict, run, seed: int, landscape: dict | None):
        self.res = result
        self.R = run
        self.seed = int(seed)
        self.lects = {l.id: l for l in result["lects"]}
        self.living = sorted((l for l in result["lects"] if l.died_kyr is None and l.deme is not None), key=lambda l: l.id)
        self.by_people: dict[str, list] = {}
        for l in self.living:
            self.by_people.setdefault(self._people(l), []).append(l)
        self.main = {p: max(ls, key=lambda l: (float(getattr(l, "population", 0) or 0), -_num(l.id), l.id))
                     for p, ls in sorted(self.by_people.items())}
        self.last = len(run.frames_kyr) - 1
        self.landscape = landscape
        self._ls: dict = {}
        self._contacts: dict = {}
        self.endonyms: dict = {}
        self.patterns: dict = {}
        self.ctx: dict = {}
        self.exo_forms: dict = {}   # (observer, subject) -> (form, gloss, roman, pattern): for relays (X4) and X9
        self.history: dict = {}     # people -> the doc's name_history: [{process, era_kyr, from, to, by, cause}]

    # -------------------------------------------------------------- helpers
    def _sites(self) -> tuple[dict, object]:
        """settlements.json's sites by cell (none without the file) and the river id per cell (None without it)."""
        import json
        from pathlib import Path
        doc = getattr(self.R, "settlements_doc", None)
        if doc is None:
            d = getattr(self.R, "dir", None)
            f = Path(d) / "settlements.json" if d is not None else None
            try:
                doc = json.loads(f.read_text()) if f is not None and f.exists() else {}
            except Exception:
                doc = {}
        by_cell: dict = {}
        for s in doc.get("sites") or []:
            if s.get("cell") is not None:
                by_cell.setdefault(int(s["cell"]), []).append(s)
        try:
            rids = np.asarray(self.R.river_id())
        except Exception:
            rids = None
        return by_cell, rids

    def _people_of_deme(self, d) -> str | None:
        try:
            return self.R.people_of(int(d))
        except Exception:
            l = next((x for x in self.lects.values() if x.deme == d), None)
            return None if l is None else l.people

    def _people(self, l) -> str:
        try:
            return self.R.people_of(l.deme)
        except Exception:
            return l.people

    def line(self, p: str) -> dict:
        return (getattr(self.R, "lines", None) or {}).get(p) or {}

    def deme_ls(self, d: int, i: int | None = None) -> dict:
        i = self.last if i is None else i
        k = (d, i)
        if k not in self._ls:
            try:
                self._ls[k] = self.R.deme_landscape(d, i) or {}
            except Exception:
                self._ls[k] = {}
        return self._ls[k]

    def lect_at(self, deme: int, kyr: float):
        """The lect deme `deme` spoke at `kyr` (kyr ago): the earliest one alive then, else its first."""
        ls = sorted((l for l in self.lects.values() if l.deme == deme), key=lambda l: (-l.born_kyr, l.id))
        for l in ls:
            if l.born_kyr + 1e-9 >= kyr and (l.died_kyr is None or l.died_kyr <= kyr + 1e-9):
                return l
        return ls[0] if ls else None

    def inherits(self, cur, old) -> bool:
        """Is `old` on cur's parent chain (bud or the shift's ruler line): cur's words descend from old's?"""
        x, seen = cur, set()
        while x is not None and x.id not in seen:
            if x.id == old.id:
                return True
            seen.add(x.id)
            x = self.lects.get(x.parent) if x.parent else None
        return False

    def family(self, l) -> str:
        x, seen = l, set()
        while x.parent and x.parent in self.lects and x.id not in seen:
            seen.add(x.id)
            x = self.lects[x.parent]
        return getattr(l, "family_true", None) or x.id

    def contacts(self, d: int, i: int) -> dict:
        k = (d, i)
        if k not in self._contacts:
            try:
                self._contacts[k] = self.R.contacts_of(d, i) or {}
            except Exception:
                self._contacts[k] = {}
        return self._contacts[k]

    # -------------------------------------------------------------- endonyms
    def settled_first(self, p: str, d: int) -> str | None:
        place = (self.R.demes[d].get("place") or "") if hasattr(self.R, "demes") else ""
        chain = {p, *(self.line(p).get("parents") or [])}
        for lm in ((getattr(self.R, "meta", {}) or {}).get("present") or {}).get("landmasses") or []:
            sb = (lm.get("settled_by") or {}).get("by")
            if sb in chain and lm.get("called") and lm["called"] in place:
                return lm["called"]
        return None

    def high_god(self, p: str, deme: int) -> tuple[str, str, float] | None:
        """(domain concept, label, individuation) of the living high god of the main deme's culture (gods.json and
        cultures.json beside the run), else None."""
        import json
        from pathlib import Path
        if not hasattr(self, "_gods"):
            d = getattr(self.R, "dir", None)
            try:   # (the run's faith readout, re-derived when stored before faiths: inputs.Run.gods_doc)
                g = (self.R.gods_doc() if hasattr(self.R, "gods_doc") else None) or \
                    (json.loads((Path(d) / "gods.json").read_text()) if d is not None else {})
                c = getattr(self.R, "cultures_doc", None) or \
                    (json.loads((Path(d) / "cultures.json").read_text()) if d is not None else {})
            except Exception:
                g, c = {}, {}
            self._gods = ({b["id"]: b for b in g.get("beings") or []}, g.get("cultures") or {}, c.get("deme_culture") or [])
        beings, cults, dc = self._gods
        if not beings or deme is None or deme >= len(dc) or dc[deme] is None:
            return None
        cu = cults.get(str(dc[deme])) or {}
        if cu.get("people") not in (None, p):
            return None
        hi = [beings[i] for i in cu.get("living") or [] if i in beings and beings[i].get("high")]
        if not hi:
            return None
        b = max(hi, key=lambda x: (float(x.get("devotion") or 0), -x["id"]))
        dom = b.get("first_domain") or ((b.get("top") or [[None]])[0][0])
        con = DOMAIN_CONCEPT.get(dom)
        if con is None:
            return None
        x, seen = b, set()   # (the god's key: the root of its parent chain, as faiths.Plan names it)
        while x.get("parent") is not None and x["parent"] in beings and x["id"] not in seen:
            seen.add(x["id"])
            x = beings[x["parent"]]
        return con, f"{dom} god", float(b.get("individuation") or 0.5), x["id"]

    def taboo_animal(self, p: str) -> str | None:
        tab = getattr(self.R, "taboos_doc", None)
        if tab is None:
            tab = self._load_taboos()
        for _cid, c in sorted((tab or {}).get("cultures", {}).items()):
            if c.get("people") != p:
                continue
            for t in c.get("taboos") or []:
                s = f"{t.get('target', '')} {t.get('label', '')}".lower()
                for key, concept in TABOO_ANIMAL:
                    if key in s:
                        return concept
        return None

    def _load_taboos(self):
        import json
        from pathlib import Path
        d = getattr(self.R, "dir", None)
        f = Path(d) / "taboos.json" if d is not None else None
        doc = json.loads(f.read_text()) if f is not None and f.exists() else {}
        try:
            self.R.taboos_doc = doc
        except Exception:
            pass
        return doc

    def body_feature(self, p: str) -> tuple[list[str], str] | None:
        """(concepts, gloss) for the most visible body trait: beak, sharp teeth, horns, wings, size."""
        l = self.line(p)
        b = l.get("body") or {}
        tr = set(l.get("traits") or [])
        disp = str(b.get("display") or "none")
        if b.get("teeth") == "beak":
            return ["BIRD", "MOUTH"], "the beaked ones (bird-mouths)"
        if disp in ("horns", "antlers") or "horn" in disp or "antler" in disp:
            return ["HORN (ANATOMY)"], "the horned ones"
        if "flies" in tr:
            return ["WING"], "the winged ones"
        if "giant" in p or "goliath" in p or "giant" in " ".join(l.get("parents") or []):
            return ["BIG"], "the big ones"
        if b.get("teeth") == "conical":
            return ["SHARP", "TOOTH"], "the sharp-toothed ones"
        if "swims" in tr:
            return ["WATER"], "the water ones"
        return None

    def endonym_pattern(self, p: str) -> tuple[str, dict]:
        main = self.main[p]
        rng = _rng(self.seed, "endonym", p)
        w = dict(ENDONYM_WEIGHTS)
        ctx: dict = {}
        ls = self.deme_ls(main.deme)
        if ls.get("river") is not None:
            ctx["river"] = ls["river"]
            big = float(ls.get("river_flow") or 0) >= BIG_RIVER
            w["river_people"] = 2.0 if big else 0.6
            w["river_name"] = 1.5 if big else 0.0
        lm = self.settled_first(p, main.deme)
        if lm:
            ctx["landmass"] = lm
            w["original"] = 2.5
        line = self.line(p)
        wc = WAY_CONCEPT.get(line.get("way") or "")
        if wc is None:
            wc = next((TRAIT_CONCEPT[t] for t in sorted(line.get("traits") or []) if t in TRAIT_CONCEPT), None)
        if wc is not None and _word(main, wc[0]) is not None:
            ctx["way"] = wc
            w["way"] = 2.0
        fa = self.high_god(p, main.deme)
        if fa and _word(main, "GOD") is not None and _word(main, fa[0]) is not None:
            ctx["faith"] = fa
            w["faith"] = FAITH_W[0] + FAITH_W[1] * fa[2]
        ta = self.taboo_animal(p)
        if ta and _word(main, ta) is not None:
            ctx["totem"] = ta
            w["totem"] = 1.0
        bf = self.body_feature(p)
        if bf and all(_word(main, c) is not None for c in bf[0]):
            ctx["body"] = bf
        else:
            w.pop("body", None)
        if any(s.get("ruler_deme") is not None and self._people_of_deme(s["ruler_deme"]) == p for s in self.res.get("shifts") or []):
            w["masters"] = 1.5  # (a people that ruled another calls itself the masters, as the Ārya 'noble')
        pops = sorted(float(getattr(self.main[q], "population", 0) or 0) for q in self.main)
        if not pops or float(getattr(main, "population", 0) or 0) < pops[int(0.75 * (len(pops) - 1))]:
            w.pop("many", None)
        return _pick(rng, w), ctx

    def endonym_in(self, lect, p: str, var: str, ctx: dict) -> dict | None:
        """People p's name in one lect, by variant (VARIANT_CODE gives the taxonomy code)."""
        W = lambda c: _word(lect, c)  # noqa: E731
        if var == "real" and W("REAL") is not None:
            return _people_name(lect, [W("REAL")], "the real people", var)
        if var == "speakers" and W("SPEAK") is not None:
            return _people_name(lect, [W("SPEAK")], "the speakers", var)
        if var == "masters" and W("MASTER") is not None:
            return _people_name(lect, [W("MASTER")], "the masters (the free, the noble)", var)
        if var == "river_people" and W("RIVER") is not None:
            return _people_name(lect, [W("RIVER")], "the river people", var)
        if var == "river_name" and ctx.get("river") is not None:
            hyd = self.river_name(lect, ctx["river"])
            if hyd is not None:
                return _people_name(lect, [], f"named after the {hyd['gloss']} ({hyd['roman']})", var, root_override=hyd["form"],
                                    note=f"the river's name {hyd['roman']}, '{hyd['gloss']}'")
        if var == "original" and W("OLD") is not None:
            return _people_name(lect, [W("OLD")], f"the old people (first on {ctx.get('landmass', 'their land')})", var)
        if var == "way" and ctx.get("way") and W(ctx["way"][0]) is not None:
            return _people_name(lect, [W(ctx["way"][0])], ctx["way"][1], var)
        if var == "totem" and ctx.get("totem") and W(ctx["totem"]) is not None:
            return _people_name(lect, [W(ctx["totem"])], f"the {_gloss(ctx['totem'])} people", var)
        if var == "body" and ctx.get("body"):
            ws = [W(c) for c in ctx["body"][0]]
            if all(x is not None for x in ws):
                return _people_name(lect, ws, ctx["body"][1], var)
        if var == "faith" and ctx.get("faith"):   # (by the god's own name in this lect when it has one: faiths.py)
            gw = W(f"name:god:{ctx['faith'][3]}") if len(ctx["faith"]) > 3 else None
            if gw is not None:
                from .faiths import name_gloss
                return _people_name(lect, [gw], f"the people of {name_gloss(gw) or 'their god'} (the {ctx['faith'][1]})", var)
            if W("GOD") is not None and W(ctx["faith"][0]) is not None:
                return _people_name(lect, [W(ctx["faith"][0]), W("GOD")], f"the people of the {ctx['faith'][1]}", var)
        if var == "many" and W("MANY") is not None:
            return _people_name(lect, [W("MANY")], "the many", var)
        if var == "ancestor" and getattr(lect, "inventory", None) is not None:
            anc = tuple(INV.draw_word(_rng(self.seed, "ancestor", p), lect.inventory, 2))
            r = RO.title_name(_roman_form(lect, anc))
            return _people_name(lect, [], f"the children of {r}", var, root_override=anc, note=f"{r}, an ancestor's name")
        return _people_name(lect, [], "the people", "people")

    # -------------------------------------------------------------- places
    def _first_on(self, kind: str, rid: int) -> tuple[int | None, float | None]:
        """The deme that named a river (lake) and when: among the demes on it at its first naming (landscape `demes`, oldest
        first), a draw weighted by each deme's population at that frame (run.deme_population; else its cells on the water), so
        numerous settled peoples usually name the water and a thinly spread one (dragons) only sometimes."""
        L = (self.landscape or {}).get("rivers" if kind == "river" else "lakes") or {}
        v = L.get(str(rid)) or L.get(rid)
        if not v or not v.get("demes"):
            return None, None
        k0 = max(float(k) for _d, k in v["demes"])
        tied = sorted({int(d) for d, k in v["demes"] if float(k) == k0})
        if len(tied) == 1:
            return tied[0], k0
        w = None
        try:
            i = self.R.frame_of(k0)
        except Exception:
            i = None
        if i is not None and hasattr(self.R, "deme_population"):
            try:
                w = [max(float(self.R.deme_population(d, i)), 0.0) ** 0.5 for d in tied]  # square root: a few dragons still name a river now and then
            except Exception:
                w = None
        if (w is None or sum(w) <= 0) and i is not None:
            try:
                ids = self.R.river_id() if kind == "river" else self.R.lake_id()
                cells = self.R.frame(i).cells
                w = [float((ids[cells[d]] == int(rid)).sum()) if d in cells else 0.0 for d in tied]
            except Exception:
                w = None
        if w is None or sum(w) <= 0:
            w = [1.0] * len(tied)
        p = np.asarray(w, float) / sum(w)
        return tied[int(_rng(self.seed, "namer", kind, rid).choice(len(tied), p=p))], k0

    def _base_name(self, namer, kind: str, rid) -> dict | None:
        head_c = "RIVER" if kind == "river" else "LAKE"
        rng = _rng(self.seed, kind, rid)
        _c, head = _first(namer, (head_c, "WATER"))
        if head is None:
            return None
        if rng.random() < 0.3:
            return {"form": tuple(head.form), "words": [head], "gloss": f"the {_gloss(head.concept)}"}
        mods = [c for c in RIVER_MODS if _word(namer, c) is not None]
        if not mods:
            return {"form": tuple(head.form), "words": [head], "gloss": f"the {_gloss(head.concept)}"}
        m = _word(namer, mods[int(rng.integers(len(mods)))])
        return {"form": _join(namer, head.form, m.form), "words": [m, head], "gloss": f"the {_gloss(m.concept)} {_gloss(head.concept)}"}

    def water_name(self, cur, kind: str, rid, deme: int) -> dict | None:
        """A river's (or lake's) name as `cur` says it: coined by the lect that lived on it first; inherited words keep evolving
        with the lect (a replaced word survives as a fossil), and a name from an unrelated or pre-shift lect is kept as heard
        by the newcomers (substrate)."""
        d0, k0 = self._first_on(kind, rid)
        namer = self.lect_at(d0, k0) if d0 is not None else None
        if namer is None:
            namer, k0 = cur, cur.born_kyr
        base = self._base_name(namer, kind, rid)
        if base is None:
            return None
        sub, via = None, None
        if self.inherits(cur, namer):
            ws = []
            for w in base["words"]:
                cw = _word(cur, w.concept)
                ws.append(cw if cw is not None and _root(cw) == _root(w) else w)
            form = ws[0].form if len(ws) == 1 else _join(cur, ws[1].form, ws[0].form)
            words = ws
        else:
            form, words = _hear(base["form"], cur), base["words"]
            sub = namer.id
            via = next((f"kept when deme {s['deme']} shifted from {s['from_lect']} to {s['to_lect']} ({s['kyr']:g} kyr ago)"
                        for s in self.res.get("shifts") or [] if s.get("from_lect") == namer.id), None) \
                or f"heard from {namer.id} ({namer.people}), who lived on it first"
            # a tautology (River Avon, Lake Windermere-mere): the newcomers, who no longer understand the old name's
            # word for water, add their own (personal.SUBSTRATE_TAUTOLOGY, as for settlements)
            head_c = "RIVER" if kind == "river" else "LAKE"
            own, old_head = _first(cur, (head_c, "WATER"))[1], base["words"][-1]
            from .personal import SUBSTRATE_TAUTOLOGY
            if own is not None and _root(own) != _root(old_head) and _rng(self.seed, "taut", kind, rid, cur.id).random() < SUBSTRATE_TAUTOLOGY:
                form = _join(cur, own.form, form)
                taut = f"{_gloss(own.concept)} + the old name (a tautology, like River Avon)"
                via += "; " + taut
                base = dict(base, gloss=f"the {_gloss(own.concept)} {base['gloss'].removeprefix('the ')}")
                words = list(words) + [own]
        g = getattr(cur, "grammar", None)
        loc = GR.place_name(form, g) if g is not None else None
        roman = RO.title_name(_roman_form(cur, form))
        roman_full = RO.title_name(_roman_form(cur, form, False))
        plain = f"{roman}, '{base['gloss']}': " + " + ".join(_part_plain(namer, w) for w in base["words"])
        plain += f"; named by {namer.id} ({namer.people}) about {k0:g} kyr ago" + (f"; {via}" if via else "")
        etym = [st for w in words for st in _merge_steps(w.etym)]
        etym.append([k0, namer.id, f"name:{kind}", word_ipa(base["form"]), base["gloss"], ""])
        if sub:
            etym.append([None, cur.id, f"substrate:{sub}", word_ipa(form), base["gloss"], via or ""])
        en, en_how = _english_feature([w.concept for w in base["words"]], f"{kind}{rid}")
        return {"kind": kind, "id": int(rid), "english": en, "english_how": en_how,
                "meaning": {"parts": [w.concept for w in base["words"]]}, "ipa": word_ipa(form), "roman": roman, "roman_full": roman_full, "gloss": base["gloss"],
                "lect": cur.id, "tautology": bool(sub and "tautology" in (via or "")),
                "named_by": namer.id, "kyr": round(float(k0), 3), "substrate_of": sub, "pattern": "P2" if sub else None,
                "locative": None if loc is None else {"ipa": loc["ipa"], "roman": _roman_words(cur, loc["words"]),
                                                      "roman_full": _roman_words(cur, loc["words"], False)},
                "etym": etym, "plain": plain, "form": tuple(form)}

    def river_name(self, cur, rid):
        return self.water_name(cur, "river", rid, cur.deme)

    def plain_place(self, cur, kind: str, head_c: str, mods: tuple, key) -> dict | None:
        rng = _rng(self.seed, kind, key)
        head = _word(cur, head_c)
        if head is None:
            return None
        ms = [c for c in mods if _word(cur, c) is not None]
        if ms:
            m = _word(cur, ms[int(rng.integers(len(ms)))])
            form, words, gloss = _join(cur, head.form, m.form), [m, head], f"the {_gloss(m.concept)} {_gloss(head.concept)}"
        else:
            form, words, gloss = tuple(head.form), [head], f"the {_gloss(head.concept)}"
        roman = RO.title_name(_roman_form(cur, form))
        g = getattr(cur, "grammar", None)
        loc = GR.place_name(form, g) if g is not None else None
        etym = [st for w in words for st in _merge_steps(w.etym)] + [[None, cur.id, f"name:{kind}", word_ipa(form), gloss, ""]]
        en, en_how = _english_feature([w.concept for w in words], f"{kind}{key}")
        return {"kind": kind, "ipa": word_ipa(form), "english": en, "english_how": en_how, "roman": roman, "roman_full": RO.title_name(_roman_form(cur, form, False)),
                "gloss": gloss, "lect": cur.id, "named_by": cur.id,
                "kyr": None, "substrate_of": None, "pattern": None,
                "locative": None if loc is None else {"ipa": loc["ipa"], "roman": _roman_words(cur, loc["words"]),
                                                      "roman_full": _roman_words(cur, loc["words"], False)},
                "etym": etym, "plain": f"{roman}, '{gloss}': " + " + ".join(_part_plain(cur, w) for w in words)}

    def places(self, l, endo: dict | None) -> list:
        ls = self.deme_ls(l.deme)
        out = []
        if ls.get("river") is not None:
            r = self.water_name(l, "river", ls["river"], l.deme)
            if r:
                out.append(r)
        if ls.get("lake") is not None:
            r = self.water_name(l, "lake", ls["lake"], l.deme)
            if r:
                out.append(r)
        if float(ls.get("coast_share") or 0) >= COAST_SHARE:
            r = self.plain_place(l, "sea", "SEA", ("BLACK", "WHITE", "BIG", "COLD", "SALTY"), l.deme)
            if r:
                out.append(r)
        if float(ls.get("mountain_m") or 0) >= PEAK_M:
            r = self.plain_place(l, "peak", "MOUNTAIN", PEAK_MODS, l.deme)
            if r:
                out.append(r)
        if endo is not None:
            land = endo["set"]["land"]
            from .placenames import anglicize
            en = anglicize(endo["roman"]) + ("land" if zlib.crc32(str(l.deme).encode()) % 3 else "mark")
            out.append({"kind": "land", "ipa": land["ipa"], "roman": land["roman"], "roman_full": land["roman_full"],
                        "english": en, "english_how": f"{endo['roman']} + -{en[len(anglicize(endo['roman'])):]} 'land'",
                        "gloss": f"the land of the {endo['gloss'].split(' (')[0].removeprefix('the ')}",
                        "lect": l.id, "named_by": l.id, "kyr": None, "substrate_of": None, "pattern": endo["pattern"],
                        "locative": None, "etym": endo["etym"][-1:], "plain": f"{land['roman']}: their land ({land['how']})"})
        for p in out:
            p.pop("form", None)
            p.pop("meaning", None)
        return out[:5]

    # -------------------------------------------------------------- exonyms
    def first_met(self, obs_lect, subject: str, since_kyr) -> object:
        """The subject's lect the observer met first: at the frame of first contact (clamped to the window), the subject deme
        most in contact with the observer's main deme; else the subject's main lect."""
        subj = self.by_people.get(subject) or []
        if not subj:
            return None
        i = self.R.frame_of(float(since_kyr)) if since_kyr is not None and hasattr(self.R, "frame_of") else self.last
        c = self.contacts(obs_lect.deme, i)
        best = None
        for l in subj:
            v = float(c.get(l.deme, 0.0))
            if v > 0 and (best is None or v > best[0]):
                best = (v, l)
        return best[1] if best else self.main.get(subject)

    def exonym(self, observer: str, subject: str, row: dict) -> dict | None:
        ol = self.main.get(observer)
        if ol is None:
            return None
        rng = _rng(self.seed, "exonym", observer, subject)
        heard = ()
        val = row.get("valence")
        basis = row.get("basis") or ""
        e3 = self.patterns.get(observer) == "speakers"
        relay = []
        W = lambda c: _word(ol, c)  # noqa: E731
        name = None
        if e3 and W("MUTE") is not None and (val != "neighbour" or rng.random() < 0.5):
            name = _people_name(ol, [W("MUTE")], "the mutes (those who do not speak)", "mutes")
        elif val == "neighbour" and subject in self.main:
            met = self.first_met(ol, subject, row.get("since_kyr"))
            src = self.endonyms.get(subject, {}).get("by_lect", {}).get(met.id) or self.endonyms.get(subject, {}).get("main")
            if src is not None:
                form = tuple(src["form"])
                bf = row.get("borrowed_from")
                pat, var = "X1", "met_first"
                if bf and bf in self.main and bf != observer:
                    form = _hear(form, self.main[bf])
                    relay = [self.main[bf].id]
                    pat, var = "X4", "relay"
                heard = _hear(form, ol)
                roman = RO.title_name(_roman_form(ol, heard))
                g = f"their own name {src['roman']} ('{src['gloss']}'), as {observer} ears hear it" + (f" through the {bf}" if relay else "")
                name = {"ipa": word_ipa(heard), "roman": roman, "roman_full": RO.title_name(_roman_form(ol, heard, False)), "gloss": g,
                        "pattern": pat, "variant": var, "lect": ol.id, "form": heard,
                        "parts": [], "etym": [[None, met.id, "name:endonym", src["ipa"], src["gloss"], ""]]
                        + [[None, r, "relay", word_ipa(form), src["gloss"], "X4: heard by a third people"] for r in relay]
                        + [[None, ol.id, f"name:{pat}", word_ipa(heard), "", "heard"]],
                        "plain": f"{roman}: what the {observer} call the {subject}: {g}" + (f" (first met in deme {met.deme})" if met else "")}
        elif val in ("feared", "despised"):
            raid = any(k in basis.lower() for k in RAID_WORDS) or row.get("category") in ("raiders", "goblin_menace")
            if raid and W("ENEMY") is not None:
                name = _people_name(ol, [W("ENEMY")], "the enemies (raiders)", "enemies")
            elif W("MUTE") is not None:
                name = _people_name(ol, [W("MUTE")], "the mutes (those who do not speak right)", "mutes")
        if name is None:
            opts: dict = {}
            dirc = DIRECTION.get(str(row.get("from_dir") or "").lower().replace("-", "")) or self.direction(ol, subject)
            if dirc and W(dirc) is not None:
                opts["X8"] = 1.0
            land = self.land_of(subject)
            if land and W(land[0]) is not None:
                opts["X7d"] = 1.0  # (dwelling as observed: the doc's X7, with X7 by body)
            bf = self.body_feature(subject)
            if bf and all(W(c) is not None for c in bf[0]):
                opts["X7"] = 1.2 if row.get("category") == "giant_kin" else 1.0
            if W("STRANGER") is not None:
                opts["X2"] = 0.35
            mis = self.misattributed(ol, observer, subject, dirc)
            if mis is not None:
                opts["X9"] = X9_W
            if not opts:
                return None
            pat = _pick(rng, opts)
            if pat == "X8":
                name = _people_name(ol, [W(dirc)], f"the {_gloss(dirc)}erners" if dirc in ("NORTH", "SOUTH") else f"the people of the {_gloss(dirc)}", "by_direction")
            elif pat == "X7d":
                name = _people_name(ol, [W(land[0])], land[1], "by_dwelling")
            elif pat == "X7":
                name = _people_name(ol, [W(c) for c in bf[0]], bf[1], "by_body")
            elif pat == "X9":
                name = self.misattributed_name(ol, observer, subject, mis)
            else:
                name = _people_name(ol, [W("STRANGER")], "the strangers", "strangers")
        if name is None:
            return None
        self.exo_forms[(observer, subject)] = (tuple(name["form"]) if name.get("form") else tuple(heard),
                                               name["gloss"], name["roman"], name["pattern"])
        out = _public(name)
        out.pop("lect", None)
        out.update({"by_people": observer, "by_lect": ol.id, "subject": subject, "basis": basis, "valence": val,
                    "era_kyr": row.get("since_kyr"), "relay": relay, "strength": row.get("strength")})
        return out

    def relay(self, observer: str, subject: str, row: dict) -> dict | None:
        """X4: a name the observer took from a third people (the row's `borrowed_from`): that people's own name for the
        subject, heard again through the observer's ears, and cut to its last two syllables now and then (Sioux <
        Naadowesiwag, through French)."""
        bf = row.get("borrowed_from")
        ol = self.main.get(observer)
        src = self.exo_forms.get((bf, subject))
        if ol is None or src is None or bf == observer or bf not in self.main:
            return None
        form, sgloss, sroman, spat = src
        heard = _hear(form, ol)
        rng = _rng(self.seed, "relay", observer, subject)
        clipped = False
        if LX.syllables(heard) >= 4 and rng.random() < RELAY_CLIP:
            from .percepts import syllabify
            heard = _repair(ol, tuple(s for x in syllabify(heard)[-2:] for s in x.segments))
            clipped = True
        roman = RO.title_name(_roman_form(ol, heard))
        g = f"the {bf} name for them, {sroman} ('{sgloss}'), as {observer} ears hear it" + (", cut short" if clipped else "")
        out = {"ipa": word_ipa(heard), "roman": roman, "roman_full": RO.title_name(_roman_form(ol, heard, False)), "gloss": g,
               "pattern": "X4", "variant": "relay", "parts": [],
               "etym": [[None, self.main[bf].id, f"name:{spat}", word_ipa(form), sgloss, ""],
                        [None, ol.id, "name:X4", word_ipa(heard), "", "heard through the " + bf]],
               "plain": f"{roman}: what the {observer} call the {subject}: {g}"}
        self.exo_forms[(observer, subject)] = (heard, sgloss, roman, "X4")
        out.update({"by_people": observer, "by_lect": ol.id, "subject": subject, "basis": row.get("basis") or "",
                    "valence": row.get("valence"), "era_kyr": row.get("since_kyr"), "relay": [self.main[bf].id],
                    "strength": row.get("strength")})
        return out

    def misattributed(self, ol, observer: str, subject: str, dirc) -> str | None:
        """X9: a people the observer knows well (a neighbour row) that lies the way the subject came from: the observer
        takes the subject to come from there (Gypsy < Egyptian, Bohémien). None without one."""
        if not dirc:
            return None
        rows = (((getattr(self.R, "meta", {}) or {}).get("present") or {}).get("reputation") or {}).get("rows") or {}
        cands = sorted(t for t, r in (rows.get(observer) or {}).items()
                       if t not in (subject, observer) and r.get("valence") == "neighbour" and t in self.main
                       and (observer, t) in self.exo_forms
                       and (DIRECTION.get(str(r.get("from_dir") or "").lower().replace("-", "")) or self.direction(ol, t)) == dirc)
        if not cands:
            return None
        return cands[int(_rng(self.seed, "x9", observer, subject).integers(len(cands)))]

    def misattributed_name(self, ol, observer: str, subject: str, third: str) -> dict | None:
        form, tgloss, troman, _p = self.exo_forms[(observer, third)]
        like = (getattr(getattr(ol, "lexicon", None), "affixes", {}) or {}).get("like")
        if like and like[0]:
            form = _repair(ol, tuple(form) + tuple(like[0]) if like[1] else tuple(like[0]) + tuple(form))
        roman = RO.title_name(_roman_form(ol, form))
        g = f"the {third}-ish ones: the {observer} took them to come from the {third} ({troman}), a misattributed origin"
        return {"ipa": word_ipa(form), "roman": roman, "roman_full": RO.title_name(_roman_form(ol, form, False)), "gloss": g,
                "pattern": "X9", "variant": "misattributed", "lect": ol.id, "parts": [], "form": tuple(form),
                "etym": [[None, ol.id, "name:X9", word_ipa(form), g, f"from their name for the {third}"]],
                "plain": f"{roman}: what the {observer} call the {subject}: {g}"}

    def direction(self, ol, subject: str) -> str | None:
        """Where the subject's main deme lies from the observer's (the larger of the north-south and east-west offsets of their
        cell centroids), as a direction concept; None without a grid."""
        sl = self.main.get(subject)
        g = getattr(self.R, "g", None)
        if sl is None or g is None:
            return None
        try:
            pts = []
            for l in (ol, sl):
                cells, _ = self.R.deme_cells(l.deme, self.last)
                if not len(cells):
                    return None
                lon = np.radians(np.asarray(g.lon)[cells])
                pts.append((float(np.mean(np.asarray(g.lat)[cells])),
                            float(np.degrees(np.arctan2(np.sin(lon).mean(), np.cos(lon).mean())))))
        except Exception:
            return None
        dlat = pts[1][0] - pts[0][0]
        dlon = (pts[1][1] - pts[0][1] + 180.0) % 360.0 - 180.0
        dlon *= np.cos(np.radians((pts[0][0] + pts[1][0]) / 2))
        if abs(dlat) < 1.0 and abs(dlon) < 1.0:
            return None
        return ("NORTH" if dlat > 0 else "SOUTH") if abs(dlat) >= abs(dlon) else ("EAST" if dlon > 0 else "WEST")

    def land_of(self, p: str) -> tuple[str, str] | None:
        l = self.main.get(p)
        tr = set(self.line(p).get("traits") or [])
        if "subterranean" in tr:
            return ("CAVE", "the cave people")
        ls = self.deme_ls(l.deme) if l is not None else {}
        if "mountain" in tr or float(ls.get("mountain_share") or 0) > 0.3:
            return ("MOUNTAIN", "the mountain people")
        if float(ls.get("coast_share") or 0) > 0.5 or tr & {"coastal", "sea_hunter", "swims"}:
            return ("SEA", "the sea people")
        if ls.get("river") is not None:
            return ("RIVER", "the river people")
        if "hardy" in tr:
            return ("HILL", "the hill people")
        return None

    # -------------------------------------------------------------- the Common and the scholars
    def unique_english(self, demes: dict) -> None:
        """PW-1654: the Common's English names unique per region (the deme's place, 'the west of Simath'): living places
        first by size, then ruins (placenames.unique_english)."""
        from .placenames import unique_english
        recs = []
        for d, e in demes.items():
            for x in e.get("places") or []:
                recs.append((0, -(x.get("id") is not None), 0, d, x))
            for x in e.get("settlements") or []:
                recs.append((1 if x.get("kind") == "ruin" else 0, 1, -(x.get("pop") or 0), d, x))
        recs.sort(key=lambda r: (r[0], r[1], r[2], str(r[3]), r[4].get("site") or r[4].get("id") or 0, r[4].get("kind")))

        def region(r):
            d = int(r["_deme"])
            try:
                return (self.R.demes[d].get("place") or str(d)) if hasattr(self.R, "demes") else str(d)
            except Exception:  # noqa: BLE001
                return str(d)
        xs = []
        for _a, _b, _c, d, x in recs:
            x["_deme"] = d
            xs.append(x)
        unique_english(xs, region)
        for x in xs:
            x.pop("_deme", None)

    def common(self) -> tuple[object, str]:
        score: dict = {}
        try:
            cities = self.R.mixed_cities(self.last)
        except Exception:
            cities = []
        for c in cities:
            l = next((x for x in self.living if x.deme == c.get("holder_deme")), None)
            if l is not None:
                score[l.id] = score.get(l.id, 0.0) + float(c.get("pop") or 1.0)
        if score:
            best = max(score, key=lambda k: (score[k], k))
            n = sum(1 for c in cities if any(x.id == best and x.deme == c.get("holder_deme") for x in self.living))
            return self.lects[best], f"held by the most mixed cities ({n}, {score[best]:,.0f} heads)"
        deg = {l.id: len(self.contacts(l.deme, self.last)) for l in self.living}
        if not deg:
            return None, "no living lects"
        best = max(deg, key=lambda k: (deg[k], k))
        return self.lects[best], f"no mixed cities: the lect in contact with the most demes ({deg[best]})"

    def scholars(self, common) -> dict:
        fams: dict = {}
        for l in self.lects.values():
            if l.deme is not None:
                fams.setdefault(self.family(l), []).append(l)
        alive = {self.family(l) for l in self.living}
        out, used = {}, {}
        like = (getattr(getattr(common, "lexicon", None), "affixes", {}) or {}).get("like") if common is not None else None
        for f, ls in sorted(fams.items()):
            if f in alive:
                continue
            old = max(ls, key=lambda l: (l.born_kyr, -_num(l.id), l.id))
            i = self.R.frame_of(old.born_kyr) if hasattr(self.R, "frame_of") else 0
            ls0 = self.deme_ls(old.deme, i)
            basis_used = None
            base, gl = None, None
            srng = _rng(self.seed, "scholars", f)
            basis = _pick(srng, SCHOLAR_W) if ls0.get("river") is not None else \
                ("reconstruction" if srng.random() < 0.6 else "land")   # (no river: the word for person, else the land)
            pw = _first(old, ("PERSON", "PEOPLE", "MAN"))[1]
            if basis == "reconstruction" and pw is not None:
                # (named from the family's reconstructed word for 'person', as Bleek named Bantu, as the Common says it)
                base = _hear(pw.form, common) if common is not None else tuple(pw.form)
                stem = RO.title_name(_roman_form(common or old, base))
                stem_full = RO.title_name(_roman_form(common or old, base, False))
                gl = (f"after their reconstructed word for '{_gloss(pw.concept)}', *{_roman_form(old, pw.form)}, as scholars "
                      "named Bantu")
                basis_used = "reconstruction"
            elif ls0.get("river") is not None:
                b = self._base_name(old, "river", ls0["river"])
                if b is not None:
                    base = _hear(b["form"], common) if common is not None else b["form"]
                    gl = f"after the river {RO.title_name(_roman_form(old, b['form']))} ('{b['gloss']}') where the oldest of them was spoken"
                basis_used = "river"
            if basis_used == "reconstruction":
                pass
            elif base is not None:
                if like and like[0]:
                    base = tuple(base) + tuple(like[0]) if like[1] else tuple(like[0]) + tuple(base)
                stem = RO.title_name(_roman_form(common or old, base))
                stem_full = RO.title_name(_roman_form(common or old, base, False))
            else:
                place = (self.R.demes[old.deme].get("place") or "") if hasattr(self.R, "demes") else ""
                lm = place.split(" of ")[-1].strip() or f"family {f}"
                suf = _roman_form(common, like[0]).lower() if common is not None and like and like[0] else "ian"
                stem = lm + suf
                stem_full = lm + (_roman_form(common, like[0], False).lower() if common is not None and like and like[0] else "ian")
                gl = f"after {lm}, the land where the oldest of them was spoken"
                basis_used = "land"
            n = used.get(stem, 0) + 1
            used[stem] = n
            if n > 1:  # (scholars number the families they name after the same river or land)
                stem = f"{stem} {_ROMAN_NUM[min(n, len(_ROMAN_NUM)) - 1]}"
                stem_full = f"{stem_full} {_ROMAN_NUM[min(n, len(_ROMAN_NUM)) - 1]}"
            out[f] = {"name": f"the {stem} languages", "roman": stem, "roman_full": stem_full, "gloss": gl, "pattern": "scholarly",
                      "basis": basis_used, "by_lect": common.id if common else None,
                      "lects": sorted(x.id for x in ls), "oldest_deme": old.deme, "died_kyr": min((x.died_kyr or 0.0) for x in ls)}
        return out

    # -------------------------------------------------------------- name history (PW-1546: the taxonomy's processes)
    def note(self, p: str, process: str, **kw) -> None:
        self.history.setdefault(p, []).append({"process": process, **kw})

    def glossonym_drift(self, p: str, main, ctx: dict) -> dict | None:
        """The language named from another root than the people (GLOSSONYM_W): 'our speech', or the place it was first
        spoken in the lect's 'like' form (Hittite nešili 'in the manner of Neša' beside Hatti). None: the people's root."""
        rng = _rng(self.seed, "glossonym", p)
        kind = _pick(rng, GLOSSONYM_W)
        if kind == "same":
            return None
        _c, sp = _first(main, ("LANGUAGE", "TONGUE", "SPEAK", "MOUTH"))
        if kind == "place":
            like = (getattr(getattr(main, "lexicon", None), "affixes", {}) or {}).get("like")
            r = self.river_name(main, ctx["river"]) if ctx.get("river") is not None else None
            if r is not None and like and like[0]:
                f = _repair(main, tuple(r["form"]) + tuple(like[0]) if like[1] else tuple(like[0]) + tuple(r["form"]))
                roman = RO.title_name(_roman_form(main, f))
                return {"ipa": word_ipa(f), "roman": roman, "roman_full": RO.title_name(_roman_form(main, f, False)),
                        "gloss": f"the way of the {r['roman']} ('{r['gloss']}'): the language named after its river",
                        "pattern": "glossonym drift: a place", "lect": main.id}
        we = _word(main, "WE")
        if we is None or sp is None:
            return None
        f = _join(main, sp.form, we.form)
        roman = RO.title_name(_roman_form(main, f))
        return {"ipa": word_ipa(f), "roman": roman, "roman_full": RO.title_name(_roman_form(main, f, False)),
                "gloss": f"our {_gloss(sp.concept).lower()}: the language named apart from the people",
                "pattern": "glossonym drift: 'our speech'", "lect": main.id}

    def conquerors(self, demes: dict, peoples: dict) -> None:
        """P1: a deme of one people that shifted to a ruling people's speech, and still speaks its line, takes the rulers'
        name with chance P1_TAKE (France after the Franks, Bulgaria after the Bulgars), said with its own words."""
        latest: dict = {}
        for s in self.res.get("shifts") or []:
            if s.get("speakers") and s.get("ruler_people") and s["speakers"] != s["ruler_people"]:
                if s["deme"] not in latest or s["kyr"] < latest[s["deme"]]["kyr"]:
                    latest[s["deme"]] = s
        for d, s in sorted(latest.items()):
            l = next((x for x in self.living if x.deme == d), None)
            rp = s["ruler_people"]
            ruler = self.lects.get(s["ruler_lect"])
            if l is None or ruler is None or rp not in self.patterns or not self.inherits(l, ruler):
                continue
            if _rng(self.seed, "p1", d).random() >= P1_TAKE:
                continue
            n = self.endonym_in(l, rp, self.patterns[rp], self.ctx.get(rp) or {})
            if n is None:
                continue
            own = (demes.get(str(d)) or {}).get("name") or {}
            n = dict(n, pattern="P1", variant="conquerors",
                     gloss=f"named after their former rulers, the {rp} ({n['gloss']})",
                     plain=n["plain"] + f"; the name of the {rp}, whose speech deme {d} took up {s['kyr']:g} kyr ago")
            demes[str(d)]["name"] = _public(n)
            demes[str(d)]["name"]["was"] = own.get("roman")
            self.note(self._people(l), "P1", era_kyr=round(float(s["kyr"]), 3),
                      by=rp, deme=d, to=n["roman"], **({"from": own.get("roman")} if own.get("roman") else {}),
                      cause=f"deme {d} shifted to the {rp}'s speech and took their name")

    def rejections_and_words(self, peoples: dict) -> None:
        """P5: a people at least as numerous as its namer rejects an insulting exonym ('the mutes', 'the enemies') and asks
        for its own name. P6: after P6_KYR or more of fear or contempt, the namer's name for a people becomes an ordinary
        word of its language (vandal 'wrecker', philistine 'boor')."""
        pop = {p: float(getattr(self.main[p], "population", 0) or 0) for p in self.main}
        for subj in sorted(peoples):
            for x in peoples[subj]["exonyms"]:
                obs = x["by_people"]
                if x.get("variant") in ("mutes", "enemies") and pop.get(subj, 0) >= pop.get(obs, 0) and \
                        _rng(self.seed, "p5", obs, subj).random() < P5_REJECT:
                    x["rejected"] = True
                    self.note(subj, "P5", era_kyr=x.get("era_kyr"), by=obs, **{"from": x["roman"]},
                              to=peoples[subj]["endonym"]["roman"],
                              cause=f"'{x['gloss'].split(' (')[0]}' is an insult; the {subj} ask the {obs} for their own name")
                if x.get("valence") in ("feared", "despised") and float(x.get("era_kyr") or 0) >= P6_KYR and \
                        _rng(self.seed, "p6", obs, subj).random() < P6_WORD:
                    raid = x.get("variant") == "enemies" or x.get("valence") == "feared"
                    meaning = "a raider, a wrecker" if raid else "a boor, an uncouth person"
                    word = x["roman"].lower()
                    peoples[subj].setdefault("words", []).append(
                        {"by_people": obs, "by_lect": x.get("by_lect"), "roman": word, "ipa": x["ipa"], "meaning": meaning,
                         "plain": f"{obs} {word} '{meaning}', from their name for the {subj} (as vandal, philistine)"})
                    self.note(subj, "P6", era_kyr=x.get("era_kyr"), by=obs, **{"from": x["roman"]}, to=word,
                              cause=f"the {obs}' name for them came to mean '{meaning}'")

    def split_roots(self, peoples: dict) -> None:
        """P7: one root, split by borrowing. Related peoples whose own names share a root (cognate PEOPLE or REAL words)
        are each named after it by different neighbours, so one root names different peoples (Deutsch, Dutch, Tedesco)."""
        key: dict = {}
        for p, e in self.endonyms.items():
            m = e.get("main")
            if m is None or p not in peoples:
                continue
            main = self.main[p]
            roots = tuple(_root(w) for c in m.get("parts") or [] if (w := _word(main, c)) is not None)
            if roots and all(roots):
                key.setdefault((self.family(main), roots), []).append(p)
        for (_fam, _r), ps in sorted(key.items(), key=lambda kv: kv[1]):
            if len(ps) < 2:
                continue
            for p in ps:
                for x in peoples[p]["exonyms"]:
                    if x.get("pattern") not in ("X1", "X4"):
                        continue
                    others = sorted({(y["by_people"], q) for q in ps if q != p for y in peoples[q]["exonyms"]
                                     if y.get("pattern") in ("X1", "X4") and y["by_people"] != x["by_people"]})
                    if others:
                        x["split"] = [f"the {o} give the same root to the {q}" for o, q in others[:3]]
                if any(x.get("split") for x in peoples[p]["exonyms"]):
                    self.note(p, "P7", by=", ".join(sorted({x["by_people"] for x in peoples[p]["exonyms"] if x.get("split")})),
                              cause="their own name and a related people's share one root, and neighbours named each of them "
                                    "after it (as Deutsch and Dutch)")

    def adopted(self, peoples: dict, common, cx: dict) -> None:
        """P3 / E12: a people smaller than the Common's takes up the Common's name for it as one of its own names (Hindu,
        Indonesia), heard back through its own ears; its old endonym stays (P8, parallel names by audience)."""
        cp = self._people(common)
        cpop = float(getattr(common, "population", 0) or 0)
        for p in sorted(peoples):
            x = cx.get(p)
            if x is None or p == cp or float(getattr(self.main[p], "population", 0) or 0) >= cpop:
                continue
            if _rng(self.seed, "p3", p).random() >= P3_ADOPT:
                continue
            src = self.exo_forms.get((cp, p))
            form = _hear(src[0], self.main[p]) if src is not None else None
            if not form:
                continue
            roman = RO.title_name(_roman_form(self.main[p], form))
            peoples[p]["adopted"] = {"ipa": word_ipa(form), "roman": roman, "pattern": "E12",
                                     "gloss": f"the Common's name for them, {x['roman']} ('{x['gloss']}'), taken up as their own",
                                     "lect": self.main[p].id}
            self.note(p, "P3", by=cp, **{"from": x["roman"]}, to=roman,
                      cause="the Common's name for them, taken up beside their own (P8: parallel names by audience)")

    def landmasses(self) -> dict:
        """Landmass names from the languages (names-spelling-gaps.md item 18): coined by the first lect of the landmass's
        first settlers ('the long land', 'the white land': LAND_MODS + LAND), and as today's main lect there says it
        (inherited, or heard: P2). The world's own names (and Daniel's, PW-867) stay the display names; this is the
        native one beside them."""
        out = {}
        lms = ((getattr(self.R, "meta", {}) or {}).get("present") or {}).get("landmasses") or []
        for lm in lms:
            called = lm.get("called")
            sb = (lm.get("settled_by") or {}).get("by")
            if not called:
                continue
            on = [l for l in self.lects.values() if l.deme is not None and called in
                  ((self.R.demes[l.deme].get("place") or "") if hasattr(self.R, "demes") else "")]
            if not on:
                continue
            chain = lambda l: {l.people, *(self.line(l.people).get("parents") or [])}  # noqa: E731
            first = [l for l in on if sb and sb in chain(l)] or on
            namer = max(first, key=lambda l: (l.born_kyr, -_num(l.id), l.id))
            rng = _rng(self.seed, "landmass", called)
            head = _first(namer, ("LAND", "EARTH (SOIL)", "GROUND"))[1]
            if head is None:
                continue
            mods = [c for c in LAND_MODS if _word(namer, c) is not None]
            if mods and rng.random() < 0.7:
                m = _word(namer, mods[int(rng.integers(len(mods)))])
                form, gloss = _join(namer, head.form, m.form), f"the {_gloss(m.concept)} {_gloss(head.concept)}"
            else:
                form, gloss = tuple(head.form), f"the {_gloss(head.concept)}"
            living = [l for l in self.living if l in on]
            now = max(living, key=lambda l: (float(getattr(l, "population", 0) or 0), l.id)) if living else None
            rec = {"called": called, "ipa": word_ipa(form), "roman": RO.title_name(_roman_form(namer, form)),
                   "gloss": gloss, "named_by": namer.id, "people": namer.people, "kyr": round(float(namer.born_kyr), 3),
                   "pattern": "E6"}
            if now is not None and now is not namer:
                inh = self.inherits(now, namer)
                f2 = form if inh else _hear(form, now)
                rec["today"] = {"lect": now.id, "people": now.people, "ipa": word_ipa(f2),
                                "roman": RO.title_name(_roman_form(now, f2)),
                                "how": "inherited" if inh else f"heard from the {namer.people}, who named it first (P2)"}
            out[called] = rec
        return out

    def dishes(self, l, deme: dict, personal: dict | None) -> list:
        """Dish names (names-spelling-gaps.md item 20, PW-692): the lect's staple food named after a place (its river or
        land in the lect's 'like' form: the Ratal-ish millet), after a person (a given name: a Pavlova), and a food that
        reached it along a food route named after the people it came from (an exonym: turkey, French fries)."""
        from .texts import KIND_ORDER, NOT_A_MEAL, food_kind
        lex = getattr(l, "lexicon", None)
        if lex is None:
            return []
        words = lex.words
        crops = sorted(c for c in words if c.startswith("crop:") and len(words[c].form) and c[5:] not in NOT_A_MEAL)
        food = next((c for k in KIND_ORDER for c in crops if food_kind(c) == k), None)
        out = []
        like = (getattr(lex, "affixes", {}) or {}).get("like")
        rng = _rng(self.seed, "dish", l.id)

        def rec(kind, form, gloss, plain):
            roman = RO.title_name(_roman_form(l, form))
            return {"kind": kind, "ipa": word_ipa(form), "roman": roman, "gloss": gloss, "plain": f"{roman}, '{gloss}': {plain}"}

        if food is not None:
            fw = words[food]
            fen = _gloss(food.split(":", 1)[1].replace("_", " "))
            place = next((p for p in deme.get("places") or [] if p["kind"] in ("river", "land", "lake")), None)
            if place is not None and like and like[0]:
                from .percepts import from_ipa
                pf = from_ipa(place["ipa"])
                mod = tuple(pf) + tuple(like[0]) if like[1] else tuple(like[0]) + tuple(pf)
                out.append(rec("toponym", _join(l, fw.form, mod), f"the {place['roman']}-style {fen}",
                               f"{fen} the way it is made on the {place['roman']} (a place name + the 'like' ending)"))
            given = [g for g in (personal or {}).get("given") or [] if g.get("ipa")]
            if given:
                g = given[int(rng.integers(len(given)))]
                from .percepts import from_ipa
                out.append(rec("eponym", _join(l, fw.form, from_ipa(g["ipa"])), f"{g['roman']}'s {fen}",
                               f"{fen} named after someone called {g['roman']} ('{g['gloss']}')"))
        for r in sorted(self.res.get("food_routes") or [], key=lambda r: (r.get("concept") or "", r.get("origin_lect") or "")):
            o = self.lects.get(r.get("origin_lect"))
            if o is None or self._people(o) == self._people(l) or not any(h.get("lect") == l.id for h in r.get("hops") or []):
                continue
            c = r.get("concept")
            w = words.get(c)
            src = self.exo_forms.get((self._people(l), self._people(o)))
            if w is None or not len(w.form) or src is None:
                continue
            fen = _gloss(c.split(":", 1)[-1].replace("_", " "))
            out.append(rec("exonym", _join(l, w.form, src[0]), f"the {self._people(o)} {fen}",
                           f"{fen}, which came from the {self._people(o)}, called by the name {src[2]} given them"))
            break
        return out[:DISH_MAX]

    # -------------------------------------------------------------- driver
    def build(self) -> dict:
        peoples = {}
        demes = {}
        for p in sorted(self.main):
            pat, ctx = self.endonym_pattern(p)
            self.patterns[p] = pat
            self.ctx[p] = ctx
            main = self.main[p]
            by_lect = {}
            for l in self.by_people[p]:
                n = self.endonym_in(l, p, pat, ctx)
                if n is not None:
                    by_lect[l.id] = n
            m = by_lect.get(main.id)
            self.endonyms[p] = {"main": m, "by_lect": by_lect}
            if m is None:
                continue
            gl = m["set"]["language"]
            glossonym = {"ipa": gl["ipa"], "roman": gl["roman"], "roman_full": gl["roman_full"], "gloss": f"the speech of {m['gloss'].split(' (')[0]}",
                         "pattern": gl["how"], "lect": main.id}
            glossonym = self.glossonym_drift(p, main, ctx) or glossonym
            peoples[p] = {"endonym": _public(m), "glossonym": glossonym, "set": m["set"],
                          "by_lect": {k: {"ipa": v["ipa"], "roman": v["roman"], "roman_full": v["roman_full"], "pattern": v["pattern"], "variant": v["variant"]} for k, v in sorted(by_lect.items())},
                          "exonyms": [], "why": {k: (v if isinstance(v, (str, int, float)) else list(v) if isinstance(v, tuple) else v)
                                                for k, v in ctx.items() if k != "body"}}
        for l in self.living:
            p = self._people(l)
            n = (self.endonyms.get(p) or {}).get("by_lect", {}).get(l.id)
            demes[str(l.deme)] = {"name": _public(n), "people": p, "lect": l.id, "places": self.places(l, n)}
        from .personal import Personal
        PN = Personal(self)
        personal = {l.id: PN.for_lect_cached(l) for l in self.living}
        personal = {k: v for k, v in personal.items() if v}
        by_cell, rids = self._sites()
        if by_cell:
            for l in self.living:
                st = PN.settlements(l, by_cell, rids)
                if st:
                    demes[str(l.deme)]["settlements"] = st
            # (PW-1604: the ruins too, under the deme whose lect named them; a deme gone since keeps an entry of its own
            # with `gone`, only its people, lect and ruins: the names slot reads every `settlements`, the pages list the
            # living demes)
            sites = [s for v in by_cell.values() for s in v]
            sites.sort(key=lambda s: s["id"])
            for d, ru in sorted(PN.ruins(sites, rids).items()):
                e = demes.get(str(d))
                if e is None:
                    lid = ru[0]["lect"]
                    e = demes[str(d)] = {"gone": True, "people": self._people(self.lects[lid]), "lect": lid, "places": []}
                e["settlements"] = (e.get("settlements") or []) + ru
        self.unique_english(demes)
        habits = {l.id: PN.H.summary(l) for l in self.living if getattr(l, "lexicon", None) is not None}
        rows = ((getattr(self.R, "meta", {}) or {}).get("present") or {}).get("reputation") or {}
        # (three rounds: neighbours first, whose X1 names the misattributed X9 names and relays reuse; then the rest; then
        # the relayed rows, X4, heard from the third people's own name for the subject)
        todo = [(o, s, r) for o, subs in sorted((rows.get("rows") or {}).items()) for s, r in sorted(subs.items())
                if s in peoples and o != s]
        for rnd in (0, 1, 2):
            for obs, subj, row in todo:
                relayed = bool(row.get("borrowed_from")) and row.get("borrowed_from") in self.main
                if (rnd == 2) != relayed or (rnd < 2 and (rnd == 0) != (row.get("valence") == "neighbour")):
                    continue
                x = self.relay(obs, subj, row) if rnd == 2 else self.exonym(obs, subj, row)
                if x is None and rnd == 2:
                    x = self.exonym(obs, subj, row)
                if x is not None:
                    peoples[subj]["exonyms"].append(x)
        for p in peoples:
            peoples[p]["exonyms"].sort(key=lambda x: (x["by_people"], x.get("pattern") or ""))
        self.conquerors(demes, peoples)
        self.rejections_and_words(peoples)
        self.split_roots(peoples)
        common, why = self.common()
        cx = {}
        if common is not None:
            cp = self._people(common)
            for p in sorted(peoples):
                if p == cp:
                    continue
                row = next((x for x in peoples[p]["exonyms"] if x["by_people"] == cp), None)
                if row is None:
                    src = self.endonyms[p]["main"]
                    heard = _hear(src["form"], common)
                    row = {"ipa": word_ipa(heard), "roman": RO.title_name(_roman_form(common, heard)),
                           "roman_full": RO.title_name(_roman_form(common, heard, False)), "pattern": "X1",
                           "gloss": f"their own name {src['roman']}, as the Common says it"}
                cx[p] = {k: row.get(k) for k in ("ipa", "roman", "roman_full", "gloss", "pattern")}
        out_common = None if common is None else {"lect": common.id, "people": self._people(common), "deme": common.deme, "why": why,
                                                  "exonyms": cx}
        if common is not None:
            self.adopted(peoples, common, cx)
        for p, h in self.history.items():
            if p in peoples:
                peoples[p]["history"] = sorted(h, key=lambda x: (-(x.get("era_kyr") or 0.0), x["process"], x.get("by") or ""))
        for l in self.living:
            ds = self.dishes(l, demes.get(str(l.deme)) or {}, personal.get(l.id))
            if ds:
                demes[str(l.deme)]["dishes"] = ds
        return {"peoples": peoples, "demes": demes, "common": out_common, "scholars": self.scholars(common), "personal": personal,
                "landmasses": self.landmasses(), "habits": habits,
                "patterns": PATTERNS, "note": "PW-972: patterns from the owner's ethnonym taxonomy; forms from each lect's words "
                                              "and grammar (names.py)"}


_ROMAN_NUM = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII",
              "XVIII", "XIX", "XX", "many")


def _root(w):
    for s in reversed(w.etym):
        if s.process.split(":", 1)[0] not in ("sound_change", "borrow", "substrate", "nativize", "analogy", "accent"):
            return (s.kyr, s.lect, s.process)
    return None


def _num(lid: str) -> float:
    try:
        return float(lid.lstrip("dp").split(".")[0])
    except ValueError:
        return 0.0


def build_names(result: dict, run, rng_seed: int | None = None, landscape: dict | None = None) -> dict:
    """The `names` block of languages.json (architecture section 11). `landscape`: output.landscape_json(run) if already made
    (rivers and lakes with the demes on them, oldest first); without it a river is named by the lect living on it now."""
    seed = result.get("seed") if rng_seed is None else rng_seed
    if seed is None:
        seed = getattr(run, "seed", 0)
    _SPELL.clear()
    return _Pass(result, run, int(seed), landscape).build()


def names_for_brief(names: dict, people_id: str) -> dict | None:
    """The brief's few lines for a people: headword (romanized endonym), glossonym, two exonyms with who says them and why,
    three etymologies in plain words."""
    p = (names.get("peoples") or {}).get(people_id)
    if not p:
        return None
    e = p["endonym"]
    ex = sorted(p.get("exonyms") or [], key=lambda x: (-(x.get("strength") or 0.0), x["by_people"]))
    pick, seen = [], set()
    for x in ex:  # (two exonyms of different patterns where possible)
        if x["pattern"] not in seen:
            pick.append(x)
            seen.add(x["pattern"])
        if len(pick) == 2:
            break
    for x in ex:
        if len(pick) == 2:
            break
        if x not in pick:
            pick.append(x)
    exonyms = [{"name": x["roman"], "said_by": x["by_people"], "gloss": x["gloss"], "pattern": x["pattern"],
                "why": x.get("basis") or "", "relay": x.get("relay") or []} for x in pick]
    ety = [e["plain"]]
    ety += [x["plain"] for x in pick if x.get("plain")][:1]
    places = [pl for d in (names.get("demes") or {}).values() if d.get("people") == people_id for pl in d.get("places") or []
              if pl["kind"] in ("river", "lake")]
    places.sort(key=lambda pl: (pl.get("substrate_of") is None, -(pl.get("kyr") or 0.0), pl["roman"]))
    if places:
        ety.append(places[0]["plain"])
    else:
        g = p["glossonym"]
        ety.append(f"{g['roman']}, '{g['gloss']}' ({g['pattern']})")
    return {"headword": e["roman"], "ipa": e["ipa"], "gloss": e["gloss"], "pattern": e["pattern"],
            "glossonym": {"roman": p["glossonym"]["roman"], "gloss": p["glossonym"]["gloss"]},
            "exonyms": exonyms, "etymologies": ety[:3]}
