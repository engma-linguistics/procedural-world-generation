"""A lect: one speech variety, spoken by one deme at a time (PW-986, architecture section 8).

A lect holds an inventory, a lexicon (lexicon.py), a grammar (grammar.py), its rule history and a rate. `step` advances it by
a batch of generations (one frame interval): k rule events ~ Poisson(n x RATE_RULE x RATE_SCALE x rate) through
rules.pick_rule (weighted, vetoed by functional load) applied to every stored form (lexicon words, affixes, grams, paradigm
forms), then the lexical events (lexicon.step) and the grammar events (grammar.step, typology drift). Rates are per
generation with exponent 1 (Daniel, 2026-11-03): a people with 430-year generations changes 15x slower per year than humans.

The other modules are reached through the small adapters at the top so a signature change touches one place."""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

import numpy as np

from . import lexicon as LX
from . import rules as RU

RATE_RULE = 0.1  # sound-change events per generation at rate 1 (calibrated by the horizon check; see calibration.md)
RATE_SIGMA = 0.3  # lognormal sigma of a proto lect's rate
RATE_REDRAW = 0.1  # lognormal sigma of the re-draw at budding
INV_CAP_RATIO = 1.5  # consonants may grow to 1.5x the proto-language's count ...
INV_CAP_V = 20  # vowel qualities (length and nasality count, tone does not), as PHOIBLE counts them
INV_CAP_C = 45  # ... and never past 45 (PHOIBLE's 99th percentile is ~50); beyond, the rarest new ones fold (dispersion)
NEW_SEG_WEIGHT = 0.3  # a rule that would add a segment the lect lacks is drawn this much less often (phonemicization is rare)
LOAD_SAMPLE = 120  # forms handed to rules.pick_rule for the functional-load estimate (the most frequent words first)


# ---------------------------------------------------------------------------------------------- adapters to A, C, D
def _inv_mod():
    from . import inventory as INV
    return INV


def _gr_mod():
    try:
        from . import grammar as GR
        return GR
    except ImportError:
        return None


def inventory_segments(inv) -> list:
    INV = _inv_mod()
    return list(INV.segments(inv))


def draw_inventory(rng, profile):
    return _inv_mod().draw_inventory(rng, profile)


def stress_of(inv):
    return getattr(inv, "stress", None) or RU.DEFAULT_STRESS


_CATALOGUES: dict = {}


def catalogue_for(profile, key: str) -> list:
    if key not in _CATALOGUES:
        _CATALOGUES[key] = RU.catalogue(profile)
    return _CATALOGUES[key]


def filtered_apply(rule, stress, segments):
    """rules.apply for one rule, skipping (unchanged) every form that holds none of the rule's target segments among
    `segments` (an insertion, target None, runs on every form)."""
    tgt = None if rule.target is None else frozenset(x for x in segments if rule.target(x))

    def fn(f, stem_index=0):
        if tgt is not None and tgt.isdisjoint(f):
            return f
        return normalize(RU.apply(rule, f, stress, stem_index=stem_index))
    return fn


def normalize(f: tuple) -> tuple:
    """Driver-side phonetic tidy of a rule's output: a voiceless consonant left with breathy phonation (a devoiced bʱ, a
    breathy-voiced p) is an aspirated one (kʱ{voice=0} > kʰ), as in the Indic and Greek devoicings."""
    if not any(x.kind == "C" and x.phonation == 1 and not x.voice for x in f):
        return f
    return tuple(replace(x, phonation=0, larynx=1) if x.kind == "C" and x.phonation == 1 and not x.voice else x for x in f)


# ---------------------------------------------------------------------------------------------- word access (families)
FORMATION_SKIP = ("sound_change", "borrow", "substrate", "nativize", "analogy")


def word_form(lect, concept: str):
    w = lect.lexicon.get(concept) if lect.lexicon is not None else None
    return w.form if w is not None else None


