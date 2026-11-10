"""Faiths in the languages (faiths & contact pass 3, 2026-11-08; contact-gaps.md rec. 5): god names, liturgical registers
and learned loans, read from the run's gods.json (planet/lineages/gods.py; derived in memory, read-only, when the stored
file predates faiths: inputs.Run.gods_doc).

**God names are words.** A god's name is a lexicon entry `name:god:<key>` (pos NAME; `key` = the root of the being's
`parent` chain in gods.json, so a daughter culture's copy of a god and a convert's copy of the converter's god share it).
It is coined once, in the lect spoken where and when the god entered the line, from that lect's own words:
- a title ('sky-father', 'lord of the sea', 'grandmother of the forest': the domain word + FATHER, MOTHER, GRANDFATHER,
  GRANDMOTHER, MASTER, CHIEF or KING), weighted to kin titles for spirits bound to a feature and to rank titles for
  individuated gods;
- an agent noun from the domain's verb ('the one who burns', 'the one who flows': the lect's 'agent' affix);
- a kenning ('eye of the sky' for a sun god, 'fish-road' for a sea god; KENNINGS);
- the domain word itself as a name (Dyēus, 'sky').
From then on it is an ordinary word of the lect: every sound change of the lect runs over it, daughters inherit it
(cognate god names across sister languages, Dyēus > Zeus / Ju-piter, when the god is older than their split), a shift
keeps it as a substrate name, and a convert borrows it from a lect of the converting faith (heard, `borrow:<lect>`).
A name is not replaced by the lexicon's word-replacement draw (`lexicon.step` skips pos NAME); instead it is renamed by
an epithet now and then (`renew_names`: the holy name avoided and a title used in its place, as Hebrew Adonai or the
Germanic bear 'the brown one'), at NAME_HALF_KYR per reference generation.

When a god entered a line: walking the being's parent chain up from today's being, the first copy made by a conversion
(`how` converted) is the moment the line took the god from another faith; with none, the root being's birth (often older
than the 20 kyr window: then the name is as old as the proto-language). The deme then is today's deme's ancestor alive at
that time (inputs.Run.parent_deme); a line that starts later (an arrival people) takes it at its first frame, from a lect
that has it.

**Liturgical registers.** A faith whose seat people knows temples (the techtree) gets a canon: the seat lect as it was
when the faith first had temples (or at its founding, if later) is frozen (a copy that no longer steps), with its sacred
vocabulary and the god names. Its holders' lects take learned loans from it over time (`learned_step`: SACRED concepts,
LEARNED_RATE per generation, the frozen form heard through the receiver: Latin religio > religion beside the inherited
word), and each living holder lect lists the frozen forms as a learned register beside its own words (`systems.learned`:
doublets like frail / fragile where the inherited word shares the root, sacred synonyms where it does not). The register
lives as long as the faith: no canon is older than the temples, so the oldest is about 6 kyr (Sumerian, Sanskrit and Ge'ez
were kept as liturgy for 2-4 kyr; a longer life is our choice: for-daniel.md).

Deterministic: every draw is history.rng_for(seed, "faith", ...).
"""
from __future__ import annotations

import math

import numpy as np

from . import lexicon as LX

GODS_PER_CULTURE = 4   # the living beings named per holding culture (by rank: the high god, then devotion)
NAME_HALF_KYR = 12.0   # half-life of a god's name against an epithet replacing it, in REF_GEN_YR generations
REF_GEN_YR = 27.7
LIT_MIN_KYR = 1.0      # a canon younger than this is the living language: no separate register
LEARNED_RATE = 0.0025  # per generation, chance a holder lect takes one sacred word from its faith's liturgy (when it differs)
SACRED = ("GOD", "SPIRIT", "SOUL", "HOLY", "PRAY", "SACRIFICE", "DEMON", "PRIEST", "TEMPLE")
LIT_WORDS = SACRED + ("DEATH", "PEACE", "TRUE", "SONG", "SING", "HEAR", "GIVE", "WE", "LIGHT (RADIATION)", "FEAST")
# the domain's verb for an agent-noun name, and its English
DOMAIN_VERB = {"fire": ("BURN", "the one who burns"), "sun": ("SHINE", "the one who shines"),
               "river": ("FLOW", "the one who flows"), "flood": ("FLOW", "the one who flows"),
               "rain": ("RAIN (RAINING)", "the one who rains"), "storm": ("STRIKE OR BEAT", "the striker"),
               "hunt": ("HUNT", "the hunter"), "war": ("FIGHT", "the fighter"), "death": ("TAKE", "the taker"),
               "smithing": ("STRIKE OR BEAT", "the striker"), "harvest": ("GROW", "the one who makes grow"),
               "fertility": ("GIVE", "the giver"), "herd": ("KEEP", "the keeper"), "sky": ("SEE", "the one who sees"),
               "sea": ("HOLD", "the holder"), "hearth": ("BURN", "the one who burns"),
               "ancestors": ("KNOW", "the one who knows"), "mountain": ("STAND", "the one who stands"),
               "forest": ("HIDE", "the hidden one"), "desert": ("BURN", "the one who burns")}
