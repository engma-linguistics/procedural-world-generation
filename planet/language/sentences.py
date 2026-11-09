"""Grammar notes and glossed sample sentences for a living lect (round 5, surface lane).

Everything here reads one lect's languages.json record (`output.lect_json`): its typology, its live grams (form, level,
side, host), its paradigm exemplars, its lexicon and inventory. Nothing is drawn at random: every form comes from a word
or gram the lect already has, every order from a typology feature, so the sentences show what the engine's grammar
implies. Where the engine tracks no gram for a construction (a question particle, a copula, a relativizer) the form is a
lexical word the construction commonly grows from (Heine & Kuteva's paths in grammaticalization_paths.tsv), and the note
says so.

`enrich(lj)` adds two compact fields to a living lect's record:
- `grammar_notes`: [{topic, text, ex: [[form line, gloss line, English] | sentence id]}], one per topic (nouns, verbs,
  agreement, negation, questions, possession, relative clauses, copula); a sample sentence used as an example is named by
  its id rather than copied (`example` resolves it);
- `sentences`: [{id, en, w: [[form, gloss] per word], ipa, roman, q, note}], 5-10 interlinear-glossed sentences (Leipzig
  conventions: '-' between affix and stem, '=' before or after a clitic, the gloss line with the same breaks; category
  labels in capitals). `ipa` is the whole sentence after the simple joining rules, words separated by spaces, for audio;
  `q` is 1 for a yes/no question (rising intonation).

Joining (`join`): at a morpheme or clitic boundary, a vowel meeting a vowel takes a glide the lect has (j after a front
unrounded vowel, w after a rounded or back one, else ʔ), and a nasal before a stop or affricate takes the stop's place
(when the lect has that nasal). Nothing is joined across word boundaries.

A sentence whose words the lexicon lacks is left out, so the set degrades gracefully as concepts come and go (each slot
names fallbacks, and concepts the core lane is adding, such as HAVE, are tried first)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import grammar as GR
from .percepts import from_ipa, is_V, word_ipa

# ---- Leipzig glosses ------------------------------------------------------------------------------------------------------

ABBR = {"PL": "PL", "DU": "DU", "DEF": "DEF", "INDEF": "INDF", "GEN": "GEN", "LOC": "LOC", "ABL": "ABL", "ALL": "ALL",
        "DAT": "DAT", "ACC": "ACC", "ERG": "ERG", "INS": "INS", "COM": "COM", "DIM": "DIM", "AGENT": "AGT",
        "PLACE": "PLACE", "PAST": "PST", "RECPST": "PST.RCT", "FUT": "FUT", "PERF": "PRF", "PROG": "PROG",
        "IPFV": "IPFV", "HAB": "HAB", "EVID.DIR": "DIR", "EVID.REP": "REP", "NEG": "NEG", "CAUS": "CAUS",
        "PASS": "PASS", "REFL": "REFL", "Q": "Q", "REL": "REL", "COP": "COP", "CLF": "CLF", "ITER": "ITER",
        "INTS": "INTS", "CONT": "CONT",
        # grammar phase B: mood, the inclusive subject marker, object and possessor series
        "IMP": "IMP", "HORT": "HORT", "OBLG": "OBLG", "APPR": "APPR", "1PL.INCL": "1PL.INCL",
        **{f"{p}.O": f"{p}.OBJ" for p in GR.PERSON_FNS}, **{f"{p}.POSS": f"{p}.POSS" for p in GR.PERSON_FNS},
        # grammar phase C: constructions, valence, switch-reference, voice
        "COMP": "COMP", "TOP": "TOP", "FOC": "FOC", "APPL": "APPL", "RECP": "RECP", "ANTIP": "ANTIP", "SS": "SS",
        "DS": "DS", "AV": "AV", "PV": "PV", "PIV": "PIV",
        # grammar phase D: distance, remoteness, aspect, mirativity, politeness, obviation
        "DIST": "DIST", "REMPST": "PST.REM", "INCH": "INCH", "COMPL": "COMPL", "RPT": "RPT", "MIR": "MIR", "HON": "HON",
        "OBV": "OBV"}
#: abbreviations that are not in the Leipzig list, explained on the pages
EXTRA_ABBR = {"PST.RCT": "recent past", "DIR": "direct (witnessed) evidential", "REP": "reported evidential",
              "AGT": "agent noun", "CL": "noun class", "CLF": "classifier", "ANIM": "animate", "INAN": "inanimate",
              "ITER": "iterative (reduplication)", "INTS": "intensive (reduplication)",
              "CONT": "continuous (reduplication)", "HORT": "hortative ('let us')", "OBLG": "obligative ('must')",
              "APPR": "apprehensive ('lest')", "INCL": "inclusive (you among us)", "EXCL": "exclusive (not you)",
              "SS": "same subject as the next clause", "DS": "different subject from the next clause",
              "AV": "actor voice (the doer is the pivot)", "PV": "patient voice (the undergoer is the pivot)",
              "PIV": "pivot (the phrase the voice picks out)", "PST.REM": "remote past", "INCH": "inceptive ('begin to')",
              "COMPL": "completive ('finish, fully')", "RPT": "repetitive ('again')", "MIR": "mirative (news, surprise)",
              "HON": "honorific (respect for the subject)", "OBV": "obviative (the less central third person)",
              "POL": "polite (a plural or third person used to address one person)", "PROX": "near (proximal)"}
#: English gloss of a pronoun concept
PRON = {"I": "1SG", "THOU": "2SG", "HE OR SHE OR IT": "3SG", "WE": "1PL", "YOU": "2PL", "THEY": "3PL",
        "WE (INCLUSIVE)": "1PL"}
CASE_NAME = {"GEN": "genitive", "LOC": "locative", "ABL": "ablative", "ALL": "allative", "DAT": "dative",
             "ACC": "accusative", "ERG": "ergative", "INS": "instrumental", "COM": "comitative",
             **{f: GR.FUNCS[f].gloss.split(" (")[0] for f in GR.LOCAL_CASE + GR.PERIPHERAL_CASE}}
CASE_EN = {"GEN": "of the {n}", "LOC": "in the {n}", "ABL": "from the {n}", "ALL": "to the {n}", "DAT": "to/for the {n}",
           "ACC": "the {n} (as object)", "ERG": "the {n} (as doer)", "INS": "with (using) the {n}", "COM": "with the {n}",
           "INE": "in the {n}", "ILL": "into the {n}", "ELA": "out of the {n}", "SUPE": "on the {n}", "SUBL": "onto the {n}",
           "DEL": "off the {n}", "PERL": "through the {n}", "PRIV": "without the {n}", "TRANSL": "into (becoming) the {n}"}
TAM_ORDER = ("PAST", "RECPST", "PERF", "FUT", "PROG", "IPFV", "HAB", "REMPST", "COMPL", "INCH", "RPT")
#: English verb forms: base, 3sg, past, participle, -ing
EN_VERB = {
    "SEE": ("see", "sees", "saw", "seen", "seeing"), "EAT": ("eat", "eats", "ate", "eaten", "eating"),
    "DRINK": ("drink", "drinks", "drank", "drunk", "drinking"), "SLEEP": ("sleep", "sleeps", "slept", "slept", "sleeping"),
    "SIT": ("sit", "sits", "sat", "sat", "sitting"), "LIE (REST)": ("lie", "lies", "lay", "lain", "lying"),
    "HIT": ("hit", "hits", "hit", "hit", "hitting"), "HOLD": ("hold", "holds", "held", "held", "holding"),
    "CARRY": ("carry", "carries", "carried", "carried", "carrying"), "COOK": ("cook", "cooks", "cooked", "cooked", "cooking"),
    "KILL": ("kill", "kills", "killed", "killed", "killing"), "HEAR": ("hear", "hears", "heard", "heard", "hearing"),
    "KNOW": ("know", "knows", "knew", "known", "knowing"), "KNOW (SOMETHING)": ("know", "knows", "knew", "known", "knowing"),
    "SING": ("sing", "sings", "sang", "sung", "singing"), "LAUGH": ("laugh", "laughs", "laughed", "laughed", "laughing"),
    "HUNT": ("hunt", "hunts", "hunted", "hunted", "hunting"), "GO": ("go", "goes", "went", "gone", "going"),
    "HAVE": ("have", "has", "had", "had", "having"), "WALK": ("walk", "walks", "walked", "walked", "walking"),
    "COME": ("come", "comes", "came", "come", "coming"), "CRY": ("cry", "cries", "cried", "cried", "crying"),
    # (round 5, finish lane: the WOLD verbs the templates now prefer)
    "BRING": ("bring", "brings", "brought", "brought", "bringing"), "FIND": ("find", "finds", "found", "found", "finding"),
    "BUILD": ("build", "builds", "built", "built", "building"), "GIVE": ("give", "gives", "gave", "given", "giving"),
    "RUN": ("run", "runs", "ran", "run", "running"), "SWIM": ("swim", "swims", "swam", "swum", "swimming"),
    "CLIMB": ("climb", "climbs", "climbed", "climbed", "climbing"), "CATCH": ("catch", "catches", "caught", "caught", "catching"),
    "FOLLOW": ("follow", "follows", "followed", "followed", "following"), "SELL": ("sell", "sells", "sold", "sold", "selling"),
    "BUY": ("buy", "buys", "bought", "bought", "buying"), "DANCE": ("dance", "dances", "danced", "danced", "dancing"),
    "SHOUT": ("shout", "shouts", "shouted", "shouted", "shouting"),
    "CARVE": ("carve", "carves", "carved", "carved", "carving"),
    "TAKE": ("take", "takes", "took", "taken", "taking"), "CUT": ("cut", "cuts", "cut", "cut", "cutting"),
    "BITE": ("bite", "bites", "bit", "bitten", "biting"), "FLY": ("fly", "flies", "flew", "flown", "flying"),
}
EN_NOUN = {"CHILD (YOUNG HUMAN)": "child", "LIE (REST)": "lie", "FLESH OR MEAT": "meat", "SMOKE (EXHAUST)": "smoke",
           "STONE OR ROCK": "stone", "kin:mother": "mother", "kin:brother": "brother", "kin:sister": "sister"}
EN_PLURAL = {"CHILD (YOUNG HUMAN)": "children", "FISH": "fish", "PERSON": "people", "MAN": "men", "WOMAN": "women",
             "SHEEP": "sheep", "GOOSE": "geese", "OX": "oxen"}


def en(concept: str) -> str:
    c = str(concept)
    if c in EN_NOUN:
        return EN_NOUN[c]
    return c.split(" (")[0].split(" OR ")[0].split(":")[-1].lower().replace("_", " ")


def lgloss(concept: str) -> str:
    """A lexical gloss: lowercase, multi-word meanings joined with '.' (Leipzig rule 4)."""
    return en(concept).replace(" ", ".")


# ---- the lect, read from its json record ----------------------------------------------------------------------------------

class View:
    """One lect's grammar and words, as the sentence builder needs them."""

    def __init__(self, lj: dict):
        self.lj = lj
        self.t = dict(lj.get("typology") or {})
        self.lex = lj.get("lexicon") or {}
        inv = lj.get("inventory") or {}
        self.cons = set(inv.get("consonants") or [])
        self.vows = set(inv.get("vowels") or [])
        self.grams: dict[str, dict] = {}
        for g in lj.get("grams") or []:
            if not g.get("form_ipa") or (g.get("level") or 0) >= GR.LOST:
                continue
            cur = self.grams.get(g["function"])
            if cur is None or _better(g, cur):
                self.grams[g["function"]] = g
        self.cells = {}
        par = lj.get("paradigms") or {}
        for key in ("nouns", "verbs"):
            for r in (par.get(key) or {}).get("rows") or []:
                self.cells[r["concept"]] = r
        self.classes = _classes(lj, self.t, self.grams)
        # the lect's live phonological rules (phonology.py, sound lane): word-level ones run over affixed words, phrase-level
        # ones across word joins
        from . import phonology as PH
        self.stress = inv.get("stress")
        self.rules = PH.rules_from_json(lj.get("phonology"))
        #: the number a reader sees for each class: 1..n in the engine's order (the engine never reuses a lost class's
        #: number, so its own numbers can have gaps)
        self.cl_num = {f: i + 1 for i, (_k, _g, f) in enumerate(sorted((self.classes or {}).get("classes") or [],
                                                                         key=lambda c: c[0]))}
        self.proc = dict(lj.get("processes") or {})   # (grammar phase A: split ergativity, reduplication)
        self.extra: list = []   # (notes a clause adds: concord, second-position clitics; `finish` takes them)

    def w(self, *concepts) -> str | None:
        """The first of the concepts the lexicon has."""
        for c in concepts:
            if c in self.lex and self.lex[c].get("ipa"):
                return c
        return None

    def ipa(self, c: str) -> str:
        return self.lex[c]["ipa"]

    def pair(self, *options) -> tuple[str, str] | tuple[None, None]:
        """The first (verb, object) the lexicon has both words for, from (verb concepts, object concepts) options in order
        of preference (a verb only meets objects that suit it: hear the thunder, not see it)."""
        for verbs, objs in options:
            a, b = self.w(*verbs), self.w(*objs)
            if a and b:
                return a, b
        return None, None

    def g(self, fn: str) -> dict | None:
        return self.grams.get(fn)

    def hd_final(self) -> bool:
        return self.t.get("head_direction", "final") == "final"

    def order(self) -> str:
        wo = self.t.get("word_order", "SOV")
        if wo not in ("SOV", "SVO", "VSO", "VOS", "OVS", "OSV"):
            return "SOV" if self.hd_final() else "SVO"
        return wo

    def ov(self) -> bool:
        o = self.order()
        return o.index("O") < o.index("V")

    def before(self, feature: str, first: str) -> bool:
        """Does the modifier stand before the noun (mixed/other: by head direction)?"""
        v = self.t.get(feature)
        if v in (None, "mixed", "other"):
            return self.hd_final()
        return v == first

    def segs(self):
        out = []
        for x in sorted(self.cons) + sorted(self.vows):
            try:
                out += from_ipa(x)
            except Exception:  # noqa: BLE001
                continue
        return out


def _better(a: dict, b: dict) -> bool:
    """Grammar.gram: a bound gram (affix or fused) before a free or clitic one, then the youngest."""
    ab, bb = (a.get("level") or 0) >= GR.AFFIX, (b.get("level") or 0) >= GR.AFFIX
    if ab != bb:
        return ab
    return (a.get("born_kyr") or 0) < (b.get("born_kyr") or 0)


#: a class gram's source concept -> its group, for records written before `classes` was stored
_SOURCE_GROUP = {c: g for g, cs in GR.CLASS_SOURCES.items() for c in cs if g not in ("masculine", "feminine", "animate",
                                                                                     "inanimate")}


def _classes(lj: dict, t: dict, grams: dict) -> dict:
    """{"kind", "classes": [[k, group, function]]} from the record (`classes`, written by output.grammar_json), else
    rebuilt from the CLASS grams' sources and the gender feature."""
    c = lj.get("classes")
    if c:
        return c
    fns = sorted((f for f in grams if f.startswith("CLASS:")), key=lambda f: int(f.split(":")[1]))
    if not fns:
        return {}
    kind = {"sex": "sex", "animacy": "animacy"}.get(t.get("gender"), "classes")
    out = []
    for f in fns:
        src = (grams[f].get("source") or ["?"])[0]
        if kind == "sex":
            grp = "feminine" if src == "WOMAN" else "masculine" if src in ("MAN", "HE") else "abstract"
        elif kind == "animacy":
            grp = "animate" if src in ("PERSON", "ANIMAL") else "inanimate" if src in ("STONE", "THAT") else "abstract"
        else:
            grp = _SOURCE_GROUP.get(src, "abstract")
        out.append([int(f.split(":")[1]), grp, f])
    return {"kind": kind, "classes": out}


def class_of(v: View, concept: str) -> tuple[str, str] | None:
    """(CLASS:k function, gloss label) of a noun, the way grammar._class_for picks it."""
    cs = v.classes
    if not cs or not cs.get("classes"):
        return None
    grp = GR.semantic_group(concept)
    kind = cs.get("kind")
    if kind == "sex":
        want = "feminine" if str(concept).upper() in GR._FEMALE or str(concept) in GR._FEMALE else "masculine"
    elif kind == "animacy":
        want = "animate" if grp in ("person", "animal") else "inanimate"
    else:
        want = grp
    by = {g: (k, f) for k, g, f in cs["classes"]}
    hit = by.get(want)
    if hit is None:
        k, f = default_class(cs, grp)
        hit = (k, f)
    want = next(g for g, kf in by.items() if kf == hit)
    k, f = hit
    k = v.cl_num.get(f, k)
    if grp_of(cs, f) != _want(cs, concept):
        return f, f"CL{k}"   # (the noun's own class is missing; the engine falls back on another, so no gender label)
    lab = {"masculine": "M", "feminine": "F", "animate": "ANIM", "inanimate": "INAN"}.get(want, f"CL{k}")
    if kind in ("sex", "animacy") and want == "abstract":
        lab = "N" if kind == "sex" else "INAN"
    return f, lab


def default_class(cs: dict, grp: str | None = None) -> tuple:
    """(k, function) of the class a noun of semantic group `grp` takes when its own group has no class (as
    grammar._class_for falls back, grammar.fallback_groups): an animate noun the person or animal class first, then the
    abstract, tools, plant or animal class, the first the lect has, else its last class. With no group: the inanimate
    default."""
    by = {g: (k, f) for k, g, f in cs["classes"]}
    hit = next((by[a] for a in (GR.fallback_groups(grp) if grp else GR.CLASS_FALLBACK) if a in by), None)
    if hit is None:
        k, _g, f = cs["classes"][-1]
        hit = (k, f)
    return hit


def grp_of(cs: dict, fn: str) -> str | None:
    return next((g for _k, g, f in cs["classes"] if f == fn), None)


def _want(cs: dict, concept: str) -> str:
    grp = GR.semantic_group(concept)
    if cs.get("kind") == "sex":
        return "feminine" if str(concept).upper() in GR._FEMALE or str(concept) in GR._FEMALE else "masculine"
    if cs.get("kind") == "animacy":
        return "animate" if grp in ("person", "animal") else "inanimate"
    return grp


# ---- words and joining ----------------------------------------------------------------------------------------------------

_GLIDE_FRONT, _GLIDE_BACK = "j", "w"
_NASAL_AT = {0: "m", 1: "n̪", 2: "n", 3: "n", 4: "ɲ", 5: "ŋ", 6: "ɴ"}


def _segs(x: str):
    try:
        s = from_ipa(x)
    except Exception:  # noqa: BLE001
        return None
    return s if word_ipa(s) == x else None


def join(left: str, right: str, cons: set) -> tuple[str, str]:
    """The simple joining rules at one morpheme or clitic boundary (see the module doc)."""
    a, b = _segs(left), _segs(right)
    if not a or not b:
        return left, right
    x, y = a[-1], b[0]
    if is_V(x) and is_V(y):
        glide = _GLIDE_BACK if (x.round or x.back >= 3) and _GLIDE_BACK in cons else \
            _GLIDE_FRONT if _GLIDE_FRONT in cons and not x.round else \
            _GLIDE_BACK if _GLIDE_BACK in cons else "ʔ" if "ʔ" in cons else None
        if glide:
            return left, glide + right
        return left, right
    if x.kind == "C" and x.manner == 3 and y.kind == "C" and y.manner in (0, 1) and not y.double and x.place != y.place:
        n = _NASAL_AT.get(y.place)
        if n and n in cons and not y.retroflex:
            return word_ipa(a[:-1]) + n, right
    return left, right


