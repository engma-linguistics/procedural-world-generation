"""Connected glossed texts: a fixed fable told in a proto-language and its daughters (Schleicher's way of showing sound
change and grammar change through one text), and a short recipe per living language.

Like sentences.py, everything here reads one lect's json record and draws nothing: each clause is built by the sentence
builder (`sentences.noun_phrase`, `verb`, `clause`, `finish`), so a text shows the same grammar as the sample sentences.
A text sentence whose words the lexicon lacks is left out, and `complete` says whether the whole text could be told.

Every sentence comes back in the sentence shape (`{id, en, w: [[form, gloss]...], ipa, roman, note?}`): a page shows it in
four lines, book spelling (`roman`), IPA (the forms with their morph breaks), gloss and English.

The fable uses only Swadesh-100 words, because a proto-language's record keeps only those (`lexicon_full` false); the
recipe uses the people's own staple and fuel words where the lexicon has them (the cuisine data the lexicon lane put in),
and plain words otherwise. The myth tells what the run's faith data holds and nothing more (`myth`): which god holds which
domain, what the high god gives, which foods are forbidden because they belong to a god, and a closing invocation."""
from __future__ import annotations

import re

from . import grammar as GR
from . import sentences as SN

#: the fable, in English: one line per sentence (the title is not glossed)
FABLE_TITLE = "The Bird and the Fish"
FABLE_EN = (
    "A bird sat in a tree.",
    "The bird saw a fish in the water.",
    "The bird said: “Come! I will give you a good seed.”",
    "The fish said: “I do not eat seeds. You will eat me.”",
    "The fish did not come.",
    "The bird ate the seed.",
)
#: the Swadesh-100 words the fable needs (a lect lacking one tells the fable without that sentence)
FABLE_WORDS = ("BIRD", "SIT", "TREE", "SEE", "FISH", "WATER", "SAY", "COME", "I", "GIVE", "THOU", "GOOD", "SEED", "EAT",
               "NOT")

#: taboo targets (taboos.json) -> the concept naming them (English as taboos.json labels them); targets with no word are
#: left out of the myth (eels: no 'eel' concept; 'fish' would say more than the taboo does)
TABOO_CONCEPT = {"swine": "PIG", "carrion_birds": "BIRD", "waterfowl": "DUCK", "sea_beasts": "good:seals",
                 "shellfish": "good:shellfish", "wheat": "crop:wheat", "cattle": "animal:cattle"}


# ---- clause helpers --------------------------------------------------------------------------------------------------------

def past(v: SN.View) -> str | None:
    """The narrative tense: the past marker, else the perfect, else none (time left to context)."""
    return next((f for f in ("PAST", "PERF") if v.g(f) is not None), None)


def future(v: SN.View) -> str | None:
    return "FUT" if v.g("FUT") is not None else None


def _det(v: SN.View, known: bool) -> str | None:
    """'the' for a participant already in the story, 'a' for a new one, where the lect has the article."""
    return SN._the(v) if known else SN._a(v)


def subject(v: SN.View, concept: str, known: bool = True, adj: str | None = None) -> SN.NP:
    return SN.noun_phrase(v, concept, _det(v, known), adj=adj)


def pron(v: SN.View, concept: str) -> SN.NP | None:
    return SN.pronoun(v, concept)


def tclause(v: SN.View, S: SN.NP | None, Vc: str, O: SN.NP | None = None, X: SN.NP | None = None,
            tam: str | None = None, neg: bool = False, person: str | None = None) -> list:
    """One clause: the verb with its tense, negation and the subject's person marker; a pronoun subject dropped where
    the verb marks it and the lect drops pronouns."""
    person = person or (S.person if S is not None else "3SG")
    vw = SN.verb(v, Vc, person, tam, neg=neg)
    if S is not None and SN._is_pron(S) and any("subject's" in n for n in vw[2]) and v.t.get("pro_drop") == "yes":
        S = None
    return SN.clause(v, S, vw, O, X, transitive=O is not None, tam=tam)


def locative(v: SN.View, concept: str, known: bool, words: tuple = ("IN", "AT")) -> SN.NP:
    """'in the N': the locative case or an adposition ('in', 'at': `words`, in order of preference); a bare noun when
    the lect has neither."""
    np_ = SN.noun_phrase(v, concept, _det(v, known))
    x = SN.oblique(v, np_, "LOC", words)
    return x[0] if x else np_