# (head, modifier, English) kennings for a god by its domain
KENNINGS = {"sun": (("EYE", "SKY", "eye of the sky"),), "sea": (("ROAD", "FISH", "the fish-road"),),
            "sky": (("ROOF", "WORLD", "roof of the world"),), "storm": (("SPEAR", "SKY", "the sky-spear"),),
            "death": (("HOUSE", "NIGHT", "the night-house"),), "fire": (("TONGUE", "WOOD", "the wood-tongue"),),
            "river": (("ROAD", "WATER", "the water-road"),), "harvest": (("MOTHER", "SEED", "seed-mother"),)}
KIN_TITLES = (("FATHER", "father"), ("MOTHER", "mother"), ("GRANDFATHER", "grandfather"), ("GRANDMOTHER", "grandmother"))
RANK_TITLES = (("MASTER", "lord"), ("CHIEF", "chief"), ("KING", "king"))
# a domain's gift, for the petition formula ('may the sky-father give rain')
GIFT = {"sea": "FISH", "river": "WATER", "rain": "RAIN (PRECIPITATION)", "flood": "WATER", "sky": "RAIN (PRECIPITATION)",
        "sun": "LIGHT (RADIATION)", "storm": "RAIN (PRECIPITATION)", "mountain": "WATER", "fire": "FIRE",
        "forest": "WOOD", "desert": "WATER", "herd": "MILK", "hunt": "FLESH OR MEAT", "harvest": "SEED",
        "fertility": "CHILD (YOUNG HUMAN)", "hearth": "FIRE", "smithing": "SPEAR", "death": "PEACE", "war": "SPEAR",
        "ancestors": "PEACE"}


def god_concept(key: int) -> str:
    return f"name:god:{int(key)}"


def is_god(concept: str) -> bool:
    return concept.startswith("name:god:")


def _domain_word(dom: str) -> str:
    return LX.GOD_DOMAIN_CONCEPT.get(dom, "GOD")


def _taboos_doc(R) -> dict:
    """The run's taboos.json (read once, read-only); {} without one or for a run held in memory."""
    if "_taboos_doc" not in R.__dict__:
        doc = {}
        d = getattr(R, "dir", None)
        if d is not None:
            import json
            from pathlib import Path
            tp = Path(d) / "taboos.json"
            try:
                doc = json.loads(tp.read_text()) if tp.exists() else {}
            except (OSError, ValueError):
                doc = {}
        R.__dict__["_taboos_doc"] = doc
    return R.__dict__["_taboos_doc"]


