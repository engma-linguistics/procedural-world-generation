"""Lexical systems (lexicon & contact lane, 2026-11-08): parts of the lexicon that real languages build as a whole, not word
by word. `lexicon.step` and `history` call in here; the words themselves stay ordinary `lexicon.Word`s with etymologies.

- **Numerals by base.** Each lect counts in one system, read from its grammar's `numeral_base` typology value (so the
  sketch's "counting base" is true): decimal (with a quinary 6-9 in some), vigesimal or vigesimal below a hundred
  (hybrid), and for "other" a 5-based system or a restricted one (1-3 and then body-part phrases: 'two two', 'one hand',
  'one person', 'many'). Roots are ordinary words; the composite numerals (SIX = FIVE + ONE, TWENTY = TEN x TWO,
  THIRTY = TWENTY + TEN ...) are compounds by the system's recipe, and a replacement hit on one rebuilds it from the
  current parts (analogical re-formation) or keeps it. WALS 131A (Comrie 2013): of 196 languages 125 decimal, 22
  hybrid vigesimal-decimal, 20 pure vigesimal, 20 restricted, 5 other bases; the weights below follow it inside each
  Grambank-based label.
- **Colour terms by Berlin & Kay stage** (Berlin & Kay 1969; Kay & Maffi 1999, the composite trajectories). A
  proto-language starts at a stage drawn from STAGE_WEIGHTS, with composite categories (light-warm, dark-cool, grue,
  yellow-with-brown) as one word for all their members; over time a composite splits in the B&K order (`colour_step`),
  the new word made from an object word by the 'like' rows of derivations.tsv (GRASS > green, SKY > blue, EARTH >
  brown) or a fresh root, or borrowed from a contact lect that has the term (`after_replace`). The partition is read off
  the forms (colour concepts that share a form), so it survives any other process.
- **Sound symbolism.** Nursery words (Murdock 1959; Jakobson 1960): MOTHER mostly with a nasal and an open vowel,
  often reduplicated (mama, nana), FATHER mostly with a labial or dental stop (papa, tata, baba). A few of the
  sound-meaning links of Blasi et al. 2016 (PNAS 113:10818), mildly: NOSE with a nasal, TONGUE and LEAF with l, ROUND
  and RED with r, SMALL and NAME with i, SAND with s, BONE with k, BREAST with m, FULL with a labial stop, KNEE with a
  back rounded vowel. Applied when a proto root or a fresh root is drawn (`symbolic`).
"""
from __future__ import annotations

import numpy as np

from . import inventory as _inv
from . import lexicon as LX

KEEP = object()   # system_word: a system concept hit by replacement that keeps its word

# --- numerals ----------------------------------------------------------------------------------------------------------
NUM_VALUE = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6, "SEVEN": 7, "EIGHT": 8, "NINE": 9, "TEN": 10,
             "ELEVEN": 11, "TWELVE": 12, "FIFTEEN": 15, "TWENTY": 20, "THIRTY": 30, "FORTY": 40, "HUNDRED": 100,
             "THOUSAND": 1000}
NUMERALS = tuple(NUM_VALUE)
# label (grammar typology numeral_base) -> [(system, weight)]; inside "vigesimal" WALS has 22 hybrid : 20 pure, inside
# "other" 20 restricted : 5 other bases (we let the 5-based stand for the other bases and give it more room, since a
# restricted system upgrades to it as a people grows: RESTRICT_UP)
SYSTEMS_BY_LABEL = {"decimal": [("decimal", 1.0)], "vigesimal": [("hybrid", 0.52), ("vigesimal", 0.48)],
                    "other": [("restricted", 0.6), ("quinary", 0.4)]}
QUINARY_SUB = {"decimal": 0.2, "hybrid": 0.45, "vigesimal": 0.6}   # 6-9 as five + n (Wolof, Khmer, Nahuatl, Mayan)
RESTRICT_POP = 20000.0   # a restricted system grows into a 5-based one past this many speakers ...
RESTRICT_UP = 0.002      # ... at this hazard per generation
NUM_REFORM = 0.7         # a composite numeral hit by replacement is re-formed from its parts with this chance (else kept)


