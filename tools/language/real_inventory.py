"""Experiment harness (not a model change): seed human protos with a real language's inventory, or with as much of its
toolkit as the engine can take, and see how much of that language comes out (owner's question, 2026-11-10: "give the
proto the phonemic inventory of a real language, 10x, and see what pops out ... it might show weird gaps").

    uv run python -I tools/language/real_inventory.py --seeds 10 --kyr 2.5 --workers 8 \\
        --json /scratch/realinv/real-inventories.json --html /scratch/realinv/real-inventories.html [--extra-html F]
    uv run python -I tools/language/real_inventory.py --extract data/language/raw/phoible/phoible.csv   # rebuild the TSV
    uv run python -I tools/language/real_inventory.py --check            # the standing check (PW-1641), ~50 s at 8 workers
    uv run python -I tools/language/real_inventory.py --check --record "LABEL"   # store a new baseline (say why in LABEL)

Tiers, per language and seed (seeds 1..N):
- `inv`: a proto made exactly as history.History.make_proto makes one (inventory draw, proto lexicon, proto grammar,
  numerals, book-spelling style), except that after the normal inventory draw its consonants, vowels and tones are
  swapped for the real language's (`fixed_inventory`). Syllable templates, onset/coda limits, coda class, stress and
  grammar are drawn as normal.
- `full`: the inventory plus the rest of the toolkit the engine can hold (FULL): syllable-template weights read off the
  real word list, onset/coda limits (capped at the engine's 2), coda class, onsets required, stress, the typology
  features (word order, adpositions, case, gender/classes, agreement, articles, TAM...; the rest drawn conditional on
  them, as grammar.draw_typology does), and the root length (`length_patch`).
- `control`: a normal proto.
The inventory draw consumes the same random numbers in every tier, so seed k's drawn phonotactics are shared by the
`inv` row and the control. Each proto then buds one daughter that changes for `--kyr` thousand years under the normal
engine (lect.Lect.step in 0.5 kyr steps, the pass's RATE_SCALE, REPLACE_SCALE and RULE_WEIGHT; no contact, no waves, no
shifts). The engine's code is used unchanged; the one thing with no hook, lexicon.length_scale, is swapped for the
duration of a `full` task inside the harness process only.

Measures: tools/language/find.py's lect features and its distance to the language's reference profile (plus the rank of
that profile among all 16), word statistics (find.word_stats plus closed-syllable share, onset and coda cluster shares,
segment-token shares) over the concepts the reference word list shares with the lexicon, and for `full` the share of
the set typology features the grammar still shows. The real column reads the same word statistics off the reference
word list (tools/language/data/reference_words.tsv; English from sketch.ENGLISH_WORDS).

Inventories (one per language, PHOIBLE InventoryID; marginal phonemes left out): LANGS says which and every
normalisation. The rows used are copied to tools/language/data/real_inventories.tsv (CC-BY-SA 3.0, PHOIBLE 2.0).
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import statistics as st
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import find as F  # noqa: E402
import sketch as SK  # noqa: E402

from planet.language import grammar as GRM  # noqa: E402
from planet.language import history as H  # noqa: E402
from planet.language import inventory as INV  # noqa: E402
from planet.language import lect as LC  # noqa: E402
from planet.language import lexicon as LX  # noqa: E402
from planet.language import output as OU  # noqa: E402
from planet.language import profiles as PR  # noqa: E402
from planet.language import romanize as RO  # noqa: E402
from planet.language.percepts import from_ipa, parse_segment, syllabify, to_ipa  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
INV_TSV = DATA / "real_inventories.tsv"
PROTO_KYR = 3.0          # the proto's date (kyr ago); the daughter runs --kyr from it
GEN_YR = 25.0            # human generation length (presets: 25)

#: language -> PHOIBLE inventory, symbol fixes (map: PHOIBLE phoneme -> IPA the engine reads it as), tones kept or not
LANGS = {
    "english": {"label": "English", "id": 2175, "tones": False,
                "map": {"iɪ": "i", "eɪ̯": "e", "oʊ": "o", "ɚː": "ɚ"},
                "note": "PHOIBLE 2175, English (American), Western and Mid-Western US (ph). FLEECE iɪ, FACE eɪ̯, GOAT oʊ "
                        "kept as i e o (the engine has no diphthong phonemes); aɪ aʊ ɔɪ dropped; ɚː read as ɚ."},
    "spanish": {"label": "Spanish", "id": 2210, "tones": False, "add": ["k"],
                "note": "PHOIBLE 2210, Castilian Spanish (ph). The source lists no /k/; it is added (every description "
                        "of Spanish has it). Diphthongs dropped (their vowels are all in the set)."},
    "swahili": {"label": "Swahili", "id": 823, "tones": False,
                "note": "PHOIBLE 823, Swahili (aa). Marginal Arabic-loan x ð ɣ θ left out, as everywhere; prenasalized "
                        "stops mb nd nz ndʒ ŋɡ ɱv kept as single phonemes."},
    "japanese": {"label": "Japanese", "id": 2196, "tones": False, "map": {"d̠": "ɾ"},
                 "note": "PHOIBLE 2196, Japanese, Tokyo (ph). Its d̠ (allophones d̠ ɾ l̠) is read as ɾ, the usual r; the "
                         "moraic nasal is ɴ; no long vowels in this analysis (length is two moras). Pitch accent is "
                         "not lexical tone here."},
    "mandarin": {"label": "Mandarin", "id": 1047, "tones": True,
                 "note": "PHOIBLE 1047, Standard Chinese, Beijing (ph). The four tones ˦ ˦˨ ˧˦ ˧˨˧ are read by the engine "
                         "as high, falling, rising and mid (the dipping tone has no engine shape); diphthongs and "
                         "triphthongs dropped (their vowels are all in the set)."},
    "hawaiian": {"label": "Hawaiian", "id": 43, "tones": False,
                 "note": "PHOIBLE 43, Hawaiian (spa). Its s is as the source lists it."},
    "arabic": {"label": "Arabic", "id": 2157, "tones": False, "map": {"xʀ̥": "χ", "ii̯": "iː", "uu̯": "uː"},
               "note": "PHOIBLE 2157, Arabic (stan1318; Safad, Beirut, Damascus, Kuwait; ph): a spoken Levantine/Gulf "
                       "set, scored against the Modern Standard Arabic profile. xʀ̥ read as χ; ii̯ uu̯ as long iː uː; ai au "
                       "dropped."},
}

#: the full toolkit (tier `full`): coda class, onsets required, stress, typology (present-day values: WALS and the
#: grammars cited in tools/language/data/reference_profiles.tsv). Syllable limits come from the profile, template
#: weights and root length from the reference word list.
FULL = {
    "english": {"coda_class": "any", "onset_required": False, "stress": "initial", "typology": {
        "word_order": "SVO", "adposition": "pre", "genitive": "mixed", "adjective": "AN", "demonstrative": "DemN",
        "numeral": "NumN", "relative": "NRel", "definite_article": "pre", "indefinite_article": "present", "case": "none",
        "alignment": "nom-acc", "number": "sg-pl", "gender": "none", "past": "marked", "future": "marked",
        "progressive": "marked", "negation": "preverbal", "pro_drop": "no", "numeral_classifiers": "no",
        "clusivity": "no", "causative": "periphrastic", "passive": "periphrastic", "copula": "yes",
        "predicative_possession": "have", "numeral_base": "decimal", "wh_in_situ": "no", "verb_agreement": "suffix",
        "object_agreement": "none", "adjective_verb_like": "no", "evidentiality": "none"}},
    "spanish": {"coda_class": "any", "onset_required": False, "stress": "penult", "typology": {
        "word_order": "SVO", "adposition": "pre", "genitive": "NG", "adjective": "NA", "demonstrative": "DemN",
        "numeral": "NumN", "relative": "NRel", "definite_article": "pre", "indefinite_article": "present", "case": "none",
        "alignment": "nom-acc", "number": "sg-pl", "gender": "sex", "past": "marked", "future": "marked",
        "perfective": "marked", "progressive": "marked", "negation": "preverbal", "polar_question": "intonation",
        "pro_drop": "yes", "numeral_classifiers": "no", "clusivity": "no", "causative": "periphrastic",
        "passive": "periphrastic", "copula": "yes", "predicative_possession": "have", "numeral_base": "decimal",
        "wh_in_situ": "no", "verb_agreement": "suffix", "object_agreement": "none", "adjective_verb_like": "no",
        "evidentiality": "none"}},
    "swahili": {"coda_class": "any", "onset_required": False, "stress": "penult", "typology": {
        "word_order": "SVO", "adposition": "pre", "genitive": "NG", "adjective": "NA", "demonstrative": "NDem",
        "numeral": "NNum", "relative": "NRel", "definite_article": "none", "indefinite_article": "none", "case": "none",
        "alignment": "nom-acc", "number": "sg-pl", "gender": "classes", "past": "marked", "future": "marked",
        "perfective": "marked", "negation": "preverbal", "polar_question": "intonation", "pro_drop": "yes",
        "numeral_classifiers": "no", "clusivity": "no", "causative": "bound", "passive": "bound", "copula": "yes",
        "numeral_base": "decimal", "wh_in_situ": "yes", "verb_agreement": "prefix", "object_agreement": "prefix",
        "adjective_verb_like": "no", "evidentiality": "none"}},
    "japanese": {"coda_class": "nasal", "onset_required": False, "stress": "none", "typology": {
        "word_order": "SOV", "adposition": "post", "genitive": "GN", "adjective": "AN", "demonstrative": "DemN",
        "numeral": "mixed", "relative": "RelN", "definite_article": "none", "indefinite_article": "none", "case": "few",
        "alignment": "nom-acc", "number": "none", "gender": "none", "past": "marked", "future": "none",
        "progressive": "marked", "negation": "postverbal", "polar_question": "final_particle", "pro_drop": "yes",
        "numeral_classifiers": "yes", "clusivity": "no", "causative": "bound", "passive": "bound",
        "comparative": "locational", "copula": "yes", "predicative_possession": "locational", "numeral_base": "decimal",
        "wh_in_situ": "yes", "verb_agreement": "none", "object_agreement": "none", "adjective_verb_like": "yes",
        "evidentiality": "none"}},
    "mandarin": {"coda_class": "nasal", "onset_required": False, "stress": "none", "typology": {
        "word_order": "SVO", "adposition": "mixed", "genitive": "GN", "adjective": "AN", "demonstrative": "DemN",
        "numeral": "NumN", "relative": "RelN", "definite_article": "none", "indefinite_article": "none", "case": "none",
        "alignment": "neutral", "number": "none", "gender": "none", "past": "none", "future": "none",
        "perfective": "marked", "progressive": "marked", "negation": "preverbal", "polar_question": "final_particle",
        "pro_drop": "yes", "numeral_classifiers": "yes", "clusivity": "yes", "causative": "periphrastic",
        "passive": "periphrastic", "serial_verbs": "yes", "verb_reduplication": "yes", "copula": "yes",
        "predicative_possession": "have", "numeral_base": "decimal", "wh_in_situ": "yes", "verb_agreement": "none",
        "object_agreement": "none", "adjective_verb_like": "yes", "evidentiality": "none"}},
    "hawaiian": {"coda_class": "any", "onset_required": False, "stress": "penult", "typology": {
        "word_order": "VSO", "adposition": "pre", "genitive": "NG", "adjective": "NA", "demonstrative": "DemN",
        "numeral": "NumN", "relative": "NRel", "definite_article": "pre", "indefinite_article": "present", "case": "none",
        "alignment": "nom-acc", "number": "none", "gender": "none", "past": "marked", "future": "marked",
        "perfective": "marked", "negation": "clause_initial", "polar_question": "intonation", "pro_drop": "no",
        "numeral_classifiers": "no", "clusivity": "yes", "causative": "bound", "passive": "bound", "copula": "no",
        "numeral_base": "decimal", "wh_in_situ": "yes", "verb_agreement": "none", "object_agreement": "none",
        "adjective_verb_like": "yes", "evidentiality": "none"}},
    "arabic": {"coda_class": "any", "onset_required": True, "stress": "weight", "typology": {
        "word_order": "VSO", "adposition": "pre", "genitive": "NG", "adjective": "NA", "demonstrative": "DemN",
        "numeral": "mixed", "relative": "NRel", "definite_article": "pre", "indefinite_article": "present", "case": "few",
        "alignment": "nom-acc", "number": "sg-du-pl", "gender": "sex", "past": "marked", "future": "marked",
        "perfective": "marked", "negation": "preverbal", "polar_question": "initial_particle", "pro_drop": "yes",
        "numeral_classifiers": "no", "clusivity": "no", "causative": "bound", "passive": "bound", "copula": "no",
        "predicative_possession": "locational", "numeral_base": "decimal", "wh_in_situ": "no", "verb_agreement": "both",
        "object_agreement": "suffix", "adjective_verb_like": "no", "evidentiality": "none"}},
}
CONTROL = "control"
TIERS = ("inv", "full", CONTROL)
TIER_LABEL = {"inv": "inventory only", "full": "full toolkit", CONTROL: "control"}
SENTENCE_IDS = ("transitive", "tense", "negation", "possession", "locative", "polar")


# ---- the inventories ---------------------------------------------------------------------------------------------------

def extract(raw_csv: str) -> None:
    """Copy LANGS' inventory rows (phoneme, class, marginal) from PHOIBLE's phoible.csv to INV_TSV."""
    ids = {str(v["id"]) for v in LANGS.values()}
    rows = []
    with open(raw_csv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["InventoryID"] in ids:
                rows.append([r["InventoryID"], r["LanguageName"], r["SpecificDialect"], r["Source"], r["Phoneme"],
                             r["SegmentClass"], r["Marginal"]])
    head = ["# source: https://github.com/phoible/dev (data/phoible.csv); https://phoible.org",
            "# licence: CC-BY-SA 3.0 (PHOIBLE 2.0, Moran & McCloy eds. 2019); this extract shares that licence.",
            "# script: tools/language/real_inventory.py --extract; the inventories tools/language/real_inventory.py LANGS uses.",
            "inventory\tlanguage\tdialect\tsource\tphoneme\tclass\tmarginal"]
    INV_TSV.write_text("\n".join(head + ["\t".join(r) for r in rows]) + "\n", encoding="utf-8")
    print(f"{len(rows)} rows -> {INV_TSV}")


def _inv_rows() -> list[dict]:
    lines = [x for x in INV_TSV.read_text(encoding="utf-8").splitlines() if x and not x.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def fixed_inventory(key: str) -> tuple[list, list, list, list[str]]:
    """(consonants, vowels, tones, notes) of a language's PHOIBLE inventory as engine segments."""
    spec = LANGS[key]
    cons, vows, tones, notes = [], [], [], []
    for r in _inv_rows():
        if r["inventory"] != str(spec["id"]) or r["marginal"] == "TRUE":
            continue
        ph = spec.get("map", {}).get(r["phoneme"], r["phoneme"])
        if ph is None:
            continue
        if r["class"] == "tone":
            if spec["tones"]:
                s = parse_segment(ph)
                if s is not None and s.tone and s.tone not in tones:
                    tones.append(s.tone)
            continue
        s = parse_segment(ph)
        if s is None:   # (a diphthong: not one engine segment)
            notes.append(f"dropped {r['phoneme']}")
            continue
        if s.kind == "V" and "̯" in ph and s.length == 0:
            notes.append(f"dropped glide {r['phoneme']}")
            continue
        (cons if s.kind == "C" else vows).append(s)
    for ph in spec.get("add", []):
        cons.append(parse_segment(ph))
    dedup = lambda xs: list(dict.fromkeys(xs))  # noqa: E731
    return dedup(cons), dedup(vows), sorted(tones), notes


