"""Connected glossed texts: a fixed fable told in a proto-language and its daughters (Schleicher's way of showing sound
change and grammar change through one text), and a short recipe per living language.

Like sentences.py, everything here reads one lect's json record and draws nothing: each clause is built by the sentence
builder (`sentences.noun_phrase`, `verb`, `clause`, `finish`), so a text shows the same grammar as the sample sentences.
A text sentence whose words the lexicon lacks is left out, and `complete` says whether the whole text could be told.

Every sentence comes back in the sentence shape (`{id, en, w: [[form, gloss]...], ipa, roman, note?}`): a page shows it in
four lines, book spelling (`roman`), IPA (the forms with their morph breaks), gloss and English.

The fable uses only Swadesh-100 words, because a proto-language's record keeps only those (`lexicon_full` false); the
recipe uses the people's own staple and fuel words where the lexicon has them (the cuisine data the lexicon lane put in),
and plain words otherwise. A faith's origin myth will follow once the faiths lane's god names are merged
(`MYTH_HOOK`)."""
from __future__ import annotations

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

#: where the faith origin myth will plug in (faiths lane: god names and a liturgical register; not merged yet)
MYTH_HOOK = "origin myth: waits for the faiths lane (gods.json names in the lexicon)"


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


def locative(v: SN.View, concept: str, known: bool) -> SN.NP:
    """'in the N': the locative case or an adposition ('in', 'at'); a bare noun when the lect has neither."""
    np_ = SN.noun_phrase(v, concept, _det(v, known))
    x = SN.oblique(v, np_, "LOC", ("IN", "AT"))
    return x[0] if x else np_


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


def pick_family(lects: dict, intel: dict | None = None, prefer: tuple = ()) -> tuple[dict, list[dict]] | None:
    """(proto, daughters): a proto-language that tells the whole fable with 3 daughters that do too, preferring the
    peoples in `prefer` (the demo's languages), then the most daughters; None when no family can."""
    best = None
    for p in sorted(lects.values(), key=lambda x: x["id"]):
        if p.get("parent") is not None or not complete(fable(p), len(FABLE_EN)):
            continue
        ds = pick_daughters(lects, p["id"], 3, intel)
        if len(ds) < 2:
            continue
        key = (p["people"] in prefer, len(ds), len(descendants(lects, p["id"])), p["id"])
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


def _it(v: SN.View) -> SN.NP | None:
    """'it' as an object: the verb's 3SG object marker carries it where bound (nothing else said), else the pronoun."""
    g = v.g("3SG.O")
    if g is not None and (g.get("level") or 0) >= GR.CLITIC:
        return SN.NP([], 0)
    return SN.pronoun(v, "HE OR SHE OR IT")


def _imp(v: SN.View, Vc: str, O: SN.NP | None, X: SN.NP | None = None) -> list:
    vw = SN.verb(v, Vc, mood="IMP")
    if O is not None and not O.words:   # (a bound object marker alone)
        SN.object_marker(v, vw[0], vw[0][vw[1]], "3SG")
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
            add(2, _imp(v, prep, _it(v), x[0]), f"{SN.en(prep).capitalize()} it with a {SN.en(tool)}.", [x[1]])
    if has("PUT", "POT"):
        add(3, _imp(v, "PUT", _it(v), locative(v, "POT", True)), "Put it in the pot.")
    if has("COOK", "FIRE"):
        add(4, _imp(v, "COOK", _it(v), locative(v, "FIRE", True)), "Cook it on the fire.")
    if has("EAT", "SALT"):
        x = SN.oblique(v, SN.noun_phrase(v, "SALT"), "COM", ("WITH",))
        if x:
            add(5, _imp(v, "EAT", _it(v), x[0]), "Eat it with salt.", [x[1]])
    if has("GOOD"):
        subj = SN.pronoun(v, "HE OR SHE OR IT")
        if subj is not None:
            pred = SN.NP([SN.Word(v.ipa("GOOD"), "good", "GOOD")], 0)
            words = (subj.words + SN.verb(v, "GOOD", "3SG")[0]) if v.t.get("adjective_verb_like") == "yes" else \
                subj.words + SN.cop_phrase(v, pred)
            add(6, words, "It is good.")
    return f"How to cook {fen}", out
