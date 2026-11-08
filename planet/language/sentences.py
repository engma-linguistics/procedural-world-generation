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

from dataclasses import dataclass, field

from . import grammar as GR
from .percepts import from_ipa, is_V, word_ipa

# ---- Leipzig glosses ------------------------------------------------------------------------------------------------------

ABBR = {"PL": "PL", "DU": "DU", "DEF": "DEF", "INDEF": "INDF", "GEN": "GEN", "LOC": "LOC", "ABL": "ABL", "ALL": "ALL",
        "DAT": "DAT", "ACC": "ACC", "ERG": "ERG", "INS": "INS", "COM": "COM", "DIM": "DIM", "AGENT": "AGT",
        "PLACE": "PLACE", "PAST": "PST", "RECPST": "PST.RCT", "FUT": "FUT", "PERF": "PRF", "PROG": "PROG",
        "IPFV": "IPFV", "HAB": "HAB", "EVID.DIR": "DIR", "EVID.REP": "REP", "NEG": "NEG", "CAUS": "CAUS",
        "PASS": "PASS", "REFL": "REFL", "Q": "Q", "REL": "REL", "COP": "COP", "CLF": "CLF"}
#: abbreviations that are not in the Leipzig list, explained on the pages
EXTRA_ABBR = {"PST.RCT": "recent past", "DIR": "direct (witnessed) evidential", "REP": "reported evidential",
              "AGT": "agent noun", "CL": "noun class", "CLF": "classifier", "ANIM": "animate", "INAN": "inanimate"}
#: English gloss of a pronoun concept
PRON = {"I": "1SG", "THOU": "2SG", "HE OR SHE OR IT": "3SG", "WE": "1PL", "YOU": "2PL", "THEY": "3PL"}
CASE_EN = {"GEN": "of the {n}", "LOC": "in the {n}", "ABL": "from the {n}", "ALL": "to the {n}", "DAT": "to/for the {n}",
           "ACC": "the {n} (as object)", "ERG": "the {n} (as doer)", "INS": "with (using) the {n}", "COM": "with the {n}"}
TAM_ORDER = ("PAST", "RECPST", "PERF", "FUT", "PROG", "IPFV", "HAB")
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
        hit = next((by[a] for a in ("abstract", "manner", "plant", "animal") if a in by), None)
    if hit is None:
        k, g0, f = cs["classes"][-1]
        hit = (k, f)
        want = g0
    else:
        want = next(g for g, kf in by.items() if kf == hit)
    k, f = hit
    if grp_of(cs, f) != _want(cs, concept):
        return f, f"CL{k}"   # (the noun's own class is missing; the engine falls back on another, so no gender label)
    lab = {"masculine": "M", "feminine": "F", "animate": "ANIM", "inanimate": "INAN"}.get(want, f"CL{k}")
    if kind in ("sex", "animacy") and want == "abstract":
        lab = "N" if kind == "sex" else "INAN"
    return f, lab


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


@dataclass
class Word:
    form: str
    gloss: str
    concept: str | None = None
    pre: list = field(default_factory=list)
    post: list = field(default_factory=list)
    fns: list = field(default_factory=list)      # bound gram functions on the word (for paradigm cells)

    def add(self, form: str, gloss: str, level: int, side: str, fn: str | None = None) -> "Word":
        m = Morph(form, gloss, "=" if level == GR.CLITIC else "-", _rank(fn) + (100 if level == GR.CLITIC else 0))
        (self.pre if side == "pre" else self.post).append(m)
        if fn and level >= GR.AFFIX:
            self.fns.append(fn)
        return self

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
    try:
        return GR.SLOT_ORDER.index(GR.func_info(fn).slot)
    except Exception:  # noqa: BLE001
        return len(GR.SLOT_ORDER)