def real_inventory_ipa(key: str) -> dict:
    c, v, t, notes = fixed_inventory(key)
    a = parse_segment("a")
    return {"consonants": [to_ipa(x) for x in c], "vowels": [to_ipa(x) for x in v],
            "tones": [to_ipa(replace(a, tone=x))[1:] for x in t], "dropped": notes}


def shapes_of(ipas: list[str], max_onset: int, max_coda: int) -> dict:
    """Syllable-template weights (the engine's "CV", "CCVC" ... keys) read off a word list, onsets and codas cut to the
    limits."""
    c: Counter = Counter()
    for ipa in ipas:
        segs = [s for s in from_ipa(ipa) if s.kind != "T"]
        for sy in syllabify(segs):
            c["C" * min(len(sy.onset), max_onset) + "V" + "C" * min(len(sy.coda), max_coda)] += 1
    tot = sum(c.values()) or 1
    return {k: round(v / tot, 3) for k, v in c.most_common()}


# ---- protos and daughters ------------------------------------------------------------------------------------------------

class length_patch:
    """Swap lexicon.length_scale (the root-length multiplier; no hook) for a constant while a `full` task runs."""

    def __init__(self, scale: float | None):
        self.scale = scale

    def __enter__(self):
        self.old = LX.length_scale
        if self.scale is not None:
            LX.length_scale = lambda inv, _s=self.scale: _s
        return self

    def __exit__(self, *exc):
        LX.length_scale = self.old