@dataclass
class Morph:
    form: str
    gloss: str
    sep: str = "-"       # the break between this morph and the stem side ('-' affix, '=' clitic)
    rank: int = 0        # SLOT_ORDER rank: inner morphs first
    fn: str | None = None
    redup: bool = False  # a reduplicant: joined to the stem with no glide (a copy, not an affix meeting a stem)


@dataclass
class Word:
    form: str
    gloss: str
    concept: str | None = None
    pre: list = field(default_factory=list)
    post: list = field(default_factory=list)
    fns: list = field(default_factory=list)      # bound gram functions on the word (for paradigm cells)
    infix: tuple | None = None                   # (form, gloss) of an infix inside the stem (grammar C)

    def add(self, form: str, gloss: str, level: int, side: str, fn: str | None = None) -> "Word":
        m = Morph(form, gloss, "=" if level == GR.CLITIC else "-", _rank(fn) + (100 if level == GR.CLITIC else 0), fn)
        (self.pre if side == "pre" else self.post).append(m)
        if fn and level >= GR.AFFIX:
            self.fns.append(fn)
        return self

    def ordered(self) -> list:
        """The morphs left to right as Morph objects, None standing for the stem."""
        return sorted(self.pre, key=lambda m: m.rank)[::-1] + [None] + sorted(self.post, key=lambda m: m.rank)

    def morphs(self) -> list[tuple[str, str, str, bool]]:
        """[(form, gloss, break before it, is a clitic)] left to right; a prefix's break stands after it."""
        pre = sorted(self.pre, key=lambda m: m.rank)[::-1]
        post = sorted(self.post, key=lambda m: m.rank)
        items = [(m.form, m.gloss, m.sep == "=") for m in pre] + [(self.form, self.gloss, False)] + \
            [(m.form, m.gloss, m.sep == "=") for m in post]
        breaks = [""] + [m.sep for m in pre] + [m.sep for m in post]
        return [(f, g, b, c) for (f, g, c), b in zip(items, breaks)]


def _rank(fn: str | None) -> int:
    if not fn:
        return 0
    if fn.startswith("CLASS"):
        return GR.SLOT_ORDER.index("class")
    if "+" in fn:
        fn = fn.split("+")[-1]
    try:
        return GR.SLOT_ORDER.index(GR.func_info(fn).slot)
    except Exception:  # noqa: BLE001
        return len(GR.SLOT_ORDER)


def render_word(v: View, w: Word) -> tuple[str, str, str]:
    """(form line with breaks, gloss line with the same breaks, surface IPA). A noun or verb whose bound grams make a
    stored paradigm cell takes the cell's form (the engine's own, with any alternation sound change left in it)."""
    _portmanteaus(v, w)
    ms = w.morphs()
    objs = w.ordered()
    forms = [m[0] for m in ms]
    cell, cov = _cell(v, w)
    si = len(w.pre)
    if cov is None:
        inner = [i for i, m in enumerate(ms) if not m[3]]
    else:   # (a stored cell for the inner markers only: the outer ones are added to it, as a speaker builds on it)
        inner = [i for i, o in enumerate(objs) if o is None or (o.sep == "-" and o.fn in cov)]
        if inner != list(range(inner[0], inner[-1] + 1)):
            cell, cov = None, None
    fused = False
    if cell is not None:
        pieces = cell.split("-")
        if len(pieces) == len(inner) and si in inner and pieces[inner.index(si)] != w.form:
            if cov is None:
                fused = True   # (the stem itself alternates in this cell: its morph boundaries are not reliable)
            else:
                cell = None
        elif len(pieces) == len(inner):
            for i, x in zip(inner, pieces):
                forms[i] = x
        else:
            cell = None
    if fused:   # (the stored cell's stem piece is not the dictionary form: segment it from the forms themselves)
        pieces = _resegment(v, w, cell.split("-"), inner.index(si))
        for i, x in zip(inner, pieces):
            forms[i] = x
        disp = [x if x else ZERO for x in forms]
        fl, gl = disp[0], ms[0][1]
        for i in range(1, len(ms)):
            fl += ms[i][2] + disp[i]
            gl += ms[i][2] + ms[i][1]
        return fl, gl, "".join(forms)
    for i in range(len(forms) - 1):
        if cell is not None and i in inner and i + 1 in inner:
            continue   # (inside a stored cell the engine's own forms stand)
        if any(o is not None and o.redup for o in objs[i:i + 2]):
            continue   # (a reduplicant is a copy of the stem: no glide between them, Tagalog a-alis)
        forms[i], forms[i + 1] = join(forms[i], forms[i + 1], v.cons)
    disp, glo, surf = list(forms), [m[1] for m in ms], list(forms)
    if w.infix:   # (Leipzig rule 9: s<um>ulat, gloss <AV>write)
        si = len(w.pre)
        seg = _segs(forms[si]) or []
        k = next((i for i, x in enumerate(seg) if is_V(x)), 0)
        if 0 < k < len(seg):
            on, rest = word_ipa(seg[:k]), word_ipa(seg[k:])
            disp[si] = f"{on}<{w.infix[0]}>{rest}"
            surf[si] = on + w.infix[0] + rest
            glo[si] = f"<{w.infix[1]}>{glo[si]}"
    fl, gl = disp[0], glo[0]
    for i in range(1, len(ms)):
        fl += ms[i][2] + disp[i]
        gl += ms[i][2] + glo[i]
    surface = "".join(surf)
    if len(ms) > 1 and getattr(v, "rules", None):   # (the lect's live rules at its morpheme joins: phonology.py)
        from . import phonology as PH
        pre, f = _segs("".join(surf[:len(w.pre)])) or (), _segs(surface)
        if f:
            try:
                g = PH.apply_word(tuple(f), [r for r in v.rules if r[1] != "stem"], v.stress, stem_index=len(pre),
                                  stem_len=len(_segs(surf[si]) or ()))  # (stem-level: word-making only; the stem keeps a vowel)
                if g and g != tuple(f):
                    surface = word_ipa(g)
            except Exception:  # noqa: BLE001 - a rule that cannot run leaves the plain join
                pass
    return fl, gl, surface


ZERO = "∅"   # (Leipzig: a marker with no sound in this word)


def _resegment(v: View, w: Word, pieces: list, k: int) -> list:
    """The pieces of a stored cell whose stem piece is not the dictionary form (polish lane: the page called these
    'merged with the stem' even where the word was the bare stem or the stem plus a plain ending). With one marker on
    one side, the cell is split at the dictionary stem when it begins (suffix) or ends (prefix) with it: the marker's
    shape here is the rest (empty: no sound here, shown ∅; kobold eie 'go.3SG'). Otherwise the cell's own pieces stand,
    the stem in its changed shape, and the note says what the stem became (frost giant sɛw 'dog', ʃi-dɛw 'LOC-dog')."""
    whole, stem = "".join(pieces), w.form
    if len(pieces) == 2 and k == 0 and whole.startswith(stem):
        return [stem, whole[len(stem):]]
    if len(pieces) == 2 and k == 1 and whole.endswith(stem):
        return [whole[:len(whole) - len(stem)], stem]
    if pieces[k] != stem:
        # (PW-1537 R5: Welsh mutation was cited for every change, also glides and cut finals at a word's end; the
        # parallel now follows where the stem changed)
        p = pieces[k]
        head = next((i for i, (x, y) in enumerate(zip(stem, p)) if x != y), min(len(stem), len(p)))
        like = ("as Welsh cath 'cat', y gath 'the cat'" if head == 0 else
                "as German Tag [taːk] 'day', Tage [taːɡə] 'days'" if len(p) >= len(stem) else
                "as French petit [pəti] beside petite [pətit]")
        v.extra.append(f"the stem {stem} is {p} in this form (a sound change at the join, {like})")
    return pieces


def _portmanteaus(v: View, w: Word) -> None:
    """Two bound markers the lect has fused into one ending (a portmanteau gram 'A+B', grammar C) are shown as that one
    morph, glossed A.B (Leipzig rule 4)."""
    for fn, g in v.grams.items():
        if "+" not in fn:
            continue
        a, b = fn.split("+", 1)
        for side in ("pre", "post"):
            ms = w.pre if side == "pre" else w.post
            ma = next((m for m in ms if m.fn == a and m.sep == "-"), None)
            mb = next((m for m in ms if m.fn == b and m.sep == "-"), None)
            if ma is None or mb is None:
                continue
            ms.remove(ma)
            ms.remove(mb)
            ms.append(Morph(_form_for(v, g, fn, w.concept), f"{ma.gloss}.{mb.gloss}", "-", mb.rank, fn))


def _cell(v: View, w: Word) -> tuple[str | None, set | None]:
    """(the stored paradigm cell for the word's bound markers, None) when the paradigm has that cell; else (the cell for
    its innermost markers, the set of those markers) when it has one, so that the outer markers are added to the stored
    form (storm giant n-aʁu 'M-dog' and ŋi-n-aʁu 'PL-M-dog', not ŋi-nɛ-jaʁu); else (None, None)."""
    if not w.concept or not w.fns:
        return None, None
    row = v.cells.get(w.concept)
    if not row or (row.get("cells") or {}).get("lemma", {}).get("ipa") != w.form:
        return None, None
    fns = sorted(w.fns, key=lambda f: (_rank(f), f))
    for k in range(len(fns), 0, -1):
        key = ".".join(sorted(fns[:k], key=lambda f: (_rank(f), f)))
        seg = (row.get("segmented") or {}).get(key)
        if not seg:
            c = (row.get("cells") or {}).get(key)
            seg = None if not c else c.get("ipa")
        if seg:
            return seg, (None if k == len(fns) else set(fns[:k]))
    return None, None


# ---- phrases ------------------------------------------------------------------------------------------------------------

@dataclass
class NP:
    words: list            # list[Word], in order
    head: int              # index of the noun
    person: str = "3SG"    # agreement person of the phrase
    notes: list = field(default_factory=list)
    cls: tuple | None = None   # (CLASS:k, label) of the head noun when its class marker is bound (for concord)


def gram_word(g: dict, fn: str) -> Word:
    return Word(g["form_ipa"], ABBR.get(fn, fn))


def attach(v: View, words: list, idx: int, fn: str, label: str | None = None) -> bool:
    """Put gram `fn` on words[idx] if it is bound (clitic or affix); a free gram is inserted beside it. Returns False when
    the lect has no such gram."""
    g = v.g(fn)
    lab = label or ABBR.get(fn, fn)
    if g is None:
        return _stem_change(v, words[idx], fn, lab)
    lv = g.get("level") or 0
    side = g.get("side") or "post"
    form = _form_for(v, g, fn, words[idx].concept)
    if lv >= GR.AFFIX and side == "pre" and (v.proc.get("infix") or {}).get("fn") == fn and words[idx].concept:
        seg = _segs(words[idx].form) or []
        if seg and not is_V(seg[0]) and any(is_V(x) for x in seg):
            words[idx].infix = (form, lab)
            return True
    if lv >= GR.CLITIC:
        words[idx].add(form, lab, min(lv, GR.AFFIX) if lv >= GR.AFFIX else GR.CLITIC, side, fn)
    else:
        words.insert(idx if side == "pre" else idx + 1, Word(form, lab))
    return True


def _form_for(v: View, g: dict, fn: str, concept) -> str:
    """A marker's form on a word: the second inflection class's form for the words of that class (grammar C)."""
    if g.get("alt_ipa") and GR.iclass_member((v.proc.get("iclass") or {}).get(fn), concept):
        return g["alt_ipa"]
    return g["form_ipa"]


def _stem_change(v: View, w: Word, fn: str, lab: str) -> bool:
    """A category the lect marks only by a change in the stem (grammar C): the stem's last vowel that the rule names
    takes its new value, glossed with a backslash (Leipzig rule 7: mouse\\PL)."""
    vmap = dict((v.proc.get("stem_change") or {}).get(fn) or [])
    seg = _segs(w.form) if vmap and w.concept else None
    if not seg:
        return False
    for i in range(len(seg) - 1, -1, -1):
        x = word_ipa(seg[i:i + 1])
        if is_V(seg[i]) and x in vmap:
            new = from_ipa(vmap[x])
            w.form = word_ipa(list(seg[:i]) + list(new) + list(seg[i + 1:]))
            w.gloss += "\\" + lab
            return True
    return False


def noun_phrase(v: View, concept: str, det: str | None = None, adj: str | None = None, num: str | None = None,
                poss: "NP | None" = None, plural: bool = False, dem: str | None = None, inalienable: bool = False,
                gloss: str | None = None, dual: bool = False) -> NP:
    """Dem Num Adj N, mirrored for postnominal modifiers (Greenberg's Universal 20 orders); the possessor outermost."""
    notes = []
    n = Word(v.ipa(concept), gloss or lgloss(concept), concept)
    cl = class_of(v, concept)
    bound_cl = cl is not None and (v.g(cl[0]) or {}).get("level", 0) >= GR.CLITIC
    if bound_cl:
        attach(v, [n], 0, cl[0], cl[1])
    conc = set(v.proc.get("concord") or []) if bound_cl else set()
    core = [n]
    if dual and v.g("DU") is not None:
        attach(v, core, 0, "DU")
    elif plural:
        pl = v.g("PL")
        if pl is not None and ((pl.get("level") or 0) >= GR.AFFIX or not num):
            attach(v, core, 0, "PL")
        elif pl is not None:
            notes.append("no plural marker after a numeral (the marker is not yet obligatory)")
    head = next(i for i, x in enumerate(core) if x is n)
    pre, post = [], []
    if adj:
        a = Word(v.ipa(adj), lgloss(adj), adj)
        if "adj" in conc:   # (concord: the adjective takes the noun's class marker, grammar C)
            attach(v, [a], 0, cl[0], cl[1])
            notes.append("the adjective agrees with the noun's class")
        (pre if v.before("adjective", "AN") else post).append(a)
    if num:
        nw = [Word(v.ipa(num), lgloss(num), num)]
        clf = _classifier(v, concept)
        if clf is not None:
            nw.append(clf)
        if v.before("numeral", "NumN"):
            pre.insert(0, nw)
        else:
            post.append(nw)
    if dem:
        d = Word(v.ipa(dem), lgloss(dem), dem)
        if "dem" in conc:
            attach(v, [d], 0, cl[0], cl[1])
            notes.append("the demonstrative agrees with the noun's class")
        if v.before("demonstrative", "DemN"):
            pre.insert(0, d)
        else:
            post.append(d)
    words: list = []
    for x in pre:
        words += x if isinstance(x, list) else [x]
    head = len(words) + head
    words += core
    for x in post:
        words += x if isinstance(x, list) else [x]
    np_ = NP(words, head, "3PL" if plural else "3SG", notes, cl if bound_cl else None)
    if det == "DEF":
        _np_gram(v, np_, "DEF")
    elif det == "INDEF":
        _np_gram(v, np_, "INDEF")
    if poss is not None:
        gen = None if inalienable and v.t.get("alienability") == "yes" else v.g("GEN")
        pw = list(poss.words)
        pm = v.g(poss.person.split(".")[0] + ".POSS")
        if pm is not None and (pm.get("level") or 0) >= GR.CLITIC:   # (grammar B: head-marked possession)
            attach(v, np_.words, np_.head, poss.person.split(".")[0] + ".POSS")
            np_.head = next(i for i, w in enumerate(np_.words) if w is n)
            notes.append("the possessed noun carries the possessor's person marker")
            if _is_pron(poss) and v.t.get("pro_drop") == "yes":
                pw = []   # (the marker says whose: the pronoun is dropped, as Turkish ev-im 'my house')
                notes.append("the possessor pronoun is dropped")
        if gen is not None and pw:
            tmp = NP(pw, poss.head)
            _np_gram(v, tmp, "GEN")
            pw = tmp.words
        if v.before("genitive", "GN"):
            np_.head += len(pw)
            np_.words = pw + np_.words
        else:
            np_.words = np_.words + pw
        if inalienable and v.t.get("alienability") == "yes":
            notes.append("kin are inalienably possessed: no genitive marker" + (
                "" if pm is not None and (pm.get("level") or 0) >= GR.CLITIC else
                ", the possessor stands beside the noun with no marker"))
    return np_


def _classifier(v: View, concept: str) -> Word | None:
    if v.t.get("numeral_classifiers") != "yes":
        return None
    cl = class_of(v, concept)
    if cl is None:
        return None
    g = v.g(cl[0])
    if g is None or (g.get("level") or 0) != GR.FREE:
        return None
    return Word(g["form_ipa"], "CLF")


def _np_gram(v: View, np_: NP, fn: str, label: str | None = None) -> bool:
    """A noun-phrase gram (article, case): bound ones go on the edge word of its side, free ones stand at that edge."""
    g = v.g(fn)
    lab = label or ABBR.get(fn, fn)
    if g is None:
        return _stem_change(v, np_.words[np_.head], fn, lab) if np_.words else False
    side = g.get("side") or "post"
    lv = g.get("level") or 0
    host = g.get("host") or "NP"
    if host == "N":
        return attach(v, np_.words, np_.head, fn, label)
    form = _form_for(v, g, fn, np_.words[np_.head].concept)
    if lv >= GR.CLITIC:
        idx = 0 if side == "pre" else len(np_.words) - 1
        if lv >= GR.AFFIX:
            idx = np_.head   # an affix stays on the noun
        np_.words[idx].add(form, lab, GR.AFFIX if lv >= GR.AFFIX else GR.CLITIC, side, fn)
    else:
        w = Word(form, lab)
        if side == "pre":
            np_.words.insert(0, w)
            np_.head += 1
        else:
            np_.words.append(w)
    return True


def pronoun(v: View, concept: str) -> NP | None:
    if not v.w(concept):
        return None
    gl = PRON.get(concept, lgloss(concept))
    if concept == "WE (INCLUSIVE)":
        gl = "1PL.INCL"
    elif concept == "WE" and v.w("WE (INCLUSIVE)"):
        gl = "1PL.EXCL"
    return NP([Word(v.ipa(concept), gl, concept)], 0, PRON.get(concept, "3SG"))


def oblique(v: View, np_: NP, fn: str, word_concepts: tuple[str, ...]) -> tuple[NP, str] | None:
    """A case-marked or adpositional phrase: the lect's gram for `fn` if it has one, else an adposition from a function
    word (IN, AT, WITH), on the side the adposition order gives."""
    if v.g(fn) is not None:
        _np_gram(v, np_, fn)
        g = v.g(fn)
        what = {0: "an adposition", 1: "a case clitic", 2: "a case suffix" if g.get("side") == "post" else "a case prefix",
                3: "a case ending" if g.get("side") == "post" else "a case prefix"}[min(3, g.get("level") or 0)]
        return np_, f"{ABBR.get(fn, fn)} is {what}"
    c = v.w(*word_concepts)
    if c is None:
        return None
    adp = v.t.get("adposition")
    pre = adp == "pre" or (adp not in ("pre", "post") and not v.hd_final())
    w = Word(v.ipa(c), lgloss(c), c)
    if pre:
        np_.words.insert(0, w)
        np_.head += 1
    else:
        np_.words.append(w)
    return np_, f"'{en(c)}' as a {'preposition' if pre else 'postposition'} (there is no {CASE_NAME.get(fn, fn)} case)"


# ---- the verb -----------------------------------------------------------------------------------------------------------

