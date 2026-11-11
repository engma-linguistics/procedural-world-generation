"""Contact kinds in borrowing (PW-1636, language lane 13; proposal-2026-11-10-paradigms-and-conquest.md Part 2, owner
rulings D2.1 B and D2.2 B): which words a lect borrows depends on who it borrows them from.

- **Field profiles by contact kind (P1).** history.loan_kinds labels each donor of a lect: `elite` (a ruling people: an
  elite-incursion or a takeover trigger with the donor's deme as ruler; the old speech of a deme that shifted under one,
  borrowing from the rulers' speech), `trade` (a trade trigger, or a deme that passed a crop, a herd animal or a
  technology here lately, another people), `city` (a mixed city), else `flat` (neighbours, swamping newcomers, the other speech of the
  deme). `mult(kind, concept)` is the profile's multiplier for the concept's field (`field_group`): rulers lend law,
  rule, faith, war, dress, the house and cuisine (Baugh & Cable 2002 ch. 7, the French domains of English; Tadmor 2009's
  field spread), traders lend commerce, measure, money, goods and drink, a mixed city crafts, the house, dress and food.
  Each profile is mean-normalised over the concept list (closed-class words excluded and fixed at 1), so the volume of
  borrowing is unchanged and only its spread moves; crops stay at x1 under trade (the food routes already carry them:
  wheat is a loan in 76% of a24559's lects). lexicon.step multiplies the loan source by the donors' pull-weighted mean
  multiplier and draws the donor by pull x multiplier: the ruler supplies the law word, the trader the market word.
- **Trade numerals: hundred and up.** Thomason & Kaufman's trade layers bring the high numerals first (Swahili mia, elfu;
  the Sino-Japanese and Sino-Korean sets). Owner ruling 2026-11-11 (desk card p.numerals, A): trade raises HUNDRED and
  THOUSAND x3 (`TRADE_NUMERALS`, {concept: multiplier}, applied by the trade profile to those closed-class numerals);
  six to nine and whole second numeral sets come later. Every other closed-class word keeps x1.
- **Doublets (P2).** When a lect is borrowing concept k from an elite donor (or, for products only, a trade or city donor),
  the loan can come in beside the native word instead of replacing it (`doublet`):
  - a **meaning split** (data/splits.tsv): k is an animal or an ingredient, and the donor's word for k is kept for its
    meat or its product, the native word keeping k. Old French boef 'ox' became English beef 'ox meat' beside native
    cow; Latin vinum came into Germanic as the wine beside native grape words. For a product the donor's own word for
    the product is taken when it has one (Latin caseus > cheese), else its word for k, narrowed. The other way round, a
    meat word being replaced by an elite donor's word is the donor's word for the animal, narrowed (`narrow_meat`);
  - a **register split** (no split child): the loan is kept as a high-register synonym, `high:<k>` in the lexicon while
    the history runs (sound change reaches it, and it dies at the word's own replacement hazard x HIGH_DEATH: doublets
    are not permanent), and moved into `systems.registers.high` at the end of the pass (`finish_registers`), the shape of
    the faiths' learned register: {concept: [ipa, "doublet" | "synonym", donor lect, kyr]} (English ask / question,
    kingly / royal, Thai rachasap).
  Every loan's etymology note names its channel ("contact, elite"), so the pages and checks can tell a conqueror's word
  from a neighbour's.
"""
from __future__ import annotations

import csv
import functools
from dataclasses import replace
from pathlib import Path

DATA = Path(__file__).parent / "data"

