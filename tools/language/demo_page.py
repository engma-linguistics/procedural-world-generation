"""One self-contained HTML page showing a handful of very different living languages, playable offline.

    uv run python tools/language/demo_page.py runs/a24559/languages.json --out /some/dir/languages-demo.html
        [--run runs/a24559/run.json] [--n 10] [--backend auto|espeak|piper] [--no-audio]

The page needs no server: CSS, script and audio are inline (no fetches, no storage it depends on), it reads well at phone
width, and the claude.ai artifact viewer can host it. The languages are picked by tools/language/sketch.py's criteria
(clicks, a tonal kenku or aarakocra lect, a dragon lect, a tiny inventory, the most conservative, the most English-like),
then by DEMO_EXTRA (the most spoken, an elvish lect, a dwarvish one, an ergative one, the most and least synthetic), each
from a people (and where possible a true family) not shown yet.

Each language: an infobox, its line of descent and closest living relatives, vowel and consonant charts, pronouns, the
grammar in short (`grammar_notes`), the glossed sample sentences (`sentences`), words, and word families seen two ways
(`roots`, `etym_roots`). Sentences, pronouns and a few words are pre-rendered by planet/language/speak.py and embedded as
MP3 (ffmpeg; low-rate WAV without it); the page says which backend made them.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import sketch as SK  # noqa: E402

from planet.language import sentences as SN  # noqa: E402

E = html.escape
WORDS = ["MAN", "WOMAN", "CHILD (YOUNG HUMAN)", "MOTHER", "FATHER", "DOG", "FISH", "BIRD", "TREE", "WATER", "FIRE", "SUN",
         "MOON", "STONE", "HOUSE", "EAT", "DRINK", "SEE", "SLEEP", "SING", "BIG", "SMALL", "GOOD", "COLD", "ONE", "TWO",
         "THREE", "WHO", "WHAT", "NOT"]
SPOKEN_WORDS = 10  # of WORDS, with audio (besides pronouns)


def _bound(l):
    return sum(1 for g in l.get("grams") or [] if g.get("level", 0) >= 2)


DEMO_EXTRA = [
    ("most_spoken", "the most spoken language", lambda l: True, lambda l: (l.get("population") or 0,),
     lambda l: f"about {_pop(l)} speakers"),
    ("elvish", "an elvish language", lambda l: SK.group(l["people"]) == "elf", lambda l: (l.get("population") or 0,),
     lambda l: f"spoken by {SK.people(l['people'])}"),
    ("dwarvish", "a dwarvish language", lambda l: "dwar" in l["people"], lambda l: (l.get("population") or 0,),
     lambda l: f"spoken by {SK.people(l['people'])}"),
    ("ergative", "an ergative language", lambda l: (l.get("typology") or {}).get("alignment") == "erg-abs"
     and any(g["function"] == "ERG" for g in l.get("grams") or []), lambda l: (_bound(l),),
     lambda l: "the doer of a transitive verb is marked (ergative), the doer of an intransitive one is not"),
    ("synthetic", "the most affixes", lambda l: True, lambda l: (_bound(l),),
     lambda l: f"{_bound(l)} live affixes"),
    ("isolating", "the fewest affixes", lambda l: len(l.get("sentences") or []) >= 8, lambda l: (-_bound(l),),
     lambda l: f"{_bound(l)} live affixes: grammar by word order and separate words"),
]


def _pop(l) -> str:
    p = l.get("population") or 0
    return f"{p / 1e6:.1f} million" if p >= 1e6 else f"{p / 1e3:.0f} thousand" if p >= 1e3 else str(int(p))


def pick(doc, n: int) -> list[tuple[str, dict, str]]:
    """(why heading, lect, why text): sketch.py's picks and the most English-like, then DEMO_EXTRA, each from a people
    not shown yet (and a true family not shown yet when there is one)."""
    out = [(head, l, why) for _k, head, l, why in SK.pick(doc)]
    rank = SK.english_ranking(doc)
    used = {l["people"] for _h, l, _w in out}
    for s, l, _c in rank:
        if l["people"] not in used:
            out.append(("the most English-like language", l, f"English-likeness score {s:.2f} (sketch.py)"))
            break
    for _k, head, ok, score, why in DEMO_EXTRA:
        if len(out) >= n:
            break
        used_p = {l["people"] for _h, l, _w in out}
        used_f = {l["family_true"] for _h, l, _w in out}
        cands = [l for l in doc.living if ok(l) and l["people"] not in used_p and l.get("sentences")]
        fresh = [l for l in cands if l["family_true"] not in used_f]
        cands = fresh or cands
        if cands:
            best = max(cands, key=lambda l: (score(l), l["id"]))
            out.append((head, best, why(best)))
    return out[:n]


# ---- audio ------------------------------------------------------------------------------------------------------------------

class Audio:
    def __init__(self, backend: str, enabled: bool):
        self.clips: dict[str, str] = {}  # key -> data URI
        self.keys: dict[tuple, str] = {}
        self.backend = None
        self.codec = None
        self.failed = 0
        if not enabled:
            return
        from planet.language import speak as SP
        have = SP.available_backends()
        want = ("piper" if "piper" in have else "espeak" if "espeak" in have else None) if backend == "auto" else backend
        if want not in have:
            print(f"(no {backend} speech backend: the page has no audio)", file=sys.stderr)
            return
        self.SP, self.backend = SP, want
        self.ffmpeg = shutil.which("ffmpeg")
        self.codec = "MP3" if self.ffmpeg else "WAV (11 kHz)"
        self.tmp = Path(tempfile.mkdtemp(prefix="langdemo-"))

    def clip(self, ipa: str, people: str, sentence: bool = False, q: bool = False) -> str | None:
        if not self.backend or not ipa:
            return None
        k = (ipa, people, sentence, q)
        if k in self.keys:
            return self.keys[k]
        prof = self.SP.profile_for_people(people)
        try:
            wav = (self.SP.speak_utterance(ipa, prof, backend=self.backend, question=q) if sentence
                   else self.SP.speak(ipa, prof, backend=self.backend))
        except Exception as e:  # noqa: BLE001 (one unsayable form must not sink the page)
            self.failed += 1
            print(f"  (could not say /{ipa}/: {type(e).__name__}: {e})", file=sys.stderr)
            self.keys[k] = None
            return None
        uri = self._encode(wav)
        cid = f"a{len(self.clips)}"
        self.clips[cid] = uri
        self.keys[k] = cid
        return cid

    def _encode(self, wav: bytes) -> str:
        if self.ffmpeg:
            src, dst = self.tmp / "in.wav", self.tmp / "out.mp3"
            src.write_bytes(wav)
            r = subprocess.run([self.ffmpeg, "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "22050",
                                "-c:a", "libmp3lame", "-b:a", "40k", str(dst)], capture_output=True)
            if r.returncode == 0:
                return "data:audio/mpeg;base64," + base64.b64encode(dst.read_bytes()).decode()
        return "data:audio/wav;base64," + base64.b64encode(_downsample_wav(wav)).decode()

    def close(self):
        if getattr(self, "tmp", None):
            shutil.rmtree(self.tmp, ignore_errors=True)


def _downsample_wav(wav: bytes) -> bytes:
    """22.05 kHz 16-bit WAV -> 11.025 kHz 8-bit (the no-ffmpeg fallback: a quarter of the size)."""
    import io
    import wave
    import numpy as np
    with wave.open(io.BytesIO(wav)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
        sr = w.getframerate()
    x = x[: len(x) // 2 * 2].reshape(-1, 2).mean(1)
    bio = io.BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(sr // 2)
        w.writeframes((np.clip(x, -1, 1) * 127 + 128).astype(np.uint8).tobytes())
    return bio.getvalue()


# ---- page pieces ------------------------------------------------------------------------------------------------------------

def md_table(md: str) -> str:
    """sketch.py's markdown chart -> an HTML table (first column and header as th)."""
    rows = [r.strip().strip("|").split("|") for r in md.strip().splitlines()]
    rows = [r for r in rows if not all(c.strip().startswith("---") for c in r)]
    out = ["<div class='scroll'><table class='chart'>"]
    for i, r in enumerate(rows):
        cells = []
        for j, c in enumerate(r):
            c = c.strip().replace("**", "")
            tag = "th" if i == 0 or j == 0 else "td"
            cells.append(f"<{tag}{' class=ipa' if tag == 'td' else ''}>{E(c)}</{tag}>")
        out.append("<tr>" + "".join(cells) + "</tr>")
    return "".join(out) + "</table></div>"


