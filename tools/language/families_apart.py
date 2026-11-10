"""Do a run's language families read as families, and different families as different? (PW-1642, owner 11-10)

    uv run python -I tools/language/families_apart.py runs/a24559/languages.json [--json out.json]

Over the living lects: the top-level families (family_true) and their major branches (the subtree under each child of
the family's proto that still has two or more living lects), then three distances, each a mean over pairs:
- sound: tools/language/find.py's distance between two lects (each read as the other's profile, as real_inventory.py's
  lect_gap does): inventory, syllable shape, word length, sound texture, stress and the main typology;
- shape: the gap in word shape alone (words ending in a consonant, words with a cluster, syllables per word);
- tendency: the root-mean-square gap between the lines' family tendencies (log scale; lect.Lect.tendency, PW-1642),
  where the run's json carries them;
for pairs in one branch, in one family but different branches, and in different families. A family reads as a family
when its within-family distance is well under the cross-family one, and branches read apart when the between-branch
distance sits above the within-branch one. Signatures: the branch-defining changes (lect.Lect.signatures) that most of a
branch's living lects carry.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import find as F  # noqa: E402
import real_inventory as RI  # noqa: E402

PAIRS = 3000   # pairs sampled per kind


def _shape(f):
    return (abs(f["final_vowel_share"] - 0) if f["final_vowel_share"] is not None else 0, f["cluster_share"] or 0,
            (f["mean_syllables"] or 0) / 1.5)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("languages")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    doc, feats = F.load(a.languages)
    by_id = {l["id"]: l for l in doc["lects"]}
    living = F.living(doc)
    fx = {f["id"]: f for f in feats}

    def chain(lid):
        out = []
        while lid is not None and lid in by_id:
            out.append(lid)
            lid = by_id[lid].get("parent")
        return out[::-1]   # root first

    branch, fam = {}, {}
    for l in living:
        c = chain(l["id"])
        fam[l["id"]] = l.get("family_true") or c[0]
        branch[l["id"]] = c[1] if len(c) > 1 else c[0]
    nb = Counter(branch.values())
    fams = defaultdict(list)
    for lid, f in fam.items():
        fams[f].append(lid)
    rng = random.Random(1)
    ids = list(fam)
    kinds = {"same branch": [], "same family, other branch": [], "other family": []}
    for _ in range(PAIRS * 20):
        x, y = rng.sample(ids, 2)
        k = ("other family" if fam[x] != fam[y] else "same branch" if branch[x] == branch[y] else
             "same family, other branch")
        if len(kinds[k]) < PAIRS:
            kinds[k].append((x, y))
        if all(len(v) >= PAIRS for v in kinds.values()):
            break
    for f, members in fams.items():   # (small families: every within pair)
        if len(members) < 40:
            for i, x in enumerate(members):
                for y in members[i + 1:]:
                    k = "same branch" if branch[x] == branch[y] else "same family, other branch"
                    kinds[k].append((x, y))

    def tend(lid):
        return by_id[lid].get("tendency")

    out = {"living": len(living), "families": len(fams), "families_3plus": sum(len(v) >= 3 for v in fams.values()),
           "major_branches": sum(1 for b, n in nb.items() if n >= 2 and by_id[b].get("parent") is not None)}
    rows = {}
    for k, pairs in kinds.items():
        pairs = list(dict.fromkeys(pairs))[:PAIRS]
        if not pairs:
            continue
        snd = [RI.lect_gap(fx[x], fx[y]) for x, y in pairs]
        shp = [sum(abs(p - q) for p, q in zip(_shape(fx[x]), _shape(fx[y]))) for x, y in pairs]
        td = []
        for x, y in pairs:
            tx, ty = tend(x), tend(y)
            if tx and ty:
                ks = set(tx) & set(ty)
                td.append(math.sqrt(sum((tx[q] - ty[q]) ** 2 for q in ks) / max(1, len(ks))))
        rows[k] = {"pairs": len(pairs), "sound": round(st.mean(snd), 3), "shape": round(st.mean(shp), 3),
                   "tendency": round(st.mean(td), 3) if td else None}
    out["distances"] = rows
    sig_branches = []
    for b, n in nb.items():
        if n < 2:
            continue
        mem = [lid for lid in branch if branch[lid] == b]
        cnt = Counter(s["rule"] for lid in mem for s in {x["rule"]: x for x in by_id[lid].get("signatures") or []}.values())
        top = [(r, c) for r, c in cnt.most_common(2) if c >= 0.5 * len(mem)]
        if top:
            sig_branches.append({"branch": b, "family": fam[mem[0]], "living": n,
                                 "signatures": [doc.get("rules", {}).get(r, r) for r, _ in top]})
    out["branches_with_signature"] = len(sig_branches)
    out["signature_examples"] = sorted(sig_branches, key=lambda d: -d["living"])[:8]
    print(f"{out['living']} living lects, {out['families']} families ({out['families_3plus']} with 3+ living), "
          f"{out['major_branches']} major branches, {out['branches_with_signature']} carrying a signature change")
    print(f"{'pairs':28s} {'n':>5s} {'sound':>6s} {'shape':>6s} {'tendency':>8s}")
    for k, r in rows.items():
        t = f"{r['tendency']:8.2f}" if r["tendency"] is not None else f"{'-':>8s}"
        print(f"{k:28s} {r['pairs']:5d} {r['sound']:6.2f} {r['shape']:6.2f} {t}")
    for e in out["signature_examples"]:
        print(f"  {e['family']} / {e['branch']} ({e['living']} living): {'; '.join(e['signatures'])}")
    if a.json:
        Path(a.json).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
