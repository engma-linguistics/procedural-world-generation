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

Column `initial` (PW-1686): how much busier a class is at the very start of a word than in words overall: per language,
its share of word-initial tokens of its kind over its share of all tokens of its kind; the median over the languages.
Word-initial position has its own profile (p x2.1, h x2.0, k x1.5, m x1.3 against l x0.6, n x0.55, r x0.3, ŋ 0 in the
sample): the engine multiplies a word's first sound's weight by it (inventory.initial_weights).
"""
from __future__ import annotations

import csv
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np  # noqa: E402

from planet.language import checks as CK  # noqa: E402
from planet.language import inventory as INV  # noqa: E402
from planet.language.percepts import from_ipa  # noqa: E402

OUT = INV.TOKEN_TSV
OUT_INITIAL = INV.DATA / "word_initial.tsv"   # (the word-start check's reference, checks.word_starts)
QS = (0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95)
MIN_USES = 3
MIN_LANGS = 20  # (thin classes are mostly marginal there: ʔ in 17 languages, often a laryngeal coda, at 0.23)


def main(path: str) -> int:
    forms: dict[str, list[str]] = defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r.get("rawIPA"):
                forms[r["Language_ID"]].append(r["rawIPA"])
    rel: dict[str, list[float]] = defaultdict(list)
    ini: dict[str, list[float]] = defaultdict(list)
    starts: dict[str, list[float]] = defaultdict(list)   # word-start group -> its share of the language's words
    bad = 0
    for lang, fs in forms.items():
        tok: Counter = Counter()
        first: Counter = Counter()
        grp: Counter = Counter()
        nw = 0
        for f in fs:
            try:
                segs = from_ipa(f.replace(" ", ""))
            except Exception:  # noqa: BLE001 (a form the percepts table cannot read is skipped)
                bad += 1
                continue
            segs = [s for s in segs if s.kind in ("C", "V")]
            tok.update(segs)
            if segs:
                first[segs[0]] += 1
                nw += 1
                grp.update(CK.start_groups(segs[0]))
        for g in CK.START_GROUPS:
            if nw:
                starts[g].append(grp[g] / nw)
        phon = {s: n for s, n in tok.items() if n >= MIN_USES}
        for kind in ("C", "V"):
            ks = {s: n for s, n in phon.items() if s.kind == kind}
            tot = sum(ks.values())
            if not ks or not tot:
                continue
            ftot = sum(first[s] for s in ks)
            by: dict[str, list[int]] = defaultdict(list)
            byf: Counter = Counter()
            for s, n in ks.items():
                by[INV.token_class(s)].append(n)
                byf[INV.token_class(s)] += first[s]
            for c, ns in by.items():
                rel[c].append((sum(ns) / tot) / len(ns) * len(ks))
                if ftot:
                    ini[c].append((byf[c] / ftot) / (sum(ns) / tot))
    rows = sorted(((c, st.median(v), len(v), st.median(ini[c])) for c, v in rel.items() if len(v) >= MIN_LANGS),
                  key=lambda t: t[0])
    head = ("# Relative token frequency per phoneme, by inventory.token_class (PW-1623): the median over NorthEuraLex 0.9's\n"
            "# languages (Dellert et al. 2020, CC-BY 4.0) of a class's share of its kind's tokens, per phoneme of the class,\n"
            "# over the average phoneme of the kind (1.0 = average). Built by tools/language/token_priors.py; classes in\n"
            f"# fewer than {MIN_LANGS} languages left out. Eurasian sample: a lexical prior, not a world average.\n"
            "# initial (PW-1686): the class's share of word-initial tokens of its kind over its share of all its kind's\n"
            "# tokens, median over the languages (word starts favour p h k m, disfavour l n r ŋ).\n")
    OUT.write_text(head + "class\trelative\tlanguages\tinitial\n"
                   + "".join(f"{c}\t{v:.3f}\t{n}\t{i:.3f}\n" for c, v, n, i in rows), encoding="utf-8")
    qs = {g: [float(x) for x in np.quantile(np.asarray(v, float), QS)] for g, v in starts.items()}
    OUT_INITIAL.write_text(
        "# Word-start groups (PW-1686, checks.word_starts): each group's share of a language's words that begin with it,\n"
        f"# quantiles {', '.join(f'p{round(q * 100)}' for q in QS)} over NorthEuraLex 0.9's {len(forms)} languages (Dellert et\n"
        "# al. 2020, CC-BY 4.0). Built by tools/language/token_priors.py. Eurasian sample.\n"
        "group\t" + "\t".join(f"p{round(q * 100)}" for q in QS) + "\n"
        + "".join(f"{g}\t" + "\t".join(f"{x:.4f}" for x in qs[g]) + "\n" for g in CK.START_GROUPS), encoding="utf-8")
    print(f"{len(forms)} languages, {bad} forms unread; wrote {OUT} ({len(rows)} classes) and {OUT_INITIAL}")
    for g in CK.START_GROUPS:
        print(f"  starts {g:7s} " + " ".join(f"{x:.3f}" for x in qs[g]))
    for c, v, n, i in sorted(rows, key=lambda t: -t[1]):
        print(f"  {c:22s} {v:5.2f}  initial x{i:4.2f}  ({n})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