def fixed_typology(rng, fixed: dict, inv) -> GRM.Typology:
    """grammar.draw_typology with some features set: every feature in FEATURES order, the set ones taken as given and
    the rest drawn conditional on them (grammar._draw_feature), then the derived ones."""
    T = GRM.load_tables()
    typ = GRM.Typology()
    for name, _ in GRM.FEATURES:
        typ[name] = fixed[name] if name in fixed else GRM._draw_feature(rng, name, typ, T)
    GRM._derive(typ, inv)
    return typ


def make_proto(seed: int, key: str | None, tier: str, refw: dict | None = None) -> LC.Lect:
    """history.History.make_proto for a human people; tier inv/full put the language's inventory / toolkit in."""
    rng = H.rng_for(seed, "proto", "realinv")
    prof = PR.HUMAN
    inv = LC.draw_inventory(rng, prof)
    if tier in ("inv", "full"):
        cons, vows, tones, _ = fixed_inventory(key)
        pc, pv = INV._pool_for(prof)
        pool_f = {s: f for s, f in pc + pv}
        inv = replace(inv, consonants=cons, vowels=vows, tones=tones,
                      cost={s: INV._cost(prof, s) for s in cons + vows},
                      freq={s: pool_f.get(s, 0.01) for s in cons + vows}, allophones={})
    if tier == "full":
        prof_row = F.load_profiles()[key]
        mo = min(prof_row["max_onset"] or 1, INV.MAX_ONSET)
        mc = min(prof_row["max_coda"] if prof_row["max_coda"] is not None else 1, INV.MAX_CODA)
        fu = FULL[key]
        inv = replace(inv, shapes=shapes_of(list(refw[key].values()), mo, mc), max_onset=mo, max_coda=mc,
                      coda_class=fu["coda_class"] if mc else "any", onset_required=fu["onset_required"],
                      stress=fu["stress"])
    pid = f"p{seed}" if key is None else f"p{seed}{key[:3]}"   # (a line's drift is keyed by its id: one per language)
    lex = LX.proto_lexicon(rng, inv, LX.concepts(None), PROTO_KYR, pid)
    GR = LC._gr_mod()
    if tier == "full":
        typ = fixed_typology(H.rng_for(seed, "typology", "realinv", key), FULL[key]["typology"], inv)
        deep = GR.deep_past_gens(GEN_YR) if hasattr(GR, "deep_past_gens") else 0.0
        gram = GR.proto_grammar(rng, inv, lex, typ=typ, kyr=PROTO_KYR, deep_gens=deep)
    else:
        gram = H.proto_grammar(GR, rng, lex, inv, prof, PROTO_KYR, pid, GEN_YR)
    hf = H.head_first_of(GR, gram)
    if hf is not None:
        lex.head_first = hf
    nb = (getattr(gram, "typology", None) or {}).get("numeral_base")
    if nb is not None:
        from planet.language import lexsys as LS
        sy = lex.systems.get("numeral") or {}
        LS.set_numerals(H.rng_for(seed, "numerals", "realinv"), lex, nb, inv, PROTO_KYR, pid,
                        system=sy if sy.get("label") == nb else None)
    rate = float(math.exp(rng.normal(0.0, LC.RATE_SIGMA)))
    p = LC.Lect(id=pid, deme=None, people="human", parent=None, how="proto", born_kyr=PROTO_KYR, rate=rate, inventory=inv,
                lexicon=lex, grammar=gram, profile=prof, profile_key="human", gen_yr=GEN_YR)
    p.orth = RO.draw_style(seed, pid)
    return p


def evolve(p: LC.Lect, seed: int, kyr: float) -> tuple[LC.Lect, list[int]]:
    """One daughter budded from p, stepped for `kyr` thousand years (0.5 kyr steps, no contact), and the number of sound
    changes that fired in each step."""
    l = p.copy("d" + p.id[1:], 0, PROTO_KYR, "bud", H.rng_for(seed, "bud", "realinv"))
    fired = []
    for i in range(max(1, int(round(kyr / 0.5)))):
        t1 = PROTO_KYR - 0.5 * (i + 1)
        ctx = {"rate_scale": H.RATE_SCALE, "replace_scale": H.REPLACE_SCALE, "rule_weight": H.RULE_WEIGHT,
               "population": 5000.0, "isolation": 0.3, "l2": 0.0}
        f = l.step(H.rng_for(seed, "step", "realinv", i), H.change_generations(500.0, l.gen_yr), t1, ctx)
        l.sync()
        fired.append(len(f))
    return l, fired


# ---- measures ------------------------------------------------------------------------------------------------------------

def _plain(s):
    return replace(s, tone=0, tone2=0) if s.kind == "V" else s


def word_measures(ipas: list[str]) -> dict:
    """find.word_stats plus closed-syllable share, onset/coda cluster shares (per syllable), mean segments per word and
    token shares of the finder's sound classes (find.seg_class)."""
    out = F.word_stats(ipas)
    out.pop("texture", None)
    syl = closed = oc = cc = segs_n = words = 0
    tok: Counter = Counter()
    for ipa in ipas:
        segs = [s for s in from_ipa(ipa) if s.kind != "T"]
        if not segs:
            continue
        words += 1
        segs_n += len(segs)
        tok.update(F.seg_class(s) for s in segs)   # (the finder's coarse sound classes: PHOIBLE and the word lists
        #                                             transcribe alike sounds differently, t̪ / t, ɛ / e, kʰ / k)
        for sy in syllabify(segs):
            syl += 1
            closed += bool(sy.coda)
            oc += len(sy.onset) >= 2
            cc += len(sy.coda) >= 2
    tot = sum(tok.values()) or 1
    out.update(closed_share=round(closed / max(syl, 1), 3), onset_cluster_share=round(oc / max(syl, 1), 3),
               coda_cluster_share=round(cc / max(syl, 1), 3), mean_segments=round(segs_n / max(words, 1), 2),
               tokens={k: v / tot for k, v in tok.items()}, top5_share=round(sum(v for _, v in tok.most_common(5)) / tot, 3))
    return out


def reference_words() -> dict[str, dict[str, str]]:
    """profile -> {concept: ipa} from reference_words.tsv (gloss upper-cased; English from sketch.ENGLISH_WORDS)."""
    out: dict = {}
    for r in F._rows(F.WORDS_TSV):
        out.setdefault(r["profile"], {})[r["gloss"].upper()] = r["ipa"]
    out["english"] = dict(SK.ENGLISH_WORDS)
    return out


