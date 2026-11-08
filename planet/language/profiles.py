"""Voice profiles (architecture.md section 3): how a species makes and hears the shared percept space.

A profile says, per percept-class key, how much dearer a sound is to make than for a human (a multiplier on the human cost,
inf = impossible), and per axis how finely the species hears it (1 human, 0 not heard, 2 twice as fine). Profiles are
resolved along the lineage tree: data/voice_profiles.toml gives tables per stem and kind, a lineage's own `voice` table in the
spec overrides, key by key, down the first-parent chain. Anything unresolved is the human default, flagged as such.

Human cost per segment comes from PHOIBLE (planet/language/data/phoible_segments.tsv when present, else a built-in snapshot
of its 120 commonest segments): cost = -ln(share of the world's inventories holding it), clamped to [0.1, 8]; never attested
-> 8; harsh (epiglottalized) phonation -> the modal sound's cost x HUMAN_HARSH plus the substitute surcharge
(species_cost); any other non-human percept -> inf.

Hearing: `hear` holds axis multipliers for distance, plus two audibility keys, `sub` and `ultra`: whether a percept carried in
the sub-bass (register -1) or ultra (register +1) reaches the listener at all (0 = no). A segment the listener cannot hear is
dropped by hear_word; an ordinary axis heard at 0 is ignored (the listener maps to the nearest sound regardless of it), not
dropped - otherwise a non-tonal ear would lose every toned vowel.
"""
from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable

from planet.language.percepts import AXES, Segment, distance, is_nonhuman, parse_segment

DATA = Path(__file__).parent / "data"
INF = math.inf
COST_MIN, COST_MAX = 0.1, 8.0
DROP_DISTANCE = 8.0

ARTICULATORS = ("lips", "teeth", "tongue_tip", "tongue_body", "tongue_root", "velum", "larynx", "pharynx", "syrinx", "beak")
HUMAN_ARTICULATORS = frozenset(("lips", "teeth", "tongue_tip", "tongue_body", "tongue_root", "velum", "larynx", "pharynx"))
PLACE_KEYS = ("labial", "dental", "alveolar", "postalveolar", "palatal", "velar", "uvular", "pharyngeal", "glottal")
MANNER_KEYS = ("stop", "affricate", "fricative", "nasal", "approximant", "lateral", "trill", "tap", "click", "percussive")
PERCEPT_KEYS = PLACE_KEYS + MANNER_KEYS + (
    "voiced", "aspirated", "ejective", "implosive", "breathy", "creaky", "harsh", "purr", "labialized", "palatalized",
    "velarized", "pharyngealized", "sibilant", "retroflex", "labiodental", "prenasal", "double",
    "round_vowel", "nasal_vowel", "front_vowel", "back_vowel", "high_vowel", "low_vowel", "tone", "long",
    "source2", "sub_register", "ultra_register")
HEAR_KEYS = AXES + ("sub", "ultra")
VOICE_KEYS = ("modality", "articulators", "make_cost", "hear", "register", "notes", "sources", "same_as_human")
MODALITIES = ("spoken", "signed")
NONHUMAN_KEYS = ("harsh", "purr", "percussive", "source2", "sub_register", "ultra_register")


@dataclass
class VoiceProfile:
    id: str
    source: str  # human_default | data_file | spec
    modality: str = "spoken"
    articulators: frozenset = HUMAN_ARTICULATORS
    make_cost: dict = field(default_factory=dict)
    hear: dict = field(default_factory=dict)
    register: int = 0  # habitual voice pitch vs human, in rough octaves (-2 dragons .. +1 small folk); descriptive
    notes: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    chain: list = field(default_factory=list)  # [(lineage id, "data_file" | "spec")] that contributed, root first

    def hear_weights(self) -> dict[str, float]:
        """Axis weights for percepts.distance (the audibility keys left out)."""
        return {k: v for k, v in self.hear.items() if k in AXES}

    def hears(self, seg: Segment) -> bool:
        """Does the percept reach this listener at all (sub-bass and ultra registers)?"""
        if seg.register < 0:
            return self.hear.get("sub", 1.0) > 0
        if seg.register > 0:
            return self.hear.get("ultra", 1.0) > 0
        return True

    def to_json(self) -> dict:
        return {"source": self.source, "modality": self.modality, "articulators": sorted(self.articulators),
                "make_cost": {k: ("inf" if math.isinf(v) else v) for k, v in sorted(self.make_cost.items())},
                "hear": dict(sorted(self.hear.items())), "register": self.register, "notes": list(self.notes),
                "sources": list(self.sources), "chain": [list(c) for c in self.chain]}