# ------------------------------------------------------------------------------------------------- the plan
class Plan:
    """What the history needs from the faith readout, worked out once before it runs: which god enters which line when
    (`events`), the canons (`canons`), each faith's holders (now, and their ancestors at a frame: `holders_at`)."""

    def __init__(self, R):
        self.R = R
        self.ok = False
        self.gods: dict[int, dict] = {}       # key -> {domain, domains, ind, high, label, faith, name}
        self.events: dict[int, list] = {}     # frame -> [(deme then, key, kind)]
        self.canons: dict[int, list] = {}     # frame -> [(faith, deme then)]
        self.faiths: dict[int, dict] = {}     # faith id -> {name, core, founded_kyr, holders (demes now), seat, canon_kyr}
        self.deme_faith: dict[int, int] = {}  # deme now -> faith id
        self.deme_gods: dict[int, list] = {}  # deme now -> [god keys], ranked
        self._anc: dict = {}
        try:
            gd = R.gods_doc()
        except Exception:   # noqa: BLE001 - no faiths then
            gd = None
        cd = getattr(R, "cultures_doc", None) or {}
        dc = cd.get("deme_culture") or []
        fl = ((gd or {}).get("faiths") or {}).get("list") or []
        if not gd or not dc or not fl:
            return
        self.ok = True
        beings = {b["id"]: b for b in gd.get("beings") or []}
        cults = gd.get("cultures") or {}
        last = len(R.frames_kyr) - 1
        k_last = R.kyr(last)
        start = R.kyr(0)
        fby = {f["id"]: f for f in fl}
        arr: dict[int, dict] = {}   # deme now -> {god key: (kyr the line took it, kind, today's being)}
        for d in R.demes_alive(last):
            c = dc[d] if d < len(dc) else None
            cu = cults.get(str(c)) if c is not None else None
            if not cu or cu.get("faith_now") is None:
                continue
            fid = int(cu["faith_now"])
            self.deme_faith[d] = fid
            live = [beings[i] for i in cu.get("living") or [] if i in beings]
            live.sort(key=lambda b: (not b.get("high"), -float(b.get("devotion") or 0), -float(b.get("individuation") or 0), b["id"]))
            keys = arr[d] = {}
            for b in live:
                key, t, kind = self._arrival(b, beings)
                if key in keys:
                    continue
                keys[key] = (t, kind, b)
                if len(keys) >= GODS_PER_CULTURE:
                    break
        # One faith, one pantheon (polish lane, 2026-11-08). gods.json lists each holding culture's own living beings, so
        # the holders of one faith named different gods (a drow and an elvish lect of one sky faith told of different
        # gods, domains and gifts). The faith's pantheon is now its seat culture's gods (the founding culture's, by rank),
        # topped up with the gods most of its holders share; every holder names exactly these, a culture lacking one
        # taking it with the faith (when it took the faith's other gods, else at the founding), and each god's domain and
        # label are the seat's. The holders' divine food taboos are the faith's too (`taboos`, ranked by how
        # characteristic they are of this faith against all cultures).
        tcount_all = self._taboo_counts(None, R, dc, beings)
        for fid in sorted(set(self.deme_faith.values())):
            f = fby.get(fid) or {}
            hold = sorted(d for d, x in self.deme_faith.items() if x == fid)
            org = f.get("origin_culture")
            seat_pool = [d for d in hold if org is not None and d < len(dc) and dc[d] == org] or hold
            seat = max(seat_pool, key=lambda d: (R.deme_population(d, last), -d))
            pan = list(arr.get(seat) or {})
            cnt: dict[int, int] = {}
            for d in hold:
                for k in arr.get(d) or {}:
                    cnt[k] = cnt.get(k, 0) + 1
            for k in sorted(cnt, key=lambda k: (-cnt[k], k)):
                if len(pan) >= GODS_PER_CULTURE:
                    break
                if k not in pan:
                    pan.append(k)
            founded = min(float(f.get("founded_kyr") if f.get("founded_kyr") is not None else start), start)
            for k in pan:
                src = (arr.get(seat) or {}).get(k) or next(arr[d][k] for d in hold if k in (arr.get(d) or {}))
                b = src[2]
                root = beings.get(k) or b
                dom = b.get("first_domain") or ((b.get("top") or [["ancestors"]])[0][0])
                self.gods.setdefault(k, {"domain": dom, "domains": [x[0] for x in b.get("top") or []][:3],
                                         "ind": float(b.get("individuation") or 0.0), "high": bool(b.get("high")),
                                         "label": b.get("label") or b.get("role") or "", "faith": fid,
                                         "name": b.get("name") or root.get("name"),
                                         "born_kyr": float(root.get("born_kyr") or start)})
            for d in hold:
                own = arr.get(d) or {}
                took = max([own[k][0] for k in own] + [founded]) if own else founded
                for k in pan:
                    t, kind = (own[k][0], own[k][1]) if k in own else (min(took, start), "convert")
                    j, dthen = self._frame_deme(d, t)
                    if j is not None:
                        self.events.setdefault(j, []).append((dthen, k, kind))
                self.deme_gods[d] = list(pan)
            people = R.people_of(seat)
            known = (((R.meta.get("techtree") or {}).get("known") or {}).get(people) or {})
            tk = known.get("temples")
            canon = None
            if tk:
                canon = min(float(f.get("founded_kyr") or start), float(tk[0]))
                canon = min(canon, start)
                if canon - k_last < LIT_MIN_KYR:
                    canon = None
            self.faiths[fid] = {"name": f.get("name") or f"faith {fid}", "core": f.get("core"),
                                "founded_kyr": f.get("founded_kyr"), "how": f.get("how"), "parent": f.get("parent"),
                                "holders": hold, "seat": seat, "canon_kyr": canon,
                                "peoples": sorted({R.people_of(d) for d in hold}), "pantheon": pan,
                                "taboos": self._faith_taboos(hold, pan, R, dc, beings, tcount_all)}
            if canon is not None:
                j, dthen = self._frame_deme(seat, canon)
                if j is not None:
                    self.canons.setdefault(j, []).append((fid, dthen))
                    self.faiths[fid]["canon_kyr"] = R.kyr(j)
        for j in self.events:
            self.events[j] = sorted(set(self.events[j]))

    def _arrival(self, b: dict, beings: dict) -> tuple[int, float, str]:
        """(god key, kyr the line took the god, "coin" | "convert") for today's being b."""
        x, seen, conv = b, set(), None
        while x is not None and x["id"] not in seen:
            seen.add(x["id"])
            if conv is None and x.get("how") == "converted":
                conv = float(x.get("born_kyr") or 0.0)
            p = x.get("parent")
            if p is None or p not in beings:
                break
            x = beings[p]
        if conv is not None:
            return x["id"], conv, "convert"
        return x["id"], float(x.get("born_kyr") or 0.0), "coin"

    def _taboo_counts(self, demes, R, dc, beings) -> dict:
        """{taboo target: number of cultures} with a divine food taboo on it, over the cultures of `demes` (None: every
        culture of the run's taboos.json)."""
        td = _taboos_doc(R).get("cultures") or {}
        cs = sorted(td, key=int) if demes is None else sorted({str(dc[d]) for d in demes if d < len(dc)}, key=int)
        out: dict[str, int] = {}
        for c in cs:
            for t in (td.get(c) or {}).get("taboos") or []:
                if t.get("origin") == "divine" and t.get("god") is not None:
                    out[t["target"]] = out.get(t["target"], 0) + 1
        return out

    def _faith_taboos(self, hold, pan, R, dc, beings, all_counts) -> list:
        """The faith's divine food taboos: [[god key, target, English label]] over its holders' cultures whose god is a
        god of the pantheon, one per target, the ones most characteristic of this faith first (share among the holders'
        cultures over the share among all cultures), then by target."""
        td = _taboos_doc(R).get("cultures") or {}
        cs = sorted({str(dc[d]) for d in hold if d < len(dc)}, key=int)
        n_all = max(1, len(td))
        got: dict[str, list] = {}
        cnt: dict[str, int] = {}
        for c in cs:
            for t in (td.get(c) or {}).get("taboos") or []:
                if t.get("origin") != "divine" or t.get("god") is None or t["god"] not in beings:
                    continue
                key = self._arrival(beings[t["god"]], beings)[0]
                if key not in pan:
                    continue
                cnt[t["target"]] = cnt.get(t["target"], 0) + 1
                got.setdefault(t["target"], [key, t["target"], t.get("label") or t["target"]])
        nc = max(1, len(cs))
        lift = {k: (cnt[k] / nc) / max(all_counts.get(k, 1) / n_all, 1e-9) for k in got}
        return [got[k] for k in sorted(got, key=lambda k: (-round(lift[k], 6), k))]

    def ancestor(self, d: int, kyr: float) -> tuple[int, bool]:
        """(the deme of d's line alive at kyr, True) or (the oldest deme of the line, False) when the line starts later."""
        k = (d, round(kyr, 3))
        v = self._anc.get(k)
        if v is None:
            x, seen = d, set()
            while x is not None and x not in seen and not self.R.alive_at(x, kyr):
                seen.add(x)
                p = self.R.parent_deme(x)
                if p is None:
                    break
                x = p
            v = self._anc[k] = (x, self.R.alive_at(x, kyr))
        return v

    def _frame(self, kyr: float) -> int:
        fk = self.R.frames_kyr
        return min(range(len(fk)), key=lambda j: (abs(fk[j] - kyr), j))

    def _frame_deme(self, d: int, kyr: float) -> tuple[int | None, int]:
        R = self.R
        start = R.kyr(0)
        last = len(R.frames_kyr) - 1
        t = min(float(kyr), start)
        x, ok = self.ancestor(d, t)
        if ok:
            j = self._frame(t)
        else:   # (the line starts later: its first frame)
            born = float(R.demes[x]["born_kyr"])
            j = self._frame(born)
            while j < last and not R.alive_at(x, R.kyr(j)):
                j += 1
        return min(j, last - 1), x

    def holders_at(self, fid: int, kyr: float) -> list[int]:
        """The demes then of the faith's holders now (their ancestors alive at kyr)."""
        out = set()
        for d in (self.faiths.get(fid) or {}).get("holders") or ():
            x, ok = self.ancestor(d, kyr)
            if ok:
                out.add(x)
        return sorted(out)