KINDS = ("elite", "trade", "city", "flat")
ELITE_TRIGGERS = ("elite", "takeover")   # (on a24559 the shift triggers are takeover 87, elite 1: takeover is the elite case)
# raw multipliers by field group (field_group) before mean-normalisation; groups not named are x1
RAW = {
    "elite": {"law": 4.0, "social": 4.0, "religion": 3.0, "war": 3.0, "dress": 2.0, "house": 2.0, "cuisine": 3.0,
              "table": 2.0, "commerce": 1.5, "body": 0.25, "kin": 0.25, "sense": 0.25, "motion": 0.25, "basic": 0.25,
              "nature": 0.25},
    "trade": {"commerce": 3.0, "goods": 2.5, "cuisine": 1.5, "table": 1.0, "body": 0.5, "kin": 0.5},
    "city": {"dress": 2.0, "house": 2.0, "cuisine": 2.0, "table": 1.5, "goods": 1.5, "craft": 2.0},
    "flat": {},
}
CAP = {"trade": {"crop": 1.0}}   # (fixed multipliers, outside the normalisation: crops under trade stay x1)
TRADE_NUMERALS: dict = {"HUNDRED": 3.0, "THOUSAND": 3.0}   # owner 2026-11-11, desk card p.numerals A: hundred and up only
# doublets: chance a loan drawn from a donor of this kind comes in beside the native word (meaning split; register split)
# ("table" = the animals and ingredients of data/splits.tsv: a ruler's word for the ox comes to the table, and at
# DOUBLET_P 0.7 most of those extra loans become the meat word, not the animal's)
DOUBLET_P = {"elite": 0.7, "trade": 0.3, "city": 0.2}
SPLIT_KINDS = {"elite": ("meat", "product"), "trade": ("product",), "city": ("product",)}
REGISTER_P = {"elite": 0.15}
REGISTER_MIN_FREQ = 3   # (the most frequent words, freq classes 1-2, are not doubled: English kept 'go', 'eat' alone)
# a formal synonym only where formal registers have them: the fields the elite profile raises (rule, law, faith, war,
# dress, the house, cuisine, commerce) and the abstract ones (English fear / terror, ask / question, think / cogitate);
# no formal word for frog, jaw or bite (a first pass gave them: 4.6 per language, mostly body and nature words)
REGISTER_FIELDS = ("Emotions and values", "Cognition", "Speech and language")
HIGH = "high:"
HIGH_DEATH = 1.0   # a high-register doublet dies at this x its concept's replacement hazard

_LAW = {"STEAL", "THIEF", "LAW", "JUDGE", "COURT", "TAX", "RULE"}
_SOCIAL = {"CHIEF", "KING", "NOBLE", "TOWN", "SERVANT", "MASTER", "SLAVE", "COUNTRY", "STRANGER", "ENEMY", "FRIEND", "GUEST",
           "ELDER"}
_RELIGION = {"GOD", "SPIRIT", "PRIEST", "TEMPLE", "ANCESTORS", "SOUL", "HOLY", "PRAY", "SACRIFICE", "OMEN", "DEMON"}
_WAR = {"WAR", "FIGHTER", "SPEAR", "SOLDIER", "SHIELD", "FIGHT"}
_CUISINE = {"BREAD", "CHEESE", "BUTTER", "WINE", "SOUP", "FEAST", "MEAL", "BEER", "MEAD", "SPIRITS", "VINEGAR", "PORRIDGE",
            "DOUGH", "CURD", "FISH SAUCE", "SUGAR", "PALM WINE", "RICE WINE", "COOK", "BOIL", "ROAST OR FRY", "BAKE",
            "COOKED", "OVEN", "SALT (FOOD)", "PICKLE", "STEAM (FOOD)", "SMOKE (FOOD)", "FERMENT", "KNEAD", "YEAST",
            "GRIDDLE", "TASTY", "FRAGRANT", "BEVERAGE", "FLOUR", "QUERN"}
_COMMERCE = {"BUY", "SELL", "MARKET", "PAY", "LEND", "BORROW", "EARN", "MERCHANT", "TRADE OR BARTER", "RICH", "POOR",
             "COUNT", "PRICE", "MONEY", "DEBT", "WEIGH", "MEASURE", "PROFIT", "ACCOUNT"}
_CRAFT = {"SMITH", "SMITHING", "KNIFE", "AXE", "NEEDLE", "CUP", "POT", "BOWL", "JUG", "MORTAR"}
PRESTIGE = ("law", "social", "religion", "war")   # (the proposal's "prestige" group, for the check)
_FIELD = {"Law": "law", "Social and political relations": "social", "Religion and belief": "religion",
          "Warfare and hunting": "war", "Clothing and grooming": "dress", "The house": "house", "The body": "body",
          "Kinship": "kin", "Sense perception": "sense", "Motion": "motion", "Animals": "nature",
          "Agriculture and vegetation": "nature", "The physical world": "nature"}
_NATURE_DOMAINS = ("landscape", "animal", "fauna", "flora")


