"""Recompute the scholars' horizon from a stored languages.json with the current families code (calibration without re-running
the pass; docs/review/language/calibration.md). Two measures:

- pairs (the old one, families.horizon_pairs): per-pair blind share by edit distance against the pair's own shuffled chance
  level, 1-kyr bins, for several COGNATE_DIST and MIN_EXCESS values;
- splits (families.horizon): splits of the true tree recovered as clades of the scholars' UPGMA under the strict
  (recurring-correspondence) cognate test, 2-kyr windows; with the sisters / cross-family shares loose, strict and true.

    uv run python -I tools/language/horizon_offline.py runs/a24559/languages.json [--pairs 0.45 0.05] [--excess 0.02,0.03,0.05]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from planet.language import families as FA, lexicon as LX  # noqa: E402
from planet.language.percepts import from_ipa  # noqa: E402


def pairs_measure(doc, cds, excesses):
    class L:
        pass
    by = {}
    for x in doc["lects"]:
        l = L()
        l.id, l.parent, l.born_kyr, l.died_kyr, l.deme, l.people = x["id"], x["parent"], x["born_kyr"], x["died_kyr"], x["deme"], x["people"]
        l.forms = {c: tuple(from_ipa(w["ipa"])) for c, w in x["lexicon"].items() if c in LX.CORE100}
        by[l.id] = l
    living = [l for l in by.values() if l.died_kyr is None and l.deme is not None]
    core = sorted(LX.CORE100)
    T = FA.divergence_matrix(living, by)
    keep = FA.COGNATE_DIST, FA.MIN_EXCESS
    for cd in cds:
        FA.COGNATE_DIST = cd
        tab = FA.WordTable(living, core, lambda l, c: l.forms.get(c))
        S = tab.share_matrix(blind=True)
        for me in excesses:
            FA.MIN_EXCESS = me
            iu = np.triu_indices(len(living), 1)
            hum = np.array([living[i].people == "human" and living[j].people == "human" for i, j in zip(*iu)])
            hz = FA.horizon_pairs(tab, T, S, S, (iu[0][hum], iu[1][hum]), np.random.default_rng(1))
            ha = FA.horizon_pairs(tab, T, S, S, iu, np.random.default_rng(2))
            sib = np.isfinite(T[iu]) & (T[iu] <= 2)
            print(f"pairs  cd {cd} excess {me}: human {hz['horizon_kyr']} all {ha['horizon_kyr']} chance {hz.get('chance_mean')} "
                  f"sib {S[iu][sib].mean():.3f}", [(b["from_kyr"], b["pairs"], b["above_chance"]) for b in hz["bins"]])
    FA.COGNATE_DIST, FA.MIN_EXCESS = keep


def splits_measure(doc, excesses, out_json=None):
    res = {}
    for ex in excesses:
        FA.SPLIT_EXCESS = ex
        h = FA.horizon(doc)
        res[ex] = h
        print(f"\nsplits SPLIT_EXCESS {ex}: human {h['horizon_kyr']} kyr, all {h['by']['all']['horizon_kyr']} kyr "
              f"({h['by']['human']['splits']} human splits, {h['by']['all']['splits']} all)")
        print(f"  sisters <= 2 kyr ({h['sisters']['pairs']} pairs): loose {h['sisters']['loose']} strict {h['sisters']['strict']} "
              f"true {h['sisters']['true']}; cross-family: loose {h['cross_family']['loose']} strict {h['cross_family']['strict']}")
        for name in ("human", "all"):
            print(f"  {name}: window | splits (big) | scored | recovered | all splits recovered | mean strict share")
            for w in h["by"][name]["recovery_by_bin"]:
                print(f"    {w['from_kyr']:4.0f}-{w['to_kyr']:<4.0f} {w['splits']:4d} ({w['big_splits']:3d}) {w['scored']:>4} "
                      f"{w['recovered']:6.2f} {w['recovered_all']:6.2f} {w['mean_share']:7.3f}")
    if out_json:
        Path(out_json).write_text(json.dumps({str(k): v for k, v in res.items()}, default=list))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("languages_json")
    ap.add_argument("--pairs", nargs=2, metavar=("COGNATE_DISTS", "MIN_EXCESSES"), default=("0.45", "0.05"),
                    help="comma lists for the old pair measure ('-' skips it)")
    ap.add_argument("--excess", default="0.03", help="comma list of SPLIT_EXCESS values for the split measure")
    ap.add_argument("--json", help="write the split results here")
    a = ap.parse_args()
    doc = json.load(open(a.languages_json))
    if a.pairs[0] != "-":
        pairs_measure(doc, [float(x) for x in a.pairs[0].split(",")], [float(x) for x in a.pairs[1].split(",")])
    splits_measure(doc, [float(x) for x in a.excess.split(",")], a.json)


if __name__ == "__main__":
    main()