def play(cid: str | None, label: str = "") -> str:
    if not cid:
        return ""
    return f"<button class='say{' lab' if label else ''}' data-a='{cid}' aria-label='play'>&#9654;{(' ' + E(label)) if label else ''}</button>"


def gloss_html(g: str) -> str:
    import re
    return "".join(f"<span class='sc'>{E(t)}</span>" if re.fullmatch(r"[0-9A-Z]+", t) and t != "I" else E(t)
                   for t in re.split(r"([-=.])", g))


def interlinear(form: str, gloss: str) -> str:
    fw, gw = form.split(" "), gloss.split(" ")
    if len(fw) != len(gw):
        fw, gw = [form], [gloss]
    return "<div class='igl'>" + "".join(f"<div><span class='f ipa'>{E(f)}</span><span class='g'>{gloss_html(g)}</span></div>"
                                         for f, g in zip(fw, gw)) + "</div>"


def families(doc, l, field: str, au: Audio) -> str:
    lex = l.get("lexicon") or {}
    fam: dict = {}
    seen = False
    for c, w in lex.items():
        rs = w.get(field)
        if not isinstance(rs, list):
            continue
        seen = True
        for k, r in enumerate(rs):
            f = fam.setdefault(r, {"main": [], "all": set()})
            if k == 0:
                f["main"].append(c)
            f["all"].add(c)
    if not seen:
        return f"<p class='muted'>This languages file has no <code>{E(field)}</code> yet.</p>"
    big = sorted((x for x in fam.items() if len(x[1]["main"]) >= 2), key=lambda x: (-len(x[1]["main"]), str(x[0])))
    inside = {c for _r, f in big for c in f["main"]}
    out = [f"<p class='muted'>{sum(len(f['main']) >= 3 for _r, f in big)} families of 3+ words; "
           f"{round(100 * len(inside) / max(1, len(lex)))}% of the {len(lex)} words share a root with another.</p>"]
    R = doc.d.get("roots") or {}
    for r, f in big[:5]:
        info = R.get(r) or {}
        head = info.get("gloss") or SK.cname(str(r).split(":", 1)[-1].split("@")[0])
        words = ", ".join(f"{E(SK.cname(c))} <span class='ipa'>{E(lex[c]['ipa'])}</span>" for c in sorted(f["main"])[:8])
        more = f" <span class='muted'>+{len(f['main']) - 8}</span>" if len(f["main"]) > 8 else ""
        star = f" <span class='ipa'>*{E(info['ipa'])}</span>" if info.get("ipa") else ""
        out.append(f"<div class='fam'><b>{E(str(head))}</b>{star} <span class='muted'>· {len(f['main'])} words</span>"
                   f"<br>{words}{more}</div>")
    if not big:
        out.append("<p class='muted'>Every root has a single word here.</p>")
    return "".join(out)