def _recipes(system: str, quinary: bool) -> dict:
    """concept -> (head, modifier, op): op "add" (head + modifier), "mul" (head x modifier), "same" (the head's word)."""
    r: dict = {}
    five = {"SIX": ("FIVE", "ONE", "add"), "SEVEN": ("FIVE", "TWO", "add"), "EIGHT": ("FIVE", "THREE", "add"),
            "NINE": ("FIVE", "FOUR", "add")}
    teens = {"ELEVEN": ("TEN", "ONE", "add"), "TWELVE": ("TEN", "TWO", "add"), "FIFTEEN": ("TEN", "FIVE", "add")}
    if system in ("decimal", "quinary"):
        r.update(teens)
        r.update({"TWENTY": ("TEN", "TWO", "mul"), "THIRTY": ("TEN", "THREE", "mul"), "FORTY": ("TEN", "FOUR", "mul")})
    if system in ("hybrid", "vigesimal", "restricted"):
        r.update(teens)
        r.update({"THIRTY": ("TWENTY", "TEN", "add"), "FORTY": ("TWENTY", "TWO", "mul")})
    if system == "vigesimal":
        r["HUNDRED"] = ("TWENTY", "FIVE", "mul")
    if system == "quinary":
        r.update(five)
        r["TEN"] = ("FIVE", "TWO", "mul")
    if system == "restricted":
        r.update(five)
        r.update({"FOUR": ("TWO", "TWO", "mul"), "FIVE": ("HAND", "ONE", "mul"), "TEN": ("HAND", "TWO", "mul"),
                  "TWENTY": ("PERSON", "ONE", "mul"), "HUNDRED": ("MANY", None, "same"), "THOUSAND": ("MANY", None, "same")})
    if quinary and system in ("decimal", "hybrid", "vigesimal"):
        r.update(five)
    return r


def _num_word(rng, lex, k: str, rec: tuple, system: str, inv, kyr: float, lect_id: str):
    h, m, op = rec
    if op == "same":
        w = lex.words.get(h)
        if w is None:
            return None
        c = LX.concept_info(k)
        return LX.Word(c.id, w.form, c.pos, c.freq_class,
                       w.etym + (LX._step(kyr, lect_id, f"colex:{h}", w.form, c.gloss, f"colexified with {h}"),),
                       float(kyr), w.roots, LX.etym_roots(w))
    if h not in lex.words or m not in lex.words:
        return None
    sign = "+" if op == "add" else "x"
    # (a multiplier stands where the lect puts a numeral beside its noun: 'two ten' in a NumN lect, Mandarin er-shi 20;
    # 'ten two' in an NNum lect, Swahili makumi mawili; Greenberg 1978. Without a grammar, on the other side of its base
    # from an addend, so twelve and twenty never meet: Mandarin shi-er 'ten two' 12 vs er-shi 'two ten' 20)
    hd = bool(lex.head_first) if lex.head_first is not None else True
    mf = (lex.systems.get("numeral") or {}).get("mul_first")
    # (polish lane, 2026-11-08: the addend now always stands on the other side from the multiplier. With the grammar's
    # order given, an NNum lect put both after the base, 'ten two' for 12 and for 20: TWELVE = TWENTY in 83 of 612
    # living lects of a24559. Swahili keeps them apart with a linker, kumi na mbili; the order contrast does it here.)
    mul_hf = not mf if mf is not None else not hd
    hf = mul_hf if op == "mul" else not mul_hf
    said = f"{h} {m}" if hf else f"{m} {h}"
    return LX.compound(rng, lex, k, inv, kyr, lect_id, head_first=hf, head=h, modifier=m, process=f"compound:{h}+{m}",
                       note=f"{said.lower()}: counting {system} ({h.lower()} {sign} {m.lower()})")


def draw_system(rng, label: str | None) -> dict:
    opts = SYSTEMS_BY_LABEL.get(label or "decimal", SYSTEMS_BY_LABEL["decimal"])
    w = np.array([x[1] for x in opts])
    system = opts[int(rng.choice(len(opts), p=w / w.sum()))][0]
    quinary = bool(rng.random() < QUINARY_SUB.get(system, 0.0))
    return {"label": label or "decimal", "system": system, "quinary": quinary}


def set_numerals(rng, lex, label: str | None, inv, kyr: float, lect_id: str, system: dict | None = None,
                 mul_first: bool | None = None) -> list:
    """Give `lex` a numeral system for its typology label (or `system`) and build every composite numeral by its recipe
    (in value order, so a part is rebuilt before the numbers made from it). mul_first: the grammar puts a numeral before
    its noun (NumN), so a multiplier precedes its base ('two ten'); kept with the system. Returns [(concept, "system")]."""
    sy = dict(system or draw_system(rng, label))
    if mul_first is not None:
        sy["mul_first"] = bool(mul_first)
    elif "mul_first" not in sy and (lex.systems.get("numeral") or {}).get("mul_first") is not None:
        sy["mul_first"] = lex.systems["numeral"]["mul_first"]
    lex.systems["numeral"] = sy
    out = []
    rec = _recipes(sy["system"], sy["quinary"])
    for k in sorted(rec, key=lambda x: NUM_VALUE[x]):
        if k not in lex.words:
            continue   # (not on this lexicon's concept list)
        w = _num_word(rng, lex, k, rec[k], sy["system"], inv, kyr, lect_id)
        if w is not None:
            lex.set(w)
            out.append((k, "system"))
    return out


