"""The synchronic rule layer: each lect's live phonological rules (sound lane, 2026-11-08).

Daniel asked (11-07) "do we have phonology and phonological rules?". Before this layer a lect had allophones found by
complementary distribution, phonotactic templates, positional stress, hiatus repair and two joins in sentences, but no
rules of its grammar: a sound change fired once over the stored forms and was gone, so words made later, affixes, loans
and word joins never showed it.

**What a live rule is.** An ordinary `rules.Rule` (the sound-change machinery applies it) held by the lect with a level:

- `phrase`: applies inside words and across word joins in a sentence (postlexical: Spanish la vaca [laˈβaka]);
- `word`: inside a word, its affixes and compounds, not across words;
- `stem`: only where words are made (derivation, compounding, coinage, loans), no longer to inflected forms.

**Where they come from.** (1) A conditioned sound change that fires (own or by wave) starts as a phrase-level rule. (2)
Each allophone of the inventory (`inventory.ALLO_TESTS`) is a phonetic rule (`/p/ -> [b] / V_V`), re-derived whenever
the inventory is (it lives as long as the complementary distribution does). (3) A tonal lect gets one tone-sandhi rule
(Meeussen's rule, Mandarin-type low-tone sandhi, or high-tone spread), drawn once per line. (4) Harmony starts at word
level (harmony is a word-domain process).

**How they age: the life cycle of phonological processes** (Bermúdez-Otero 2007, 2015; Kiparsky's stratal phonology):
a new process is phrasal and phonetic; as it ages its domain narrows (phrase -> word -> stem), and in the end it dies,
leaving lexicalized alternations. Ages: `PHRASE_KYR`, `WORD_KYR`, and a death age drawn per rule (lognormal around
`LIFE_KYR`). A rule also dies when later changes make it opaque (`OPAQUE_MAX` of the forms it could apply to it would
change: the stored words no longer obey it), or when the lect holds more than `MAX_LIVE` (the oldest go).

**Order.** Lexical rules (stem, word) in the order they were born (rule addition at the end of the grammar: Halle 1962;
King 1969), then phrase-level rules, then the allophone rules (phonetic implementation comes last).

**Where they apply.** `inventory.realize` (so `inventory.repair`, hence every coinage, derivation, compound, loan and
name the lexicon or names pass makes) runs the stem, word and phrase rules over the new form; `sentences.render_word`
runs the word-level rules over an affixed word and `sentences.finish` the phrase-level ones across word joins (pairs of
adjacent words, length-preserving rules only). Paradigm cells built by grammar.py are not run through them yet.

Output: lect["phonology"] = {"rules": [{"r": ref, "lv": level, "b": born kyr, "t": notation, "w": plain words,
"ex": [input, output, gloss] | null}], "dead": [[ref, born, died, why]]} for living lects (architecture.md section 11).
"""
from __future__ import annotations

import math
import zlib
from dataclasses import dataclass, replace

import numpy as np

from . import rules as RU
from .percepts import from_ipa, to_ipa, word_ipa

LEVELS = ("phrase", "word", "stem")
PHRASE_KYR = 1.0      # a new rule applies across word joins for about this long ...
WORD_KYR = 3.0        # ... then inside words (affixes, compounds) until this age, then only where words are made
LIFE_KYR = 6.0        # median age at death (lexicalization), lognormal sigma LIFE_SIGMA per rule
LIFE_SIGMA = 0.5
OPAQUE_MAX = 0.2      # a rule dies when it would change more than this share of the frequent forms it could apply to
OPAQUE_SAMPLE = 60     # frequent forms the opacity test looks at
OPAQUE_MIN_HITS = 5   # ... counted only once it could apply to at least this many forms
MAX_LIVE = 8          # live rules a lect keeps (allophone and sandhi rules aside); the oldest die first
DEAD_KEEP = 6         # most recent deaths kept for the page
SANDHI_SHARE = 0.7    # share of tonal lect lines with a tone-sandhi rule (Chen 2000: sandhi is the rule in tone languages
#                       of East and Southeast Asia, Meeussen-type OCP effects common in Bantu; not universal)
_SKIP_PREFIX = ("simplification", "tone.default", "tone.phonemic", "dispersion.", "sandhi:", "allo:")