def verb(v: View, concept: str, person: str | None = None, tam: str | None = None, neg: bool = False,
         gloss: str | None = None, redup: bool = False, voice: str | None = None,
         mood: str | None = None) -> tuple[list, int, list]:
    """The verb with its grams: (words, index of the verb, notes). Bound grams go on the verb, free ones (auxiliaries,
    particles) beside it on their side, inner ones nearest. `redup`: the lect's reduplication process (a copy of the
    stem, innermost); `voice`: a valence gram (PASS)."""
    notes = []
    vw = Word(v.ipa(concept), gloss or lgloss(concept), concept)
    words = [vw]
    rd = v.proc.get("redup")
    if redup and rd:
        red = word_ipa(GR.reduplicant(tuple(from_ipa(vw.form)), rd["shape"], rd["side"]))
        vw.add(red, ABBR[rd["fn"]], GR.AFFIX, rd["side"])   # (productive: a copy of today's stem, not the stored cell)
        (vw.pre if rd["side"] == "pre" else vw.post)[-1].redup = True
    if voice:
        attach(v, words, words.index(vw), voice)
    if tam:
        attach(v, words, words.index(vw), tam)
    if mood:
        attach(v, words, words.index(vw), mood)
    if person:
        g = v.g(person)
        if g is not None and (g.get("level") or 0) >= GR.CLITIC:
            attach(v, words, words.index(vw), person)
            notes.append(f"the verb carries the subject's {person} marker")
        elif g is None and _stem_change(v, vw, person, person):
            notes.append(f"the subject ({person}) is shown by the stem's vowel")
    if neg:
        neg_gram(v, words, vw, notes)
    return words, words.index(vw), notes


def neg_gram(v: View, words: list, vw: Word, notes: list) -> None:
    g = v.g("NEG")
    if g is not None and (g.get("level") or 0) >= GR.CLITIC:
        attach(v, words, words.index(vw), "NEG")
        notes.append(f"negation is {_how(g)}")
        return
    form = g["form_ipa"] if g is not None else (v.ipa(v.w("NOT")) if v.w("NOT") else None)
    if form is None:
        return
    nv = v.t.get("negation", "preverbal")
    w = Word(form, "NEG")
    w.concept = "_neg_" + nv
    if nv in ("preverbal", "clause_initial"):
        words.insert(0, w)
    else:
        words.append(w)
    notes.append(f"negation is a free word ({nv.replace('_', ' ')})")


# ---- the clause ---------------------------------------------------------------------------------------------------------

def _animate(np_: NP) -> bool:
    """Is the phrase's head a person, an animal or a pronoun (high on the animacy hierarchy)?"""
    c = np_.words[np_.head].concept if np_.words else None
    if c is None or c in PRON:
        return True
    return GR.semantic_group(str(c)) in ("person", "people", "animal")


def _is_pron(np_: NP | None) -> bool:
    return np_ is not None and np_.words[np_.head].concept in PRON


def flagging(v: View, S: NP | None, O: NP | None, tam: str | None = None) -> tuple[bool, bool]:
    """(ERG on the transitive subject, ACC on the object) by alignment. A split lect (both markers live) divides them as
    its grammar chose (`processes.split`): by person, pronouns accusative and nouns ergative (Dyirbal); by aspect, the
    ergative in the perfective or past clause and the accusative elsewhere (Hindi)."""
    al = v.t.get("alignment", "neutral")
    acc, erg = v.g("ACC") is not None, v.g("ERG") is not None
    if acc and v.proc.get("dom") and O is not None and not _animate(O):
        acc = False   # (differential object marking, phase D: only animate objects take the accusative)
    if al == "nom-acc":
        return False, acc
    if al == "erg-abs":
        return erg and S is not None, False
    if al == "split":
        if v.proc.get("split") == "aspect":
            past = tam in GR.SPLIT_ASPECT or tam in ("REMPST", "RECPST")   # (a graded past is a past too)
            return erg and past and S is not None, acc and not past
        return erg and S is not None and not _is_pron(S), acc and _is_pron(O)
    return False, False


def clause(v: View, S: NP | None, Vw: tuple, O: NP | None = None, X: NP | None = None, transitive: bool = True,
           tam: str | None = None) -> list:
    """Order S, O and the verb complex by the basic word order (free order: by head direction, and the note says so); an
    oblique X stands before the verb in OV lects and after the object in VO ones. Case by alignment (`flagging`): ACC on
    the object, ERG on the transitive subject, a split lect by person or aspect. Clause-edge negators move to the edge."""
    words, _vi, _n = Vw
    if transitive and O is not None:
        e, a = flagging(v, S, O, tam)
        if a:
            _np_gram(v, O, "ACC")
        if e:
            _np_gram(v, S, "ERG")
        object_marker(v, words, words[_vi] if words else None, O.person)
    if words:
        _verb_concord(v, words[_vi], S)
    parts = {"S": S.words if S else [], "O": O.words if O else [], "V": words}
    seq = []
    for ch in v.order():
        if ch == "V" and X is not None and v.ov():
            seq.append(X.words)
        seq.append(parts[ch])
        if ch == ("O" if v.order().index("O") > v.order().index("V") else "V") and X is not None and not v.ov():
            seq.append(X.words)
    out = [w for p in seq for w in p]
    # clause-initial / clause-final negators
    for w in list(out):
        if w.concept == "_neg_clause_initial":
            out.remove(w)
            out.insert(0, w)
        elif w.concept == "_neg_clause_final":
            out.remove(w)
            out.append(w)
    if words and v.proc.get("second"):
        _second_position(v, out, words[_vi])
    return out


def _verb_concord(v: View, vw: Word, S: NP | None) -> None:
    """Subject concord (grammar C): where the verb agrees in class, a noun subject's class marker stands in the verb's
    third-person slot (Swahili m-tu a-li-kuja, ki-tabu ki-li-anguka: the class, not the person, is marked)."""
    if S is None or S.cls is None or "verb" not in (v.proc.get("concord") or []) or S.person not in ("3SG", "3PL"):
        return
    fn, lab = S.cls
    g = v.g(fn)
    if g is None:
        return
    for ms in (vw.pre, vw.post):
        for m in list(ms):
            if m.fn in ("3SG", "3PL"):
                ms.remove(m)
                if m.fn in vw.fns:
                    vw.fns.remove(m.fn)
    vw.add(g["form_ipa"], lab, min(max(g.get("level") or 0, GR.CLITIC), GR.AFFIX), g.get("side") or "pre", fn)
    v.extra.append("the verb agrees with the subject's noun class (subject concord)")


def _second_position(v: View, out: list, vw: Word) -> None:
    """Wackernagel clitics (grammar C): the verb's clitics follow the clause's first word."""
    if not out or out[0] is vw and not vw.pre:
        return
    moved = []
    for ms in (vw.pre, vw.post):
        for m in list(ms):
            if m.sep == "=" and m.fn and (m.fn in GR.FUNCS or "+" in m.fn) and GR.func_info(m.fn).host[0] == "V":
                ms.remove(m)
                moved.append(m)
    if not moved:
        return
    host = out[0]
    for m in moved:
        host.post.append(Morph(m.form, m.gloss, "=", m.rank + 200, m.fn))
    v.extra.append("the verb's clitics stand in second position, after the first word of the clause")


def object_marker(v: View, words: list, vw: "Word | None", person: str) -> bool:
    """The verb's object agreement (grammar B): the object's person marker when the lect has bound it (clitic or
    tighter; a free one is still a pronoun)."""
    fn = person.split(".")[0] + ".O"
    g = v.g(fn)
    if vw is None or g is None or (g.get("level") or 0) < GR.CLITIC or vw not in words:
        return False
    attach(v, words, words.index(vw), fn)
    return True


def subject_marker(v: View, person: str) -> str:
    """The subject series function for a person: the inclusive 'we' takes its own marker when the lect has bound one."""
    if person == "1PL.INCL":
        g = v.g("1PL.INCL")
        return "1PL.INCL" if g is not None and (g.get("level") or 0) >= GR.CLITIC else "1PL"
    return person


_VERB_CLITIC = re.compile(r"a clitic (?:before|after) the verb(?: phrase)?")


def _second_fix(v: View, text: str) -> str:
    """Where the verb's clitics stand in second position (grammar C), a verb clitic sits after the clause's first word,
    whatever its old side: the notes say so (dragonborn: 'a clitic after the verb' on the first word)."""
    if not v.proc.get("second") or not text:
        return text
    return _VERB_CLITIC.sub("a clitic in second position (after the first word of the clause)", text)


_CARRIES = re.compile(r"the verb carries the subject's (\S+) marker")


def _claims_absent(note: str, gloss: str) -> bool:
    """Does a note name a subject marker the glossed words do not show (a noun subject's class marker took the
    person marker's place: subject concord)? Notes are kept to what the forms show."""
    m = _CARRIES.search(note)
    return bool(m) and re.search(rf"(^|[-=.\s<]){re.escape(m.group(1))}($|[-=.\s>])", gloss) is None


def haplology(v: View, words: list) -> list:
    """PW-1537 R1: a free marker still identical to the word it grew from does not stand beside that word ('that COP'
    ɡbiːnaf ɡbiːnaf, 'ACC take' ʁa‼ ʁa‼): one form serves both, glossed for both (morphological haplology, the
    repeated-morph constraint: English the boys', not *the boys's; Stemberger 1981, Menn & MacWhinney 1984)."""
    out: list = []
    for w in words:
        p = out[-1] if out else None
        if (p is not None and p.form == w.form and not (p.pre or p.post or w.pre or w.post or p.infix or w.infix)
                and (p.concept is None) != (w.concept is None) and w.form):
            lex, gram = (w, p) if p.concept is None else (p, w)
            out[-1] = Word(lex.form, f"{lex.gloss}.{gram.gloss}", lex.concept)
            v.extra.append(f"the {gram.gloss} marker, still the same as the word it came from, is not said again "
                           f"beside it: one {lex.form} serves both (haplology, as English the boys', not *the boys's)")
            continue
        out.append(w)
    return out


def finish(v: View, sid: str, en_text: str, words: list, note: list, q: bool = False) -> dict:
    words = haplology(v, words)
    rows, surf = [], []
    for w in words:
        fl, gl, s = render_word(v, w)
        rows.append([fl, gl])
        surf.append(s)
    if getattr(v, "rules", None) and len(surf) > 1:   # (phrase-level live rules across word joins: phonology.py)
        from . import phonology as PH
        phr = [r for r in v.rules if r[1] in ("phrase", "phonetic")]
        fs = [_segs(x) for x in surf]
        if phr and all(fs):
            try:
                fs = [tuple(f) for f in fs]
                gs = PH.apply_phrase(fs, phr, v.stress)
                surf = [word_ipa(g) if g != f else x for x, f, g in zip(surf, fs, gs)]
            except Exception:  # noqa: BLE001
                pass
    ipa = " ".join(surf)
    roman = book_spelling(v.lj, surf)
    out = {"id": sid, "en": en_text, "w": rows, "ipa": ipa, "roman": roman}
    if q:
        out["q"] = 1
    gl_all = " ".join(r[1] for r in rows)
    note = [x for x in note if not _claims_absent(x, gl_all)]
    nt = _second_fix(v, "; ".join(x for x in dict.fromkeys(list(note) + v.extra) if x))
    v.extra = []
    if nt:
        out["note"] = nt
    return out


_ORTH: dict = {}


def orthography(lj: dict):
    """The lect's spelling (romanize.Orthography) read from its record: its phonemes, its allophones spelled as their
    phonemes, its book folds ranked by token counts in its lexicon (the plan output.py uses on the engine's lect), so a
    sentence is spelled as the pages spell the lect's words."""
    from . import romanize as RO
    from .percepts import parse_segment
    k = id(lj)
    if k in _ORTH and _ORTH[k][0] is lj:
        return _ORTH[k][1]
    inv = lj.get("inventory") or {}
    allo = {}
    for a in inv.get("allophones") or []:
        if isinstance(a, dict):
            x = parse_segment(a.get("ipa", ""))
            if x is not None:
                allo[x] = (parse_segment(a["of"]) if a.get("of") else None, a.get("test"))
    counts: dict = {}
    for e in (lj.get("lexicon") or {}).values():
        try:
            for x in from_ipa(e.get("ipa") or ""):
                counts[x] = counts.get(x, 0) + 1
        except Exception:  # noqa: BLE001
            continue
    segs = {x for x in (parse_segment(y) for y in inv.get("consonants", []) + inv.get("vowels", [])) if x is not None}
    o = RO.Orthography(segs | set(counts), allo, counts, tuple(lj.get("orth") or ()) or None)
    if len(_ORTH) > 64:
        _ORTH.clear()
    _ORTH[k] = (lj, o)
    return o


def book_spelling(lj: dict, words: list[str]) -> str:
    """Words (IPA) in the lect's book spelling, the spelling the pages show for its words."""
    try:
        o = orthography(lj)
    except Exception:  # noqa: BLE001
        return " ".join(words)
    out = []
    for w in words:
        try:
            out.append(o.word(from_ipa(w), book=True))
        except Exception:  # noqa: BLE001
            out.append(w)
    return " ".join(out)


def _order_note(v: View) -> str:
    wo = v.t.get("word_order")
    if wo == "free":
        return f"word order is free; shown as {v.order()} (head-{v.t.get('head_direction', 'final')})"
    return f"{v.order()} order"


def _vf(c: str, i: int) -> str:
    return EN_VERB.get(c, (en(c), en(c) + "s", en(c) + "ed", en(c) + "ed", en(c) + "ing"))[i]


def _tam(v: View) -> str | None:
    return next((f for f in TAM_ORDER if v.g(f) is not None), None)


def _tam_en(fn: str | None, c: str, third: bool = True) -> str:
    """English for a verb under a TAM gram (third person subject)."""
    if fn in ("PAST", "RECPST"):
        return _vf(c, 2) if fn == "PAST" else "just " + _vf(c, 2)
    if fn == "PERF":
        return ("has " if third else "have ") + _vf(c, 3)
    if fn == "FUT":
        return "will " + _vf(c, 0)
    if fn == "PROG":
        return ("is " if third else "am ") + _vf(c, 4)
    if fn == "IPFV":   # (ongoing or repeated, past or present: English has no one form for it)
        return (_vf(c, 1) if third else _vf(c, 0)) + " (ongoing or repeated)"
    if fn == "HAB":
        return ("usually " + _vf(c, 1)) if third else "usually " + _vf(c, 0)
    if fn == "REMPST":
        return _vf(c, 2) + " long ago"
    if fn == "COMPL":
        return ("has " if third else "have ") + _vf(c, 3) + " completely"
    if fn == "INCH":
        return ("begins" if third else "begin") + " to " + _vf(c, 0)
    if fn == "RPT":
        return (_vf(c, 1) if third else _vf(c, 0)) + " again"
    return _vf(c, 1) if third else _vf(c, 0)


def _the(v: View) -> str | None:
    return "DEF" if v.g("DEF") is not None else None


def _a(v: View) -> str | None:
    return "INDEF" if v.g("INDEF") is not None else None


# ---- the sentences ------------------------------------------------------------------------------------------------------

def s_transitive(v: View) -> dict | None:
    S, Vc, O = v.w("WOMAN", "MAN", "PERSON"), v.w("SEE", "HOLD", "CARRY", "HIT", "EAT"), v.w("DOG", "BIRD", "FISH", "STONE")
    if not (S and Vc and O):
        return None
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, "3SG")
    words = clause(v, s, vw, o)
    return finish(v, "transitive", f"The {en(S)} {_vf(Vc, 1)} the {en(O)}.", words, [_order_note(v)] + vw[2] + s.notes)


def s_locative(v: View) -> dict | None:
    S, Vc, L = v.w("DOG", "CHILD (YOUNG HUMAN)", "BIRD"), v.w("SLEEP", "SIT", "LIE (REST)"), v.w("HOUSE", "CAMP", "VILLAGE",
                                                                                                    "CAVE", "FOREST")
    A = v.w("BIG", "SMALL", "OLD")
    if not (S and Vc and L):
        return None
    s = noun_phrase(v, S, _the(v), adj=A)
    M = v.w("RUN", "WALK", "GO", "COME") if v.g("ALL") is not None else None
    if M:   # (a lect with an allative shows it: motion to a place, the motion verbs of the WOLD list)
        x = oblique(v, noun_phrase(v, L, _the(v)), "ALL", ("AT",))
        Vc, prep = M, "to"
    else:
        x = oblique(v, noun_phrase(v, L, _the(v)), "LOC", ("IN", "AT"))
        prep = "in"
    if x is None:
        return None
    vw = verb(v, Vc, "3SG")
    words = clause(v, s, vw, None, x[0], transitive=False)
    adj = f"{en(A)} " if A else ""
    return finish(v, "locative", f"The {adj}{en(S)} {_vf(Vc, 1)} {prep} the {en(L)}.", words,
                  [x[1], f"adjective {'before' if v.before('adjective', 'AN') else 'after'} the noun"] + vw[2])


def s_tense(v: View) -> dict | None:
    S = v.w("MAN", "PERSON", "HUNTER")
    Vc, O = v.pair((("BUILD",), ("BOAT", "RAFT", "HOUSE")), (("CARVE",), ("BOW", "PADDLE", "BOWL")),
                   (("EAT", "COOK", "KILL", "CARRY"), ("FISH", "FLESH OR MEAT", "BIRD", "EGG")))
    if not (S and Vc and O):
        return None
    fn = _tam(v)
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, "3SG", fn)
    words = clause(v, s, vw, o, tam=fn)
    g = v.g(fn) if fn else None
    note = (f"{ABBR[fn]} is {_how(g)}"
            if g else "no tense or aspect marker: time is left to context")
    en_v = _tam_en(fn, Vc) if fn else _vf(Vc, 2)
    return finish(v, "tense", f"The {en(S)} {en_v} the {en(O)}.", words, [note] + vw[2])


def _q_particle(v: View) -> str | None:
    c = v.w("IF")
    return v.ipa(c) if c else None


def s_polar(v: View) -> dict | None:
    Vc, O = v.pair((("HEAR",), ("THUNDER", "VOICE")), (("SEE",), ("RAINBOW", "FIRE", "SMOKE (EXHAUST)", "RIVER", "SUN")),
                   (("HEAR",), ("RIVER", "FIRE")))
    S = pronoun(v, "THOU")
    if not (Vc and O and S):
        return None
    o = noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, "2SG")
    if vw[2] and v.t.get("pro_drop") == "yes":
        S = None
    pq = v.t.get("polar_question", "intonation")
    words = clause(v, S, vw, o)
    notes = vw[2][:] + (["the subject pronoun is dropped"] if S is None else [])
    qp = _q_particle(v)
    qg = v.g("Q")
    if qg is not None:   # (grammar C: the lect's own question gram)
        lv = qg.get("level") or 0
        if lv >= GR.CLITIC:
            attach(v, words, words.index(vw[0][vw[1]]), "Q")
            notes.append(f"the question marker is {_how(qg)} ({qg['form_ipa']}, {_src(v, qg)})")
        else:
            w = Word(qg["form_ipa"], "Q")
            words.insert(0, w) if qg.get("side") == "pre" else words.append(w)
            notes.append(f"a {'clause-initial' if qg.get('side') == 'pre' else 'clause-final'} question particle "
                         f"({qg['form_ipa']}, {_src(v, qg)})")
    elif pq in ("initial_particle", "final_particle") and qp:
        w = Word(qp, "Q")
        if pq == "initial_particle":
            words.insert(0, w)
        else:
            words.append(w)
        notes.append(f"a {'clause-initial' if pq == 'initial_particle' else 'clause-final'} question particle, the word "
                     f"for 'if, whether' (as Russian li is both)")
    elif pq == "verb_morph" and qp:
        vword = vw[0][vw[1]]
        side = "post" if v.ov() else "pre"
        vword.add(_first_syllable(qp), "Q", GR.CLITIC, side)
        notes.append("the verb takes a question clitic, cut down from the word for 'if, whether'")
    else:
        notes.append("a yes/no question by rising intonation alone")
    return finish(v, "polar", f"Do you {_vf(Vc, 0)} the {en(O)}?", words, notes, q=True)