def lineage(doc, l) -> str:
    line = doc.line(l["id"])[::-1]  # oldest first
    steps = []
    for x in line[-6:]:
        nm = doc.label(x["id"], short=True)
        steps.append(f"<span class='step'>{E(nm)} <span class='muted'>{E(SK.kyr(x.get('born_kyr')))}</span></span>")
    hidden = f"<span class='muted'>… {len(line) - 6} older stages … </span>" if len(line) > 6 else ""
    sis = []
    for x in doc.living:
        if x["id"] != l["id"] and x.get("family_true") == l.get("family_true"):
            v = doc.intel.get((l["id"], x["id"]))
            sis.append((-(v or 0), x["id"], v))
    sis.sort()
    rel = ", ".join(f"{E(doc.label(i, short=True))}{f' <span class=muted>({v:.0%} understood)</span>' if v else ''}"
                    for _s, i, v in sis[:4])
    out = f"<div class='line'>{hidden}{' → '.join(steps)}</div>"
    fam_n = 1 + len(sis)
    out += (f"<p class='muted'>{fam_n} living languages in this true family. Closest living relatives: {rel}.</p>" if sis
            else "<p class='muted'>The only living language of its true family.</p>")
    return out


def infobox(doc, l, why_head, why) -> str:
    inv = l.get("inventory") or {}
    t = l.get("typology") or {}
    tones = len(inv.get("tones") or [])
    rows = [("people", SK.people(l["people"])), ("speakers", f"about {_pop(l)}"),
            ("sounds", f"{len(inv.get('consonants', []))} consonants, {len(inv.get('vowels', []))} vowels"
                       + (f", {tones} tones" if tones else "")),
            ("word order", t.get("word_order", "?")), ("first spoken", SK.kyr(l.get("born_kyr")))]
    return ("<div class='why'><b>Why it is here:</b> " + E(why_head) + f" <span class='muted'>({E(why)})</span></div>"
            "<dl class='info'>" + "".join(f"<dt>{E(a)}</dt><dd>{E(str(b))}</dd>" for a, b in rows) + "</dl>")