def _prep_en(np_: SN.NP, default: str) -> str:
    """The English preposition for a locative phrase as the lect said it: the adposition's own meaning ('in', 'at')
    when it used one, else `default` (a locative case covers on / in / at)."""
    for w in np_.words:
        if w.gloss in ("in", "at"):
            return w.gloss
    return default


def quote(v: SN.View, S: SN.NP, said: list, tam: str | None) -> list:
    """'S said: "..."': the quotation stands in the object's place (before 'say' in OV lects, as Japanese ... to itta;
    after it in VO lects)."""
    vw = SN.verb(v, "SAY", S.person, tam)
    return SN.clause(v, S, vw, SN.NP(said, 0), transitive=False, tam=tam)


def give(v: SN.View, S: SN.NP | None, R: SN.NP, T: SN.NP, tam: str | None, person: str) -> list:
    """'S gives R T' as the lect gives: a dative recipient where it has a dative, else both objects bare."""
    if v.g("DAT") is not None:
        x = SN.oblique(v, R, "DAT", ())
        return tclause(v, S, "GIVE", T, x[0], tam=tam, person=person)
    words = tclause(v, S, "GIVE", T, tam=tam, person=person)
    # (double object: the recipient beside the theme, recipient first as English 'give you a seed')
    i = next(i for i, w in enumerate(words) if any(w is x for x in T.words))
    return words[:i] + R.words + words[i:]


def imperative(v: SN.View, Vc: str) -> list:
    return SN.verb(v, Vc, mood="IMP")[0]


# ---- the fable ----------------------------------------------------------------------------------------------------------------

def fable(lj: dict) -> list[dict]:
    """The fable in this lect: [sentence dict] (see the module doc), a sentence left out where a word is missing."""
    v = SN.View(lj)
    out = []
    pst, fut = past(v), future(v)
    steps = (_f1, _f2, _f3, _f4, _f5, _f6)
    for i, (fn, en) in enumerate(zip(steps, FABLE_EN)):
        try:
            r = fn(v, pst, fut)
        except (KeyError, IndexError, ValueError, StopIteration, TypeError, AttributeError):
            r = None
        if r is None:
            continue
        words, notes = r
        out.append(SN.finish(v, f"fable{i + 1}", en, words, notes))
    return out


def complete(sents: list[dict], n: int) -> bool:
    return len(sents) == n


def _need(v: SN.View, *cs) -> bool:
    return all(v.w(c) for c in cs)


def _tnote(v: SN.View, tam: str | None) -> list:
    return [f"{SN.ABBR[tam]} for the story's past" if tam in ("PAST", "PERF") else
            f"{SN.ABBR[tam]} for the future" if tam else ""]


def _f1(v, pst, fut):
    if not _need(v, "BIRD", "SIT", "TREE"):
        return None
    return tclause(v, subject(v, "BIRD", False), "SIT", X=locative(v, "TREE", False), tam=pst), _tnote(v, pst)


def _f2(v, pst, fut):
    if not _need(v, "BIRD", "SEE", "FISH", "WATER"):
        return None
    return tclause(v, subject(v, "BIRD"), "SEE", SN.noun_phrase(v, "FISH", SN._a(v)), locative(v, "WATER", True),
                   tam=pst), []


def _f3(v, pst, fut):
    if not _need(v, "BIRD", "SAY", "COME", "I", "GIVE", "THOU", "SEED"):
        return None
    adj = "GOOD" if v.w("GOOD") else None
    said = imperative(v, "COME") + give(v, pron(v, "I"), pron(v, "THOU"), SN.noun_phrase(v, "SEED", SN._a(v), adj=adj),
                                        fut, "1SG")
    return quote(v, subject(v, "BIRD"), said, pst), ["the quotation stands where an object would"]


def _f4(v, pst, fut):
    if not _need(v, "FISH", "SAY", "I", "EAT", "SEED", "THOU") or (v.g("NEG") is None and not v.w("NOT")):
        return None
    said = tclause(v, pron(v, "I"), "EAT", SN.noun_phrase(v, "SEED", plural=True), neg=True, person="1SG") + \
        tclause(v, pron(v, "THOU"), "EAT", pron(v, "I"), tam=fut, person="2SG")
    return quote(v, subject(v, "FISH"), said, pst), []


def _f5(v, pst, fut):
    if not _need(v, "FISH", "COME") or (v.g("NEG") is None and not v.w("NOT")):
        return None
    return tclause(v, subject(v, "FISH"), "COME", tam=pst, neg=True), []


