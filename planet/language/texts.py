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
import zlib

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
    if SN.flagging(v, S, SN.NP(said, 0), tam)[0]:   # (PW-1537 R5: the sayer of a quote is an ergative subject too)
        SN._np_gram(v, S, "ERG")
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


def pick_daughters(lects: dict, pid: str, n: int = 3, intel: dict | None = None,
                   branches: dict | None = None) -> list[dict]:
    """Up to n living daughters that tell the whole fable, from different branches, least mutually intelligible first,
    then the most spoken. `branches` ({living id: branch}, a split state's) limits them to the lines of that split."""
    if branches is not None:
        cand = [lects[i] for i in branches if i in lects]

        def br(l):
            return branches[l["id"]]
    else:
        cand = descendants(lects, pid)

        def br(l):
            return branch_of(lects, l, pid)
    full = [l for l in cand if complete(fable(l), len(FABLE_EN))]
    full.sort(key=lambda l: (-(l.get("population") or 0), l["id"]))
    out: list = []
    for l in full:
        if len(out) >= n:
            break
        b = br(l)
        if any(br(x) == b for x in out) and len({br(x) for x in full}) > len(out):
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


def pick_family(lects: dict, intel: dict | None = None, prefer: tuple = (),
                splits: list | None = None) -> tuple[dict, list[dict]] | None:
    """(ancestor, daughters): a lect as it stood when it split FABLE_DEPTH_KYR ago that tells the whole fable, with 2-4
    living daughters that do too (from at least two of its branches), preferring the peoples in `prefer` (the demo's
    languages), then 3+ daughters, then an age near the middle of the window; outside the window, the nearest age. None
    when no family can.

    PW-1592: the ancestor is a split state (`splits`, the doc's `fable_splits`: a lect kept as it stood at its first bud),
    the daughters' true common ancestor, so they cannot share a change it lacks. A doc without split states falls back to
    dead lects (whose daughters may all descend through a later lect that innovated after it: the cold review's R2)."""
    lo, hi = FABLE_DEPTH_KYR
    mid = (lo + hi) / 2.0
    best = None
    if splits:
        cands = [(p, p.get("branches") or {}) for p in sorted(splits, key=lambda x: x["id"])]
    else:
        cands = [(p, None) for p in sorted(lects.values(), key=lambda x: x["id"])]
    for p, brs in cands:
        age = p.get("died_kyr")
        if age is None or not complete(fable(p), len(FABLE_EN)):
            continue
        ds = pick_daughters(lects, p["id"], FABLE_DAUGHTERS[1], intel, brs)
        if len(ds) < FABLE_DAUGHTERS[0] or (brs is not None and len({brs[d["id"]] for d in ds}) < 2):
            continue
        off = max(0.0, lo - age, age - hi)
        key = (-round(off, 3), p["people"] in prefer, len(ds) >= 3, -round(abs(age - mid), 3), len(ds), p["id"])
        if best is None or key > best[0]:
            best = (key, p, ds)
    return None if best is None else (best[1], best[2])


