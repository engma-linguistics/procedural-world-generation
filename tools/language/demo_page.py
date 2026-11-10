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

from planet.language import percepts as P  # noqa: E402
from planet.language import sentences as SN  # noqa: E402

E = html.escape
WORDS = ["MAN", "WOMAN", "CHILD (YOUNG HUMAN)", "MOTHER", "FATHER", "DOG", "FISH", "BIRD", "TREE", "WATER", "FIRE", "SUN",
         "MOON", "STONE", "HOUSE", "EAT", "DRINK", "SEE", "SLEEP", "SING", "BIG", "SMALL", "GOOD", "COLD", "ONE", "TWO",
         "THREE", "WHO", "WHAT", "NOT"]
SPOKEN_WORDS = 10  # of WORDS, with audio (besides pronouns)


def _bound(l):
    return sum(1 for g in l.get("grams") or [] if g.get("level", 0) >= 2)


def _proto_people(doc, l) -> str:
    """The people whose proto-language the lect descends from (a shifted people speaks another people's line)."""
    return doc.line(l["id"])[-1]["people"]


#: sample sentences that show the newer grammar (phases C and D); the picker prefers languages with more of them
NEWER = ("applicative", "voice_av", "voice_pv", "incorp", "reciprocal", "antipassive", "focus", "topic", "chain",
         "comparative", "polite", "mirative", "remote", "aspect", "obviative", "deixis")


NEWER_EN = {"voice_av": "voice and pivot", "voice_pv": "voice and pivot", "incorp": "noun incorporation",
            "chain": "switch-reference", "polite": "polite address", "remote": "graded tenses",
            "aspect": "more aspects", "obviative": "obviation", "deixis": "three-way demonstratives",
            "comparative": "comparison"}


def _newer(l) -> int:
    """How many of the newer constructions a language shows: NEWER sentences, an infix, concord beyond the adjective."""
    ids = {s["id"] for s in l.get("sentences") or []}
    proc = l.get("processes") or {}
    return (sum(1 for x in NEWER if x in ids) + (1 if proc.get("infix") else 0)
            + sum(1 for x in proc.get("concord") or [] if x in ("dem", "verb")))


DEMO_EXTRA = [
    ("most_spoken", "the most spoken language", lambda doc, l: True, lambda l: (l.get("population") or 0,),
     lambda l: f"about {_pop(l)} speakers"),
    # (an elvish or dwarvish language is one spoken by that people AND descended from that people's own proto-language)
    ("elvish", "an elvish language", lambda doc, l: SK.group(l["people"]) == "elf"
     and SK.group(_proto_people(doc, l)) == "elf", lambda l: (_newer(l), l.get("population") or 0),
     lambda l: f"spoken by {SK.people(l['people'])}"),
    ("dwarvish", "a dwarvish language", lambda doc, l: "dwar" in l["people"] and "dwar" in _proto_people(doc, l),
     lambda l: (_newer(l), l.get("population") or 0), lambda l: f"spoken by {SK.people(l['people'])}"),
    ("ergative", "an ergative language", lambda doc, l: (l.get("typology") or {}).get("alignment") == "erg-abs"
     and any(g["function"] == "ERG" for g in l.get("grams") or []), lambda l: (_newer(l), _bound(l)),
     lambda l: "the doer of a transitive verb is marked (ergative), the doer of an intransitive one is not"),
    ("newer", "the most of the newer grammar", lambda doc, l: True, lambda l: (_newer(l), l.get("population") or 0),
     lambda l: "shows " + ", ".join(dict.fromkeys(NEWER_EN.get(x, x) for x in NEWER
                                                  if x in {s["id"] for s in l.get("sentences") or []}))),
    ("synthetic", "the most affixes", lambda doc, l: True, lambda l: (_bound(l),),
     lambda l: f"{_bound(l)} live affixes"),
    ("isolating", "the fewest affixes", lambda doc, l: len(l.get("sentences") or []) >= 8, lambda l: (-_bound(l),),
     lambda l: f"{_bound(l)} live affixes: grammar by word order and separate words"),
]


def _pop(l) -> str:
    p = l.get("population") or 0
    return f"{p / 1e6:.2f} million" if p >= 1e6 else f"{p / 1e3:.0f} thousand" if p >= 1e3 else str(int(p))