@dataclass
class Live:
    ref: str            # "c:<rule id>" a sound change | "a:<allophone>|<phoneme>|<test>" | "s:<sandhi kind>"
    rule: object        # rules.Rule
    born: float         # kyr ago it began
    level: str = "phrase"
    life: float = LIFE_KYR
    checked: int = -1   # the whole kyr of age at which opacity was last checked (checked once per kyr of age)

    def age(self, kyr: float) -> float:
        return self.born - kyr


# ---------------------------------------------------------------------------------------------- which changes become rules

def _conditioned(rule) -> bool:
    env = rule.env
    return bool(env.stress or env.syll or any(l or r for l, r in env.alts))


def eligible(rule) -> bool:
    """A sound change that can live on as a rule: conditioned (a context-free change leaves no alternation), one step
    (staged rows aside), not a driver's bookkeeping (folds, tone hygiene, dispersion pushes)."""
    if rule is None or rule.then or rule.id.startswith(_SKIP_PREFIX):
        return False
    if rule.change.kind in ("metathesis", "rewrite"):
        return False   # (cluster rewrites and metathesis are lexical, word-by-word in the record: not productive rules)
    return _conditioned(rule)


def _life(lect_id: str, ref: str) -> float:
    z = float(np.random.default_rng(zlib.crc32(f"{lect_id}|{ref}".encode("utf-8"))).normal())
    return LIFE_KYR * math.exp(LIFE_SIGMA * z)


def on_change(lect, rule, kyr: float) -> None:
    """A sound change fired in `lect`: it becomes (or renews) a live rule, phrase level (harmony: word level)."""
    if not eligible(rule):
        return
    live = list(getattr(lect, "live", None) or [])
    ref = "c:" + rule.id
    live = [x for x in live if x.ref != ref]
    level = "word" if rule.family == "harmony" else "phrase"
    live.append(Live(ref, rule, float(kyr), level, _life(lect.id, ref)))
    lect.live = live


# ---------------------------------------------------------------------------------------------- allophones as rules

_ALLO_ENV = {
    "nasal_place": None,                # built per place below
    "palatal": "_[V back=0..1], _j",
    "intervocalic": "V_V",
    "final": "_#",
    "initial": "#_",
    "nasal_vowel": "_N",
    "coda": "_C, _#",
}
_ALLO_CACHE: dict = {}


def allophone_rule(x, p, test):
    """The rule behind one allophone: p -> x in the test's environment (a glottal onset: ∅ -> ʔ before a vowel at the start
    of a word or between vowels). None when the notation does not parse."""
    key = (x, p, test)
    if key in _ALLO_CACHE:
        return _ALLO_CACHE[key]
    if p is None:
        note = f"∅ > {to_ipa(x)} / #_V, V_V"
    elif test == "nasal_place":
        note = f"{to_ipa(p)} > {to_ipa(x)} / _[C place={x.place}]"
    elif test in _ALLO_ENV:
        note = f"{to_ipa(p)} > {to_ipa(x)} / {_ALLO_ENV[test]}"
    else:
        _ALLO_CACHE[key] = None
        return None
    ref = f"a:{to_ipa(x)}|{to_ipa(p) if p is not None else ''}|{test}"
    r, _why = RU.parse_rule({"id": ref, "rule": note, "cause": "coarticulation", "family": "allophone"})
    _ALLO_CACHE[key] = r
    return r


def allophone_rules(inv) -> list:
    out = []
    for x, (p, test) in sorted((getattr(inv, "allophones", None) or {}).items(), key=lambda kv: (to_ipa(kv[0]), kv[1][1])):
        r = allophone_rule(x, p, test)
        if r is not None:
            out.append(Live(r.id, r, 0.0, "phrase", math.inf))
    return out


