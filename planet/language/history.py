"""The language driver (PW-986, architecture section 8): walks a stored peoples run from START_KYR (20 kyr ago) to the present
in its 0.5-kyr frame intervals and grows one lect per deme.

Per interval (never per generation; every per-generation hazard is batched over the interval's n = dt / generation length):
1. births: a budding deme's lect is its parent deme's lect copied (`how="bud"`, rate re-drawn a little); a deme whose people
   has no speech parent (an arrival's first demes, a people new in the window) gets a fresh proto-language (`how="arrival"`);
2. steps: every living lect runs its rule, lexical and grammar events (lect.Lect.step), borrowing replacement words from the
   lects it is in contact with;
3. wave: every rule that fired in lect X is offered to each lect Y in contact with X (contact above CONTACT_MIN); Y adopts it
   with p = tanh(WAVE_K x contact x prestige ratio / 2) when the rule applies to Y's sounds (judgement call: tanh rather than
   the contract's sigmoid, so that no contact gives no spread);
4. shift: under each active trigger (inputs.Trigger: elite rule, swamping, settlement takeovers, mixed cities, long trade
   contact) the ruled deme's share of the ruler's lect rises per generation by SHIFT_K x kind weight x strength x prestige
   factor x the ruler's presence on the ruled land; shares with no trigger decay. Past 0.5 the deme shifts: its new lect is
   the ruler's lect copied (`how="shift"`, `substrate=<old lect>`), spoken with the shifting people's own voice profile; it keeps
   the old lect's local words (landscape, local plants and animals, names: lexicon.substrate_transfer), takes an accent (some
   of the sounds the old lect lacked are heard as the nearest old sound, consistently: a correspondence), and calques one or
   two typology features from the old grammar;
5. food: every crop or animal arrival (inputs.Run.crop_arrivals) borrows the donor deme's word, coining it there first when
   the donor has none; an arrival with no donor coins its own word; so each hop chains and the etymology is the route;
6. deaths: an extinct or fused deme ends its lect.

Deterministic per seed: every draw comes from np.random.default_rng((seed, 986, crc32(<stable key>))), seed = meta.seed."""
from __future__ import annotations

import math
import time
import zlib
from pathlib import Path

import numpy as np

from . import inputs as I
from . import lect as LC
from . import lexicon as LX
from . import rules as RU

START_KYR = I.START_KYR
RATE_SCALE = float(__import__("os").environ.get("LANG_RATE_SCALE", "5.0"))  # multiplies lect.RATE_RULE (calibration lever; calibration.md)
REPLACE_SCALE = float(__import__("os").environ.get("LANG_REPLACE_SCALE", "1.0"))  # (1.25 -> 1.0 with lexicon.FREQ_SPREAD 10 -> 4, 2026-11-04) multiplies lexicon.BASE_REPLACE through the generations handed to lexicon.step (calibration lever)
PROTO_LINK = 0.05  # same-people contact that joins start demes into one proto-language
CONTACT_MIN = 0.05  # contact for the wave
CONTACT_BORROW = 0.1  # contact for lexical borrowing on replacement
WAVE_K = 3.0
PRESTIGE_CAP = 4.0
SHIFT_K = 0.015  # per generation, at strength 1, kind weight 1, equal prestige, full presence
SHIFT_DECAY = 0.01  # per generation, of a share with no trigger behind it
SHIFT_AT = 0.5
KIND_WEIGHT = {"elite": 1.0, "takeover": 0.6, "swamp": 1.0, "city": 0.5, "trade": 0.08}
ACCENT_P = 0.5  # share of the missing sounds the shifting speakers replace (consistently)
CALQUE_MAX = 2
WORKERS = int(__import__("os").environ.get("LANG_WORKERS", "1"))  # forked processes for the steps (1 = this process)
KOINE_HARD = 3.0  # a sound is hard for a people when its make cost is this many times the human cost (or impossible)
KOINE_MAJ = 0.5  # share of a mixed city's heads for whom a sound is hard before koine pressure acts on it
KOINE_RATE = 0.02  # per generation, x city weight x the hard share: chance a hard sound is replaced in the holder's lect
KOINE_CITY = 20.0  # city weight = min(1, KOINE_CITY x city heads / the holding deme's heads)
KIN_KYR = 4.0  # lects parted more recently than this are one speech for shift purposes
SHIFT_COOLDOWN_KYR = 6.0  # a deme does not shift again within this long of its last shift
SHIFT_MAX = 3  # ... and shifts at most this many times in SHIFT_MAX_KYR
SHIFT_MAX_KYR = 20.0
SHIFT_KIN_SHARE = 0.3  # a shift to a lect of the deme's own true family needs a blind core share under this (else it levels)
MINORITY_MIN = 0.1  # a shifted-away lect lives on (a minority speech of its deme) until its share falls under this
STRONG_WAVE = 1.0  # contact used for the wave while a shift trigger holds on a pair already speaking one language
KOINE_LEVEL = 0.1  # per interval, chance each differing core word of a koine receiver is borrowed from the majority lect
# driver-side draw (and wave adoption) weight overrides, by rule id, catalogue id or `family:<name>` (lect.weight_override):
# ʔ-prothesis is rare; tonogenesis (which needs the conditioning coda/onset contrast lost) and vowel reduction are not drawn in
# every lect; the onset-voicing split, never vetoed (it merges nothing), was the tone source of nearly every lect at 0.3
RULE_WEIGHT = {"S042": 0.15, "family:tone": 0.3, "tone.onset_voicing_split": 0.05, "family:reduction": 0.5,
               "S073": 0.1}  # (u > y: with y > i after it, the u of every lect drained into i)


def rng_for(seed: int, *key) -> np.random.Generator:
    return np.random.default_rng((int(seed), 986, zlib.crc32(":".join(map(str, key)).encode())))