def fable_descent(anc: dict, ds: list[dict], roots: dict, lects: dict, nodes: list | None = None) -> list[str]:
    """PW-1592 check over the fable's words: what contradicts the claim that the daughters `ds` descend from `anc`. A
    daughter word whose root was coined in the ancestor's own line at or before the split must find that root in the
    ancestor's lexicon (else the shown ancestor is not the state they came from); a root coined in the family after the
    split must not be shared by daughters on two branches (a shared change the ancestor lacks: R2). A root coined
    outside the line is a loan and passes; so does a word borrowed after the split (`nodes`, the doc's etym_nodes: a
    borrow step in its chain younger than the split), whatever its root: a loan from a cousin line carries a root the
    two lines share by descent from before the split, which the ancestor itself may have replaced (PW-1595, a24559:
    d754 lost d584's SIT for a coinage at 6 kyr, then borrowed its cousin d216.1's reflex of it back at 3 kyr, as English
    took 'skirt' from Norse beside its own 'shirt'). [] when the fable is a true reconstruction."""
    t = float(anc.get("split_kyr") or anc.get("died_kyr") or 0.0)

    def loan(w):   # (a borrow step after the split in the word's chain: node = [up, kyr, lect, process, ...])
        n, seen = (w or {}).get("etym"), set()
        while nodes is not None and isinstance(n, int) and 0 <= n < len(nodes) and n not in seen:
            seen.add(n)
            row = nodes[n]
            if str(row[3]).startswith("borrow") and float(row[1]) < t - 1e-6:
                return True
            n = row[0]
        return False
    line, x, seen = set(), lects.get(anc.get("split_of") or anc["id"]), set()
    while x is not None and x["id"] not in seen:
        seen.add(x["id"])
        line.add(x["id"])
        x = lects.get(x.get("parent"))
    line.add(anc["id"])
    top = anc.get("split_of") or anc["id"]

    def under(lid):   # (a lect of the ancestor's line or below it: a root it coined is no loan from outside)
        x, seen = lects.get(lid), set()
        while x is not None and x["id"] not in seen:
            if x["id"] == top:
                return True
            seen.add(x["id"])
            x = lects.get(x.get("parent"))
        return lid in line
    def deep(w):   # (the etymological roots: a felt root is renamed once speakers stop hearing it, SAY < SPEAK)
        return (w or {}).get("etym_roots") or (w or {}).get("roots") or ()
    have = {r for w in (anc.get("lexicon") or {}).values() for r in (*deep(w), *(w.get("roots") or ()))}
    brs = anc.get("branches") or {}
    out, after = [], {}
    for d in ds:
        for c in FABLE_WORDS:
            w = (d.get("lexicon") or {}).get(c)
            if loan(w):
                continue
            for r in deep(w):
                e = roots.get(r) or {}
                if e.get("kyr") is None or e.get("lect") is None:
                    continue
                same_frame = abs(float(e["kyr"]) - t) < 1e-6 and r not in have   # (coined in the split's own frame,
                # after the bud copied the parent: history.birth runs before the lects step)
                if float(e["kyr"]) >= t - 1e-6 and not same_frame:
                    seen_c = anc.get("lexicon_full", True) or e.get("concept") in (anc.get("lexicon") or {})
                    if e["lect"] in line and r not in have and seen_c:   # (a partial lexicon shows only its words)
                        out.append(f"{d['id']} {c}: root {r} is older than the split but not in the ancestor")
                elif under(e["lect"]):
                    after.setdefault(r, set()).add(brs.get(d["id"], d["id"]))
    for r, bs in sorted(after.items()):
        if len(bs) >= 2:
            out.append(f"root {r}, coined in the family after the split, is shared by branches {sorted(bs)}")
    return out


# ---- the recipe (grammar phase D: a connected text per demo language) -------------------------------------------------------

# PW-1537 R3 (cold review: all ten recipes ran "Take X. Grind it with a stone. Put it in the pot. Cook it at the fire. Eat
# it with salt. It is good."): the recipe follows the food. Each kind of staple has its own ways (a grain is ground and
# boiled into porridge or baked in the ashes, a pulse soaked then boiled, a tuber boiled and pounded in a mortar as fufu
# is or roasted in the ashes, meat and fish roasted, smoked or boiled, sweet fruit pressed and left to ferment or dried);
# among the ways a kind has, the lect picks by a fixed hash of its id (`_pick`), not by a draw, and a way whose first
# words the lexicon lacks is passed over. The steps say only what the language has words for.

#: crops by kind (planet.lineages.crop_defs ids; a crop missing here is cooked as a fruit)
CROP_KIND = {**{c: "grain" for c in ("wheat", "foxtail_millet", "rice", "sorghum", "maize", "rye", "stonegrain",
                                     "pseudograin")},
             **{c: "pulse" for c in ("pulses", "beans", "soybean", "cowpea", "peanut")},
             **{c: "tuber" for c in ("potato", "roots", "sweet_potato")},
             **{c: "sweet" for c in ("vine", "date_palm", "cane", "sap_sugar")},
             **{c: "green" for c in ("greens", "alliums", "squash", "nightshade_fruit")}}
#: the staple's kind in order of preference (a people's main food first: grain, then roots, then pulses ...)
KIND_ORDER = ("grain", "tuber", "pulse", "fruit", "green", "sweet")
#: crops no one makes a meal of (spices, drink plants, flavourings): never the recipe's food
NOT_A_MEAL = ("spice_tree", "chili", "tea", "cacao", "vanilla", "oil_seeds")