def pick(doc, n: int) -> list[tuple[str, dict, str]]:
    """(why heading, lect, why text): sketch.py's picks and the most English-like, then DEMO_EXTRA, each from a people
    not shown yet (and a true family not shown yet when there is one)."""
    out = [(head, l, why) for _k, head, l, why in SK.pick(doc)]
    rank = SK.english_ranking(doc)
    used = {l["people"] for _h, l, _w in out}
    for s, l, _c in rank:
        if l["people"] not in used:
            out.append(("the most English-like language", l, f"English-likeness score {s:.2f}"))
            break
    for _k, head, ok, score, why in DEMO_EXTRA:
        if len(out) >= n:
            break
        used_p = {l["people"] for _h, l, _w in out}
        used_f = {l["family_true"] for _h, l, _w in out}
        cands = [l for l in doc.living if ok(doc, l) and l["people"] not in used_p and l.get("sentences")]
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


def play(cid: str | None, label: str = "", cls: str = "") -> str:
    if not cid:
        return ""
    return f"<button class='say{' lab' if label else ''}{' ' + cls if cls else ''}' data-a='{cid}' aria-label='play'>&#9654;{(' ' + E(label)) if label else ''}</button>"


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


def interlinear4(s: dict) -> str:
    """A text sentence in four lines: book spelling, IPA with morph breaks and gloss word by word, then the English."""
    fw, gw = [w[0] for w in s["w"]], [w[1] for w in s["w"]]
    bw = (s.get("roman") or "").split(" ")
    if len(bw) != len(fw):
        bw = [""] * len(fw)
    return ("<div class='igl'>" + "".join(f"<div><span class='b'>{E(b)}</span><span class='f ipa'>{E(f)}</span>"
                                          f"<span class='g'>{gloss_html(g)}</span></div>" for b, f, g in zip(bw, fw, gw))
            + f"</div><div class='l2'>‘{E(s['en'])}’</div>")


def text_lines(sents: list, l: dict, au: "Audio", tag: str) -> str:
    """A connected text: each sentence in four lines with its own play button (class `tag` for 'play all')."""
    out = []
    for s in sents:
        cid = au.clip(s["ipa"], l["people"], True)
        out.append(f"<div class='tx'>{play(cid, cls=tag)}{interlinear4(s)}</div>")
    return "".join(out)