def numeral_recipe(lex, k: str):
    sy = lex.systems.get("numeral")
    if not sy:
        return None
    return _recipes(sy["system"], sy["quinary"]).get(k)


def builds_on_five(lex) -> bool | None:
    """Does the lect's counting system build on five (a 5-based or restricted count, or 6-9 as five + n)? None without a
    system."""
    sy = lex.systems.get("numeral")
    if not sy:
        return None
    return sy["system"] in ("quinary", "restricted") or bool(sy.get("quinary"))


def recipe_fits(lex, k: str, head: str, modifier: str) -> bool:
    """May an ordinary compound recipe of data/compounds.tsv name the numeral `k` in this lect? A 'five + n' digit (six =
    'five one') or 'two hands' for ten only where the counting system builds on five: a decimal lect renewing SIX does
    not reach for five-one (grammar A's leftover, 2026-11-08). The subtractive and multiplicative ones (nine 'one from
    ten', Finnish yhdeksän; eight 'two fours') fit any system. Every other concept: True."""
    if k not in NUM_VALUE:
        return True
    five = builds_on_five(lex)
    if five is None or five:
        return True
    return not (head == "FIVE" or (k == "TEN" and head == "HAND"))


def system_word(rng, lex, k: str, inv, kyr: float, lect_id: str):
    """A replacement hit on a system word: a composite numeral is re-formed from its current parts (NUM_REFORM) or kept
    (KEEP); None for every other concept (the ordinary sources apply)."""
    rec = numeral_recipe(lex, k)
    if rec is None:
        return None
    if rng.random() >= NUM_REFORM or inv is None:
        return KEEP
    w = _num_word(rng, lex, k, rec, lex.systems["numeral"]["system"], inv, kyr, lect_id)
    if w is None or (k in lex.words and w.form == lex.words[k].form):
        return KEEP
    return w


# --- colour terms ------------------------------------------------------------------------------------------------------
COLOUR_ORDER = ("WHITE", "BLACK", "RED", "YELLOW", "GREEN", "BLUE", "BROWN")
_W, _BK, _R, _Y, _G, _BU, _BR = COLOUR_ORDER
# stage -> partition (each group's first member is its focus: the word it keeps when the group splits)
STAGES = {
    "I": ((_W, _R, _Y), (_BK, _G, _BU, _BR)),
    "II": ((_W,), (_R, _Y, _BR), (_BK, _G, _BU)),
    "IIIa": ((_W,), (_R,), (_Y, _BR), (_BK, _G, _BU)),
    "IIIb": ((_W,), (_R, _Y, _BR), (_G, _BU), (_BK,)),
    "IV": ((_W,), (_R,), (_Y, _BR), (_G, _BU), (_BK,)),
    "V": ((_W,), (_R,), (_Y, _BR), (_G,), (_BU,), (_BK,)),
    "VI": tuple((c,) for c in COLOUR_ORDER),
}
NEXT_STAGE = {"I": ("II",), "II": ("IIIa", "IIIb"), "IIIa": ("IV",), "IIIb": ("IV",), "IV": ("V",), "V": ("VI",)}
# proto stages, 20 kyr ago (foragers): weighted toward the early stages, so living lects spread over II-VI like the
# World Color Survey's 110 languages (most at III-V, grue common, few with a brown); calibrate with COLOUR_SPLIT
STAGE_WEIGHTS = {"I": 0.04, "II": 0.14, "IIIa": 0.1, "IIIb": 0.16, "IV": 0.3, "V": 0.16, "VI": 0.1}
COLOUR_SPLIT = 0.0008   # per generation: a lect's next B&K split, x (population / COLOUR_POP) ** 0.5 clipped to 0.5-2
COLOUR_POP = 20000.0
_RANK = {_W: 0, _BK: 0, _R: 1, _Y: 2, _G: 2, _BU: 3, _BR: 4}


def colour_partition(lex) -> tuple:
    """The lect's colour categories, read off the forms: colour concepts that share a form are one category. Groups in
    COLOUR_ORDER, each led by its earliest member."""
    by: dict = {}
    for c in COLOUR_ORDER:
        w = lex.words.get(c)
        if w is not None:
            by.setdefault(w.form, []).append(c)
    return tuple(sorted((tuple(sorted(g, key=COLOUR_ORDER.index)) for g in by.values()),
                        key=lambda g: COLOUR_ORDER.index(g[0])))