# Harsh (epiglottalized, ventricular) phonation: human voices make it and a few languages contrast it (the !Xóõ
# epiglottalized vowels; Bai's harsh-voiced tones), so it is very dear rather than impossible. Purr, a second source and the
# sub-bass / ultra registers stay impossible. 30, not 8: inventory adds harsh variants of the commonest sonorants and vowels
# at 0.25 x their share / make_cost, so x8 put a growled sound in ~14% of human proto-inventories; x30 gives ~2%, near the
# share of languages with epiglottalized or harsh-voiced phonemes.
HUMAN_HARSH = 30.0
HUMAN = VoiceProfile(
    id="human_default", source="human_default",
    make_cost={**{k: INF for k in NONHUMAN_KEYS}, "harsh": HUMAN_HARSH},
    hear={"source2": 0.3, "sub": 0.0, "ultra": 0.0},
    notes=["Human default: costs from PHOIBLE frequencies; harsh (epiglottalized) voice very dear (x30: contrastive in a few "
           "languages, !Xóõ, Bai); no purr, percussive, second voice or sub-bass/ultra speech; "
           "a second simultaneous voice is heard only faintly, as timbre; nothing below ~20 Hz or above ~20 kHz is heard."],
    sources=["Moran & McCloy (eds.) 2019, PHOIBLE 2.0 (opened: phoible/dev data/phoible.csv via planet/language/data/phoible_segments.tsv)"])


# ---- validation (shared with planet.lineages.spec.parse_voice) ------------------------------------------------------------

def _num(x, what: str, lid: str, allow_inf: bool) -> float:
    if isinstance(x, str) and x.strip().lower() == "inf" and allow_inf:
        return INF
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError(f"{lid}: voice.{what} must be a number{' or \"inf\"' if allow_inf else ''}")
    if x < 0 or (x == 0 and allow_inf):
        raise ValueError(f"{lid}: voice.{what} must be {'> 0' if allow_inf else '>= 0'}")
    return float(x)


def validate_voice(v, lid: str = "") -> dict:
    """Validate a voice table (only the keys given). make_cost values come back as floats (inf allowed); the caller keeps the
    raw table for round trips."""
    if v in (None, ""):
        return {}
    if not isinstance(v, dict):
        raise ValueError(f"{lid}: voice must be a table of {list(VOICE_KEYS)}")
    out: dict = {}
    for k, x in v.items():
        if k not in VOICE_KEYS:
            raise ValueError(f"{lid}: unknown voice key {k!r} (one of {list(VOICE_KEYS)})")
        if k == "modality":
            if x not in MODALITIES:
                raise ValueError(f"{lid}: voice.modality must be one of {list(MODALITIES)}")
            out[k] = x
        elif k == "articulators":
            xs = [x] if isinstance(x, str) else list(x)
            bad = [a for a in xs if a.lstrip("+-") not in ARTICULATORS]
            if bad:
                raise ValueError(f"{lid}: unknown articulators {bad} (one of {list(ARTICULATORS)}; +x / -x edit the parent's)")
            out[k] = xs
        elif k == "make_cost":
            if not isinstance(x, dict):
                raise ValueError(f"{lid}: voice.make_cost must be a table of percept keys")
            bad = [q for q in x if q not in PERCEPT_KEYS]
            if bad:
                raise ValueError(f"{lid}: unknown percept keys {bad} (one of {list(PERCEPT_KEYS)})")
            out[k] = {q: _num(y, f"make_cost.{q}", lid, True) for q, y in x.items()}
        elif k == "hear":
            if not isinstance(x, dict):
                raise ValueError(f"{lid}: voice.hear must be a table of axes")
            bad = [q for q in x if q not in HEAR_KEYS]
            if bad:
                raise ValueError(f"{lid}: unknown hear axes {bad} (one of {list(HEAR_KEYS)})")
            out[k] = {q: _num(y, f"hear.{q}", lid, False) for q, y in x.items()}
        elif k == "register":
            if isinstance(x, bool) or not isinstance(x, int) or not -3 <= x <= 3:
                raise ValueError(f"{lid}: voice.register must be an integer -3..3")
            out[k] = x
        elif k in ("notes", "sources"):
            xs = [x] if isinstance(x, str) else list(x)
            if not all(isinstance(s, str) for s in xs):
                raise ValueError(f"{lid}: voice.{k} must be a list of strings")
            out[k] = xs
        elif k == "same_as_human":
            if not isinstance(x, bool):
                raise ValueError(f"{lid}: voice.same_as_human must be true or false")
            out[k] = x
    return out


