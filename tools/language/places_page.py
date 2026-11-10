"""Place names by family (lane 15): each family's biggest settlements with local name, English Common, meaning and history.
Usage: uv run python tools/language/places_page.py runs/<run>/languages.json <out.html> [n_families]"""
"""Side-by-side place names of 3-4 families (lane 15, PW-1658/1654): local name, English Common, meaning, history.
usage: uv run python places_page.py <languages.json> <out.html> [n_families]"""
import html
import json
import sys
from collections import Counter, defaultdict

E = html.escape
d = json.load(open(sys.argv[1]))
out = sys.argv[2]
nfam = int(sys.argv[3]) if len(sys.argv) > 3 else 4
names = d["names"]
L = {l["id"]: l for l in d["lects"]}
hab = names.get("habits") or {}
by_fam = defaultdict(list)
for dk, e in names["demes"].items():
    for s in e.get("settlements") or []:
        if s.get("kind") == "ruin" or not s.get("english") or s.get("substrate_of"):
            continue
        l = L.get(s["lect"])
        if l is None or l.get("people") != "human":
            continue
        by_fam[l.get("family_true")].append((dk, s))
# families: the biggest, preferring different templates
fams = sorted(by_fam, key=lambda f: -len(by_fam[f]))
pick, used = [], set()
for f in fams:
    tm = Counter(hab.get(s["lect"], {}).get("template") for _d, s in by_fam[f]).most_common(1)[0][0]
    if tm in used:
        continue
    pick.append((f, tm))
    used.add(tm)
    if len(pick) == nfam:
        break
cols = []
for f, tm in pick:
    rows = sorted(by_fam[f], key=lambda x: (-(x[1].get("pop") or 0), x[1]["site"]))
    lects = Counter(s["lect"] for _d, s in rows)
    h = hab.get(rows[0][1]["lect"], {})
    gens = Counter(g for _d, s in rows for g in [(s.get("meaning") or {}).get("generic")] if g)
    share = Counter()
    for lid in lects:
        share.update(set((hab.get(lid) or {}).get("generics") or []))
    items = []
    for dk, s in rows[:12]:
        hist = " &rarr; ".join(f"{E(x[3])} <span class=m>({E(str(x[2]))}, {x[0]:g} kyr)</span>" for x in s.get("history") or [])
        items.append(f"<tr><td><b>{E(s['roman'])}</b><br><span class=ipa>/{E(s.get('ipa') or '')}/</span></td>"
                     f"<td><b>{E(s['english'])}</b><br><span class=m>{E(s.get('english_how') or '')}</span></td>"
                     f"<td>&lsquo;{E(s['gloss'])}&rsquo;<br><span class=m>{E(s.get('frame') or '')}; {E(s['lect'])}, a {E(str(s.get('tier')))}</span></td>"
                     f"<td class=m>{hist}</td></tr>")
    cols.append(f"<section><h2>Family {E(str(f))}: {E(h.get('like') or tm)}-like habit</h2>"
                f"<p class=m>{len(rows)} named settlements in {len(lects)} lects. Habit drawn by {E(h.get('origin') or '?')} "
                f"({E(h.get('order') or '')}); generics in use: {E(', '.join(h.get('generics') or []))}; by rivers "
                f"{E(', '.join(h.get('river') or []) or 'none')}; hills {E(', '.join(h.get('hill') or []) or 'none')}; specifics "
                f"{E(', '.join(h.get('specific') or []))}. Generics actually used: "
                f"{E(', '.join(f'{k.split(chr(32) + chr(40))[0].lower()} {v}' for k, v in gens.most_common(6)))}.</p>"
                f"<div class=wrap><table><tr><th>local name</th><th>English Common</th><th>meaning</th><th>history (oldest first)</th></tr>"
                f"{''.join(items)}</table></div></section>")
deep = sorted((s for e in names["demes"].values() for s in e.get("settlements") or []
               if s.get("kind") != "ruin" and len(s.get("history") or []) >= 3),
              key=lambda s: (-len(s["history"]), -(s.get("pop") or 0)))[:10]
rows = "".join(f"<tr><td><b>{E(s['english'])}</b><br><span class=m>&lsquo;{E(s['gloss'])}&rsquo;</span></td><td>"
               + " &rarr; ".join(f"<b>{E(x[3])}</b> <span class=m>{E(str(x[2]))} ({E(x[1])}), {x[0]:g} kyr ago: {E(x[4])}</span>"
                                 for x in s["history"]) + "</td></tr>" for s in deep)
cols.append(f"<section><h2>What the locals actually call it: the deepest histories</h2><p class=m>Places that changed hands "
            f"between peoples of different speech: the founders' name, heard anew by each later holder.</p><div class=wrap>"
            f"<table><tr><th>English Common</th><th>the names it went through</th></tr>{rows}</table></div></section>")
css = (":root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#6b6a66;--line:#dedbd3;--card:#fff}"
       "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#17181a;--fg:#e8e6e1;--mut:#9a978f;"
       "--line:#33342f;--card:#1f2023}}:root[data-theme=dark]{--bg:#17181a;--fg:#e8e6e1;--mut:#9a978f;--line:#33342f;"
       "--card:#1f2023}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}"
       "main{max-width:1180px;margin:0 auto;padding:16px}table{border-collapse:collapse;font-size:.88rem;background:var(--card)}"
       "td,th{border:1px solid var(--line);padding:3px 6px;text-align:left;vertical-align:top}.wrap{overflow-x:auto;max-width:100%}"
       ".ipa,.m{color:var(--mut);font-size:.85em}p{max-width:95ch}")
doc = (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
       f"<title>Place names by family</title><style>{css}</style></head><body><main><h1>Place names by family</h1>"
       f"<p>Run {E(str(d.get('run')))}, language lane 15 (PW-1658 naming habits, PW-1654 English Common). Each family's "
       f"biggest settlements: what the locals call it, the Common's English rendering of its meaning, the meaning, and "
       f"the names it went through.</p>{''.join(cols)}</main></body></html>")
open(out, "w").write(doc)
print("wrote", out, [p for p in pick])