def _f6(v, pst, fut):
    if not _need(v, "BIRD", "EAT", "SEED"):
        return None
    return tclause(v, subject(v, "BIRD"), "EAT", SN.noun_phrase(v, "SEED", SN._the(v)), tam=pst), []


# ---- picking a family to tell it in ---------------------------------------------------------------------------------------

def descendants(lects: dict, pid: str) -> list[dict]:
    """The living lects whose line of descent reaches lect `pid`."""
    out = []
    for l in lects.values():
        if l.get("died_kyr") is not None:
            continue
        x, seen = l, set()
        while x is not None and x["id"] not in seen:
            seen.add(x["id"])
            if x["id"] == pid:
                out.append(l)
                break
            x = lects.get(x.get("parent"))
    return out


def branch_of(lects: dict, l: dict, pid: str) -> str:
    """The proto's daughter (first split) that `l` descends through: daughters on different branches differ most."""
    x, prev = l, l["id"]
    while x is not None and x["id"] != pid:
        prev = x["id"]
        x = lects.get(x.get("parent"))
    return prev


def pick_daughters(lects: dict, pid: str, n: int = 3, intel: dict | None = None) -> list[dict]:
    """Up to n living daughters that tell the whole fable, from different branches, least mutually intelligible first,
    then the most spoken."""
    full = [l for l in descendants(lects, pid) if complete(fable(l), len(FABLE_EN))]
    full.sort(key=lambda l: (-(l.get("population") or 0), l["id"]))
    out: list = []
    for l in full:
        if len(out) >= n:
            break
        b = branch_of(lects, l, pid)
        if any(branch_of(lects, x, pid) == b for x in out) and len({branch_of(lects, x, pid) for x in full}) > len(out):
            continue
        if intel and any((intel.get((l["id"], x["id"])) or 0) > 0.5 for x in out):
            continue
        if any(x.get("deme") == l.get("deme") for x in out):
            continue   # (two lects of one community share its name: one is enough)
        out.append(l)
    for l in full:   # (too few branches: fill from the rest)
        if len(out) >= n:
            break
        if l not in out:
            out.append(l)
    return out


#: how long ago the fable's ancestor was last spoken (polish lane, 2026-11-08): the root proto-languages are ~20 kyr
#: older than their daughters, too deep for shared words to survive (bird, tree, water, 2SG were all replaced: demo read
#: 4); an ancestor of 3-6 kyr shows the same words worn by sound change (Latin to the Romance languages is ~2 kyr, Proto-
#: Indo-European to its daughters ~5-6)
FABLE_DEPTH_KYR = (3.0, 6.0)
FABLE_DAUGHTERS = (2, 4)


def pick_family(lects: dict, intel: dict | None = None, prefer: tuple = ()) -> tuple[dict, list[dict]] | None:
    """(ancestor, daughters): a lect last spoken FABLE_DEPTH_KYR ago (it split then) that tells the whole fable, with 2-4
    living daughters that do too, preferring the peoples in `prefer` (the demo's languages), then 3+ daughters, then an
    age near the middle of the window; outside the window, the nearest age. None when no family can."""
    lo, hi = FABLE_DEPTH_KYR
    mid = (lo + hi) / 2.0
    best = None
    for p in sorted(lects.values(), key=lambda x: x["id"]):
        age = p.get("died_kyr")
        if age is None or not complete(fable(p), len(FABLE_EN)):
            continue
        ds = pick_daughters(lects, p["id"], FABLE_DAUGHTERS[1], intel)
        if len(ds) < FABLE_DAUGHTERS[0]:
            continue
        off = max(0.0, lo - age, age - hi)
        key = (-round(off, 3), p["people"] in prefer, len(ds) >= 3, -round(abs(age - mid), 3), len(ds), p["id"])
        if best is None or key > best[0]:
            best = (key, p, ds)
    return None if best is None else (best[1], best[2])


# ---- the recipe (grammar phase D: a connected text per demo language) -------------------------------------------------------

#: the recipe's English, with {f} for the food (the people's own crop or herd animal where the lexicon has one)
RECIPE_EN = ("Take some {f}.", "{prep} it with a {tool}.", "Put it in the pot.", "Cook it on the fire.",
             "Eat it with salt.", "It is good.")
#: food by kind: (what is done to it in step 2, the tool)
_PREP = {"crop": ("GRIND", "STONE"), "animal": ("CUT", "KNIFE"), "plain": ("CUT", "KNIFE")}