def lang_section(doc, l, why_head, why, au: Audio, k: int) -> str:
    p = l["people"]
    lex = l.get("lexicon") or {}
    nm = doc.deme_name(l)
    title = nm["roman"] if nm else doc.label(l["id"], short=True)
    sents = l.get("sentences") or []
    sc = [au.clip(s["ipa"], p, True, bool(s.get("q"))) for s in sents]
    first = next((c for c in sc if c), None)
    h = [f"<section class='lang' id='L{k}' data-k='{k}'><h2>{E(title)} <span class='muted'>{E(l.get('deme_name') or doc.label(l['id']))}</span></h2>",
         f"<div class='row'>{play(first, 'hear a sample')}"
         + (f"<button class='say lab all' data-k='{k}'>&#9654; play all sentences</button>" if len(sents) > 1 and first else "")
         + "</div>", infobox(doc, l, why_head, why), "<h3>Where it comes from</h3>", lineage(doc, l)]
    # sentences
    h.append("<h3>Sample sentences</h3>")
    for i, (s, cid) in enumerate(zip(sents, sc)):
        form, gloss = " ".join(w[0] for w in s["w"]), " ".join(w[1] for w in s["w"])
        h.append(f"<div class='sent'><div class='en'><span class='muted'>({i + 1})</span> ‘{E(s['en'])}’ {play(cid)}</div>"
                 f"{interlinear(form, gloss)}<div class='l2'><span class='ipa'>/{E(s['ipa'])}/</span> · "
                 f"<i>{E(s.get('roman') or '')}</i>{' · rising intonation' if s.get('q') else ''}</div>"
                 + (f"<div class='note'>{E(s['note'])}</div>" if s.get("note") else "") + "</div>")
    if not sents:
        h.append("<p class='muted'>Too few words of its own for the sample sentences.</p>")
    # grammar
    h.append("<h3>The grammar in short</h3><div class='notes'>")
    for i, n in enumerate(l.get("grammar_notes") or []):
        exs = []
        for x in (n.get("ex") or [])[:2]:
            r = SN.example(l, x)
            if r:
                exs.append(f"<div class='ex'>{interlinear(r[0], r[1])}<span class='muted'>‘{E(r[2])}’"
                           f"{' (sentence ' + str(sents.index(r[3]) + 1) + ')' if r[3] in sents else ''}</span></div>")
        h.append(f"<details{' open' if i == 0 else ''}><summary>{E(n['topic'])}</summary><p>{E(n['text'])}</p>{''.join(exs)}</details>")
    h.append("</div>")
    # sounds
    inv = l.get("inventory") or {}
    h.append("<h3>Sounds</h3><h4>Consonants</h4>" + md_table(SK.consonant_chart(inv.get("consonants", [])))
             + "<h4>Vowels</h4>" + md_table(SK.vowel_chart(inv.get("vowels", []))))
    if inv.get("tones"):
        h.append(f"<p class='muted'>{len(inv['tones'])} tones.</p>")
    # pronouns
    h.append("<h3>Pronouns</h3><table class='t'><tr><th></th><th>singular</th><th>plural</th></tr>")
    for name, sg, pl in SK.PRONOUNS:
        cells = []
        for c in (sg, pl):
            e = lex.get(c)
            cells.append(f"<td><span class='ipa'>{E(e['ipa'])}</span> <i>{E(e.get('roman') or '')}</i> "
                         f"{play(au.clip(e['ipa'], p))}</td>" if e else "<td class='muted'>–</td>")
        h.append(f"<tr><th>{name}</th>{''.join(cells)}</tr>")
    h.append("</table>")
    # words
    h.append("<h3>Words</h3><table class='t words'><tr><th>meaning</th><th>IPA</th><th>spelling</th><th></th></tr>")
    spoken = 0
    for c in WORDS:
        e = lex.get(c)
        if not e:
            continue
        cid = au.clip(e["ipa"], p) if spoken < SPOKEN_WORDS else None
        spoken += 1
        h.append(f"<tr><td>{E(SK.cname(c))}</td><td class='ipa'>{E(e['ipa'])}</td><td><i>{E(e.get('roman') or '')}</i></td>"
                 f"<td>{play(cid)}</td></tr>")
    h.append("</table>")
    # families
    h.append("<h3>Word families</h3><div class='two'><div class='card'><h4>Families a speaker feels</h4>"
             "<p class='muted'>Roots a speaker still hears: derivations and compounds younger than about 3,000 years whose "
             "parts are still words.</p>" + families(doc, l, "roots", au) + "</div><div class='card'><h4>Families a "
             "historian reconstructs</h4><p class='muted'>Every word's family as it was when the word was made, however "
             "opaque it has become since.</p>" + families(doc, l, "etym_roots", au) + "</div></div></section>")
    return "".join(h)