def _canon(p) -> tuple:
    return tuple(sorted((tuple(sorted(g, key=COLOUR_ORDER.index)) for g in p), key=lambda g: COLOUR_ORDER.index(g[0])))


_STAGE_OF = {_canon(v): k for k, v in STAGES.items()}


def colour_stage(lex) -> str:
    """The B&K stage of the lect's partition, or "other" (a partition the stages do not list, after a loan)."""
    return _STAGE_OF.get(_canon(colour_partition(lex)), "other")


def _group_word(lex, members: tuple, src_word, kyr: float, lect_id: str) -> None:
    for c in members:
        if c == src_word.concept:
            continue
        ci = LX.concept_info(c)
        lex.words[c] = LX.Word(c, src_word.form, ci.pos, ci.freq_class,
                               src_word.etym + (LX._step(kyr, lect_id, f"colex:{src_word.concept}", src_word.form,
                                                         ci.gloss, f"colexified with {src_word.concept}"),),
                               float(kyr), src_word.roots, LX.etym_roots(src_word))


def set_colours(rng, lex, kyr: float, lect_id: str, stage: str | None = None) -> str:
    """A proto-language's colour stage: each composite category takes its focus's word (the members' own proto roots are
    dropped). Returns the stage."""
    if stage is None:
        ks = list(STAGE_WEIGHTS)
        w = np.array([STAGE_WEIGHTS[k] for k in ks])
        stage = ks[int(rng.choice(len(ks), p=w / w.sum()))]
    for g in STAGES[stage]:
        if len(g) > 1 and g[0] in lex.words:
            _group_word(lex, tuple(c for c in g if c in lex.words), lex.words[g[0]], kyr, lect_id)
    return stage


def _new_colour_word(rng, lex, members: tuple, inv, kyr: float, lect_id: str):
    """A word for a category splitting off: from an object word by derivation ('like' rows), else a fresh root."""
    head = min(members, key=lambda c: (_RANK[c], COLOUR_ORDER.index(c)))
    w = LX.derive(rng, lex, head, inv, kyr, lect_id, meaning="like")
    if w is None or LX._clashes(lex, head, w.form):
        w = LX.coin(rng, lex, head, inv, kyr, lect_id, how="root", store=False)
    return head, w


def split_colours(rng, lex, inv, kyr: float, lect_id: str, target: tuple | None = None) -> list:
    """One step along the B&K order: the lect's partition moves to the next stage (or, off the table, its latest-ranked
    composite member leaves its group). The part with the old focus keeps the word; the other part gets a new one.
    Returns [(concept, "colour")]."""
    cur = colour_partition(lex)
    st = _STAGE_OF.get(_canon(cur))
    if target is None:
        if st is not None:
            nxt = NEXT_STAGE.get(st)
            if not nxt:
                return []
            target = STAGES[nxt[int(rng.integers(len(nxt)))]]
        else:
            comp = [(g, c) for g in cur if len(g) > 1 for c in g[1:]]
            if not comp:
                return []
            g, c = min(comp, key=lambda x: (_RANK[x[1]], COLOUR_ORDER.index(x[1])))
            target = tuple(x for x in cur if x != g) + (tuple(y for y in g if y != c), (c,))
    out = []
    for g in cur:
        parts = [tuple(c for c in t if c in g) for t in target]
        parts = [p for p in parts if p]
        if len(parts) < 2:
            continue
        for p in parts:
            if g[0] in p:
                continue   # (the focus's part keeps the word)
            head, w = _new_colour_word(rng, lex, p, inv, kyr, lect_id)
            lex.set(w)
            _group_word(lex, p, w, kyr, lect_id)
            out += [(c, "colour") for c in p]
    return out


def colour_group(lex, k: str) -> tuple:
    """The colour concepts sharing `k`'s current form (`k` included), or `k`'s kin-system group (`kin_group`); () for
    any other concept."""
    if k not in _RANK and k in KIN_CONCEPTS:
        return kin_group(lex, k)
    if k not in _RANK or k not in lex.words:
        return ()
    f = lex.words[k].form
    return tuple(c for c in COLOUR_ORDER if c in lex.words and lex.words[c].form == f)


def after_replace(lex, k: str, src: str, new, contact_words, kyr: float, lect_id: str, group: tuple) -> None:
    """After `k` got a new word in `lexicon.step` (`group`: its colour category before): a colour composite moves as one
    word, unless the word is a loan from a lect that keeps `k` apart (then `k` splits off: a colour term borrowed with
    its meaning)."""
    if len(group) < 2:
        return
    if src == "borrow" and contact_words:
        d = new.etym[-1].process.split(":", 1)[1] if new.etym and new.etym[-1].process.startswith("borrow:") else None
        dl = contact_words.get(d) if d else None
        if dl is not None and k in dl and all(dl.get(c) is None or dl[c].form != dl[k].form for c in group if c != k):
            return
    _group_word(lex, tuple(c for c in group if c in lex.words), new, kyr, lect_id)