class History:
    """The state of the pass; `generate` drives it."""

    def __init__(self, run: I.Run, seed: int | None = None, log_every: bool = False):
        self.R = run
        self.seed = int(run.seed if seed is None else seed)
        self.concepts = LX.concepts(run.meta)
        self.lects: dict[str, LC.Lect] = {}
        self.by_deme: dict[int, str] = {}
        self.first_family: dict[int, str] = {}  # deme -> root of its first lect (for the shift check)
        self.shifts: list[dict] = []
        self.routes: dict = {}  # root key -> route
        self.log: list[str] = []
        self.timing: dict = {}
        self._profiles: dict = {}
        self._prest: dict = {}
        self._n_shift: dict[int, int] = {}
        self.proto_count = 0
        self.intel: dict = {}  # (lect a, lect b) a < b -> {frame: intelligibility}
        self.intel_now: list = []
        self._root: dict = {}
        self.pending: dict = {}  # lect id -> [(rule, origin lect, kyr)]: wave adoptions to apply at its next step
        self._snap: dict = {}
        self.minority: dict[int, list[str]] = {}  # deme -> shifted-away lects still spoken there (oldest first)
        self.last_shift: dict[int, float] = {}  # deme -> kyr of its last shift
        self.shift_times: dict[int, list] = {}  # deme -> kyr of each shift (SHIFT_MAX)
        self.forced: dict = {}  # (giver lect, receiver lect) -> wave probability, for the next interval (strong contact, koine)
        self.route_ev: dict = {}  # (lect, concept, kyr, process) of a route event's etymology step -> its food route key
        self._lang: dict = {}

    # ------------------------------------------------------------------ helpers
    def say(self, kyr: float, text: str) -> None:
        self.log.append(f"{kyr:.1f} kyr ago: {text}")

    def profile(self, people: str):
        if people not in self._profiles:
            self._profiles[people] = self.R.profile(people)
        return self._profiles[people]

    def prestige(self, deme: int, i: int) -> float:
        k = (deme, i)
        if k not in self._prest:
            self._prest[k] = max(self.R.prestige(deme, i), 1.0)
        return self._prest[k]

    def lect_of(self, deme: int) -> LC.Lect | None:
        lid = self.by_deme.get(deme)
        return self.lects.get(lid) if lid else None

    def deme_label(self, deme: int) -> str:
        return self.R.demes[deme].get("short") or f"deme {deme}"

    def add(self, l: LC.Lect) -> LC.Lect:
        self.lects[l.id] = l
        if l.deme is not None:
            self.by_deme[l.deme] = l.id
            l.deme_name = self.R.demes[l.deme].get("name")
        return l

    # ------------------------------------------------------------------ protos
    def make_proto(self, people: str, key: str, kyr: float, how: str) -> LC.Lect:
        rng = rng_for(self.seed, "proto", key)
        prof = self.profile(people)
        inv = LC.draw_inventory(rng, prof)
        pid = f"p{self.proto_count}"
        self.proto_count += 1
        lex = LX.proto_lexicon(rng, inv, self.concepts, kyr, pid)
        gram = None
        GR = LC._gr_mod()
        if GR is not None and hasattr(GR, "proto_grammar"):
            gram = proto_grammar(GR, rng, lex, inv, prof, kyr, pid)
            hf = head_first_of(GR, gram)
            if hf is not None:
                lex.head_first = hf
        rate = float(math.exp(rng.normal(0.0, LC.RATE_SIGMA)))
        p = LC.Lect(id=pid, deme=None, people=people, parent=None, how=how, born_kyr=float(kyr), rate=rate, inventory=inv,
                    lexicon=lex, grammar=gram, profile=prof, profile_key=people, gen_yr=self.R.generation_yr(people))
        p.died_kyr = float(kyr)
        p.end = "split"
        return self.add(p)

    def daughter(self, parent: LC.Lect, deme: int, kyr: float, how: str, rng=None) -> LC.Lect:
        lid = f"d{deme}"
        if lid in self.lects:
            n = self._n_shift.get(deme, 0) + 1
            self._n_shift[deme] = n
            lid = f"d{deme}.{n}"
        l = parent.copy(lid, deme, kyr, how, rng)
        people = self.R.people_of(deme)
        if people != parent.people:  # (a deme of another people speaking it: its own voice)
            l.people = people
            l.profile = self.profile(people)
            l.profile_key = people
            l.gen_yr = self.R.generation_yr(people)
        return self.add(l)

    def start(self) -> None:
        R = self.R
        for p, ov in sorted(R.generation_overrides.items()):
            self.say(START_KYR, f"generation length of {p}: {ov['stored_yr']} yr stored in the run, {ov['current_yr']} yr under the "
                                f"current preset ({Path(ov['spec']).name if ov.get('spec') else '?'}); the current one is used")
        for comp in R.start_components(PROTO_LINK):
            people = R.people_of(comp[0])
            k0 = R.kyr(0)
            p = self.make_proto(people, f"start:{comp[0]}", k0, "proto")
            for d in comp:
                l = self.daughter(p, d, k0, "proto")
                self.first_family[d] = p.id
            self.say(k0, f"proto-language {p.id} of the {people}: spoken by {len(comp)} deme(s), "
                                f"{', '.join(self.deme_label(d) for d in comp[:4])}{' ...' if len(comp) > 4 else ''}")
        for d, concept in R.known_at_start():
            l = self.lect_of(d)
            if l is not None and concept not in l.lexicon:
                LX.coin(rng_for(self.seed, "coin0", d, concept), l.lexicon, concept, l.inventory, R.kyr(0), l.id)

    def birth(self, deme: int, parent_deme: int | None, i: int) -> None:
        kyr = self.R.kyr(i)
        if deme in self.by_deme:
            return
        pl = self.lect_of(parent_deme) if parent_deme is not None else None
        if pl is None and parent_deme is not None:  # (a parent that never had a lect: look up its line)
            p2 = self.R.parent_deme(parent_deme)
            pl = self.lect_of(p2) if p2 is not None else None
        if pl is not None:
            self.daughter(pl, deme, kyr, "bud", rng_for(self.seed, "bud", deme))
            self.first_family.setdefault(deme, LC_root(self, pl))
            self.say(kyr, f"{self.deme_label(deme)} budded off {self.deme_label(pl.deme) if pl.deme is not None else pl.id}: "
                          f"lect {self.by_deme[deme]} from {pl.id}")
            return
        people = self.R.people_of(deme)
        how = "arrival" if self.R.is_arrival(people) else "proto"
        p = self.make_proto(people, f"birth:{deme}", kyr, how)
        self.daughter(p, deme, kyr, how)
        self.first_family[deme] = p.id
        self.say(kyr, f"{self.deme_label(deme)} ({people}) speaks a new language {p.id} ({how})")

    # ------------------------------------------------------------------ one interval
    def interval(self, i: int) -> None:
        R = self.R
        t0, t1 = R.kyr(i - 1), R.kyr(i)
        tm = time.perf_counter()
        ev = R.events_in(i)
        for child, parent in sorted(ev["buds"]):
            self.birth(child, parent, i)
        for d in sorted(ev["births"]):
            self.birth(d, None, i)
        alive = R.demes_alive(i)
        for d in alive:
            if d not in self.by_deme:
                self.birth(d, R.parent_deme(d), i)
        self.timing["births"] = self.timing.get("births", 0.0) + time.perf_counter() - tm
        # steps (own changes, lexical and grammar events; the wave adoptions decided last interval first)
        tm = time.perf_counter()
        living = [self.lect_of(d) for d in alive if self.lect_of(d) is not None]
        living = [l for l in living if l.alive]
        for d in alive:  # (minority speech of a shifted deme steps too)
            living += [self.lects[m] for m in self.minority.get(d, ()) if self.lects[m].alive]
        contacts = {l.deme: R.contacts_of(l.deme, i, CONTACT_MIN) for l in living}
        self._snap = {l.id: l.lexicon.copy() for l in living}  # (borrowing reads the lexicons as they were at the interval's start)
        tasks = []
        for l in living:
            n = (t0 - t1) * 1000.0 / l.gen_yr
            cids = []
            for o, c in contacts[l.deme].items():
                ol = self.lect_of(o)
                if ol is not None and ol.alive and c >= CONTACT_BORROW and ol.id != l.id:
                    cids.append(ol.id)
            for x in self.deme_speech(l.deme):  # (the other speech of the same deme: the dominant lect, its minorities)
                if x.id != l.id:
                    cids.append(x.id)
            ctx = {"contact_ids": sorted(set(cids)), "niche": niche_for(R, l.deme, i), "l2": R.l2_share(l.deme, i),
                   "population": R.deme_population(l.deme, i), "isolation": R.isolation(l.deme, i),
                   "rate_scale": RATE_SCALE, "replace_scale": REPLACE_SCALE, "rule_weight": RULE_WEIGHT}
            tasks.append((l.id, i, n, t1, ctx, self.pending.pop(l.id, [])))
        fired = self.run_steps(tasks)
        self.timing["steps"] = self.timing.get("steps", 0.0) + time.perf_counter() - tm
        # wave: decide the adoptions now, apply them at the start of the receiver's next step
        tm = time.perf_counter()
        forced, self.forced = self.forced, {}
        for d in alive:  # (the dominant lect's changes reach its deme's minority speech)
            ml = self.lect_of(d)
            for m in self.minority.get(d, ()):
                if ml is not None and ml.alive and self.lects[m].alive:
                    forced.setdefault((ml.id, m), math.tanh(WAVE_K * STRONG_WAVE / 2.0))
        by_giver: dict = {}
        for (g, r), p in sorted(forced.items()):
            by_giver.setdefault(g, []).append((r, p))
        for l in living:
            if not fired.get(l.id):
                continue
            px = self.prestige(l.deme, i)
            offers = []
            for o, c in sorted(contacts[l.deme].items()):
                y = self.lect_of(o)
                if y is None or not y.alive or y.id == l.id or (l.id, y.id) in forced:
                    continue
                ratio = min(px / self.prestige(o, i), PRESTIGE_CAP)
                # (a change spreads through children learning it: a receiver living fewer generations in the interval than
                # the giver adopts proportionally less, so long-lived peoples are not swept by short-lived neighbours)
                offers.append((y, math.tanh(WAVE_K * c * ratio / 2.0) * min(1.0, l.gen_yr / y.gen_yr)))
            for yid, p in by_giver.get(l.id, ()):
                y = self.lects.get(yid)
                if y is not None and y.alive and y.id != l.id:
                    offers.append((y, p))
            for y, p in offers:
                rng = rng_for(self.seed, "wave", l.id, y.id, i)
                for r in fired[l.id]:
                    w = LC.weight_override(RULE_WEIGHT, r)
                    w = 1.0 if w is None else w
                    if r.family == "tone" or r.cause == "tonogenesis":  # (an ear that hears tone coarsely takes it up less)
                        w *= min(1.0, (getattr(y.profile, "hear", None) or {}).get("tone", 1.0)) ** 2
                    w *= min(1.0, LC.ease_factor(r, y))  # (a change toward rarer sounds spreads as reluctantly as it arises)
                    w *= min(1.0, LC.size_factor(r, y))  # (... and one that takes the receiver's inventory off its line's size)
                    if rng.random() < p * min(1.0, w):
                        self.pending.setdefault(y.id, []).append((r, l.id, t1))
        self.timing["wave"] = self.timing.get("wave", 0.0) + time.perf_counter() - tm
        tm = time.perf_counter()
        self.koine_step(i)
        self.timing["koine"] = self.timing.get("koine", 0.0) + time.perf_counter() - tm
        tm = time.perf_counter()
        self.shift_step(i, alive)
        self.timing["shift"] = self.timing.get("shift", 0.0) + time.perf_counter() - tm
        tm = time.perf_counter()
        self.food_step(i)
        self.timing["food"] = self.timing.get("food", 0.0) + time.perf_counter() - tm
        for absorbed, host in ev["fusions"]:
            l = self.lect_of(absorbed)
            self.end_minorities(absorbed, t1, "fused")
            if l is not None and l.alive:
                l.died_kyr, l.end = t1, "fused"
                h = self.lect_of(host)
                self.say(t1, f"{self.deme_label(absorbed)} merged into {self.deme_label(host)}; lect {l.id} ends"
                             f"{' (its speakers now speak ' + h.id + ')' if h is not None else ''}")
        for d in ev["extinct"]:
            self.end_minorities(d, t1, "extinct")
            l = self.lect_of(d)
            if l is not None and l.alive:
                l.died_kyr, l.end = t1, "extinct"
                self.say(t1, f"{self.deme_label(d)} died out; lect {l.id} ends")
        tm = time.perf_counter()
        self.observe(i)
        self.timing["observe"] = self.timing.get("observe", 0.0) + time.perf_counter() - tm

    def run_steps(self, tasks: list) -> dict:
        """Step every living lect (own events after the pending wave adoptions): in this process, or over WORKERS forked
        processes that inherit this interval's state and send back the stepped lects. Same result either way."""
        global _H
        _H = self
        w = min(WORKERS, len(tasks))
        if w <= 1:
            return dict(_work(t) for t in tasks)
        import multiprocessing as mp
        for t in tasks:  # (catalogues built once here, inherited by the workers)
            l = self.lects[t[0]]
            LC.catalogue_for(l.profile, l.profile_key)
        order = sorted(tasks, key=lambda t: -t[2])  # (longest first)
        with mp.get_context("fork").Pool(w) as pool:
            res = pool.map(_work_remote, order, chunksize=max(1, len(order) // (4 * w)))
        out = {}
        for lid, (l, f) in res:
            l.profile = self.profile(l.profile_key)
            self.lects[lid] = l
            out[lid] = f
        return out

    def deme_speech(self, deme: int) -> list:
        """Every living lect spoken in a deme: the dominant one, then its minority speech."""
        out = [self.lects[m] for m in self.minority.get(deme, ()) if self.lects[m].alive]
        l = self.lect_of(deme)
        return ([l] if l is not None and l.alive else []) + out

    def end_minorities(self, deme: int, kyr: float, end: str) -> None:
        for m in self.minority.pop(deme, []):
            ml = self.lects[m]
            if ml.alive:
                ml.died_kyr, ml.end = kyr, end

    def same_language(self, a: LC.Lect, b: LC.Lect, i: int) -> bool:
        """One language: the same true family and a blind core-list share at or above families.LANG_SHARE (or parted less
        than KIN_KYR ago). Cached per frame."""
        if a.id == b.id:
            return True
        key = (min(a.id, b.id), max(a.id, b.id), i)
        v = self._lang.get(key)
        if v is None:
            from . import families as FA
            if self.root(a) != self.root(b):
                v = False
            elif self.kin_recent(a, b):
                v = True
            else:
                v = FA.cognate_share(a, b, CORE, blind=True) >= FA.LANG_SHARE
            if len(self._lang) > 200_000:
                self._lang.clear()
            self._lang[key] = v
        return v

    def flush_pending(self) -> None:
        """Apply the wave adoptions decided in the last interval (at the end of the pass)."""
        for lid in sorted(self.pending):
            l = self.lects.get(lid)
            if l is not None and l.alive:
                adopt(l, self.pending[lid])
                l.sync()
        self.pending = {}

    # ------------------------------------------------------------------ koine
    def koine_step(self, i: int) -> None:
        """Koine pressure in mixed cities (owner, 2026-11-03): in a city whose heads hold two or more peoples (each >= 10%), a
        sound of the holding deme's lect that most of the city's heads cannot make cheaply (make cost >= KOINE_HARD x the
        human cost, by each people's voice profile, weighted by heads) is replaced, with a per-generation hazard, by the nearest
        sound the majority people makes cheaply (profiles.hear_word over the lect's cheap sounds), consistently over the
        lexicon and grammar; logged as a `koine` change. Human-only cities exert none (every cost equals the human cost)."""
        from . import percepts as PC, profiles as PR
        R = self.R
        t0, t1 = R.kyr(i - 1), R.kyr(i)
        for c in R.mixed_cities(i):
            l = self.lect_of(c["holder_deme"])
            if l is None or not l.alive:
                continue
            self.koine_level(c, l, i)
            n = (t0 - t1) * 1000.0 / l.gen_yr
            w = min(1.0, KOINE_CITY * c["pop"] / max(R.deme_population(c["holder_deme"], i), 1.0))
            profs = {p: self.profile(p) or PR.HUMAN for p in c["who"]}
            segs = l.segments()
            hard = {}
            for x in segs:
                hcost = max(PR.human_cost(x) if not PC.is_nonhuman(x) else PR.NONHUMAN_BASE, 0.1)
                hs = sum(sh for p, sh in c["who"].items() if PR.species_cost(profs[p], x) >= KOINE_HARD * hcost)
                if hs >= KOINE_MAJ:
                    hard[x] = hs
            if not hard:
                continue
            rng = rng_for(self.seed, "koine", l.id, c["site"], i)
            maj = max(c["who"], key=lambda p: (c["who"][p], p))
            cheap = [x for x in segs if x not in hard]
            mapping = {}
            for x in sorted(hard, key=lambda q: (PC.to_ipa(q), repr(q))):
                if rng.random() >= 1.0 - math.exp(-KOINE_RATE * n * w * hard[x]):
                    continue
                cand = [y for y in cheap if y.kind == x.kind]
                hw = PR.hear_word([x], profs[maj], cand) if cand else ()
                mapping[x] = hw[0] if hw else None
            if not mapping:
                continue

            def fn(f, stem_index=0, m=mapping):
                return tuple(m.get(y, y) for y in f if m.get(y, y) is not None)
            LX.apply_rule_to_lexicon(l.lexicon, fn, f"koine:{c['site']}", t1, l.id)
            GR = LC._gr_mod()
            if GR is not None and l.grammar is not None:
                GR.apply_rule_to_grammar(l.grammar, fn, f"koine:{c['site']}", t1)
            l.touch()
            l._dirty = True
            l.sync()
            what = ", ".join(f"{PC.to_ipa(a)} > {PC.to_ipa(b) if b is not None else '0'}" for a, b in mapping.items())
            l.changes.append({"kyr": round(t1, 3), "rule": "koine", "cause": "koine", "origin_lect": None,
                              "city": c["site"], "peoples": sorted(c["who"]), "merged": what})
            self.say(t1, f"koine in city {c['site']} ({', '.join(sorted(c['who']))}): {l.id} {what}")

    def koine_level(self, c: dict, holder: LC.Lect, i: int) -> None:
        """Koine levelling (PW-986 review, section 9): in a mixed city, each other people's lect on the city's cell that is one
        language with the holder's (same_language) levels with it: the lect of the people with the smaller share of the city's
        heads (the holder's on a tie) takes up the other's sound changes by wave at p ~ 1 (next interval) and borrows its core
        words with probability KOINE_LEVEL per word per interval; logged as `koine.level`, merged "levelled to <lect>"."""
        R = self.R
        t1 = R.kyr(i)
        hp = R.people_of(holder.deme)
        for p in sorted(c["who"]):
            d = R.deme_at_cell(p, c["cell"], i)
            o = self.lect_of(d) if d is not None else None
            if o is None or not o.alive or o.id == holder.id or not self.same_language(holder, o, i):
                continue
            recv, give = (holder, o) if c["who"].get(p, 0.0) >= c["who"].get(hp, 0.0) else (o, holder)
            self.forced[(give.id, recv.id)] = 1.0
            rng = rng_for(self.seed, "koine-level", recv.id, give.id, c["site"], i)
            n = 0
            for concept in CORE:
                wg, wr = give.lexicon.get(concept), recv.lexicon.get(concept)
                if wg is None or wr is None or wg.form == wr.form:
                    continue
                if rng.random() < KOINE_LEVEL:
                    LX.borrow(wg, give.id, recv.lexicon, recv.profile, recv.inventory, t1,
                              note=f"koine levelling in city {c['site']}")
                    n += 1
            if n:
                recv.touch()
                recv._dirty = True
                recv.sync()
            recv.changes.append({"kyr": round(t1, 3), "rule": "koine.level", "cause": "koine", "origin_lect": give.id,
                                 "city": c["site"], "peoples": sorted(c["who"]),
                                 "merged": f"levelled to {give.id} ({n} core word{'s' if n != 1 else ''} borrowed)"})
            self.say(t1, f"koine in city {c['site']}: {recv.id} levels toward {give.id} ({n} core words)")

    # ------------------------------------------------------------------ snapshots and intelligibility
    def root(self, l: LC.Lect) -> str:
        if l.id not in self._root:
            self._root[l.id] = LC_root(self, l)
        return self._root[l.id]

    def observe(self, i: int) -> None:
        """Per-frame snapshot of every living lect, and intelligibility between lects in contact or of one family."""
        from . import families as FA
        R = self.R
        kyr = R.kyr(i)
        living = sorted((l for l in self.lects.values() if l.alive and l.deme is not None), key=lambda l: l.id)
        for l in living:
            full = snapshot(l)
            prev = getattr(l, "_snap_full", None)
            l.snapshots.append([kyr, full if prev is None else snapshot_delta(prev, full)])
            l._snap_full = full
        if len(living) < 2:
            return
        idx = {l.id: j for j, l in enumerate(living)}
        tab = FA.WordTable(living, CORE, LC.word_form)
        pairs = set()
        for a, b in R.frame(i).pairs:
            la, lb = self.lect_of(a), self.lect_of(b)
            if la is not None and lb is not None and la.alive and lb.alive and la.id != lb.id:
                pairs.add(tuple(sorted((la.id, lb.id))))
        groups: dict = {}
        for l in living:
            groups.setdefault(self.root(l), []).append(l.id)
        for g in groups.values():
            for x in range(len(g)):
                for y in range(x + 1, len(g)):
                    pairs.add((g[x], g[y]) if g[x] < g[y] else (g[y], g[x]))
        last = i == len(R.frames_kyr) - 1
        if last:
            pl = [(a.id, b.id) for x, a in enumerate(living) for b in living[x + 1:]]
        else:
            pl = sorted(pairs)
        if not pl:
            return
        ia = np.array([idx[a] for a, _ in pl])
        ib = np.array([idx[b] for _, b in pl])
        typ = [l._snap_full["typ"] for l in living]
        v = FA.pair_intelligibility(tab, ia, ib, [typ[j] for j in ia], [typ[j] for j in ib])
        for (a, b), x in zip(pl, v.tolist()):
            if last and (a, b) not in pairs:
                continue
            self.intel.setdefault((a, b), {})[i] = round(x, 3)
        if last:
            self.intel_now = [[a, b, round(x, 3)] for (a, b), x in zip(pl, v.tolist()) if x >= 0.05]

    # ------------------------------------------------------------------ shift
    def kin_recent(self, a: LC.Lect, b: LC.Lect) -> bool:
        """True when two lects' lines parted less than KIN_KYR ago (a shift between them would be no shift)."""
        from .families import divergence
        return divergence(a, b, self.lects) <= KIN_KYR

    def shift_step(self, i: int, alive: list[int]) -> None:
        R = self.R
        t0, t1 = R.kyr(i - 1), R.kyr(i)
        push: dict = {}  # ruled deme -> {ruler lect id: (rate per generation, trigger)}
        for tr in R.shift_triggers(i):
            ld, lr = self.lect_of(tr.ruled_deme), self.lect_of(tr.ruler_deme)
            if ld is None or lr is None or not ld.alive or not lr.alive or ld.id == lr.id:
                continue
            if self.same_language(ld, lr, i):  # (already speaking the ruler's language: strong contact, not a shift)
                self.forced[(lr.id, ld.id)] = math.tanh(WAVE_K * STRONG_WAVE / 2.0)
                continue
            ratio = self.prestige(tr.ruler_deme, i) / self.prestige(tr.ruled_deme, i)
            pf = math.sqrt(min(max(ratio, 1.0 / PRESTIGE_CAP), PRESTIGE_CAP))
            presence = min(max(R.contact(tr.ruler_deme, tr.ruled_deme, i), 0.05), 1.0)
            g = SHIFT_K * KIND_WEIGHT.get(tr.kind, 0.5) * tr.strength * pf * presence
            cur = push.setdefault(tr.ruled_deme, {})
            if lr.id in cur:
                cur[lr.id] = (cur[lr.id][0] + g, cur[lr.id][1] if cur[lr.id][0] >= g else tr)
            else:
                cur[lr.id] = (g, tr)
        for d in alive:
            l = self.lect_of(d)
            if l is None or not l.alive:
                continue
            n = (t0 - t1) * 1000.0 / l.gen_yr
            p = push.get(d, {})
            for lid in list(l.shares):
                if lid not in p:
                    l.shares[lid] *= math.exp(-SHIFT_DECAY * n)
                    if l.shares[lid] < 0.005:
                        del l.shares[lid]
            for lid, (g, tr) in p.items():
                s = l.shares.get(lid, 0.0)
                l.shares[lid] = s + (1.0 - s) * (1.0 - math.exp(-g * n))
            mins = self.minority.get(d, [])
            for m in list(mins):  # (a minority speech dies when its share falls under MINORITY_MIN)
                if l.shares.get(m, 0.0) < MINORITY_MIN:
                    ml = self.lects[m]
                    if ml.alive:
                        ml.died_kyr, ml.end = t1, "shifted"
                        self.say(t1, f"{self.deme_label(d)}: the old speech {m} is no longer spoken")
                    mins.remove(m)
                    l.shares.pop(m, None)
            if l.shares:
                l.record_shares(t1)
                cand = [k for k in l.shares if k in self.lects and self.lects[k].alive and self.lects[k].deme != d]
                best = max(cand, key=lambda k: (l.shares[k], k)) if cand else None
                if (best is not None and l.shares[best] >= SHIFT_AT
                        and self.last_shift.get(d, math.inf) - t1 >= SHIFT_COOLDOWN_KYR - 1e-9
                        and sum(1 for k in self.shift_times.get(d, ()) if k - t1 < SHIFT_MAX_KYR - 1e-9) < SHIFT_MAX
                        and not self.same_language(l, self.lects[best], i) and not self.kin_close(l, self.lects[best])):
                    self.shift(d, l, self.lects[best], p.get(best, (0, None))[1], i)

    def kin_close(self, a: LC.Lect, b: LC.Lect) -> bool:
        """Two lects of one true family still sharing SHIFT_KIN_SHARE or more of the blind core list: a deme speaking one does
        not shift to the other (the wave and koine level them instead); half the run's shifts were such re-shifts."""
        if self.root(a) != self.root(b):
            return False
        from . import families as FA
        return FA.cognate_share(a, b, CORE, blind=True) >= SHIFT_KIN_SHARE

    def shift(self, deme: int, old: LC.Lect, ruler: LC.Lect, trig, i: int) -> None:
        R = self.R
        t1 = R.kyr(i)
        rng = rng_for(self.seed, "shift", deme, i)
        new = self.daughter(ruler, deme, t1, "shift")
        new.substrate = old.id
        new.shares_history = list(old.shares_history)
        new.shares = {old.id: round(1.0 - old.shares.get(ruler.id, 0.5), 3)}
        for m in self.minority.get(deme, ()):  # (older minority speech of the deme keeps its share)
            if m in old.shares and self.lects[m].alive:
                new.shares[m] = old.shares[m]
        kept = LX.substrate_transfer(old.lexicon, new.lexicon, kyr=t1, inv=new.inventory, profile=new.profile)
        new.touch()
        accent = self.accent(rng, old, new, t1)
        calques = calque(rng, old, new)
        # (the old lect lives on as the deme's minority speech while its share holds: shift_step ends it under MINORITY_MIN)
        old.minority = True
        old.shares = {}
        self.minority.setdefault(deme, []).append(old.id)
        self.last_shift[deme] = t1
        self.shift_times.setdefault(deme, []).append(t1)
        rec = {"deme": deme, "kyr": t1, "from_lect": old.id, "to_lect": new.id, "ruler_lect": ruler.id,
               "ruler_deme": ruler.deme, "trigger": trig.to_json() if trig is not None else None,
               "substrate_words": kept, "accent": accent, "calques": calques,
               "speakers": R.people_of(deme), "ruler_people": ruler.people}
        self.shifts.append(rec)
        self.say(t1, f"{self.deme_label(deme)} ({R.people_of(deme)}) shifted from {old.id} to the speech of "
                     f"{self.deme_label(ruler.deme) if ruler.deme is not None else ruler.id} ({ruler.people}, lect {ruler.id}); "
                     f"{len(kept)} local words kept, {len(accent)} sounds heard the old way"
                     f"{'; why: ' + trig.source if trig is not None else ''}")

    def accent(self, rng, old: LC.Lect, new: LC.Lect, kyr: float) -> list:
        """Some of the sounds the old lect lacked are replaced by the nearest old sound (as the shifting speakers hear it),
        consistently over the whole lexicon and grammar: a substrate accent."""
        from . import percepts as PC
        old_s = old.segments()
        if not old_s:
            return []
        hear = getattr(new.profile, "hear", None) or None
        have = set(old_s)
        pairs = []
        mapping = {}
        for s in sorted(set(new.segments()) - have, key=lambda q: (PC.to_ipa(q), repr(q))):
            if rng.random() >= ACCENT_P:
                continue
            best = min(old_s, key=lambda o: (PC.distance(s, o, hear), PC.to_ipa(o), repr(o)))
            if best.kind != s.kind:
                continue
            mapping[s] = best
            pairs.append([PC.to_ipa(s), PC.to_ipa(best)])
        if not mapping:
            return []

        def fn(f):
            return tuple(mapping.get(x, x) for x in f)
        kept = {k for k, w in new.lexicon.words.items() if any(st.process.startswith("substrate:") for st in w.etym[-1:])}
        saved = {k: new.lexicon.words[k] for k in kept}
        LX.apply_rule_to_lexicon(new.lexicon, fn, f"accent:{old.id}", kyr, new.id)
        new.touch()
        new.lexicon.words.update(saved)
        GR = LC._gr_mod()
        if GR is not None and new.grammar is not None:
            GR.apply_rule_to_grammar(new.grammar, fn, f"accent:{old.id}", kyr)
        LC._sync_inventory(new, kyr)
        new.changes.append({"kyr": round(kyr, 3), "rule": f"accent:{old.id}", "cause": "substrate", "origin_lect": old.id})
        return pairs

    # ------------------------------------------------------------------ food
    def food_step(self, i: int) -> None:
        """Every crop or animal arrival of the frame (inputs.Run.crop_arrivals, donors from the previous frame): the receiver
        borrows the donor's word as it stands now (so each hop's donor form is the receiver's source), the donor coining
        one first when it has none; a taming deme (or an arrival nobody could have passed on) coins its own: a route origin."""
        R = self.R
        t1 = R.kyr(i)
        ci = LX.concept_index()
        for d, concept, donor, origin, how in R.crop_arrivals(i):
            l = self.lect_of(d)
            if l is None or not l.alive:
                continue
            if concept not in ci and LX.resolve(concept) not in ci:
                continue
            if concept in l.lexicon:
                continue
            dl = self.lect_of(donor) if donor is not None else None
            if dl is not None and dl.alive and dl.id != l.id:
                if concept not in dl.lexicon:
                    self.coin_food(dl, concept, t1, donor, origin=False)
                src = dl.lexicon[concept]
                w = LX.borrow(src, dl.id, l.lexicon, l.profile, l.inventory, t1,
                              note=f"with the {LX.concept_info(concept).gloss.lower()} from {self.deme_label(donor)}"
                                   f"{' over the sea' if how == 'sea' else ''}")
                self.route_hop(concept, src, w, l, dl, d, donor, t1, how)
            else:
                self.coin_food(l, concept, t1, d, origin=origin)
            l.touch()

    def coin_food(self, l: LC.Lect, concept: str, kyr: float, deme: int, origin: bool) -> None:
        w = LX.coin(rng_for(self.seed, "coin", l.id, concept), l.lexicon, concept, l.inventory, kyr, l.id)
        key = (concept, l.id, kyr)
        self.routes[key] = {"concept": concept, "origin_deme": deme, "origin_lect": l.id, "kyr": kyr, "ipa": w.ipa,
                            "origin": "tamed here" if origin else ("first known here" if deme is not None else ""),
                            "hops": []}
        if w.etym:
            self.route_ev[_ev(w.etym[-1], concept)] = key

    def route_key_of(self, word, concept: str):
        """The route a word for a crop came by, read from its own etymology (the one source of truth, shared with the
        receivers' etymology records): the latest step of its chain that was a route event (a coinage on arrival or a hop's
        borrowing), looking through other borrowings (a loan renewed by contact is the same word). Stops at the first other
        word-formation step (a later coinage, derivation, compound, shift of meaning, taboo): the word came another way, and
        None is returned with that step."""
        for st in reversed(word.etym):
            k = self.route_ev.get(_ev(st, concept))
            if k is not None:
                return k, None
            if st.process.split(":", 1)[0] in ROUTE_FORMATION:
                return None, st
        return None, None

    def route_hop(self, concept, src, w, l, dl, deme, donor, kyr, how: str = "land") -> None:
        key, st = self.route_key_of(src, concept)
        r = self.routes.get(key) if key is not None else None
        if r is None:  # (the donor's word came another way: inherited, substrate or coined outside a route)
            okyr = round(float(st.kyr), 3) if st is not None else None
            key = (concept, dl.id, okyr)
            r = self.routes.get(key)
            if r is None:
                r = self.routes[key] = {"concept": concept, "origin_deme": dl.deme, "origin_lect": dl.id, "kyr": None,
                                        "ipa": src.ipa, "origin": "inherited by the donor", "hops": [],
                                        "word_from": ({"kyr": okyr, "lect": st.lect, "process": st.process} if st is not None else None)}
        since = []
        for s in reversed(src.etym):
            if s.process.startswith(("borrow:", "coin", "derive:", "compound:", "proto")):
                break
            since.append(s.process)
        r["hops"].append({"deme": deme, "lect": l.id, "kyr": kyr, "ipa": w.ipa, "from_deme": donor, "from_lect": dl.id,
                          "from_ipa": src.ipa, "changes": since[::-1], "how": how})
        if w.etym:
            self.route_ev[_ev(w.etym[-1], concept)] = key


# word-formation steps: a word whose chain has one of these after a route event did not come by that route (a borrowing
# is not one: it hands the same word on, as a renewed loan does; nor is substrate:, a word kept through a shift)
ROUTE_FORMATION = frozenset(("proto", "coin", "derive", "compound", "shift", "taboo", "elaborate"))


def _ev(step, concept: str) -> tuple:
    """A route event's key: the etymology step (lect, kyr, process) of the word it made, for the concept."""
    return (step.lect, concept, round(float(step.kyr), 3), step.process)


def hop_status(h: "History", hop: dict, concept: str) -> dict:
    """Does the receiver's word for the concept still come from this hop? Read from the receiver lect's own word at its end
    (now for a living lect, at its death or split for a dead one): {"now": "kept" | "replaced" | "lost", "by": {kyr,
    process, lect} of the first word-formation step after the hop (replaced), or None}."""
    l = h.lects.get(hop["lect"])
    w = l.lexicon.words.get(concept) if l is not None else None
    if w is None:
        return {"now": "lost", "by": None}
    proc = f"borrow:{hop['from_lect']}"
    k = round(float(hop["kyr"]), 3)
    for i, st in enumerate(w.etym):
        if st.lect == hop["lect"] and st.process == proc and round(float(st.kyr), 3) == k:
            later = [x for x in w.etym[i + 1:] if x.process.split(":", 1)[0] in ROUTE_FORMATION]
            if not later:
                return {"now": "kept", "by": None}
            x = later[0]
            return {"now": "replaced", "by": {"kyr": round(float(x.kyr), 3), "process": x.process, "lect": x.lect}}
    x = next((x for x in reversed(w.etym) if x.process.split(":", 1)[0] in ROUTE_FORMATION), None)
    return {"now": "replaced", "by": {"kyr": round(float(x.kyr), 3), "process": x.process, "lect": x.lect} if x is not None else None}


_H: History | None = None
CORE = sorted(LX.CORE100)  # (the core-100 concepts, in a fixed order: snapshots store their forms as a list in this order)
_IPA: dict = {}


def _ipa(form) -> str:
    v = _IPA.get(form)
    if v is None:
        if len(_IPA) > 500_000:
            _IPA.clear()
        from .percepts import word_ipa
        v = _IPA[form] = word_ipa(form)
    return v


def snapshot(l: LC.Lect) -> dict:
    """A lect at one frame, compact: inventory (c, v), the core-100 forms in CORE order (None where it has no word), the
    typology summary, live grams [function, ipa, level], the complexity score and the deme's shares."""
    from .percepts import to_ipa
    inv = l.inventory
    out = {"c": [to_ipa(x) for x in inv.consonants] if inv is not None else [],
           "v": [to_ipa(x) for x in inv.vowels] if inv is not None else []}
    al = getattr(inv, "allophones", None) if inv is not None else None
    if al:  # allophones beside the phonemes: [[allophone, phoneme (None: an inserted ʔ), test]]
        out["al"] = sorted([to_ipa(x), to_ipa(p) if p is not None else None, t] for x, (p, t) in al.items())
    core = []
    for c in CORE:
        w = l.lexicon.get(c)
        core.append(_ipa(w.form) if w is not None else None)
    out["core"] = core
    g = l.grammar
    out["typ"] = typology_summary(g)
    if g is not None:
        from . import grammar as GR
        out["grams"] = [[gr.function, _ipa(tuple(gr.form)), gr.level] for gr in g.grams if gr.live]
        out["cx"] = GR.complexity(g)["score"]
    else:
        out["grams"], out["cx"] = [], None
    out["shares"] = {k: round(v, 3) for k, v in l.shares.items() if v > 0.005}
    return out


def snapshot_delta(prev: dict, cur: dict) -> dict:
    """A later snapshot as changes from the one before: {"d": 1, "core": {index: ipa | None} (changed entries only), and the
    keys c, v, typ, grams, cx, shares only when they changed}. The first snapshot of a lect is full (no "d")."""
    out = {"d": 1, "core": {str(j): b for j, (a, b) in enumerate(zip(prev["core"], cur["core"])) if a != b}}
    if "core_roman" in cur:
        pr = prev.get("core_roman") or [None] * len(cur["core_roman"])
        out["core_roman"] = {str(j): b for j, (a, b) in enumerate(zip(pr, cur["core_roman"])) if a != b}
    for k in ("c", "v", "al", "typ", "grams", "cx", "shares"):
        if cur.get(k) != prev.get(k):
            out[k] = cur.get(k)
    return out


def snapshot_full(snaps: list, upto: int | None = None) -> list:
    """Undo the delta encoding: every snapshot of a lect as a full dict (readers and tests)."""
    out, cur = [], None
    for kyr, sn in snaps[: None if upto is None else upto + 1]:
        if not sn.get("d"):
            cur = {k: (list(v) if isinstance(v, list) else v) for k, v in sn.items()}
        else:
            cur = dict(cur)
            for key in ("core", "core_roman"):
                if key in sn and key in cur:
                    cur[key] = list(cur[key])
                    for j, x in sn[key].items():
                        cur[key][int(j)] = x
            for k, v in sn.items():
                if k not in ("d", "core", "core_roman"):
                    cur[k] = v
        out.append([kyr, cur])
    return out


def typology_summary(g) -> dict:
    """{order, adp, case, number, gender (typology values), n_case, n_number, n_class (live grams in those slots)}."""
    if g is None:
        return {}
    from . import grammar as GR
    t = g.typology
    n = {"case": 0, "number": 0, "class": 0}
    for gr in g.grams:
        if not gr.live:
            continue
        try:
            slot = GR.func_info(gr.function).slot
        except KeyError:
            continue
        if slot in n:
            n[slot] += 1
    return {"order": t.get("word_order"), "adp": t.get("adposition"), "case": t.get("case"), "number": t.get("number"),
            "gender": t.get("gender"), "n_case": n["case"], "n_number": n["number"], "n_class": n["class"]}


def adopt(l: LC.Lect, offers: list) -> int:
    """Apply the rules offered by contacts, in order, where they apply to the lect's sounds and the lect's re-fire memory
    allows them (an epenthesis inserts the receiver's own epenthetic vowel, a reduction reduces to its own central vowel)."""
    n = 0
    for r, origin, kyr in offers:
        r = LC.reduction_variant(LC.epenthesis_variant(r, l.inventory), l.inventory)
        if not l.may_fire(r, kyr) or not RU.applies(r, l.segments()):
            continue
        if l.apply_rule(r, kyr, origin=origin) > 0:
            n += 1
    return n


def _work(task):
    lid, i, n, t1, ctx, offers = task
    h = _H
    l = h.lects[lid]
    adopt(l, offers)
    ctx = dict(ctx)
    ctx["contact_words"] = {c: h._snap[c] for c in ctx.pop("contact_ids") if c in h._snap}
    fired = l.step(rng_for(h.seed, "step", lid, i), n, t1, ctx)
    l.sync()
    return lid, fired


def _work_remote(task):
    lid, fired = _work(task)
    l = _H.lects[lid]
    l.profile = None  # (restored from the parent's cache; profiles are shared)
    l._rw = None  # (the weighted catalogue cache holds closures; rebuilt on demand)
    return lid, (l, fired)


def LC_root(h: History, l: LC.Lect) -> str:
    cur = l
    while cur.parent is not None and cur.parent in h.lects:
        cur = h.lects[cur.parent]
    return cur.id


def niche_for(R: I.Run, deme: int, i: int) -> dict:
    """inputs.niche_weights mapped onto lexicon.ELABORATIONS niches (herder, coast, farmer, hunter), scaled so the leading
    niche can pass lexicon.ELAB_THRESHOLD."""
    w = R.niche_weights(deme, i)
    m = {"herder": w["herd"], "coast": w["fish"], "farmer": w["crop"], "hunter": w["hunt"]}
    top = max(m.values()) or 1.0
    return {k: round(v / top, 3) for k, v in m.items()}


def proto_grammar(GR, rng, lex, inv, prof, kyr, lid):
    return GR.proto_grammar(rng, inv, lex, kyr=kyr)


def head_first_of(GR, gram):
    """Compound order follows the typology's head direction (head-final -> modifier first)."""
    try:
        return not bool(gram.typology.head_final)
    except Exception:
        return None


def calque(rng, old: LC.Lect, new: LC.Lect) -> list:
    """One or two typology features of the old grammar carried into the new lect (calqued grammar)."""
    ot = getattr(old.grammar, "typology", None)
    nt = getattr(new.grammar, "typology", None)
    if not isinstance(ot, dict) or not isinstance(nt, dict):
        return []
    diff = sorted(k for k in ot if k in nt and ot[k] != nt[k])
    if not diff:
        return []
    k = int(rng.integers(1, CALQUE_MAX + 1))
    pick = [diff[j] for j in sorted(rng.choice(len(diff), size=min(k, len(diff)), replace=False).tolist())]
    out = []
    for f in pick:
        out.append({"feature": f, "from": nt[f], "to": ot[f]})
        nt[f] = ot[f]
    return out


def generate(run_dir, seed: int | None = None, run: I.Run | None = None, analyse: bool = True, frames: int | None = None) -> dict:
    """The whole pass: {"history": History, "lects", "shifts", "food_routes", "families", "checks", "log", "timing"}."""
    from . import checks as CK
    from . import families as FA
    t = time.perf_counter()
    R = run or I.Run(Path(run_dir))
    h = History(R, seed)
    h.start()
    h.observe(0)
    for i in range(1, len(R.frames_kyr) if frames is None else frames):
        h.interval(i)
    # (adoptions decided in the last interval would land in the next one, which does not exist: they are dropped)
    h.timing["driver_s"] = round(time.perf_counter() - t, 1)
    for l in h.lects.values():
        if l.alive and l.deme is not None:
            l.population = R.deme_population(l.deme, len(R.frames_kyr) - 1)
    out = {"history": h, "run": R, "seed": h.seed, "lects": list(h.lects.values()), "shifts": h.shifts,
           "food_routes": [r for r in h.routes.values()], "log": h.log, "timing": h.timing}
    if analyse:
        t2 = time.perf_counter()
        core = sorted(c for c in LX.CORE100)
        out["families"] = FA.analyse(out["lects"], core, h.seed, people_sets=CK.HORIZON_PEOPLES)
        h.timing["families_s"] = round(time.perf_counter() - t2, 1)
        living = [l for l in out["lects"] if l.alive and l.deme is not None]
        now = {(a, b): v for a, b, v in h.intel_now}
        last = len(R.frames_kyr) - 1
        out["continua"] = FA.continua(living, now, lambda a, b: R.contact(h.lects[a].deme, h.lects[b].deme, last) > 0,
                                      lambda l: l.family_true)
        out["checks"] = CK.run_all(out)
    h.timing["total_s"] = round(time.perf_counter() - t, 1)
    return out