def render_word(v: View, w: Word) -> tuple[str, str, str]:
    """(form line with breaks, gloss line with the same breaks, surface IPA). A noun or verb whose bound grams make a
    stored paradigm cell takes the cell's form (the engine's own, with any alternation sound change left in it)."""
    ms = w.morphs()
    forms = [m[0] for m in ms]
    cell = _cell(v, w)
    inner = [i for i, m in enumerate(ms) if not m[3]]
    if cell is not None:
        pieces = cell.split("-")
        if len(pieces) == len(inner):
            for i, x in zip(inner, pieces):
                forms[i] = x
        else:
            cell = None
    for i in range(len(forms) - 1):
        if cell is not None and not (ms[i][3] or ms[i + 1][3]):
            continue   # (inside a stored cell the engine's own forms stand)
        forms[i], forms[i + 1] = join(forms[i], forms[i + 1], v.cons)
    fl, gl = forms[0], ms[0][1]
    for i in range(1, len(ms)):
        fl += ms[i][2] + forms[i]
        gl += ms[i][2] + ms[i][1]
    return fl, gl, "".join(forms)


def _cell(v: View, w: Word) -> str | None:
    if not w.concept or not w.fns:
        return None
    row = v.cells.get(w.concept)
    if not row or (row.get("cells") or {}).get("lemma", {}).get("ipa") != w.form:
        return None
    key = ".".join(sorted(w.fns, key=lambda f: (_rank(f), f)))
    seg = (row.get("segmented") or {}).get(key)
    if seg:
        return seg
    c = (row.get("cells") or {}).get(key)
    return None if not c else c.get("ipa")


# ---- phrases ------------------------------------------------------------------------------------------------------------

@dataclass
class NP:
    words: list            # list[Word], in order
    head: int              # index of the noun
    person: str = "3SG"    # agreement person of the phrase
    notes: list = field(default_factory=list)


def gram_word(g: dict, fn: str) -> Word:
    return Word(g["form_ipa"], ABBR.get(fn, fn))


def attach(v: View, words: list, idx: int, fn: str, label: str | None = None) -> bool:
    """Put gram `fn` on words[idx] if it is bound (clitic or affix); a free gram is inserted beside it. Returns False when
    the lect has no such gram."""
    g = v.g(fn)
    if g is None:
        return False
    lab = label or ABBR.get(fn, fn)
    lv = g.get("level") or 0
    side = g.get("side") or "post"
    if lv >= GR.CLITIC:
        words[idx].add(g["form_ipa"], lab, min(lv, GR.AFFIX) if lv >= GR.AFFIX else GR.CLITIC, side, fn)
    else:
        words.insert(idx if side == "pre" else idx + 1, Word(g["form_ipa"], lab))
    return True


def noun_phrase(v: View, concept: str, det: str | None = None, adj: str | None = None, num: str | None = None,
                poss: "NP | None" = None, plural: bool = False, dem: str | None = None, inalienable: bool = False,
                gloss: str | None = None) -> NP:
    """Dem Num Adj N, mirrored for postnominal modifiers (Greenberg's Universal 20 orders); the possessor outermost."""
    notes = []
    n = Word(v.ipa(concept), gloss or lgloss(concept), concept)
    cl = class_of(v, concept)
    if cl is not None and (v.g(cl[0]) or {}).get("level", 0) >= GR.CLITIC:
        attach(v, [n], 0, cl[0], cl[1])
    core = [n]
    if plural:
        pl = v.g("PL")
        if pl is not None and ((pl.get("level") or 0) >= GR.AFFIX or not num):
            attach(v, core, 0, "PL")
        elif pl is not None:
            notes.append("no plural marker after a numeral (the marker is not yet obligatory)")
    head = next(i for i, x in enumerate(core) if x is n)
    pre, post = [], []
    if adj:
        a = Word(v.ipa(adj), lgloss(adj), adj)
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
    np_ = NP(words, head, "3PL" if plural else "3SG", notes)
    if det == "DEF":
        _np_gram(v, np_, "DEF")
    elif det == "INDEF":
        _np_gram(v, np_, "INDEF")
    if poss is not None:
        gen = None if inalienable and v.t.get("alienability") == "yes" else v.g("GEN")
        pw = list(poss.words)
        if gen is not None:
            tmp = NP(pw, poss.head)
            _np_gram(v, tmp, "GEN")
            pw = tmp.words
        if v.before("genitive", "GN"):
            np_.head += len(pw)
            np_.words = pw + np_.words
        else:
            np_.words = np_.words + pw
        if inalienable and v.t.get("alienability") == "yes":
            notes.append("kin are inalienably possessed: the possessor stands beside the noun with no marker")
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