# --- kinship systems ----------------------------------------------------------------------------------------------------
# Murdock's six cousin-terminology types (Murdock 1949, Social Structure), as which kin share one word. A group's first
# member is its focus (it keeps the word when the group splits). Crow and Omaha skew the cross cousins into the
# generation above (Crow: father's sister's child called as father's sister; Omaha: mother's brother's child as mother's
# brother); with one CROSS COUSIN concept the skew is shown on it.
FB, MB, FZ, MZ, PC, CC = "FATHER'S BROTHER", "MOTHER'S BROTHER", "FATHER'S SISTER", "MOTHER'S SISTER", "PARALLEL COUSIN", "CROSS COUSIN"
KIN_SYSTEMS = {
    "hawaiian": (("FATHER", FB, MB, "UNCLE"), ("MOTHER", MZ, FZ, "AUNT"), ("BROTHER", PC, CC, "COUSIN")),
    "eskimo": ((FB, MB, "UNCLE"), (FZ, MZ, "AUNT"), ("COUSIN", PC, CC)),
    "iroquois": (("FATHER", FB), ("MOTHER", MZ), (MB, "UNCLE"), (FZ, "AUNT"), ("BROTHER", PC), ("COUSIN", CC)),
    "sudanese": ((FB, "UNCLE"), (FZ, "AUNT"), (PC, "COUSIN")),
    "crow": (("FATHER", FB), ("MOTHER", MZ), (MB, "UNCLE"), (FZ, "AUNT", CC, "COUSIN"), ("BROTHER", PC)),
    "omaha": (("FATHER", FB), ("MOTHER", MZ), (MB, "UNCLE", CC, "COUSIN"), (FZ, "AUNT"), ("BROTHER", PC)),
}
KIN_CONCEPTS = ("FATHER", "MOTHER", "BROTHER", "UNCLE", "AUNT", "COUSIN", FB, MB, FZ, MZ, PC, CC)
# proto weights: the Ethnographic Atlas's cousin terminologies, from memory (≈; Murdock 1967): Hawaiian about a third,
# Iroquois a fifth, Crow and Omaha an eighth each, Eskimo a tenth, Sudanese rare
KIN_WEIGHTS = {"hawaiian": 0.33, "iroquois": 0.22, "crow": 0.13, "omaha": 0.13, "eskimo": 0.12, "sudanese": 0.07}
# a system changes to a neighbouring one (the typological drift paths: generational <-> lineal <-> descriptive, bifurcate
# merging <-> its skewed forms); per generation
KIN_NEXT = {"hawaiian": ("eskimo", "iroquois"), "eskimo": ("hawaiian", "sudanese"), "iroquois": ("hawaiian", "crow", "omaha"),
            "sudanese": ("eskimo", "iroquois"), "crow": ("iroquois",), "omaha": ("iroquois",)}
KIN_CHANGE = 0.0006
# The culture steers the drift (lexcon pass 2): a terminology follows the marriage rules its people keep (Murdock 1949,
# Social Structure: bifurcate-merging terms go with exogamous unilineal kin groups; a cross / parallel cousin split with
# cross-cousin marriage, the 'Dravidian' and Iroquois kind; lineal Eskimo and generational Hawaiian terms with bilateral
# kin and no clans). The culture's kinship taboos (taboos.json: clan_exogamy, cousin_one_side) weight the next system,
# and a lect whose system its culture does not favour changes up to KIN_PULL_MAX times faster.
KIN_PULL = {"clan_exogamy": {"iroquois": 2.0, "crow": 2.0, "omaha": 2.0},
            "cousin_one_side": {"iroquois": 3.0, "crow": 1.5, "omaha": 1.5},
            None: {"hawaiian": 1.5, "eskimo": 1.5}}
KIN_PULL_MAX = 3.0


def kin_pull(rules) -> dict | None:
    """Weights per kinship system from a culture's taboo rule ids (KIN_PULL); None when the culture is not known."""
    if rules is None:
        return None
    w = {k: 1.0 for k in KIN_SYSTEMS}
    hit = [r for r in ("clan_exogamy", "cousin_one_side") if r in rules]
    for r in hit or [None]:
        for k, x in KIN_PULL[r].items():
            w[k] *= x
    return w