def _o(fn, adps, noun, prep, art):
    """An oblique: (function, adposition concepts, noun, English preposition, English article)."""
    return (fn, adps, noun, prep, art)


_IN, _AT = ("IN", "AT"), ("AT", "IN")
_WITH = ("WITH",)
#: the ways of each kind, each a tuple of steps (verb concept, English verb, oblique or None[, English after 'it'])
WAYS = {
    "grain": (
        (("GRIND", "grind", _o("INS", _WITH, "STONE", "with", "a")), ("PUT", "put", _o("LOC", _IN, "POT", "in", "the")),
         ("BOIL", "boil", _o("COM", _WITH, "WATER", "with", "")), ("EAT", "eat", _o("COM", _WITH, "MILK", "with", ""))),
        (("POUND", "pound", _o("LOC", _IN, "MORTAR", "in", "a")), ("BAKE", "bake", _o("LOC", _IN, "ASH", "in", "the")),
         ("EAT", "eat", _o("COM", _WITH, "HONEY", "with", ""))),
        (("GRIND", "grind", _o("INS", _WITH, "STONE", "with", "a")), ("BAKE", "bake", _o("LOC", _AT, "FIRE", "on", "the")),
         ("EAT", "eat", _o("COM", _WITH, "SALT", "with", ""))),
    ),
    "pulse": (
        (("PUT", "put", _o("LOC", _IN, "WATER", "in", "")), ("BOIL", "boil", _o("LOC", _IN, "POT", "in", "the")),
         ("EAT", "eat", _o("COM", _WITH, "SALT", "with", ""))),
        (("ROAST OR FRY", "roast", _o("LOC", _AT, "FIRE", "on", "the")), ("GRIND", "grind", _o("INS", _WITH, "STONE", "with", "a")),
         ("EAT", "eat", _o("COM", _WITH, "SALT", "with", ""))),
    ),
    "tuber": (
        (("WASH", "wash", _o("LOC", _IN, "WATER", "in", "")), ("BOIL", "boil", _o("LOC", _IN, "POT", "in", "the")),
         ("POUND", "pound", _o("LOC", _IN, "MORTAR", "in", "a")), ("EAT", "eat", None)),
        (("CUT", "cut", _o("INS", _WITH, "KNIFE", "with", "a")), ("ROAST OR FRY", "roast", _o("LOC", _IN, "ASH", "in", "the")),
         ("EAT", "eat", _o("COM", _WITH, "SALT", "with", ""))),
    ),
    "fruit": (
        (("ROAST OR FRY", "roast", _o("LOC", _AT, "FIRE", "on", "the")), ("EAT", "eat", None)),
        (("CUT", "cut", _o("INS", _WITH, "KNIFE", "with", "a")), ("PUT", "put", _o("LOC", _IN, "SUN", "in", "the")),
         ("KEEP", "keep", None)),
        (("BOIL", "boil", _o("LOC", _IN, "POT", "in", "the")), ("EAT", "eat", _o("COM", _WITH, "HONEY", "with", ""))),
    ),
    "green": (
        (("CUT", "cut", _o("INS", _WITH, "KNIFE", "with", "a")), ("BOIL", "boil", _o("LOC", _IN, "POT", "in", "the")),
         ("EAT", "eat", _o("COM", _WITH, "SALT", "with", ""))),
        (("CUT", "cut", _o("INS", _WITH, "KNIFE", "with", "a")),
         ("ROAST OR FRY", "fry", _o("COM", _WITH, "FAT (ORGANIC SUBSTANCE)", "with", "")), ("EAT", "eat", None)),
    ),
    "sweet": (
        (("SQUEEZE", "press", _o("INS", _WITH, "STONE", "with", "a")), ("PUT", "put", _o("LOC", _IN, "POT", "in", "a")),
         ("FERMENT", "leave", None, "to ferment"), ("DRINK", "drink", None)),
        (("PUT", "put", _o("LOC", _IN, "SUN", "in", "the")), ("KEEP", "keep", None)),
    ),
    "meat": (
        (("CUT", "cut", _o("INS", _WITH, "KNIFE", "with", "a")), ("ROAST OR FRY", "roast", _o("LOC", _AT, "FIRE", "on", "the")),
         ("EAT", "eat", _o("COM", _WITH, "SALT", "with", ""))),
        (("CUT", "cut", _o("INS", _WITH, "KNIFE", "with", "a")), ("SALT (FOOD)", "salt", None),
         ("SMOKE (FOOD)", "smoke", _o("LOC", _AT, "FIRE", "over", "the")), ("KEEP", "keep", None)),
        (("CUT", "cut", _o("INS", _WITH, "KNIFE", "with", "a")), ("BOIL", "boil", _o("LOC", _IN, "POT", "in", "the")),
         ("EAT", "eat", None)),
    ),
}
WAYS["fish"] = WAYS["meat"]