def _first_syllable(ipa: str) -> str:
    s = _segs(ipa)
    if not s:
        return ipa
    return GR.ipa(GR.first_syllable(tuple(s)))


def s_content(v: View) -> dict | None:
    S, Vc, Q = v.w("CHILD (YOUNG HUMAN)", "BOY", "GIRL", "PERSON"), v.w("BRING", "FIND", "EAT", "HOLD", "SEE"), v.w("WHAT")
    if not (S and Vc and Q):
        return None
    s = noun_phrase(v, S, _the(v))
    o = NP([Word(v.ipa(Q), "what", Q)], 0)
    vw = verb(v, Vc, "3SG")
    words = clause(v, s, vw, o)
    if v.t.get("wh_in_situ") != "yes":
        qws = [w for w in words if any(w is x for x in o.words)]   # (the whole phrase: a free case word goes with it)
        words = qws + [w for w in words if not any(w is x for x in qws)]
        note = "the question word moves to the front" + (" with its case marker" if len(qws) > 1 else "")
    else:
        note = "the question word stays where the object stands"
    return finish(v, "content", f"What does the {en(S)} {_vf(Vc, 0)}?", words, [note] + vw[2])


def s_negation(v: View) -> dict | None:
    Vc, O = v.pair((("DRINK",), ("MILK", "SOUP", "WATER", "BLOOD")), (("EAT",), ("MEAT", "FLESH OR MEAT", "EGG")),
                   (("SEE",), ("WATER", "BLOOD")))
    S = pronoun(v, "I")
    if not (Vc and O and S) or (v.g("NEG") is None and not v.w("NOT")):
        return None
    o = noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, "1SG", neg=True)
    if any("subject's" in n for n in vw[2]) and v.t.get("pro_drop") == "yes":
        S = None
    words = clause(v, S, vw, o)
    return finish(v, "negation", f"I do not {_vf(Vc, 0)} the {en(O)}.", words,
                  vw[2] + (["the subject pronoun is dropped"] if S is None else []))


def _my(v: View) -> NP | None:
    return pronoun(v, "I")


def s_possession(v: View) -> dict | None:
    K, T = v.w("MOTHER", "kin:mother", "FATHER"), v.w("BOAT", "BASKET", "POT", "DOG", "HOUSE", "KNIFE")
    me = _my(v)
    if not (K and T and me):
        return None
    pp = v.t.get("predicative_possession", "other")
    owner = noun_phrase(v, K, poss=me, inalienable=True)
    thing = noun_phrase(v, T, _a(v))
    notes = list(owner.notes)
    if pp == "have":
        hv = v.w("HAVE", "HOLD", "TAKE")
        if hv is None:
            return None
        vw = verb(v, hv, "3SG", gloss="have")
        words = clause(v, owner, vw, thing)
        notes.append("a 'have' verb" + ("" if hv == "HAVE" else f" (the word for '{en(hv)}')"))
    elif pp == "locational":
        x = oblique(v, owner, "LOC", ("AT", "IN"))
        if x is None:
            return None
        words = x[0].words + cop_phrase(v, thing)
        notes += [f"locational possession ('at my {en(K)} (is) a {en(T)}')", x[1]]
    else:
        x = oblique(v, thing, "COM", ("WITH",))
        if x is None:
            return None
        words = owner.words + cop_phrase(v, x[0])
        notes += [f"possession with 'with' ('my {en(K)} (is) with a {en(T)}')", x[1]]
    return finish(v, "possession", f"My {en(K)} has a {en(T)}.", words, notes)


def s_number(v: View) -> dict | None:
    K, N = v.w("OLDER BROTHER", "YOUNGER SIBLING", "BROTHER", "SISTER", "kin:brother", "SON"), v.w("THREE", "FOUR", "TWO")
    Vc, O = v.pair((("CATCH",), ("FISH", "RABBIT", "BIRD")), (("SELL", "BUY"), ("SHEEP", "GOOSE", "POT", "BASKET")),
                   (("SEE", "HUNT", "HOLD"), ("BIRD", "FISH", "DOG", "DEER")))
    me = _my(v)
    if not (K and Vc and N and O and me):
        return None
    s = noun_phrase(v, K, poss=me, inalienable=True)
    o = noun_phrase(v, O, num=N, plural=True)
    vw = verb(v, Vc, "3SG")
    words = clause(v, s, vw, o)
    notes = s.notes + o.notes + [f"numeral {'before' if v.before('numeral', 'NumN') else 'after'} the noun"]
    if any(w.gloss == "CLF" for w in o.words):
        notes.append("a numeral classifier follows the numeral")
    return finish(v, "number", f"My {en(K)} {_vf(Vc, 1)} {en(N)} {EN_PLURAL.get(O, en(O) + 's')}.", words, notes)


def _copula(v: View) -> tuple[str, str] | None:
    """(form, note) of the copula when the lect has one (typology `copula`): no gram is tracked, so it is the word a
    copula commonly comes from (G056: a third-person or demonstrative pronoun > copula, as Hebrew hu, Mandarin shi)."""
    g = v.g("COP")
    if g is not None:   # (grammar C: the lect's own copula gram)
        return g["form_ipa"], f"the copula is {_how(g)} ({g['form_ipa']}, {_src(v, g)})"
    if v.t.get("copula") != "yes":
        return None
    c = v.w("HE OR SHE OR IT", "THAT", "SIT", "STAND")
    if c is None:
        return None
    src = en(c) if c != "HE OR SHE OR IT" else "he, she, it"
    return v.ipa(c), (f"the copula is the word for '{src}' (a pointing word or pronoun often becomes 'is', as Hebrew hu "
                      f"and Mandarin shi did)" if c in ("HE OR SHE OR IT", "THAT") else f"the copula is the word for '{src}'")


def _cop_bound(v: View) -> bool:
    return (v.g("COP") or {}).get("level", 0) >= GR.CLITIC


def cop_phrase(v: View, pred: NP) -> list:
    """The predicate with the copula: a bound copula on the predicate's head (Turkish -dIr), a free one in the verb's
    place (after the predicate in OV lects, before it in VO)."""
    cop = _copula(v)
    if cop is None:
        return list(pred.words)
    if _cop_bound(v):   # (on the edge of the whole predicate phrase, not inside it: 'with boat'=COP, Turkish evde-dir)
        ws = list(pred.words)
        g = v.g("COP") or {}
        attach(v, ws, (len(ws) - 1 if g.get("side") != "pre" else 0) if len(ws) > 1 else pred.head, "COP")
        return ws
    cw = [Word(cop[0], "COP")]
    return pred.words + cw if v.ov() else cw + pred.words


def s_copula(v: View) -> dict | None:
    D, S, P = v.w("THAT", "THIS"), v.w("MAN", "PERSON", "WOMAN"), v.w("MERCHANT", "SOLDIER", "TEACHER", "HUNTER", "FISHER",
                                                                                  "HERDER", "SMITH", "FIGHTER", "THIEF")
    if not (S and P):
        return None
    s = noun_phrase(v, S, dem=D)
    pred = noun_phrase(v, P, _a(v))
    cop = _copula(v)
    notes = []
    if cop:
        words = s.words + cop_phrase(v, pred)
        notes.append(cop[1] + ("" if _cop_bound(v) else f", in the verb's place ({'after' if v.ov() else 'before'} the "
                                                           "predicate)"))
    else:
        words = s.words + pred.words
        notes.append("no copula: subject and predicate noun stand side by side")
    notes.append(f"demonstrative {'before' if v.before('demonstrative', 'DemN') else 'after'} the noun")
    return finish(v, "copula", f"{(en(D) if D else 'the').capitalize()} {en(S)} is a {en(P)}.", words, notes)


def relative(v: View, head: str, rc_verb: str, det: str | None) -> tuple[NP, str]:
    """The noun with a subject relative clause 'the N who V-s': NRel with a relativizer from 'that' (G055, as English
    that, German der); RelN with the clause before the noun, verb-final, no relativizer, or a genitive linker if the lect
    has a free or clitic one (as Mandarin de); other: a correlative ('who sings, that woman')."""
    rv = verb(v, rc_verb, "3SG")[0]
    hn = noun_phrase(v, head, det)
    kind = v.t.get("relative", "NRel")
    that = v.w("THAT")
    rg = v.g("REL")
    if kind == "NRel" and rg is not None:   # (grammar C: the lect's own relativizer gram)
        if (rg.get("level") or 0) >= GR.CLITIC:
            attach(v, rv, next(i for i, w in enumerate(rv) if w.concept == rc_verb), "REL")
            rel = []
        else:
            rel = [Word(rg["form_ipa"], "REL")]
        np_ = NP(hn.words + rel + rv, hn.head)
        return np_, f"relative clause after the noun; the relativizer is {_how(rg)} ({rg['form_ipa']}, {_src(v, rg)})"
    if kind == "NRel":
        rel = [Word(v.ipa(that), "REL")] if that else []
        np_ = NP(hn.words + rel + rv, hn.head)
        return np_, "relative clause after the noun" + (", introduced by the word for 'that' (as English that and German der grew from a pointing word)"
                                                         if that else "")
    if kind == "RelN":
        gen = v.g("GEN")
        link = [Word(gen["form_ipa"], "REL")] if gen is not None and (gen.get("level") or 0) <= GR.CLITIC else []
        np_ = NP(rv + link + hn.words, len(rv) + len(link) + hn.head)
        return np_, "relative clause before the noun" + (" with the genitive word as a linker" if link else
                                                          ", no relativizer")
    who = v.w("WHO")
    corr = ([Word(v.ipa(who), "who", who)] if who else []) + rv
    dem = [Word(v.ipa(that), "that", that)] if that else []
    np_ = NP(corr + dem + hn.words, len(corr) + len(dem) + hn.head)
    return np_, f"a correlative: 'who {_vf(rc_verb, 1)}, that {en(head)}' (the relative clause comes first, with 'who', and " \
                f"'that' picks the noun up again)"


def s_relative(v: View) -> dict | None:
    Vc, H, R = v.w("KNOW", "KNOW (SOMETHING)", "SEE"), v.w("WOMAN", "MAN", "PERSON"), v.w("DANCE", "SING", "LAUGH", "SHOUT", "HUNT", "CRY")
    S = pronoun(v, "I")
    if not (Vc and H and R and S):
        return None
    o, note = relative(v, H, R, _the(v))
    vw = verb(v, Vc, "1SG")
    if vw[2] and v.t.get("pro_drop") == "yes":
        S = None
    words = clause(v, S, vw, o)
    return finish(v, "relative", f"I know the {en(H)} who {_vf(R, 1)}.", words, [note] + vw[2])


# ---- grammar phase A sentences (2026-11-08): give, imperative, passive, serial verbs, reduplication, split, clusivity -----

def s_give(v: View) -> dict | None:
    """A ditransitive: the recipient in the dative (case or adposition) when the lect has a DAT gram, else a serial
    'give' after the theme when the lect serializes, else a double object (both bare)."""
    S, G_, T, R = v.w("WOMAN", "MAN", "PERSON"), v.w("GIVE"), v.w("FISH", "FLESH OR MEAT", "EGG", "STONE"), \
        v.w("CHILD (YOUNG HUMAN)", "BOY", "GIRL", "MAN")
    if not (S and G_ and T and R) or R == S:
        return None
    s, o, r = noun_phrase(v, S, _the(v)), noun_phrase(v, T, _a(v)), noun_phrase(v, R, _the(v))
    en_text = f"The {en(S)} gives the {en(R)} {'an' if en(T)[0] in 'aeiou' else 'a'} {en(T)}."
    if v.g("DAT") is not None:
        x = oblique(v, r, "DAT", ())
        vw = verb(v, G_, "3SG")
        return finish(v, "give", en_text, clause(v, s, vw, o, x[0]), [x[1] + ", on the recipient"] + vw[2])
    if v.t.get("serial_verbs") == "yes" and v.w("TAKE"):
        return _serial(v, "give", S, ("TAKE", T), (G_, R), en_text,
                       "no dative: a serial construction, 'take the thing, give (it to) the person'")
    vw = verb(v, G_, "3SG")
    words = clause(v, s, vw, o, r)
    return finish(v, "give", en_text, words, ["double object: theme and recipient both unmarked"] + vw[2])


def s_imperative(v: View) -> dict | None:
    """A command: the verb with the lect's imperative marker (IMP) when it has one, else the bare stem (the commonest
    imperative in the world's languages: WALS 70A); no subject either way."""
    Vc, O = v.pair((("EAT", "DRINK"), ("FISH", "WATER", "FLESH OR MEAT")), (("TAKE", "CARRY", "HOLD"), ("STONE", "STICK")))
    if not (Vc and O):
        return None
    o = noun_phrase(v, O, _the(v))
    if flagging(v, None, o)[1]:
        _np_gram(v, o, "ACC")   # (the object keeps its case in a command, as Latin cape librum)
    words, vi, _n = verb(v, Vc, mood="IMP")
    om = object_marker(v, words, words[vi], o.person)
    seq = (o.words + words) if v.ov() else (words + o.words)
    g = v.g("IMP")
    note = (f"the imperative is marked: {_how(g)} ({g['form_ipa']}, {_src(v, g)}); no subject" if g else
            "the imperative is the bare verb stem, with no subject and no subject or tense marker")
    if om:
        note += "; the verb still marks its object"
    return finish(v, "imperative", f"{_vf(Vc, 0).capitalize()} the {en(O)}!", seq, [note])


def s_hortative(v: View) -> dict | None:
    """'Let us eat the fish!' with the lect's hortative marker (HORT; from 'let, leave', 'give', 'come' or 'go')."""
    g = v.g("HORT")
    Vc, O = v.pair((("EAT",), ("FISH", "FLESH OR MEAT")), (("DRINK",), ("WATER", "MILK")), (("GO",), ("HOUSE", "RIVER")))
    if g is None or not (Vc and O):
        return None
    o = noun_phrase(v, O, _the(v))
    if flagging(v, None, o)[1]:
        _np_gram(v, o, "ACC")
    words, vi, _n = verb(v, Vc, subject_marker(v, "1PL.INCL") if v.w("WE (INCLUSIVE)") else "1PL", mood="HORT")
    object_marker(v, words, words[vi], o.person)
    seq = (o.words + words) if v.ov() else (words + o.words)
    return finish(v, "hortative", f"Let us {_vf(Vc, 0)} the {en(O)}!", seq,
                  [f"the hortative ('let us') is {_how(g)} ({g['form_ipa']}, {_src(v, g)})"])


def s_object(v: View) -> dict | None:
    """'The woman sees you.': the verb agrees with its object as well as its subject (Swahili a-ku-ona), where the lect
    has bound object markers."""
    if not any((v.g(f) or {}).get("level", 0) >= GR.CLITIC for f in GR.OBJ_FNS):
        return None
    S, Vc = v.w("WOMAN", "MAN", "PERSON"), v.w("SEE", "HEAR", "HIT")
    o = next((pronoun(v, c) for c in ("THOU", "I", "THEY") if v.w(c) and
              (v.g(PRON[c] + ".O") or {}).get("level", 0) >= GR.CLITIC), None)
    if not (S and Vc and o):
        return None
    s = noun_phrase(v, S, _the(v))
    vw = verb(v, Vc, "3SG")
    words = clause(v, s, vw, o)
    who = {"2SG": "you", "1SG": "me", "3PL": "them"}[o.person]
    return finish(v, "object", f"The {en(S)} {_vf(Vc, 1)} {who}.", words,
                  [f"the verb agrees with its object too ({ABBR[o.person + '.O']})"] + vw[2])


def s_passive(v: View) -> dict | None:
    g = v.g("PASS")
    S, Vc = v.w("FISH", "DOG", "BIRD", "STONE"), v.w("SEE", "EAT", "CARRY", "HIT", "KILL")
    if g is None or not (S and Vc):
        return None
    s = noun_phrase(v, S, _the(v))
    vw = verb(v, Vc, "3SG", voice="PASS")
    words = clause(v, s, vw, None, None, transitive=False)
    return finish(v, "passive", f"The {en(S)} is {_vf(Vc, 3)}.", words,
                  [f"the passive is {_how(g)} ({g['form_ipa']}, {_src(v, g)}); the doer is left out"] + vw[2])


def _serial(v: View, sid: str, S: str, v1: tuple, v2: tuple, en_text: str, note: str) -> dict:
    """S V1 O1 V2 (O2) as one clause with one subject: VO lects put each object after its verb, OV lects before; only
    the first verb carries the subject's person marker."""
    s = noun_phrase(v, S, _the(v))
    w1 = verb(v, v1[0], "3SG")[0]
    w2 = verb(v, v2[0])[0]
    n1 = noun_phrase(v, v1[1], _the(v)) if v1[1] else None
    n2 = noun_phrase(v, v2[1], _the(v)) if v2[1] else None
    e, a = flagging(v, s, n1 or n2)   # (the clause is transitive: the doer takes the ergative, an object the accusative)
    if e:
        _np_gram(v, s, "ERG")
    if a and n1 is not None:
        _np_gram(v, n1, "ACC")
    o1, o2 = (n1.words if n1 else []), (n2.words if n2 else [])
    if v.ov():
        vp = o1 + w1 + o2 + w2
    else:
        vp = w1 + o1 + w2 + o2
    o = v.order()
    words = (vp + s.words) if o.index("S") > o.index("V") else (s.words + vp)
    return finish(v, sid, en_text, words, [note])


def s_serial(v: View) -> dict | None:
    """Serial verbs (`serial_verbs` yes): 'take X come' for bring (Yoruba mu ... wa, Mandarin na ... lai)."""
    if v.t.get("serial_verbs") != "yes":
        return None
    S, T, C, O = v.w("MAN", "WOMAN", "PERSON"), v.w("TAKE", "HOLD"), v.w("COME"), v.w("FISH", "WATER", "STONE", "STICK")
    if not (S and T and C and O):
        return None
    return _serial(v, "serial", S, (T, O), (C, None), f"The {en(S)} brings the {en(O)} (takes it and comes).",
                   f"serial verbs: '{en(T)}' and '{en(C)}' in one clause make 'bring'")


_REDUP_EN = {"ITER": ("{s} {v3} the {o} again and again", ("HIT", "CUT", "EAT")),
             "INTS": ("{s} really {v3} the {o}", ("EAT", "HIT", "SEE")),
             "CONT": ("{s} is {ving} the {o}", ("EAT", "CARRY", "SEE"))}


def s_redup(v: View) -> dict | None:
    rd = v.proc.get("redup")
    if not rd:
        return None
    tmpl, verbs = _REDUP_EN[rd["fn"]]
    S, Vc, O = v.w("MAN", "WOMAN", "CHILD (YOUNG HUMAN)"), v.w(*verbs), v.w("FISH", "STONE", "DOG", "BIRD")
    if not (S and Vc and O):
        return None
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, "3SG", redup=True)
    words = clause(v, s, vw, o)
    what = "the whole stem" if rd["shape"] == "full" else \
        f"a CV copy {'before' if rd['side'] == 'pre' else 'after'} the stem"
    en_text = "The " + tmpl.format(s=en(S), v3=_vf(Vc, 1), ving=_vf(Vc, 4), o=en(O)) + "."
    return finish(v, "redup", en_text, words,
                  [f"reduplication ({GR.REDUP_INFO[rd['fn']].gloss.split(' (')[0]}): {what}"] + vw[2])