@lru_cache(maxsize=4)
def load_profiles(path: str | None = None) -> dict[str, dict]:
    """data/voice_profiles.toml, validated: lineage id -> voice table."""
    p = Path(path) if path else DATA / "voice_profiles.toml"
    raw = tomllib.loads(p.read_text(encoding="utf-8"))
    return {lid: validate_voice(t, f"voice_profiles.toml[{lid}]") for lid, t in raw.items()}


# ---- human cost -------------------------------------------------------------------------------------------------------------

# Fallback when phoible_segments.tsv is absent: the 120 commonest PHOIBLE segments (share of 2175 languages, one inventory per
# Glottocode), snapshot of that table on 2026-11-03.
BUILTIN_FREQ = {
    'm': 0.966, 'i': 0.936, 'k': 0.905, 'j': 0.901, 'u': 0.893, 'a': 0.888, 'p': 0.853, 'w': 0.846, 'n': 0.818, 't': 0.721,
    'l': 0.703, 's': 0.677, 'ŋ': 0.641, 'e': 0.625, 'b': 0.623, 'o': 0.614, 'ɡ': 0.565, 'h': 0.558, 'd': 0.476, 'r': 0.466,
    'f': 0.434, 'ɲ': 0.422, 't̠ʃ': 0.395, 'ʔ': 0.376, 'ɛ': 0.368, 'ɔ': 0.356, 'ʃ': 0.343, 'iː': 0.323, 'aː': 0.311,
    'uː': 0.299, 'z': 0.297, 'd̠ʒ': 0.274, 'v': 0.271, 'ɾ': 0.251, 't̪': 0.221, 'ts': 0.219, 'ə': 0.218, 'eː': 0.208,
    'oː': 0.207, '˦': 0.2, '˨': 0.198, 'ĩ': 0.178, 'kʰ': 0.17, 'x': 0.17, 'ã': 0.169, 'n̪': 0.165, 'pʰ': 0.16,
    'ɨ': 0.164, 'ũ': 0.163, 'ʈ': 0.155, 'ɪ': 0.143, 'ɳ': 0.141, 'ʒ': 0.14, 'kp': 0.139, 'ɡb': 0.138, 'ȵ': 0.137,
    'ɣ': 0.137, 'ʊ': 0.137, 'c': 0.134, 'ɭ': 0.13, 'kʷ': 0.125, 'tʰ': 0.124, 'd̪': 0.123, 'mb': 0.117, 'ɻ': 0.117,
    'ɟ': 0.116, 'ȶ': 0.111, 'β': 0.111, 'ɓ': 0.11, '˧': 0.109, 'ɛː': 0.109, 'nd': 0.109, 'ŋɡ': 0.109, 'õ': 0.108,
    'ɔː': 0.106, 'ɗ': 0.103, 'ẽ': 0.102, 'ɖ': 0.1, 'ʎ': 0.096, 'dz': 0.095, 'ɸ': 0.094, 'ɛ̃': 0.093, 'l̪': 0.091,
    'ɔ̃': 0.089, 'ð': 0.088, 'ʂ': 0.086, 'θ': 0.084, 'ɡʷ': 0.084, 'ɯ': 0.083, 'ɦ': 0.082, 'ç': 0.08, 'ʋ': 0.08,
    'tʃʰ': 0.079, 'χ': 0.077, 'ɕ': 0.076, 'q': 0.075, 'ŋm': 0.074, 'ʈʂ': 0.072, 'ɽ': 0.071, 'y': 0.07, 'æ': 0.069,
    'ø': 0.068, 'tsʰ': 0.067, 'ʁ': 0.064, 'ʕ': 0.062, 'ħ': 0.062, 'kʼ': 0.061, 'ɬ': 0.06, 'tɕ': 0.059, 'ʌ': 0.058,
    'ɑ': 0.058, 'ɐ': 0.056, 'ɤ': 0.055, 'tʼ': 0.054, 'pʼ': 0.051, 'ɹ': 0.05, 'ʉ': 0.049, 'tʃʼ': 0.047, 'qʼ': 0.04,
    'tsʼ': 0.04, 'dʑ': 0.039, 'ɵ': 0.035, 'ʝ': 0.03, 'ɢ': 0.03, 'ɮ': 0.02, 'tɬʼ': 0.02, 'ǃ': 0.01, 'ǀ': 0.01,
}


