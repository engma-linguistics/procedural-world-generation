"""Build planet/language/data/token_frequency.tsv (PW-1623): how busy a phoneme of each token class is in words, from
NorthEuraLex 0.9 (Dellert et al. 2020, CC-BY 4.0; 107 languages x ~1,000 concepts, IPA).

    uv run python -I tools/language/token_priors.py path/to/northeuralex-0.9-forms.tsv
    (the file: http://www.sfs.uni-tuebingen.de/~jdellert/northeuralex/0.9/northeuralex-0.9-forms.tsv)

For each language: its phonemes are the segments its forms use (rawIPA read by percepts.from_ipa; one used under MIN_USES
times is dropped as noise), grouped by inventory.token_class. A class's relative busyness there is its share of the
language's tokens of that kind (consonant or vowel), per phoneme of the class, over the average phoneme of the kind
(1 / the number of phonemes of the kind): 1.0 = an average phoneme, 2.0 = twice as busy. The table keeps the median over
the languages that have the class (classes found in fewer than MIN_LANGS languages are left out, and the engine keeps
its PHOIBLE presence weight for them). The engine draws a phoneme by this number over sqrt(1 + its make cost)
(inventory._weights).
"""
from __future__ import annotations

import csv
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from planet.language import inventory as INV  # noqa: E402
from planet.language.percepts import from_ipa  # noqa: E402

OUT = INV.TOKEN_TSV
MIN_USES = 3
MIN_LANGS = 20  # (thin classes are mostly marginal there: ʔ in 17 languages, often a laryngeal coda, at 0.23)


def main(path: str) -> int:
    forms: dict[str, list[str]] = defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r.get("rawIPA"):
                forms[r["Language_ID"]].append(r["rawIPA"])
    rel: dict[str, list[float]] = defaultdict(list)
    bad = 0
    for lang, fs in forms.items():
        tok: Counter = Counter()
        for f in fs:
            try:
                segs = from_ipa(f.replace(" ", ""))
            except Exception:  # noqa: BLE001 (a form the percepts table cannot read is skipped)
                bad += 1
                continue
            tok.update(s for s in segs if s.kind in ("C", "V"))
        phon = {s: n for s, n in tok.items() if n >= MIN_USES}
        for kind in ("C", "V"):
            ks = {s: n for s, n in phon.items() if s.kind == kind}
            tot = sum(ks.values())
            if not ks or not tot:
                continue
            by: dict[str, list[int]] = defaultdict(list)
            for s, n in ks.items():
                by[INV.token_class(s)].append(n)
            for c, ns in by.items():
                rel[c].append((sum(ns) / tot) / len(ns) * len(ks))
    rows = sorted(((c, st.median(v), len(v)) for c, v in rel.items() if len(v) >= MIN_LANGS), key=lambda t: t[0])
    head = ("# Relative token frequency per phoneme, by inventory.token_class (PW-1623): the median over NorthEuraLex 0.9's\n"
            "# languages (Dellert et al. 2020, CC-BY 4.0) of a class's share of its kind's tokens, per phoneme of the class,\n"
            "# over the average phoneme of the kind (1.0 = average). Built by tools/language/token_priors.py; classes in\n"
            f"# fewer than {MIN_LANGS} languages left out. Eurasian sample: a lexical prior, not a world average.\n")
    OUT.write_text(head + "class\trelative\tlanguages\n" + "".join(f"{c}\t{v:.3f}\t{n}\n" for c, v, n in rows),
                   encoding="utf-8")
    print(f"{len(forms)} languages, {bad} forms unread; wrote {OUT} ({len(rows)} classes)")
    for c, v, n in sorted(rows, key=lambda t: -t[1]):
        print(f"  {c:22s} {v:5.2f}  ({n})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