# ------------------------------------------------------------------------------------------------- names
def _gloss_dom(dom: str) -> str:
    return LX.concept_info(_domain_word(dom)).gloss.lower().split(" (")[0]


def coin_name(rng, lex, key: int, god: dict, inv, kyr: float, lect_id: str, renew: bool = False, min_moras: int = 0):
    """A Word naming the god in this lexicon (not stored), or None. `renew`: an epithet in place of an old name (the
    avoidance titles 'the lord', 'the holy one' join the patterns). `min_moras`: no name shorter (lexicon.moras)."""
    con = god_concept(key)
    dom = god.get("domain") or "ancestors"
    dw = _domain_word(dom)
    ind = float(god.get("ind") or 0.0)
    dg = _gloss_dom(dom)
    opts = []
    if dw in lex.words:
        opts.append(("bare", 0.15, None))
        for c, g in KIN_TITLES:
            if c in lex.words:
                opts.append(("kin", (0.1 + 0.3 * (1.0 - ind)) / len(KIN_TITLES), (c, g)))
        for c, g in RANK_TITLES:
            if c in lex.words:
                opts.append(("rank", (0.1 + 0.3 * ind) / len(RANK_TITLES), (c, g)))
    vb = DOMAIN_VERB.get(dom)
    if vb and vb[0] in lex.words and (lex.affixes.get("agent") or ((), True))[0]:
        opts.append(("agent", 0.1 + 0.3 * ind, vb))
    for h, m, g in KENNINGS.get(dom, ()):
        if h in lex.words and m in lex.words:
            opts.append(("kenning", 0.12, (h, m, g)))
    if renew:
        if "MASTER" in lex.words:
            opts.append(("title", 0.25, ("MASTER", "the lord")))
        for q, g in (("HOLY", "the holy one"), ("OLD", "the old one")):
            if q in lex.words and (lex.affixes.get("agent") or ((), True))[0]:
                opts.append(("avoid", 0.12, (q, g)))
    if not opts:
        return None
    taken = {x.form for k, x in lex.words.items() if is_god(k) and k != con}   # (two gods of one people, one name: no)
    w = np.array([o[1] for o in opts], float)
    order = [int(i) for i in rng.choice(len(opts), size=len(opts), replace=False, p=w / w.sum())]
    for oi in order:
        kind, _w, arg = opts[oi]
        word, gloss = None, None
        if kind == "bare":
            b = lex.words[dw]
            word, gloss = b, dg.capitalize()
        elif kind in ("kin", "rank"):
            word = LX.compound(rng, lex, con, inv, kyr, lect_id, head=arg[0], modifier=dw, process="name:god",
                               note=f"{arg[0]} + {dw}")
            gloss = f"{dg}-{arg[1]}" if kind == "kin" else f"{arg[1]} of the {dg}"
        elif kind == "title":
            word, gloss = lex.words[arg[0]], arg[1]
        elif kind in ("agent", "avoid"):
            word = LX.derive(rng, lex, con, inv, kyr, lect_id, base=arg[0], meaning="agent", free=True)
            gloss = arg[1]
        elif kind == "kenning":
            word = LX.compound(rng, lex, con, inv, kyr, lect_id, head=arg[0], modifier=arg[1], process="name:god",
                               note=f"{arg[0]} + {arg[1]}")
            gloss = arg[2]
        if word is None or not len(word.form) or word.form in taken or LX.moras(word.form) < min_moras:
            continue
        how = {"bare": "the word as a name", "kin": "a kin title", "rank": "a title", "title": "a title in place of the name",
               "agent": "an agent noun", "avoid": "an avoidance epithet", "kenning": "a kenning"}[kind]
        st = LX._step(kyr, lect_id, "name:god", word.form, gloss, how + (" (the old name avoided)" if renew else ""))
        etym = word.etym if word.concept == con else word.etym
        if etym and etym[-1].process == "name:god":
            etym = etym[:-1]
        return LX.Word(con, word.form, "NAME", 1, etym + (st,), float(kyr), word.roots, LX.etym_roots(word))
    return None