def _kin_groups(system: str) -> list:
    """All the system's groups, with every kin concept it does not group standing alone."""
    gs = [tuple(g) for g in KIN_SYSTEMS[system]]
    seen = {c for g in gs for c in g}
    return gs + [(c,) for c in KIN_CONCEPTS if c not in seen]


def set_kin(rng, lex, kyr: float, lect_id: str, inv=None, system: str | None = None) -> list:
    """Give `lex` a kinship system (drawn by KIN_WEIGHTS unless given) and make its words agree: each group takes the word
    its focus has (or, when the focus's word is shared with kin the system now keeps apart, a new word: a descriptive
    compound like 'mother-brother', a derivation, or a fresh root). Returns [(concept, "kin")]."""
    if system is None:
        ks = sorted(KIN_WEIGHTS)
        w = np.array([KIN_WEIGHTS[k] for k in ks])
        system = ks[int(rng.choice(len(ks), p=w / w.sum()))]
    lex.systems["kin"] = {"system": system}
    out = []
    groups = [tuple(c for c in g if c in lex.words) for g in _kin_groups(system)]
    groups = [g for g in groups if g]
    taken: dict = {}
    for g in groups:
        f = lex.words[g[0]].form
        owner = taken.get(f)
        if owner is not None and owner != g:   # (the focus still shares a word with another group: it needs its own)
            new = None
            if inv is not None:
                new = LX.compound(rng, lex, g[0], inv, kyr, lect_id) or LX.derive(rng, lex, g[0], inv, kyr, lect_id)
                if new is None:
                    new = LX.coin(rng, lex, g[0], inv, kyr, lect_id, how="root", store=False)
            if new is None:
                continue
            lex.set(new)
            out.append((g[0], "kin"))
            f = new.form
        taken[f] = g
        for c in g[1:]:
            if lex.words[c].form != f:
                _group_word(lex, (g[0], c), lex.words[g[0]], kyr, lect_id)
                out.append((c, "kin"))
    return out


def kin_group(lex, k: str) -> tuple:
    """The concepts of `k`'s group in the lect's kinship system that share `k`'s current form; () if none."""
    sy = (lex.systems.get("kin") or {}).get("system")
    if sy is None or k not in lex.words:
        return ()
    f = lex.words[k].form
    for g in _kin_groups(sy):
        if k in g:
            return tuple(c for c in g if c in lex.words and lex.words[c].form == f)
    return ()


# --- speech taboos and avoidance registers (lexcon pass 2; contact-gaps rec. 7, lexicon-gaps rec. 6) ----------------
# A culture whose taboos ban the names of the dead or of the ruler and the words that sound like them (taboos.json
# dead_soundalike, ruler_name) replaces its words faster: Australian languages (Dixon 1980, The Languages of Australia,
# ch. 2: a word like a dead person's name is dropped for a synonym or a neighbour's word) and Tahitian pi'i (words in a
# chief's name replaced). Each such rule raises the open-class hazard by SPEECH_TABOO_X (judgement: Dixon reckons the
# effect large but gives no rate).
SPEECH_TABOO_X = {"dead_soundalike": 0.3, "ruler_name": 0.2}


def speech_taboo(rules) -> float:
    """The replacement-hazard factor from a culture's speech taboos (1.0 without)."""
    return 1.0 + sum(x for r, x in SPEECH_TABOO_X.items() if rules and r in rules)


# An avoidance register (a 'mother-in-law language': Dyirbal Jalnguy, Guugu Yimidhirr; Dixon 1972, Haviland 1979): where
# the culture has the in-law avoidance rules (taboos.json motherinlaw, inlaw_words) the lect keeps a second word for
# everyday meanings, used before the avoided kin. Jalnguy words are often a neighbour's everyday word, or a general term
# standing for several ordinary ones; here: a contact lect's word (AVOID_LOAN) or a paraphrase 'the <quality> one'
# (lexicon.taboo_word), else a derivation. Built for the living lects as they stand today (`avoidance`), not inherited.
AVOID_CONCEPTS = ("EAT", "DRINK", "SEE", "HEAR", "GO", "COME", "SIT", "SLEEP", "WATER", "FIRE", "HAND", "EYE", "FOOT",
                  "HEAD", "HOUSE", "DOG", "FISH", "MEAT", "SPEAK", "GIVE")
AVOID_LOAN = 0.5
#: PW-1537 R10: a Jalnguy word is a general term over one semantic field (Dixon 1972: one avoidance verb for several
#: everyday verbs of a kind), never one word for unrelated meanings ('eat', 'see', 'sit' and 'sleep' all o˨n). Within a
#: group the first meaning's avoidance word serves the others; across groups a form is never used twice.
AVOID_GROUPS = (("EAT", "DRINK"), ("SEE", "HEAR"), ("GO", "COME"), ("SIT", "SLEEP"), ("HAND", "FOOT"))