def _np_gram(v: View, np_: NP, fn: str) -> bool:
    """A noun-phrase gram (article, case): bound ones go on the edge word of its side, free ones stand at that edge."""
    g = v.g(fn)
    if g is None:
        return False
    side = g.get("side") or "post"
    lv = g.get("level") or 0
    host = g.get("host") or "NP"
    if host == "N":
        return attach(v, np_.words, np_.head, fn)
    if lv >= GR.CLITIC:
        idx = 0 if side == "pre" else len(np_.words) - 1
        if lv >= GR.AFFIX:
            idx = np_.head   # an affix stays on the noun
        np_.words[idx].add(g["form_ipa"], ABBR.get(fn, fn), GR.AFFIX if lv >= GR.AFFIX else GR.CLITIC, side, fn)
    else:
        w = Word(g["form_ipa"], ABBR.get(fn, fn))
        if side == "pre":
            np_.words.insert(0, w)
            np_.head += 1
        else:
            np_.words.append(w)
    return True


def pronoun(v: View, concept: str) -> NP | None:
    if not v.w(concept):
        return None
    return NP([Word(v.ipa(concept), PRON.get(concept, lgloss(concept)), concept)], 0, PRON.get(concept, "3SG"))


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
    return np_, f"'{en(c)}' as a {'preposition' if pre else 'postposition'} (no {ABBR.get(fn, fn)} gram)"


# ---- the verb -----------------------------------------------------------------------------------------------------------

def verb(v: View, concept: str, person: str | None = None, tam: str | None = None, neg: bool = False,
         gloss: str | None = None) -> tuple[list, int, list]:
    """The verb with its grams: (words, index of the verb, notes). Bound grams go on the verb, free ones (auxiliaries,
    particles) beside it on their side, inner ones nearest."""
    notes = []
    vw = Word(v.ipa(concept), gloss or lgloss(concept), concept)
    words = [vw]
    if tam:
        attach(v, words, words.index(vw), tam)
    if person:
        g = v.g(person)
        if g is not None and (g.get("level") or 0) >= GR.CLITIC:
            attach(v, words, words.index(vw), person)
            notes.append(f"the verb carries the subject's {person} marker")
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

def clause(v: View, S: NP | None, Vw: tuple, O: NP | None = None, X: NP | None = None, transitive: bool = True) -> list:
    """Order S, O and the verb complex by the basic word order (free order: by head direction, and the note says so); an
    oblique X stands before the verb in OV lects and after the object in VO ones. Case by alignment: ACC on the object
    (nominative-accusative), ERG on the transitive subject (ergative). Clause-edge negators move to the edge."""
    words, _vi, _n = Vw
    if transitive and O is not None:
        al = v.t.get("alignment", "neutral")
        if al in ("nom-acc", "split") and v.g("ACC") is not None:
            _np_gram(v, O, "ACC")
        if al in ("erg-abs",) and S is not None and v.g("ERG") is not None:
            _np_gram(v, S, "ERG")
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
    return out


