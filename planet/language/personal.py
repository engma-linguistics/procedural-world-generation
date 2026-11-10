"""Personal names and settlement names (names & spelling lane, 2026-11-08; names-spelling-gaps.md recs 8-11, 14).

Called from names._Pass.build; fills `names.personal` (per living lect) and each deme's `settlements`.

**Naming traditions.** Every proto lect draws a tradition: how a given name is made (`given`), what goes with it
(`byname`) and the order of the two (`order`). Each later lect inherits its parent's and, now and then (DRIFT per lect
step), redraws one field, so sister languages mostly share a tradition and distant ones differ. Given names:
- `dithematic` (Germanic Wil-helm, Slavic Vladi-mir): two themes from a closed pool fixed where the tradition began
  (THEMES_A first, THEMES_B second), compounded in the lect's head order;
- `phrase` (Yoruba Baba-tunde 'father has returned'): a subject and a verb in the lect's own order, run together;
- `single`: one meaningful word ('Wolf', 'Dove').
Bynames: `patronymic` / `matronymic` (the parent's name + the GEN gram + SON or DAUGHTER, in the lect's head order: a bound
GEN in a head-final lect fuses, Jón-s-son; a free one stands apart, mac X), `epithet` ('the Tall', after the name), `clan`
(an inherited clan name, family name first when `order` says so). With no GEN gram (none of a24559's living lects has one) the kin word and the parent's name compound in head order (Mac-X, Wil-son).

**Old names go opaque.** Each lect shows three names coined in its own line about OLD_NAME_KYR ago (by the lect spoken
then, or where its tradition began if that is later; sister lects share them, as William / Guillaume / Wilhelm) and three
coined now from its own words. An old name is the coiner's compound carried down: a theme whose root the lect
still has (by `etym_roots`) takes the lect's reflex of it (the name drifts with the word); a theme whose word the lect has
replaced keeps the old form as the lect hears it (a fossil: the name is now opaque, as -helm is in William); and an old
name is clipped toward two syllables with a chance growing with its age (Wilhelm > Bill). This approximates sound change on
names (the names are not run through the lect's rule history; architecture section 12).

**Settlements.** A living deme's largest standing sites (settlements.json, sites in the deme's cells now): a generic from
the lect's own words chosen by the site (FORD or BRIDGE on a river, COAST by the sea, HILL in the mountains, else TOWN,
VILLAGE, HOUSE, FENCE 'enclosure', FIELD) and a specific (a founder's personal name in the genitive, Kraków-style; the
river's name; a plain adjective). An old generic erodes to one syllable, a suffix (-ton, -by). A site founded by another
people keeps their name as heard (substrate, P2); sometimes the newcomers add their own generic to it, a tautology
(River Avon, Pendle Hill), more often when its meaning is lost.

Deterministic: every draw is names._rng(seed, ...). Taste calls are module constants (for the owner)."""
from __future__ import annotations

import numpy as np

from . import grammar as GR
from . import lexicon as LX
from . import romanize as RO
from .percepts import word_ipa

DRIFT = 0.12  # chance a lect redraws one field of its parent's naming tradition
GIVEN_W = {"dithematic": 0.5, "phrase": 0.25, "single": 0.25}
BYNAME_W = {"patronymic": 0.35, "matronymic": 0.1, "epithet": 0.25, "clan": 0.3}
FAMILY_FIRST = 0.5  # chance a clan tradition puts the family name first (Chinese, Hungarian)
THEMES_A = ("WOLF", "BEAR", "GOD", "HOLY", "PEACE", "WAR", "STRONG", "GOOD", "RICH", "SUN", "STAR", "STONE", "FIRE",
            "EAGLE", "SPEAR", "PEOPLE", "LAND", "HEART", "LOVE", "FRIEND", "GIFT", "SHINE", "OLD", "WHITE", "RED", "DEER",
            "HORN (ANATOMY)", "WATER", "SKY")