# ---------------------------------------------------------------------------------------------- tone sandhi

# kind -> (notation, needs tones, weight, plain words, source)
SANDHI = {
    "meeussen": ("V˦ > V˨ / V˦C*_", (3, 1), 3.0, "a high tone after a high tone becomes low (Meeussen's rule)",
                 "Bantu: Shona, Kirundi (Meeussen 1963; Goldsmith 1984)"),
    "low_low": ("V˨ > V˨˦ / _C*V˨", (1, 4), 2.0, "a low tone before a low tone becomes rising",
                "Mandarin third-tone sandhi: hěn hǎo > hén hǎo (Chen 2000)"),
    "low_low_h": ("V˨ > V˦ / _C*V˨", (1, 3), 1.0, "a low tone before a low tone becomes high",
                  "Mandarin-type third-tone sandhi where the lect has no rising tone (Chen 2000)"),
    "high_spread": ("V˨ > V˦ / V˦C*_", (3, 1), 2.0, "a high tone spreads onto a following low syllable",
                    "Bantu high-tone spread: Chichewa, Zulu (Hyman 2007)"),
    "contour_level": ("V˦˨ > V˦ / _C*V", (5, 3), 1.5, "a falling tone before another syllable keeps only its high part",
                      "contour simplification in phrase-medial position: Min and Wu sandhi (Chen 2000)"),
}
_SANDHI_RULES: dict = {}


def sandhi_rule(kind: str):
    if kind not in _SANDHI_RULES:
        note, _t, w, words, src = SANDHI[kind]
        r, _why = RU.parse_rule({"id": "sandhi:" + kind, "rule": note, "cause": "prosody", "family": "tone",
                                 "articulators_or_axes_needed": "pitch_ear", "naturalness": str(w), "example": src})
        _SANDHI_RULES[kind] = r
    return _SANDHI_RULES[kind]


def draw_sandhi(lect, kyr: float) -> None:
    """A tonal lect line without a sandhi rule draws one, once (seeded by the line), among the kinds its tones allow."""
    tones = set(getattr(lect.inventory, "tones", None) or ())
    live = list(getattr(lect, "live", None) or [])
    if len(tones) < 2 or any(x.ref.startswith("s:") for x in live) or getattr(lect, "sandhi_drawn", False):
        return
    lect.sandhi_drawn = True
    rng = np.random.default_rng(zlib.crc32(f"sandhi|{lect.hiatus_key or lect.id}".encode("utf-8")))
    if rng.random() >= SANDHI_SHARE:
        return
    kinds = [k for k, v in SANDHI.items() if set(v[1]) <= tones]
    if not kinds:
        return
    w = np.array([SANDHI[k][2] for k in kinds])
    k = kinds[int(rng.choice(len(kinds), p=w / w.sum()))]
    r = sandhi_rule(k)
    if r is None:
        return
    live.append(Live("s:" + k, r, float(kyr), "phrase", math.inf))
    lect.live = live


# ---------------------------------------------------------------------------------------------- ageing and death

def _opaque(rule, forms, stress) -> bool:
    hits = changed = 0
    for f in forms:
        if rule.target is not None and not any(rule.target(x) for x in f):
            continue
        hits += 1
        if RU.apply(rule, f, stress) != f:
            changed += 1
    return hits >= OPAQUE_MIN_HITS and changed > OPAQUE_MAX * hits