def fable_section(doc, k: int, au: "Audio", picks: list) -> str | None:
    """The fable (planet/language/texts.py) in a proto-language and three of its living daughters, sentence by sentence
    side by side, each with audio: Schleicher's way of showing sound change and grammar change through one text."""
    from planet.language import texts as TX
    fam = TX.pick_family(doc.lects, doc.intel, tuple(l["people"] for _h, l, _w in picks), doc.d.get("fable_splits"))
    if fam is None:
        return None
    proto, ds = fam
    bad = TX.fable_descent(proto, ds, doc.d.get("roots") or {}, doc.lects, doc.d.get("etym_nodes"))
    if bad:   # (PW-1592: the page's reconstruction must hold; say so where the page is built)
        print(f"fable: the daughters do not all descend from the shown ancestor ({len(bad)}): " + "; ".join(bad[:4]),
              file=sys.stderr)
    lects = [proto] + ds
    tells = [TX.fable(l) for l in lects]

    def name(l):
        if l is proto:
            return f"their common ancestor ({doc.label(l.get('split_of') or l['id'], short=True)}, as it was then)"
        nm = doc.deme_name(l)
        return nm["roman"] if nm and l.get("parent") else doc.label(l["id"], short=True)
    age = f"{int(round(float(proto.get('died_kyr') or 0) * 10)) * 100:,} years"
    heads = []
    for j, l in enumerate(lects):
        when = (f"spoken by {SK.people(l['people'])} until about {age} ago, when it split into the lines below"
                if l is proto else f"spoken today by {SK.people(l['people'])}, about {_pop(l)}")
        first = next((c for c in (au.clip(s["ipa"], l["people"], True) for s in tells[j][:1]) if c), None)
        heads.append(f"<li><b>{E(name(l))}</b> <span class='muted'>({E(when)})</span> "
                     + (f"<button class='say lab all' data-sel='.fx{j}'>&#9654; the whole fable</button>" if first else "")
                     + "</li>")
    h = [f"<section class='lang' id='L{k}' data-k='{k}'><h2>A fable: {E(TX.FABLE_TITLE)}</h2>",
         f"<p>One short fable, the same in every language, told here in an ancestor language and in {len(ds)} of its "
         "living daughters, in the way August Schleicher wrote his fable of the sheep and the horses in reconstructed "
         f"Proto-Indo-European (1868). The ancestor was last spoken about {E(age)} ago"
         + (" (about as far back as Proto-Indo-European is from its daughters)" if 3.0 <= float(proto.get("died_kyr") or 0)
            <= 7.0 else "") + ", so many words are still shared: side by side, the same sentence shows what "
         "sound change did to them and what grammaticalization did to the grammar: markers that are separate words in "
         "the ancestor can be clitics or endings in the daughters, and new ones appear. Each sentence has four lines: "
         "the book spelling, the IPA with its morph breaks, the gloss and the English.</p>",
         "<p class='muted'>The English: " + E(" ".join(TX.FABLE_EN)) + "</p>",
         "<ul>" + "".join(heads) + "</ul>"]
    for i, en in enumerate(TX.FABLE_EN):
        h.append(f"<h3>({i + 1}) {E(en)}</h3><div class='fab'>")
        for j, (l, sents) in enumerate(zip(lects, tells)):
            s = next((x for x in sents if x["id"] == f"fable{i + 1}"), None)
            if s is None:
                continue
            h.append(f"<div class='card'><h4>{E(name(l))}</h4>{text_lines([s], l, au, f'fx{j}')}"
                     + (f"<div class='note'>{E(s['note'])}</div>" if s.get("note") else "") + "</div>")
        h.append("</div>")
    h.append("</section>")
    return "".join(h)


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
    R = doc.d.get("roots") or {}
    if field == "roots":   # (a speaker feels a family only while the shared part can be heard in each member)
        for r, f in fam.items():
            f["main"] = SK.felt_members(doc, lex, r, f["main"])
    # (polish lane: one word with several meanings, uncle = father's brother = mother's brother, is one word, not a
    # family; a family counts its distinct words, and the header counts what the cards show)
    for f in fam.values():
        by_form: dict = {}
        for c in sorted(f["main"]):
            by_form.setdefault(lex[c]["ipa"], []).append(c)
        f["forms"] = sorted(by_form.items(), key=lambda x: SK.cname(x[1][0]))
    big = sorted((x for x in fam.items() if len(x[1]["forms"]) >= 2), key=lambda x: (-len(x[1]["forms"]), str(x[0])))
    inside = {c for _r, f in big for c in f["main"]}
    n3 = sum(len(f["forms"]) >= 3 for _r, f in big)
    n2 = len(big) - n3
    out = [f"<p class='muted'>{n3} {'family' if n3 == 1 else 'families'} of 3+ words and {n2} of two; "
           f"{round(100 * len(inside) / max(1, len(lex)))}% of the {len(lex)} words share a root with another.</p>"]
    for r, f in big[:5]:
        info = R.get(r) or {}
        head = info.get("gloss") or SK.cname(str(r).split(":", 1)[-1].split("@")[0])
        words = ", ".join(" / ".join(E(SK.cname(c)) for c in cs) + f" <span class='ipa'>{E(ipa)}</span>"
                          for ipa, cs in f["forms"][:8])
        more = f" <span class='muted'>+{len(f['forms']) - 8}</span>" if len(f["forms"]) > 8 else ""
        star = f" <span class='ipa'>*{E(info['ipa'])}</span>" if info.get("ipa") else ""
        out.append(f"<div class='fam'><b>{E(str(head))}</b>{star} <span class='muted'>· {len(f['forms'])} words</span>"
                   f"<br>{words}{more}</div>")
    if not big:
        out.append("<p class='muted'>Every root has a single word here.</p>")
    return "".join(out)


def lineage(doc, l) -> str:
    line = []   # oldest first; a stage named as the one before it (a split that kept the deme) is folded into it, so no
    # language is listed as its own ancestor
    for x in doc.line(l["id"])[::-1]:
        nm = doc.label(x["id"], short=True)
        if line and line[-1][0] == nm:
            continue
        line.append((nm, x))
    steps = []
    names = [nm for nm, _x in line]
    for i, (nm, x) in enumerate(line):
        if i < len(line) - 6:
            continue
        lab = f"older speech of {nm}" if nm in names[i + 1:] else nm
        why = ""
        if x.get("how") == "shift" and i > 0:
            why = (f" <span class='muted'>(language shift: its speakers, {E(SK.people(x['people']))}, took up "
                   f"{E(line[i - 1][0])}'s language)</span>")
        elif i > 0 and x.get("people") != line[i - 1][1].get("people"):
            why = (f" <span class='muted'>(spoken now by {E(SK.people(x['people']))}, who took it from "
                   f"{E(SK.people(line[i - 1][1]['people']))})</span>")
        steps.append(f"<span class='step'>{E(lab)} <span class='muted'>{E(SK.kyr(x.get('born_kyr')))}</span>{why}</span>")
    hidden = f"<span class='muted'>… {len(line) - 6} older stages … </span>" if len(line) > 6 else ""
    sis = []
    for x in doc.living:
        if x["id"] != l["id"] and x.get("family_true") == l.get("family_true"):
            v = doc.intel.get((l["id"], x["id"]))
            sis.append((-(v or 0), x["id"], v))
    sis.sort()
    rel = ", ".join(f"{E(doc.label(i, short=True))} <span class=muted>("
                    + ("today's speech of a community it descends from; " if doc.label(i, short=True) in names else "")
                    + f"{f'{v:.0%}' if v else 'under 5%'} understood)</span>" for _s, i, v in sis[:4])
    # (the file keeps intelligibility only from 5% up: a missing pair is below that, not unknown)
    out = f"<div class='line'>{hidden}{' → '.join(steps)}</div>"
    fam_n = 1 + len(sis)
    out += (f"<p class='muted'>{fam_n} living languages in this true family. Closest living relatives: {rel}.</p>" if sis
            else "<p class='muted'>The only living language of its true family.</p>")
    return out