CSS = """
:root{--bg:#f7f6f2;--fg:#1d2126;--muted:#6a717c;--card:#fff;--line:#dcdad3;--acc:#2f6fb3;--sc:#7a4b12}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#11151b;--fg:#e3e8ef;--muted:#8d97a5;--card:#18202a;--line:#2a3441;--acc:#6aa8ef;--sc:#e3b26b}}
:root[data-theme=dark]{--bg:#11151b;--fg:#e3e8ef;--muted:#8d97a5;--card:#18202a;--line:#2a3441;--acc:#6aa8ef;--sc:#e3b26b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1000px;margin:0 auto;padding:12px 16px 60px}h1{font-size:22px;margin:8px 0 4px}h2{font-size:19px;margin:6px 0}
h3{font-size:16px;margin:18px 0 6px;border-bottom:1px solid var(--line);padding-bottom:2px}h4{margin:4px 0}
.muted{color:var(--muted)}.ipa{font-family:"Charis SIL","Doulos SIL","Noto Serif","DejaVu Sans",serif}
nav{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0;position:sticky;top:0;background:var(--bg);padding:6px 0;z-index:2}
nav button{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:14px;padding:4px 10px;font:inherit;font-size:13px;cursor:pointer}
nav button.on{border-color:var(--acc);color:var(--acc);font-weight:600}
.lang{display:none}.lang.on{display:block}
.say{border:1px solid var(--acc);color:var(--acc);background:transparent;border-radius:12px;font-size:11px;padding:1px 7px;cursor:pointer;vertical-align:middle}
.say.lab{font-size:13px;padding:3px 10px;margin-right:6px}.say.busy,.say.playing{background:var(--acc);color:var(--bg)}
.row{margin:4px 0 8px}.why{margin:6px 0}
.info{display:grid;grid-template-columns:max-content 1fr;gap:2px 12px;margin:6px 0}.info dt{color:var(--muted)}.info dd{margin:0}
.line{line-height:1.7;overflow-wrap:anywhere}
.sent{border-bottom:1px solid var(--line);padding:6px 0}.en{font-weight:600}
.igl{display:flex;flex-wrap:wrap;gap:2px 14px;margin:3px 0}.igl>div{display:flex;flex-direction:column}.igl .f{font-size:16px}.igl .g{font-size:12px}
.sc{font-variant:small-caps;text-transform:lowercase;letter-spacing:.03em;color:var(--sc)}
.l2{font-size:13px;color:var(--muted)}.note{font-size:12px;color:var(--muted)}
details{border:1px solid var(--line);background:var(--card);border-radius:6px;padding:4px 10px;margin:4px 0}summary{cursor:pointer;font-weight:600}
.ex{margin:2px 0 6px 8px}
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:6px 10px}
@media (max-width:700px){.two{grid-template-columns:minmax(0,1fr)}main{padding:8px 16px 40px}nav{flex-wrap:nowrap;overflow-x:auto}nav button{white-space:nowrap}}
.sent,.notes,details,.line{min-width:0;overflow-wrap:anywhere}
.scroll{overflow-x:auto;max-width:100%}
table{border-collapse:collapse}.chart th,.chart td,.t th,.t td{border:1px solid var(--line);padding:2px 6px;font-size:13px;text-align:left}
.chart td{font-size:15px}.chart th{white-space:nowrap}.chart{margin-bottom:6px}.t{margin:4px 0}.words{width:100%}.fam{margin:4px 0 8px}
"""