def update(lect, kyr: float) -> None:
    """Age the lect's live rules at `kyr`: narrow each one's level by age, retire the dead (too old, opaque, or past
    MAX_LIVE), draw tone sandhi for a tonal line, and hand the active list to the inventory (inventory.realize)."""
    live = list(getattr(lect, "live", None) or [])
    dead = list(getattr(lect, "dead_rules", None) or [])
    stress = getattr(lect.inventory, "stress", None)
    forms = lect.load_forms()[:OPAQUE_SAMPLE] if lect.lexicon is not None else []
    keep = []
    for x in live:
        why = None
        a = x.age(kyr)
        if x.ref.startswith("s:"):
            if len(set(getattr(lect.inventory, "tones", None) or ())) < 2:
                why = "the lect lost its tones"
        elif a > x.life:
            why = "old: its alternations are now learned word by word"
        elif int(a) != x.checked and _opaque(x.rule, forms, stress):
            why = "opaque: later changes left words that break it"
        if why:
            dead.append([x.ref, round(x.born, 3), round(float(kyr), 3), why])
            continue
        x = replace(x, checked=int(a))
        if not x.ref.startswith("s:") and x.rule.family != "harmony":
            x = replace(x, level="phrase" if a < PHRASE_KYR else "word" if a < WORD_KYR else "stem")
        keep.append(x)
    changes = [x for x in keep if x.ref.startswith("c:")]
    if len(changes) > MAX_LIVE:
        changes.sort(key=lambda x: -x.born)
        for x in changes[MAX_LIVE:]:
            dead.append([x.ref, round(x.born, 3), round(float(kyr), 3), "crowded out by younger rules"])
        old = {id(x) for x in changes[MAX_LIVE:]}
        keep = [x for x in keep if id(x) not in old]
    lect.live = keep
    lect.dead_rules = dead[-DEAD_KEEP:]
    draw_sandhi(lect, kyr)
    attach(lect)


def ordered(live: list, inv=None) -> list:
    """Application order: lexical rules (stem, word) oldest first, then phrase-level rules oldest first, then the allophone
    rules of `inv`."""
    lex = sorted((x for x in live if x.level in ("stem", "word")), key=lambda x: (-x.born, x.ref))
    post = sorted((x for x in live if x.level == "phrase"), key=lambda x: (-x.born, x.ref))
    return lex + post + (allophone_rules(inv) if inv is not None else [])


def attach(lect) -> None:
    """Put the active rules on the inventory (Inventory.live: ((rule, level), ...)) for inventory.realize."""
    inv = lect.inventory
    if inv is None or not hasattr(inv, "live"):
        return
    inv.live = tuple((x.rule, x.level) for x in ordered(list(getattr(lect, "live", None) or [])))


# ---------------------------------------------------------------------------------------------- applying

def _rule_of(x):
    return x[0] if isinstance(x, tuple) else getattr(x, "rule", x)


def apply_word(form: tuple, rules, stress=None, inventory=None, stem_index=None) -> tuple:
    """Run rules ((rule, level) pairs or Live) over one form, in order."""
    from .inventory import fuse_vowels
    f = tuple(form)
    for x in rules:
        r = _rule_of(x)
        try:
            g = RU.apply(r, f, stress, stem_index=stem_index, inventory=inventory)
        except Exception:  # noqa: BLE001 - a rule that cannot run on this form is skipped
            continue
        if g:
            f = fuse_vowels(tuple(g))
    return f


def apply_phrase(forms: list, rules, stress=None) -> list:
    """Run phrase-level rules across each join of adjacent words: the pair is run as one string and split again where it
    was joined; a rule that would change the pair's length (an insertion, a deletion) is not run across the join."""
    out = [tuple(f) for f in forms]
    for i in range(len(out) - 1):
        a, b = out[i], out[i + 1]
        if not a or not b:
            continue
        for x in rules:
            r = _rule_of(x)
            pair = a + b
            try:
                g = RU.apply(r, pair, _pair_stress(a, b, stress))
            except Exception:  # noqa: BLE001
                continue
            if len(g) != len(pair) or g == pair:
                continue
            a, b = tuple(g[:len(a)]), tuple(g[len(a):])
        out[i], out[i + 1] = a, b
    return out


def _pair_stress(a, b, stress):
    """Stress over a joined pair: each word keeps its own stressed vowel (the first word's, for a rule's focus test)."""
    if not stress or stress == "none":
        return None
    sa = RU.stressed_vowel(a, stress)
    return (lambda w, s=sa: s)


# ---------------------------------------------------------------------------------------------- notation and examples