def name_gloss(w) -> str:
    """The English of a god's name: its latest name step's gloss."""
    for st in reversed(w.etym):
        if st.process == "name:god":
            return st.gloss
    return ""


def renew_hazard(n_generations: float) -> float:
    h = math.log(2.0) / (NAME_HALF_KYR * 1000.0 / REF_GEN_YR)
    return 1.0 - (1.0 - h) ** max(0.0, n_generations)


# ------------------------------------------------------------------------------------------------- the history's side
def _rng(h, *key):
    from .history import rng_for
    return rng_for(h.seed, "faith", *key)


def _plan(h) -> Plan | None:
    p = h.__dict__.get("faith_plan", False)
    if p is False:
        try:
            p = Plan(h.R)
        except Exception as e:   # noqa: BLE001 - a run whose faith readout cannot be read has no faiths in its languages
            h.say(h.R.kyr(0), f"faiths: not read ({type(e).__name__}: {e})")
            p = None
        if p is not None and not p.ok:
            p = None
        h.__dict__["faith_plan"] = p
        h.__dict__["liturgy"] = {}
    return p


def _donor(h, l, con: str, j: int):
    """A living lect that has the god's name, for `l` to take it from: the one most in contact, else one of its own
    family, else the first by id."""
    have = [x for x in sorted(h.lects) if h.lects[x].alive and x != l.id and con in h.lects[x].lexicon]
    if not have:
        return None
    if l.deme is not None:
        c = h.R.contacts_of(l.deme, j)
        near = [(c.get(h.lects[x].deme, 0.0), x) for x in have if h.lects[x].deme is not None and c.get(h.lects[x].deme, 0.0) > 0]
        if near:
            return h.lects[max(near)[1]]
    from .history import LC_root
    root = LC_root(h, l)
    fam = [x for x in have if LC_root(h, h.lects[x]) == root]
    return h.lects[(fam or have)[0]]