PHON_KEYS = ("consonants", "vowels", "tones", "max_onset", "max_coda", "final_vowel_share", "mean_syllables",
             "cluster_share", "series", "stress", "texture", "nonhuman")


def finder(d: dict, profiles: dict, target: str) -> dict:
    f = F.lect_features({**d, "end": None}, {})
    ranked = sorted(((F.distance(f, p)[0], k) for k, p in profiles.items()), key=lambda t: t[0])
    dist, comp = F.distance(f, profiles[target])
    return {"distance": round(dist, 3), "sound_distance": round(sum(v for k, v in comp.items() if k in PHON_KEYS), 3),
            "contributions": {k: round(v, 3) for k, v in comp.items()},
            "rank": [k for _, k in ranked].index(target) + 1, "nearest": ranked[0][1],
            "features": F.public(f), "texture": f["texture"]}


def lect_record(l: LC.Lect, concepts: list[str], profiles: dict, target: str | None, with_text: bool = False) -> dict:
    d = OU.lect_json(l, False, OU.EtymTable())
    sp = OU.Speller(l)
    for c in concepts:   # (every concept asked for, not only the core list lect_json keeps)
        w = l.lexicon.words.get(c)
        if w is not None and c not in d["lexicon"]:
            d["lexicon"][c] = {"ipa": w.ipa, "roman": sp.form(w.form)}
    SK.Doc._bookify(d)
    inv = l.inventory
    rec = {"id": l.id, "stress": inv.stress, "max_onset": inv.max_onset, "max_coda": inv.max_coda,
           "coda_class": inv.coda_class, "tones": list(inv.tones),
           "typology": dict(d["typology"]), "synthesis": (d.get("complexity") or {}).get("mean_level")}
    rec["measures"] = word_measures([d["lexicon"][c]["ipa"] for c in concepts if c in d["lexicon"]])
    if target:
        rec["finder"] = finder(d, profiles, target)
    if with_text:
        rec["words"] = {c: {"ipa": INV.stressed_ipa(d["lexicon"][c]["ipa"], inv.stress),
                            "roman": d["lexicon"][c].get("roman", "")} for c in concepts if c in d["lexicon"]}
        rec["consonants"] = [to_ipa(x) for x in inv.consonants]
        rec["vowels"] = [to_ipa(x) for x in inv.vowels]
        try:
            from planet.language import sentences as SN
            utt = {u.get("id"): u for u in SN.utterances(d)}
            rec["sentences"] = [{"id": i, "en": utt[i]["en"], "roman": utt[i].get("roman", ""), "ipa": utt[i].get("ipa", ""),
                                 "gloss": " ".join(r[1] for r in utt[i].get("w", []))} for i in SENTENCE_IDS if i in utt]
        except Exception as e:  # noqa: BLE001 (a sample sentence must not stop the experiment)
            rec["sentences"] = [{"id": "error", "en": f"{type(e).__name__}: {e}", "roman": "", "ipa": "", "gloss": ""}]
    return rec


def names_for(l: LC.Lect, seed: int) -> list[str]:
    out = []
    try:
        from planet.language import personal as PE
        r = PE.Personal(SimpleNamespace(seed=seed, lects={l.id: l})).for_lect(l) or {}
        out += [f"{g['roman']} /{g.get('ipa', '')}/ '{g.get('gloss', '')}'" for g in r.get("given", [])[:3]]
    except Exception as e:  # noqa: BLE001
        out.append(f"(names failed: {type(e).__name__})")
    try:
        from planet.language import names as NM
        n = NM._people_name(l, [], "the people", "E1")
        if n:
            out.append(f"{n['roman']} /{n['ipa']}/ 'the people'")
    except Exception:  # noqa: BLE001
        pass
    return out


def run_one(task) -> dict:
    """One (language or None, tier, seed): proto and daughter records, scored against the language (the control
    against every language)."""
    key, tier, seed, kyr, concepts, show, scale = task
    profiles = F.load_profiles()
    refw = reference_words()
    targets = list(LANGS) if tier == CONTROL else [key]
    out = {"key": key, "tier": tier, "seed": seed}
    with length_patch(scale if tier == "full" else None):
        p = make_proto(seed, key, tier, refw)
        stages = (("proto", p),)
        d, out["fired"] = evolve(p, seed, kyr)
        out["changes"] = sorted({c["rule"] for c in d.changes})
        stages += (("daughter", d),)
        for stage, lect in stages:
            rec = {"by_target": {t: lect_record(lect, concepts[t], profiles, t) for t in targets},
                   "shown": lect_record(lect, show, profiles, None, with_text=True)}
            rec["names"] = names_for(lect, seed) if stage == "proto" else []
            out[stage] = rec
    return out


# ---- the summary ----------------------------------------------------------------------------------------------------------

MEASURE_ROWS = [("consonants", "consonants (phonemes)", "f"), ("vowels", "vowels (phonemes)", "f"), ("tones", "tones", "f"),
                ("final_vowel_share", "words ending in a vowel", "m"), ("initial_vowel_share", "words starting with a vowel", "m"),
                ("mean_syllables", "syllables per word", "m"), ("mean_segments", "segments per word", "m"),
                ("closed_share", "closed syllables (coda share)", "m"), ("onset_cluster_share", "syllables with an onset cluster", "m"),
                ("coda_cluster_share", "syllables with a coda cluster", "m"), ("cluster_share", "words with any CC", "m"),
                ("consonants_per_vowel", "consonants per vowel (tokens)", "m"), ("top5_share", "token share of the 5 commonest segments", "m")]
COLS = tuple(f"{t}_{s}" for t in TIERS for s in ("proto", "daughter"))


def _agg(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"mean": round(st.mean(xs), 3), "min": round(min(xs), 3), "max": round(max(xs), 3)}


def _recs(results, key, tier, stage):
    return [r[stage]["by_target"][key] for r in results if r["tier"] == tier and (tier == CONTROL or r["key"] == key)]


def summarise(results: list[dict]) -> dict:
    profiles = F.load_profiles()
    refw = reference_words()
    summ = {}
    for key in sorted({r["key"] for r in results if r["tier"] != CONTROL}, key=list(LANGS).index):
        real = word_measures(list(refw.get(key, {}).values()))
        prof = profiles[key]
        real.update(consonants=prof["consonants"], vowels=prof["vowels"], tones=prof["tones"])
        rows, tokens = {}, {}
        for col in COLS:
            tier, stage = col.split("_")
            recs = _recs(results, key, tier, stage)
            m = {name: _agg([(r["finder"]["features"] if src == "f" else r["measures"]).get(name) for r in recs])
                 for name, _lab, src in MEASURE_ROWS}
            fd = {x: _agg([r["finder"][x] for r in recs]) for x in ("distance", "sound_distance", "rank")}
            fd["nearest"] = Counter(r["finder"]["nearest"] for r in recs).most_common(3)
            fd["target_first"] = sum(r["finder"]["rank"] == 1 for r in recs)
            comp: Counter = Counter()
            for r in recs:
                comp.update(r["finder"]["contributions"])
            fd["contributions"] = {c: round(v / len(recs), 3) for c, v in comp.most_common()}
            fixed = FULL[key]["typology"]
            kept = [sum(r["typology"].get(f) == v for f, v in fixed.items()) / len(fixed) for r in recs]
            lost = Counter(f for r in recs for f, v in fixed.items() if r["typology"].get(f) != v)
            rows[col] = {"measures": m, "finder": fd, "stress": Counter(r["stress"] for r in recs).most_common(),
                         "limits": Counter(f"{r['max_onset']}/{r['max_coda']}" for r in recs).most_common(),
                         "typology_kept": _agg(kept), "typology_lost": lost.most_common(6),
                         "n": len(recs)}
            tk: Counter = Counter()
            for r in recs:
                tk.update(r["measures"]["tokens"])
            tokens[col] = {s: v / len(recs) for s, v in tk.items()}
        rt = real.pop("tokens")
        segs = sorted(set(rt) | set(tokens["inv_proto"]) | set(tokens["full_proto"]), key=lambda s: -rt.get(s, 0))
        tok_rows = [{"seg": s, "real": round(rt.get(s, 0), 4), **{c: round(tokens[c].get(s, 0), 4) for c in
                                                                    ("inv_proto", "full_proto", "full_daughter")}} for s in segs]
        summ[key] = {"label": LANGS[key]["label"], "note": LANGS[key]["note"], "inventory": real_inventory_ipa(key),
                     "real": real, "real_stress": prof["stress"], "real_limits": f"{prof['max_onset']}/{prof['max_coda']}",
                     "rows": rows, "tokens": tok_rows, "n_real_words": len(refw.get(key, {})),
                     "full_shapes": shapes_of(list(refw[key].values()), min(prof["max_onset"] or 1, 2),
                                              min(prof["max_coda"] or 0, 2)),
                     "full": {k: v for k, v in FULL[key].items() if k != "typology"},
                     "full_typology": FULL[key]["typology"]}
    return summ