def avoidance(rng, lex, inv, kyr: float, lect_id: str, contact_words: dict | None = None, profile=None) -> dict:
    """{concept: [ipa, how, note]} for the avoidance register of `lex` (AVOID_CONCEPTS it has); stored in
    lex.systems["avoidance"]."""
    out = {}
    donors = sorted(contact_words or {})
    group_of = {LX.resolve(c): g for g in AVOID_GROUPS for c in g}
    used: dict = {}   # avoidance ipa -> its group (or concept)
    for k in AVOID_CONCEPTS:
        k = LX.resolve(k)
        if k not in lex.words:
            continue
        cur = lex.words[k].form
        grp = group_of.get(k)
        if grp is not None:
            first = next((LX.resolve(c) for c in grp if LX.resolve(c) in out), None)
            if first is not None and out[first][0] != LX.word_ipa(cur):
                out[k] = [out[first][0], "general term", f"the avoidance word for '{first.lower()}' serves for both"]
                continue
        w, how = None, None
        have = [d for d in donors if k in contact_words[d] and contact_words[d][k].form != cur]
        if have and rng.random() < AVOID_LOAN:
            d = have[int(rng.integers(len(have)))]
            w = LX.borrow(contact_words[d][k], d, lex, profile, inv, kyr, "avoidance register", store=False)
            how = f"loan from {d}"
        if w is None:
            w = LX.taboo_word(rng, lex, k, inv, kyr, lect_id, generic=True)   # ('the <quality> one': PW-1739)
            how = "paraphrase" if w is not None else None
        if w is None:
            w = LX.derive(rng, lex, k, inv, kyr, lect_id)
            how = "derived" if w is not None else None
        if w is not None and used.get(LX.word_ipa(w.form), grp or k) != (grp or k):
            w2 = LX.derive(rng, lex, k, inv, kyr, lect_id)   # (a form another field took: derive instead)
            w, how = (w2, "derived") if w2 is not None and LX.word_ipa(w2.form) not in used else (None, None)
        if w is None or w.form == cur:
            continue
        used[LX.word_ipa(w.form)] = grp or k
        out[k] = [LX.word_ipa(w.form), how, w.etym[-1].note or ""]
    lex.systems["avoidance"] = out
    return out


SYSTEM_CONCEPTS = frozenset((*NUMERALS, "MANY", *COLOUR_ORDER, *KIN_CONCEPTS))


# --- the per-step systems --------------------------------------------------------------------------------------------
def systems_step(rng, lex, n_generations: float, inv, kyr: float, lect_id: str, numeral_base: str | None = None,
                 population: float | None = None, contact_words=None, weights=None, kin_weights: dict | None = None) -> list:
    """The systems' own clocks, once per lexicon step: a numeral system follows its grammar's label (a changed label
    re-draws the system and rebuilds the composites), a restricted system grows into a 5-based one in a large people,
    and the colour terms take their next B&K split."""
    out = []
    sy = lex.systems.get("numeral")
    if sy is not None and numeral_base is not None and numeral_base != sy.get("label"):
        out += set_numerals(rng, lex, numeral_base, inv, kyr, lect_id)
    elif sy is not None and sy.get("system") == "restricted" and (population or 0.0) >= RESTRICT_POP:
        if rng.random() < 1.0 - (1.0 - RESTRICT_UP) ** n_generations:
            out += set_numerals(rng, lex, sy["label"], inv, kyr, lect_id,
                                system={"label": sy["label"], "system": "quinary", "quinary": True})
    ksy = (lex.systems.get("kin") or {}).get("system")
    if ksy is not None:
        nx = KIN_NEXT[ksy]
        kw = np.array([(kin_weights or {}).get(k, 1.0) for k in nx])
        up = min(KIN_PULL_MAX, max(1.0, kw.max() / (kin_weights or {}).get(ksy, 1.0)))   # (a disfavoured system moves sooner)
        if rng.random() < 1.0 - (1.0 - KIN_CHANGE * up) ** n_generations:
            out += set_kin(rng, lex, kyr, lect_id, inv, system=nx[int(rng.choice(len(nx), p=kw / kw.sum()))])
    if any(c in lex.words for c in COLOUR_ORDER) and any(len(g) > 1 for g in colour_partition(lex)):
        pf = min(2.0, max(0.5, ((population or COLOUR_POP) / COLOUR_POP) ** 0.5))
        if rng.random() < 1.0 - (1.0 - COLOUR_SPLIT * pf) ** n_generations:
            out += split_colours(rng, lex, inv, kyr, lect_id)
    return out