def step(h, i: int) -> None:
    """At the start of interval i (before the births): the god names and canons of frame i - 1, then the renaming of
    old names and the learned loans over the interval."""
    P = _plan(h)
    if P is None:
        return
    R = h.R
    j = i - 1
    kyr = R.kyr(j)
    n_ev = 0
    for dthen, key, kind in P.events.get(j, ()):
        l = h.lect_of(dthen)
        if l is None or not l.alive:
            continue
        con = god_concept(key)
        if con in l.lexicon:
            continue
        god = P.gods[key]
        par = h.lects.get(l.parent) if l.parent else None
        if par is not None and par.deme is None and abs(par.born_kyr - l.born_kyr) < 1e-9 and l.how in ("proto", "arrival") \
                and abs(l.born_kyr - kyr) < 1e-9 and kind == "coin":
            if con not in par.lexicon:   # (coined in the proto-language: its daughters inherit one word)
                w = coin_name(_rng(h, "coin", key, par.id), par.lexicon, key, god, par.inventory, par.born_kyr, par.id)
                if w is None:
                    continue
                par.lexicon.set(w)
            l.lexicon.set(par.lexicon[con])
        else:
            src = _donor(h, l, con, j)
            if src is not None:
                fn = (h.__dict__.get("faith_plan").faiths.get(god["faith"]) or {}).get("name") or "a faith"
                LX.borrow(src.lexicon[con], src.id, l.lexicon, l.profile, l.inventory, kyr,
                          note=("with the faith, " if kind == "convert" else "") + f"a god of {fn}")
            else:
                w = coin_name(_rng(h, "coin", key, l.id), l.lexicon, key, god, l.inventory, kyr, l.id)
                if w is None:
                    continue
                l.lexicon.set(w)
        l.touch()
        n_ev += 1
    for fid, dthen in P.canons.get(j, ()):
        l = h.lect_of(dthen)
        if l is None or fid in h.liturgy:
            continue
        lit = l.copy(f"lit{fid}", None, kyr, "liturgy")
        lit.died_kyr, lit.end = kyr, "liturgy"
        h.liturgy[fid] = {"lect": lit, "kyr": kyr, "from": l.id, "deme": dthen}
        h.say(kyr, f"the liturgy of {P.faiths[fid]['name']} is fixed in the speech of {h.deme_label(dthen)} (lect {l.id})")
    t0, t1 = R.kyr(i - 1), R.kyr(i)
    from .history import change_generations
    # renaming: a name replaced by an epithet (the old name avoided)
    for lid in sorted(h.lects):
        l = h.lects[lid]
        if not l.alive or l.deme is None or l.lexicon is None:
            continue
        names = [k for k in l.lexicon.words if is_god(k)]
        if not names:
            continue
        n = change_generations((t0 - t1) * 1000.0, l.gen_yr)
        p = renew_hazard(n)
        rng = _rng(h, "renew", l.id, i)
        for k in sorted(names):
            if rng.random() >= p:
                continue
            key = int(k.rsplit(":", 1)[1])
            god = P.gods.get(key)
            if god is None:
                continue
            old = l.lexicon[k]
            w = coin_name(rng, l.lexicon, key, god, l.inventory, t0, l.id, renew=True)
            if w is None or w.form == old.form:
                continue
            st = w.etym[-1]
            w = LX.Word(w.concept, w.form, w.pos, w.freq_class, w.etym[:-1] + (LX.EtymStep(
                st.kyr, st.lect, st.process, st.form, st.gloss, f"{st.note}; it replaced the old name {old.ipa} "
                f"'{name_gloss(old)}'"),), w.born_kyr, w.roots, w.etym_roots)
            l.lexicon.set(w)
            l.touch()
    learned_step(h, P, i)


#: the shortest god name the pages keep (lexicon.moras): a name worn to one short vowel ('I', 'U') is renewed at the end
MIN_NAME_MORAS = 2


def finish_names(h, last: int) -> dict:
    """PW-1548, after the history (so it is untouched): every living holder of a faith names every god of its pantheon,
    and no god name is worn to one short sound. A lect born after its faith's events (a deme alive at the start that the
    history gives a lect a frame or two later) missed them: it takes the name from a lect that has it (`_donor`), else
    coins one, today. A name worn below MIN_NAME_MORAS is renewed as the renaming in `step` renews names (an epithet or
    title; the old name noted). Returns {"named": n, "renewed": n}."""
    P = h.__dict__.get("faith_plan")
    out = {"named": 0, "renewed": 0}
    if not P:
        return out
    R = h.R
    kyr = R.kyr(last)
    for fid in sorted(P.faiths):
        F = P.faiths[fid]
        for d in F["holders"]:
            l = h.lect_of(d)
            if l is None or not l.alive or l.lexicon is None:
                continue
            for key in F.get("pantheon") or ():
                con = god_concept(key)
                if con in l.lexicon or key not in P.gods:
                    continue
                src = _donor(h, l, con, last)
                if src is not None:
                    LX.borrow(src.lexicon[con], src.id, l.lexicon, l.profile, l.inventory, kyr,
                              note=f"a god of {F.get('name') or 'a faith'}, named late")
                else:
                    w = coin_name(_rng(h, "late", key, l.id), l.lexicon, key, P.gods[key], l.inventory, kyr, l.id,
                                  min_moras=MIN_NAME_MORAS)
                    if w is None:
                        continue
                    l.lexicon.set(w)
                l.touch()
                out["named"] += 1
    for lid in sorted(h.lects):
        l = h.lects[lid]
        if not l.alive or l.deme is None or l.lexicon is None:
            continue
        for k in sorted(x for x in l.lexicon.words if is_god(x)):
            old = l.lexicon[k]
            key = int(k.rsplit(":", 1)[1])
            if LX.moras(old.form) >= MIN_NAME_MORAS or key not in P.gods:
                continue
            w = coin_name(_rng(h, "worn", key, l.id), l.lexicon, key, P.gods[key], l.inventory, kyr, l.id, renew=True,
                          min_moras=MIN_NAME_MORAS)
            if w is None or w.form == old.form:
                continue
            st = w.etym[-1]
            w = LX.Word(w.concept, w.form, w.pos, w.freq_class, w.etym[:-1] + (LX.EtymStep(
                st.kyr, st.lect, st.process, st.form, st.gloss, f"{st.note}; it replaced the old name {old.ipa} "
                f"'{name_gloss(old)}', worn to one sound"),), w.born_kyr, w.roots, w.etym_roots)
            l.lexicon.set(w)
            l.touch()
            out["renewed"] += 1
    return out


