"""Recompute the scholars' horizon from a stored languages.json with the current families code, for several COGNATE_DIST and
MIN_EXCESS values (calibration without re-running the pass; docs/review/language/calibration.md).

    uv run python tools/language/horizon_offline.py runs/a24559/languages.json 0.45,0.6 0,0.03,0.05
"""
import sys, json
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from planet.language import families as FA, lexicon as LX
from planet.language.percepts import from_ipa
d = json.load(open(sys.argv[1]))
class L: pass
by = {}
for x in d["lects"]:
    l = L(); l.id, l.parent, l.born_kyr, l.died_kyr, l.deme, l.people = x["id"], x["parent"], x["born_kyr"], x["died_kyr"], x["deme"], x["people"]
    l.forms = {c: tuple(from_ipa(w["ipa"])) for c, w in x["lexicon"].items() if c in LX.CORE100}
    by[l.id] = l
living = [l for l in by.values() if l.died_kyr is None and l.deme is not None]
core = sorted(LX.CORE100)
T = FA.divergence_matrix(living, by)
for cd in [float(x) for x in sys.argv[2].split(",")]:
    FA.COGNATE_DIST = cd
    tab = FA.WordTable(living, core, lambda l, c: l.forms.get(c))
    S = tab.share_matrix(blind=True)
    for me in [float(x) for x in sys.argv[3].split(",")]:
        FA.MIN_EXCESS = me
        iu = np.triu_indices(len(living), 1)
        hum = np.array([living[i].people == "human" and living[j].people == "human" for i, j in zip(*iu)])
        hz = FA.horizon_pairs(tab, T, S, S, (iu[0][hum], iu[1][hum]), np.random.default_rng(1))
        ha = FA.horizon_pairs(tab, T, S, S, iu, np.random.default_rng(2))
        sib = np.isfinite(T[iu]) & (T[iu] <= 2)
        print(f"cd {cd} excess {me}: human {hz['horizon_kyr']} all {ha['horizon_kyr']} chance {hz.get('chance_mean')} sib {S[iu][sib].mean():.3f}",
              [(b["from_kyr"], b["above_chance"]) for b in hz["bins"]])
