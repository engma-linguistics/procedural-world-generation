"""Sister languages side by side (owner 11-10, PW-1642: "a Fantasy French vs Fantasy Spanish equivalent side by side").

    uv run python -I tools/language/sisters_page.py AFTER/languages.json [--before BEFORE/languages.json] --out page.html

Picks, in the AFTER pass, two or three living human lects of one family (each a different language) whose common
ancestor split closest to 2-4 kyr ago (the actual split age is shown), the most different by find.py's sound distance
among those; a pair from two branches of one family that took different signature changes (the centum/satem kind);
and a pair from different families for contrast. Shows 36 core words in aligned columns with the shared ancestor's form at the split (its snapshot), each
lect's signature changes (lect.Lect.signatures) and strongest family tendencies, and two sample sentences. With
--before, the same demes' lects in the BEFORE pass are shown under them (same world, older code).
"""
from __future__ import annotations

import argparse
import html
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import find as F  # noqa: E402
import real_inventory as RI  # noqa: E402

from planet.language import output as OU  # noqa: E402

E = html.escape
WORDS = ["I", "THOU", "WE", "WHO", "WHAT", "NOT", "ONE", "TWO", "THREE", "MAN", "WOMAN", "MOTHER", "FATHER", "CHILD",
         "DOG", "FISH", "BIRD", "TREE", "WATER", "FIRE", "STONE", "SUN", "MOON", "STAR", "NIGHT", "HAND", "EYE", "HEAD",
         "NAME", "EAT", "DRINK", "SEE", "SLEEP", "BIG", "GOOD", "NEW"]
SPLIT = (2.0, 4.0)


def _chain(by_id, lid):
    out = []
    while lid is not None and lid in by_id:
        out.append(lid)
        lid = by_id[lid].get("parent")
    return out[::-1]


def _split(by_id, a, b):
    ca, cb = _chain(by_id, a), _chain(by_id, b)
    i = 0
    while i < min(len(ca), len(cb)) and ca[i] == cb[i]:
        i += 1
    if i == 0 or i >= len(ca) or i >= len(cb):
        return None, None
    t = max(by_id[ca[i]]["born_kyr"], by_id[cb[i]]["born_kyr"])
    return ca[i - 1], t


def _core_at(doc, lect, kyr):
    """The lect's core-100 forms at the snapshot nearest after `kyr` ago (snapshots are delta-coded)."""
    core = None
    best = None
    for k, s in lect.get("snapshots") or []:
        if not s.get("d"):
            core = list(s.get("core") or [])
        elif core is not None:
            for j, v in (s.get("core") or {}).items():
                core[int(j)] = v
        if k >= kyr - 1e-9 and core is not None:
            best = dict(zip(doc.get("snapshot_concepts") or [], core))
    return best or {}


def _sentences(l):
    try:
        from planet.language import sentences as SN
        return [(u.get("en", ""), u.get("roman", ""), u.get("ipa", "")) for u in SN.utterances(l)][:2]
    except Exception as e:  # noqa: BLE001
        return [(f"({type(e).__name__})", "", "")]


def _gap_to_window(t):
    """How far a split age (kyr ago) sits outside SPLIT (0 inside it)."""
    return max(0.0, SPLIT[0] - t, t - SPLIT[1])


def pick(doc, sizes=(3, 2)):
    """The sisters to show (lane 14b): for each family, the sets of 2-3 living human lects (each a different language) whose
    common ancestor split closest to SPLIT (every pair's split age counted; 0 inside the window), the most different by
    sound among the closest; three sisters preferred over two when they come as close. Returns
    (score, ids, (ancestor, split kyr), off) or None, plus the contrast pair, by_id and the features."""
    by_id = {l["id"]: l for l in doc["lects"]}
    liv = [l for l in F.living(doc) if l.get("people") == "human"]
    feats = {f["id"]: f for f in (F.lect_features(l, doc.get("names") or {}) for l in liv)}
    fams = {}
    for l in liv:
        fams.setdefault(l.get("family_true"), []).append(l["id"])
    best = None
    for n in sizes:
        for fam, ids in fams.items():
            ids = sorted(ids)[:60]
            for tri in itertools.combinations(ids, n):
                if len({by_id[x].get("language") for x in tri}) < n:
                    continue
                sp = [_split(by_id, a, b) for a, b in itertools.combinations(tri, 2)]
                if any(t is None for _, t in sp):
                    continue
                off = round(max(_gap_to_window(t) for _, t in sp), 3)
                if best is not None and off > best[0][0]:
                    continue
                score = min(RI.lect_gap(feats[a], feats[b]) for a, b in itertools.combinations(tri, 2))
                key = (off, -score)
                if best is None or key < best[0]:
                    best = (key, tri, max(sp, key=lambda x: x[1]), off)
        if best is not None and best[3] <= 0:
            break   # (three sisters inside the window: done; else two whose split is nearest it)
    fam_big = sorted(fams, key=lambda f: -len(fams[f]))[:2]
    contrast = [fams[f][0] for f in fam_big] if len(fam_big) == 2 else []
    return best, contrast, by_id, feats