# ---- the page -------------------------------------------------------------------------------------------------------------

E = html.escape
PCT = {"final_vowel_share", "initial_vowel_share", "closed_share", "onset_cluster_share", "coda_cluster_share", "cluster_share",
       "top5_share"}
CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#6b6a66;--line:#dedbd3;--card:#fff;--acc:#2f5d8a;--hi:#fff3cd;--bad:#a8322d}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#17181a;--fg:#e8e6e1;--mut:#9a978f;--line:#33342f;--card:#1f2023;--acc:#8fb7e0;--hi:#3d3519;--bad:#e07a74}}
:root[data-theme=dark]{--bg:#17181a;--fg:#e8e6e1;--mut:#9a978f;--line:#33342f;--card:#1f2023;--acc:#8fb7e0;--hi:#3d3519;--bad:#e07a74}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:16px}h1{font-size:1.6rem;margin:.4em 0}h2{margin-top:2.2em;border-bottom:2px solid var(--line);padding-bottom:.2em}
h3{margin:1.4em 0 .4em}p,li{max-width:85ch}.mut,.r{color:var(--mut)}.r{font-size:.85em}
nav{position:sticky;top:0;background:var(--bg);padding:6px 0;border-bottom:1px solid var(--line);z-index:2}nav a{margin-right:.8em;color:var(--acc)}
table{border-collapse:collapse;font-size:.86rem;background:var(--card)}td,th{border:1px solid var(--line);padding:3px 6px;vertical-align:top;text-align:left}
th{background:var(--bg)}.wrap{overflow-x:auto;max-width:100%;margin:.5em 0}
.ipa{font-family:'Charis SIL','Doulos SIL','Noto Sans',serif;color:var(--mut);font-size:.85em}.d{color:var(--acc);font-size:.85em}
.real{background:var(--hi)}.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:10px 14px;margin:.6em 0}
.gap{border-left:4px solid var(--bad);padding-left:10px;margin:1em 0}.small{font-size:.85rem}details{margin:.5em 0}summary{cursor:pointer;color:var(--acc)}
.sent{margin:.3em 0 .6em}.sent b{font-weight:600}
"""
COL_HEAD = {"inv_proto": "inventory only", "inv_daughter": "inventory only, +{k} kyr", "full_proto": "full toolkit",
            "full_daughter": "full toolkit, +{k} kyr", "control_proto": "control", "control_daughter": "control, +{k} kyr"}


def _fmt(a, pct=False):
    if a is None:
        return "–"
    f = (lambda x: f"{x:.0%}") if pct else (lambda x: f"{x:.2f}".rstrip("0").rstrip(".") if abs(x) < 10 else f"{x:.0f}")
    if isinstance(a, dict):
        return f"{f(a['mean'])} <span class=r>({f(a['min'])}–{f(a['max'])})</span>"
    return E(f(a)) if isinstance(a, (int, float)) else E(str(a))


def _heads(k):
    return "".join(f"<th>{E(COL_HEAD[c].format(k=f'{k:g}'))}</th>" for c in COLS)


def page(summ: dict, results: list[dict], args, show: list[str], refw: dict, extra: str = "") -> str:
    ov, _, gaps = extra.partition("<!--GAPS-->")
    out = ["<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>",
           "<title>Real inventories, real toolkits</title><style>", CSS, "</style></head><body><main>",
           "<h1>Real languages' toolkits in our engine</h1>",
           f"<p>For each language, {args.seeds} human proto-languages in three tiers: <b>inventory only</b> (the real "
           "phonemes, everything else drawn as normal), <b>full toolkit</b> (the phonemes plus the syllable templates read "
           "off real words, the onset and coda limits, the coda class, stress or tone, the root length, and the main grammar "
           "settings: word order, adpositions, case, gender or classes, agreement, articles, tense), and the <b>control</b> "
           f"(a normal random proto). Each proto then changed for {args.kyr:g} thousand years under the normal "
           "sound-change, word and grammar engine, with no neighbours.</p>",
           "<p class=mut>Finder distance: tools/language/find.py's weighted distance to the language's reference profile "
           "(0 = identical; for comparison, the closest living human lect in run a24559 is 2.9 from English, 3.0 from Spanish, 2.6 from Swahili, 1.4 from Japanese, 3.9 from Mandarin, 2.7 from Hawaiian and 4.8 from Arabic). "
           "The sound part leaves out word order, adpositions, case and synthesis. Rank: where the target language comes "
           "among the finder's 16 profiles (1 = nearest).</p>",
           "<nav>" + "".join(f"<a href='#{k}'>{E(v['label'])}</a>" for k, v in summ.items()) + "<a href='#gaps'>Gaps</a></nav>",
           ov]
    out.append(_overview(summ, args))
    for key, s in summ.items():
        out.append(_section(key, s, results, args, show, refw.get(key, {})))
    out.append(gaps)
    out.append("<p class='mut small'>Made by tools/language/real_inventory.py (engine code unchanged). PHOIBLE 2.0 (Moran & "
               "McCloy eds. 2019, CC-BY-SA 3.0). Real word lists: tools/language/data/reference_words.tsv. No audio.</p>"
               "</main></body></html>")
    return "\n".join(out)


def _overview(summ, args) -> str:
    out = ["<h2 id=overview>All languages at a glance</h2><div class=wrap><table><tr><th>finder distance (rank)</th>",
           _heads(args.kyr), "</tr>"]
    for key, s in summ.items():
        R = s["rows"]
        out.append(f"<tr><td><a href='#{key}'>{E(s['label'])}</a></td>" + "".join(
            f"<td>{R[c]['finder']['distance']['mean']:.2f} <span class=r>(rank {R[c]['finder']['rank']['mean']:.1f}; "
            f"nearest in {R[c]['finder']['target_first']}/{R[c]['n']})</span></td>" for c in COLS) + "</tr>")
    out.append("</table></div>")
    return "".join(out)


def _section(key, s, results, args, show, real_words) -> str:
    inv = s["inventory"]
    R = s["rows"]
    out = [f"<h2 id={key}>{E(s['label'])}</h2>",
           f"<p class=small>{E(s['note'])}<br><b>Consonants ({len(inv['consonants'])}):</b> "
           f"<span class=ipa>{E(' '.join(inv['consonants']))}</span><br><b>Vowels ({len(inv['vowels'])}):</b> "
           f"<span class=ipa>{E(' '.join(inv['vowels']))}</span>"
           + (f"<br><b>Tones:</b> <span class=ipa>{E(' '.join(inv['tones']))}</span>" if inv['tones'] else "")
           + (f"<br><span class=mut>{E('; '.join(inv['dropped']))}</span>" if inv['dropped'] else "") + "</p>",
           "<p class=small><b>Full toolkit adds:</b> syllable templates "
           + E(", ".join(f"{k} {v:.0%}" for k, v in s["full_shapes"].items()))
           + f"; limits (onset/coda) {E(s['real_limits'])} (engine cap 2/2); coda class {E(s['full']['coda_class'])}; "
           f"onsets required: {'yes' if s['full']['onset_required'] else 'no'}; stress {E(s['full']['stress'])}; grammar: "
           + E(", ".join(f"{k.replace('_', ' ')} {v}" for k, v in s["full_typology"].items())) + ".</p>"]
    out.append(f"<h3>Finder scores</h3><div class=wrap><table><tr><th></th>{_heads(args.kyr)}</tr>")
    out.append(f"<tr><td>distance to {E(s['label'])}</td>" + "".join(f"<td>{_fmt(R[c]['finder']['distance'])}</td>" for c in COLS) + "</tr>")
    out.append("<tr><td>sound part</td>" + "".join(f"<td>{_fmt(R[c]['finder']['sound_distance'])}</td>" for c in COLS) + "</tr>")
    out.append(f"<tr><td>rank of {E(s['label'])} (of 16)</td>" + "".join(f"<td>{_fmt(R[c]['finder']['rank'])}</td>" for c in COLS) + "</tr>")
    out.append("<tr><td>nearest profile (seeds)</td>" + "".join(
        "<td class=small>" + ", ".join(f"{E(k)} {n}" for k, n in R[c]['finder']['nearest']) + "</td>" for c in COLS) + "</tr>")
    out.append("<tr><td>largest parts of the distance</td>" + "".join(
        "<td class=small>" + ", ".join(f"{E(k)} {v:.2f}" for k, v in list(R[c]['finder']['contributions'].items())[:5]) + "</td>" for c in COLS) + "</tr>")
    out.append("<tr><td>grammar settings matching the real language</td>" + "".join(
        f"<td>{_fmt(R[c]['typology_kept'], True)}</td>" for c in COLS) + "</tr>")
    out.append("<tr><td>settings most often off</td>" + "".join(
        "<td class=small>" + ", ".join(f"{E(k.replace('_', ' '))} {n}" for k, n in R[c]['typology_lost'][:4]) + "</td>" for c in COLS) + "</tr>")
    out.append("</table></div>")
    out.append(f"<h3>Measures</h3><p class='mut small'>Word measures over the {s['n_real_words']} concepts of the reference word "
               "list (real = that list itself; ours = our words for the same concepts). Mean (range over seeds).</p>"
               f"<div class=wrap><table><tr><th>measure</th><th class=real>real {E(s['label'])}</th>{_heads(args.kyr)}</tr>")
    for name, lab, _src in MEASURE_ROWS:
        pct = name in PCT
        out.append(f"<tr><td>{E(lab)}</td><td class=real>{_fmt(s['real'].get(name), pct)}</td>"
                   + "".join(f"<td>{_fmt(R[c]['measures'].get(name), pct)}</td>" for c in COLS) + "</tr>")
    out.append(f"<tr><td>onset/coda limits</td><td class=real>{E(s['real_limits'])}</td>" + "".join(
        "<td class=small>" + ", ".join(f"{E(k)} ×{n}" for k, n in R[c]['limits']) + "</td>" for c in COLS) + "</tr>")
    out.append(f"<tr><td>stress</td><td class=real>{E(str(s['real_stress']))}</td>" + "".join(
        "<td class=small>" + ", ".join(f"{E(k)} {n}" for k, n in R[c]['stress']) + "</td>" for c in COLS) + "</tr>")
    out.append("</table></div>")
    tok = [t for t in s["tokens"] if t["real"] >= 0.012 or t["inv_proto"] >= 0.025 or t["full_proto"] >= 0.025][:36]
    out.append("<details><summary>Sound-class token shares (the finder's classes: t covers t, tʰ, t̪, ʈ; e covers e, ɛ): real words vs ours</summary><div class=wrap><table><tr><th>class</th>"
               "<th class=real>real</th><th>inventory only</th><th>full toolkit</th><th>full, evolved</th><th>full / real</th></tr>")
    for t in tok:
        ratio = f"{t['full_proto'] / t['real']:.1f}×" if t["real"] else ""
        out.append(f"<tr><td class=ipa>{E(t['seg'])}</td><td class=real>{t['real']:.1%}</td><td>{t['inv_proto']:.1%}</td>"
                   f"<td>{t['full_proto']:.1%}</td><td>{t['full_daughter']:.1%}</td><td>{ratio}</td></tr>")
    out.append("</table></div></details>")
    ch = Counter(c for r in results if r["tier"] == "full" and r["key"] == key for c in r.get("changes", []))
    out.append(f"<p class=small><b>Sound changes in the most full-toolkit daughters</b> (daughters out of {args.seeds} "
               "where the row fired; ids from planet/language/data/sound_changes.tsv): "
               + E(", ".join(f"{k} {n}" for k, n in ch.most_common(14))) + "</p>")
    for tier in ("full", "inv"):
        out.append(_words_table(key, tier, results, show, real_words, args))
    return "".join(out)


def _words_table(key, tier, results, show, real_words, args) -> str:
    rs = sorted((r for r in results if r["tier"] == tier and r["key"] == key), key=lambda r: r["seed"])
    k = f"{args.kyr:g}"
    out = [f"<h3>{E(TIER_LABEL[tier].capitalize())}: words and sentences, {len(rs)} protos</h3>",
           f"<p class='mut small'>Book spelling, IPA with stress, and (blue) the book spelling after {k} kyr. Column heads: "
           "onset/coda limits, stress, word order.</p>" if tier == "full" else
           f"<details><summary>Show the inventory-only words and sentences ({len(rs)} protos)</summary>",
           "<div class=wrap><table><tr><th>concept</th><th class=real>real</th>"]
    for r in rs:
        pr = r["proto"]["shown"]
        out.append(f"<th>seed {r['seed']}<br><span class=r>{pr['max_onset']}/{pr['max_coda']}, {E(pr['stress'])}"
                   f"{', ' + str(len(pr['tones'])) + ' tones' if pr['tones'] else ''}, {E(str(pr['typology'].get('word_order')))}</span></th>")
    out.append("</tr>")
    for c in show:
        rw = real_words.get(c)
        out.append(f"<tr><td>{E(SK.cname(c))}</td><td class='real ipa'>{E(rw) if rw else ''}</td>")
        for r in rs:
            w = r["proto"]["shown"]["words"].get(c)
            dw = r["daughter"]["shown"]["words"].get(c)
            out.append("<td></td>" if not w else
                       f"<td><b>{E(w['roman'])}</b><br><span class=ipa>{E(w['ipa'])}</span>"
                       + (f"<br><span class=d>→ {E(dw['roman'])}</span>" if dw else "") + "</td>")
        out.append("</tr>")
    out.append("</table></div>")
    out.append("<details><summary>Sentences and names per seed (proto, then after "
               f"{k} kyr)</summary><div class=small>" if tier == "full" else "<div class=small>")
    for r in rs:
        out.append(f"<div class=card><b>seed {r['seed']}</b> · names: {E('; '.join(r['proto']['names']))}"
                   f"<br><span class=mut>sound changes per 0.5 kyr: {r['fired']}</span>")
        for stage in ("proto", "daughter"):
            for sn in r[stage]["shown"].get("sentences", [])[:4 if stage == "proto" else 2]:
                out.append(f"<div class=sent>{'' if stage == 'proto' else '<span class=d>+' + k + ' kyr</span> '}"
                           f"“{E(sn['en'])}” <b>{E(sn['roman'])}</b> <span class=ipa>/{E(sn['ipa'])}/</span>"
                           f"<br><span class=mut>{E(sn['gloss'])}</span></div>")
        out.append("</div>")
    out.append("</div></details>" if tier == "full" else "</div></details>")
    return "".join(out)


# ---- main -----------------------------------------------------------------------------------------------------------------

def calibrate_scale(key: str, concepts: list[str], refw: dict, seeds=(101, 102, 103, 104)) -> float:
    """The constant root-length multiplier that gives `full` protos the real list's syllables per word: build a few at
    multiplier 1 and scale by real / ours (the multiplier acts on the drawn root syllables, so the ratio carries)."""
    real = word_measures(list(refw[key].values()))["mean_syllables"]
    ours = []
    with length_patch(1.0):
        for s in seeds:
            p = make_proto(s, key, "full", refw)
            ours.append(word_measures([p.lexicon.words[c].ipa for c in concepts if c in p.lexicon.words])["mean_syllables"])
    return round(max(0.6, min(2.5, real / max(st.mean(ours), 0.5))), 3)


# ---- the standing check (PW-1641) -----------------------------------------------------------------------------------------
# Owner 11-10: this experiment is the language model's Earth, a plausibility anchor run after every language-model change
# (as tools/earth_check.py is for climate). Plausible-or-better, never a fidelity target: the question is whether a
# language seeded Hawaiian-like stays recognisably itself for 2.5 kyr, not whether it reproduces Hawaiian. `--check`
# runs the full-toolkit tier and the control, prints the table below against the stored baseline
# (BASELINE, written by `--check --record`), and flags a number that moved the wrong way by more than its band (BAND_SE
# combined standard errors over the seeds, and at least the metric's floor).

BASELINE = DATA / "real_inventory_baseline.json"
CHECK_SEEDS = 20       # seeds the check runs (10 leave the per-language means too noisy to band; ~50 s with 8 workers)
BAND_SE = 2.0          # a change is flagged when it is worse than the baseline by this many combined standard errors ...
NEAR_GROWTH = 0.5      # a language counts as "kept its character" when its +kyr distance is within this of its birth one
UNIVERSAL_SHARE = 0.8  # a change fired in this share of all full-toolkit daughters (every language) is a drift signature:
#                        the engine's own habit, not any line's
#: metric -> (better direction, floor of its band)
CHECK_METRICS = {"birth": (-1, 0.15), "aged": (-1, 0.15), "growth": (-1, 0.15), "closed_shift": (-1, 0.04),
                 "final_c_shift": (-1, 0.04), "harmony": (-1, 0.15)}
AGG_METRICS = {"near": (+1, 1.0), "spread_ratio": (+1, 0.05), "universal": (-1, 1.0), "mean_growth": (-1, 0.1)}
# Absolute bars (PW-1737): the baseline bands above only catch a change for the worse, so a stale or poor baseline passes
# forever. These hold whatever the baseline says. metric -> (direction, bar, label); see ABS_BARS in check_report.
ABS_BARS = {"back_harmony": (-1, 0.25, "full-toolkit daughters that fired harmony.back < 25%"),
            "near": (+1, 4.0, "languages that kept their character >= 4 of 7"),
            "universal": (-1, 0.0, "no drift signature (a change in >= 80% of all daughters)")}


def _mse(xs: list[float]) -> tuple[float, float]:
    xs = [x for x in xs if x is not None]
    if not xs:
        return float("nan"), 0.0
    m = st.mean(xs)
    return m, (st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0)


def _as_profile(f: dict) -> dict:
    """A lect's finder features read as a reference profile, for the lect-to-lect distance."""
    p = {k: f.get(k) for k in ("consonants", "vowels", "tones", "max_onset", "max_coda", "final_vowel_share",
                               "cluster_share", "mean_syllables", "stress", "word_order", "adposition", "case", "synthesis")}
    p["series"] = [k for k in F.SERIES if f.get(k)]
    p["texture"] = f.get("texture") or {}
    return p