#: the closing line, picked by the lect's hash: (quality concept, English)
CLOSING = (("GOOD", "good"), ("TASTY", "tasty"), ("GOOD", "good"))
CLOSING_SWEET = (("SWEET", "sweet"), ("GOOD", "good"), ("TASTY", "tasty"))   # (fruit and sweet crops)
#: English for an oblique's noun where the bare concept name reads wrong ('in the ash')
OBL_EN = {"ASH": "ashes"}
#: the title's verb by kind
TITLE_VERB = {"sweet": "keep", "fruit": "eat"}

#: herd animals as English names their meat
ANIMAL_EN = {"caprine": "goat meat", "cattle": "beef", "ovine": "mutton", "fowl": "fowl", "porcine": "pork",
             "horse": "horse meat", "camelid": "camel meat", "cervid": "venison"}


def _pick(lj: dict, salt: str, n: int) -> int:
    """A fixed choice among n for this lect (a hash of its id and `salt`): two lects pick differently, a rebuild the same."""
    return zlib.crc32(f"{lj.get('id')}:{salt}".encode()) % max(n, 1)


def food_kind(concept: str) -> str:
    if concept.startswith("crop:"):
        return CROP_KIND.get(concept[5:], "fruit")
    return "fish" if concept == "FISH" else "meat"


def staple(lj: dict) -> tuple[str, str] | None:
    """(concept, kind) of the recipe's food: the people's own crop of the most staple kind (KIND_ORDER; spices and drink
    plants never), else one of their herd animals, else fish or meat. Among several of one kind the lect picks by
    `_pick`."""
    lex = lj.get("lexicon") or {}
    crops = sorted(c for c in lex if c.startswith("crop:") and lex[c].get("ipa") and c[5:] not in NOT_A_MEAL)
    for kind in KIND_ORDER:
        cs = [c for c in crops if food_kind(c) == kind]
        if cs:
            return cs[_pick(lj, "crop", len(cs))], kind
    an = sorted(c for c in lex if c.startswith("animal:") and lex[c].get("ipa"))
    if an:
        return an[_pick(lj, "animal", len(an))], "meat"
    c = next((c for c in ("FISH", "FLESH OR MEAT", "EGG") if lex.get(c, {}).get("ipa")), None)
    return (c, food_kind(c)) if c else None


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


def _usable(v: SN.View, way: tuple) -> bool:
    """A way is told when the lexicon has the words of its first two steps (the rest are left out where missing)."""
    return all(v.w(st[0]) and (st[2] is None or v.w(st[2][2])) for st in way[:2])


