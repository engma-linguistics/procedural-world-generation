"""The percept space (architecture.md section 2): every sound of every species stored as *heard*, as a record of small ordinal
axis values, with the IPA / extIPA / VoQS / house symbol table in data/symbols.tsv.

Axes beyond the contract (additive, default 0, so code written against section 2 keeps working): `retroflex`, `labiodental`,
`lateral`, `double` (labial-velar double articulation, k͡p, w) and `prenasal` (ᵐb). Without them PHOIBLE's commonest segments
collide (ʈ vs t̠, f vs ɸ, ɬ vs l̥, k͡p vs kʷ, ᵐb vs b); together they hold about 20% of the world's inventories.
`lateral` is 1 on every lateral, including l (manner 5 stays "lateral approximant" as the contract says).

Vowel height is the seven rows of the IPA chart: 0 open (a ɑ), 1 near-open (æ ɐ), 2 open-mid (ɛ ɔ), 3 mid (ə e̞), 4 close-mid
(e o), 5 near-close (ɪ ʊ), 6 close (i u). Backness 0 front, 1 near-front, 2 central, 3 near-back, 4 back.
Tone: 1 low, 2 mid, 3 high, 4 rising, 5 falling (contract) plus 6 extra-high and 7 extra-low; distance compares tones as
(onset, offset) pitch pairs, not as the raw integers.

Place distance is perceptual, not ordinal: it combines Jakobson's grave/acute and compact/diffuse with a small ordinal term,
so a labial is about as near a velar (both grave) as an alveolar. That is what makes labials go to velars, not dentals, when a
listener lacks them (kw > p, Romanian lupta < lucta; the parrot's labial substitutes are heard as labial-ish grave stops).
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field, fields, replace
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable

DATA = Path(__file__).parent / "data"


@dataclass(frozen=True, slots=True)
class Segment:
    kind: str  # "C" | "V" | "T" (standalone tone letter)
    place: int = 0  # 0 labial 1 dental 2 alveolar 3 postalveolar 4 palatal 5 velar 6 uvular 7 pharyngeal 8 glottal
    manner: int = 0  # 0 stop 1 affricate 2 fricative 3 nasal 4 approximant 5 lateral 6 trill 7 tap 8 click 9 percussive
    voice: int = 0  # 0 voiceless 1 voiced
    larynx: int = 0  # 0 plain 1 aspirated 2 ejective 3 implosive
    phonation: int = 0  # 0 modal 1 breathy 2 creaky 3 harsh (growl) 4 purr
    secondary: int = 0  # 0 none 1 labialized 2 palatalized 3 velarized 4 pharyngealized
    sibilant: int = 0
    height: int = 0  # vowels: 0 open .. 6 close
    back: int = 0  # vowels: 0 front .. 4 back
    round: int = 0
    nasal: int = 0  # nasalized (vowels; also nasalized approximants)
    length: int = 0  # long vowel / geminate
    tone: int = 0  # 0 none 1 low 2 mid 3 high 4 rising 5 falling 6 extra-high 7 extra-low
    source2: int = 0  # second simultaneous source (syrinx), non-human
    register: int = 0  # 0 human range, -1 sub-bass, +1 ultra, non-human
    retroflex: int = 0
    labiodental: int = 0
    lateral: int = 0
    double: int = 0  # labial-velar double articulation
    prenasal: int = 0
    # the hash, worked out once (finish lane, 2026-11-07): segments are dict keys and set members everywhere, and the
    # generated hash rebuilt a 20-field tuple on every lookup (a fifth of the pass's time). Same value as the generated
    # one, so set and dict behaviour is unchanged; not compared, not an init argument (replace() starts it afresh).
    _h: int = field(default=0, init=False, compare=False, repr=False)

    def __hash__(self):
        h = self._h
        if not h:
            h = hash((self.kind, self.place, self.manner, self.voice, self.larynx, self.phonation, self.secondary,
                      self.sibilant, self.height, self.back, self.round, self.nasal, self.length, self.tone, self.source2,
                      self.register, self.retroflex, self.labiodental, self.lateral, self.double, self.prenasal)) or 1
            object.__setattr__(self, "_h", h)
        return h


AXES: tuple[str, ...] = tuple(f.name for f in fields(Segment) if f.name not in ("kind", "_h"))
AXIS_RANGE: dict[str, tuple[int, int]] = {
    "place": (0, 8), "manner": (0, 9), "voice": (0, 1), "larynx": (0, 3), "phonation": (0, 4), "secondary": (0, 4),
    "sibilant": (0, 1), "height": (0, 6), "back": (0, 4), "round": (0, 1), "nasal": (0, 1), "length": (0, 1),
    "tone": (0, 7), "source2": (0, 1), "register": (-1, 1), "retroflex": (0, 1), "labiodental": (0, 1),
    "lateral": (0, 1), "double": (0, 1), "prenasal": (0, 1)}
# axes that mark a percept outside the human voice (human cost inf): checked by is_nonhuman
NONHUMAN = ("source2", "register")
Word = tuple  # tuple[Segment, ...]


def is_nonhuman(seg: Segment) -> bool:
    """A percept outside the ordinary human voice: a second source, a sub-bass or ultra register, harsh (growl) or purr
    phonation, percussives. Harsh voice is the one humans make too (rarely contrastive; profiles.HUMAN_HARSH)."""
    return bool(seg.source2 or seg.register or seg.phonation in (3, 4) or (seg.kind == "C" and seg.manner == 9))


# ---- the symbol table ------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Symbol:
    symbol: str
    seg: Segment
    source: str
    note: str


def _nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


@lru_cache(maxsize=1)
def symbols() -> tuple[Symbol, ...]:
    """The rows of data/symbols.tsv."""
    out = []
    head = None
    for line in (DATA / "symbols.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if head is None:
            head = cols
            continue
        r = dict(zip(head, cols + [""] * (len(head) - len(cols))))
        seg = Segment(r["kind"], **{a: int(r[a]) if r.get(a) else 0 for a in AXES})
        out.append(Symbol(unicodedata.normalize("NFC", r["symbol"]), seg, r["source"], r["note"]))
    return tuple(out)


# diacritics and modifiers (NFD code points) -> what they do
_COMBINING = {
    "̥": ("voice", 0), "̊": ("voice", 0), "̬": ("voice", 1), "̪": ("dental", 1),
    "̤": ("phonation", 1), "̰": ("phonation", 2), "̃": ("nasal", 1), "̴": ("secondary", 3),
    "̞": ("lower", 1), "̝": ("raise", 1), "̈": ("centre", 1), "̠": ("retract", 1), "̟": ("advance", 1),
    "́": ("tone", 3), "̀": ("tone", 1), "̄": ("tone", 2), "̌": ("tone", 4), "̂": ("tone", 5),
    "̋": ("tone", 6), "̏": ("tone", 7),
}
_COMBINING_IGNORED = set("̩̯̹̜̺̻̘̙̱̣̼̆̚͜͡")
_SPACING = {"ʰ": ("larynx", 1), "ʼ": ("larynx", 2), "ʱ": ("phonation", 1), "ʷ": ("secondary", 1), "ʲ": ("secondary", 2),
            "ˠ": ("secondary", 3), "ˤ": ("secondary", 4), "ː": ("length", 1), "‼": ("phonation", 3), "ᵣ": ("phonation", 4),
            "ᴖ": ("source2", 1), "˯": ("register", -1), "˰": ("register", 1)}
_SPACING_IGNORED = set("ˑ˞ⁿˡ")  # half-long, rhoticity, nasal and lateral release: not separate percepts here
_PRENASAL = set("ᵐⁿᵑᶬᶯᶮᶰ")
_TONE_LETTERS = {"˥": 5, "˦": 4, "˧": 3, "˨": 2, "˩": 1}  # pitch levels
_LEVEL_TONE = {5: 6, 4: 3, 3: 2, 2: 1, 1: 7}
_SEPARATORS = set(".ˈˌ‿ -‍|") - {"|"}
TIE, TIE_BELOW = "\u0361", "\u035c"
_ALIASES = [("ʦ", "ts"), ("ʣ", "dz"), ("ʧ", "tʃ"), ("ʤ", "dʒ"), ("ʨ", "tɕ"), ("ʥ", "dʑ"), ("g", "ɡ"), (":", "ː"),
            ("'", "ʼ"), ("’", "ʼ"), ("||", "ǁ"), ("‖", "ǁ"), ("|", "ǀ"), ("!", "ǃ"), ("ɚ", "ə"), ("ɝ", "ɜ"), ("ɩ", "ɪ"),
            ("ʇ", "ǀ"), ("ʗ", "ǃ"), ("ʖ", "ǁ")]


@lru_cache(maxsize=1)
def _tables():
    keys: dict[str, Segment] = {}
    base_keys: dict[str, Segment] = {}
    rev: dict[Segment, str] = {}
    modchars = set(_COMBINING) | set(_SPACING) | set(_TONE_LETTERS) | _PRENASAL
    for row in symbols():
        k = _nfd(row.symbol)
        rev.setdefault(row.seg, row.symbol)
        if any(ch in _TONE_LETTERS for ch in k):
            continue  # a vowel + tone letter row is a composition; parsing it whole would cut contours (a˦ + ˧)
        keys[k] = row.seg
        base = not any(ch in modchars for ch in k)
        if base:
            base_keys[k] = row.seg
        # affricates and other two-letter symbols accept a tie bar after the first letter (t͡s = ts)
        if len(k) >= 2 and TIE not in k and k[0] not in _PRENASAL and unicodedata.category(k[1]).startswith("L") \
                and k[1] not in _SPACING:
            for tie in (TIE, TIE_BELOW):
                keys[k[0] + tie + k[1:]] = row.seg
                if base:
                    base_keys[k[0] + tie + k[1:]] = row.seg
    return keys, base_keys, rev, max(map(len, keys))


def _normalize(s: str) -> str:
    s = _nfd(s)
    for a, b in _ALIASES:
        s = s.replace(a, b)
    s = s.replace("̠ʃ", "ʃ").replace("̠ʒ", "ʒ")  # PHOIBLE t̠ʃ, d̠ʒ
    return s


def _apply(seg: Segment, what: str, v: int) -> Segment:
    if what == "dental":  # t̪ dental; p̪ m̪ labiodental (the IPA's own use of the bridge on labials)
        if seg.kind == "C" and seg.place == 2:
            return replace(seg, place=1)
        return replace(seg, labiodental=1) if seg.kind == "C" and seg.place == 0 else seg
    if what in ("retract", "advance"):  # one step back / forward: place for consonants, backness for vowels
        step = 1 if what == "retract" else -1
        if seg.kind == "C":
            return replace(seg, place=min(8, max(0, seg.place + step)))
        if seg.kind == "V":
            return replace(seg, back=min(4, max(0, seg.back + step)))
        return seg
    if what == "nasal" and seg.kind == "C" and seg.manner == 0:
        # a nasalized stop is the (voiced) nasal of its place: ʔ̃ the glottal nasal; a ring above after it, ʔ̃̊, unvoices
        return replace(seg, manner=3, voice=1)
    if what == "lower":
        if seg.kind == "V":
            return replace(seg, height=max(0, seg.height - 1))
        return replace(seg, manner=4) if seg.manner == 2 else seg
    if what == "raise":
        if seg.kind == "V":
            return replace(seg, height=min(6, seg.height + 1))
        return replace(seg, manner=2) if seg.manner == 4 else seg
    if what == "centre":
        return replace(seg, back=2) if seg.kind == "V" else seg
    if what == "phonation" and v == 1:
        return replace(seg, phonation=1, voice=1)
    if what == "tone" and seg.kind != "V":
        return seg
    return replace(seg, **{what: v})


def _apply_escape(seg: Segment, body: str) -> Segment:
    """{axis=value,...}: the house escape to_ipa writes for an axis no IPA mark carries (a sibilant stop, a lateral trill);
    values are absolute."""
    d = {}
    for part in body.replace("ɡ", "g").split(","):  # _normalize turned g into IPA ɡ (lenɡth)
        ax, _, val = part.strip().partition("=")
        if ax in AXES and val.strip().lstrip("-").isdigit():
            d[ax] = int(val)
    return replace(seg, **d) if d else seg


def _tone_of(levels: list[int]) -> int:
    if len(levels) == 1 or levels[0] == levels[-1]:
        return _LEVEL_TONE[levels[0]]
    return 4 if levels[-1] > levels[0] else 5


def from_ipa(s: str, strict: bool = False, base_only: bool = False) -> list[Segment]:
    """Parse an IPA string into Segments: longest match over the symbol table, diacritics and modifier letters applied to the
    segment they follow (prenasal superscripts to the one they precede), tie bars optional, `ts`/`tʃ` as affricates.
    Tone letters after a vowel are its tone; elsewhere they are standalone "T" segments. Separators (. ˈ ˌ space) end a segment.
    Unknown characters are skipped (strict=True raises). base_only parses with the plain rows only (tests use it to check that
    the table's diacritic rows equal their composition)."""
    keys, base_keys, _, maxlen = _tables()
    table = base_keys if base_only else keys
    s = _normalize(s)
    out: list[Segment] = []
    i, n = 0, len(s)
    attach = False  # may a following modifier attach to out[-1]?
    pren = False
    while i < n:
        ch = s[i]
        if ch in _SEPARATORS:
            attach = False
            i += 1
            continue
        if ch in _PRENASAL and not attach:
            pren = True
            i += 1
            continue
        m = None
        for L in range(min(maxlen, n - i), 0, -1):
            if s[i:i + L] in table:
                m = L
                break
        if m is not None:
            seg = table[s[i:i + m]]
            if pren:
                seg = replace(seg, prenasal=1)
                pren = False
            out.append(seg)
            attach = True
            i += m
            continue
        if ch in _TONE_LETTERS:
            j = i
            while j < n and s[j] in _TONE_LETTERS:
                j += 1
            t = _tone_of([_TONE_LETTERS[c] for c in s[i:j]])
            if attach and out and out[-1].kind == "V":
                out[-1] = replace(out[-1], tone=t)
            else:
                out.append(Segment("T", tone=t))
                attach = False
            i = j
            continue
        if ch == "{" and "}" in s[i:]:
            j = s.index("}", i)
            if attach and out:
                out[-1] = _apply_escape(out[-1], s[i + 1:j])
            elif strict:
                raise ValueError(f"axis escape {s[i:j + 1]!r} with no segment before it in {s!r}")
            i = j + 1
            continue
        if attach and out and (ch in _COMBINING or ch in _SPACING):
            what, v = _COMBINING.get(ch) or _SPACING[ch]
            out[-1] = _apply(out[-1], what, v)
            i += 1
            continue
        if ch in _COMBINING_IGNORED or ch in _SPACING_IGNORED or ch in _COMBINING or ch in _SPACING:
            i += 1
            continue
        if strict:
            raise ValueError(f"unknown IPA character {ch!r} (U+{ord(ch):04X}) in {s!r}")
        i += 1
        attach = False
    return out


def _fold(segs: list[Segment]) -> list[Segment]:
    """Fold a PHOIBLE-style multi-letter segment: k+p, ɡ+b, ŋ+m into labial-velars, a nasal before an obstruent or click
    into prenasalization, a velar stop before a click into the click (every click has a velar or uvular rear closure)."""
    out = list(segs)
    changed = True
    while changed and len(out) > 1:
        changed = False
        for i in range(len(out) - 1):
            a, b = out[i], out[i + 1]
            if not (a.kind == b.kind == "C"):
                continue
            if a.place == 5 and b.place == 0 and a.manner == b.manner and a.manner in (0, 3) and not a.double:
                out[i:i + 2] = [replace(a, double=1, voice=max(a.voice, b.voice), prenasal=a.prenasal)]
            elif a.manner == 3 and b.manner in (0, 1, 2, 8) and not b.prenasal:
                out[i:i + 2] = [replace(b, prenasal=1)]
            elif b.manner == 8 and a.manner == 0 and a.place in (5, 6):
                out[i:i + 2] = [replace(b, voice=max(b.voice, a.voice))]
            else:
                continue
            changed = True
            break
    return out


def parse_segment(s: str) -> Segment | None:
    """One segment written as one string (PHOIBLE's convention): like from_ipa, but a nasal + obstruent reads as prenasalized
    (mb = ᵐb), k+p, ɡ+b, ŋ+m as labial-velar, k+ǃ as the click, a diacritic inside an affricate (t̪s̪, ɟ̤ʝ) as on the whole,
    and "a|b" (PHOIBLE's either-or) as its last alternative. None when it is not one segment (diphthongs)."""
    s = s.split("|")[-1].replace("R", "r")
    segs = _fold(from_ipa(s))
    if len(segs) != 1:
        d = _nfd(_normalize(s))
        marks = "".join(ch for ch in d[1:] if unicodedata.combining(ch))
        bare = d[0] + "".join(ch for ch in d[1:] if not unicodedata.combining(ch))
        segs = _fold(from_ipa(bare + marks))
    return segs[0] if len(segs) == 1 else None


_SEC_MARK = {1: "ʷ", 2: "ʲ", 3: "ˠ", 4: "ˤ"}
_TONE_MARK = {1: "˨", 2: "˧", 3: "˦", 4: "˨˦", 5: "˦˨", 6: "˥", 7: "˩"}
_PREN_MARK = {0: "ᵐ", 4: "ᶮ", 5: "ᵑ", 6: "ᶰ"}
_STRIP = ("register", "source2", "tone", "length", "phonation", "larynx", "secondary", "nasal", "prenasal")


def core(seg: Segment) -> Segment:
    """The segment without its modifiers (what a base letter writes): no register, second source, tone, length, phonation,
    aspiration or ejection (implosion stays: it has its own letters), secondary articulation, nasalization, prenasalization."""
    d = {a: 0 for a in _STRIP}
    if seg.larynx == 3:
        d.pop("larynx")
    return replace(seg, **d)


def _marks(seg: Segment, stripped: Iterable[str], flip: bool, dental: bool) -> tuple[str, str, str]:
    st = set(stripped)
    pre = comb = sp = ""
    if "prenasal" in st and seg.prenasal:
        pre = "ᵑ" if seg.manner == 8 else ("ᶯ" if seg.retroflex else _PREN_MARK.get(seg.place, "ⁿ"))
    if flip:
        comb += "̬" if seg.voice else "̥"
    if dental:
        comb += "̪"
    if "nasal" in st and seg.nasal:
        comb += "̃"
    if "phonation" in st and seg.phonation in (1, 2) and (seg.kind == "V" or seg.phonation == 2):
        comb += "̤" if seg.phonation == 1 else "̰"
    if "secondary" in st and seg.secondary:
        sp += _SEC_MARK[seg.secondary]
    if "larynx" in st and seg.larynx in (1, 2):
        sp += "ʰ" if seg.larynx == 1 else "ʼ"
    if "phonation" in st and seg.phonation == 1 and seg.kind == "C":
        sp += "ʱ"
    if "phonation" in st and seg.phonation in (3, 4):
        sp += "‼" if seg.phonation == 3 else "ᵣ"
    if "length" in st and seg.length:
        sp += "ː"
    if "tone" in st and seg.tone:
        sp += _TONE_MARK[seg.tone]
    if "source2" in st and seg.source2:
        sp += "ᴖ"
    if "register" in st and seg.register:
        sp += "˯" if seg.register < 0 else "˰"
    return pre, comb, sp


def _join(pre: str, base: str, comb: str, sp: str) -> str:
    # combining marks go after the whole base (ts̪ = dental affricate; t̪s would read as t̪ + s)
    return unicodedata.normalize("NFC", pre + _nfd(base) + comb + sp)


@lru_cache(maxsize=4096)
def to_ipa(seg: Segment) -> str:
    """The IPA for a segment: its table symbol, or a base symbol plus diacritics in a fixed order (prenasal, base, voicing,
    dental, nasal, breathy/creaky, secondary, aspiration/ejection, ʱ, ‼/ᵣ, ː, tone letters, ᴖ, ˯/˰).

    Injective: from_ipa(to_ipa(s)) == [s] for every Segment. A combination with no symbol takes the nearest base symbol plus
    marks for the difference (̝ ̞ raised/lowered vowel or fricative/approximant, ̟ ̠ advanced/retracted place or
    backness, ̃ nasal (on a stop: the nasal of that place, ʔ̃), ̥ ̬ voiceless/voiced, ̪ dental/labiodental), and
    what no IPA mark carries as a house escape {axis=value,...} after it (a sibilant stop, a lateral trill: rare)."""
    _, _, rev, _ = _tables()
    if seg in rev:
        return rev[seg]
    cur, stripped = seg, []
    first = None
    for ax in _STRIP:
        if getattr(cur, ax) and not (ax == "larynx" and cur.larynx == 3):
            cur = replace(cur, **{ax: 0})
            stripped.append(ax)
            if cur in rev:
                first = _join(*_parts(seg, rev[cur], stripped, False, False))
                break
    if first is None and seg.kind == "C":
        for flip, dental in ((True, False), (False, True), (True, True)):
            c = cur
            if flip:
                c = replace(c, voice=1 - c.voice)
            if dental:
                if c.place != 1:
                    continue
                c = replace(c, place=2)
            if c in rev:
                first = _join(*_parts(seg, rev[c], stripped, flip, dental))
                break
    if first is not None and from_ipa(first) == [seg]:
        return first
    pre, comb, sp = _marks(seg, stripped, False, False)
    bases = _base_rows(seg.kind)
    if not bases:  # a tone letter with a consonant axis set (never made by rules): escape everything
        return "˧{" + ",".join(f"{a}={getattr(seg, a)}" for a in AXES if getattr(seg, a)) + "}"
    ranked = sorted(bases, key=lambda r: distance(cur, r.seg))
    best = None
    for r in ranked[:24]:
        extra = _delta_marks(r.seg, cur)
        if extra is None:
            continue
        out = _join(pre, r.symbol, comb + extra, sp)
        if from_ipa(out) == [seg]:
            key = (len(extra), distance(cur, r.seg))
            if best is None or key < best[0]:
                best = (key, out)
    if best is not None:
        return best[1]
    out = _join(pre, ranked[0].symbol, comb, sp)
    got = from_ipa(out)
    if len(got) != 1:
        out, got = ranked[0].symbol, [ranked[0].seg]
    diff = [a for a in AXES if getattr(got[0], a) != getattr(seg, a)]
    out += "{" + ",".join(f"{a}={getattr(seg, a)}" for a in diff) + "}"
    assert from_ipa(out) == [seg], (seg, out)
    return out


@lru_cache(maxsize=4)
def _base_rows(kind: str) -> tuple[Symbol, ...]:
    return tuple(r for r in symbols() if r.seg.kind == kind and not _has_mods(r.symbol) and r.seg == core(r.seg)
                 and r.seg.larynx in (0, 3))


def _delta_marks(base: Segment, target: Segment) -> str | None:
    """IPA combining marks that turn `base` into `target` (both without strippable modifiers), or None when some axis has no
    mark. Order follows the parser's application order after canonical reordering (marks below, then marks above)."""
    below = above = ""
    stop_to_nasal = base.kind == "C" and (base.manner, target.manner) == (0, 3)
    if stop_to_nasal:  # ̃ also voices; the ring above (same canonical class, so it stays after) unvoices again
        above = "̃" + ("" if target.voice else "̊")
        base = replace(base, manner=3, voice=target.voice)
    for ax in AXES:
        x, y = getattr(base, ax), getattr(target, ax)
        if x == y:
            continue
        if ax == "voice":
            below += "̬" if y else "̥"
        elif ax == "place" and base.kind == "C" and abs(y - x) <= 2:
            below += ("̠" if y > x else "̟") * abs(y - x)
        elif ax == "back" and base.kind == "V":
            below += ("̠" if y > x else "̟") * abs(y - x)
        elif ax == "height" and base.kind == "V":
            below += ("̝" if y > x else "̞") * abs(y - x)
        elif ax == "manner" and base.kind == "C" and (x, y) == (4, 2):
            below += "̝"
        elif ax == "manner" and base.kind == "C" and (x, y) == (2, 4):
            below += "̞"
        elif ax == "labiodental" and y == 1 and base.kind == "C":
            below += "̪"
        else:
            return None
    return below + above


def _has_mods(sym: str) -> bool:
    k = _nfd(sym)
    return any(ch in _COMBINING or ch in _SPACING or ch in _TONE_LETTERS or ch in _PRENASAL for ch in k)


def _parts(seg, base, stripped, flip, dental):
    pre, comb, sp = _marks(seg, stripped, flip, dental)
    return pre, base, comb, sp


@lru_cache(maxsize=65536)
def _boundary_ok(a: Segment, b: Segment) -> bool:
    return from_ipa(to_ipa(a) + to_ipa(b)) == [a, b]


def word_ipa(word: Iterable[Segment]) -> str:
    """A word as IPA; a '.' goes between two segments only where plain juxtaposition would parse differently (t.s vs ts,
    a.˦ for a standalone tone after a vowel)."""
    w = tuple(word)
    out = []
    for i, s in enumerate(w):
        if i and not _boundary_ok(w[i - 1], s):
            out.append(".")
        out.append(to_ipa(s))
    return "".join(out)


# ---- distance --------------------------------------------------------------------------------------------------------------

KIND_PENALTY = 20.0
# place as heard: (grave, compact, ordinal). Jakobson, Fant & Halle 1952: labials and velars grave, dentals-palatals acute;
# palatals, velars and further back compact. Glottal is placed apart (no oral filter).
_PLACE = {0: (1.0, 0.0, 0), 1: (0.0, 0.0, 1), 2: (0.0, 0.0, 2), 3: (0.0, 1.0, 3), 4: (0.0, 1.0, 4), 5: (1.0, 1.0, 5),
          6: (1.0, 1.0, 6), 7: (1.0, 1.0, 7), 8: (0.5, 1.0, 9)}
_TONE_PITCH = {0: (3, 3), 1: (2, 2), 2: (3, 3), 3: (4, 4), 4: (2, 4), 5: (4, 2), 6: (5, 5), 7: (1, 1)}
_SCALE = {"height": 0.5, "back": 0.5, "labiodental": 0.5, "register": 2.0}


def place_distance(a: int, b: int) -> float:
    ga, ca, oa = _PLACE[a]
    gb, cb, ob = _PLACE[b]
    return 2.0 * abs(ga - gb) + abs(ca - cb) + 0.25 * abs(oa - ob)


def _axis_d(ax: str, x: int, y: int) -> float:
    if x == y:
        return 0.0
    if ax == "place":
        return place_distance(x, y)
    if ax == "manner":
        return float(min(abs(x - y), 3))
    if ax == "tone":
        (a1, a2), (b1, b2) = _TONE_PITCH[x], _TONE_PITCH[y]
        return 0.5 * (abs(a1 - b1) + abs(a2 - b2)) + (0.5 if (x == 0) != (y == 0) else 0.0)
    if ax == "larynx":
        return 1.0
    return _SCALE.get(ax, 1.0) * abs(x - y)


def distance(a: Segment, b: Segment, weights: dict[str, float] | None = None) -> float:
    """Weighted L1 over the axes as heard; `weights` (a listener's hear resolution) multiply each axis, 0 = not heard.
    A kind mismatch (consonant vs vowel vs tone) adds KIND_PENALTY."""
    d = KIND_PENALTY if a.kind != b.kind else 0.0
    for ax in AXES:
        x, y = getattr(a, ax), getattr(b, ax)
        if x != y:
            w = 1.0 if weights is None else weights.get(ax, 1.0)
            if w:
                d += w * _axis_d(ax, x, y)
    return d


# ---- natural classes -------------------------------------------------------------------------------------------------------

class ClassPred:
    """A natural-class predicate over Segment (callable), combinable with & | ~. EDGE matches the word edge (None)."""
    __slots__ = ("fn", "text", "edge", "focus")

    def __init__(self, fn: Callable[[Segment], bool], text: str, edge: bool = False, focus: bool = False):
        self.fn, self.text, self.edge, self.focus = fn, text, edge, focus

    def __call__(self, seg: Segment | None) -> bool:
        if seg is None:
            return self.edge
        return bool(self.fn(seg))

    def __and__(self, o: "ClassPred") -> "ClassPred":
        return ClassPred(lambda s: self.fn(s) and o.fn(s), f"{self.text}&{o.text}", self.edge and o.edge)

    def __or__(self, o: "ClassPred") -> "ClassPred":
        return ClassPred(lambda s: self.fn(s) or o.fn(s), f"{self.text}|{o.text}", self.edge or o.edge)

    def __invert__(self) -> "ClassPred":
        return ClassPred(lambda s: not self.fn(s), f"!{self.text}", not self.edge)

    def __repr__(self) -> str:
        return f"ClassPred({self.text})"


def is_C(s: Segment) -> bool:
    return s.kind == "C"


def is_V(s: Segment) -> bool:
    return s.kind == "V"


def is_T(s: Segment) -> bool:
    return s.kind == "T"


def is_liquid(s: Segment) -> bool:
    return s.kind == "C" and (s.manner in (5, 6, 7) or (s.manner == 4 and s.lateral) or (s.manner == 4 and 1 <= s.place <= 3 and not s.double))


def is_glide(s: Segment) -> bool:
    return s.kind == "C" and s.manner == 4 and not is_liquid(s)


NASAL_V = "V\u0303"  # Ṽ, nasal vowel
_ATOMS: dict[str, Callable[[Segment], bool]] = {
    "C": is_C, "V": is_V,
    "N": lambda s: s.kind == "C" and s.manner == 3,
    "P": lambda s: s.kind == "C" and s.manner == 0,
    "T": lambda s: s.kind == "C" and s.manner == 0 and not s.voice,  # voiceless stop (rule notation; not the tone kind)
    "D": lambda s: s.kind == "C" and s.manner == 0 and bool(s.voice),
    "A": lambda s: s.kind == "C" and s.manner == 1,
    "F": lambda s: s.kind == "C" and s.manner == 2,
    "S": lambda s: s.kind == "C" and bool(s.sibilant),
    "L": is_liquid, "G": is_glide,
    "K": lambda s: s.kind == "C" and s.manner == 8,
    NASAL_V: lambda s: s.kind == "V" and bool(s.nasal),
    "TONE": is_T,
}
_FEATURES: dict[str, Callable[[Segment], bool]] = {
    "voice": lambda s: bool(s.voice), "nasal": lambda s: (s.kind == "C" and s.manner == 3) or bool(s.nasal),
    "round": lambda s: bool(s.round) or (s.kind == "C" and (s.secondary == 1 or s.double)),
    "long": lambda s: bool(s.length), "sibilant": lambda s: bool(s.sibilant), "lateral": lambda s: bool(s.lateral),
    "retroflex": lambda s: bool(s.retroflex), "labiodental": lambda s: bool(s.labiodental), "double": lambda s: bool(s.double),
    "prenasal": lambda s: bool(s.prenasal), "aspirated": lambda s: s.larynx == 1, "ejective": lambda s: s.larynx == 2,
    "implosive": lambda s: s.larynx == 3, "breathy": lambda s: s.phonation == 1, "creaky": lambda s: s.phonation == 2,
    "harsh": lambda s: s.phonation == 3, "purr": lambda s: s.phonation == 4,
    "labialized": lambda s: s.secondary == 1, "palatalized": lambda s: s.secondary == 2,
    "velarized": lambda s: s.secondary == 3, "pharyngealized": lambda s: s.secondary == 4,
    "syllabic": is_V, "consonantal": is_C,
    "continuant": lambda s: s.kind == "V" or (s.kind == "C" and s.manner in (2, 4, 5, 6)),
    "sonorant": lambda s: s.kind == "V" or (s.kind == "C" and s.manner in (3, 4, 5, 6, 7)),
    "obstruent": lambda s: s.kind == "C" and s.manner in (0, 1, 2, 8, 9),
    "labial": lambda s: s.kind == "C" and (s.place == 0 or bool(s.double)),
    "coronal": lambda s: s.kind == "C" and 1 <= s.place <= 3,
    "dorsal": lambda s: s.kind == "C" and 4 <= s.place <= 6,
    "high": lambda s: s.kind == "V" and s.height >= 5, "low": lambda s: s.kind == "V" and s.height <= 1,
    "front": lambda s: s.kind == "V" and s.back <= 1, "back": lambda s: s.kind == "V" and s.back >= 3,
    "tone": lambda s: s.tone != 0, "source2": lambda s: bool(s.source2), "sub": lambda s: s.register < 0,
    "ultra": lambda s: s.register > 0,
}
EDGE = ClassPred(lambda s: False, "#", edge=True)
FOCUS = ClassPred(lambda s: True, "_", focus=True)
CLASSES: dict[str, ClassPred] = {k: ClassPred(f, k) for k, f in _ATOMS.items()}


def natural_class(**bounds) -> ClassPred:
    """A predicate from axis bounds: natural_class(kind="C", manner=0, place=(0, 1)) - ints are exact, (lo, hi) inclusive."""
    def fn(s: Segment) -> bool:
        for ax, b in bounds.items():
            v = getattr(s, ax)
            if isinstance(b, tuple):
                if not b[0] <= v <= b[1]:
                    return False
            elif v != b:
                return False
        return True
    return ClassPred(fn, ",".join(f"{k}={v}" for k, v in bounds.items()))


def _bracket(body: str) -> ClassPred:
    preds = []
    for part in (p.strip() for p in body.split(",") if p.strip()):
        part = part.replace("−", "-")
        if part[0] in "+-" and part[1:] in _FEATURES:
            f = _FEATURES[part[1:]]
            preds.append(ClassPred(f if part[0] == "+" else (lambda s, f=f: not f(s)), f"[{part}]"))
            continue
        neg = "!=" in part
        ax, _, val = part.partition("!=" if neg else "=")
        ax, val = ax.strip(), val.strip()
        if ax not in AXES and ax != "kind":
            raise ValueError(f"unknown feature or axis {ax!r} in [{body}]")
        if ax == "kind":
            p = natural_class(kind=val)
        elif ".." in val:
            lo, hi = (int(x) for x in val.split(".."))
            p = natural_class(**{ax: (lo, hi)})
        else:
            p = natural_class(**{ax: int(val)})
        preds.append(~p if neg else p)
    out = preds[0]
    for p in preds[1:]:
        out = out & p
    out.text = f"[{body}]"
    return out


def parse_class(text: str) -> ClassPred:
    """Parse the rule class notation: atoms C V N P T D A F S L G K Ṽ TONE, # (word edge), _ (the focus), feature brackets
    [+voice] [-voice] [+round,-long] [place=0..1] [manner=2] [place!=8]; juxtaposition or & intersects ("P[-voice]",
    "P & [-voice]"), | unites, a leading ! negates an atom."""
    t = _nfd(text.strip())
    if t == "#":
        return EDGE
    if t == "_":
        return FOCUS
    if "|" in t:
        parts = [parse_class(p) for p in t.split("|")]
        out = parts[0]
        for p in parts[1:]:
            out = out | p
        out.text = text.strip()
        return out
    preds, i, neg = [], 0, False
    while i < len(t):
        ch = t[i]
        if ch in " &":
            i += 1
            continue
        if ch == "!":
            neg = True
            i += 1
            continue
        if ch == "[":
            j = t.index("]", i)
            p = _bracket(t[i + 1:j])
            i = j + 1
        elif t.startswith("TONE", i):
            p, i = CLASSES["TONE"], i + 4
        elif t.startswith(NASAL_V, i):
            p, i = CLASSES[NASAL_V], i + len(NASAL_V)
        elif ch in _ATOMS:
            p, i = CLASSES[ch], i + 1
        elif ch == "#":
            p, i = EDGE, i + 1
        else:
            # a literal segment ("p", "tʃ"): matches exactly that percept
            j = i + 1
            while j < len(t) and t[j] not in " &[!":
                j += 1
            segs = from_ipa(t[i:j], strict=True)
            if len(segs) != 1:
                raise ValueError(f"class literal {t[i:j]!r} is not one segment")
            target = segs[0]
            p = ClassPred(lambda s, target=target: s == target, to_ipa(target))
            i = j
        preds.append(~p if neg else p)
        neg = False
    if not preds:
        raise ValueError(f"empty class {text!r}")
    out = preds[0]
    for p in preds[1:]:
        out = out & p
    out.text = text.strip()
    return out


# ---- sonority and syllables ------------------------------------------------------------------------------------------------

def SONORITY(seg: Segment) -> int:
    """V 10 > G 8 > L 7 > N 6 > voiced F 5 > F 4 > affricate 3 > voiced P 2 > P 1 (clicks, percussives 1; tone letters 0)."""
    if seg.kind == "V":
        return 10
    if seg.kind == "T":
        return 0
    m = seg.manner
    if m == 4:
        return 7 if is_liquid(seg) else 8
    if m in (5, 6, 7):
        return 7
    if m == 3:
        return 6
    if m == 2:
        return 5 if seg.voice else 4
    if m == 1:
        return 3
    if m == 0:
        return 2 if seg.voice else 1
    return 1


@dataclass(frozen=True)
class Syllable:
    onset: tuple
    nucleus: tuple
    coda: tuple

    @property
    def segments(self) -> tuple:
        return self.onset + self.nucleus + self.coda

    def shape(self) -> str:
        """e.g. 'CCVC' (a tone letter in the nucleus is not counted)."""
        return "C" * len(self.onset) + "V" * sum(1 for s in self.nucleus if s.kind != "T") + "C" * len(self.coda)


def syllabify(word: Iterable[Segment], sonority: Callable[[Segment], int] = SONORITY) -> list[Syllable]:
    """Split a word into syllables: every vowel is a nucleus (a tone letter joins the nucleus before it); with no vowel, the
    sonority peaks of nasal rank or higher are nuclei. Between two nuclei the onset is the longest stretch whose sonority rises
    strictly into the nucleus (maximal onset), the rest is the coda before."""
    w = tuple(word)
    if not w:
        return []
    son = [sonority(s) for s in w]
    nuc = [i for i, s in enumerate(w) if s.kind == "V"]
    if not nuc:
        nuc = [i for i in range(len(w)) if son[i] >= 6 and (i == 0 or son[i] >= son[i - 1]) and (i == len(w) - 1 or son[i] >= son[i + 1])]
        nuc = [i for k, i in enumerate(nuc) if not k or i != nuc[k - 1] + 1] or [max(range(len(w)), key=lambda i: son[i])]
    spans = []  # nucleus [start, end)
    for i in nuc:
        j = i + 1
        while j < len(w) and w[j].kind == "T":
            j += 1
        spans.append((i, j))
    out = []
    start = 0
    for k, (a, b) in enumerate(spans):
        nxt = spans[k + 1][0] if k + 1 < len(spans) else None
        onset = w[start:a]
        if nxt is None:
            coda = w[b:]
            out.append(Syllable(onset, w[a:b], coda))
            break
        cluster = list(range(b, nxt))
        cut = nxt  # onset of the next syllable starts at cut
        for j in reversed(cluster):
            right = son[j + 1] if j + 1 < nxt else son[nxt]
            if son[j] < right and w[j].kind != "T":
                cut = j
            else:
                break
        out.append(Syllable(onset, w[a:b], w[b:cut]))
        start = cut
    return out
