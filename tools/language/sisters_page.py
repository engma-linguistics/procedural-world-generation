"""Sister languages side by side (owner 11-10, PW-1642: "a Fantasy French vs Fantasy Spanish equivalent side by side").

    uv run python -I tools/language/sisters_page.py AFTER/languages.json [--before BEFORE/languages.json] --out page.html

Picks, in the AFTER pass, the three living human lects of one family that split from a common ancestor 2-4 kyr ago and
now sit farthest apart by find.py's sound distance (each a different language), plus a pair from different families
for contrast. Shows 36 core words in aligned columns with the shared ancestor's form at the split (its snapshot), each
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


def pick(doc):
    by_id = {l["id"]: l for l in doc["lects"]}
    liv = [l for l in F.living(doc) if l.get("people") == "human"]
    feats = {f["id"]: f for f in (F.lect_features(l, doc.get("names") or {}) for l in liv)}
    fams = {}
    for l in liv:
        fams.setdefault(l.get("family_true"), []).append(l["id"])
    best = None
    for fam, ids in fams.items():
        for tri in itertools.combinations(ids[:40], 3):
            langs = {by_id[x].get("language") for x in tri}
            if len(langs) < 3:
                continue
            sp = [_split(by_id, a, b) for a, b in itertools.combinations(tri, 2)]
            if any(t is None or not SPLIT[0] <= t <= SPLIT[1] for _, t in sp):
                continue
            score = min(RI.lect_gap(feats[a], feats[b]) for a, b in itertools.combinations(tri, 2))
            if best is None or score > best[0]:
                best = (score, tri, max(sp, key=lambda x: x[1]))
    fam_big = sorted(fams, key=lambda f: -len(fams[f]))[:2]
    contrast = [fams[f][0] for f in fam_big] if len(fam_big) == 2 else []
    return best, contrast, by_id, feats


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
            cells.append(f"<td>{E(w.get('roman', ''))}<br><span class=ipa>/{E(w.get('ipa', ''))}/</span></td>")
        a = anc_core.get(c)
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
        parts.append("<p>No three sister languages split 2-4 kyr ago in this pass.</p>")
    else:
        score, tri, (anc, t) = best
        parts.append(block(doc, by_id, tri, anc, t, f"Sisters, after (lane 14): three languages of one family, split "
                                                   f"about {t:g} kyr ago", feats))
        if a.before:
            bd = OU.load(a.before)
            bby = {l["id"]: l for l in bd["lects"]}
            demes = [by_id[x]["deme"] for x in tri]
            old = [next((l["id"] for l in F.living(bd) if l["deme"] == d and l.get("people") == "human"), None)
                   for d in demes]
            old = [x for x in old if x]
            if len(old) >= 2:
                anc_b, t_b = _split(bby, old[0], old[1])
                parts.append(block(bd, bby, old, anc_b, t_b or t, "The same places, before (main)", {}))
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