def word_root(lect, concept: str):
    """The etymology root of a lect's word for a concept: its last word-formation step (proto, coin, derive, compound, shift,
    taboo, elaborate) as (kyr, lect, process, gloss). Inherited words share it with their sisters; loans share it with their
    donors; independent coinages differ."""
    w = lect.lexicon.get(concept) if lect.lexicon is not None else None
    if w is None:
        return None
    for s in reversed(w.etym):
        if not s.process.split(":", 1)[0] in FORMATION_SKIP:
            return (s.kyr, s.lect, s.process, s.gloss)
    return (w.etym[0].kyr, w.etym[0].lect, w.etym[0].process, w.etym[0].gloss) if w.etym else None


# ---------------------------------------------------------------------------------------------- the lect
@dataclass
class Lect:
    id: str
    deme: int | None
    people: str
    parent: str | None
    how: str  # proto | bud | shift | arrival
    born_kyr: float
    rate: float = 1.0
    substrate: str | None = None
    died_kyr: float | None = None
    end: str | None = None  # bud parents keep living; extinct | fused | shifted
    inventory: object = None
    lexicon: object = None
    grammar: object = None
    profile: object = None
    profile_key: str = "human"
    gen_yr: float = 25.0
    changes: list = field(default_factory=list)  # {kyr, rule, cause, origin_lect}
    shares: dict = field(default_factory=dict)  # lect id -> share of this deme speaking it (bilingual years)
    shares_history: list = field(default_factory=list)  # [kyr, {lect: share}]
    snapshots: list = field(default_factory=list)  # [kyr, snapshot dict] per frame alive (history.snapshot)
    l2: float = 0.0
    population: float = 0.0
    isolation: float = 0.0
    deme_name: str | None = None
    language: str | None = None
    family_true: str | None = None
    family_scholars: str | None = None
    rules_applied: int = 0
    generations: float = 0.0
    base_segs: frozenset = frozenset()  # the proto-language's consonants (inventory cap; carried by daughters)
    rule_text: dict = field(default_factory=dict)  # rules.describe of rules made on the fly (dispersion pushes), for the json

    def copy(self, new_id: str, deme: int | None, kyr: float, how: str, rng=None) -> "Lect":
        """A daughter lect: same inventory, a copied lexicon and grammar, the rate re-drawn a little (budding)."""
        rate = self.rate
        if rng is not None and how == "bud":
            rate = float(self.rate * math.exp(rng.normal(0.0, RATE_REDRAW)))
        GR = _gr_mod()
        gram = None
        if self.grammar is not None:
            gram = GR.copy(self.grammar) if GR is not None and hasattr(GR, "copy") else _deepcopy(self.grammar)
        return Lect(id=new_id, deme=deme, people=self.people, parent=self.id, how=how, born_kyr=float(kyr), rate=rate,
                    inventory=_copy_inv(self.inventory), lexicon=self.lexicon.copy(new_id) if self.lexicon is not None else None,
                    grammar=gram, profile=self.profile, profile_key=self.profile_key, gen_yr=self.gen_yr,
                    base_segs=self.base_segs or self.consonants())

    def consonants(self) -> frozenset:
        """The proto-like base for the inventory cap: the consonants, and the vowel qualities (tone set aside)."""
        if self.lexicon is None:
            return frozenset()
        return frozenset(_unit(x) for x in self.segments() if x.kind in ("C", "V"))

    def weighted_rules(self, rules) -> list:
        """The catalogue with rules that would add a segment the lect lacks down-weighted by NEW_SEG_WEIGHT (cached per
        segment set)."""
        segs = frozenset(self.segments())
        hit = getattr(self, "_rw", None)
        if hit is not None and hit[0] is rules and hit[1] == segs:
            return hit[2]
        out = []
        for r in rules:
            new = False
            for x in segs:
                o = RU._single(r, x)
                if o and any(y not in segs for y in o):
                    new = True
                    break
            out.append(replace(r, weight=r.weight * NEW_SEG_WEIGHT) if new else r)
        self._rw = (rules, segs, out)
        return out

    def cap_inventory(self, kyr: float) -> int:
        """Keep inventories PHOIBLE-sized: past min(INV_CAP_RATIO x the proto count, INV_CAP_C consonants / INV_CAP_V
        vowels; vowels counted by quality with length and nasality, tone set aside), the rarest units the proto lacked
        (else the rarest) fold into their nearest remaining unit, consistently over the lexicon and grammar; logged as
        one `simplification:` change with cause "dispersion". Returns units folded."""
        from .percepts import distance, to_ipa
        segs = self.all_segments()
        mapping = {}
        for kind, absmax in (("C", INV_CAP_C), ("V", INV_CAP_V)):
            units = sorted({_unit(x) for x in segs if x.kind == kind}, key=to_ipa)
            base = sum(1 for u in self.base_segs if u.kind == kind) or len(units)
            cap = int(min(absmax, max(INV_CAP_RATIO * base, base + 2)))
            if len(units) <= cap:
                continue
            cnt = dict.fromkeys(units, 0)
            for w in self.lexicon.words.values():
                for x in w.form:
                    u = _unit(x)
                    if u in cnt:
                        cnt[u] += 1
            keep = set(units)
            um = {}
            while len(keep) > cap:
                pool = [x for x in keep if x not in self.base_segs] or list(keep)
                x = min(pool, key=lambda q: (cnt[q], to_ipa(q)))
                keep.discard(x)
                um[x] = min(keep, key=lambda q: (distance(x, q), -cnt[q], to_ipa(q)))
            for x in um:  # (a fold into a unit folded later follows it on)
                y = um[x]
                while y in um:
                    y = um[y]
                um[x] = y
            for x in segs:
                u = _unit(x)
                if u in um:
                    mapping[x] = replace(um[u], tone=x.tone) if x.kind == "V" else um[u]
        if not mapping:
            return 0

        def fn(f, stem_index=0, m=mapping):
            return tuple(m.get(y, y) for y in f)
        what = ", ".join(sorted({f"{to_ipa(_unit(a))} > {to_ipa(_unit(b))}" for a, b in mapping.items()}))
        rid = "simplification"
        self.touch()
        LX.apply_rule_to_lexicon(self.lexicon, fn, "simplification", kyr, self.id)
        GR = _gr_mod()
        if GR is not None and self.grammar is not None:
            GR.apply_rule_to_grammar(self.grammar, fn, "simplification", kyr)
        self.changes.append({"kyr": round(float(kyr), 3), "rule": rid, "cause": "dispersion", "origin_lect": None, "merged": what})
        self._dirty = True
        return len(mapping)

    @property
    def alive(self) -> bool:
        return self.died_kyr is None

    def segments(self) -> list:
        """The segments in use: every segment of every word (the inventory as it now stands after sound change); cached until
        the forms change (touch())."""
        segs = getattr(self, "_segs", None)
        if segs is None:
            seen = {}
            for w in self.lexicon.words.values():
                for s in w.form:
                    seen[s] = True
            segs = self._segs = list(seen)
        return segs

    def all_segments(self) -> list:
        """Segments of the words and of the grammar's forms (grams, paradigm cells): what a rule may touch."""
        segs = set(self.segments())
        if self.grammar is not None:
            for gr in getattr(self.grammar, "grams", ()):
                segs.update(gr.form)
            for ex in getattr(self.grammar, "exemplars", ()):
                segs.update(ex.stem)
                for f in ex.cells.values():
                    segs.update(f)
            for _c, f in getattr(self.grammar, "helpers", {}).values():
                segs.update(f)
        for f, _s in getattr(self.lexicon, "affixes", {}).values():
            segs.update(f)
        return list(segs)

    def touch(self) -> None:
        self._segs = None

    def all_forms(self) -> list:
        return [w.form for w in self.lexicon.words.values()]

    def load_forms(self) -> list:
        """The forms the functional-load veto looks at: the LOAD_SAMPLE most frequent words (frequency class, then concept),
        a fixed sample so the estimate costs the same for every lect."""
        ws = sorted(self.lexicon.words.values(), key=lambda w: (w.freq_class, w.concept))[:LOAD_SAMPLE]
        return [w.form for w in ws]

    def sync(self) -> None:
        """Bring the inventory in line with the forms after this interval's sound changes."""
        if getattr(self, "_dirty", False):
            _sync_inventory(self)
            self._dirty = False

    def apply_rule(self, rule, kyr: float, origin: str | None = None) -> int:
        """Run one sound change over every stored form; record it. Returns words changed."""
        stress = stress_of(self.inventory)
        fn = filtered_apply(rule, stress, self.all_segments())
        self.touch()
        n = LX.apply_rule_to_lexicon(self.lexicon, fn, rule.id, kyr, self.id)
        GR = _gr_mod()
        if GR is not None and self.grammar is not None:
            g = GR.apply_rule_to_grammar(self.grammar, fn, rule.id, kyr)
            n += g if isinstance(g, int) else len(g or ())
        self.changes.append({"kyr": round(float(kyr), 3), "rule": rule.id, "cause": rule.cause, "origin_lect": origin})
        if rule.id.startswith("dispersion.") and rule.id not in self.rule_text:
            self.rule_text[rule.id] = RU.describe(rule)
        self.rules_applied += 1
        self._dirty = True
        return n

    def step(self, rng, n_generations: float, kyr: float, ctx: dict) -> list:
        """Advance by n generations in one batch (one frame interval). ctx: contact_words {lect id: Lexicon}, niche, l2,
        population, isolation, rate_scale, replace_scale. Returns the rules that fired (for the wave)."""
        self.l2 = float(ctx.get("l2", self.l2))
        self.population = float(ctx.get("population", self.population))
        self.isolation = float(ctx.get("isolation", self.isolation))
        self.generations += n_generations
        fired = []
        lam = n_generations * RATE_RULE * ctx.get("rate_scale", 1.0) * self.rate
        k = int(rng.poisson(lam)) if lam > 0 else 0
        if k:
            rules = catalogue_for(self.profile, self.profile_key)
            for _ in range(k):
                r = RU.pick_rule(rng, self.weighted_rules(rules), self.load_forms(), self.segments(), stress_of(self.inventory))
                if r is None:
                    continue
                if self.apply_rule(r, kyr) > 0:
                    fired.append(r)
                else:  # (a rule that changed nothing is not a change; drop the record)
                    self.changes.pop()
                    self.rules_applied -= 1
        self.cap_inventory(kyr)  # (also catches segments brought by wave adoptions applied before this step)
        self.sync()
        self.touch()
        rs = ctx.get("replace_scale", 1.0)
        LX.step(rng, self.lexicon, n_generations * rs, self.inventory, contact_words=ctx.get("contact_words"), kyr=kyr,
                lect_id=self.id, niche_weights=ctx.get("niche"), profile=self.profile,
                head_first=getattr(self.lexicon, "head_first", None))
        GR = _gr_mod()
        if GR is not None and self.grammar is not None:
            gctx = {"l2": self.l2, "population": self.population, "isolation": self.isolation, "kyr": kyr, "lect": self.id,
                    "lexicon": self.lexicon, "inventory": self.inventory}
            grammar_step(GR, rng, self, n_generations, gctx)
        return fired

    def record_shares(self, kyr: float) -> None:
        if self.shares:
            self.shares_history.append([round(float(kyr), 3), {k: round(v, 3) for k, v in self.shares.items() if v > 0.005}])