def s_split(v: View) -> dict | None:
    """A split-ergative lect by person: a noun doer takes the ergative, a pronoun object the accusative ('the man sees
    me'). (An aspect split shows in the transitive and tense sentences side by side.)"""
    if v.t.get("alignment") != "split" or v.proc.get("split") != "person":
        return None
    S, Vc = v.w("MAN", "WOMAN", "PERSON"), v.w("SEE", "HIT", "HEAR")
    o = pronoun(v, "I")
    if not (S and Vc and o):
        return None
    s = noun_phrase(v, S, _the(v))
    vw = verb(v, Vc, "3SG")
    words = clause(v, s, vw, o)
    return finish(v, "split", f"The {en(S)} {_vf(Vc, 1)} me.", words,
                  ["split ergativity: the noun doer takes the ergative, the pronoun object the accusative"] + vw[2])


def s_clusive(v: View) -> dict | None:
    if not v.w("WE (INCLUSIVE)"):
        return None
    Vc, O = v.pair((("EAT",), ("FISH", "FLESH OR MEAT")), (("SEE",), ("DOG", "BIRD")))
    if not (Vc and O):
        return None
    s, o = pronoun(v, "WE (INCLUSIVE)"), noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, subject_marker(v, "1PL.INCL"))
    words = clause(v, s, vw, o)
    return finish(v, "clusive", f"We (you and I) {_vf(Vc, 0)} the {en(O)}.", words,
                  [f"inclusive 'we' {v.ipa('WE (INCLUSIVE)')}; the exclusive (not you) is {v.ipa('WE')}"] + vw[2])


# ---- grammar phase C sentences (2026-11-08) --------------------------------------------------------------------------

def _gram_on_verb(v: View, words: list, vi: int, fn: str) -> None:
    attach(v, words, vi, fn)


def s_complement(v: View) -> dict | None:
    """'The man says that the dog sleeps.': a complement clause, with the complementizer gram (COMP, from 'say' or the
    relativizer) where the lect has one; the clause stands in the object's place."""
    S, Vc, E, Ev = v.w("MAN", "WOMAN", "PERSON"), v.w("SAY", "KNOW", "KNOW (SOMETHING)"), v.w("DOG", "CHILD (YOUNG HUMAN)", "BIRD"), \
        v.w("SLEEP", "SIT", "SING", "LAUGH")
    if not (S and Vc and E and Ev):
        return None
    emb_s = noun_phrase(v, E, _the(v))
    ev = verb(v, Ev, "3SG")
    emb = clause(v, emb_s, ev, None, transitive=False)
    g = v.g("COMP")
    if g is not None:
        if (g.get("level") or 0) >= GR.CLITIC:
            attach(v, emb, emb.index(ev[0][ev[1]]), "COMP")
        else:
            w = Word(g["form_ipa"], "COMP")
            emb = [w] + emb if g.get("side") == "pre" else emb + [w]
        note = f"the complementizer is {_how(g)} ({g['form_ipa']}, {_src(v, g)})"
    else:
        note = "no complementizer: the clause stands bare in the object's place"
    s = noun_phrase(v, S, _the(v))
    if flagging(v, s, NP(emb, 0))[0]:   # (PW-1537 R5: 'say' with a clause is transitive, ERG on the sayer as in Basque
        _np_gram(v, s, "ERG")             # esan; the clause itself takes no case)
    vw = verb(v, Vc, "3SG")
    words = clause(v, s, vw, NP(emb, 0), transitive=False)
    return finish(v, "complement", f"The {en(S)} {_vf(Vc, 1)} that the {en(E)} {_vf(Ev, 1)}.", words, [note] + vw[2])


def s_topic(v: View) -> dict | None:
    """'The fish, the man eats (it).': the object fronted as the topic, with the topic gram (TOP) where the lect has
    one; shown also where word order is free, since that freedom is mostly topic and focus at work."""
    g = v.g("TOP")
    if g is None and v.t.get("word_order") != "free":
        return None
    S, Vc, O = v.w("MAN", "WOMAN", "PERSON"), v.w("EAT", "SEE", "CARRY"), v.w("FISH", "DOG", "STONE")
    if not (S and Vc and O):
        return None
    t = noun_phrase(v, O, _the(v))
    if g is not None:
        _np_gram(v, t, "TOP")
    s = noun_phrase(v, S, _the(v))
    e, a = flagging(v, s, t)   # (PW-1537 R5: the clause is still transitive: ERG on its subject; a topic marker
    if e:                      # stands in for the object's case, as Japanese wa for o, else the object keeps it)
        _np_gram(v, s, "ERG")
    if a and g is None:
        _np_gram(v, t, "ACC")
    vw = verb(v, Vc, "3SG")
    res = object_marker(v, vw[0], vw[0][vw[1]], "3SG")
    words = t.words + clause(v, s, vw, None, transitive=False)
    note = (f"the topic comes first, marked by {_how(g)} ({g['form_ipa']}, {_src(v, g)})" if g is not None else
            "word order is free: the topic (here the object) comes first")
    return finish(v, "topic", f"The {en(O)}, the {en(S)} {_vf(Vc, 1)} it.", words,
                  [note] + (["the verb's object marker points back to it"] if res else []))


def s_focus(v: View) -> dict | None:
    """'It is the man who sees the dog.': the focus gram (FOC) on the subject."""
    g = v.g("FOC")
    S, Vc, O = v.w("MAN", "WOMAN"), v.w("SEE", "HIT", "HOLD"), v.w("DOG", "BIRD", "FISH")
    if g is None or not (S and Vc and O):
        return None
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _the(v))
    _np_gram(v, s, "FOC")
    vw = verb(v, Vc, "3SG")
    return finish(v, "focus", f"It is the {en(S)} who {_vf(Vc, 1)} the {en(O)}.", clause(v, s, vw, o),
                  [f"the focus marker is {_how(g)} ({g['form_ipa']}, {_src(v, g)})"] + vw[2])


def s_applicative(v: View) -> dict | None:
    """'The man builds a house for the child.': the applicative (APPL) makes the beneficiary an object of the verb."""
    g = v.g("APPL")
    S, B = v.w("MAN", "WOMAN"), v.w("CHILD (YOUNG HUMAN)", "BOY", "GIRL")
    Vc, T = v.pair((("BUILD",), ("HOUSE", "BOAT")), (("CARRY", "TAKE"), ("WATER", "STONE", "FISH")))
    if g is None or not (S and B and Vc and T):
        return None
    s, b, t = noun_phrase(v, S, _the(v)), noun_phrase(v, B, _the(v)), noun_phrase(v, T, _a(v))
    vw = verb(v, Vc, "3SG", voice="APPL")
    words = clause(v, s, vw, b, t)
    return finish(v, "applicative", f"The {en(S)} {_vf(Vc, 1)} {'an' if en(T)[0] in 'aeiou' else 'a'} {en(T)} for the "
                  f"{en(B)}.", words, [f"the applicative is {_how(g)} ({g['form_ipa']}, {_src(v, g)}): the one it is done "
                                       "for becomes the verb's object, with no adposition"] + vw[2])


def s_reciprocal(v: View) -> dict | None:
    g = v.g("RECP")
    S, Vc = v.w("MAN", "WOMAN", "PERSON"), v.w("SEE", "HIT", "HEAR")
    if g is None or not (S and Vc):
        return None
    s = noun_phrase(v, S, _the(v), plural=True)
    vw = verb(v, Vc, "3PL", voice="RECP")
    return finish(v, "reciprocal", f"The {EN_PLURAL.get(S, en(S) + 's')} {_vf(Vc, 0)} each other.",
                  clause(v, s, vw, None, transitive=False),
                  [f"the reciprocal is {_how(g)} ({g['form_ipa']}, {_src(v, g)})"] + vw[2])


def s_antipassive(v: View) -> dict | None:
    """'The man eats (something).': the antipassive (ANTIP) leaves the doer unmarked and the object out (Dyirbal)."""
    g = v.g("ANTIP")
    S, Vc = v.w("MAN", "WOMAN", "PERSON"), v.w("EAT", "HIT", "SEE")
    if g is None or not (S and Vc):
        return None
    s = noun_phrase(v, S, _the(v))
    vw = verb(v, Vc, "3SG", voice="ANTIP")
    return finish(v, "antipassive", f"The {en(S)} {_vf(Vc, 1)} (something).", clause(v, s, vw, None, transitive=False),
                  [f"the antipassive is {_how(g)} ({g['form_ipa']}, {_src(v, g)}): "
                   + ("the doer takes no ergative and " if v.g("ERG") is not None else "")
                   + "the object is left out"] + vw[2])


def s_chain(v: View) -> dict | None:
    """Clause chaining with switch-reference: 'The man comes and (he) eats the fish' (SS on the medial verb) or 'the
    man comes and the dog eats the fish' (DS)."""
    fn = "SS" if v.g("SS") is not None else "DS" if v.g("DS") is not None else None
    S, M, Vc, O, S2 = v.w("MAN", "WOMAN"), v.w("COME", "GO", "SIT"), v.w("EAT", "SEE"), v.w("FISH", "BIRD"), \
        v.w("DOG", "CHILD (YOUNG HUMAN)")
    if fn is None or not (S and M and Vc and O) or (fn == "DS" and not S2):
        return None
    g = v.g(fn)
    s = noun_phrase(v, S, _the(v))
    mw, mi, _n = verb(v, M, "3SG")
    attach(v, mw, mi, fn)
    first = clause(v, s, (mw, mw.index(next(w for w in mw if w.concept == M)), []), None, transitive=False)
    s2 = noun_phrase(v, S2, _the(v)) if fn == "DS" else None
    vw = verb(v, Vc, "3SG")
    second = clause(v, s2, vw, noun_phrase(v, O, _the(v)))
    who = f"the {en(S2)}" if fn == "DS" else "(he)"
    return finish(v, "chain", f"The {en(S)} {_vf(M, 1)} and {who} {_vf(Vc, 1)} the {en(O)}.", first + second,
                  [f"switch-reference: the first verb's {ABBR[fn]} marker ({_how(g)}, {g['form_ipa']}, {_src(v, g)}) says "
                   f"the next clause has {'the same' if fn == 'SS' else 'a different'} subject"])


def s_incorp(v: View) -> dict | None:
    """'The man fish-eats.': a generic object noun incorporated into the verb (Mohawk, Chukchi)."""
    if not v.proc.get("incorp"):
        return None
    S, Vc, O = v.w("MAN", "WOMAN"), v.w("EAT", "CATCH", "HUNT"), v.w("FISH", "FLESH OR MEAT", "BIRD")
    if not (S and Vc and O):
        return None
    s = noun_phrase(v, S, _the(v))
    vw = verb(v, Vc, "3SG")
    vw[0][vw[1]].add(v.ipa(O), lgloss(O), GR.AFFIX, "pre" if v.hd_final() else "post")
    return finish(v, "incorp", f"The {en(S)} {_vf(Vc, 1)} {EN_PLURAL.get(O, en(O))} (is a {en(O)}-{_vf(Vc, 0)}er).",
                  clause(v, s, vw, None, transitive=False),
                  ["noun incorporation: the object noun is part of the verb word, with no article or case"] + vw[2])


def s_voice(v: View) -> list[dict]:
    """Philippine-type voice: the verb's voice marker picks the pivot, which takes the pivot marker (the old article,
    as Tagalog ang); actor voice makes the doer the pivot, patient voice the undergoer."""
    out = []
    S, Vc, O = v.w("MAN", "WOMAN"), v.w("EAT", "SEE", "HOLD"), v.w("FISH", "DOG", "BIRD")
    if not (S and Vc and O):
        return out
    piv = v.g("DEF")
    for fn, sid in (("AV", "voice_av"), ("PV", "voice_pv")):
        g = v.g(fn)
        if g is None:
            continue
        s, o = noun_phrase(v, S), noun_phrase(v, O)
        p = s if fn == "AV" else o
        if piv is not None:
            _np_gram(v, p, "DEF", "PIV")
        vw = verb(v, Vc, None, voice=fn)
        words = clause(v, s, vw, o, transitive=False)
        en_text = (f"The {en(S)} eats a {en(O)}." if fn == "AV" else f"The {en(S)} eats the {en(O)}.") if Vc == "EAT" else \
            f"The {en(S)} {_vf(Vc, 1)} {'a' if fn == 'AV' else 'the'} {en(O)}."
        out.append(finish(v, sid, en_text, words,
                          [f"{'actor' if fn == 'AV' else 'patient'} voice ({_how(g)}, {g['form_ipa']}, {_src(v, g)}): the "
                           f"{'doer' if fn == 'AV' else 'undergoer'} is the pivot"
                           + (f", marked by the pivot marker {piv['form_ipa']}" if piv is not None else "")]))
    return out


# ---- grammar phase D sentences (2026-11-08) --------------------------------------------------------------------------

def dist_gram(v: View) -> dict | None:
    """The far demonstrative gram (DIST), unless sound change has made it sound like 'that' (or 'this'): then the
    language has two distances again, whatever the gram list says (polish lane: the storm giant 'yon' was 'that')."""
    g = v.g("DIST")
    if g is None:
        return None
    if any(v.w(c) and v.ipa(c) == g["form_ipa"] for c in ("THAT", "THIS")):
        return None
    return g


def dem_np(v: View, concept: str, which: str, det: str | None = None) -> NP:
    """A noun with a demonstrative: 'this' or 'that' from the lexicon, 'yon' the far demonstrative gram (DIST)."""
    if which == "DIST":
        np_ = noun_phrase(v, concept, det)
        g = v.g("DIST")
        if g is not None and (g.get("level") or 0) >= GR.CLITIC:
            _np_gram(v, np_, "DIST")
        elif g is not None:
            w = Word(g["form_ipa"], "DIST")
            if v.before("demonstrative", "DemN"):
                np_.words.insert(0, w)
                np_.head += 1
            else:
                np_.words.append(w)
        return np_
    return noun_phrase(v, concept, det, dem=which)


def s_deixis(v: View) -> dict | None:
    """'That man over there sees this dog.': three distances where the lect has a far demonstrative (DIST)."""
    g = dist_gram(v)
    S, Vc, O = v.w("MAN", "WOMAN", "PERSON"), v.w("SEE", "HEAR"), v.w("DOG", "BIRD", "TREE")
    if g is None or not (S and Vc and O and v.w("THIS")):
        return None
    s, o = dem_np(v, S, "DIST"), noun_phrase(v, O, dem="THIS")
    vw = verb(v, Vc, "3SG")
    return finish(v, "deixis", f"That {en(S)} over there {_vf(Vc, 1)} this {en(O)}.", clause(v, s, vw, o),
                  [f"three distances: 'this' (near), 'that' (further) and the far demonstrative ({g['form_ipa']}, "
                   f"{_src(v, g)})"] + vw[2])


def s_remote(v: View) -> dict | None:
    """'The man built a boat long ago.': a remote past beside the plain (and recent) past (graded pasts, Bantu)."""
    g = v.g("REMPST")
    S = v.w("MAN", "PERSON", "HUNTER")
    Vc, O = v.pair((("BUILD",), ("BOAT", "HOUSE")), (("EAT", "KILL", "CARRY"), ("FISH", "BIRD")))
    if g is None or not (S and Vc and O):
        return None
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _a(v))
    vw = verb(v, Vc, "3SG", "REMPST")
    grades = [ABBR[f] for f in ("RECPST", "PAST", "REMPST") if v.g(f)]
    if len(grades) > 1:
        rest = "the pasts are graded, from nearer to further back: " + ", ".join(grades)
    else:   # (the plain past has been lost since: nearer events take the perfect, or the bare verb)
        rest = ("there is no plain past beside it: nearer events take the perfect (PRF)" if v.g("PERF") else
                "there is no plain past beside it: nearer events take the bare verb")
    return finish(v, "remote", f"The {en(S)} {_vf(Vc, 2)} {'an' if en(O)[0] in 'aeiou' else 'a'} {en(O)} long ago.",
                  clause(v, s, vw, o, tam="REMPST"),
                  [f"the remote past is {_how(g)} ({g['form_ipa']}, {_src(v, g)}); {rest}"] + vw[2])


_ASPECT_EN = {"COMPL": ("The {s} has eaten the {o} up.", ("EAT", "DRINK")),
              "INCH": ("The {s} begins to eat the {o}.", ("EAT", "DRINK")),
              "RPT": ("The {s} eats the {o} again.", ("EAT", "DRINK"))}


def s_aspect(v: View) -> dict | None:
    """One of the newer aspects (completive 'finish', inceptive 'begin', repetitive 'again')."""
    fn = next((f for f in ("COMPL", "INCH", "RPT") if v.g(f) is not None), None)
    if fn is None:
        return None
    tmpl, verbs = _ASPECT_EN[fn]
    S, Vc, O = v.w("CHILD (YOUNG HUMAN)", "MAN", "WOMAN"), v.w(*verbs), v.w("FISH", "WATER", "MILK", "EGG")
    if not (S and Vc and O):
        return None
    if Vc == "DRINK":
        tmpl = tmpl.replace("eat", "drink").replace("eaten", "drunk")
    g = v.g(fn)
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, "3SG", fn)
    return finish(v, "aspect", tmpl.format(s=en(S), o=en(O)), clause(v, s, vw, o, tam=fn),
                  [f"the {GR.func_info(fn).gloss.split(' (')[0]} is {_how(g)} ({g['form_ipa']}, {_src(v, g)})"] + vw[2])


def s_mirative(v: View) -> dict | None:
    """'The dog ate the fish!' said as news (the mirative: unexpected information; DeLancey 1997)."""
    g = v.g("MIR")
    S, Vc, O = v.w("DOG", "BIRD", "CHILD (YOUNG HUMAN)"), v.w("EAT", "DRINK"), v.w("FISH", "FLESH OR MEAT", "MILK", "EGG")
    if g is None or not (S and Vc and O):
        return None
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, "3SG", "MIR")
    src = (g.get("source") or [""])[0]
    same = src in ("PERF", "EVID.REP") and v.g(src) is not None and v.g(src)["form_ipa"] == g["form_ipa"]
    return finish(v, "mirative", f"(Look!) The {en(S)} {_vf(Vc, 2)} the {en(O)}!", clause(v, s, vw, o, tam="MIR"),
                  [f"the mirative ({_how(g)}, {g['form_ipa']}, {_src(v, g)}) marks news the speaker did not expect"
                   + (f"; it sounds like the {GR.func_info(src).gloss.split(' (')[0]} marker it grew from" if same else "")]
                  + vw[2])


def polite_live(v: View) -> bool:
    """Does the lect have polite address with a polite pronoun that differs from the plain 'you' (grammar.polite_contrast:
    a lect whose 2SG and 2PL fell together cannot be polite with the plural)?"""
    pol = v.proc.get("polite")
    return bool(pol and v.w(pol["concept"]) and v.w("THOU") and v.ipa(pol["concept"]) != v.ipa("THOU"))


def polite_pronoun(v: View) -> NP | None:
    """The pronoun the lect uses to address one person with respect (processes.polite): the plural 'you' (French vous)
    or a third person (German Sie), glossed with its own person and POL."""
    pol = v.proc.get("polite")
    if not polite_live(v):
        return None
    np_ = pronoun(v, pol["concept"])
    np_.words[0].gloss = PRON[pol["concept"]] + ".POL"
    return np_