def finish(v: View, sid: str, en_text: str, words: list, note: list, q: bool = False) -> dict:
    rows, surf = [], []
    for w in words:
        fl, gl, s = render_word(v, w)
        rows.append([fl, gl])
        surf.append(s)
    ipa = " ".join(surf)
    try:
        from . import romanize as RO
        segs = v.segs()
        roman = " ".join(RO.romanize(s, inventory=segs) for s in surf)
    except Exception:  # noqa: BLE001
        roman = ipa
    out = {"id": sid, "en": en_text, "w": rows, "ipa": ipa, "roman": roman}
    if q:
        out["q"] = 1
    nt = "; ".join(x for x in dict.fromkeys(note) if x)
    if nt:
        out["note"] = nt
    return out


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
    if fn in ("PROG", "IPFV"):
        return ("is " if third else "am ") + _vf(c, 4)
    if fn == "HAB":
        return ("usually " + _vf(c, 1)) if third else "usually " + _vf(c, 0)
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
    words = clause(v, s, vw, o)
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
    if pq in ("initial_particle", "final_particle") and qp:
        w = Word(qp, "Q")
        if pq == "initial_particle":
            words.insert(0, w)
        else:
            words.append(w)
        notes.append(f"a {'clause-initial' if pq == 'initial_particle' else 'clause-final'} question particle, the word "
                     f"for 'if, whether' (as Russian li is both); no question gram is tracked")
    elif pq == "verb_morph" and qp:
        vword = vw[0][vw[1]]
        side = "post" if v.ov() else "pre"
        vword.add(_first_syllable(qp), "Q", GR.CLITIC, side)
        notes.append("the verb takes a question clitic, cut down from the word for 'if, whether'; no question gram is "
                     "tracked")
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
        qw = next(w for w in words if w.concept == Q)
        words.remove(qw)
        words.insert(0, qw)
        note = "the question word moves to the front"
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
        cop = _copula(v)
        vw = ([Word(cop[0], "COP")], 0, []) if cop else ([], 0, [])
        words = x[0].words + (vw[0] if not v.ov() else []) + thing.words + (vw[0] if v.ov() else [])
        notes += ["locational possession ('at my mother (is) a dog')", x[1]]
    else:
        x = oblique(v, thing, "COM", ("WITH",))
        if x is None:
            return None
        cop = _copula(v)
        words = owner.words + ((([Word(cop[0], "COP")] if cop else []) + x[0].words) if not v.ov() else
                               (x[0].words + ([Word(cop[0], "COP")] if cop else [])))
        notes += ["possession with 'with' ('my mother (is) with a dog'; Grambank marks neither a 'have' verb nor "
                  "locational possession, and the lane picked the conjunctional type)", x[1]]
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
    if v.t.get("copula") != "yes":
        return None
    c = v.w("HE OR SHE OR IT", "THAT", "SIT", "STAND")
    if c is None:
        return None
    return v.ipa(c), f"the copula is the word for '{en(c) if c != 'HE OR SHE OR IT' else 'he, she, it'}' (G056)"


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
        cw = [Word(cop[0], "COP")]
        words = s.words + (pred.words + cw if v.ov() else cw + pred.words)
        notes.append(cop[1] + f", in the verb's place ({'after' if v.ov() else 'before'} the predicate)")
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
    if kind == "NRel":
        rel = [Word(v.ipa(that), "REL")] if that else []
        np_ = NP(hn.words + rel + rv, hn.head)
        return np_, "relative clause after the noun" + (", introduced by the word for 'that' (G055)" if that else "")
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
    return np_, "a correlative: 'who sings, that woman' (the typology's 'other' relative type)"


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


SENTENCES = (s_transitive, s_locative, s_tense, s_polar, s_content, s_negation, s_possession, s_number, s_copula,
             s_relative)


def utterances(lj: dict) -> list[dict]:
    v = View(lj)
    out = []
    for fn in SENTENCES:
        try:
            s = fn(v)
        except (KeyError, IndexError, ValueError, StopIteration):
            s = None
        if s is not None:
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
    return f"{'a prefix' if g.get('side') == 'pre' else 'a suffix'}{' fused with the stem' if lv >= GR.FUSED else ''}"


def _ex(v: View, words: list, en_text: str) -> list:
    fl, gl = [], []
    for w in words:
        f, g, _s = render_word(v, w)
        fl.append(f)
        gl.append(g)
    return [" ".join(fl), " ".join(gl), en_text]


def _src(g: dict) -> str:
    src = g.get("source") or ["?"]
    s = src[0]
    if len(src) > 2 and src[2] == "gram" and s in GR.FUNCS:
        return f"from the {GR.FUNCS[s].gloss} marker"
    return f"from '{en(s)}'" if s and s != "?" else "a coined form"


_CASE_NOUN = {"GEN": ("MAN", "PERSON"), "DAT": ("MAN", "PERSON"), "ACC": ("DOG", "FISH"), "ERG": ("MAN", "PERSON"),
              "INS": ("STONE", "KNIFE", "STICK"), "COM": ("DOG", "FRIEND", "PERSON")}