def _env_text(rule) -> str:
    n = (rule.notation or "").split("  [")[0]
    return n.split(" / ", 1)[1].strip() if " / " in n else ""


def notation(rule, segs, allophone: bool = False) -> str:
    """Plain notation over the lect's own sounds: '/t/ → [ɾ] / V_V' for an allophone, 't → ɾ, d → ð / V_V' for a rule
    (the input sounds the lect has that the rule rewrites, context aside)."""
    env = _env_text(rule)
    pairs = []
    if rule.target is None:
        lit = rule.change.items[0][1] if rule.change.items else None
        pairs.append(("∅", to_ipa(lit) if lit is not None else "?"))
    else:
        segs = {replace(s, tone=0) if s.kind == "V" and s.tone else s for s in segs}   # (tone aside: one row per sound)
        for s in sorted(segs, key=to_ipa):
            if not rule.target(s):
                continue
            o = RU._single(rule, s)
            if o is None or tuple(o) == (s,):
                continue
            pairs.append((to_ipa(s), "".join(to_ipa(y) for y in o) or "∅"))
            if len(pairs) == 4:
                break
    if not pairs:
        main = (rule.notation or rule.id).split("  [")[0].split(" / ")[0].replace(">", "→")
    elif allophone:
        main = ", ".join(f"/{a}/ → [{b}]" for a, b in pairs)
    else:
        main = ", ".join(f"{a} → {b}" for a, b in pairs)
    return f"{main} / {env}" if env else main


def _words_of(lect, n: int = 150) -> list:
    ws = sorted(lect.lexicon.words.values(), key=lambda w: (w.freq_class, w.concept))[:n]
    return [(w.form, w.concept) for w in ws if w.form]


def _at_join(rule, joined: tuple, k: int, stress, stem_index=None) -> tuple | None:
    """The rule run over a form joined at segment k, when it changes something within two segments of the join (the
    alternation the join makes); None otherwise. No vowel fusion here, so only the rule's own effect counts."""
    try:
        g = RU.apply(rule, joined, stress, stem_index=stem_index)
    except Exception:  # noqa: BLE001
        return None
    if g == joined:
        return None
    a = next((i for i, (x, y) in enumerate(zip(joined, g)) if x != y), min(len(joined), len(g)))
    b = next((i for i, (x, y) in enumerate(zip(joined[::-1], g[::-1])) if x != y), min(len(joined), len(g)))
    hi = len(joined) - b   # the changed stretch of the input is [a, hi)
    return g if a <= k + 1 and hi >= k - 1 else None


def _obeys(rule, f, stress) -> bool:
    try:
        return RU.apply(rule, f, stress) == f
    except Exception:  # noqa: BLE001
        return False