def s_polite(v: View) -> dict | None:
    """'You (sir) eat the fish.': polite address, with the honorific verb marker where the lect has one."""
    S = polite_pronoun(v)
    Vc, O = v.pair((("EAT",), ("FISH", "FLESH OR MEAT")), (("SEE",), ("HOUSE", "DOG")))
    if S is None or not (Vc and O):
        return None
    pol = v.proc["polite"]
    o = noun_phrase(v, O, _the(v))
    vw = verb(v, Vc, S.person)
    hon = v.g("HON")
    if hon is not None:
        attach(v, vw[0], vw[1], "HON")
    if vw[2] and v.t.get("pro_drop") == "yes":
        pass   # (a polite subject is said aloud: the pronoun is the point)
    notes = [f"polite address: the {'plural' if pol['kind'] == 'plural' else 'third-person'} pronoun "
             f"{v.ipa(pol['concept'])} ('{'you all' if pol['kind'] == 'plural' else 'they'}') speaks to one person with "
             f"respect; the plain 'you' is {v.ipa('THOU')}" if v.w("THOU") else ""]
    if hon is not None:
        notes.append(f"the verb takes the honorific marker ({_how(hon)}, {hon['form_ipa']}, {_src(v, hon)})")
    return finish(v, "polite", f"You (sir) {_vf(Vc, 0)} the {en(O)}.", clause(v, S, vw, o), notes + vw[2])


def comparative(v: View, a: str, b: str, adj: str) -> tuple[list, str] | None:
    """'A is ADJ-er than B' by the lect's comparison type (processes.compare; Stassen, WALS 121A): locational ('A is
    big from B': the standard in the ablative or locative), exceed ('A is big, climbs B': a verb 'exceed'), particle
    ('A is big than B', a particle from 'that'), conjoined ('A is big, B is small')."""
    kind = v.proc.get("compare") or ("locational" if v.g("ABL") or v.g("LOC") else "conjoined")
    A, B = noun_phrase(v, a, _the(v)), noun_phrase(v, b, _the(v))
    pred = [Word(v.ipa(adj), lgloss(adj), adj)]
    if v.t.get("adjective_verb_like") == "yes":
        pw = verb(v, adj, "3SG")[0]
    else:
        pw = cop_phrase(v, NP(pred, 0))
    if kind == "exceed":
        ex = v.w(*GR.EXCEED_VERBS)
        if ex is None:
            kind = "conjoined"
        else:
            ew = verb(v, ex, None, gloss="exceed")[0]   # (the verb 'climb', used as 'exceed, go over')
            stdp = (B.words + ew) if v.ov() else (ew + B.words)
            return A.words + pw + stdp, f"an 'exceed' comparison: 'A is {en(adj)}, exceeds B', with the verb for '{en(ex)}' "                                          "(as Yoruba ju 'exceed', Thai kwaa 'cross over')"
    if kind == "locational":
        fn = "ABL" if v.g("ABL") else "LOC" if v.g("LOC") else None
        if fn is not None:
            _np_gram(v, B, fn)
            how = f"the standard takes the {CASE_NAME[fn]} ('{'from' if fn == 'ABL' else 'at'} B')"
        else:
            x = oblique(v, B, "ABL", ("AT", "IN"))
            if x is None:
                kind = "conjoined"
            how = "the standard takes the word for 'at' ('big at B')"
        if kind == "locational":
            body = (B.words + pw) if v.ov() else (pw + B.words)
            return A.words + body, f"a locational comparison: {how}, as " + (
                "Japanese yori, Turkish -den" if fn == "ABL" else "Swahili kuliko 'where there is'")
    if kind == "particle":
        th = v.w("THAT")
        if th:
            part = [Word(v.ipa(th), "than")]
            return A.words + pw + part + B.words, "a particle comparison: 'than' is the word for 'that' (as English than "                                                   "grew from 'then')"
        kind = "conjoined"
    opp = {"BIG": "SMALL", "SMALL": "BIG", "OLD": "NEW", "NEW": "OLD", "LONG": "SHORT", "GOOD": "BAD"}.get(adj)
    if not opp or not v.w(opp):
        return None
    pw2 = verb(v, opp, "3SG")[0] if v.t.get("adjective_verb_like") == "yes" else \
        cop_phrase(v, NP([Word(v.ipa(opp), lgloss(opp), opp)], 0))
    return A.words + pw + B.words + pw2, f"a conjoined comparison: 'A is {en(adj)}, B is {en(opp)}' (no comparative " \
                                         "construction, as in many languages of New Guinea and Australia)"


def s_comparative(v: View) -> dict | None:
    A, B, adj = v.w("MAN", "WOMAN"), v.w("DOG", "CHILD (YOUNG HUMAN)"), v.w("BIG", "OLD", "STRONG")
    if not (A and B and adj):
        return None
    r = comparative(v, A, B, adj)
    if r is None:
        return None
    er = {"BIG": "bigger", "OLD": "older", "STRONG": "stronger"}[adj]
    return finish(v, "comparative", f"The {en(A)} is {er} than the {en(B)}.", r[0], [r[1]])


def s_obviative(v: View) -> dict | None:
    """'The woman sees the man (OBV)': where two third persons meet, the less central one is obviative (Algonquian)."""
    g = v.g("OBV")
    S, Vc, O = v.w("WOMAN", "MAN"), v.w("SEE", "HEAR", "HIT"), v.w("MAN", "CHILD (YOUNG HUMAN)", "DOG")
    if g is None or not (S and Vc and O) or S == O:
        return None
    s, o = noun_phrase(v, S, _the(v)), noun_phrase(v, O, _the(v))
    attach(v, o.words, o.head, "OBV")
    vw = verb(v, Vc, "3SG")
    return finish(v, "obviative", f"The {en(S)} sees the {en(O)}.", clause(v, s, vw, o),
                  [f"two third persons: the one the story is about is proximate (unmarked), the other obviative "
                   f"({_how(g)}, {g['form_ipa']}, {_src(v, g)})"] + vw[2])


def s_own(v: View) -> dict | None:
    """One sentence from the language's own life (owner ruling 11-08, PW-1538 E: keep the core set, add one per lect):
    its people's faith ('We pray to <god>.'), home landscape ('We live by the river.', from the record's `home`, set by
    output.home_feature) or staple food ('We eat millet.'), the first of the three the lexicon can say, in an order fixed
    by the lect's id so that neighbouring pages differ."""
    import zlib
    from . import texts as TX
    we = pronoun(v, "WE")
    if we is None:
        return None
    lj = v.lj
    lid = str(lj.get("id") or "")
    k0 = zlib.crc32(lid.encode("utf-8")) % 3

    def faith():
        Vc = v.w("PRAY")
        gods = sorted((c for c in v.lex if c.startswith("name:god:") and v.lex[c].get("ipa")),
                      key=lambda c: (len(c), c))
        if not (Vc and gods):
            return None
        g = gods[0]
        name = (v.lex[g].get("roman") or v.ipa(g)).capitalize()
        x = oblique(v, NP([Word(v.ipa(g), name, g)], 0), "DAT", ("TO", "AT"))
        if x is None:
            return None
        vw = verb(v, Vc, "1PL")
        return finish(v, "own", f"We pray to {name}.", clause(v, we, vw, None, x[0], transitive=False),
                      [f"{name} is a god of this people's faith", x[1]] + vw[2])

    def home():
        L = lj.get("home")
        Vc = v.w("DWELL (LIVE, RESIDE)", "SIT")
        if not (L and Vc and v.w(L)):
            return None
        x = oblique(v, noun_phrase(v, L, _the(v)), "LOC", ("NEAR", "AT", "IN"))
        if x is None:
            return None
        vw = verb(v, Vc, "1PL")
        prep = "in the mountains" if L == "MOUNTAIN" else f"by the {en(L)}"
        return finish(v, "own", f"We live {prep}.", clause(v, we, vw, None, x[0], transitive=False),
                      [f"the people's home: {prep.split(' the ')[-1]}", x[1]] + vw[2])

    def food():
        st = TX.staple(lj)
        Vc = v.w("EAT")
        if not (st and Vc):
            return None
        f, kind = st
        fen = TX.ANIMAL_EN.get(en(f), en(f) + " meat") if f.startswith("animal:") else en(f)
        o = noun_phrase(v, f)
        vw = verb(v, Vc, "1PL")
        return finish(v, "own", f"We eat {fen}.", clause(v, we, vw, o), [f"the people's staple: {fen}"] + vw[2])
    opts = (faith, home, food)
    for j in range(3):
        try:
            r = opts[(k0 + j) % 3]()
        except (KeyError, IndexError, ValueError, StopIteration):
            r = None
        if r is not None:
            return r
    return None


SENTENCES = (s_transitive, s_locative, s_tense, s_polar, s_content, s_negation, s_possession, s_number, s_copula,
             s_relative, s_give, s_imperative, s_passive, s_serial, s_redup, s_split, s_clusive, s_object, s_hortative,
             s_complement, s_topic, s_focus, s_applicative, s_reciprocal, s_antipassive, s_chain, s_incorp, s_voice,
             s_deixis, s_remote, s_aspect, s_mirative, s_polite, s_comparative, s_obviative, s_own)


def utterances(lj: dict) -> list[dict]:
    v = View(lj)
    out = []
    for fn in SENTENCES:
        try:
            s = fn(v)
        except (KeyError, IndexError, ValueError, StopIteration):
            s = None
        if isinstance(s, list):
            out += s
        elif s is not None:
            out.append(s)
    return out


# ---- grammar notes ------------------------------------------------------------------------------------------------------

def _how(g: dict) -> str:
    lv = g.get("level") or 0
    side = "before" if g.get("side") == "pre" else "after"
    host = {"N": "noun", "NP": "noun phrase", "V": "verb", "VP": "verb phrase"}.get(g.get("host"), "word")
    if lv == GR.FREE:
        return f"a separate word {side} the {host}"
    if lv == GR.CLITIC:
        return f"a clitic {side} the {host}"
    return f"{'a prefix' if g.get('side') == 'pre' else 'a suffix'}{' that fuses with some stems' if lv >= GR.FUSED else ''}"


def _ex(v: View, words: list, en_text: str) -> list:
    fl, gl = [], []
    for w in words:
        f, g, _s = render_word(v, w)
        fl.append(f)
        gl.append(g)
    return [" ".join(fl), " ".join(gl), en_text]


def _src(v: "View", g: dict) -> str:
    src = g.get("source") or ["?"]
    s = src[0]
    if len(src) > 2 and src[2] == "gram" and s in GR.FUNCS:
        if v.g(s) is None or (s == "REL" and v.t.get("relative") == "RelN"):   # (PW-1537 R5: 'from the relativizer marker' beside 'no relativizer': it has gone since)
            return f"from a {GR.FUNCS[s].gloss} marker the language has since lost"
        return f"from the {GR.FUNCS[s].gloss} marker"
    if s == "I":
        return "from 'I'"
    return f"from '{en(s)}'" if s and s != "?" else "a coined form"


_CASE_NOUN = {"GEN": ("MAN", "PERSON"), "DAT": ("MAN", "PERSON"), "ACC": ("DOG", "FISH"), "ERG": ("MAN", "PERSON"),
              "INS": ("STONE", "KNIFE", "STICK"), "COM": ("DOG", "FRIEND", "PERSON")}


def notes_nouns(v: View) -> list[dict]:
    out = []
    N = v.w("DOG", "BIRD", "FISH", "STONE", "TREE")
    # number
    nums = [f for f in ("PL", "DU") if v.g(f)]
    if nums and N:
        txt = "; ".join(f"{GR.FUNCS[f].gloss}: {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})" for f in nums)
        ex = [_ex(v, noun_phrase(v, N).words, f"{en(N)}")]
        if "PL" in nums:
            ex.append(_ex(v, noun_phrase(v, N, plural=True).words, EN_PLURAL.get(N, en(N) + "s")))
        if "DU" in nums:
            ex.append(_ex(v, noun_phrase(v, N, dual=True).words, "two " + EN_PLURAL.get(N, en(N) + "s")))
        out.append({"topic": "Number", "text": "Nouns mark number: " + txt + ".", "ex": ex})
    else:
        out.append({"topic": "Number", "text": "Nouns do not mark number: one noun form serves for one or many; a numeral "
                                               "or 'many' says how many.", "ex": []})
    # case
    cases = [f for f in GR.CASE_FNS if v.g(f)]
    bound = [f for f in cases if (v.g(f).get("level") or 0) >= GR.CLITIC]
    free = [f for f in cases if f not in bound]
    alv = v.t.get("alignment", "neutral")
    if v.g("ACC") is not None or v.g("ERG") is not None:
        al = {"nom-acc": "Alignment is accusative: the object is marked (ACC), subjects are not.",
              "erg-abs": "Alignment is ergative: the subject of a transitive verb is marked (ERG); the subject of an "
                         "intransitive verb and the object are not.",
              "split": {"person": "Alignment is split by person: a noun doing a transitive action takes the ergative "
                                  "(ERG), a pronoun object takes the accusative (ACC); pronoun doers and noun objects "
                                  "are unmarked.",
                        "aspect": "Alignment is split by aspect: in the perfective or past the doer of a transitive verb "
                                  "takes the ergative (ERG); elsewhere the object takes the accusative (ACC)."
                        }.get(v.proc.get("split"), "Alignment is split: both an accusative and an ergative marker "
                                                   "are live.")}.get(alv, "")
        if alv == "split" and (v.g("ACC") is None or v.g("ERG") is None):   # (the notes say what the forms show)
            have, lack = ("ACC", "ERG") if v.g("ACC") is not None else ("ERG", "ACC")
            al = (f"The grammar leans to a split by {v.proc.get('split') or 'person'}, but only the {CASE_NAME[have]} "
                  f"({have}) is live; with no {CASE_NAME.get(lack, lack.lower())} ({lack}) " +
                  ("the object is marked and subjects are not." if have == "ACC" else
                   "the doer of a transitive verb is marked and objects are not.") +
                  (" (In the past the object is left unmarked: there the split would want the ergative.)"
                   if have == "ACC" and v.proc.get("split") == "aspect" else ""))
    elif alv == "neutral":
        al = "Subject and object are not marked apart: word order tells them."
    else:
        al = (f"The typology leans {alv.replace('-', '-')} in alignment, but no case marker shows it yet: word order "
              "tells subject from object.")
    H = v.w("HOUSE", "RIVER", "TREE", "STONE")
    if cases and H:
        bits = [f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})" for f in bound]
        fbits = [f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})" for f in free]
        txt = ""
        if bits:
            txt += f"Nouns take {len(bits)} case marker{'s' if len(bits) > 1 else ''}: " + "; ".join(bits) + ". "
        else:
            txt += "Nouns have no bound case. "
        if fbits:
            txt += "Adpositions (free words, not yet case): " + "; ".join(fbits) + ". "
        ex = []
        for f in cases[:5]:
            Hc = v.w(*_CASE_NOUN.get(f, ())) or H
            np_ = noun_phrase(v, Hc)
            _np_gram(v, np_, f)
            ex.append(_ex(v, np_.words, CASE_EN.get(f, "{n}").format(n=en(Hc))))
        if v.proc.get("dom") and v.g("ACC") is not None:
            al += (" The accusative marks only animate objects (people and animals) and pronouns, which stand at the top "
                   "of the animacy scale whatever they point to; a thing named by a noun stays bare "
                   "(differential object marking, as Spanish a and Hindi ko).")
            An, In = v.w("DOG", "MAN", "CHILD (YOUNG HUMAN)"), v.w("STONE", "WATER", "HOUSE")
            Vt = v.w("SEE", "HIT", "HOLD")
            Sb = v.w("WOMAN", "PERSON", "MAN")
            if An and In and Vt and Sb:
                for o_c in (An, In):
                    sb, ob = noun_phrase(v, Sb, _the(v)), noun_phrase(v, o_c, _the(v))
                    ex.append(_ex(v, clause(v, sb, verb(v, Vt, "3SG"), ob),
                                  f"the {en(Sb)} {_vf(Vt, 1)} the {en(o_c)}"))
        out.append({"topic": "Case", "text": (txt + al).strip(), "ex": ex})
    else:
        adps = [c for c in ("IN", "AT", "WITH") if v.w(c)]
        out.append({"topic": "Case", "text": "Nouns have no case marking. " + al + (
            " Place and company are said with the plain words " + ", ".join(f"'{en(c)}' ({v.ipa(c)})" for c in adps)
            + " as adpositions." if adps else ""), "ex": []})
    # gender / classes
    cs = v.classes
    if cs and cs.get("classes"):
        kind = cs.get("kind")
        rows = []
        ex = []
        bound_cls = any((v.g(f) or {}).get("level", 0) >= GR.CLITIC for _k, _g, f in cs["classes"])
        for k, grp, f in cs["classes"]:
            g = v.g(f)
            if g is None:
                continue
            how = _how(g) if bound_cls or (g.get("level") or 0) >= GR.CLITIC else "a separate word after the numeral"
            have = {x[1] for x in cs["classes"]}
            dflt = ", and for every thing no other class takes" if default_class(cs)[1] == f and len(cs["classes"]) and \
                any(_want(cs, c) not in have for c in ("HOUSE", "MILK", "STONE")) else ""
            if kind not in ("sex", "animacy"):   # (animate nouns fall to the person or animal class first: PW-1538 B)
                dflt += "".join(f", and for {what} (no class of their own)" for a, what in (("animal", "animals"),
                                                                                       ("person", "persons"))
                                if a not in have and a != grp and default_class(cs, a)[1] == f)
            rows.append(f"class {v.cl_num.get(f, k)} for {GR.GROUP_GLOSS.get(grp, grp)}{dflt}, {how} ({g['form_ipa']}, "
                        f"{_src(v, g)})")
            n = _noun_of_group(v, kind, grp)
            if n and len(ex) < 4:
                ex.append(_class_example(v, n, f, g, bound_cls))
        lead = {"sex": "Nouns fall into genders by sex", "animacy": "Nouns fall into genders by animacy",
                "classes": "Nouns fall into noun classes by meaning", "classifiers": "Nouns are counted with classifiers"
                }.get(kind, "Nouns fall into classes")
        if not bound_cls:
            lead = "Nouns are counted with classifiers (free words, not yet bound to the noun)"
        elif not v.proc.get("concord"):   # (owner 11-08, PW-1538 A: gender only where something agrees with the noun)
            lead = {"sex": "Nouns carry a class marker by sex", "animacy": "Nouns carry a class marker by animacy"}.get(
                kind, "Nouns carry a class marker by meaning") + (" (" + GR.GENDER_NO_AGREEMENT + ": nothing else in the "
                                                                   "sentence agrees with the noun's class)")
        if rows:
            out.append({"topic": "Gender and noun classes", "text": lead + ": " + "; ".join(rows) + ".", "ex": ex})
        else:
            out.append({"topic": "Gender and noun classes", "text": "There is no gender or noun class: the old class "
                        "markers have worn away.", "ex": []})
    else:
        out.append({"topic": "Gender and noun classes", "text": "There is no gender or noun class.", "ex": []})
    return out