def notes_nouns(v: View) -> list[dict]:
    out = []
    N = v.w("DOG", "BIRD", "FISH", "STONE", "TREE")
    # number
    nums = [f for f in ("PL", "DU") if v.g(f)]
    if nums and N:
        txt = "; ".join(f"{GR.FUNCS[f].gloss}: {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v.g(f))})" for f in nums)
        ex = [_ex(v, noun_phrase(v, N).words, f"{en(N)}"), _ex(v, noun_phrase(v, N, plural=True).words,
                                                              EN_PLURAL.get(N, en(N) + "s"))]
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
              "split": "Alignment is split: both an accusative and an ergative marker are live."}.get(alv, "")
    elif alv == "neutral":
        al = "Subject and object are not marked apart: word order tells them."
    else:
        al = (f"The typology leans {alv.replace('-', '-')} in alignment, but no case marker shows it yet: word order "
              "tells subject from object.")
    H = v.w("HOUSE", "RIVER", "TREE", "STONE")
    if cases and H:
        bits = [f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v.g(f))})" for f in bound]
        fbits = [f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v.g(f))})" for f in free]
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
        for k, grp, f in cs["classes"]:
            g = v.g(f)
            if g is None:
                continue
            rows.append(f"{f.replace('CLASS:', 'class ')} for {GR.GROUP_GLOSS.get(grp, grp)}, {_how(g)} ({g['form_ipa']}, "
                        f"{_src(g)})")
            n = _noun_of_group(v, kind, grp)
            if n and len(ex) < 4:
                ex.append(_ex(v, noun_phrase(v, n).words, en(n)))
        bound_cls = any((v.g(f) or {}).get("level", 0) >= GR.CLITIC for _k, _g, f in cs["classes"])
        lead = {"sex": "Nouns fall into genders by sex", "animacy": "Nouns fall into genders by animacy",
                "classes": "Nouns fall into noun classes by meaning", "classifiers": "Nouns are counted with classifiers"
                }.get(kind, "Nouns fall into classes")
        if not bound_cls:
            lead = "Nouns are counted with classifiers (free words, not yet bound to the noun)"
        out.append({"topic": "Gender and noun classes", "text": lead + ": " + "; ".join(rows) + ".", "ex": ex})
    else:
        out.append({"topic": "Gender and noun classes", "text": "There is no gender or noun class.", "ex": []})
    return out


def _noun_of_group(v: View, kind: str, grp: str) -> str | None:
    pool = {"person": ("PERSON", "MAN", "WOMAN"), "people": ("PEOPLE",), "manner": ("TONGUE", "WORD", "SONG"),
            "abstract": ("NAME", "DAY (NOT NIGHT)", "STONE"), "plant": ("TREE", "GRASS", "LEAF"), "animal": ("DOG", "BIRD"),
            "liquid": ("WATER", "BLOOD", "MILK"), "place": ("RIVER", "HOUSE", "MOUNTAIN"), "small": ("EGG", "SEED"),
            "masculine": ("MAN", "FATHER"), "feminine": ("WOMAN", "MOTHER"), "animate": ("PERSON", "DOG"),
            "inanimate": ("STONE", "WATER")}.get(grp, ())
    for c in pool:
        if v.w(c) and (class_of(v, c) or ("",))[0] == next((f for _k, g, f in v.classes["classes"] if g == grp), None):
            return c
    return None