@lru_cache(maxsize=1)
def human_freq() -> tuple[dict[Segment, float], str]:
    """Segment -> share of the world's languages that have it, and where the numbers came from ("phoible_segments.tsv" or
    "builtin"). Several PHOIBLE symbols can map to one percept (n̺ and n); the commonest wins."""
    p = DATA / "phoible_segments.tsv"
    items: list[tuple[str, float]] = []
    src = "builtin"
    if p.exists():
        head = None
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if head is None:
                head = cols
                continue
            r = dict(zip(head, cols))
            items.append((r["segment"], float(r["frequency"])))
        src = "phoible_segments.tsv"
    else:
        items = list(BUILTIN_FREQ.items())
    out: dict[Segment, float] = {}
    for sym, f in items:
        s = parse_segment(sym)
        if s is not None and f > out.get(s, 0.0):
            out[s] = f
    return out, src


def _nonhuman_core(seg: Segment) -> Segment:
    """The human-makeable part of a percept (for the base of a non-human species' cost)."""
    return replace(seg, source2=0, register=0, phonation=0 if seg.phonation in (3, 4) else seg.phonation,
                   manner=0 if (seg.kind == "C" and seg.manner == 9) else seg.manner)


def _freq_cost(f: float | None) -> float:
    if not f:
        return COST_MAX
    return min(COST_MAX, max(COST_MIN, -math.log(f)))


def human_cost(seg: Segment) -> float:
    """-ln(PHOIBLE share), clamped to [0.1, 8]; 8 if never attested; harsh phonation as species_cost(HUMAN) (x HUMAN_HARSH);
    inf for any other non-human percept. A toned vowel costs its vowel plus its tone letter (PHOIBLE lists tones as separate
    segments)."""
    if seg.phonation == 3 and not (seg.source2 or seg.register or (seg.kind == "C" and seg.manner == 9)):
        return species_cost(HUMAN, seg)  # harsh voice: rare in human languages, dear (HUMAN_HARSH), not impossible
    if is_nonhuman(seg):
        return INF
    freq, _ = human_freq()
    if seg.kind == "V" and seg.tone:
        return min(COST_MAX, _freq_cost(freq.get(replace(seg, tone=0))) + _freq_cost(freq.get(Segment("T", tone=seg.tone))))
    return _freq_cost(freq.get(seg))