#: herd animals as English names their meat
ANIMAL_EN = {"caprine": "goat meat", "cattle": "beef", "ovine": "mutton", "fowl": "fowl", "porcine": "pork",
             "horse": "horse meat", "camelid": "camel meat", "cervid": "venison"}


def staple(lj: dict) -> tuple[str, str] | None:
    """(concept, kind) of the recipe's food: one of the people's own crops (the cuisine data the lexicon lane put in),
    else one of their herd animals, else fish or meat. Picked by a fixed order (the first by name), not by taste."""
    lex = lj.get("lexicon") or {}
    for pre, kind in (("crop:", "crop"), ("animal:", "animal")):
        cs = sorted(c for c in lex if c.startswith(pre) and lex[c].get("ipa"))
        if cs:
            return cs[0], kind
    c = next((c for c in ("FISH", "FLESH OR MEAT", "EGG") if lex.get(c, {}).get("ipa")), None)
    return (c, "plain") if c else None


def _it(v: SN.View, many: bool = False) -> SN.NP | None:
    """'it' ('them' for a plural food) as an object: the verb's object marker carries it where bound (nothing else
    said), else the pronoun."""
    p = "3PL" if many else "3SG"
    g = v.g(f"{p}.O")
    if g is not None and (g.get("level") or 0) >= GR.CLITIC:
        np_ = SN.NP([], 0)
        np_.person = p
        return np_
    return SN.pronoun(v, "THEY" if many else "HE OR SHE OR IT")


def _imp(v: SN.View, Vc: str, O: SN.NP | None, X: SN.NP | None = None) -> list:
    vw = SN.verb(v, Vc, mood="IMP")
    if O is not None and not O.words:   # (a bound object marker alone)
        SN.object_marker(v, vw[0], vw[0][vw[1]], getattr(O, "person", None) or "3SG")
        O = None
    return SN.clause(v, None, vw, O, X, transitive=O is not None)


def recipe(lj: dict) -> tuple[str, list[dict]]:
    """(title, sentences): a short recipe in this lect, as commands; a step whose words are missing is left out."""
    v = SN.View(lj)
    st = staple(lj)
    if st is None:
        return "", []
    food, kind = st
    prep, tool = _PREP[kind]
    fen = ANIMAL_EN.get(SN.en(food), SN.en(food) + " meat") if kind == "animal" else SN.en(food)
    many = kind != "animal" and fen.endswith("s") and not fen.endswith("ss")   # (alliums, beans: 'them', not 'it')
    it_en, It_en = ("them", "They are") if many else ("it", "It is")
    out = []

    def has(*cs):   # (View.w is "the first it has"; a step needs every word)
        return all(v.w(c) for c in cs)

    def add(i, words, en, notes=()):
        out.append(SN.finish(v, f"recipe{i}", en, words, list(notes)))
    if has("TAKE"):
        add(1, _imp(v, "TAKE", SN.noun_phrase(v, food, SN._a(v))),
            f"Take some {fen}.", ["a command: the bare verb or the imperative marker"])
    if has(prep, tool):
        x = SN.oblique(v, SN.noun_phrase(v, tool, SN._a(v)), "INS", ("WITH",))
        if x:
            add(2, _imp(v, prep, _it(v, many), x[0]), f"{SN.en(prep).capitalize()} {it_en} with a {SN.en(tool)}.",
                [x[1]])
    if has("PUT", "POT"):
        loc = locative(v, "POT", True)
        add(3, _imp(v, "PUT", _it(v, many), loc), f"Put {it_en} {_prep_en(loc, 'in')} the pot.")
    if has("COOK", "FIRE"):
        loc = locative(v, "FIRE", True, ("AT", "IN"))
        add(4, _imp(v, "COOK", _it(v, many), loc), f"Cook {it_en} {_prep_en(loc, 'on')} the fire.")
    if has("EAT", "SALT"):
        x = SN.oblique(v, SN.noun_phrase(v, "SALT"), "COM", ("WITH",))
        if x:
            add(5, _imp(v, "EAT", _it(v, many), x[0]), f"Eat {it_en} with salt.", [x[1]])
    if has("GOOD"):
        subj = SN.pronoun(v, "THEY" if many else "HE OR SHE OR IT")
        if subj is not None:
            pred = SN.NP([SN.Word(v.ipa("GOOD"), "good", "GOOD")], 0)
            words = (subj.words + SN.verb(v, "GOOD", "3PL" if many else "3SG")[0]) \
                if v.t.get("adjective_verb_like") == "yes" else subj.words + SN.cop_phrase(v, pred)
            add(6, words, f"{It_en} good.")
    return f"How to cook {fen}", out