@functools.cache
def field_group(cid: str) -> str:
    """The loan-profile field of a concept: closed | law | social | religion | war | dress | house | cuisine | commerce |
    craft | goods | table | crop | body | kin | sense | motion | nature | basic | other."""
    from . import lexicon as LX
    k = LX.resolve(cid)
    if k.startswith(HIGH):
        k = k[len(HIGH):]
    if LX.closed_class(k):
        return "closed"
    if k.startswith("meat:") or k in _CUISINE:
        return "cuisine"
    if k in splits():
        return "table"
    for s, g in ((_LAW, "law"), (_SOCIAL, "social"), (_RELIGION, "religion"), (_WAR, "war"), (_COMMERCE, "commerce"),
                 (_CRAFT, "craft")):
        if k in s:
            return g
    c = LX.concept_info(k)
    if c.domain == "crop":
        return "crop"
    if c.domain in ("good", "fuel") and not c.proto or k.startswith("good:"):
        return "goods"
    if c.field in _FIELD:
        return _FIELD[c.field]
    if c.domain == "kin":
        return "kin"
    if c.domain in _NATURE_DOMAINS:
        return "nature"
    if c.lists & {"LJ100", "SW100"}:
        return "basic"
    return "other"


@functools.cache
def _profiles() -> dict:
    """{kind: {group: multiplier}}, each mean-normalised over the open-class concept list (CAP groups fixed)."""
    from . import lexicon as LX
    groups = [field_group(c.id) for c in LX.concepts() if c.pos != "NAME"]
    groups = [g for g in groups if g != "closed"]
    out = {}
    for kind, raw in RAW.items():
        cap = CAP.get(kind, {})
        fixed = sum(cap[g] for g in groups if g in cap)
        free = sum(raw.get(g, 1.0) for g in groups if g not in cap)
        s = (len(groups) - fixed) / free if free > 0 else 1.0
        m = {g: raw.get(g, 1.0) * s for g in set(groups) | set(raw) if g not in cap}
        m.update(cap)
        m["closed"] = 1.0
        out[kind] = m
    return out


def profile(kind: str) -> dict:
    """{field group: multiplier} of a contact kind's profile (normalised)."""
    return _profiles().get(kind if kind in RAW else "flat", {})


def mult(kind: str | None, cid: str) -> float:
    """The loan multiplier of concept `cid` from a donor of contact kind `kind` (1 for flat contact and closed-class words;
    the trade numerals hook aside)."""
    if kind is None or kind == "flat":
        return 1.0
    g = field_group(cid)
    if g == "closed":
        return float(TRADE_NUMERALS.get(cid, 1.0)) if kind == "trade" else 1.0
    return _profiles().get(kind, {}).get(g, 1.0)


def register_field(cid: str) -> bool:
    """A concept that can take a formal synonym (REGISTER_FIELDS, or a field the elite profile raises)."""
    from . import lexicon as LX
    return mult("elite", cid) > 1.0 or LX.concept_info(cid).field in REGISTER_FIELDS


def channel(kind: str | None) -> str:
    """The etymology note of a contact loan: 'contact' (flat), 'contact, elite' ..."""
    return "contact" if kind in (None, "flat") else f"contact, {kind}"


def kind_of_note(note: str) -> str | None:
    """The contact kind a loan's note names (`channel`), else None."""
    if not note or not note.startswith("contact"):
        return None
    rest = note[len("contact"):].split(";")[0].strip(" ,")
    return rest.split()[0] if rest and rest[0] != "(" else "flat"   # ('contact (paradigm repair)': a flat loan)