JS = """
(function(){
var A=JSON.parse(document.getElementById('clips').textContent);
var cur=null,curBtn=null,queue=[];
function stop(){if(cur){cur.pause();cur=null}if(curBtn){curBtn.classList.remove('playing','busy');curBtn=null}queue=[]}
function playOne(id,btn,next){
  if(cur){cur.pause()} if(curBtn)curBtn.classList.remove('playing','busy');
  var a=new Audio(A[id]);cur=a;curBtn=btn;btn.classList.add('busy');
  a.onplaying=function(){btn.classList.remove('busy');btn.classList.add('playing')};
  a.onended=function(){btn.classList.remove('playing');if(cur===a){cur=null;curBtn=null}if(next)next()};
  a.onerror=function(){btn.classList.remove('busy','playing');btn.title='could not play'};
  var p=a.play();if(p&&p.catch)p.catch(function(){btn.classList.remove('busy')});
}
document.addEventListener('click',function(e){
  var b=e.target.closest('button');if(!b)return;
  if(b.dataset.lang!==undefined){show(+b.dataset.lang);return}
  if(b.classList.contains('all')){
    if(b===curBtn||b.classList.contains('playing')){stop();b.classList.remove('playing');return}
    stop();var ids=[].slice.call(document.querySelectorAll('#L'+b.dataset.k+' .sent .say')).map(function(x){return x.dataset.a});
    b.classList.add('playing');var i=0;
    (function step(){if(i>=ids.length||!b.classList.contains('playing')){b.classList.remove('playing');return}
      var id=ids[i++];var a=new Audio(A[id]);cur=a;a.onended=function(){setTimeout(step,350)};a.play()})();
    return}
  if(b.dataset.a){if(b===curBtn){stop();return}stop();playOne(b.dataset.a,b)}
});
function show(k){stop();[].forEach.call(document.querySelectorAll('.lang'),function(s){s.classList.toggle('on',+s.dataset.k===k)});
  [].forEach.call(document.querySelectorAll('nav button'),function(b){b.classList.toggle('on',+b.dataset.lang===k)});
  try{history.replaceState(null,'','#L'+k)}catch(e){}window.scrollTo(0,0)}
var m=/^#L(\\d+)$/.exec(location.hash||'');show(m?+m[1]:0);
})();
"""