#: marks for sounds no human makes, beyond the IPA (percepts.py, symbols.tsv): what each one means on the page
HOUSE_MARKS = (("‼", "harsh, growled voice (the Voice Quality Symbols' mark); one ‼ after a vowel growls its whole syllable"),
               ("ᵣ", "purred voice, about 25 pulses a second"),
               ("ᴖ", "a second voice sounding at once, as a bird's syrinx makes two notes (house mark); tone letters after it are the second voice's own tone (high ˦, low ˨, rising ˨˦, falling ˦˨), those before it the first voice's"),
               ("˯", "sub-bass register, below human hearing (house mark)"),
               ("˰", "ultrasonic register, above human hearing (house mark)"),
               ("ʞ", "a beak or mandible clap (the withdrawn IPA letter, reused)"))


def house_marks(l, shown: str = "", whole: bool = True) -> str:
    """A key to the non-human sound marks this language's sounds use (`whole`), or its section shows (an old root
    reconstructed from a people with other mouths can carry one), or ''. With `whole` False only the marks in `shown`
    (a card that shows a few forms: PW-1537 R10, a key under forms that had none of the marks)."""
    inv = (l.get("inventory") or {}) if whole else {}
    segs = "".join((inv.get("consonants") or []) + (inv.get("vowels") or [])) + shown
    used = [(m, t) for m, t in HOUSE_MARKS if m in segs]
    if not used:
        return ""
    return ("<p class='muted'>Marks beyond the standard IPA in this language: "
            + "; ".join(f"<span class='ipa'>{E(m)}</span> {E(t)}" for m, t in used) + ".</p>")


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
         + "</div>", infobox(doc, l, why_head, why), "<!--MARKS-->", "<h3>Where it comes from</h3>", lineage(doc, l)]
    # sentences
    h.append("<h3>Sample sentences</h3>")
    for i, (s, cid) in enumerate(zip(sents, sc)):
        form, gloss = " ".join(w[0] for w in s["w"]), " ".join(w[1] for w in s["w"])
        h.append(f"<div class='sent'><div class='en'><span class='muted'>({i + 1})</span> ‘{E(s['en'])}’ {play(cid)}</div>"
                 f"{interlinear(form, gloss)}<div class='l2'><span class='ipa' title='as said: allophones and joins between words'>[{E(s['ipa'])}]</span> · "
                 f"<i>{E(s.get('roman') or '')}</i>{' · rising intonation' if s.get('q') else ''}</div>"
                 + (f"<div class='note'>{E(s['note'])}</div>" if s.get("note") else "") + "</div>")
    if not sents:
        h.append("<p class='muted'>Too few words of its own for the sample sentences.</p>")
    # a connected text: a short recipe in four lines (book spelling, IPA, gloss, English), with audio
    from planet.language import texts as TX
    title, rec = TX.recipe(l)
    if rec:
        h.append(f"<h3>A recipe: {E(title)}</h3><p class='muted'>A short connected text, each line in the book spelling, "
                 "the IPA with its morph breaks, the gloss and the English. The food is one of this people's own (from "
                 f"the world's cuisine data where the language has a word for it).</p>"
                 f"<div class='row'><button class='say lab all' data-sel='#L{k} .rx{k}'>&#9654; the whole recipe</button></div>"
                 + text_lines(rec, l, au, f"rx{k}"))
    title, my = SK.myth_of(doc, l)   # (the faith's myth: what the run's faith data holds, nothing added)
    if my:
        h.append(f"<h3>A myth: {E(title)}</h3><p class='muted'>What this people's faith data holds, told in the language: "
                 "each god's domain, the high god's gift, the foods forbidden because they belong to a god, and the "
                 "invocation. The run records no creation story or deeds, so none is told.</p>"
                 f"<div class='row'><button class='say lab all' data-sel='#L{k} .mx{k}'>&#9654; the whole myth</button></div>"
                 + text_lines(my, l, au, f"mx{k}"))
    # grammar
    h.append("<h3>The grammar in short</h3><div class='notes'>")
    for i, n in enumerate(l.get("grammar_notes") or []):
        exs = []
        for x in (n.get("ex") or [])[:4]:   # (every marker a note names has its example: sg/pl/du, 4 classes)
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
    out = "".join(h)
    return out.replace("<!--MARKS-->", house_marks(l, out), 1)


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
.fab{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:8px}.igl .b{font-weight:600;font-size:14px}
.tx{margin:2px 0 8px}
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
    stop();var ids=[].slice.call(document.querySelectorAll(b.dataset.sel||('#L'+b.dataset.k+' .sent .say'))).map(function(x){return x.dataset.a}).filter(Boolean);
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