def signature_pair(doc, by_id):
    """Two branches of one family that took different signature changes (the centum/satem kind): the family whose
    branches under the living lects' common ancestor each carry a signature most of their living members share, two such
    branches with different marks, one living lect from each (the one carrying it). None if no family has two."""
    liv = [l for l in F.living(doc) if l.get("people") == "human"]
    fams = {}
    for l in liv:
        fams.setdefault(l.get("family_true"), []).append(l["id"])
    best = None
    for fam, ids in fams.items():
        if len(ids) < 2:
            continue
        cs = {x: _chain(by_id, x) for x in ids}
        i = 0
        while all(len(c) > i + 1 for c in cs.values()) and len({c[i] for c in cs.values()}) == 1 \
                and len({c[i + 1] for c in cs.values()}) == 1:
            i += 1
        br = {}
        for x, c in cs.items():
            if len(c) > i + 1:
                br.setdefault(c[i + 1], []).append(x)
        marks = []
        for b, mem in br.items():
            cnt = {}
            for x in mem:
                for sg in {q["rule"]: q for q in by_id[x].get("signatures") or []}.values():
                    cnt[sg["rule"]] = cnt.get(sg["rule"], 0) + 1
            top = sorted(((c, r) for r, c in cnt.items() if c >= 0.5 * len(mem)), reverse=True)
            if top:
                r = top[0][1]
                rep = next(x for x in sorted(mem) if any(q["rule"] == r for q in by_id[x].get("signatures") or []))
                marks.append((len(mem), b, r, rep))
        marks.sort(reverse=True)
        for j in range(len(marks)):
            for k in range(j + 1, len(marks)):
                if marks[j][2] != marks[k][2]:
                    cand = (marks[j][0] + marks[k][0], fam, marks[j], marks[k], cs[marks[j][3]][i])
                    if best is None or cand[0] > best[0]:
                        best = cand
                    break
    return best