def lect_gap(a: dict, b: dict) -> float:
    """Symmetric finder distance between two lects (each read once as the other's profile)."""
    return 0.5 * (F.distance(a, _as_profile(b))[0] + F.distance(b, _as_profile(a))[0])


def check_metrics(results: list[dict]) -> dict:
    """Per language (full toolkit): birth and +kyr distance to the real language, their growth, the shift in
    closed-syllable share and in word-final consonants (|daughter - proto|: a language keeping its own pattern, either
    way), the share of daughters that fired a harmony change; and over all of them: how many kept their character
    (growth under NEAR_GROWTH), how far apart the seven daughters stay against the seven protos (spread_ratio: 1 = no
    convergence), and the drift signatures (changes fired in UNIVERSAL_SHARE of all daughters)."""
    fam = {base_id: r.family for r in LC.catalogue_for(PR.HUMAN, "human") for base_id in (LC.base_id(r.id),)}
    out: dict = {"langs": {}}
    full = [r for r in results if r["tier"] == "full"]
    for key in [k for k in LANGS if any(r["key"] == k for r in full)]:
        rs = sorted((r for r in full if r["key"] == key), key=lambda r: r["seed"])
        fp = [r["proto"]["by_target"][key] for r in rs]
        fd = [r["daughter"]["by_target"][key] for r in rs]
        per = {"birth": [x["finder"]["distance"] for x in fp], "aged": [x["finder"]["distance"] for x in fd]}
        per["growth"] = [b - a for a, b in zip(per["birth"], per["aged"])]
        per["closed_shift"] = [abs(b["measures"]["closed_share"] - a["measures"]["closed_share"]) for a, b in zip(fp, fd)]
        per["final_c_shift"] = [abs(b["measures"]["final_vowel_share"] - a["measures"]["final_vowel_share"])
                                for a, b in zip(fp, fd)]
        per["harmony"] = [float(any(fam.get(LC.base_id(c)) == "harmony" for c in r["changes"])) for r in rs]
        row = {}
        for k, xs in per.items():
            m, se = _mse(xs)
            row[k] = {"mean": round(m, 3), "se": round(se, 3)}
        row["closed"] = {"proto": round(st.mean(x["measures"]["closed_share"] for x in fp), 3),
                         "daughter": round(st.mean(x["measures"]["closed_share"] for x in fd), 3)}
        row["final_c"] = {"proto": round(1 - st.mean(x["measures"]["final_vowel_share"] for x in fp), 3),
                          "daughter": round(1 - st.mean(x["measures"]["final_vowel_share"] for x in fd), 3)}
        out["langs"][key] = row
    L = out["langs"]
    growths = [v["growth"]["mean"] for v in L.values()]
    out["near"] = {"mean": float(sum(g <= NEAR_GROWTH for g in growths)), "se": 0.0}
    out["mean_growth"] = {"mean": round(st.mean(growths), 3), "se": round(math.sqrt(sum(v["growth"]["se"] ** 2
                                                                                      for v in L.values())) / len(L), 3)}
    # spread: per seed, the mean pairwise gap among the languages' daughters over that among their protos
    ratios = []
    for s in sorted({r["seed"] for r in full}):
        rs = [r for r in full if r["seed"] == s]
        if len(rs) < 2:
            continue
        fe = {st_: [(r["proto" if st_ == "p" else "daughter"]["by_target"][r["key"]]["finder"]) for r in rs] for st_ in "pd"}
        g = {st_: st.mean(lect_gap({**a["features"], "texture": a["texture"]}, {**b["features"], "texture": b["texture"]})
                          for i, a in enumerate(fe[st_]) for b in fe[st_][i + 1:]) for st_ in "pd"}
        ratios.append(g["d"] / max(g["p"], 1e-9))
    m, se = _mse(ratios)
    out["spread_ratio"] = {"mean": round(m, 3), "se": round(se, 3)}
    n = len(full)
    cnt = Counter(b for r in full for b in {LC.base_id(c) for c in r["changes"]})
    sig = sorted(((c, round(v / n, 2)) for c, v in cnt.items() if v / n >= UNIVERSAL_SHARE), key=lambda t: -t[1])
    out["universal"] = {"mean": float(len(sig)), "se": 0.0}
    out["back_harmony"] = {"mean": round(sum("harmony.back" in {LC.base_id(c) for c in r["changes"]} for r in full) / max(n, 1), 3),
                           "se": 0.0}
    out["signatures"] = sig
    out["changes_per_daughter"] = round(st.mean(len(r["changes"]) for r in full), 1)
    ctl = [r for r in results if r["tier"] == CONTROL]
    out["control_changes_per_daughter"] = round(st.mean(len(r["changes"]) for r in ctl), 1) if ctl else None
    return out