THEMES_B = ("KING", "CHIEF", "SPEAR", "SHIELD", "WOLF", "FRIEND", "PEACE", "FIGHT", "FIGHTER", "HELP", "STRONG", "GIFT",
            "HEART", "MIND", "MASTER", "STONE", "LIGHT (RADIATION)", "SONG", "HEAD")
POOL_A, POOL_B = 8, 6  # themes in a tradition's closed pool
PHRASES = (("GOD", "GIVE", "God gave"), ("FATHER", "RETURN HOME", "father has returned"), ("SUN", "RISE (MOVE UPWARDS)",
           "the sun rose"), ("GOD", "KNOW", "God knows"), ("CHILD (YOUNG HUMAN)", "COME", "the child came"),
           ("MOTHER", "LAUGH", "mother laughed"), ("RAIN (PRECIPITATION)", "COME", "the rain came"),
           ("SPIRIT", "RETURN HOME", "the spirit has come home"), ("WAR", "FINISH", "the war is over"),
           ("PEOPLE", "SING", "the people sing"))
SINGLE = ("WOLF", "BEAR", "DOVE", "EAGLE", "STAR", "FLOWER", "RAIN (PRECIPITATION)", "STONE", "SUN", "MOON", "DEER", "FOX",
          "SNOW", "FIRE", "SONG", "GIFT", "STRONG", "TALL", "CROW", "SPRING (OF WATER)")
EPITHETS = ("STRONG", "TALL", "RED", "BLACK", "WHITE", "OLD", "YOUNG", "CLEVER", "BLIND", "HAPPY", "BIG", "SMALL", "SHORT",
            "RICH", "POOR", "CALM", "BITTER")
CLANS = ("WOLF", "BEAR", "EAGLE", "DEER", "SNAKE", "CROW", "FOX", "OX", "STONE", "RIVER", "HILL", "FOREST", "HORN (ANATOMY)",
         "DOVE", "FIRE", "OAK", "SALT (FOOD)", "SPRING (OF WATER)")
OLD_NAME_KYR = 4.0  # old names were coined in the lect's line about this long ago (or where the tradition began, if later)
OPAQUE_KYR = 8.0  # an old name's chance of a hypocoristic clip reaches its cap at this age
OPAQUE_CAP = 0.6
N_OLD, N_NEW, N_BY = 3, 3, 2
# Name length by tradition (PW-1546 item 14): (syllables a theme keeps, syllables a given name keeps), both times the lect's
# length scale (names._name_caps), and themes a dithematic name joins. Chinese given names are one or two syllables, a
# morpheme each; Germanic dithematic names two themes, about four syllables; Malagasy names long compounds of whole words
# (Andrianampoinimerina 'the prince in the heart of Imerina'). The shares are a taste call (draft names-length).
NAME_LENGTH_W = {"short": 0.2, "mid": 0.6, "long": 0.2}
NAME_LENGTH = {"short": (1, 2, 2), "mid": (2, 4, 2), "long": (4, 9, 3)}
# settlements
SITES_PER_DEME = 3
SUBSTRATE_TAUTOLOGY = 0.25  # chance newcomers add their own generic to a kept old name they do not understand
SUFFIX_KYR = 3.0  # a generic older than this erodes to one syllable (a suffix)
GENERIC_BY_TIER = {"city": ("TOWN", "WALL (OF HOUSE)"), "town": ("TOWN", "MARKET", "FENCE"), "village": ("VILLAGE", "HOUSE",
                   "FIELD", "FENCE")}
SPECIFIC_ADJ = ("NEW", "OLD", "BIG", "SMALL", "WHITE", "RED", "BLACK", "HIGH", "LOW", "GOOD", "LONG")


# ------------------------------------------------------------------------------------------------------------- helpers
def _offends(lect, form) -> bool:
    """Would the name's raw spelling (either register) read as an English slur or obscenity (romanize.blocklist)?"""
    from .output import orthography
    try:
        return orthography(lect).offends(tuple(form)) is not None
    except Exception:   # noqa: BLE001 - a lect with no orthography: the spelling guard still breaks the match
        return False