def _class_example(v: View, n: str, f: str, g: dict, bound_cls: bool) -> list:
    """A noun of class `f` with its marker. A bound marker is on the noun already; a free one is a classifier: after a
    numeral ('two CLF dogs') in a system with no bound marker, else the free word beside the noun on its side."""
    if (g.get("level") or 0) >= GR.CLITIC:
        return _ex(v, noun_phrase(v, n).words, en(n))
    num = v.w("TWO", "THREE", "ONE")
    if not bound_cls and num:
        np_ = noun_phrase(v, n, num=num, plural=num != "ONE")
        if not any(w.gloss == "CLF" for w in np_.words):   # (no classifier slot shown: put it after the numeral)
            i = next(i for i, w in enumerate(np_.words) if w.concept == num)
            np_.words.insert(i + 1, Word(g["form_ipa"], "CLF"))
        return _ex(v, np_.words, f"{en(num)} {EN_PLURAL.get(n, en(n) + 's') if num != 'ONE' else en(n)}")
    words = noun_phrase(v, n).words
    lab = (class_of(v, n) or (f, "CLF"))[1]
    attach(v, words, next(i for i, w in enumerate(words) if w.concept == n), f, lab)
    return _ex(v, words, en(n))


def _noun_of_group(v: View, kind: str, grp: str) -> str | None:
    pool = {"person": ("PERSON", "MAN", "WOMAN"), "people": ("PEOPLE",), "manner": ("TONGUE", "WORD", "SONG"),
            "abstract": ("NAME", "DAY (NOT NIGHT)", "STONE"), "plant": ("TREE", "GRASS", "LEAF"), "animal": ("DOG", "BIRD"),
            "liquid": ("WATER", "BLOOD", "MILK"), "place": ("RIVER", "HOUSE", "MOUNTAIN"), "small": ("EGG", "SEED"),
            "masculine": ("MAN", "FATHER"), "feminine": ("WOMAN", "MOTHER"), "animate": ("PERSON", "DOG"),
            "inanimate": ("STONE", "WATER")}.get(grp, ())
    fn = next((f for _k, g, f in v.classes["classes"] if g == grp), None)
    src = ((v.g(fn) or {}).get("source") or [None])[0] if fn else None
    ok = [c for c in pool if v.w(c) and (class_of(v, c) or ("",))[0] == fn]
    # (not the marker's own source noun when another will do: 'tongue' with the classifier from 'tongue' says little)
    return next((c for c in ok if c != src), ok[0] if ok else None)


def notes_verbs(v: View) -> list[dict]:
    out = []
    Vc = v.w("GO", "EAT", "SEE", "WALK")
    tams = [f for f in TAM_ORDER if v.g(f)]
    evs = [f for f in ("EVID.DIR", "EVID.REP") if v.g(f)]
    if Vc and tams:
        txt = "; ".join(f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})"
                        for f in tams)
        shown = [f for f in ("PAST", "RECPST", "REMPST") if f in tams] + [f for f in tams if f not in
                                                                          ("PAST", "RECPST", "REMPST")]
        ex = [_ex(v, verb(v, Vc, None, f)[0], "(it) " + _tam_en(f, Vc)) for f in shown[:5]]
        unmarked = [k for k in ("past", "future", "perfective", "progressive", "habitual") if v.t.get(k) != "marked"]
        out.append({"topic": "Tense and aspect", "text": "Verbs mark tense and aspect. " + txt[0].upper() + txt[1:] + "." + (
            f" Unmarked: {', '.join(unmarked)} (left to context)." if unmarked else ""), "ex": ex})
    else:
        y = v.w("YESTERDAY")
        out.append({"topic": "Tense and aspect", "text": "Verbs carry no tense or aspect: time is left to context or to "
                    "words like 'yesterday'" + (f" ({v.ipa(y)})" if y else "") + ".", "ex": []})
    moods = [f for f in GR.MOOD_FNS + ("MIR",) if v.g(f)]
    if (evs or moods) and Vc:
        bits = []
        ex = []
        if evs:
            bits.append("Speakers mark how they know: " + "; ".join(
                f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})" for f in evs)
                + ".")
            ex += [_ex(v, verb(v, Vc, None, f)[0], "(it) " + _vf(Vc, 1) + (", I saw it" if f == "EVID.DIR" else
                                                                           ", they say")) for f in evs]
        if moods:
            bits.append("Mood markers: " + "; ".join(
                f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})"
                for f in moods) + ".")
            ex += [_ex(v, verb(v, Vc, mood=f)[0], _MOOD_EN[f].format(v=_vf(Vc, 0), v3=_vf(Vc, 1))) for f in moods]
        out.append({"topic": "Mood and evidentiality", "text": " ".join(bits), "ex": ex})
    else:
        out.append({"topic": "Mood and evidentiality", "text": "No evidential or mood marker is live; statements are "
                    "unmarked.", "ex": []})
    # person agreement
    pers = [f for f in GR.SERIES["S"] if v.g(f)]
    bound = [f for f in pers if (v.g(f).get("level") or 0) >= GR.CLITIC]
    free = [f for f in pers if f not in bound]
    if bound and Vc:
        txt = "; ".join(f"{f}: {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})" for f in bound)
        ex = [_ex(v, verb(v, Vc, f)[0], f"{_PERSON_EN[f]} {_vf(Vc, 1 if f == '3SG' else 0)}") for f in bound[:4]]
        pd = (" Subject pronouns are dropped when the marker is there." if v.t.get("pro_drop") == "yes" else "")
        sc = v.proc.get("stem_change") or {}
        missing = [f for f in GR.PERSON_FNS if f not in bound and f not in sc]
        scp = [f for f in GR.PERSON_FNS if f in sc and f not in bound]
        out.append({"topic": "Person agreement", "text": "Verbs agree with the subject: " + txt + "." + pd + (
            f" No marker yet for {', '.join(missing)} (zero)." if missing else "") + (
            f" {' and '.join(scp)} {'is' if len(scp) == 1 else 'are'} shown by a change of the stem's vowel (see Word "
            "shapes)." if scp else "") + (
            " The inclusive 'we' has a marker of its own (1PL.INCL); 1PL is the exclusive." if "1PL.INCL" in bound
            else ""), "ex": ex})
    else:
        txt = "Verbs do not agree with the subject."
        if free:
            full = {p: c for c, p in PRON.items() if c != "WE (INCLUSIVE)"}
            txt += " Short unstressed pronouns stand beside the verb (" + ", ".join(
                f"{f} {v.g(f)['form_ipa']}" + (f", beside the full pronoun {v.ipa(full[f])}"
                                               if full.get(f) and v.w(full[f]) and v.ipa(full[f]) != v.g(f)['form_ipa']
                                               else "") for f in free) + "), on their way to becoming agreement."
        out.append({"topic": "Person agreement", "text": txt, "ex": []})
    for ser, topic, lead, en_of in (("O", "Object agreement", "Verbs also agree with the object", _OBJ_EN),
                                    ("P", "Possessor marking", "The possessed noun carries its possessor's person",
                                     _POSS_EN)):
        b = [f for f in GR.SERIES[ser] if (v.g(f) or {}).get("level", 0) >= GR.CLITIC]
        host = v.w("SEE", "EAT", "HIT", "HOLD") if ser == "O" else v.w("HOUSE", "DOG", "NAME", "EYE")
        if not b or not host:
            continue
        txt = "; ".join(f"{ABBR[f]}: {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v, v.g(f))})" for f in b)
        ex = []
        for f in b[:3]:
            p = f.split(".")[0]
            if ser == "O":
                ws, vi, _n = verb(v, host, "3SG")
                object_marker(v, ws, ws[vi], p)
                ex.append(_ex(v, ws, f"he/she {_vf(host, 1)} {en_of[p]}"))
            else:
                w = noun_phrase(v, host).words
                attach(v, w, 0, f)
                ex.append(_ex(v, w, f"{en_of[p]} {en(host)}"))
        miss = [ABBR[f] for f in GR.SERIES[ser] if f not in b]
        out.append({"topic": topic, "text": f"{lead}: {txt}." + (f" No marker yet for {', '.join(miss)}." if miss else ""),
                    "ex": ex})
    return out


_PERSON_EN = {"1SG": "I", "2SG": "you", "3SG": "he/she", "1PL": "we", "2PL": "you all", "3PL": "they",
              "1PL.INCL": "we (you and I)"}
_OBJ_EN = {"1SG": "me", "2SG": "you", "3SG": "him/her", "1PL": "us", "2PL": "you all", "3PL": "them"}
_POSS_EN = {"1SG": "my", "2SG": "your", "3SG": "his/her", "1PL": "our", "2PL": "your (all)", "3PL": "their"}
_MOOD_EN = {"IMP": "{v}!", "HORT": "let us {v}", "OBLG": "(one) must {v}", "APPR": "lest (it) {v}",
            "MIR": "(look!) it {v3}! (news to the speaker)"}


def notes_clause(v: View, sents: dict) -> list[dict]:
    out = []
    g = v.g("NEG")
    nv = v.t.get("negation", "preverbal").replace("_", " ")
    if g is not None:
        txt = f"Negation is {_how(g)} ({g['form_ipa']}, {_src(v, g)})"
        if (g.get("level") or 0) == GR.CLITIC and v.proc.get("second") and GR.func_info("NEG").host[0] == "V":
            txt += ", but like the verb's other clitics it stands in second position, after the clause's first word"
        txt += "."
    elif v.w("NOT"):
        txt = f"Negation uses the word for 'not' ({v.ipa(v.w('NOT'))}), {nv}."
    else:
        txt = "No negator is recorded."
    out.append({"topic": "Negation", "text": txt, "ex": _sent_ex(sents, "negation")})
    pq = {"intonation": "rising intonation alone", "initial_particle": "a particle at the start of the clause",
          "final_particle": "a particle at the end of the clause", "verb_morph": "a marker on the verb"
          }.get(v.t.get("polar_question"), "intonation")
    qw = [c for c in ("WHO", "WHAT", "WHERE", "WHEN", "HOW") if v.w(c)]
    txt = f"Yes/no questions use {pq}. Question words " + (
        "stay where the questioned phrase would stand" if v.t.get("wh_in_situ") == "yes" else "move to the front") + \
        (": " + ", ".join(f"{en(c)} {v.ipa(c)}" for c in qw) if qw else "") + "."
    out.append({"topic": "Questions", "text": txt, "ex": _sent_ex(sents, "polar") + _sent_ex(sents, "content")})
    if "imperative" in sents:
        g = v.g("IMP")
        txt = (f"Commands take the imperative marker, {_how(g)} ({g['form_ipa']}, {_src(v, g)}), and no subject." if g else
               "There is no imperative marker: a command is the bare verb stem, with no subject and no subject or tense "
               "marker.")
        if v.g("HORT") is not None:
            txt += " 'Let us ...' has a hortative marker of its own."
        out.append({"topic": "Commands", "text": txt, "ex": _sent_ex(sents, "imperative") + _sent_ex(sents, "hortative")})
    gen = v.g("GEN")
    ps = sents.get("possession")
    m = re.fullmatch(r"My (.+) has an? (.+)\.", (ps or {}).get("en") or "")
    K, T = m.groups() if m else ("mother", "dog")   # (the note names the sample sentence's own kin word and thing)
    pp = {"have": f"a 'have' verb ('my {K} has a {T}')", "locational": f"a locational phrase ('at my {K} is a {T}')",
          "other": f"'with' ('my {K} is with a {T}')"
          }.get(v.t.get("predicative_possession"), "")
    head = [f for f in GR.SERIES["P"] if (v.g(f) or {}).get("level", 0) >= GR.CLITIC]
    txt = (f"The possessor stands {'before' if v.before('genitive', 'GN') else 'after'} the possessed noun"
           + (f", marked by the genitive marker, {_how(gen)} ({gen['form_ipa']})" if gen else
              "" if head else ", with no marker")
           + ("; the possessed noun carries the possessor's person marker (see Possessor marking)" if head else "")
           + ".")
    if v.t.get("alienability") == "yes":
        txt += " Kin and body parts (inalienable) take no genitive marker."
    if pp:
        txt += f" 'Having' is said with {pp}."
    ex = []
    O, P = v.w("DOG", "HOUSE"), v.w("MAN", "PERSON", "WOMAN")
    if O and P:
        ex.append(_ex(v, noun_phrase(v, O, poss=noun_phrase(v, P, _the(v))).words, f"the {en(P)}'s {en(O)}"))
    out.append({"topic": "Possession", "text": txt, "ex": ex + _sent_ex(sents, "possession")})
    H, R = v.w("WOMAN", "MAN", "PERSON"), v.w("DANCE", "SING", "LAUGH", "SHOUT", "HUNT", "CRY")
    if H and R:
        np_, note = relative(v, H, R, _the(v))
        out.append({"topic": "Relative clauses", "text": note[0].upper() + note[1:] + ".",
                    "ex": [_ex(v, np_.words, f"the {en(H)} who {_vf(R, 1)}")]})
    cop = _copula(v)
    txt = (cop[1][0].upper() + cop[1][1:] + "." if cop else "There is no copula: a predicate noun stands beside its subject.")
    if v.t.get("adjective_verb_like") == "yes":
        txt += " Adjectives behave like verbs: 'the water is cold' is said as 'the water colds', with the verb's markers."
    ex = _sent_ex(sents, "copula")
    W, C = v.w("WATER", "RIVER"), v.w("COLD", "GOOD", "BIG")
    if W and C:
        s = noun_phrase(v, W, _the(v))
        if v.t.get("adjective_verb_like") == "yes":
            pred = verb(v, C, "3SG")[0]
            words = s.words + pred if not v.order().startswith("V") else pred + s.words
        else:
            words = s.words + cop_phrase(v, NP([Word(v.ipa(C), lgloss(C), C)], 0))
        ex.append(_ex(v, words, f"the {en(W)} is {en(C)}"))
    out.append({"topic": "Copula", "text": txt, "ex": ex})
    return out


def notes_more(v: View, sents: dict) -> list[dict]:
    """Grammar phase A notes: pronouns (clusivity), voice (passive), reduplication, serial verbs, ditransitives,
    numerals. Each is written only from a live gram, a built process or a feature with its construction shown."""
    out = []
    if v.w("WE (INCLUSIVE)") and v.w("WE"):
        out.append({"topic": "Pronouns", "text": f"'We' has two forms: inclusive {v.ipa('WE (INCLUSIVE)')} (you and I, "
                    f"the hearer among us) and exclusive {v.ipa('WE')} (we, but not you).",
                    "ex": [_ex(v, pronoun(v, "WE (INCLUSIVE)").words, "we (you included)"),
                           _ex(v, pronoun(v, "WE").words, "we (not you)")] + _sent_ex(sents, "clusive")})
    g = v.g("PASS")
    if g is not None:
        out.append({"topic": "Voice", "text": f"The passive is {_how(g)} ({g['form_ipa']}, {_src(v, g)}): the object of "
                    "the active verb becomes its subject and the doer is left out.", "ex": _sent_ex(sents, "passive")})
    rd = v.proc.get("redup")
    if rd:
        what = ("copying the whole stem" if rd["shape"] == "full" else
                "copying the stem's first consonant and vowel before it" if rd["side"] == "pre" else
                "copying the stem's last consonant and vowel after it")
        mean = {"ITER": "an action done again and again, or by many", "INTS": "an action done intensely",
                "CONT": "an action going on"}[rd["fn"]]
        Vc = v.w("GO", "EAT", "SEE", "WALK")
        ex = [_ex(v, verb(v, Vc, redup=True)[0], f"({mean})")] if Vc else []
        out.append({"topic": "Reduplication", "text": f"Verbs reduplicate for {mean} ({ABBR[rd['fn']]}), by {what}.",
                    "ex": ex + _sent_ex(sents, "redup")})
    if "serial" in sents:
        txt = "Verbs can be strung together in one clause with one subject (serial verbs): 'take X come' is 'bring'."
        ex = _sent_ex(sents, "serial")
        R, Gv = v.w("RUN", "WALK", "FLY"), v.w("GO")
        if R and Gv:
            txt += f" 'Go' after a motion verb gives its direction ('{en(R)} go' = {en(R)} away)."
            ex.append(_ex(v, verb(v, R)[0] + verb(v, Gv)[0], f"{en(R)} away"))
        out.append({"topic": "Serial verbs", "text": txt, "ex": ex})
    gs = sents.get("give")
    if gs is not None:
        gn = (gs.get("note") or "").split(";")[0]
        out.append({"topic": "Giving (two objects)", "text": gn[:1].upper() + gn[1:] + ".",
                    "ex": ["give"]})
    num = numerals_note(v)
    if num:
        out.append(num)
    out += notes_phase_c(v, sents)
    out += notes_phase_d(v, sents)
    return out


def notes_phase_d(v: View, sents: dict) -> list[dict]:
    """Grammar phase D notes: demonstratives (two or three distances), polite address, comparison, obviation."""
    out = []
    N = v.w("DOG", "TREE", "HOUSE", "STONE")
    if N and v.w("THIS") and v.w("THAT"):
        ex = [_ex(v, noun_phrase(v, N, dem="THIS").words, f"this {en(N)}"),
              _ex(v, noun_phrase(v, N, dem="THAT").words, f"that {en(N)}")]
        g = dist_gram(v)
        if g is not None:
            ex.append(_ex(v, dem_np(v, N, "DIST").words, f"that {en(N)} over there (yon)"))
            that = v.ipa("THAT")
            how = ("'that' with a place word grown onto it, as English 'that there' became 'yon'"
                   if len(g["form_ipa"]) > len(that) and g["form_ipa"].startswith(that[:2]) else
                   "once 'that' with a place word, as English 'that there' became 'yon'; sound change has worn it down "
                   "since" if g.get("source", [""])[0] == "THAT" else "")
            txt = (f"Demonstratives count three distances: 'this' {v.ipa('THIS')} (near), 'that' {that} "
                   f"(further) and a far one, {_how(g)} ({g['form_ipa']}, {_src(v, g)}" + (f"; {how})" if how else ")"))
        else:
            txt = f"Demonstratives count two distances: 'this' {v.ipa('THIS')} (near) and 'that' {v.ipa('THAT')} (far)"
        out.append({"topic": "Demonstratives", "text": txt + ".", "ex": ex + _sent_ex(sents, "deixis")})
    pol = v.proc.get("polite")
    if polite_live(v):
        hon = v.g("HON")
        txt = (f"Speaking to one person with respect, one says {'the plural' if pol['kind'] == 'plural' else 'a third-person'} "
               f"pronoun {v.ipa(pol['concept'])} ('{'you all' if pol['kind'] == 'plural' else 'they'}') in place of "
               f"the plain {v.ipa('THOU') if v.w('THOU') else 'you'} (as French vous, German Sie). It arose as the "
               "speech community grew large")
        if hon is not None:
            txt += f"; the verb adds an honorific marker, {_how(hon)} ({hon['form_ipa']}, {_src(v, hon)})"
        out.append({"topic": "Polite address", "text": txt + ".", "ex": _sent_ex(sents, "polite")})
    cs = sents.get("comparative")
    if cs is not None:
        n = (cs.get("note") or "").split(";")[0]
        out.append({"topic": "Comparison", "text": n[:1].upper() + n[1:] + ".", "ex": ["comparative"]})
    g = v.g("OBV")
    if g is not None:
        out.append({"topic": "Obviation", "text": f"When two third persons meet in a clause, the one the talk is about "
                    f"stays unmarked (proximate) and the other is obviative: {_how(g)} ({g['form_ipa']}, {_src(v, g)}), as "
                    "in the Algonquian languages.", "ex": _sent_ex(sents, "obviative")})
    return out