# ---- languages getting more and less complex (Daniel, 2026-11-07) ------------------------------------------------------------
# The measure is the grammar's complexity score as each 0.5 kyr snapshot stores it (`cx`, grammar.complexity: bound
# functions + the mean bonding level of the live grams + 4 x the irregular share of the paradigm cells + 0.5 per bound class
# marker). A living lect's series runs back through its ancestors (`parent`): before its birth, the parent's snapshots
# (dead lects keep every 4th, so 2 kyr steps). The events are the differences between successive snapshots' live grams
# ([function, form, level]): a gram that appears was recruited, one that moves up a level bound or fused, one that drops
# out was lost. The causes read the lect's own L2 share, population and isolation (today's values: the file does not keep
# them per frame) and its language shifts.

CX_WINDOW = (0.5, 3.0)   # kyr: the change is read over the strongest window in this range ending now
CX_CLEAR = 1.0           # a change under this many points of the score is not "clear"
LEVEL_WORD = ("a free word", "a clitic", "an affix", "fused", "lost")


def _series(doc, l) -> list:
    """[(kyr, snapshot)] oldest first along the line of descent (the youngest lect holding each frame)."""
    from planet.language.history import snapshot_full
    line, x = [], l
    while x is not None:
        line.append(x)
        x = doc.lects.get(x.get("parent"))
    out: dict = {}
    for x in line:   # (the lect itself first: its own snapshots win)
        for kyr, sn in snapshot_full(x.get("snapshots") or []):
            out.setdefault(round(kyr, 3), (x["id"], sn))
    return sorted(((k, v[0], v[1]) for k, v in out.items()), key=lambda t: -t[0])


def _cx_change(ser) -> tuple[float, float, float] | None:
    """(delta, from kyr, cx then) over the strongest window of CX_WINDOW ending at the newest frame, or None."""
    if not ser or ser[-1][0] > 0.01 or ser[-1][2].get("cx") is None:
        return None
    now = ser[-1][2]["cx"]
    best = None
    for kyr, _lid, sn in ser:
        if CX_WINDOW[0] - 1e-6 <= kyr <= CX_WINDOW[1] + 1e-6 and sn.get("cx") is not None:
            dlt = now - sn["cx"]
            if best is None or abs(dlt) > abs(best[0]):
                best = (dlt, kyr, sn["cx"])
    return best


def _lab(fn: str) -> str:
    """A gram's function as the glosses write it (PAST -> PST, PERF -> PRF, EVID.REP -> REP, CLASS:2 -> CL2)."""
    return fn.replace("CLASS:", "CL") if fn.startswith("CLASS:") else SN.ABBR.get(fn, fn)


def _gform(g) -> str:
    """A gram [function, form, level] in words: '/li/, a clitic'; a fused gram with no segment of its own says so."""
    lv = LEVEL_WORD[min(g[2], 4)]
    return f"/{g[1]}/, {lv}" if g[1] else f"{lv}, no form of its own"


def _gram_events(ser, since: float) -> list:
    """[(kyr, kind, function, text)] from the snapshots' live grams after `since` kyr ago."""
    ev = []
    seq = [t for t in ser if t[0] <= since + 1e-6]   # (from the window's first frame on: earlier changes are not part of
    # the change read, and dated by the first frame they piled up there)
    for (k0, _a, s0), (k1, _b, s1) in zip(seq, seq[1:]):
        g0 = {g[0]: g for g in s0.get("grams") or []}
        g1 = {g[0]: g for g in s1.get("grams") or []}
        for fn in sorted(set(g0) | set(g1)):
            a, b = g0.get(fn), g1.get(fn)
            if a is None:
                ev.append((k1, "+", fn, f"{_lab(fn)} recruited: {_gform(b)}"))
            elif b is None:
                ev.append((k1, "-", fn, f"{_lab(fn)} lost (was {_gform(a)})"))
            elif b[2] > a[2]:
                ev.append((k1, "+", fn, f"{_lab(fn)} bound further: {_gform(a)} > {_gform(b)}"))
            elif b[2] < a[2]:
                ev.append((k1, "-", fn, f"{_lab(fn)} came loose: {_gform(a)} > {_gform(b)}"))
            elif a[1] != b[1] and a[1] and b[1]:
                ev.append((k1, "~", fn, f"{_lab(fn)} reshaped by sound change: /{a[1]}/ > /{b[1]}/"))
    return ev