# --- meaning splits ----------------------------------------------------------------------------------------------------
@functools.cache
def splits() -> dict:
    """{parent concept: ((child, kind), ...)} from data/splits.tsv."""
    with open(DATA / "splits.tsv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader([ln for ln in f if not ln.startswith("#")], delimiter="\t"))
    out: dict = {}
    for r in rows:
        out.setdefault(r["parent"], []).append((r["child"], r["kind"]))
    return {k: tuple(v) for k, v in out.items()}


@functools.cache
def split_parents() -> dict:
    """{child concept: ((parent, kind), ...)}."""
    out: dict = {}
    for p, ch in splits().items():
        for c, kd in ch:
            out.setdefault(c, []).append((p, kd))
    return {k: tuple(v) for k, v in out.items()}


def gloss_of(cid: str) -> str:
    """The gloss a doublet's note quotes for a concept ('cattle', 'milk')."""
    from . import lexicon as LX
    return LX.concept_info(cid).gloss


def _narrowed(w, child: str, parent: str, note: str):
    """A loan Word `w` (made for `parent`) relabelled to `child`, its loan step glossed with the child and noted."""
    from . import lexicon as LX
    c = LX.concept_info(child)
    st = w.etym[-1]
    pc = LX.concept_info(parent)
    st = replace(st, gloss=c.gloss, note=(note + f"; the donor's word for '{pc.gloss}', kept for '{c.gloss}'"))
    return replace(w, concept=c.id, pos=c.pos, freq_class=c.freq_class, etym=w.etym[:-1] + (st,))


def doublet(rng, lex, k: str, new, donor: str, kind: str | None, contact_words: dict, profile, inv, kyr: float,
            intensity: float = 0.0):
    """After `new`, a loan from `donor` (contact kind `kind`), was made to replace `k`'s word: maybe it comes in as a
    doublet instead. Returns (concept stored, how) when it did (the native word of `k` is kept), else None. Also turns
    an elite donor's word for a meat into its word for the animal, narrowed (returns None: an ordinary replacement)."""
    from . import lexicon as LX
    if kind not in DOUBLET_P or k not in lex.words:
        return None
    note = channel(kind)
    kinds = SPLIT_KINDS.get(kind, ())
    ch = [(c, kd) for c, kd in splits().get(k, ()) if kd in kinds and c in lex.words]
    if ch:
        if rng.random() >= DOUBLET_P[kind]:
            return None
        child, kd = ch[int(rng.integers(len(ch)))] if len(ch) > 1 else ch[0]
        dl = contact_words.get(donor)
        if kd == "product" and dl is not None and child in dl.words:
            w = LX.borrow(dl.words[child], donor, lex, profile, inv, kyr, f"{note}; doublet beside the native word for "
                          f"'{LX.concept_info(k).gloss}'", store=False, rng=rng, intensity=intensity)
        else:
            w = _narrowed(new, child, k, f"{note}; doublet")
        if w.form == lex.words[k].form:
            return None
        lex.set(w)
        return child, "split"
    if k in splits() or k in split_parents() or k.startswith("meat:"):
        return None
    c = LX.concept_info(k)
    if (kind in REGISTER_P and c.freq_class >= REGISTER_MIN_FREQ and c.pos in ("N", "V", "A") and register_field(k)
            and rng.random() < REGISTER_P[kind]):
        if new.form == lex.words[k].form:
            return None
        st = new.etym[-1]
        st = replace(st, note=f"{note}; high register, beside the native word")
        lex.words[HIGH + k] = replace(new, concept=HIGH + k, etym=new.etym[:-1] + (st,))
        return HIGH + k, "register"
    return None


def narrow_meat(rng, lex, k: str, new, donor: str, kind: str | None, contact_words: dict, profile, inv, kyr: float,
                intensity: float = 0.0):
    """A meat word being replaced by a loan from an elite donor: with DOUBLET_P the loan is the donor's word for the
    animal, narrowed to its meat (beef < boef 'ox'), not the donor's own meat word. Returns the Word to use, or None."""
    from . import lexicon as LX
    if kind != "elite" or not k.startswith("meat:"):
        return None
    dl = contact_words.get(donor)
    par = [p for p, kd in split_parents().get(k, ()) if kd == "meat" and dl is not None and p in dl.words]
    if not par or rng.random() >= DOUBLET_P[kind]:
        return None
    p = par[0]
    w = LX.borrow(dl.words[p], donor, lex, profile, inv, kyr, channel(kind), store=False, rng=rng, intensity=intensity)
    if p in lex.words and w.form == lex.words[p].form:
        return None
    return _narrowed(w, k, p, f"{channel(kind)}; doublet")


def high_words(lex) -> list:
    return [k for k in lex.words if k.startswith(HIGH)]


def finish_registers(lex) -> dict:
    """Move the high-register doublets out of the lexicon into `systems.registers.high`: {concept: [ipa, "doublet" |
    "synonym", donor lect, kyr]} ("doublet" when the two words share a root, as the faiths' learned register)."""
    from . import lexicon as LX
    hk = high_words(lex)
    if not hk:
        return {}
    out = {}
    for hkey in sorted(hk):
        w = lex.words.pop(hkey)
        k = hkey[len(HIGH):]
        cur = lex.words.get(k)
        if cur is None or cur.form == w.form:
            continue
        loan = next((s for s in reversed(w.etym) if s.process.startswith("borrow:")), None)
        rel = "doublet" if set(LX.etym_roots(cur)) & set(LX.etym_roots(w)) else "synonym"
        out[k] = [w.ipa, rel, loan.process.split(":", 1)[1] if loan else "", round(float(loan.kyr), 3) if loan else None]
    if out:
        lex.systems.setdefault("registers", {})["high"] = out
    return out