def keys_of(seg: Segment) -> frozenset[str]:
    """The percept-class keys a segment belongs to (the vocabulary of make_cost)."""
    k: set[str] = set()
    if seg.kind == "C":
        k.add(PLACE_KEYS[seg.place])
        if seg.double:
            k.update(("labial", "double"))
        k.add(MANNER_KEYS[seg.manner])
        if seg.lateral and seg.manner != 5:
            k.add("lateral")
        if seg.voice and seg.manner in (0, 1, 2, 8, 9):
            k.add("voiced")
        if seg.sibilant:
            k.add("sibilant")
        if seg.retroflex:
            k.add("retroflex")
        if seg.labiodental:
            k.add("labiodental")
        if seg.prenasal:
            k.add("prenasal")
        if seg.secondary:
            k.add(("labialized", "palatalized", "velarized", "pharyngealized")[seg.secondary - 1])
    elif seg.kind == "V":
        if seg.round:
            k.add("round_vowel")
        if seg.nasal:
            k.add("nasal_vowel")
        if seg.back <= 1:
            k.add("front_vowel")
        if seg.back >= 3:
            k.add("back_vowel")
        if seg.height >= 5:
            k.add("high_vowel")
        if seg.height <= 1:
            k.add("low_vowel")
    if seg.larynx:
        k.add(("aspirated", "ejective", "implosive")[seg.larynx - 1])
    if seg.phonation:
        k.add(("breathy", "creaky", "harsh", "purr")[seg.phonation - 1])
    if seg.tone or seg.kind == "T":
        k.add("tone")
    if seg.length:
        k.add("long")
    if seg.source2:
        k.add("source2")
    if seg.register < 0:
        k.add("sub_register")
    if seg.register > 0:
        k.add("ultra_register")
    return frozenset(k)


NONHUMAN_BASE = 2.0  # base cost of a percept with no human analogue (a percussive), before the species' multipliers
# A dearer-than-human sound is a substitute (a beak-made labial, a nasal without a velum): it costs effort however common the
# sound is among humans. So a multiplier m > 1 also adds SUBSTITUTE x (m - 1) to the cost; without it, x3 on m's near-floor
# human cost (-ln 0.97 = 0.1 -> 0.3) would hardly change how often aarakocra languages have labials.
SUBSTITUTE = 1.0


def species_cost(profile: VoiceProfile, seg: Segment) -> float:
    """human_cost of the segment's human-makeable core x m, the product of the profile's make_cost over keys_of(seg), plus
    SUBSTITUTE x (m - 1) when m > 1; inf wins. For HUMAN this equals human_cost (m = 1 on every human sound; the human
    make_cost is inf on the non-human keys and 8 on harsh phonation)."""
    core = _nonhuman_core(seg)
    base = NONHUMAN_BASE if (seg.kind == "C" and seg.manner == 9) else human_cost(core)
    m = 1.0
    for key in sorted(keys_of(seg)):   # (sorted: a float product in frozenset order varies with the str hash seed between
        c = profile.make_cost.get(key, 1.0)   # processes, and the ease drag makes it a rule weight)
        if math.isinf(c):
            return INF
        m *= c
    return base * m + SUBSTITUTE * max(0.0, m - 1.0)


# ---- resolution along the tree ------------------------------------------------------------------------------------------------

def _merge(p: VoiceProfile, t: dict, lid: str, src: str) -> None:
    if "modality" in t:
        p.modality = t["modality"]
    if "articulators" in t:
        xs = t["articulators"]
        if all(a[0] in "+-" for a in xs):
            arts = set(p.articulators)
            for a in xs:
                (arts.add if a[0] == "+" else arts.discard)(a[1:])
            p.articulators = frozenset(arts)
        else:
            p.articulators = frozenset(a.lstrip("+") for a in xs if not a.startswith("-"))
    if "make_cost" in t:
        p.make_cost.update(t["make_cost"])
    if "hear" in t:
        p.hear.update(t["hear"])
    if "register" in t:
        p.register = t["register"]
    p.notes.extend(f"{lid}: {n}" for n in t.get("notes", []))
    for s in t.get("sources", []):
        if s not in p.sources:
            p.sources.append(s)
    p.chain.append((lid, src))