def _spark(ser, since: float) -> str:
    """A small inline SVG of the score over the last 8 kyr, the window shaded."""
    pts = [(k, sn["cx"]) for k, _l, sn in ser if k <= 8.0 + 1e-6 and sn.get("cx") is not None]
    if len(pts) < 2:
        return ""
    W, H, P = 260, 70, 4
    lo, hi = min(v for _k, v in pts), max(v for _k, v in pts)
    hi = hi if hi > lo else lo + 1
    X = lambda k: P + (W - 2 * P) * (1 - k / 8.0)  # noqa: E731
    Y = lambda v: H - P - (H - 2 * P) * (v - lo) / (hi - lo)  # noqa: E731
    path = " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in pts)
    return (f"<svg viewBox='0 0 {W} {H + 14}' width='{W}' height='{H + 14}' role='img' aria-label='complexity score, last 8 kyr'>"
            f"<rect x='{X(since):.1f}' y='0' width='{X(0) - X(since):.1f}' height='{H}' fill='var(--line)' opacity='.6'/>"
            f"<polyline points='{path}' fill='none' stroke='var(--acc)' stroke-width='2'/>"
            f"<text x='{P}' y='{H + 12}' font-size='10' fill='var(--muted)'>8 kyr ago</text>"
            f"<text x='{W - P}' y='{H + 12}' font-size='10' fill='var(--muted)' text-anchor='end'>now</text>"
            f"<text x='{W - P}' y='10' font-size='10' fill='var(--muted)' text-anchor='end'>{hi:.1f}</text>"
            f"<text x='{W - P}' y='{H - 2}' font-size='10' fill='var(--muted)' text-anchor='end'>{lo:.1f}</text></svg>")


def _q(vals: list, x) -> float:
    vals = sorted(v for v in vals if v is not None)
    return sum(1 for v in vals if v <= x) / len(vals) if vals and x is not None else 0.5


def _rank(q: float) -> str:
    return "the highest of all living languages" if q >= 0.995 else f"above {q:.0%} of living languages"


SMALL_L2 = 0.15      # an adult-learner share at or below this is 'few adult learners'
SMALL_POP = 20_000   # a community this size or smaller is 'small' (Trudgill 2011's small societies: a few thousand)


def _cause(doc, l, rising: bool, since: float) -> str:
    liv = doc.living
    l2q, popq, isoq = (_q([x.get(k) for x in liv], l.get(k)) for k in ("l2", "population", "isolation"))
    bits = []
    shifts = [s for s in doc.d.get("shifts") or [] if s.get("to_lect") == l["id"] or s.get("from_lect") == l["id"]
              or s.get("deme") == l.get("deme")]
    recent = [s for s in shifts if s.get("kyr") is not None and 0.1 <= s["kyr"] <= since + 0.5]   # (inside the window:
    # a shift after the decline cannot explain it)
    facts = (f"L2 share {l.get('l2') or 0:.2f}, {_rank(l2q)}; {int(l.get('population') or 0):,} speakers, "
             f"{_rank(popq).replace(' of all living languages', '').replace(' of living languages', '')}; isolation "
             f"{l.get('isolation') or 0:.2f}, {_rank(isoq).replace(' of all living languages', '').replace(' of living languages', '')}")
    l2, pop = l.get("l2") or 0, int(l.get("population") or 0)
    # (the wording follows the values themselves, not only the rank among this world's languages: 'few adult learners'
    # needs a low share, 'small' a small number of speakers, Trudgill's societies of a few thousand)
    learners = ("few adult learners" if l2 <= SMALL_L2 else
                f"fewer adult learners than most languages here (share {l2:.2f})" if l2q <= 0.4 else None)
    small = pop <= SMALL_POP
    if rising:
        if learners and isoq >= 0.6 and small:
            bits.append(f"a small, isolated community with {learners}: grams are worn down and bound and few speakers "
                        "simplify them (Trudgill's small, isolated societies)")
        elif learners and isoq >= 0.6:
            bits.append(f"an isolated community with {learners} (though not a small one): what grammaticalization "
                        "binds stays bound")
        elif learners:
            bits.append(f"{learners}: what grammaticalization binds stays bound")
        elif small:
            bits.append("a small community, so new grams can spread and bind quickly")
        else:
            bits.append("nothing in its circumstances explains it (many adult learners, not isolated): the grams kept "
                        "being recruited and bound faster than they eroded, the drift's own momentum")
    else:
        if recent:
            s = recent[0]
            bits.append(f"its speakers shifted language {s['kyr']:g} kyr ago ({s.get('speakers') or '?'} under "
                        f"{s.get('ruler_people') or '?'}): adults learning a new language strip what they cannot master")
        if l2q >= 0.6 and l2 >= 0.3:
            bits.append("many adult second-language speakers (a contact or trade language): irregular and bound forms are "
                        "levelled, as in English after Norse contact or in Swahili")
        if popq >= 0.75:
            bits.append("a large, spread-out speech community")
        if not bits:
            bits.append("no strong outside pressure shows: erosion took markers faster than new ones were recruited")
    txt = "; ".join(bits)
    return f"{E(txt[:1].upper() + txt[1:])}. <span class='muted'>({E(facts)}, today's values)</span>"