def _w(lect, c):
    from .names import _word
    return _word(lect, c)


def _gloss(c: str) -> str:
    from .names import _gloss as g
    s = g(c)
    return s.split(" (")[0] if " (" in s and not s.startswith("(") else s  # (wall (of house) -> wall)


def _pick(rng, weights: dict) -> str:
    ks = sorted(weights)
    p = np.array([weights[k] for k in ks], float)
    return ks[int(rng.choice(len(ks), p=p / p.sum()))]


def _root_id(w):
    r = getattr(w, "etym_roots", None) or getattr(w, "roots", None) or ()
    return r[0] if r else None


def _head_final(lect) -> bool:
    g = getattr(lect, "grammar", None)
    try:
        return bool(g.typology.head_final()) if g is not None else bool(getattr(lect.lexicon, "head_first", False) is False)
    except Exception:
        return True


def _verb_first(lect) -> bool:
    g = getattr(lect, "grammar", None)
    try:
        return str(g.typology.get("word_order", "SOV")).startswith("V")
    except Exception:
        return False


def _ago(kyr: float) -> str:
    return "lately" if kyr < 0.25 else f"{kyr:.1f} kyr ago"


# ------------------------------------------------------------------------------------------------------------ the pass
class Personal:
    def __init__(self, P):
        self.P = P
        self.seed = P.seed
        self._trad: dict = {}

    def rng(self, *key):
        from .names import _rng
        return _rng(self.seed, "personal", *key)

    # ---------------------------------------------------------------- traditions
    def chain(self, lect) -> list:
        out, seen, x = [], set(), lect
        while x is not None and x.id not in seen:
            out.append(x)
            seen.add(x.id)
            x = self.P.lects.get(x.parent) if x.parent else None
        return out[::-1]  # root first

    def _fresh(self, lect, rng, field: str | None = None, t: dict | None = None) -> dict:
        t = dict(t or {})
        if field in (None, "given"):
            t["given"] = _pick(rng, GIVEN_W)
            a = [c for c in THEMES_A if _w(lect, c) is not None]
            b = [c for c in THEMES_B if _w(lect, c) is not None]
            t["themes_a"] = sorted(rng.choice(a, size=min(POOL_A, len(a)), replace=False).tolist()) if a else []
            t["themes_b"] = sorted(rng.choice(b, size=min(POOL_B, len(b)), replace=False).tolist()) if b else []
            t["origin"] = lect.id
        if field in (None, "byname"):
            t["byname"] = _pick(rng, BYNAME_W)
            cl = [c for c in CLANS if _w(lect, c) is not None]
            t["clans"] = sorted(rng.choice(cl, size=min(4, len(cl)), replace=False).tolist()) if cl else []
            t["byname_origin"] = lect.id
        if field in (None, "order"):
            t["order"] = "family_first" if rng.random() < FAMILY_FIRST else "given_first"
        if field in (None, "length"):
            t["length"] = _pick(rng, NAME_LENGTH_W)
        return t

    def caps(self, lect, t) -> tuple[int, int, int]:
        """(syllables a theme keeps, syllables a given name keeps, themes a dithematic name joins) by the tradition's
        name length (NAME_LENGTH), the syllable caps scaled as names._name_caps scales them."""
        from .names import _name_caps
        part, name, n = NAME_LENGTH[t.get("length") or "mid"]
        sc = _name_caps(lect)[1] / 4.0
        return max(1, round(part * sc)), max(2, round(name * sc)), n

    def tradition(self, lect) -> dict:
        if lect.id in self._trad:
            return self._trad[lect.id]
        t = None
        for x in self.chain(lect):
            if x.id in self._trad:
                t = self._trad[x.id]
                continue
            rng = self.rng("tradition", x.id)
            if t is None:
                t = self._fresh(x, rng)
                t["changed"] = None
            elif rng.random() < DRIFT:
                field = ("given", "byname", "order", "length")[int(rng.integers(4))]
                t = self._fresh(x, rng, field, t)
                t["changed"] = [x.id, field, round(float(x.born_kyr), 3)]
            self._trad[x.id] = t
        return t

    # ---------------------------------------------------------------- reflexes
    def reflex(self, lect, origin, concept: str) -> tuple[tuple, str]:
        """The lect's form of the origin lect's word for `concept` inside an old name, and how it got there."""
        w0 = _w(origin, concept)
        if w0 is None:
            return (), "missing"
        if origin is lect:
            return tuple(w0.form), "same"
        r0 = _root_id(w0)
        w = _w(lect, concept)
        if w is not None and r0 is not None and _root_id(w) == r0:
            return tuple(w.form), "kept"
        if r0 is not None:
            for c, x in sorted(lect.lexicon.words.items()):
                if len(x.form) and _root_id(x) == r0:
                    return tuple(x.form), f"now '{_gloss(c)}'"
        from .names import _hear
        return _hear(w0.form, lect), "lost"

    def _compound(self, lect, head, mod) -> tuple:
        from .names import _join
        return _join(lect, head, mod)

    def _erode(self, lect, form, age: float, key) -> tuple[tuple, bool]:
        from .names import _repair
        p = OPAQUE_CAP * min(1.0, max(0.0, age) / OPAQUE_KYR)
        if LX.syllables(form) > 2 and self.rng("erode", key).random() < p:
            return _repair(lect, LX.clip(tuple(form), 2)), True
        return tuple(form), False

    def spell(self, lect, form) -> tuple[str, str]:
        from .names import _roman_form
        return RO.title_name(_roman_form(lect, form)), word_ipa(form)

    def coiner(self, lect, t):
        """The lect old names were coined in: the one on the lect's line alive OLD_NAME_KYR ago, not before the tradition
        began (its origin), so sister lects share their old names."""
        ch = self.chain(lect)
        ids = [x.id for x in ch]
        start = ids.index(t["origin"]) if t["origin"] in ids else 0
        line = ch[start:]
        for x in line:
            if x.born_kyr + 1e-9 >= OLD_NAME_KYR and (x.died_kyr is None or x.died_kyr <= OLD_NAME_KYR + 1e-9):
                return x
        return line[0] if line[0].born_kyr < OLD_NAME_KYR else line[-1]

    @staticmethod
    def coined_kyr(x) -> float:
        """When an old name was coined in lect x: OLD_NAME_KYR ago if x was spoken then, else when x began."""
        if x.born_kyr + 1e-9 >= OLD_NAME_KYR and (x.died_kyr is None or x.died_kyr <= OLD_NAME_KYR + 1e-9):
            return OLD_NAME_KYR
        return float(x.born_kyr)

    # ---------------------------------------------------------------- given names
    def _given(self, lect, t, kind: str, i: int) -> dict | None:
        old = kind == "old"
        origin = self.coiner(lect, t) if old else lect
        if origin is None:
            return None
        rng = self.rng("given", origin.id, kind, i)
        st = t["given"]
        parts: list = []  # (concept, form in lect, how, origin form)
        if st == "dithematic":
            if not t["themes_a"] or not t["themes_b"]:
                return None
            a = t["themes_a"][int(rng.integers(len(t["themes_a"])))]
            b = [c for c in t["themes_b"] if c != a]
            if not b:
                return None
            b = b[int(rng.integers(len(b)))]
            cs = [a, b]
            more = [c for c in t["themes_a"] if c not in cs]
            for _ in range(self.caps(lect, t)[2] - 2):   # (a long tradition joins a third theme: PW-1546 item 14)
                if more:
                    cs.insert(-1, more.pop(int(rng.integers(len(more)))))
            gloss = "-".join(_gloss(c) for c in cs)
        elif st == "phrase":
            ok = [p for p in PHRASES if _w(origin, p[0]) is not None and _w(origin, p[1]) is not None]
            if not ok:
                return None
            s, v, gloss = ok[int(rng.integers(len(ok)))]
            cs = [v, s] if _verb_first(origin) else [s, v]
        else:
            ok = [c for c in SINGLE if _w(origin, c) is not None]
            if not ok:
                return None
            cs = [ok[int(rng.integers(len(ok)))]]
            gloss = _gloss(cs[0])
        part_cap, cap, _n = self.caps(lect, t)
        o_part = self.caps(origin, t)[0]
        for c in cs:
            f, how = self.reflex(lect, origin, c) if old else (tuple(_w(lect, c).form) if _w(lect, c) else (), "same")
            if not f:
                return None
            w0 = _w(origin, c)
            parts.append((c, tuple(LX.clip(tuple(f), part_cap)) if len(cs) > 1 else tuple(f), how,
                          tuple(LX.clip(tuple(w0.form), o_part)) if len(cs) > 1 else tuple(w0.form), tuple(f)))
        from .names import _repair
        if st == "dithematic":
            if old or len(parts) > 2 or t.get("length") == "long":
                # (an old name keeps the order it was coined in, a frozen compound; a long tradition joins whole themes
                # in the lect's head order, unclipped by the compound rule)
                hf = _head_final(origin if old else lect)
                seq = parts if hf else [parts[-1]] + parts[:-1]
                form = _repair(lect, tuple(s for p in seq for s in p[1]))
                proto = tuple(s for p in seq for s in p[3]) if old else None
            else:
                form = self._compound(lect, parts[1][1], parts[0][1])
                proto = None
        else:
            from .names import _repair
            form = _repair(lect, tuple(s for p in parts for s in p[1]))
            proto = tuple(s for p in parts for s in p[3]) if old else None
        if LX.syllables(form) > cap:
            form = _repair(lect, LX.clip(tuple(form), cap))
        age = self.coined_kyr(origin) if old else 0.0
        clipped = False
        if old:
            form, clipped = self._erode(lect, form, age, (lect.id, t["origin"], i))
        roman, ipa = self.spell(lect, form)
        from .names import _roman_form
        bits = []
        for c, _f, how, _f0, f in parts:
            r = _roman_form(lect, f).lower()
            note = {"same": "", "kept": "", "lost": "; the word is gone from the language", "missing": ""}.get(how, f"; the root is {how}")
            bits.append(f"{r} '{_gloss(c)}'{note}")
        etym = f"{roman} '{gloss}': " + " + ".join(bits)
        if old:
            pr = RO.title_name(_roman_form(origin, proto)) if proto else ""
            etym += f"; an old name, coined in {origin.id} {_ago(age)}" + (f" as {pr}" if pr else "")
            if clipped:
                etym += ", worn down in use"
            opaque = clipped or any(h != "kept" and h != "same" for _c, _f, h, _x, _y in parts)
        else:
            etym += "; coined from today's words"
            opaque = False
        return {"roman": roman, "ipa": ipa, "gloss": gloss, "age": kind, "opaque": bool(opaque), "etym": etym,
                "form": form}

    # ---------------------------------------------------------------- bynames
    def _byname(self, lect, t, given: list, i: int) -> dict | None:
        from .names import _roman_form, _repair
        rng = self.rng("byname", lect.id, i)
        if not given:
            return None
        me = given[i % len(given)]
        st = t["byname"]
        g = getattr(lect, "grammar", None)
        if st in ("patronymic", "matronymic"):
            parent = given[(i + 1) % len(given)]
            kin = "DAUGHTER" if i % 2 else "SON"
            kw = _w(lect, kin)
            if kw is None:
                return None
            gen = g.gram("GEN") if g is not None else None
            hf = _head_final(lect)
            if gen is not None and gen.form:
                pw, how = GR._with_gram(tuple(parent["form"]), gen)
                pw = [tuple(x) for x in pw]
            else:  # (no genitive marker: the kin word and the name compound, as Mac-X or Wil-son)
                pw, how = [self._compound(lect, tuple(kw.form), tuple(parent["form"]))], "compounded: the language has no genitive marker"
            if gen is None or not gen.form:
                words = pw
            elif hf and gen.level >= 1 and len(pw) == 1:
                words = [_repair(lect, pw[0] + tuple(kw.form))]  # (fused: Jón-s-son)
            else:
                words = pw + [tuple(kw.form)] if hf else [tuple(kw.form)] + pw
            whose = "father's" if st == "patronymic" else "mother's"
            gloss = f"{me['gloss']}, {_gloss(kin)} of {parent['gloss']}"
            etym = f"the {whose} name {parent['roman']} + {_roman_form(lect, kw.form).lower()} '{_gloss(kin)}' ({how})"
        elif st == "epithet":
            ok = [c for c in EPITHETS if _w(lect, c) is not None]
            if not ok:
                return None
            c = ok[int(rng.integers(len(ok)))]
            words = [tuple(_w(lect, c).form)]
            gloss = f"{me['gloss']}, the {_gloss(c)}"
            etym = f"{_roman_form(lect, words[0]).lower()} '{_gloss(c)}', a byname"
        else:
            clans = t.get("clans") or []
            if not clans:
                return None
            c = clans[i % len(clans)]
            origin = self.coiner(lect, {"origin": t.get("byname_origin") or lect.id})
            f, how = self.reflex(lect, origin, c)
            if not f:
                return None
            words = [f]
            gloss = f"{me['gloss']} of the {_gloss(c)} clan"
            etym = f"the clan name {RO.title_name(_roman_form(lect, f))} '{_gloss(c)}', from {origin.id} {_ago(self.coined_kyr(origin))}"
            if how == "lost":
                etym += " (the word is gone from the language)"
        sp = [_roman_form(lect, w) for w in words]
        first = t["order"] == "family_first" and st == "clan"
        roman = " ".join(RO.title_name(x) for x in (sp + [me["roman"]] if first else [me["roman"]] + sp))
        ipa = " ".join(word_ipa(w) for w in ([*words, me["form"]] if first else [me["form"], *words]))
        return {"roman": roman, "ipa": ipa, "gloss": gloss, "kind": st, "etym": etym}

    def for_lect(self, lect) -> dict | None:
        if getattr(lect, "lexicon", None) is None:
            return None
        t = self.tradition(lect)
        given = []
        for kind, n in (("old", N_OLD), ("new", N_NEW)):
            seen = {x["roman"] for x in given}
            for i in range(n + 3):  # (a few spare draws when two come out the same)
                if sum(1 for x in given if x["age"] == kind) >= n:
                    break
                x = self._given(lect, t, kind, i)
                if x is not None and _offends(lect, x["form"]):
                    continue   # (a name that reads as an English slur is not given: the next draw; cold review 11-08)
                if x is not None and x["roman"] not in seen:
                    given.append(x)
                    seen.add(x["roman"])
        bys = [b for b in (self._byname(lect, t, given, i) for i in range(N_BY)) if b is not None]
        trad = {k: t[k] for k in ("given", "byname", "order", "origin")}
        trad["length"] = t.get("length") or "mid"
        if t.get("changed"):
            trad["changed"] = t["changed"]
        if t["given"] == "dithematic":
            trad["themes"] = [[_gloss(c) for c in t["themes_a"]], [_gloss(c) for c in t["themes_b"]]]
        for x in given:
            x.pop("form", None)
        return {"tradition": trad, "given": given, "bynames": bys}

    # ---------------------------------------------------------------- settlements
    def settlements(self, lect, sites_by_cell: dict, river_ids=None, given: list | None = None) -> list:
        try:
            cells, _ = self.P.R.deme_cells(lect.deme, self.P.last)
        except Exception:
            return []
        here = [s for c in np.asarray(cells).tolist() for s in sites_by_cell.get(int(c), ())]
        here = [s for s in here if s.get("abandoned_kyr") is None and s.get("tier_now") in ("city", "town", "village")]
        here.sort(key=lambda s: (-(s.get("pop_now") or 0), s["id"]))
        return [x for x in (self.settlement(lect, s, river_ids, given) for s in here[:SITES_PER_DEME]) if x is not None]

    def ruins(self, sites: list, river_ids=None) -> dict:
        """PW-1604: names for the abandoned places of the ledger, so a state whose capital is now a ruin is named for it.
        Each ruin is named as it was said by the last people to hold it, in the lect of their deme on its cell when it was
        abandoned (the founders' name, kept as heard when the holders were newcomers: `settlement`), its generic chosen by
        its peak tier. Returns {deme id of that lect: [entry]}; an entry is the settlement record, kind "ruin", with
        `abandoned_kyr` and without the long `plain` line (thousands of ruins: the main file stays small)."""
        R = self.P.R
        by_deme: dict = {}
        for l in self.P.lects.values():
            if l.deme is not None and getattr(l, "lexicon", None) is not None:
                by_deme.setdefault(l.deme, []).append(l)
        for v in by_deme.values():
            v.sort(key=lambda l: (-l.born_kyr, l.id))
        out: dict = {}
        for s in sites:
            k = s.get("abandoned_kyr")
            if k is None or s.get("kind") == "mine" or s.get("cell") is None or not s.get("founded_by"):
                continue
            k = float(k)
            hs = s.get("holders") or []
            who = hs[-1][1] if hs else (s.get("holder") or s.get("founded_by"))
            try:
                d = R.deme_at_cell(who, int(s["cell"]), R.frame_of(k))
            except Exception:   # noqa: BLE001 - a people the run cannot place there: the founders' lect names it
                d = None
            lect = None
            for l in by_deme.get(d, ()) if d is not None else ():
                if l.born_kyr + 1e-9 >= k and (l.died_kyr is None or l.died_kyr <= k + 1e-9):
                    lect = l
                    break
            if lect is None:
                lect = self._founder_lect(s, None)
            if lect is None:
                continue
            x = self.settlement(lect, dict(s, tier_now=s.get("tier_peak") or "village"), river_ids, None)
            if x is None:
                continue
            x = {kk: v for kk, v in x.items() if kk not in ("plain", "pop", "pattern", "tautology")}
            x.update(kind="ruin", abandoned_kyr=round(k, 3))
            out.setdefault(lect.deme, []).append(x)
        return out

    def _founder_lect(self, site, lect=None):
        """The lect that named a site: the lect's own ancestor (or itself) alive at the founding when the founders were of its
        people, else the deme's lect then, else the founders' most numerous lect then."""
        p, k = site.get("founded_by"), float(site.get("founded_kyr") or 0.0)
        alive = lambda l: l.born_kyr + 1e-9 >= k and (l.died_kyr is None or l.died_kyr <= k + 1e-9)  # noqa: E731
        if lect is not None:
            for x in self.chain(lect)[::-1]:
                if alive(x) and x.people == p and getattr(x, "lexicon", None) is not None:
                    return x
            x = self.P.lect_at(lect.deme, k)
            if x is not None and alive(x) and x.people == p and getattr(x, "lexicon", None) is not None:
                return x
        cands = [l for l in self.P.lects.values() if l.people == p and l.born_kyr + 1e-9 >= k
                 and (l.died_kyr is None or l.died_kyr <= k + 1e-9) and getattr(l, "lexicon", None) is not None]
        if not cands:
            return None
        return max(cands, key=lambda l: (float(getattr(l, "population", 0) or 0), l.id))

    def _generic(self, lect, site, river_ids, rng) -> str | None:
        on_river = river_ids is not None and int(river_ids[int(site["cell"])]) > 0 if river_ids is not None else False
        opts = []
        if on_river:
            opts += ["FORD", "BRIDGE"]
        opts += list(GENERIC_BY_TIER.get(site.get("tier_now"), ("VILLAGE",)))
        opts = [c for c in opts if _w(lect, c) is not None]
        return opts[int(rng.integers(len(opts)))] if opts else None

    def settlement(self, lect, site, river_ids, given) -> dict | None:
        from .names import _hear, _roman_form, _repair
        rng = self.rng("site", site["id"])
        age = float(site.get("founded_kyr") or 0.0)
        founder = self._founder_lect(site, lect)
        sub = founder is not None and not self.P.inherits(lect, founder)
        namer = founder if founder is not None else lect
        gen_c = self._generic(namer, site, river_ids, rng)
        if gen_c is None:
            return None
        generic = tuple(_w(namer, gen_c).form)
        eroded = age >= SUFFIX_KYR
        if eroded:
            generic = LX.clip(generic, 1)
        # the specific: a founder's name in the genitive, an adjective, or the people's own root
        r = rng.random()
        spec_gloss, spec = None, None
        if r < 0.4 and namer is not None:
            pn = self.for_lect_cached(namer)
            gv = [x for x in (pn or {}).get("given", []) if x.get("ipa")]
            if gv:
                x = gv[int(rng.integers(len(gv)))]
                from .percepts import from_ipa
                spec = tuple(from_ipa(x["ipa"].replace(" ", "")))
                g = getattr(namer, "grammar", None)
                gen = g.gram("GEN", bound=True) if g is not None else None
                if gen is not None and gen.form:
                    spec = tuple(GR._attach(spec, tuple(gen.form), gen.side))
                spec_gloss = f"{x['roman']}'s"
        if spec is None:
            ok = [c for c in SPECIFIC_ADJ if _w(namer, c) is not None]
            if ok:
                c = ok[int(rng.integers(len(ok)))]
                spec, spec_gloss = tuple(_w(namer, c).form), _gloss(c)
        if spec is None:
            form = generic
            gloss = f"the {_gloss(gen_c)}"
        else:
            from .names import _join
            form = _join(namer, generic, spec)
            gloss = f"{spec_gloss} {_gloss(gen_c)}" if spec_gloss.endswith("'s") else f"the {spec_gloss} {_gloss(gen_c)}"
        etym = f"{_gloss(gen_c)}" + (" (worn to a suffix)" if eroded else "")
        pattern = None
        taut = None
        if sub:
            heard = _hear(form, lect)
            pattern = "P2"
            p_t = SUBSTRATE_TAUTOLOGY if _w(lect, gen_c) is None or _root_id(_w(lect, gen_c)) != _root_id(_w(namer, gen_c)) else 0.0
            own = self._generic(lect, site, river_ids, rng)
            if own is not None and rng.random() < p_t:
                from .names import _join
                heard = _join(lect, tuple(_w(lect, own).form), heard)
                taut = f"{_gloss(own)} + the old name: '{_gloss(own)} {gloss.removeprefix('the ')}' (a tautology, like River Avon)"
            form = heard
        form = _repair(lect, form)
        roman = RO.title_name(_roman_form(lect, form))
        plain = f"{roman}, '{gloss}'" + (f"; {taut}" if taut else "")
        if sub:
            plain += f"; named by the {site.get('founded_by')} ({namer.id}) who founded it {_ago(age)}, kept as heard"
        else:
            plain += f"; from {etym}, founded {_ago(age)}"
        return {"kind": "settlement", "site": int(site["id"]), "tier": site.get("tier_now"), "pop": site.get("pop_now"),
                "ipa": word_ipa(form), "roman": roman, "gloss": gloss, "lect": lect.id, "named_by": namer.id,
                "kyr": round(age, 3), "substrate_of": namer.id if sub else None, "pattern": pattern,
                "tautology": bool(taut), "plain": plain}

    def for_lect_cached(self, lect):
        k = ("pn", lect.id)
        if k not in self._trad:
            try:
                self._trad[k] = self.for_lect(lect)
            except Exception:
                self._trad[k] = None
        return self._trad[k]