def system_colex(lex, cs) -> bool:
    """Do the concepts `cs` share a form because a system says so (a colour composite; HUNDRED = MANY in a restricted
    count)? Such a group is not repaired as a homophone."""
    cs = list(cs)
    if all(c in _RANK for c in cs):
        return True
    ksy = (lex.systems.get("kin") or {}).get("system")
    if ksy is not None and all(c in KIN_CONCEPTS for c in cs) and any(set(cs) <= set(g) for g in _kin_groups(ksy)):
        return True
    if set(cs) <= {"MANY", "HUNDRED", "THOUSAND"}:
        sy = lex.systems.get("numeral") or {}
        return sy.get("system") == "restricted"
    return False


# --- sound symbolism ---------------------------------------------------------------------------------------------------
NURSERY = {"MOTHER": (0.6, "nasal"), "FATHER": (0.55, "stop")}
P_SYMBOL = 0.3
# concept -> (slot, wanted): slot "C" replaces the first consonant, "V" the first vowel
SYMBOLIC = {"NOSE": ("C", "nasal"), "TONGUE": ("C", "l"), "LEAF": ("C", "l"), "ROUND": ("C", "r"), "RED": ("C", "r"),
            "SMALL": ("V", "i"), "NAME": ("V", "i"), "SAND": ("C", "s"), "BONE": ("C", "k"), "BREAST": ("C", "m"),
            "FULL": ("C", "p"), "KNEE": ("V", "u")}


def _pick_seg(rng, inv, want: str):
    cs, vs = list(inv.consonants), list(inv.vowels)
    if want == "nasal":
        c = [s for s in cs if s.manner == 3 and s.place in (0, 1, 2) and not s.source2 and s.register == 0]
        c.sort(key=lambda s: (s.place != 0, s.place, s.secondary, s.length))
    elif want == "m":
        c = [s for s in cs if s.manner == 3 and s.place == 0 and not s.secondary]
    elif want == "stop":
        c = [s for s in cs if s.manner == 0 and s.place in (0, 1, 2) and s.larynx in (0, 1) and not s.secondary
             and not s.double]
        c.sort(key=lambda s: (s.place != 0, s.place, s.voice, s.larynx))
    elif want == "p":
        c = [s for s in cs if s.manner == 0 and s.place == 0 and s.larynx in (0, 1) and not s.double]
    elif want == "k":
        c = [s for s in cs if s.manner == 0 and s.place == 5 and s.larynx in (0, 1) and not s.secondary]
    elif want == "l":
        c = [s for s in cs if s.manner == 5 and not s.secondary]
    elif want == "r":
        c = [s for s in cs if s.manner in (6, 7) and not s.secondary]
    elif want == "s":
        c = [s for s in cs if s.manner == 2 and s.sibilant and s.place in (1, 2) and not s.voice]
    elif want == "open":
        c = sorted(vs, key=lambda s: (s.height, abs(s.back - 2), s.nasal, s.length, s.tone))
        return c[0] if c else None
    elif want == "i":
        c = [s for s in vs if s.height >= 5 and s.back <= 1 and not s.round and not s.nasal]
    elif want == "u":
        c = [s for s in vs if s.height >= 4 and s.back >= 3 and s.round and not s.nasal]
    else:
        return None
    if not c:
        return None
    if want in ("nasal", "stop"):   # mostly the first (labial), sometimes a dental (nana, tata)
        return c[0] if rng.random() < 0.65 or len(c) == 1 else c[1 + int(rng.integers(len(c) - 1))]
    return c[int(rng.integers(len(c)))]


def symbolic(rng, form: tuple, concept: str, inv) -> tuple:
    """`form` reshaped by a nursery pattern (MOTHER, FATHER) or a sound-symbolic link (SYMBOLIC), with its chance; else as
    it was. The result is repaired to the inventory's phonotactics."""
    if inv is None or not form:
        return form
    if concept in NURSERY:
        p, want = NURSERY[concept]
        if rng.random() >= p:
            return form
        c, v = _pick_seg(rng, inv, want), _pick_seg(rng, inv, "open")
        if c is None or v is None:
            return form
        f = (c, v, c, v) if rng.random() < 0.6 else (c, v)
        return _inv.repair(f, inv) or form
    if concept in SYMBOLIC and rng.random() < P_SYMBOL:
        slot, want = SYMBOLIC[concept]
        s = _pick_seg(rng, inv, want)
        if s is None:
            return form
        idx = next((j for j, x in enumerate(form) if x.kind == slot), None)
        if idx is None:
            return form
        f = form[:idx] + (s,) + form[idx + 1:]
        return _inv.repair(f, inv) or form
    return form