def complexity_cases(doc, n_each: int = 3) -> tuple[list, list]:
    """(rising, falling): [(lect, delta, from kyr, cx then, cx now, series)], human-voiced first then one non-human,
    each from a different people and true family where possible."""
    rows = []
    for l in doc.living:
        ser = _series(doc, l)
        ch = _cx_change(ser)
        if ch is None or abs(ch[0]) < CX_CLEAR:
            continue
        rows.append((l, ch[0], ch[1], ch[2], ser[-1][2]["cx"], ser))
    def human(l) -> bool:   # (human-voiced: not the avian, reptilian or feline mouths; profiles.human_voiced)
        ch = ((doc.d.get("profiles") or {}).get(l["people"]) or {}).get("chain") or [[l["people"]]]
        return ch[0][0] not in ("avian", "reptilian", "feline")

    def pick(cands):
        out, seen_p, seen_f = [], set(), set()
        for want_h, k in ((True, n_each - 1), (False, 1)):
            for r in cands:
                l = r[0]
                if len([x for x in out if human(x[0]) == want_h]) >= k:
                    break
                if human(l) != want_h or l["people"] in seen_p or l.get("family_true") in seen_f:
                    continue
                out.append(r)
                seen_p.add(l["people"])
                seen_f.add(l.get("family_true"))
        return out
    rise = pick(sorted([r for r in rows if r[1] > 0], key=lambda r: (-r[1], r[0]["id"])))
    fall = pick(sorted([r for r in rows if r[1] < 0], key=lambda r: (r[1], r[0]["id"])))
    return rise, fall


def complexity_section(doc, k: int) -> str:
    rise, fall = complexity_cases(doc)
    h = [f"<section class='lang' id='L{k}' data-k='{k}'><h2>Languages getting more and less complex</h2>",
         "<p>Proto-languages start with few grams and mostly gain more, so a language whose grammar <b>shrinks</b> is the "
         "more telling case. The measure is the grammar's complexity score, stored every 500 years: bound functions + the mean bonding level of the live grams (free word 0, "
         "clitic 1, affix 2, fused 3) + 4 x the share of irregular paradigm cells + 0.5 per bound class marker. Each "
         "line follows the language back through the ancestors it split from; the shaded part is the stretch the "
         "change is measured over. The events below are the grams that came, went or bound further in that stretch. "
         "The likely cause is read from the language's share of adult learners, its number of speakers and its "
         "isolation as they are today, and from the language shifts in its history.</p>"]
    for title, rows, rising in (("Getting simpler", fall, False), ("Getting more complex", rise, True)):
        h.append(f"<h3>{title}</h3>")
        if not rows:
            h.append("<p class='muted'>No living language changed clearly in this direction over the last 0.5-3 kyr.</p>")
        for l, dlt, since, c0, c1, ser in rows:
            nm = doc.deme_name(l)
            name = nm["roman"] if nm else doc.label(l["id"], short=True)
            ev = _gram_events(ser, since)
            evh = "".join(f"<li><span class='muted'>{kyr:g} kyr ago</span> {'▲' if kind == '+' else '▼' if kind == '-' else '~'} "
                          f"<span class='ipa'>{E(t)}</span></li>" for kyr, kind, _fn, t in ev[:10])
            if len(ev) > 10:
                evh += f"<li class='muted'>... and {len(ev) - 10} more</li>"
            then = next((sn for kk, _l, sn in ser if abs(kk - since) < 1e-6), None)
            now = ser[-1][2]
            g0 = {g[0]: g for g in (then or {}).get("grams") or []}
            g1 = {g[0]: g for g in now.get("grams") or []}
            pairs = [fn for fn in sorted(set(g0) | set(g1)) if g0.get(fn) != g1.get(fn)][:4]
            ba = "".join(f"<tr><td class='sc'>{E(_lab(fn))}</td><td class='ipa'>"
                         f"{E(_gform(g0[fn])) if fn in g0 else '(none)'}</td>"
                         f"<td class='ipa'>{E(_gform(g1[fn])) if fn in g1 else '(none)'}</td></tr>"
                         for fn in pairs)
            dn = l.get("deme_name") or ""
            where = dn.split(" (", 1)[1].rstrip(")") if " (" in dn else ""
            h.append(f"<div class='card' style='margin:8px 0'><h4>{E(name)} <span class='muted'>{E(SK.people(l['people']))}"
                     + (f", {E(where)}" if where else "") + "</span></h4>"
                     f"<div class='two'><div>{_spark(ser, since)}<div class='note'>score {c0:.2f} {since:g} kyr ago &rarr; "
                     f"{c1:.2f} now ({'+' if dlt > 0 else ''}{dlt:.2f})</div></div>"
                     f"<div><b>Likely cause.</b> {_cause(doc, l, rising, since)}</div></div>"
                     + (f"<details open><summary>What changed ({len(ev)} gram events)</summary><ul>{evh}</ul></details>" if ev else
                        "<p class='note'>No gram came or went: the score moved through paradigm irregularity (sound change "
                        "made or levelled alternants).</p>")
                     + (f"<div class='scroll'><table class='t'><tr><th>gram</th><th>{since:g} kyr ago</th><th>now</th></tr>{ba}</table></div>"
                        if ba else "") + house_marks(l, evh + ba, whole=False) + "</div>")
    h.append("</section>")
    return "".join(h)