# ---- the faith myth ---------------------------------------------------------------------------------------------------------

def _god(v: SN.View, g: dict, lid: str) -> tuple[str, str] | None:
    """(concept, book-spelled name) of a faith god in this lect, when its name is a word of the lect."""
    from . import faiths as FA
    con = FA.god_concept(g["key"])
    mine = next((n for n in g.get("names") or [] if n[0] == lid), None)
    if mine is None or not v.w(con):
        return None
    return con, mine[2]


def myth(lj: dict, faith: dict | None) -> tuple[str, list[dict]]:
    """(title, sentences): what the faith holds, told in this lect. Only what the data says, and all of it the faith's
    (polish lane: one faith, one pantheon, so every holder tells the same myth in its own words): each god's first
    domain (gods.json `first_domain`), the high god's gift (faiths.GIFT), the foods forbidden because they belong to a
    god's domain (the faith's `taboos` = [[god key, target, English label]], from taboos.json, origin 'divine'), and the
    faith's invocation. No creation story, kinship or deeds: gods.json has none."""
    from . import faiths as FA
    if not faith:
        return "", []
    v = SN.View(lj)
    lid = lj["id"]
    gods = [(g, _god(v, g, lid)) for g in faith.get("gods") or []]
    gods = [(g, x) for g, x in gods if x is not None]
    if not gods or not v.w("HOLD"):
        return "", []
    out = []

    names = {x[1] for _g, x in gods}

    def add(words, en, notes=()):
        x = SN.finish(v, f"myth{len(out) + 1}", en, words, list(notes))
        rs = x["roman"].split(" ")
        if len(rs) == len(x["w"]):   # (a word holding a name is spelled with a capital, clitics and all, the same
            x["roman"] = " ".join(r[:1].upper() + r[1:]   # rule in every language: CL2=name is Nobe...)
                                  if any(p in names for p in re.split(r"[-=]", w[1])) else r for r, w in zip(rs, x["w"]))
        out.append(x)

    def god_np(x):
        return SN.noun_phrase(v, x[0], gloss=x[1])

    for g, x in gods[:3]:
        dom = FA._domain_word(g["domain"])
        if dom == "GOD" or not v.w(dom):
            continue
        add(tclause(v, god_np(x), "HOLD", SN.noun_phrase(v, dom, SN._the(v))),
            f"{x[1]} holds the {SN.en(dom)}.", [f"{x[1]}: the god's name in this language"] if not out else [])
    g0, x0 = gods[0]
    gift = FA.GIFT.get(g0.get("domain") or "")
    if gift and _need(v, gift, "GIVE", "WE"):
        we = pron(v, "WE")
        if we is not None:
            add(give(v, god_np(x0), we, SN.noun_phrase(v, gift), None, "3SG"),
                f"{x0[1]} gives us {SN.en(gift)}.")
    by_key = {g["key"]: x for g, x in gods}
    seen = set()
    for key, target, label in faith.get("taboos") or []:
        con = TABOO_CONCEPT.get(target)
        x = by_key.get(key)
        if x is None or con is None or con in seen or not _need(v, con, "EAT", "WE"):
            continue
        if v.g("NEG") is None and not v.w("NOT"):
            continue
        seen.add(con)
        add(tclause(v, god_np(x), "HOLD", SN.noun_phrase(v, con, plural=True)), f"{x[1]} holds the {label}.")
        add(tclause(v, pron(v, "WE"), "EAT", SN.noun_phrase(v, con, plural=True), neg=True, person="1PL"),
            f"We do not eat {label}.", ["a food taboo: the animal belongs to the god's domain"])
        if len(seen) >= 2:
            break
    if _need(v, "HEAR", "WE"):
        we = pron(v, "WE")
        if we is not None:
            vw = SN.verb(v, "HEAR", mood="IMP")   # (clause() marks the object on the verb: once, not twice)
            name = god_np(x0)
            add(name.words + SN.clause(v, None, vw, we, transitive=True), f"{x0[1]}, hear us!",
                ["the invocation that ends the rites"])
    return f"What the gods hold ({faith['name']})", out