def build(src: str, run_json: str | None, n: int, backend: str, audio: bool) -> tuple[str, dict]:
    d = json.loads(Path(src).read_text(encoding="utf-8"))
    doc = SK.Doc(d)
    if run_json and Path(run_json).is_file():
        meta = json.loads(Path(run_json).read_text(encoding="utf-8")).get("meta") or {}
        names = {x["id"]: x.get("name") or x["id"] for x in meta.get("lineages") or []}
        SK.people = lambda p, _n=names: (_n.get(p) or p.replace("_", " "))  # noqa: E731 (page-local people names)
    for l in doc.living:
        if not l.get("sentences"):
            SN.enrich(l)
    picks = pick(doc, n)
    au = Audio(backend, audio)
    try:
        secs, nav = [], []
        for k, (head, l, why) in enumerate(picks):
            print(f"  {l['id']} {l['people']}: {head}", file=sys.stderr)
            secs.append(lang_section(doc, l, head, why, au, k))
            nm = doc.deme_name(l)
            nav.append(f"<button data-lang='{k}'>{E(nm['roman'] if nm else l['id'])} "
                       f"<span class='muted'>{E(SK.people(l['people']))}</span></button>")
    finally:
        au.close()
    voice = (f"Audio made by the {au.backend} voice ({'eSpeak NG, a formant synthesizer: robotic but exact' if au.backend == 'espeak' else 'Piper, a neural voice: more natural, a little less exact'}), "
             f"embedded as {au.codec}; each people's voice profile (pitch, rate, non-human sounds) applied."
             if au.backend else "No audio: this page was written without a speech backend.")
    clips = json.dumps(au.clips).replace("</", "<\\/")
    page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Invented Languages Demo</title><style>{CSS}</style></head><body><main>"
            f"<h1>{len(picks)} languages of run {E(str(d.get('run', '?')))}</h1>"
            f"<p class='muted'>Very different living languages from a simulated world ({len(doc.living)} spoken now), each "
            f"grown by sound change, borrowing and grammaticalization from its people's history. Glosses follow the Leipzig "
            f"rules: - joins an affix, = a clitic, category labels in small caps. Press ▶ to hear a form. {E(voice)}</p>"
            f"<nav>{''.join(nav)}</nav>{''.join(secs)}"
            f"<p class='muted'>Written by tools/language/demo_page.py from {E(Path(src).name)}.</p></main>"
            f"<script type='application/json' id='clips'>{clips}</script><script>{JS}</script></body></html>")
    return page, {"languages": [(l["id"], l["people"], h) for h, l, _w in picks], "clips": len(au.clips),
                  "backend": au.backend, "codec": au.codec, "failed": au.failed}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("languages")
    ap.add_argument("--out", required=True, help="the HTML file to write")
    ap.add_argument("--run", help="the run's run.json, for people names (default: next to the languages file)")
    ap.add_argument("--n", type=int, default=10, help="how many languages (8-12 suits a phone)")
    ap.add_argument("--backend", default="auto", choices=["auto", "espeak", "piper"])
    ap.add_argument("--no-audio", action="store_true")
    a = ap.parse_args(argv)
    run_json = a.run or str(Path(a.languages).with_name("run.json"))
    page, info = build(a.languages, run_json, a.n, a.backend, not a.no_audio)
    Path(a.out).write_text(page, encoding="utf-8")
    print(f"wrote {a.out}: {len(page.encode()) / 1e6:.1f} MB, {len(info['languages'])} languages, {info['clips']} clips "
          f"({info['backend'] or 'no audio'}{', ' + info['codec'] if info['codec'] else ''}; {info['failed']} unsayable)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