def example(lect, x: Live, inv) -> list | None:
    """A worked example from the lect's own words: [input, output, gloss]. Phrase level: two frequent words joined;
    word and stem level: a frequent word + one of the lect's affixes (or a second word, a compound); an allophone: a word
    holding it, phonemic form against phonetic. The rule must change something at the join itself."""
    stress = getattr(inv, "stress", None)
    words = _words_of(lect)
    r = x.rule
    if x.ref.startswith("a:"):
        xs, ps = x.ref[2:].split("|")[:2]
        try:
            xx = from_ipa(xs)[0]
            pp = from_ipa(ps)[0] if ps else None
        except Exception:  # noqa: BLE001
            return None
        for f, c in words:
            if pp is not None and xx in f:
                under = tuple(pp if s == xx else s for s in f)
                return ["/" + word_ipa(under) + "/", "[" + word_ipa(f) + "]", c.lower()]
            if pp is None and f and f[0] == xx:
                return ["/" + word_ipa(f[1:]) + "/", "[" + word_ipa(f) + "]", c.lower()]
        return None
    if x.level == "phrase":
        for f1, c1 in words[:60]:
            for f2, c2 in words[:60]:
                if f1 is f2:
                    continue
                if not (_obeys(r, f1, stress) and _obeys(r, f2, stress)):
                    continue
                g = apply_phrase([f1, f2], [r], stress)
                if g != [f1, f2] and g[0][:-2] == f1[:-2] and g[1][2:] == f2[2:]:
                    return [word_ipa(f1) + " " + word_ipa(f2), word_ipa(g[0]) + " " + word_ipa(g[1]),
                            f"{c1.lower()} {c2.lower()}"]
    affixes = sorted((getattr(lect.lexicon, "affixes", None) or {}).items())
    for f, c in words:
        for m, (af, suffix) in affixes:
            joined = tuple(f) + tuple(af) if suffix else tuple(af) + tuple(f)
            k = len(f) if suffix else len(af)
            if not _obeys(r, f, stress):
                break
            g = _at_join(r, joined, k, stress, stem_index=0 if suffix else len(af))
            if g is not None:
                inp = (word_ipa(f) + " + -" + word_ipa(af)) if suffix else (word_ipa(af) + "- + " + word_ipa(f))
                return [inp, word_ipa(g), f"{c.lower()}-{m}" if suffix else f"{m}-{c.lower()}"]
    for f1, c1 in words[:40]:
        for f2, c2 in words[:40]:
            if f1 is f2:
                continue
            if not (_obeys(r, f1, stress) and _obeys(r, f2, stress)):
                continue
            joined = tuple(f1) + tuple(f2)
            g = _at_join(r, joined, len(f1), stress)
            if g is not None:
                return [word_ipa(f1) + " + " + word_ipa(f2), word_ipa(g), f"{c1.lower()} + {c2.lower()} (compound)"]
    return None


def to_json(lect) -> dict:
    """The lect's phonology for the output: its rules in order (with notation over its own sounds, plain words and a
    worked example) and its latest dead rules."""
    inv = lect.inventory
    segs = [s for s in lect.segments()] if lect.lexicon is not None else []
    rows = []
    for x in ordered(list(getattr(lect, "live", None) or []), inv):
        allo = x.ref.startswith("a:")
        level = "phonetic" if allo else x.level
        words = SANDHI[x.ref[2:]][3] if x.ref.startswith("s:") else RU.describe(x.rule)
        text = SANDHI[x.ref[2:]][0].replace(">", "→") if x.ref.startswith("s:") else notation(x.rule, segs, allo)
        rows.append({"r": x.ref, "lv": level, "b": None if allo else round(x.born, 3), "t": text,
                     "w": words, "ex": example(lect, x, inv)})
    return {"rules": rows, "dead": list(getattr(lect, "dead_rules", None) or [])}


# ---------------------------------------------------------------------------------------------- from the output (sentences)

_INDEX: dict = {}


def rule_by_id(rid: str):
    """A catalogue rule (demo or table) by id; a lect variant (`S123/i`) by its base id."""
    if not _INDEX:
        for r in list(RU.DEMO_RULES) + list(RU._tsv_cached(str(RU.DATA))[0]):
            _INDEX.setdefault(r.id, r)
    return _INDEX.get(rid) or _INDEX.get(rid.split("/", 1)[0])


def rules_from_json(ph: dict | None, inv_json: dict | None = None) -> list:
    """[(rule, level)] in order from a lect's "phonology" record (allophone rules rebuilt from their refs)."""
    out = []
    for row in (ph or {}).get("rules") or []:
        ref, lv = row.get("r", ""), row.get("lv", "phrase")
        r = None
        if ref.startswith("c:"):
            r = rule_by_id(ref[2:])
        elif ref.startswith("s:") and ref[2:] in SANDHI:
            r = sandhi_rule(ref[2:])
        elif ref.startswith("a:"):
            xs, ps, test = (ref[2:].split("|") + ["", "", ""])[:3]
            try:
                xx = from_ipa(xs)[0]
                pp = from_ipa(ps)[0] if ps else None
            except Exception:  # noqa: BLE001
                continue
            r = allophone_rule(xx, pp, test)
        if r is not None:
            out.append((r, lv))
    return out