def _unit(x):
    """What the inventory cap counts: a consonant, or a vowel with its tone set aside."""
    return replace(x, tone=0) if x.kind == "V" and x.tone else x


def grammar_step(GR, rng, lect: Lect, n: float, gctx: dict) -> None:
    """grammar.step (it runs the typology drift too)."""
    GR.step(rng, lect.grammar, n, inv=lect.inventory, lexicon=lect.lexicon, l2_share=gctx["l2"],
            population=gctx["population"], isolation=gctx["isolation"], kyr=gctx["kyr"])


def _accepted(fn, kw: dict) -> dict:
    import inspect
    try:
        ps = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return {}
    if any(p.kind == p.VAR_KEYWORD for p in ps.values()):
        return kw
    return {k: v for k, v in kw.items() if k in ps}


def _deepcopy(x):
    import copy
    return copy.deepcopy(x)


def _copy_inv(inv):
    if inv is None:
        return None
    try:
        from dataclasses import replace
        return replace(inv)
    except TypeError:
        return _deepcopy(inv)


def _sync_inventory(lect: Lect) -> None:
    """Keep the inventory's segment lists in step with the forms after a sound change (so new words use today's sounds)."""
    lect.inventory = _inv_mod().observed(lect.inventory, lect.all_forms(), lect.profile)