def block(doc, by_id, ids, anc, t, title, feats):
    lects = [by_id[x] for x in ids]
    head = "".join(f"<th>{E(l.get('deme_name') or l['id'])}<br><span class=m>{E(l['id'])}, {E(str(l.get('language')))}"
                   f"</span></th>" for l in lects)
    anc_core = _core_at(doc, by_id[anc], t) if anc else {}
    rows = []
    for c in WORDS:
        cells = []
        for l in lects:
            w = (l.get("lexicon") or {}).get(c) or {}
            cells.append(f"<td>{E(w.get('roman') or '')}<br><span class=ipa>/{E(w.get('ipa') or '')}/</span></td>")
        a = anc_core.get(c) or "?"
        rows.append(f"<tr><th>{E(c.lower())}</th>" + (f"<td class=anc><span class=ipa>*{E(a)}</span></td>" if anc else "")
                    + "".join(cells) + "</tr>")
    notes = []
    for l in lects:
        sig = l.get("signatures") or []
        tend = sorted((l.get("tendency") or {}).items(), key=lambda kv: -kv[1])[:3]
        f = feats.get(l["id"]) or F.lect_features(l, doc.get("names") or {})
        s = (f"<b>{E(l.get('deme_name') or l['id'])}</b>: {f['consonants']} consonants, {f['vowels']} vowels, "
             f"{f['final_vowel_share']:.0%} of words end in a vowel, {f['mean_syllables']:.1f} syllables a word. ")
        if sig:
            s += "Signature changes: " + "; ".join(
                f"{E(doc.get('rules', {}).get(x['rule'], x['rule']))} (the {E(x['lect'])} branch, {x['kyr']:g} kyr ago)"
                for x in sig) + ". "
        if tend:
            s += "Leans to " + ", ".join(E(k) for k, _ in tend) + ". "
        for en, ro, ipa in _sentences(l):
            s += f"<br><i>{E(en)}</i> {E(ro)} <span class=ipa>/{E(ipa)}/</span>"
        notes.append(f"<p>{s}</p>")
    anc_h = f"<th>shared ancestor<br><span class=m>{E(anc)} at {t:g} kyr ago</span></th>" if anc else ""
    return (f"<h3>{E(title)}</h3><div class=wrap><table><tr><th></th>{anc_h}{head}</tr>{''.join(rows)}</table></div>"
            + "".join(notes))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("after")
    ap.add_argument("--before")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    doc = OU.load(a.after)
    best, contrast, by_id, feats = pick(doc)
    parts = []
    if best is None:
        parts.append("<p>No sister languages in one family in this pass.</p>")
    else:
        (off, _neg), tri, (anc, t), _off = best
        ages = sorted({_split(by_id, x, y)[1] for x, y in itertools.combinations(tri, 2)}, reverse=True)
        where = ("split " + " and ".join(f"{a:g}" for a in ages) + " kyr ago" + ("" if off <= 0 else
                 f" (the split nearest the {SPLIT[0]:g}-{SPLIT[1]:g} kyr window: none in this pass falls inside it)"))
        parts.append(block(doc, by_id, tri, anc, t, f"Sisters, after (lane 14): {len(tri)} languages of one family, "
                                                   f"{where}", feats))
        if a.before:
            bd = OU.load(a.before)
            bby = {l["id"]: l for l in bd["lects"]}
            demes = [by_id[x]["deme"] for x in tri]
            old = [next((l["id"] for l in F.living(bd) if l["deme"] == d and l.get("people") == "human"), None)
                   for d in demes]
            old = [x for x in old if x]
            if len(old) >= 2:
                anc_b, t_b = _split(bby, old[0], old[1])
                parts.append(block(bd, bby, old, anc_b, t_b or t, "The same places, before (main): the lects spoken "
                                   "there on the code before lane 14" + (f", split {t_b:g} kyr ago" if t_b else
                                                                         " (not sisters there)"), {}))
    sp = signature_pair(doc, by_id)
    if sp is not None:
        _n, fam, m1, m2, anc2 = sp
        _s, tsp = _split(by_id, m1[3], m2[3])
        rn = doc.get("rules", {})
        parts.append(block(doc, by_id, [m1[3], m2[3]], anc2, tsp or 0,
                           f"Two branches, two marks (the centum/satem kind): family {fam}, branch {m1[1]} "
                           f"({m1[0]} living) took '{rn.get(m1[2], m1[2])}', branch {m2[1]} ({m2[0]} living) took "
                           f"'{rn.get(m2[2], m2[2])}'", feats))
    if len(contrast) == 2:
        parts.append(block(doc, by_id, contrast, None, 0, "For contrast: two languages of different families", feats))
    css = (":root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#6b6a66;--line:#dedbd3;--card:#fff}"
           "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#17181a;--fg:#e8e6e1;--mut:#9a978f;"
           "--line:#33342f;--card:#1f2023}}:root[data-theme=dark]{--bg:#17181a;--fg:#e8e6e1;--mut:#9a978f;--line:#33342f;"
           "--card:#1f2023}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}"
           "main{max-width:1180px;margin:0 auto;padding:16px}table{border-collapse:collapse;font-size:.88rem;"
           "background:var(--card)}td,th{border:1px solid var(--line);padding:3px 6px;text-align:left;vertical-align:top}"
           ".wrap{overflow-x:auto;max-width:100%}.ipa,.m{color:var(--mut);font-size:.85em}.anc{opacity:.85}p{max-width:90ch}")
    doc_html = (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,"
                f"initial-scale=1'><title>Sister languages</title><style>{css}</style></head><body><main>"
                f"<h1>Sister languages side by side</h1><p>Run {E(str(doc.get('run')))}. Words in the book spelling, IPA "
                f"under; the ancestor's form (*) is its core word at the split.</p>{''.join(parts)}</main></body></html>")
    Path(a.out).write_text(doc_html, encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
