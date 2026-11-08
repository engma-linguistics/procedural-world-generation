"""Build the small derived language reference tables in planet/language/data/.

Reads the raw downloads under data/language/raw/<source>/ (untrusted data, read
only as CSV/TSV/GML text) and writes committed-size TSVs with '#' header lines.

    uv run python -I tools/language/build_reference_tables.py [--raw DIR] [--out DIR]

Sources and how each table is derived: docs/review/language/reference-data.md.
The knowledge-authored tables (grammaticalization_paths.tsv, sound_changes.tsv)
are hand-written and not produced here.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "tools/language/build_reference_tables.py"
TODAY = "2026-11-03"

csv.field_size_limit(sys.maxsize)

VERSIONS = {
    "phoible": "phoible/dev master @5f82b9c3 (2026-09-24), data/phoible.csv (PHOIBLE 2.0 plus later dev fixes)",
    "grambank": "Grambank v1.0.3 (git tag v1.0.3 of grambank/grambank, cldf/)",
    "wals": "WALS Online CLDF, cldf-datasets/wals master @81298aa2 (2026-09-28)",
    "clics": "CLICS3, clics/clics3 master @19b4051f (2023-05-10), clics3-network.gml.zip (graphs/network-3-families.gml)",
    "concepticon": "concepticon/concepticon-data master @1d53585c (2026-11-03), conceptlists/",
}


def write_tsv(path: Path, header_lines: list[str], columns: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        for line in header_lines:
            fh.write(f"# {line}\n" if line else "#\n")
        w = csv.writer(fh, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(columns)
        for r in rows:
            w.writerow(["" if v is None else v for v in r])
    print(f"wrote {path.relative_to(ROOT)}: {len(rows)} rows")


def common_header(source: str, url: str, licence: str, extra: list[str]) -> list[str]:
    return [
        f"source: {url}",
        f"version: {VERSIONS[source]}; derived {TODAY}",
        f"licence: {licence}",
        f"script: {SCRIPT}",
        *extra,
    ]


def fmt(x: float, nd: int = 4) -> str:
    return f"{x:.{nd}f}"


# ---------------------------------------------------------------- PHOIBLE


def build_phoible(raw: Path, out: Path) -> None:
    path = raw / "phoible" / "phoible.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        cols = reader.fieldnames
        feat_cols = cols[cols.index("tone"):]
        inv_rows: dict[int, list[dict]] = defaultdict(list)
        inv_glotto: dict[int, str] = {}
        for r in reader:
            iid = int(r["InventoryID"])
            inv_rows[iid].append(r)
            inv_glotto[iid] = r["Glottocode"]
    n_all = len(inv_rows)
    chosen: dict[str, int] = {}
    no_glotto = 0
    for iid in sorted(inv_rows):
        g = inv_glotto[iid]
        if not g or g == "NA":
            no_glotto += 1
            continue
        chosen.setdefault(g, iid)
    invs = [chosen[g] for g in sorted(chosen, key=lambda g: chosen[g])]
    n = len(invs)

    seg_count: Counter = Counter()
    seg_feats: dict[str, dict] = {}
    seg_class: dict[str, str] = {}
    sizes = []
    for iid in invs:
        seen = set()
        c = v = t = 0
        for r in inv_rows[iid]:
            ph = r["Phoneme"]
            if ph in seen:
                continue
            seen.add(ph)
            cls = r["SegmentClass"]
            c += cls == "consonant"
            v += cls == "vowel"
            t += cls == "tone"
            seg_count[ph] += 1
            if ph not in seg_feats:
                seg_feats[ph] = {k: r[k] for k in feat_cols}
                seg_class[ph] = cls
        sizes.append((c, v, t, len(seen)))

    min_count = math.ceil(0.002 * n)
    kept = [s for s in seg_count if seg_count[s] >= min_count]
    tail = [s for s in seg_count if seg_count[s] < min_count]
    tail_by_class = Counter(seg_class[s] for s in tail)
    tail_mass = sum(seg_count[s] for s in tail)
    kept.sort(key=lambda s: (-seg_count[s], s))
    rows = [[s, seg_class[s], seg_count[s], fmt(seg_count[s] / n, 5)] + [seg_feats[s][k] for k in feat_cols] for s in kept]
    hdr = common_header(
        "phoible", "https://github.com/phoible/dev (data/phoible.csv); https://phoible.org",
        "CC-BY-SA 3.0 (PHOIBLE: Moran & McCloy eds. 2019, PHOIBLE 2.0, Max Planck Institute for the Science of Human History). "
        "This derived table is shared under the same licence.",
        [
            f"inventories: {n_all} in source; {no_glotto} without a Glottocode dropped; deduplicated to one inventory per Glottocode "
            f"(the lowest InventoryID, i.e. the first listed) -> n = {n} languages.",
            "frequency = fraction of those n inventories that contain the segment (marginal segments counted as present).",
            f"tail: segments in < 0.2% of inventories (< {min_count} inventories) are omitted: {len(tail)} segments "
            f"({dict(tail_by_class)}), together {tail_mass} segment-inventory occurrences; treat as an 'other' bucket.",
            "features: PHOIBLE distinctive-feature columns verbatim from the first occurrence of the segment "
            "(+ / - / 0 = not applicable; comma lists like '+,-' mark contour segments).",
            "class: PHOIBLE SegmentClass (consonant | vowel | tone).",
        ],
    )
    write_tsv(out / "phoible_segments.tsv", hdr, ["segment", "class", "n_inventories", "frequency"] + feat_cols, rows)

    # inventory sizes
    def summary(vals):
        q = statistics.quantiles(vals, n=4, method="inclusive")
        return (fmt(statistics.fmean(vals), 2), statistics.median(vals), q[0], q[2], min(vals), max(vals))

    srows = []
    names = ["consonants", "vowels", "tones", "total"]
    for i, name in enumerate(names):
        vals = [s[i] for s in sizes]
        mean, med, q1, q3, lo, hi = summary(vals)
        for key, val in [("mean", mean), ("median", med), ("q1", q1), ("q3", q3), ("min", lo), ("max", hi)]:
            srows.append([name, "stat", key, val, ""])
        cnt = Counter(vals)
        for size in sorted(cnt):
            srows.append([name, "count", size, cnt[size], fmt(cnt[size] / n, 5)])
    hdr = common_header(
        "phoible", "https://github.com/phoible/dev (data/phoible.csv); https://phoible.org",
        "CC-BY-SA 3.0 (PHOIBLE 2.0); this derived table shares that licence.",
        [
            f"n = {n} inventories, one per Glottocode (first InventoryID), inventories without Glottocode dropped.",
            "sizes count distinct phonemes per inventory by SegmentClass, marginal phonemes included; total = consonants + vowels + tones.",
            "rows: kind=stat gives mean/median/q1/q3/min/max (quartiles: inclusive method); kind=count gives the number of "
            "inventories with exactly that size and the fraction of n.",
        ],
    )
    write_tsv(out / "phoible_inventory_sizes.tsv", hdr, ["measure", "kind", "key", "value", "fraction"], srows)


# ---------------------------------------------------------------- Grambank

GB_STRUCTURAL = [
    # word order
    "GB130", "GB131", "GB132", "GB133", "GB136", "GB024", "GB025", "GB065", "GB193", "GB327", "GB328",
    "GB074", "GB075", "GB421", "GB422", "GB262", "GB263",
    # articles
    "GB020", "GB022", "GB023",
    # case and alignment
    "GB070", "GB071", "GB072", "GB408", "GB409", "GB410",
    # gender / noun class / classifiers
    "GB030", "GB051", "GB053", "GB170", "GB171", "GB057",
    # number
    "GB044", "GB043", "GB318",
    # TAM
    "GB082", "GB083", "GB084", "GB086", "GB121", "GB521",
    # indexing / polysynthesis-ish
    "GB089", "GB090", "GB091", "GB092", "GB093", "GB094", "GB079", "GB080", "GB124", "GB107", "GB155",
]


def grambank_data(raw: Path):
    d = raw / "grambank"
    params = {r["ID"]: r for r in csv.DictReader((d / "parameters.csv").open(encoding="utf-8"))}
    codes = defaultdict(dict)
    for r in csv.DictReader((d / "codes.csv").open(encoding="utf-8")):
        codes[r["Parameter_ID"]][r["Name"]] = r["Description"]
    langs = {r["ID"]: r for r in csv.DictReader((d / "languages.csv").open(encoding="utf-8"))}
    # one languoid per Language_level_ID; prefer the 'language' row, else the first dialect by ID
    by_lang: dict[str, str] = {}
    for lid in sorted(langs):
        r = langs[lid]
        if r["level"] not in ("language", "dialect"):
            continue
        key = r["Language_level_ID"] or lid
        if key not in by_lang or (r["level"] == "language" and langs[by_lang[key]]["level"] != "language"):
            by_lang[key] = lid
    keep = set(by_lang.values())
    fam = {lid: (langs[lid]["Family_level_ID"] or f"isolate:{langs[lid]['Language_level_ID'] or lid}") for lid in keep}
    vals: dict[str, dict[str, str]] = defaultdict(dict)
    for r in csv.DictReader((d / "values.csv").open(encoding="utf-8")):
        if r["Language_ID"] in keep:
            vals[r["Parameter_ID"]][r["Language_ID"]] = r["Value"]
    return params, codes, langs, keep, fam, vals


GB_VMIN = 0.40


def build_grambank(raw: Path, out: Path) -> None:
    params, codes, langs, keep, fam, vals = grambank_data(raw)
    rows = []
    for pid in sorted(params):
        p = params[pid]
        short = p["Grambank_ID_desc"].split(" ", 1)[1] if " " in p["Grambank_ID_desc"] else p["Grambank_ID_desc"]
        v = vals[pid]
        coded = {l: x for l, x in v.items() if x != "?"}
        n_q = sum(1 for x in v.values() if x == "?")
        n = len(coded)
        cnt = Counter(coded.values())
        famsize = Counter(fam[l] for l in coded)
        fw = Counter()
        for l, x in coded.items():
            fw[x] += 1.0 / famsize[fam[l]]
        nfam = len(famsize)
        for code in sorted(codes[pid]):
            rows.append([
                pid, short, p["Name"], code, codes[pid][code], n, n_q, cnt.get(code, 0),
                fmt(cnt.get(code, 0) / n if n else 0), fmt(fw.get(code, 0) / nfam if nfam else 0),
            ])
    hdr = common_header(
        "grambank", "https://github.com/grambank/grambank (tag v1.0.3, cldf/); https://grambank.clld.org; Zenodo doi:10.5281/zenodo.7740139",
        "CC-BY 4.0 (Skirgard et al. 2023, Grambank v1.0, Science Advances 9; dataset by the Grambank consortium).",
        [
            f"languages: {len(keep)} languoids after keeping one per Language_level_ID (the 'language' row where present, "
            "else the first dialect); family-level rows dropped.",
            "n_coded = languages with a value other than '?'; n_unknown = languages coded '?'; frequency = count / n_coded.",
            "freq_family_weighted: each Glottolog top-level family (isolates = own family) gets total weight 1 split evenly "
            "over its coded languages; use it for genealogically balanced draws.",
            "value_coding: Grambank codes.csv description. Binary features: 0 absent, 1 present. Multistate order features "
            "(GB024, GB025, GB065, GB130, GB193, GB203): 1/2/3 as described, 3 = both orders.",
        ],
    )
    write_tsv(out / "grambank_features.tsv", hdr,
              ["feature_id", "short_name", "question", "value", "value_coding", "n_coded", "n_unknown", "count",
               "frequency", "freq_family_weighted"], rows)

    # correlations among structural features
    feats = [f for f in GB_STRUCTURAL if f in params]
    coded = {f: {l: x for l, x in vals[f].items() if x != "?"} for f in feats}
    pairs = []
    for f1, f2 in itertools.combinations(feats, 2):
        common = coded[f1].keys() & coded[f2].keys()
        if len(common) < 100:
            continue
        tab = Counter((coded[f1][l], coded[f2][l]) for l in common)
        a = Counter(coded[f1][l] for l in common)
        b = Counter(coded[f2][l] for l in common)
        nn = len(common)
        chi2 = sum((tab.get((x, y), 0) - a[x] * b[y] / nn) ** 2 / (a[x] * b[y] / nn) for x in a for y in b)
        k = min(len(a), len(b)) - 1
        cv = math.sqrt(chi2 / (nn * k)) if k > 0 else 0.0
        pairs.append((cv, f1, f2, nn, tab, a, b))
    pairs.sort(key=lambda t: -t[0])
    VMIN = GB_VMIN
    strong = [p for p in pairs if p[0] >= VMIN]
    short = {f: params[f]["Grambank_ID_desc"].split(" ", 1)[-1] for f in feats}
    crow = []
    for cv, f1, f2, nn, tab, a, b in strong:
        for src, dst, sa, sb, flip in ((f1, f2, a, b, False), (f2, f1, b, a, True)):
            for x in sorted(sa):
                for y in sorted(sb):
                    c = tab.get((y, x) if flip else (x, y), 0)
                    p_cond = c / sa[x]
                    p_marg = sb[y] / nn
                    crow.append([src, short[src], x, dst, short[dst], y, sa[x], c, fmt(p_cond), fmt(p_marg),
                                 fmt(p_cond / p_marg if p_marg else 0, 3), fmt(cv, 3)])
    hdr = common_header(
        "grambank", "https://github.com/grambank/grambank (tag v1.0.3, cldf/)",
        "CC-BY 4.0 (Grambank v1.0, Skirgard et al. 2023).",
        [
            f"features considered ({len(feats)}): {' '.join(feats)}",
            "(word order, adpositions, possessor-noun, adjective-noun, articles, case, alignment, gender/noun class, "
            "classifiers, number, TAM, argument indexing / affixation / incorporation).",
            f"for every unordered pair coded ('?' excluded) in >= 100 common languages, Cramer's V of the cross-tab; pairs with "
            f"V >= {VMIN} kept ({len(strong)} of {len(pairs)} pairs; rerun with --gb-vmin 0.3 for ~100 pairs). Each kept pair is written in both directions with the full "
            "conditional distribution, so for a given (f1, v1) the p_cond over v2 sums to 1.",
            "columns: n_given = languages with f1=v1 (and f2 coded); count = those with f2=v2; p_cond = P(f2=v2 | f1=v1); "
            "p_marginal = P(f2=v2) on the same common languages; lift = p_cond / p_marginal.",
            "raw language counts, NOT family-balanced: big families (Austronesian, Atlantic-Congo) inflate some associations.",
        ],
    )
    write_tsv(out / "grambank_correlations.tsv", hdr,
              ["f1", "f1_short", "v1", "f2", "f2_short", "v2", "n_given", "count", "p_cond", "p_marginal", "lift",
               "cramers_v"], crow)


# ---------------------------------------------------------------- WALS

WALS_FEATS = ["81A", "85A", "86A", "87A", "88A", "90A"]


def build_wals(raw: Path, out: Path) -> None:
    d = raw / "wals"
    params = {r["ID"]: r["Name"] for r in csv.DictReader((d / "parameters.csv").open(encoding="utf-8"))}
    codes = {r["ID"]: r["Name"] for r in csv.DictReader((d / "codes.csv").open(encoding="utf-8"))}
    vals: dict[str, dict[str, str]] = defaultdict(dict)
    for r in csv.DictReader((d / "values.csv").open(encoding="utf-8")):
        if r["Parameter_ID"] in WALS_FEATS:
            vals[r["Parameter_ID"]][r["Language_ID"]] = r["Code_ID"]
    rows = []
    for f in WALS_FEATS:
        cnt = Counter(vals[f].values())
        n = sum(cnt.values())
        for cid in sorted(cnt, key=lambda c: int(c.split("-")[1])):
            rows.append(["freq", f, params[f], cid.split("-")[1], codes[cid], "", "", "", "", cnt[cid], fmt(cnt[cid] / n), n])
    for f2 in WALS_FEATS[1:]:
        common = vals["81A"].keys() & vals[f2].keys()
        tab = Counter((vals["81A"][l], vals[f2][l]) for l in common)
        rowtot = Counter(vals["81A"][l] for l in common)
        for c1 in sorted(rowtot, key=lambda c: int(c.split("-")[1])):
            for c2 in sorted({c for _, c in tab}, key=lambda c: int(c.split("-")[1])):
                k = tab.get((c1, c2), 0)
                rows.append(["crosstab", "81A", params["81A"], c1.split("-")[1], codes[c1], f2, params[f2],
                             c2.split("-")[1], codes[c2], k, fmt(k / rowtot[c1]), rowtot[c1]])
    hdr = common_header(
        "wals", "https://github.com/cldf-datasets/wals (cldf/); https://wals.info",
        "CC-BY 4.0 (Dryer & Haspelmath eds. 2013, WALS Online v2020.x).",
        [
            "features: 81A order of S,O,V; 85A adposition-NP; 86A genitive-noun; 87A adjective-noun; 88A demonstrative-noun; "
            "90A relative clause-noun.",
            "table=freq: value frequency over WALS languages coded for that feature (count / n). Raw languages, not genus-balanced "
            "(Dryer's own counts balance by genus; these do not).",
            "table=crosstab: 81A value (rows) vs feature2 value; count = languages coded for both; fraction = count / n "
            "(n = languages with that 81A value coded for feature2), i.e. P(feature2 value | 81A value). The task asked for "
            "85A and 86A; 87A, 88A, 90A are included as well since they are the same size.",
        ],
    )
    write_tsv(out / "wals_wordorder.tsv", hdr,
              ["table", "feature", "feature_name", "value", "value_name", "feature2", "feature2_name", "value2",
               "value2_name", "count", "fraction", "n"], rows)


# ---------------------------------------------------------------- CLICS


def parse_gml(path: Path):
    """Minimal line-based reader for the CLICS3 GML: yields ('node'|'edge', {key: value})."""
    kind = None
    attrs: dict[str, str] = {}
    pat = re.compile(r'^\s+(\w+)\s+(?:"(.*)"|(\S+))\s*$')
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s in ("node [", "edge ["):
                kind, attrs = s.split()[0], {}
                continue
            if s == "]" and kind:
                yield kind, attrs
                kind = None
                continue
            if kind:
                m = pat.match(line)
                if m:
                    k = m.group(1)
                    if k in ("Words", "words", "wofam", "languages"):
                        attrs[k] = m.group(2) or ""
                        continue
                    attrs[k] = m.group(2) if m.group(2) is not None else m.group(3)


def build_clics(raw: Path, out: Path) -> None:
    path = raw / "clics3" / "extract" / "graphs" / "network-3-families.gml"
    nodes = {}
    edges = []
    for kind, a in parse_gml(path):
        if kind == "node":
            nodes[a["id"]] = (a["ID"], a["Gloss"], a.get("Semanticfield", ""))
        else:
            fams = int(a["FamilyWeight"])
            if fams >= 3:
                edges.append((a["source"], a["target"], fams, int(a["LanguageWeight"]), int(a["WordWeight"]),
                              a.get("families", "")))
    rows = []
    for s, t, fams, langs, words, famlist in edges:
        (ia, ga, sa), (ib, gb, sb) = nodes[s], nodes[t]
        if ga > gb:
            (ia, ga, sa), (ib, gb, sb) = (ib, gb, sb), (ia, ga, sa)
        rows.append([ia, ga, ib, gb, fams, langs, words, sa, sb])
    rows.sort(key=lambda r: (-r[4], -r[5], r[1], r[3]))
    hdr = common_header(
        "clics", "https://github.com/clics/clics3 (clics3-network.gml.zip); https://clics.clld.org",
        "CC-BY 4.0 (Rzymski, Tresoldi et al. 2020, The Database of Cross-Linguistic Colexifications, Scientific Data 7:13).",
        [
            "the CLICS3 colexification network as published (graphs/network-3-families.gml): undirected edges between "
            "Concepticon concepts colexified (same word form) in languages of the 30 CLICS3 lexibank datasets.",
            f"kept: edges with FamilyWeight >= 3 (attested in >= 3 Glottolog families): {len(rows)} edges over "
            f"{len(nodes)} concepts. Concept A is the alphabetically first gloss.",
            "columns: families = FamilyWeight, languages = LanguageWeight, words = WordWeight (number of colexifying word pairs).",
        ],
    )
    write_tsv(out / "clics_edges.tsv", hdr,
              ["concept_a_id", "concept_a", "concept_b_id", "concept_b", "families", "languages", "words",
               "semantic_field_a", "semantic_field_b"], rows)


# ---------------------------------------------------------------- concepts


def read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# Swadesh-only concepts with no Pagel/Holman/LJ value: class assigned from general knowledge
# of their replacement behaviour (not from data); marked stability_class_source=knowledge.
KNOWLEDGE_CLASS = {"904": 4, "2106": 3, "2272": 4}  # BERRY, MALE PERSON, HOT OR WARM

# WOLD extension (2026-11-07, round 5): everyday meanings a grammar sketch and sample sentences need, picked from the
# 1460 meanings of the World Loanword Database (Haspelmath & Tadmor 2009, Concepticon list Haspelmath-2009-1460), with
# WOLD's part of speech and composite rank (age, borrowing and simplicity scores; the ranking behind the Leipzig-Jakarta
# list). Selection by the language lane: motion and daily verbs, kin terms, numbers, function words, body, house and tools.
WOLD_EXTENSION: dict[str, tuple[str, ...]] = {
    "motion": (
        "ARRIVE", "ENTER", "LEAVE", "RETURN HOME", "CLIMB", "JUMP", "RISE (MOVE UPWARDS)", "SINK (DESCEND)",
        "APPROACH", "FOLLOW", "SEND", "BRING", "LEAD (GUIDE)", "RIDE", "ROW", "SAIL", "DWELL (LIVE, RESIDE)", "MEET",
        "GATHER", "LIFT", "DROP (SOMETHING)", "PUT", "HANG UP", "KNEEL", "LIE DOWN", "REST", "STRETCH", "SPREAD OUT",
        "BEND", "FOLD",
    ),
    "doing and making": (
        "DO", "MAKE", "BE", "BECOME", "GET", "KEEP", "SEIZE", "CATCH", "FIND", "LOOK FOR", "OPEN", "SHUT", "COVER",
        "HIDE (CONCEAL)", "BUILD", "BREAK (DESTROY OR GET DESTROYED)", "TEAR (SHRED)", "POUR", "PLANT (SOMETHING)",
        "WEAVE", "CARVE", "BAKE", "ROAST OR FRY", "KNEAD", "POUND", "CHEW", "LICK", "BATHE", "BURY",
        "LIGHT (IGNITE)", "EXTINGUISH", "BURN (SOMETHING)", "SHINE", "SHOOT", "CUT DOWN", "GROW", "CHANGE", "REMAIN",
        "DIVIDE", "JOIN", "BEGIN", "FINISH", "HELP", "WORK (LABOUR)", "BE BORN", "COUGH", "MISS (A TARGET)",
        "THRESH", "DYE", "TAN", "SCRAPE",
    ),
    "exchange and society": (
        "BUY", "SELL", "PAY", "BORROW", "LEND", "STEAL", "TRADE OR BARTER", "EARN", "RULE", "MARRY", "PRAY", "DANCE",
        "SHOUT", "WHISPER", "CALL", "TELL", "SHOW", "ASK (INQUIRE)", "ASK (REQUEST)", "ANSWER", "TEACH", "LEARN",
        "UNDERSTAND", "FORGET", "LISTEN", "LOOK", "WANT", "LOVE", "HATE", "CHOOSE", "DARE", "SCOLD",
    ),
    "qualities": (
        "DARK", "DEAD", "TALL", "HIGH", "LOW", "DEEP", "SHALLOW", "FLAT", "CROOKED", "EMPTY", "SOFT",
        "LIGHT (WEIGHT)", "STRONG", "WEAK", "YOUNG", "BEAUTIFUL", "UGLY", "HEALTHY", "SICK", "TIRED", "HAPPY",
        "DEAF", "BLIND", "RIPE", "RAW", "COOKED", "RICH", "POOR", "CLEVER", "DIFFICULT", "EASY", "TRUE", "WRONG",
        "HOLY", "CALM", "READY",
    ),
    "kin and people": (
        "SIBLING", "OLDER BROTHER", "YOUNGER BROTHER", "OLDER SIBLING", "YOUNGER SIBLING", "GRANDSON",
        "GRANDDAUGHTER", "GRANDCHILD", "NEPHEW", "NIECE", "COUSIN", "WIDOW", "WIDOWER", "ORPHAN", "PARENTS",
        "FAMILY", "FATHER-IN-LAW (OF MAN)", "MOTHER-IN-LAW (OF MAN)", "SON-IN-LAW (OF MAN)",
        "DAUGHTER-IN-LAW (OF MAN)", "YOUNG MAN", "YOUNG WOMAN", "MASTER", "SERVANT", "SLAVE", "KING", "SOLDIER",
        "MERCHANT", "TEACHER", "THIEF", "NEIGHBOUR", "WEDDING",
    ),
    "numbers and function words": (
        "TWENTY", "HUNDRED", "THOUSAND", "FIRST", "SECOND", "HALF", "PAIR", "SHE", "IT", "THROUGH", "NOTHING",
        "TODAY", "TOMORROW", "NOW", "BEFORE", "AFTER", "BEHIND", "UP", "DOWN", "WITHOUT", "NO", "YES", "HOW MUCH",
    ),
    "body": (
        "SHOULDER", "LIP", "RIB", "LUNG", "THROAT", "KIDNEY", "STOMACH", "INTESTINES", "CHIN", "FOREHEAD", "CHEEK",
        "JAW", "FACE", "HIP", "WAIST", "BODY", "PALM OF HAND", "FINGER", "TOE", "BRAIN", "BEAK", "FINGERNAIL",
        "PAIN", "POISON", "MEDICINE", "SOUL", "MIND", "VOICE",
    ),
    "nature and time": (
        "AIR", "LIGHT (RADIATION)", "DARKNESS", "DEW", "MUD", "RAINBOW", "FOAM", "STEAM", "SHORE", "FLAME",
        "PRECIPICE", "CLAY", "THUNDER", "BOLT (OF LIGHTNING)", "WORLD", "WAVE", "TIDE", "MONTH", "DAY (24 HOURS)",
        "SUMMER", "WINTER", "AUTUMN", "MORNING", "EVENING", "AFTERNOON", "TIME",
    ),
    "animals and food": (
        "SHEEP", "PIG", "OX", "BULL", "RABBIT", "HEN", "ROOSTER", "GOOSE", "DUCK", "DOVE", "EAGLE", "CROW", "FOX",
        "FROG", "SNAIL", "SPIDER", "FLEA", "BEE", "INSECT", "NEST", "WOOL", "FUR", "SCALE", "MEAT", "FLOUR",
        "BUTTER", "BEVERAGE", "SOUP", "GRAIN", "FIREWOOD",
    ),
    "house, tools, places": (
        "DOOR", "ROOF", "WALL (OF HOUSE)", "WINDOW", "FENCE", "TABLE", "CHAIR", "POT", "BOWL", "JUG", "BASKET",
        "MORTAR", "BROOM", "MAT", "PILLOW", "THREAD", "CLOTHES", "SHIRT", "SHOE", "BELT", "RING", "LEATHER", "BOW",
        "ARROW", "SHIELD", "HAMMER", "BOAT", "RAFT", "PADDLE", "BRIDGE", "PATH", "FIELD", "FURROW", "WHEEL", "CART",
        "TRAP (PITFALL)", "MARKET", "COUNTRY", "PLACE (POSITION)", "PART", "PIECE", "MIDDLE", "TOP", "EDGE",
        "END (OF SPACE)", "PEACE", "FEAR (FRIGHT)", "ANGER", "OMEN", "SACRIFICE", "DEMON",
    ),
}
WOLD_POS = {"Noun": "N", "Verb": "V", "Adjective": "A", "Adverb": "A", "Function word": "FUNC"}
# numerals stand as nouns like the Swadesh ONE..FIVE rows (pos N), not as function words
WOLD_POS_BY_GLOSS = {"TWENTY": "N", "HUNDRED": "N", "THOUSAND": "N"}


def build_concepts(raw: Path, out: Path) -> None:
    d = raw / "concepticon"
    conc = {r["ID"]: r for r in read_tsv(d / "concepticon.tsv")}
    lj = {r["CONCEPTICON_ID"]: r for r in read_tsv(d / "Tadmor-2009-100.tsv") if r["CONCEPTICON_ID"]}
    sw200 = {r["CONCEPTICON_ID"]: r for r in read_tsv(d / "Swadesh-1952-200.tsv") if r["CONCEPTICON_ID"]}
    sw100 = {r["CONCEPTICON_ID"]: r for r in read_tsv(d / "Swadesh-1955-100.tsv") if r["CONCEPTICON_ID"]}
    pagel = {r["CONCEPTICON_ID"]: r for r in read_tsv(d / "Pagel-2007-200.tsv") if r["CONCEPTICON_ID"]}
    holman = {r["CONCEPTICON_ID"]: r for r in read_tsv(d / "Holman-2008-100.tsv") if r["CONCEPTICON_ID"]}
    sw207 = set(sw200) | set(sw100)
    ids = sorted(set(lj) | sw207, key=int)

    # stability class 1 (most stable / slowest) .. 5 (least stable / fastest)
    def quint(values: dict[str, float], reverse: bool) -> dict[str, int]:
        order = sorted(values, key=lambda k: values[k], reverse=reverse)
        return {k: 1 + (5 * i) // len(order) for i, k in enumerate(order)}

    pq = quint({k: float(v["MEAN_RATE"]) for k, v in pagel.items() if v["MEAN_RATE"]}, reverse=False)
    hq = quint({k: float(v["STABILITY_SCORE"]) for k, v in holman.items() if v["STABILITY_SCORE"]}, reverse=True)
    ljq = {k: 1 + (5 * (int(v["RANK"]) - 1)) // 100 for k, v in lj.items() if v.get("RANK")}
    rows = []
    for cid in ids:
        gloss = conc.get(cid, {}).get("GLOSS") or (lj.get(cid) or sw200.get(cid) or sw100.get(cid))["CONCEPTICON_GLOSS"]
        lists = []
        if cid in lj:
            lists.append("LJ100")
        if cid in sw207:
            lists.append("SW207")
        if cid in sw200:
            lists.append("SW200")
        if cid in sw100:
            lists.append("SW100")
        p, h = pagel.get(cid), holman.get(cid)
        if cid in pq:
            cls, src = pq[cid], "pagel2007_rate_quintile"
        elif cid in hq:
            cls, src = hq[cid], "holman2008_stability_quintile"
        elif cid in ljq:
            cls, src = ljq[cid], "lj_rank_quintile"
        elif cid in KNOWLEDGE_CLASS:
            cls, src = KNOWLEDGE_CLASS[cid], "knowledge"
        else:
            cls, src = "", ""
        rows.append([
            cid, gloss, conc.get(cid, {}).get("SEMANTICFIELD", ""), ",".join(lists),
            lj[cid]["RANK"] if cid in lj else "",
            p["MEAN_RATE"] if p else "", p["ENGLISH_FREQUENCY"] if p else "",
            h["RANK"] if h else "", h["STABILITY_SCORE"] if h else "", cls, src,
        ])
    for r in rows:
        r.append("")   # (pos: the core rows' parts of speech are lexicon.py's lists)
    rows += wold_rows(raw, conc, {r[0] for r in rows})
    missing = [r for r in rows if not r[9]]
    hdr = [
        "source: Concepticon conceptlists (https://github.com/concepticon/concepticon-data, concepticondata/conceptlists/): "
        "Tadmor-2009-100 (Leipzig-Jakarta list, Tadmor, Haspelmath & Taylor 2010), Swadesh-1952-200, Swadesh-1955-100, "
        "Pagel-2007-200 (Pagel, Atkinson & Meade 2007, Nature 449), Holman-2008-100 (Holman et al. 2008, ASJP stability).",
        f"version: {VERSIONS['concepticon']}; derived {TODAY}",
        "licence: Concepticon data CC-BY 4.0 (List et al., Concepticon 3.x); underlying list values from the cited papers.",
        f"script: {SCRIPT}",
        "lists: LJ100 = Leipzig-Jakarta 100; SW207 = Swadesh 207, built as the union of Swadesh 1952 (200) and Swadesh 1955 (100) "
        f"by Concepticon id ({len(sw207)} concepts after mapping; the Wikipedia '207' list is this union); SW200 / SW100 mark the source list.",
        "lj_rank: Leipzig-Jakarta rank (1 = most borrowing-resistant/stable). pagel_rate: Pagel 2007 mean rate of lexical replacement "
        "in Indo-European (replacements per 10,000 yr, low = stable); pagel_english_freq: their English usage frequency per million.",
        "holman_rank / holman_stability: ASJP stability rank and score (Holman et al. 2008, 100 items; rank 1 = most stable).",
        "stability_class: 1 (most stable, slowest replacement) .. 5 (fastest). Derived, not published: quintile of the Pagel rate "
        "among the 200 Pagel concepts where available, else quintile of Holman stability among its 100, else quintile of the LJ rank, else (3 concepts: BERRY, MALE PERSON, HOT OR WARM) "
        f"a class from general knowledge, marked 'knowledge'. Concepts with no class: {len(missing)}.",
        "WOLD1460 rows (2026-11-07): meanings of the World Loanword Database (Haspelmath & Tadmor 2009; Concepticon list "
        "Haspelmath-2009-1460, CC-BY 4.0) picked for sample sentences and grammar sketches (WOLD_EXTENSION in the script); "
        "stability_class 3-5 by tercile of WOLD's composite rank among them (wold_rank_tercile), pos from WOLD's part of speech.",
    ]
    write_tsv(out / "concepts.tsv", hdr,
              ["concepticon_id", "gloss", "semantic_field", "lists", "lj_rank", "pagel_rate", "pagel_english_freq",
               "holman_rank", "holman_stability", "stability_class", "stability_class_source", "pos"], rows)


def wold_rows(raw: Path, conc: dict, have: set) -> list[list]:
    """The WOLD_EXTENSION meanings as concepts.tsv rows (those not already on the core lists)."""
    w = {r["CONCEPTICON_GLOSS"]: r for r in read_tsv(raw / "wold" / "Haspelmath-2009-1460.tsv") if r["CONCEPTICON_ID"]}
    pick = []
    for xs in WOLD_EXTENSION.values():
        for g in xs:
            r = w[g]
            if r["CONCEPTICON_ID"] not in have and r["CONCEPTICON_ID"] not in {x["CONCEPTICON_ID"] for x in pick}:
                pick.append(r)
    order = sorted(pick, key=lambda r: int(r["RANK"]))
    cls = {r["CONCEPTICON_ID"]: 3 + (3 * i) // len(order) for i, r in enumerate(order)}
    out = []
    for r in sorted(pick, key=lambda r: int(r["CONCEPTICON_ID"])):
        cid = r["CONCEPTICON_ID"]
        out.append([cid, r["CONCEPTICON_GLOSS"], conc.get(cid, {}).get("SEMANTICFIELD", ""), "WOLD1460", "", "", "", "", "",
                    cls[cid], "wold_rank_tercile", WOLD_POS_BY_GLOSS.get(r["CONCEPTICON_GLOSS"], WOLD_POS[r["PART_OF_SPEECH"]])])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=ROOT / "data" / "language" / "raw")
    ap.add_argument("--out", type=Path, default=ROOT / "planet" / "language" / "data")
    ap.add_argument("--gb-vmin", type=float, default=GB_VMIN)
    ap.add_argument("--only", nargs="*", default=["phoible", "grambank", "wals", "clics", "concepts"])
    a = ap.parse_args()
    globals()["GB_VMIN"] = a.gb_vmin
    for name in a.only:
        globals()[f"build_{name}"](a.raw, a.out)


if __name__ == "__main__":
    main()