def recipe(lj: dict) -> tuple[str, list[dict]]:
    """(title, sentences): a short recipe in this lect, as commands; the way of cooking follows the food (WAYS), a step
    whose words are missing is left out."""
    v = SN.View(lj)
    st = staple(lj)
    if st is None:
        return "", []
    food, kind = st
    fen = ANIMAL_EN.get(SN.en(food), SN.en(food) + " meat") if food.startswith("animal:") else SN.en(food)
    many = kind not in ("meat", "fish") and fen.endswith("s") and not fen.endswith("ss")   # (alliums, beans: 'them')
    it_en, It_en = ("them", "They are") if many else ("it", "It is")
    out = []

    def add(words, en, notes=()):
        out.append(SN.finish(v, f"recipe{len(out) + 1}", en, words, list(notes)))
    if v.w("TAKE"):
        add(_imp(v, "TAKE", SN.noun_phrase(v, food, SN._a(v))), f"Take some {fen}.",
            ["a command: the bare verb or the imperative marker"])
    ways = [w for w in WAYS[kind] if _usable(v, w)]
    for step in (ways[_pick(lj, "way", len(ways))] if ways else ()):
        verb, ven, obl = step[0], step[1], step[2]
        tail = f" {step[3]}" if len(step) > 3 else ""
        if not v.w(verb):
            continue
        X, note, xen = None, [], ""
        if obl is not None:
            fn, adps, noun, prep, art = obl
            if not v.w(noun):
                continue
            np_ = SN.noun_phrase(v, noun, SN._the(v) if art == "the" else SN._a(v) if art == "a" else None)
            x = SN.oblique(v, np_, fn, adps)
            if not x:
                continue
            X, note = x[0], [x[1]]
            if fn == "LOC":
                prep = _prep_en(X, prep)
            xen = f" {prep} {art + ' ' if art else ''}{OBL_EN.get(noun, SN.en(noun))}"
        add(_imp(v, verb, _it(v, many), X), f"{ven.capitalize()} {it_en}{tail}{xen}.", note)
    cl = CLOSING_SWEET if kind in ("fruit", "sweet") else CLOSING
    q, qen = cl[_pick(lj, "close", len(cl))]
    if not v.w(q):
        q, qen = "GOOD", "good"
    if v.w(q):
        subj = SN.pronoun(v, "THEY" if many else "HE OR SHE OR IT")
        if subj is not None:
            pred = SN.NP([SN.Word(v.ipa(q), SN.lgloss(q), q)], 0)
            words = (subj.words + SN.verb(v, q, "3PL" if many else "3SG")[0]) \
                if v.t.get("adjective_verb_like") == "yes" else subj.words + SN.cop_phrase(v, pred)
            add(words, f"{It_en} {qen}.")
    return f"How to {TITLE_VERB.get(kind, 'cook')} {fen}", out


# ---- the faith myth ---------------------------------------------------------------------------------------------------------

#: (PW-1537 R3: five faiths' myths read alike) the verb of the gods' lines and the closing invocation, each picked by a
#: hash of the faith's name, so a faith keeps one wording in all its languages and two faiths differ: (concept, English)
MYTH_HOLD = (("HOLD", "holds"), ("KEEP", "keeps"), ("HOLD", "holds"))
INVOCATION = (("HEAR", "hear"), ("SEE", "look upon"), ("HELP", "help"), ("LISTEN", "listen to"))


def _plural_en(concept: str) -> str:
    """The English plural of a taboo concept as its word says it (BIRD 'birds', PIG 'pigs'; crops and goods as named)."""
    e = SN.en(concept)
    if ":" in concept or e.endswith("s") or e.endswith("fish"):
        return e
    return e + ("es" if e.endswith(("sh", "ch", "x")) else "s")


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

    fh = zlib.crc32(str([g.get("key") for g in faith.get("gods") or []] + [faith.get("founded_kyr")]).encode())   # (one
    # faith, one wording: every holder says it the same way)
    hv, hen = MYTH_HOLD[fh % len(MYTH_HOLD)]
    if not v.w(hv):
        hv, hen = "HOLD", "holds"
    for g, x in gods[:3]:
        dom = FA._domain_word(g["domain"])
        if dom == "GOD" or not v.w(dom):
            continue
        add(tclause(v, god_np(x), hv, SN.noun_phrase(v, dom, SN._the(v))),
            f"{x[1]} {hen} the {SN.en(dom)}.", [f"{x[1]}: the god's name in this language"] if not out else [])
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
        ten = _plural_en(con)   # (PW-1537 R9: the English says what the words say, 'pigs', not the label 'wild swine')
        add(tclause(v, god_np(x), hv, SN.noun_phrase(v, con, plural=True)), f"{x[1]} {hen} the {ten}.")
        add(tclause(v, pron(v, "WE"), "EAT", SN.noun_phrase(v, con, plural=True), neg=True, person="1PL"),
            f"We do not eat {ten}.", [f"a food taboo: the {label} belong to the god's domain"])
        if len(seen) >= 2:
            break
    inv = [c for c in INVOCATION[(fh // 7) % len(INVOCATION):] + INVOCATION if _need(v, c[0], "WE")]
    if inv:
        iv, ien = inv[0]
        we = pron(v, "WE")
        if we is not None:
            vw = SN.verb(v, iv, mood="IMP")   # (clause() marks the object on the verb: once, not twice)
            name = god_np(x0)
            add(name.words + SN.clause(v, None, vw, we, transitive=True), f"{x0[1]}, {ien} us!",
                ["the invocation that ends the rites"])
    return f"What the gods hold ({faith['name']})", out