def learned_step(h, P: Plan, i: int) -> None:
    """Learned loans from each fixed liturgy into the lects of its faith's holders (then), LEARNED_RATE per generation per
    sacred word that differs."""
    if not h.liturgy:
        return
    from .history import change_generations
    R = h.R
    t0, t1 = R.kyr(i - 1), R.kyr(i)
    for fid in sorted(h.liturgy):
        lit = h.liturgy[fid]["lect"]
        name = P.faiths[fid]["name"]
        for d in P.holders_at(fid, t0):
            l = h.lect_of(d)
            if l is None or not l.alive or l.lexicon is None:
                continue
            n = change_generations((t0 - t1) * 1000.0, l.gen_yr)
            p = 1.0 - (1.0 - LEARNED_RATE) ** n
            rng = _rng(h, "learned", fid, l.id, i)
            for c in SACRED:
                lw = lit.lexicon.get(c)
                if lw is None or rng.random() >= p:
                    continue
                cur = l.lexicon.get(c)
                if cur is not None and (cur.form == lw.form or any(st.process == f"borrow:{lit.id}" for st in cur.etym)):
                    continue
                LX.borrow(lw, lit.id, l.lexicon, l.profile, l.inventory, t0, note=f"learned, from the liturgy of {name}")
                l.touch()


def learned_register(h, l) -> dict:
    """{concept: [learned ipa, "doublet" | "synonym" | "only", liturgy ipa]} for a living lect whose faith has a liturgy:
    the liturgy's sacred words as the lect hears them today, beside its own (built for today; `systems.learned`)."""
    P = h.__dict__.get("faith_plan")
    if not P or l.deme is None:
        return {}
    fid = P.deme_faith.get(l.deme)
    L = h.liturgy.get(fid) if fid is not None else None
    if L is None:
        return {}
    lit = L["lect"]
    out = {}
    for c in LIT_WORDS:
        lw = lit.lexicon.get(c)
        if lw is None:
            continue
        cur = l.lexicon.get(c)
        heard = LX.borrow(lw, lit.id, l.lexicon, l.profile, l.inventory, h.R.kyr(len(h.R.frames_kyr) - 1), store=False)
        if cur is not None and cur.form == heard.form:
            continue
        if cur is None:
            kind = "only"
        elif set(LX.etym_roots(cur)) & set(LX.etym_roots(lw)):
            kind = "doublet"
        else:
            kind = "synonym"
        out[c] = [heard.ipa, kind, lw.ipa]
    return out


# ------------------------------------------------------------------------------------------------- the document
def _spell(lect, form) -> str:
    """A god's name as the lect's books spell names (book mode: no tone marks, the lect's planned diacritics only; demo
    read 4 had Nị́dérrìnù and D̮ï from the full register), capitalised."""
    from . import output as OU
    from . import romanize as RO
    sp = OU.Speller(lect)
    try:
        return RO.title_name(sp.orth.word(tuple(form), book=True))
    except Exception:   # noqa: BLE001 - (the full register's fallback, as Speller.form)
        return RO.title_name(sp.form(tuple(form)))


def _coined(w) -> list:
    """[kyr, lect] of the god name's first naming step: two lects whose names share it hold cognates (one word, inherited
    or borrowed)."""
    st = next((s for s in w.etym if s.process == "name:god"), None)
    return [round(float(st.kyr), 3), st.lect] if st is not None else None


def _plain(w) -> str:
    """A god name's history in a line: how it was made, borrowed, renamed."""
    parts = []
    for s in w.etym:
        p = s.process.split(":", 1)
        if s.process == "name:god":
            parts.append(f"'{s.gloss}' ({s.note}) in {s.lect}, {s.kyr:g} kyr ago")
        elif p[0] == "borrow":
            parts.append(f"taken by {s.lect} from {p[1]}, {s.kyr:g} kyr ago")
        elif p[0] == "substrate":
            parts.append(f"kept through a shift by {s.lect}, {s.kyr:g} kyr ago")
    return "; ".join(parts)