def notes_verbs(v: View) -> list[dict]:
    out = []
    Vc = v.w("GO", "EAT", "SEE", "WALK")
    tams = [f for f in TAM_ORDER if v.g(f)]
    evs = [f for f in ("EVID.DIR", "EVID.REP") if v.g(f)]
    if Vc and tams:
        txt = "; ".join(f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v.g(f))})"
                        for f in tams)
        ex = [_ex(v, verb(v, Vc, None, f)[0], "(it) " + _tam_en(f, Vc)) for f in tams[:4]]
        unmarked = [k for k in ("past", "future", "perfective", "progressive", "habitual") if v.t.get(k) != "marked"]
        out.append({"topic": "Tense and aspect", "text": "Verbs mark tense and aspect. " + txt[0].upper() + txt[1:] + "." + (
            f" Unmarked: {', '.join(unmarked)} (left to context)." if unmarked else ""), "ex": ex})
    else:
        y = v.w("YESTERDAY")
        out.append({"topic": "Tense and aspect", "text": "Verbs carry no tense or aspect: time is left to context or to "
                    "words like 'yesterday'" + (f" ({v.ipa(y)})" if y else "") + ".", "ex": []})
    if evs and Vc:
        txt = "; ".join(f"{GR.FUNCS[f].gloss} ({ABBR[f]}): {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v.g(f))})"
                        for f in evs)
        ex = [_ex(v, verb(v, Vc, None, f)[0], "(it) " + _vf(Vc, 1) + (", I saw it" if f == "EVID.DIR" else
                                                                       ", they say")) for f in evs]
        out.append({"topic": "Mood and evidentiality", "text": "Speakers mark how they know: " + txt + ".", "ex": ex})
    else:
        out.append({"topic": "Mood and evidentiality", "text": "No evidential or mood marker is live; statements are "
                    "unmarked.", "ex": []})
    # person agreement
    pers = [f for f in GR.PERSON_FNS if v.g(f)]
    bound = [f for f in pers if (v.g(f).get("level") or 0) >= GR.CLITIC]
    free = [f for f in pers if f not in bound]
    if bound and Vc:
        txt = "; ".join(f"{f}: {_how(v.g(f))} ({v.g(f)['form_ipa']}, {_src(v.g(f))})" for f in bound)
        ex = [_ex(v, verb(v, Vc, f)[0], f"{_PERSON_EN[f]} {_vf(Vc, 1 if f == '3SG' else 0)}") for f in bound[:4]]
        pd = (" Subject pronouns are dropped when the marker is there." if v.t.get("pro_drop") == "yes" else "")
        missing = [f for f in GR.PERSON_FNS if f not in bound]
        out.append({"topic": "Person agreement", "text": "Verbs agree with the subject: " + txt + "." + pd + (
            f" No marker yet for {', '.join(missing)} (zero)." if missing else ""), "ex": ex})
    else:
        txt = "Verbs do not agree with the subject."
        if free:
            txt += " Pronoun-like words stand beside the verb (" + ", ".join(f"{f} {v.g(f)['form_ipa']}" for f in free) + \
                   "), on their way to becoming agreement."
        out.append({"topic": "Person agreement", "text": txt, "ex": []})
    return out


_PERSON_EN = {"1SG": "I", "2SG": "you", "3SG": "he/she", "1PL": "we", "2PL": "you all", "3PL": "they"}


def notes_clause(v: View, sents: dict) -> list[dict]:
    out = []
    g = v.g("NEG")
    nv = v.t.get("negation", "preverbal").replace("_", " ")
    if g is not None:
        txt = f"Negation is {_how(g)} ({g['form_ipa']}, {_src(g)}); the typology calls it {nv}."
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
    gen = v.g("GEN")
    pp = {"have": "a 'have' verb ('my mother has a dog')", "locational": "a locational phrase ('at my mother is a dog')",
          "other": "'with' ('my mother is with a dog'; the lane's pick for Grambank's 'neither')"
          }.get(v.t.get("predicative_possession"), "")
    txt = (f"The possessor stands {'before' if v.before('genitive', 'GN') else 'after'} the possessed noun"
           + (f", marked by the genitive {_how(gen)} ({gen['form_ipa']})" if gen else ", with no marker") + ".")
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
            a = [Word(v.ipa(C), lgloss(C), C)]
            cw = [Word(cop[0], "COP")] if cop else []
            words = s.words + ((a + cw) if v.ov() else (cw + a))
        ex.append(_ex(v, words, f"the {en(W)} is {en(C)}"))
    out.append({"topic": "Copula", "text": txt, "ex": ex})
    return out


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
    try:
        out += notes_clause(v, by)
    except (KeyError, IndexError, ValueError, StopIteration):
        pass
    return out


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