def resolve_profile(lineage_id: str, parents_fn: Callable[[str], list[str]],
                    spec_voice_fn: Callable[[str], dict | None] | None = None, data: dict | None = None) -> VoiceProfile:
    """Walk the first-parent chain from the root down to `lineage_id`, merging key by key: for each line, its
    voice_profiles.toml table, then its spec `voice` table (the spec overrides). Starts from HUMAN. `source` is "spec" if any
    spec table contributed, else "data_file" if any data table did, else "human_default" (not yet profiled)."""
    data = load_profiles() if data is None else data
    chain, cur, seen = [], lineage_id, set()
    while cur is not None and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        ps = parents_fn(cur) or []
        cur = ps[0] if ps else None
    p = VoiceProfile(id=lineage_id, source="human_default", modality=HUMAN.modality, articulators=HUMAN.articulators,
                     make_cost=dict(HUMAN.make_cost), hear=dict(HUMAN.hear), register=HUMAN.register,
                     notes=list(HUMAN.notes), sources=list(HUMAN.sources))
    srcs = set()
    for lid in reversed(chain):
        if lid in data and data[lid]:
            _merge(p, data[lid], lid, "data_file")
            srcs.add("data_file")
        given = spec_voice_fn(lid) if spec_voice_fn else None
        if given:
            _merge(p, validate_voice(given, lid), lid, "spec")
            srcs.add("spec")
    p.source = "spec" if "spec" in srcs else ("data_file" if srcs else "human_default")
    return p


def profile_for(tree, lineage_id: str, data: dict | None = None) -> VoiceProfile:
    """resolve_profile over a planet.lineages.spec.Tree (groups follow their group_of, others their first parent)."""
    def parents(l: str) -> list[str]:
        ln = tree.lines.get(l)
        if ln is None:
            return []
        if ln.origin == "group" and getattr(ln, "group_of", None):
            return [ln.group_of]
        return list(ln.parents)

    def given(l: str):
        ln = tree.lines.get(l)
        return getattr(ln, "voice_given", None) if ln is not None else None
    return resolve_profile(lineage_id, parents, given, data)


# ---- nativization ---------------------------------------------------------------------------------------------------------------

def hear_word(word: Iterable[Segment], listener: VoiceProfile, inventory: list[Segment],
              drop_distance: float = DROP_DISTANCE) -> tuple:
    """Hear a word through a listener: each segment goes to the nearest segment of the listener's inventory by distance under
    the listener's hear weights; it is dropped when it does not reach the listener (an unheard register) or when even the
    nearest is farther than drop_distance. Phonotactic repair is the inventory module's (inventory.repair)."""
    w = listener.hear_weights()
    out = []
    for seg in word:
        if not listener.hears(seg):
            continue
        cands = [c for c in inventory if c.kind == seg.kind] or list(inventory)
        if not cands:
            continue
        best = min(cands, key=lambda c: (distance(seg, c, w), c.kind, tuple(getattr(c, a) for a in AXES)))
        if distance(seg, best, w) > drop_distance:
            continue
        out.append(best)
    return tuple(out)


# ---- human-voiced or not ---------------------------------------------------------------------------------------------------

def human_voiced(profile: VoiceProfile | None) -> bool:
    """A human vocal tract: the human articulators and no non-human percept it can make (harsh voice aside, which humans make
    at a high cost). Elves, dwarves, giants, orcs and the like are; dragons (sub-bass), kenku and aarakocra (syrinx, beak),
    the reptilian mouths (no lips) and the purring cats are not. What is easy for such a voice is what is common among human
    languages (PHOIBLE); for the others it is only their own make costs (rules.cost_factor)."""
    if profile is None:
        return True
    if frozenset(profile.articulators) != HUMAN_ARTICULATORS:
        return False
    return all(math.isinf(profile.make_cost.get(k, INF)) for k in NONHUMAN_KEYS if k != "harsh")