def _verdict(new: dict, old: dict | None, better: int, floor: float) -> str:
    if old is None:
        return ""
    d = (new["mean"] - old["mean"]) * better      # > 0: better
    band = max(floor, BAND_SE * math.sqrt(new["se"] ** 2 + old["se"] ** 2))
    if d < -band:
        return "WORSE"
    if d > band:
        return "better"
    return "ok"


def check_report(m: dict, base: dict | None, args) -> tuple[str, int]:
    """The printed table and the number of WORSE flags."""
    L = []
    p = L.append
    worse = 0
    bl = (base or {}).get("metrics")
    p(f"=== Real-language benchmark (PW-1641): {args.seeds} seeds, +{args.kyr:g} kyr, full toolkit ===")
    if base:
        p(f"baseline: {base.get('label', '?')} ({base.get('seeds')} seeds, +{base.get('kyr')} kyr)")
    else:
        p("baseline: none stored (run with --record)")
    p("distance = tools/language/find.py's distance to the real language's profile (lower = closer); "
      "growth = +kyr minus birth")
    p("shift = |daughter - proto| (a language keeping its own pattern, open or closed); harmony = daughters firing one")
    head = f"{'':9s} {'birth':>6s} {'+kyr':>6s} {'growth':>7s}  {'closed p>d':>11s} {'shift':>6s}  " \
           f"{'final C p>d':>11s} {'shift':>6s}  {'harm':>5s}  vs baseline"
    p("")
    p(head)
    for key, row in m["langs"].items():
        flags = []
        for k, (bt, fl) in CHECK_METRICS.items():
            v = _verdict(row[k], (bl or {}).get("langs", {}).get(key, {}).get(k), bt, fl)
            if v == "WORSE":
                worse += 1
            if v and v != "ok":
                old = bl["langs"][key][k]["mean"]
                flags.append(f"{k} {v} ({old:.2f})")
        p(f"{LANGS[key]['label']:9s} {row['birth']['mean']:6.2f} {row['aged']['mean']:6.2f} {row['growth']['mean']:+7.2f}  "
          f"{row['closed']['proto']:5.2f}>{row['closed']['daughter']:4.2f} {row['closed_shift']['mean']:6.2f}  "
          f"{row['final_c']['proto']:5.2f}>{row['final_c']['daughter']:4.2f} {row['final_c_shift']['mean']:6.2f}  "
          f"{row['harmony']['mean']:5.2f}  {', '.join(flags) or ('ok' if bl else '')}")
    p("")
    labels = {"near": f"languages that kept their character (growth <= {NEAR_GROWTH})",
              "mean_growth": "mean distance growth",
              "spread_ratio": "spread kept (daughters' mutual distance / protos'; 1 = no convergence)",
              "universal": f"drift signatures (changes in >= {UNIVERSAL_SHARE:.0%} of all daughters)"}
    for k, (bt, fl) in AGG_METRICS.items():
        old = (bl or {}).get(k)
        v = _verdict(m[k], old, bt, fl)
        worse += v == "WORSE"
        was = f"  baseline {old['mean']:g}" if old else ""
        p(f"{labels[k]:72s} {m[k]['mean']:6g}{was}  {v}")
    p("signatures: " + (", ".join(f"{c} {s:.0%}" for c, s in m["signatures"]) or "none"))
    p(f"distinct changes per daughter: full toolkit {m['changes_per_daughter']}, control {m['control_changes_per_daughter']}")
    p("")
    p("absolute bars (PW-1737; hold whatever the baseline):")
    miss = 0
    for k, (bt, bar, label) in ABS_BARS.items():
        v = m[k]["mean"]
        ok = v >= bar if bt > 0 else (v <= bar if bar == 0 else v < bar)
        miss += not ok
        p(f"  {label:70s} {v:6g}  {'ok' if ok else 'MISSED'}")
    p("")
    p(f"{worse} metric(s) WORSE than the baseline" if bl else "no baseline to compare with")
    p(f"{miss} of {len(ABS_BARS)} absolute bar(s) missed")
    return "\n".join(L), worse + miss


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--extract", help="rebuild tools/language/data/real_inventories.tsv from PHOIBLE's phoible.csv and exit")
    ap.add_argument("--langs", default=",".join(LANGS))
    ap.add_argument("--seeds", type=int, default=None, help=f"seeds per language and tier (10; --check {CHECK_SEEDS})")
    ap.add_argument("--kyr", type=float, default=2.5)
    ap.add_argument("--workers", type=int, default=8, help="processes (capped at 8)")
    ap.add_argument("--json", help="write the raw results and summary here")
    ap.add_argument("--html", help="write the page here")
    ap.add_argument("--extra-html", help="an HTML fragment: an overview part, then <!--GAPS-->, then the gaps section")
    ap.add_argument("--check", action="store_true", help="the standing check (PW-1641): print the benchmark table "
                    "against the stored baseline; exit 1 if a number is worse than its band or misses an absolute bar")
    ap.add_argument("--record", metavar="LABEL", help="with --check: store this run as the baseline, labelled LABEL")
    a = ap.parse_args(argv)
    if a.seeds is None:
        a.seeds = CHECK_SEEDS if a.check else 10
    if a.extract:
        extract(a.extract)
        return 0
    langs = [k for k in a.langs.split(",") if k]
    refw = reference_words()
    probe = make_proto(1, None, CONTROL)
    concepts = {k: [c for c in refw.get(k, {}) if c in probe.lexicon.words] for k in LANGS}
    show = [c for c in ["I", "THOU", "WE", "WHO", "WHAT", "NOT", "ONE", "TWO", "THREE", "MAN", "WOMAN", "MOTHER", "CHILD",
                        "DOG", "FISH", "BIRD", "TREE", "WATER", "FIRE", "STONE", "SUN", "MOON", "STAR", "NIGHT", "HAND",
                        "EYE", "HEAD", "NAME", "EAT", "DRINK", "SEE", "SLEEP", "BIG", "GOOD"] if c in probe.lexicon.words][:30]
    scales = {k: calibrate_scale(k, concepts[k], refw) for k in langs}
    print("root-length multipliers:", scales)
    tasks = [(k, t, s, a.kyr, concepts, show, scales[k]) for k in langs for t in ("inv", "full") for s in range(1, a.seeds + 1)]
    tasks += [(None, CONTROL, s, a.kyr, concepts, show, None) for s in range(1, a.seeds + 1)]
    if a.workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(a.workers, 8)) as pool:
            results = pool.map(run_one, tasks, chunksize=1)
    else:
        results = [run_one(t) for t in tasks]
    summ = summarise(results)
    for k, s in summ.items():
        R = s["rows"]
        print(f"{s['label']:9s} " + " | ".join(f"{c} {R[c]['finder']['distance']['mean']:.2f} r{R[c]['finder']['rank']['mean']:.1f}"
                                               for c in COLS))
    if a.json:
        Path(a.json).write_text(json.dumps({"summary": summ, "results": results, "show": show, "concepts": concepts,
                                            "scales": scales}, ensure_ascii=False, default=list), encoding="utf-8")
    if a.html:
        extra = Path(a.extra_html).read_text(encoding="utf-8") if a.extra_html else ""
        doc = page(summ, results, a, show, refw, extra)
        Path(a.html).write_text(doc, encoding="utf-8")
        print(f"wrote {a.html} ({len(doc.encode()) / 1e6:.2f} MB)")
    if a.check:
        m = check_metrics(results)
        base = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() and not a.record else None
        text, worse = check_report(m, base, a)
        print()
        print(text)
        if a.record:
            BASELINE.write_text(json.dumps({"label": a.record, "seeds": a.seeds, "kyr": a.kyr, "metrics": m},
                                           ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"recorded the baseline in {BASELINE}")
        return 1 if worse else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