def _portmanteau_example(v: View, a: str, b: str) -> list | None:
    """A word showing the portmanteau ending A+B (number + case on a noun, tense or aspect + person on a verb)."""
    if a in _NUMBER_FNS or a in GR.CASE_FNS or b in GR.CASE_FNS:
        N = v.w("DOG", "HOUSE", "STONE", "TREE", "FISH")
        if not N:
            return None
        np_ = noun_phrase(v, N, plural=a == "PL" or b == "PL", dual=a == "DU" or b == "DU")
        for fn in (a, b):
            if fn in GR.CASE_FNS:
                _np_gram(v, np_, fn)
        return _ex(v, np_.words, CASE_EN.get(b if b in GR.CASE_FNS else a, "{n}").format(
            n=EN_PLURAL.get(N, en(N) + "s") if "PL" in (a, b) else en(N)))
    Vc = v.w("GO", "EAT", "SEE")
    pers = next((x for x in (a, b) if x in _PERSON_EN), None)
    tam = next((x for x in (a, b) if x in TAM_ORDER), None)
    if not Vc or not pers or not tam:
        return None
    return _ex(v, verb(v, Vc, pers, tam)[0], f"{_PERSON_EN[pers]} {_tam_en(tam, Vc, pers == '3SG')}")


_NUMBER_FNS = ("PL", "DU")


def _syncretic(v: View) -> list[str]:
    """Bound markers on the same kind of host with the same form ('1SG.OBJ and 1PL.OBJ are both n')."""
    by: dict = {}
    for fn, g in sorted(v.grams.items()):
        if (g.get("level") or 0) < GR.CLITIC or fn.startswith("CLASS") or "+" in fn or fn not in GR.FUNCS:
            continue
        by.setdefault((GR.func_info(fn).host[0], g["form_ipa"]), []).append(ABBR.get(fn, fn))
    return [f"{' and '.join(fs)} are all {f}" if len(fs) > 2 else f"{fs[0]} and {fs[1]} are both {f}"
            for (_h, f), fs in sorted(by.items()) if len(fs) > 1]


def _gbit(v: View, fn: str) -> str:
    g = v.g(fn)
    return f"{GR.FUNCS[fn].gloss} ({ABBR[fn]}): {_how(g)} ({g['form_ipa']}, {_src(v, g)})"


def notes_phase_c(v: View, sents: dict) -> list[dict]:
    """Grammar phase C notes: concord, valence, clause linking, topic and focus, and the morphology types
    (inflection classes, portmanteaus, stem change, infixes, second-position clitics, incorporation, voice)."""
    out = []
    conc = v.proc.get("concord") or []
    if conc:
        what = {"dem": "demonstratives", "adj": "adjectives", "verb": "the verb (subject concord)"}
        ex = []
        N, A, D = next((c for c in ("DOG", "PERSON", "WATER", "TREE", "STONE") if v.w(c) and class_of(v, c)), None), \
            v.w("BIG", "SMALL", "GOOD", "OLD"), v.w("THAT", "THIS")
        if N:
            np_ = noun_phrase(v, N, adj=A if "adj" in conc else None, dem=D if "dem" in conc else None)
            ex.append(_ex(v, np_.words, " ".join(x for x in (en(D) if D and "dem" in conc else "",
                                                            en(A) if A and "adj" in conc else "", en(N)) if x)))
        out.append({"topic": "Concord", "text": "The noun's class marker is copied onto "
                    + " and ".join(what[c] for c in ("dem", "adj", "verb") if c in conc)
                    + " (agreement in class, as in Bantu and in Indo-European gender).", "ex": ex})
    val = [f for f in ("APPL", "RECP", "ANTIP") if v.g(f)]
    if val:
        out.append({"topic": "Valence", "text": "The verb changes how many participants it takes: "
                    + "; ".join(_gbit(v, f) for f in val) + ".",
                    "ex": [x for f, sid in (("APPL", "applicative"), ("RECP", "reciprocal"), ("ANTIP", "antipassive"))
                           if f in val for x in _sent_ex(sents, sid)]})
    if v.g("AV") or v.g("PV"):
        out.append({"topic": "Voice and pivot", "text": "Each clause picks one phrase as its pivot, and the verb's voice "
                    "says which: " + "; ".join(_gbit(v, f) for f in ("AV", "PV") if v.g(f)) + ".",
                    "ex": _sent_ex(sents, "voice_av") + _sent_ex(sents, "voice_pv")})
    link = [f for f in ("COMP", "SS", "DS") if v.g(f)]
    if link or "complement" in sents:
        txt = ("Clauses are linked by " + "; ".join(_gbit(v, f) for f in link) + "." if link else
               "Complement clauses stand bare, with no complementizer.")
        out.append({"topic": "Linking clauses", "text": txt,
                    "ex": _sent_ex(sents, "complement") + _sent_ex(sents, "chain")})
    tf = [f for f in ("TOP", "FOC") if v.g(f)]
    if tf or "topic" in sents:
        txt = ("Topic and focus are marked: " + "; ".join(_gbit(v, f) for f in tf) + "." if tf else
               "There is no topic marker, but the free word order puts the topic first.")
        out.append({"topic": "Topic and focus", "text": txt, "ex": _sent_ex(sents, "topic") + _sent_ex(sents, "focus")})
    bits, ex = [], []
    ic = v.proc.get("iclass") or {}
    for fn in sorted(ic):
        g = v.g(fn)
        if g is None or not g.get("alt_ipa"):
            continue
        bits.append(f"the {GR.FUNCS[fn].gloss} marker has two forms by inflection class, {g['form_ipa']} and "
                    f"{g['alt_ipa']}, and which a word takes must be learnt with it")
        host = GR.func_info(fn).host[0]
        pool = ("DOG", "BIRD", "FISH", "STONE", "TREE", "HOUSE", "EYE", "HAND", "FIRE", "WATER", "MAN", "WOMAN") \
            if host == "N" else ("GO", "EAT", "SEE", "DRINK", "SLEEP", "COME", "HEAR", "SIT", "GIVE", "RUN")
        ns = [c for c in pool if v.w(c)]
        one = next((c for c in ns if not GR.iclass_member(ic[fn], c)), None)
        two = next((c for c in ns if GR.iclass_member(ic[fn], c)), None)
        for c in (one, two):
            if not c:
                continue
            if fn in ("PL", "DU"):
                ex.append(_ex(v, noun_phrase(v, c, plural=fn == "PL", dual=fn == "DU").words,
                              ("two " if fn == "DU" else "") + EN_PLURAL.get(c, en(c) + "s")))
            elif fn in GR.CASE_FNS:
                np_ = noun_phrase(v, c)
                _np_gram(v, np_, fn)
                ex.append(_ex(v, np_.words, CASE_EN.get(fn, "{n}").format(n=en(c))))
            elif host == "V" and fn in _PERSON_EN:
                ex.append(_ex(v, verb(v, c, fn)[0], f"{_PERSON_EN[fn]} {_vf(c, 1 if fn == '3SG' else 0)}"))
            elif host == "V" and fn in TAM_ORDER:
                ex.append(_ex(v, verb(v, c, None, fn)[0], "(it) " + _tam_en(fn, c)))
    pm = [fn for fn in v.grams if "+" in fn]
    for fn in sorted(pm):
        a, b = fn.split("+")
        f, fa, fb = v.g(fn)["form_ipa"], (v.g(a) or {}).get("form_ipa"), (v.g(b) or {}).get("form_ipa")
        if fa and fb and f in (fa + fb, fb + fa):   # (PW-1537 R5: a plain sequence is not a portmanteau)
            continue
        bits.append(f"{ABBR.get(a, a)} and {ABBR.get(b, b)} together are one ending, {f}, that does "
                    "not split into the two (cumulative exponence)")
        r = _portmanteau_example(v, a, b)
        if r:
            ex.append(r)
    same = _syncretic(v)
    if same:
        bits.append("some markers sound the same: " + "; ".join(same) + " (context tells them apart)")
    for fn, vmap in sorted((v.proc.get("stem_change") or {}).items()):
        if v.g(fn) is not None:
            continue   # (a live marker of its own is shown instead)
        name = f"{fn} subject ({_PERSON_EN[fn]})" if fn in _PERSON_EN else GR.func_info(fn).gloss
        bits.append(f"the {name} is shown by a change of the stem's vowel ("
                    + ", ".join(f"{a} > {b}" for a, b in vmap) + "), its old ending long gone")
        pool = ("DOG", "BIRD", "FISH", "STONE", "TREE", "HOUSE", "WATER", "FIRE", "EYE", "HAND", "MAN", "WOMAN") \
            if GR.func_info(fn).host[0] == "N" else ("EAT", "SEE", "GO", "DRINK", "SLEEP", "COME", "HEAR", "SIT", "GIVE")
        for N in (c for c in pool if v.w(c)):
            ws = [Word(v.ipa(N), lgloss(N), N)]
            if _stem_change(v, ws[0], fn, ABBR.get(fn, fn)):
                ex.append(_ex(v, ws, f"{_PERSON_EN[fn]} {_vf(N, 1 if fn == '3SG' else 0)}" if fn in _PERSON_EN
                              else f"{en(N)} ({GR.func_info(fn).gloss})"))
                break
    inf = v.proc.get("infix")
    if inf and v.g(inf["fn"]):
        bits.append(f"the {GR.func_info(inf['fn']).gloss} marker {v.g(inf['fn'])['form_ipa']} is an infix, placed after "
                    "the stem's first consonant")
        Vc = next((c for c in ("EAT", "SEE", "GO", "DRINK", "SIT", "CARRY") if v.w(c) and
                   (_segs(v.ipa(c)) or [None])[0] is not None and not is_V(_segs(v.ipa(c))[0])), None)
        if Vc:
            ws = [Word(v.ipa(Vc), lgloss(Vc), Vc)]
            attach(v, ws, 0, inf["fn"])
            ex.append(_ex(v, ws, f"{en(Vc)} ({GR.func_info(inf['fn']).gloss})"))
    if v.proc.get("second"):
        bits.append("the verb's clitics stand in second position, after the first word of the clause (Wackernagel's "
                    "law)")
    if v.proc.get("incorp"):
        bits.append("a generic object noun can be incorporated into the verb")
        ex += _sent_ex(sents, "incorp")
    if bits:
        out.append({"topic": "Word shapes", "text": "; ".join(bits)[0].upper() + "; ".join(bits)[1:] + ".", "ex": ex})
    return out


_SYSTEM_LEAD = {
    "decimal": "Counting is decimal: numbers above ten are built from ten and the units",
    "hybrid": "Counting is in twenties, with ten and the units inside each twenty (as French quatre-vingt-dix, 'four "
              "twenty ten')",
    "vigesimal": "Counting is in twenties: twenty, two twenties, a hundred as five twenties",
    "quinary": "Counting builds on five: six to nine are 'five and one' to 'five and four', ten is 'two fives'",
    "restricted": "Counting is restricted: a few number words, then hands and persons ('two hands' for ten, 'one "
                  "person' for twenty), and 'many' for a hundred and more"}   # (PW-1537 R8: thirty and forty are built)


def _bare(ipa: str) -> str:
    """IPA without tone letters, length and stress marks, for comparing forms by ear."""
    return re.sub(r"[˥˦˧˨˩ːˑˈˌ̀-ͯ]", "", ipa)


def _part_heard(part: str, word: str) -> bool:
    """A compound's part can be heard in it: as `audibly_shares`, or its first two sounds anywhere in the word (a
    compound clips its parts: kawan + pulu > kawpu)."""
    a = _bare(part)
    return audibly_shares(part, word) or (len(a) >= 2 and a[:2] in _bare(word))


def audibly_shares(root: str, word: str) -> bool:
    """Does `word` contain the root word's form (tones and length aside), or for a long root its first or last three
    sounds? A semantic shift, old derivation or compound whose form has drifted away from the root's is not felt."""
    a, b = _bare(root), _bare(word)
    if not a:
        return True
    if len(a) <= 2:   # (a two-sound root heard only at a word's edge: 'ma' inside any word is chance)
        return b.startswith(a) or b.endswith(a)
    return a in b or a[:3] in b or a[-3:] in b


def numerals_note(v: View) -> dict | None:
    """The lect's own counting system (lexsys: `systems.numeral`) and its own number words (polish lane: the note built
    11 'ten one' from the typology label while the lexicon's ELEVEN had its system's recipe and form, so the note and
    the word lists disagreed): each composite numeral as the word the lect says, with the recipe it was built by."""
    from . import lexsys as LS
    sy = (v.lj.get("systems") or {}).get("numeral") or {}
    system = sy.get("system")
    if system not in _SYSTEM_LEAD:
        return None
    rec = LS._recipes(system, bool(sy.get("quinary")))
    ex = []
    for c in ("SIX", "ELEVEN", "FIFTEEN", "THIRTY", "FORTY", "HUNDRED", "TEN"):
        r = rec.get(c)
        if r is None or r[2] == "same" or not v.w(c) or len(ex) >= 4:
            continue
        h, m, op = r
        n, a, b = LS.NUM_VALUE[c], LS.NUM_VALUE.get(h, h.lower()), LS.NUM_VALUE.get(m, m.lower())
        how = f"{a} {'+' if op == 'add' else '×'} {b}"
        if v.w(h) and v.w(m) and _part_heard(v.ipa(h), v.ipa(c)) and _part_heard(v.ipa(m), v.ipa(c)):
            text = f"{n} = {how} ('{en(h)}' and '{en(m)}')"
        else:   # (PW-1537 R8: a composition is printed only where both parts can still be heard in the form)
            text = f"{n}: built as {how} ('{en(h)}' and '{en(m)}'), now worn past recognition"
        ex.append(_ex(v, [Word(v.ipa(c), str(n), c)], text))
    if not ex:
        return None
    lead = _SYSTEM_LEAD[system]
    if sy.get("quinary") and system in ("decimal", "hybrid", "vigesimal"):
        lead += "; six to nine are built on five ('five one' for six)"
    words = [c for c in ("TWENTY", "HUNDRED") if v.w(c)]
    tail = (" " + " and ".join(f"{('Twenty' if c == 'TWENTY' else 'a hundred')} is {v.ipa(c)}" for c in words) + "."
            if words else "")
    return {"topic": "Numerals", "text": lead + "." + tail, "ex": ex}


def _sent_ex(sents: dict, sid: str) -> list:
    """A sample sentence as a note's example: by its id (a string; `example` resolves it), not a copy."""
    return [sid] if sid in sents else []


def example(lj: dict, ex) -> list | None:
    """A grammar note's example as [form line, gloss line, English, sentence or None]: a list as stored, or a sentence id
    (a string) resolved against the lect's `sentences`."""
    if isinstance(ex, str):
        s = next((x for x in lj.get("sentences") or [] if x["id"] == ex), None)
        if s is None:
            return None
        return [" ".join(w[0] for w in s["w"]), " ".join(w[1] for w in s["w"]), s["en"], s]
    return [*ex[:3], None]


def grammar_notes(lj: dict, sents: list | None = None) -> list[dict]:
    v = View(lj)
    by = {s["id"]: s for s in (sents if sents is not None else utterances(lj))}
    out = []
    for fn in (notes_nouns, notes_verbs):
        try:
            out += fn(v)
        except (KeyError, IndexError, ValueError, StopIteration):
            continue
    for fn in (notes_clause, notes_more):
        try:
            out += fn(v, by)
        except (KeyError, IndexError, ValueError, StopIteration):
            continue
    for n in out:
        n["text"] = _second_fix(v, _shown_forms(v, n, by))
    return out


def _morph_pairs(form: str, gloss: str):
    """(gloss piece, form piece) for each morph of an interlinear example, words and morphs aligned by '-' and '='."""
    for f, g in zip(form.split(" "), gloss.split(" ")):
        fp, gp = re.split(r"[-=]", f), re.split(r"[-=]", g)
        if len(fp) == len(gp):
            yield from zip(gp, fp)


def _where(base: str, var: str, cons: set) -> str:
    """Why a marker's form in an example differs from its base form: the joining rules, or the stored word form."""
    if var == ZERO:
        return "not heard (∅) in some words, where sound change has worn it into the stem"
    if len(var) > len(base) and var.endswith(base) and var[: len(var) - len(base)] in cons:
        gl = var[: len(var) - len(base)]
        return f"{var} after " + ("a front or central vowel" if gl == _GLIDE_FRONT else
                                  "a back or rounded vowel" if gl == _GLIDE_BACK else "a vowel")
    b, w = _segs(base), _segs(var)
    if b and w and len(b) == len(w) and b[:-1] == w[:-1] and b[-1].kind == "C" and b[-1].manner == 3:
        return f"{var} before a stop"
    return f"{var} in some words (sound change at the join)"


def _shown_forms(v: View, note: dict, by: dict) -> str:
    """A note quotes each marker's base form; where its examples show it only in another shape (a glide before it after
    a vowel, a nasal that took a stop's place, a form sound change reshaped on a stored word) the note says so, so the
    prose and the examples agree."""
    seen: dict[str, set] = {}
    merged: dict[str, set] = {}   # (a marker shown only inside an unsegmented word: go.1SG)
    for x in note.get("ex") or []:
        s = by.get(x) if isinstance(x, str) else None
        form, gloss = ((" ".join(w[0] for w in s["w"]), " ".join(w[1] for w in s["w"])) if s else
                       (x[0], x[1]) if isinstance(x, list) else ("", ""))
        for gp, fp in _morph_pairs(form, gloss):
            seen.setdefault(gp, set()).add(fp)
            parts = gp.split(".")
            for k in range(1, len(parts)):
                merged.setdefault(".".join(parts[k:k + 2]) if ".".join(parts[k:k + 2]) in ABBR.values() else parts[k],
                                  set()).add(f"{fp} '{gp}'")
    text = note["text"]
    for fn, g in sorted(v.grams.items()):
        base, lab = g.get("form_ipa"), ABBR.get(fn, fn)
        if not base or f"({base}, " not in text:
            continue
        at = _slot(text, base, (lab, fn, (GR.FUNCS[fn].gloss if fn in GR.FUNCS else fn)))
        if at < 0:
            continue
        if lab in seen and base not in seen[lab]:
            alts = "; ".join(_where(base, x, v.cons) for x in sorted(seen[lab]))
        elif lab not in seen and lab in merged:
            alts = "fused into one ending with the marker beside it in " + ", ".join(sorted(merged[lab]))
        else:
            continue
        k = at + len(f"({base}")
        text = text[:k] + f"; {alts}; " + text[k + 2:]   # (after the '(form': ', from ...' becomes '; from ...')
    return text


def _slot(text: str, base: str, names: tuple) -> int:
    """Where a marker's '(form, ' stands in a note: the occurrence whose clause (since the last ';' or full stop) names the
    marker, so two markers with one form are told apart; else the only occurrence; else -1."""
    pat = f"({base}, "
    hits = [i for i in range(len(text)) if text.startswith(pat, i)]
    for i in hits:
        lead = re.split(r"; |\. ", text[:i])[-1]
        if any(n and re.search(rf"(^|[\s(]){re.escape(n)}([\s):,]|$)", lead) for n in names):
            return i
    return hits[0] if len(hits) == 1 else -1


def enrich(lj: dict) -> dict:
    """Add `sentences` and `grammar_notes` to a living lect's record (in place); returns it."""
    s = utterances(lj)
    lj["sentences"] = s
    lj["grammar_notes"] = grammar_notes(lj, s)
    return lj


def header_sample(lj: dict) -> dict | None:
    """The short sample the viewer's header plays: the first sentence."""
    s = lj.get("sentences") or []
    return s[0] if s else None
