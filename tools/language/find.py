"""Find languages in a run's languages.json by features, or by likeness to a named reference language.

    uv run python tools/language/find.py runs/a24559/languages.json --like hawaiian
    uv run python tools/language/find.py runs/a24559/languages.json --like sindarin --people elves --explain
    uv run python tools/language/find.py runs/a24559/languages.json --where "syllables=CV" --where "consonants<=10" \\
        --where "tones>=2" --order VSO --sort final_vowel_share
    uv run python tools/language/find.py runs/a24559/languages.json --list-profiles | --features

Filters (`--where`, `--people`, `--order`) narrow the living lects; `--like P` ranks what is left by a weighted distance to the
reference profile P (tools/language/data/reference_profiles.tsv, sound texture from reference_words.tsv), else `--sort KEY`
(descending; `KEY:asc` for ascending), else by speakers. Each hit prints its id, endonym, people, place, a one-line feature
summary and sample words (book spelling and IPA); `--explain` adds the per-feature distance contributions, `--json` prints
everything as JSON.

`--where` takes `KEY OP VALUE` with OP one of = != < <= > >= ~ (substring); `=` and `!=` accept alternatives `a|b`; a bare
`KEY` keeps lects where the feature is true or non-zero, `!KEY` where it is false or zero. Keys: `--features`.

Everything is computed in memory from the main file (no sidecars; about 2-3 s on a24559), so nothing is cached and nothing is
written next to the run.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import sketch as SK  # noqa: E402

from planet.language import output as OU  # noqa: E402
from planet.language import percepts as P  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
PROFILES_TSV = DATA / "reference_profiles.tsv"
WORDS_TSV = DATA / "reference_words.tsv"

#: sound series, each 0/1 per lect (inventory) and listed per reference profile
SERIES = {
    "clicks": lambda s: s.kind == "C" and s.manner == 8,
    "ejectives": lambda s: s.kind == "C" and s.larynx == 2,
    "implosives": lambda s: s.kind == "C" and s.larynx == 3,
    "retroflex": lambda s: s.kind == "C" and bool(s.retroflex),
    "uvular": lambda s: s.kind == "C" and s.place == 6,
    "pharyngeal": lambda s: s.kind == "C" and (s.place == 7 or s.secondary == 4),   # ħ ʕ, or pharyngealized (Arabic emphatics)
    "labial_velar": lambda s: s.kind == "C" and bool(s.double) and s.manner in (0, 3),  # k͡p ɡ͡b ŋ͡m (not w)
    "front_rounded": lambda s: s.kind == "V" and s.back <= 1 and bool(s.round),     # y ø œ
    "nasal_vowels": lambda s: s.kind == "V" and bool(s.nasal),
    "interdental": lambda s: s.kind == "C" and s.place == 1 and s.manner == 2 and not s.sibilant,  # θ ð
    "aspirated": lambda s: s.kind == "C" and s.larynx == 1,
    "long_vowels": lambda s: s.kind == "V" and bool(s.length),
    "lateral_obstruent": lambda s: s.kind == "C" and bool(s.lateral) and s.manner in (1, 2),   # ɬ ɮ tɬ (Welsh ll, Klingon tlh)
}
#: words shown per hit
SAMPLE_WORDS = ["SUN", "WATER", "MOTHER", "FIRE", "BIRD", "I", "TWO", "EAT"]
#: concepts whose forms give a lect's word statistics and sound texture (the core list sketch.py compares with English)
TEXTURE_CONCEPTS = sorted(set(SK.ENGLISH_WORDS) | set(SK.SAMPLE) | {"MOTHER", "FATHER", "HOUSE", "SING", "CHILD (YOUNG HUMAN)"})
ENGINE_MAX_CLUSTER = 2   # the engine's largest onset and coda (sketch.py index page)
NUMERIC = ("consonants", "vowels", "tones", "max_onset", "max_coda", "final_vowel_share", "initial_vowel_share",
           "mean_syllables", "cluster_share", "consonants_per_vowel", "synthesis", "fusion", "population", "nonhuman")

#: weight of each distance component; every component is first scaled to 0..1 (see distance())
WEIGHTS = {"consonants": 1.0, "vowels": 0.7, "tones": 1.0, "max_onset": 0.5, "max_coda": 0.8, "final_vowel_share": 1.2,
           "mean_syllables": 0.6, "cluster_share": 0.6, "series": 0.25, "stress": 0.3, "word_order": 0.3,
           "adposition": 0.1, "case": 0.2, "synthesis": 0.2, "texture": 2.5, "nonhuman": 0.8}
TEXTURE_SCALE = 0.6      # 1 - cosine at which the texture term is full (lects span cosine ~0.1-0.9 to a profile; median ~0.5)


# ---- segments and words -----------------------------------------------------------------------------------------------

def seg_class(s) -> str:
    """A coarse sound class for the texture vector: what an ear (or an eye on the romanization) notices."""
    if P.is_nonhuman(s):
        return "NH"
    if s.kind == "V":
        if s.back <= 1 and s.round:
            return "y"
        if s.height <= 1:
            return "a"
        if s.back <= 1:
            return "i" if s.height >= 5 else "e"
        if s.back >= 3 and s.round:
            return "u" if s.height >= 5 else "o"
        return "ə"
    m = s.manner
    if m == 8:
        return "!"
    if m == 9:
        return "NH"
    if s.larynx in (2, 3):
        return "ʼ"
    if m == 0:
        if s.double:
            return "kp"
        if s.place == 0:
            return "b" if s.voice else "p"
        if s.place <= 3:
            return "d" if s.voice else "t"
        if s.place <= 5:
            return "g" if s.voice else "k"
        return "q" if s.place == 6 else "ʔ"
    if m in (1, 2):
        if s.lateral:
            return "ɬ"
        if s.sibilant:
            return "ts" if m == 1 else "s"
        if s.place == 0:
            return "f"
        if s.place == 1:
            return "θ"
        if s.place <= 4:
            return "ts" if m == 1 else "s"
        if s.place <= 6:
            return "x"
        return "ħ" if s.place == 7 else "h"
    if m == 3:
        return "m" if s.place == 0 else ("n" if s.place <= 3 else "ŋ")
    if m == 4:
        if s.lateral:
            return "l"
        if s.double or s.place in (0, 5):
            return "w"
        return "j" if s.place == 4 else "r"
    return "l" if m == 5 else "r"


def word_stats(ipas: list[str]) -> dict:
    """Word-level statistics and the sound-texture vector of a list of IPA words (a lect's core forms or a reference list)."""
    tex, words, finals, syl, clus, nc, nv = Counter(), 0, 0, 0, 0, 0, 0
    initials = 0
    for ipa in ipas:
        segs = [s for s in P.from_ipa(ipa) if s.kind != "T"]
        if not segs:
            continue
        words += 1
        kinds = [s.kind for s in segs]
        cls = [seg_class(s) for s in segs]
        tex.update(cls)
        tex["#" + cls[-1]] += 0.5 * len(segs)   # word-final and word-initial classes, weighted per word
        tex["^" + cls[0]] += 0.25 * len(segs)
        finals += kinds[-1] == "V"
        initials += kinds[0] == "V"
        syl += sum(1 for i, k in enumerate(kinds) if k == "V" and (i == 0 or kinds[i - 1] != "V"))
        clus += any(a == b == "C" for a, b in zip(kinds, kinds[1:]))
        nc += kinds.count("C")
        nv += kinds.count("V")
    if not words:
        return {"final_vowel_share": None, "initial_vowel_share": None, "mean_syllables": None, "cluster_share": None,
                "consonants_per_vowel": None, "texture": {}}
    tot = sum(tex.values())
    return {"final_vowel_share": round(finals / words, 3), "initial_vowel_share": round(initials / words, 3),
            "mean_syllables": round(syl / words, 2), "cluster_share": round(clus / words, 3),
            "consonants_per_vowel": round(nc / max(1, nv), 2), "texture": {k: v / tot for k, v in tex.items()}}


def cosine(a: dict, b: dict) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def syllable_template(onset, coda) -> str:
    return "C" * max(1, int(onset or 1)) + "V" + "C" * int(coda or 0)


# ---- lects ----------------------------------------------------------------------------------------------------------------

def _place(deme_name: str | None) -> str:
    m = re.search(r"\((.*)\)\s*$", deme_name or "")
    return m.group(1) if m else ""


def lect_features(l: dict, names: dict) -> dict:
    """The feature vector of one living lect (plus id, names and the texture vector under 'texture')."""
    inv = l.get("inventory") or {}
    t = l.get("typology") or {}
    cx = l.get("complexity") or {}
    segs = SK.inv_segments(l)
    nm = SK.Doc.deme_name(SimpleNamespace(names=names), l)
    f = {"id": l["id"], "name": nm["roman"] if nm else "", "people": l.get("people", ""),
         "place": _place(l.get("deme_name")), "language": l.get("language"), "family": l.get("family_scholars"),
         "family_true": l.get("family_true"), "population": int(l.get("population") or 0),
         "consonants": len(inv.get("consonants", [])), "vowels": len(inv.get("vowels", [])),
         "tones": len(inv.get("tones") or []), "max_onset": inv.get("max_onset", 1), "max_coda": inv.get("max_coda", 0),
         "stress": inv.get("stress"), "synthesis": cx.get("mean_level"), "fusion": cx.get("fused"),
         "nonhuman": sum(1 for s in segs if P.is_nonhuman(s))}
    f["syllables"] = syllable_template(f["max_onset"], f["max_coda"])
    for k, pred in SERIES.items():
        f[k] = int(any(pred(s) for s in segs))
    lex = l.get("lexicon") or {}
    f.update(word_stats([lex[c]["ipa"] for c in TEXTURE_CONCEPTS if c in lex and lex[c].get("ipa")]))
    for k, v in t.items():
        f.setdefault(k, v)
    return f


def living(doc: dict) -> list[dict]:
    return [l for l in doc["lects"] if l.get("end") is None and l.get("deme") is not None]


def load(path) -> tuple[dict, list[dict]]:
    doc = OU.load(path, sidecars=False)
    names = doc.get("names") or {}
    return doc, [lect_features(l, names) for l in living(doc)]


# ---- reference profiles ---------------------------------------------------------------------------------------------------

def _rows(path: Path) -> list[dict]:
    lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def load_profiles() -> dict[str, dict]:
    words: dict[str, list[str]] = {}
    for r in _rows(WORDS_TSV):
        words.setdefault(r["profile"], []).append(r["ipa"])
    words["english"] = list(SK.ENGLISH_WORDS.values())
    out = {}
    for r in _rows(PROFILES_TSV):
        p = {"profile": r["profile"], "label": r["label"], "sources": r["sources"]}
        for k in ("consonants", "vowels", "tones", "max_onset", "max_coda"):
            p[k] = int(r[k]) if r[k].strip() else None
        p["synthesis"] = float(r["synthesis"]) if r["synthesis"].strip() else None
        for k in ("stress", "word_order", "adposition", "case"):
            p[k] = r[k].strip() or None
        listed = {x.strip() for x in r["series"].split(",") if x.strip()}
        unknown = listed - set(SERIES)
        if unknown:
            raise ValueError(f"{r['profile']}: unknown series {sorted(unknown)}")
        p["series"] = sorted(listed)
        if r["profile"] == "english":   # one English: the reference sketch.py's English-likeness score uses
            p.update(consonants=len(SK.ENGLISH_CONSONANTS), vowels=len(SK.ENGLISH_VOWELS),
                     max_onset=SK.ENGLISH_MAX_ONSET, max_coda=SK.ENGLISH_MAX_CODA)
        p["words"] = len(words.get(r["profile"], []))
        p.update(word_stats(words.get(r["profile"], [])))
        out[r["profile"]] = p
    return out


def distance(f: dict, prof: dict) -> tuple[float, dict]:
    """Weighted distance of a lect's features to a profile, and each component's share (WEIGHTS x a 0..1 gap)."""
    c = {}

    def put(key, gap):
        if gap is not None:
            c[key] = WEIGHTS[key] * min(1.0, gap)

    def logratio(a, b):
        return None if a is None or b is None else abs(math.log(max(a, 1) / max(b, 1))) / math.log(3)

    put("consonants", logratio(f["consonants"], prof["consonants"]))
    put("vowels", logratio(f["vowels"], prof["vowels"]))
    if prof["tones"] is not None:
        put("tones", abs(f["tones"] - prof["tones"]) / 3)
    for k in ("max_onset", "max_coda"):
        if prof[k] is not None:
            put(k, abs(f[k] - min(prof[k], ENGINE_MAX_CLUSTER)) / 2)
    for k, scale in (("final_vowel_share", 1.0), ("cluster_share", 1.0), ("mean_syllables", 1.5)):
        if prof.get(k) is not None and f.get(k) is not None:
            put(k, abs(f[k] - prof[k]) / scale)
    c["series"] = WEIGHTS["series"] * sum(f[k] != (k in prof["series"]) for k in SERIES)   # per mismatched series, uncapped
    for k in ("stress", "word_order", "adposition", "case"):
        if prof[k] is not None:
            put(k, float(f.get(k) != prof[k]))
    if prof["synthesis"] is not None and f.get("synthesis") is not None:
        put("synthesis", abs(f["synthesis"] - prof["synthesis"]) / 1.5)
    if prof.get("texture"):
        put("texture", (1 - cosine(f["texture"], prof["texture"])) / TEXTURE_SCALE)
    put("nonhuman", f["nonhuman"] / 3)
    return sum(c.values()), c


# ---- filters ---------------------------------------------------------------------------------------------------------------

_COND = re.compile(r"^\s*([\w.]+)\s*(<=|>=|!=|=|<|>|~)\s*(.+?)\s*$")


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def parse_where(expr: str):
    expr = expr.strip()
    if _COND.match(expr):
        k, op, v = _COND.match(expr).groups()
        return k, op, v
    if re.fullmatch(r"!?\w+", expr):
        return expr.lstrip("!"), ("falsy" if expr.startswith("!") else "truthy"), None
    raise ValueError(f"cannot read --where {expr!r} (want KEY OP VALUE, KEY or !KEY)")


def matches(f: dict, cond) -> bool:
    k, op, v = cond
    if k not in f:
        raise KeyError(k)
    x = f[k]
    if op == "truthy":
        return bool(x) and x not in ("no", "none")
    if op == "falsy":
        return not x or x in ("no", "none")
    if op == "~":
        return v.lower() in str(x).lower()
    if op in ("=", "!="):
        alts = [a.strip() for a in v.split("|")]
        hit = any((_num(a) is not None and _num(x) is not None and _num(a) == _num(x)) or str(x).lower() == a.lower()
                  for a in alts)
        return hit if op == "=" else not hit
    a, b = _num(x), _num(v)
    if a is None or b is None:
        return False
    return {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op]


def _singular(w: str) -> str:
    w = w.strip().lower().replace(" ", "_").replace("-", "_")
    if w.endswith("ves"):
        return w[:-3] + "f"   # elves, dwarves
    if w.endswith("men"):
        return w[:-3] + "man"
    if w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def people_match(people: str, wanted: list[str]) -> bool:
    """'elves' takes elf, drow and sea elf (sketch.group); 'dragons' every dragon kind; 'giants' every giant."""
    for w in wanted:
        w = _singular(w)
        if people == w or SK.group(people) == w or people.endswith("_" + w):
            return True
    return False


# ---- output ----------------------------------------------------------------------------------------------------------------

def samples(l: dict) -> list[dict]:
    SK.Doc._bookify(l)   # book spellings, as the sketches show them (only the lects printed)
    lex = l.get("lexicon") or {}
    return [{"concept": SK.cname(c), "roman": lex[c].get("roman", ""), "ipa": lex[c].get("ipa", "")}
            for c in SAMPLE_WORDS if c in lex]


def summary(f: dict) -> str:
    series = [k.replace("_", " ") for k in SERIES if f[k]]
    parts = [f"{f['consonants']}C {f['vowels']}V", f"{f['tones']} tones" if f["tones"] else "no tone", f["syllables"],
             f"V-final {f['final_vowel_share']:.0%}" if f["final_vowel_share"] is not None else "",
             f"{f['mean_syllables']} syl/word" if f["mean_syllables"] is not None else "",
             f"stress {f['stress']}", f.get("word_order") or "", f"case {f.get('case')}",
             f"synthesis {f['synthesis']}" if f.get("synthesis") is not None else ""]
    if series:
        parts.append("has " + ", ".join(series))
    if f["nonhuman"]:
        parts.append(f"{f['nonhuman']} non-human sounds")
    return " · ".join(p for p in parts if p)


def public(f: dict) -> dict:
    return {k: v for k, v in f.items() if k != "texture"}


def run(doc: dict, feats: list[dict], wheres=(), people=None, order=None, like=None, sort=None, top=8,
        profiles=None) -> tuple[list[dict], int]:
    """Filter, rank and return hits: {features, distance, contributions, samples}."""
    conds = [parse_where(w) for w in wheres]
    if order:
        conds.append(("word_order", "=", order))
    want = [p for p in (people or "").split(",") if p.strip()]
    rows = [f for f in feats if all(matches(f, c) for c in conds) and (not want or people_match(f["people"], want))]
    hits = []
    if like:
        profiles = profiles or load_profiles()
        if like not in profiles:
            raise KeyError(f"no profile {like!r}; have {', '.join(sorted(profiles))}")
        for f in rows:
            d, c = distance(f, profiles[like])
            hits.append({"f": f, "distance": round(d, 3), "contributions": {k: round(v, 3) for k, v in c.items()}})
    else:
        hits = [{"f": f} for f in rows]
    if sort:
        key, _, way = sort.partition(":")
        if feats and key not in feats[0]:
            raise KeyError(key)
        num = all(_num(h["f"].get(key)) is not None for h in hits)
        hits.sort(key=lambda h: (-h["f"]["population"], h["f"]["id"]))   # ties: most spoken first
        hits.sort(key=lambda h: (_num(h["f"].get(key)) if num else str(h["f"].get(key))), reverse=(way != "asc"))
    elif like:
        hits.sort(key=lambda h: (h["distance"], h["f"]["id"]))
    else:
        hits.sort(key=lambda h: (-h["f"]["population"], h["f"]["id"]))
    lects = {l["id"]: l for l in doc["lects"]}
    out = []
    for h in hits[:top]:
        h["samples"] = samples(lects[h["f"]["id"]])
        out.append(h)
    return out, len(rows)


def print_hits(hits, n_rows, n_all, like, profiles, explain) -> None:
    head = f"{n_rows} of {n_all} living lects pass the filters"
    if like:
        head += f"; ranked by distance to {profiles[like]['label']}"
    print(head + "\n")
    for i, h in enumerate(hits, 1):
        f = h["f"]
        dist = f"   distance {h['distance']:.2f}" if "distance" in h else ""
        print(f"{i}. {f['id']}  {f['name'] or '(unnamed)'}: {SK.people(f['people'])}, {f['place']}, "
              f"{f['population']:,} speakers{dist}")
        print("   " + summary(f))
        print("   " + " · ".join(f"{s['concept']} {s['roman']} /{s['ipa']}/" for s in h["samples"]))
        if explain and "contributions" in h:
            parts = sorted(h["contributions"].items(), key=lambda kv: -kv[1])
            print("   why: " + ", ".join(f"{k} {v:.2f}" for k, v in parts if v > 0.005))
        print()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("languages", nargs="?", help="path to a languages.json (e.g. runs/a24559/languages.json)")
    ap.add_argument("--where", action="append", default=[], help="feature filter, repeatable: 'consonants<=10', 'clicks'")
    ap.add_argument("--people", help="comma list of peoples; plurals and groups work (elves, dragons, giants)")
    ap.add_argument("--order", help="word order shorthand, e.g. VSO (same as --where word_order=VSO)")
    ap.add_argument("--like", help="rank by likeness to a reference profile (--list-profiles)")
    ap.add_argument("--sort", help="sort by a feature, descending; KEY:asc for ascending")
    ap.add_argument("--top", type=int, default=8, help="hits to show (default 8)")
    ap.add_argument("--explain", action="store_true", help="show each feature's share of the distance")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--list-profiles", action="store_true", help="list reference profiles and exit")
    ap.add_argument("--features", action="store_true", help="list feature keys (with an example lect) and exit")
    a = ap.parse_args(argv)
    profiles = load_profiles()
    if a.list_profiles:
        for k, p in profiles.items():
            print(f"{k:13s} {p['label']}: {p['consonants']}C {p['vowels']}V, {p['tones'] or 'no'} tones, "
                  f"{syllable_template(p['max_onset'], p['max_coda'])}, V-final {p['final_vowel_share']:.0%}, "
                  f"{p['mean_syllables']} syl/word; has {', '.join(p['series']) or 'none of the series'} "
                  f"({p['words']} words). Sources: {p['sources']}")
        return 0
    if not a.languages:
        ap.error("languages.json path required")
    doc, feats = load(a.languages)
    if a.features:
        ex = feats[0] if feats else {}
        for k, v in public(ex).items():
            print(f"{k:24s} {'number' if k in NUMERIC or k in SERIES else 'text':7s} e.g. {v}")
        return 0
    try:
        hits, n = run(doc, feats, a.where, a.people, a.order, a.like, a.sort, a.top, profiles)
    except KeyError as e:
        print(f"unknown key or profile: {e}; see --features / --list-profiles", file=sys.stderr)
        return 2
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps({"matched": n, "living": len(feats), "like": a.like,
                          "hits": [{**public(h["f"]), **{k: v for k, v in h.items() if k != "f"}} for h in hits]},
                         ensure_ascii=False, indent=1))
    else:
        print_hits(hits, n, len(feats), a.like, profiles, a.explain)
    return 0


if __name__ == "__main__":
    sys.exit(main())