def formulas(lit, gods: list) -> list:
    """Two or three fixed formulas of a liturgy, built with the sentence builder (sentences.py) on the frozen lect:
    an invocation ('<god>, hear us!'), a praise ('<god> is holy') and a petition ('<god> gives <the domain's gift>')."""
    from . import output as OU
    from . import sentences as SN
    if lit.grammar is None or not gods:
        return []
    sp = OU.Speller(lit)
    gj = OU.grammar_json(lit, sp)
    lex = {k: {"ipa": w.ipa} for k, w in lit.lexicon.words.items()}
    inv = lit.inventory
    from . import inventory as INV
    lj = {"typology": gj["typology"], "grams": gj["grams"], "paradigms": gj["paradigms"], "lexicon": lex,
          "classes": gj.get("classes"), "processes": gj.get("processes"),
          "inventory": {"consonants": INV.to_json(inv)["consonants"], "vowels": INV.to_json(inv)["vowels"]}}
    v = SN.View(lj)
    out = []
    key, god = gods[0]
    con = god_concept(key)
    if con not in v.lex:
        return []
    gw = lit.lexicon[con]
    gl = name_gloss(gw).replace(" ", ".")
    tries = []

    def invocation():
        if not v.w("HEAR") or not v.w("WE"):
            return None
        name = SN.Word(v.ipa(con), gl, con)
        words, vi, _n = SN.verb(v, "HEAR", mood="IMP")
        o = SN.pronoun(v, "WE")
        if o is None:
            return None
        SN.object_marker(v, words, words[vi], o.person)
        seq = [name] + ((o.words + words) if v.ov() else (words + o.words))
        return SN.finish(v, "invocation", f"{name_gloss(gw).capitalize()}, hear us!", seq, [])

    def praise():
        if not v.w("HOLY") or "holy" in name_gloss(gw):
            return None   # (not 'Holy is the holy one')
        s = SN.noun_phrase(v, con, gloss=gl)
        cop = SN._copula(v)
        pred = [SN.Word(v.ipa("HOLY"), "holy", "HOLY")]
        words = s.words + ((pred + ([SN.Word(cop[0], "COP")] if cop else [])) if v.ov() else (([SN.Word(cop[0], "COP")] if cop else []) + pred))
        return SN.finish(v, "praise", f"Holy is {name_gloss(gw)}.", words, [])

    def petition():
        g = GIFT.get(god.get("domain") or "")
        if not g or not v.w(g) or not v.w("GIVE"):
            return None
        s = SN.noun_phrase(v, con, gloss=gl)
        o = SN.noun_phrase(v, g)
        vw = SN.verb(v, "GIVE", "3SG")
        return SN.finish(v, "petition", f"{name_gloss(gw).capitalize()} gives {SN.en(g)}.", SN.clause(v, s, vw, o), [])

    for fn in (invocation, praise, petition):
        try:
            x = fn()
        except (KeyError, IndexError, ValueError, StopIteration, TypeError, AttributeError):
            x = None
        if x is not None:
            x.pop("note", None)
            out.append(x)
    return out


def faiths_json(result: dict) -> dict:
    """The doc's `faiths`: {faith id: {name, core, founded_kyr, peoples, holders: [lect], gods: [{key, domain, label, names:
    [[lect, ipa, roman, gloss, coined [kyr, lect]]], plain}], liturgy: {lect_from, deme, kyr, words: {concept: [ipa,
    roman]}, gods: {key: [ipa, roman, gloss]}, formulas}}} for the faiths held today; {} without a faith readout."""
    h = result["history"]
    P = h.__dict__.get("faith_plan")
    if not P:
        return {}
    out = {}
    for fid in sorted(P.faiths):
        F = P.faiths[fid]
        lects = []
        for d in F["holders"]:
            l = h.lect_of(d)
            if l is not None and l.alive and l.id not in lects:
                lects.append(l.id)
        keys = list(F.get("pantheon") or [])   # (one faith, one pantheon: every holder names these)
        gods = []
        for k in keys:
            con = god_concept(k)
            names, plain = [], None
            for lid in lects:
                l = h.lects[lid]
                w = l.lexicon.get(con)
                if w is None:
                    continue
                names.append([lid, w.ipa, _spell(l, w.form), name_gloss(w), _coined(w)])
                if plain is None:
                    plain = _plain(w)
            g = P.gods[k]
            gods.append({"key": k, "domain": g["domain"], "label": g["label"], "high": g["high"], "names": names,
                         "plain": plain or ""})
        rec = {"name": F["name"], "core": F["core"], "how": F["how"], "parent": F["parent"],
               "founded_kyr": F["founded_kyr"], "peoples": F["peoples"], "holders": lects, "gods": gods,
               "taboos": [list(t) for t in F.get("taboos") or []]}
        L = h.liturgy.get(fid)
        if L is not None:
            lit = L["lect"]
            words = {c: [lit.lexicon[c].ipa, _spell(lit, lit.lexicon[c].form).lower()] for c in LIT_WORDS if c in lit.lexicon}
            gn = {}
            gl = []
            for k in keys:
                w = lit.lexicon.get(god_concept(k))
                if w is not None:
                    gn[str(k)] = [w.ipa, _spell(lit, w.form), name_gloss(w)]
                    gl.append((k, P.gods[k]))
            rec["liturgy"] = {"lect_from": L["from"], "deme": L["deme"], "kyr": round(float(L["kyr"]), 3),
                              "people": lit.people, "words": words, "gods": gn, "formulas": formulas(lit, gl)}
        out[str(fid)] = rec
    return out