def build(src: str, run_json: str | None, n: int, backend: str, audio: bool, re_enrich: bool = False
          ) -> tuple[str, dict]:
    from planet.language import output as OU
    d = OU.load(src)
    doc = SK.Doc(d)
    if run_json and Path(run_json).is_file():
        meta = json.loads(Path(run_json).read_text(encoding="utf-8")).get("meta") or {}
        names = {x["id"]: x.get("name") or x["id"] for x in meta.get("lineages") or []}
        SK.people = lambda p, _n=names: (_n.get(p) or p.replace("_", " "))  # noqa: E731 (page-local people names)
    for l in doc.living:
        if re_enrich or not l.get("sentences"):
            SN.enrich(l)   # (re_enrich: the sentences and notes as today's sentences.py writes them, from the record)
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
        fab = fable_section(doc, len(picks), au, picks)   # (a tab: one fable in a proto-language and its daughters)
        if fab:
            secs.append(fab)
            nav.append(f"<button data-lang='{len(secs) - 1}'>A fable</button>")
        secs.append(complexity_section(doc, len(secs)))   # (one more tab: languages getting more and less complex)
        nav.append(f"<button data-lang='{len(secs) - 1}'>More and less complex</button>")
    finally:
        au.close()
    voice = (f"Audio made by the {au.backend} voice ({'eSpeak NG, a formant synthesizer: robotic but exact' if au.backend == 'espeak' else 'Piper, a neural voice: more natural, a little less exact'}), "
             f"embedded as {au.codec}; each people's voice profile (pitch, rate, non-human sounds) applied."
             if au.backend else "No audio: this page was written without a speech backend.")
    clips = json.dumps(au.clips).replace("</", "<\\/")
    page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Invented Languages Demo</title><style>{CSS}</style></head><body><main>"
            f"<h1>{len(picks)} invented languages from one simulated world</h1>"
            f"<p class='muted'>Very different living languages from a simulated world ({len(doc.living)} spoken now), each "
            f"grown by sound change, borrowing and grammaticalization from its people's history. Glosses follow the Leipzig "
            f"rules: - joins an affix, = a clitic, category labels in small caps. Press ▶ to hear a form. {E(voice)}</p>"
            f"<nav>{''.join(nav)}</nav>{P.page_growl(''.join(secs))}"   # (PW-1613: one growl per growled syllable)
            "</main>"
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
    ap.add_argument("--re-enrich", action="store_true",
                    help="rewrite every living lect's sentences and grammar notes with the current sentences.py")
    a = ap.parse_args(argv)
    run_json = a.run or str(Path(a.languages).with_name("run.json"))
    page, info = build(a.languages, run_json, a.n, a.backend, not a.no_audio, a.re_enrich)
    Path(a.out).write_text(page, encoding="utf-8")
    print(f"wrote {a.out}: {len(page.encode()) / 1e6:.1f} MB, {len(info['languages'])} languages, {info['clips']} clips "
          f"({info['backend'] or 'no audio'}{', ' + info['codec'] if info['codec'] else ''}; {info['failed']} unsayable)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
