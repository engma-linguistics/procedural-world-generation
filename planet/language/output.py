"""languages.json (PW-986, architecture section 11) and the placeholder export for the writing repo.

`document(result)` turns history.generate's result into the json document: every lect (full lexicon for living lects, the
Swadesh-100 and names for dead ones), the shifts, the food-word routes, the families (true tree, scholars' tree, languages,
horizon), the checks, the landscape a names pass needs (rivers and lakes with the demes that lived on them, oldest first), a
plain-words log, and the voice profiles. Romanized forms come from romanize.py with each lect's own contrasts. `names` is left
for names.py (builder F) to fill."""
from __future__ import annotations

import numpy as np

from . import inventory as INV
from . import lexicon as LX
from . import romanize as RO
from . import inputs as I
from . import names as NM
from .percepts import from_ipa, word_ipa
from . import phonology as PH

FORMAT = "procgen-languages/1"


class Speller:
    """Romanization with one lect's contrasts and inventory."""

    def __init__(self, lect):
        self.orth = orthography(lect)
        self.inv = self.orth.inv
        self.cs = self.orth.cs

    failures: dict = {}  # (romanizer errors, by segment IPA: the word falls back to its IPA rather than stopping the pass)

    def form(self, form) -> str:
        try:
            return self.orth.word(form)
        except Exception as e:
            from .percepts import to_ipa
            key = f"{type(e).__name__}: {' '.join(to_ipa(s) for s in form)}"
            Speller.failures[key] = Speller.failures.get(key, 0) + 1
            return "".join(to_ipa(s) for s in form)

    def ipa(self, ipa: str) -> str:
        try:
            return self.orth.word(from_ipa(ipa))
        except Exception:
            return ipa


def orthography(lect) -> RO.Orthography:
    """A lect's spelling (romanize.Orthography): its surface segments, its allophones spelled as their phonemes, its book
    diacritics ranked by token counts in its lexicon. Cached on the lect until its forms change (lect.segments' cache)."""
    segs = lect.segments() if getattr(lect, "lexicon", None) is not None else []
    o = getattr(lect, "_orth", None)
    if o is not None and o[0] is getattr(lect, "_segs", None) and o[0] is not None:
        return o[1]
    counts: dict = {}
    if getattr(lect, "lexicon", None) is not None:
        for w in lect.lexicon.words.values():
            for s in w.form:
                counts[s] = counts.get(s, 0) + 1
    inv = getattr(lect, "inventory", None)
    orth = RO.Orthography(segs, getattr(inv, "allophones", None) or {}, counts, getattr(lect, "orth", None))
    try:
        lect._orth = (getattr(lect, "_segs", None), orth)
    except Exception:
        pass
    return orth


def _r(x, k=3):
    return None if x is None else round(float(x), k)


class EtymTable:
    """Etymologies stored once: a word's chain is a node id; node = [parent node | -1, kyr, lect, process, ipa, gloss(, note)],
    where gloss 0 means "the same as the parent node's".
    Within one lect, a run of successive sound changes is merged into one step ("sound_change:a+b+…n", the last form), and
    sister lects share the nodes of their common past."""

    MAX_IDS = 2

    def __init__(self):
        self.nodes: list = []
        self._key: dict = {}
        self._by_obj: dict = {}
        self._gloss: list = []
        self.roots: dict = {}   # root id -> {"node", "lect", "kyr", "concept", "gloss", "ipa", "pos"} (lexicon.Word.roots)

    def note_roots(self, w) -> None:
        """Record the words' roots: the main root's entry is the step of the word's chain the root starts at
        (`lexicon.root_step`: the root word as the proto or a coining lect made it, or the shift, loan or old derivation
        a speaker no longer analyses; "node" is that step's node id, shared by every word of the family); a compound's
        modifier root gets an entry from the first word met that has it as its main root (else concept and lect only)."""
        for roots in (w.roots, w.etym_roots):   # (felt roots, then the historian's: one table for both)
            self._note(w, roots)

    def _note(self, w, roots) -> None:
        for i, r in enumerate(roots):
            e = self.roots.get(r)
            if e is not None and (i or e.get("node") is not None):
                continue
            lect, _, rest = r.partition(":")
            concept = rest.split("@", 1)[0]
            if i == 0 and w.etym:
                st = LX.root_step(w, r)   # (the step the root starts at: a proto root, a coinage, a shift, a loan ...)
                j = next((k for k, x in enumerate(w.etym) if x is st), 0)
                self.roots[r] = {"node": self.chain(w.etym[:j + 1], cache=False), "lect": st.lect, "kyr": _r(st.kyr), "concept": concept,
                                 "gloss": LX.concept_info(concept).gloss, "ipa": st.form, "pos": LX.concept_info(concept).pos}
            elif e is None:
                self.roots[r] = {"node": None, "lect": lect, "kyr": None, "concept": concept,
                                 "gloss": LX.concept_info(concept).gloss, "ipa": None, "pos": LX.concept_info(concept).pos}

    def _merge(self, etym) -> list:
        out = []
        for st in etym:
            if out and st.process.startswith("sound_change:") and out[-1][3].startswith("sound_change:") and out[-1][2] == st.lect:
                ids = out[-1][3][len("sound_change:"):].split("+") + st.process[len("sound_change:"):].split("+")
                out[-1] = [out[-1][0], _r(st.kyr), st.lect, "sound_change:" + _join_ids(ids, self.MAX_IDS), st.form, st.gloss, st.note]
            else:
                out.append([None, _r(st.kyr), st.lect, st.process, st.form, st.gloss, st.note])
        return out

    def chain(self, etym, cache: bool = True) -> int:
        """The node id of the chain's last step (adding the nodes it lacks); `cache=False` for a one-off prefix (a root's
        step: its nodes are the word's own, so nothing new is added)."""
        k = id(etym)
        hit = self._by_obj.get(k)
        if hit is not None and hit[0] is etym:
            return hit[1]
        parent = -1
        for st in self._merge(etym):
            st[0] = parent
            key = tuple(st)
            nid = self._key.get(key)
            if nid is None:
                nid = self._key[key] = len(self.nodes)
                row = list(st if st[6] else st[:6])
                if parent >= 0 and self._gloss[parent] == st[5]:
                    row[5] = 0
                self._gloss.append(st[5])
                self.nodes.append(row)
            parent = nid
        if cache:
            self._by_obj[k] = (etym, parent)
        return parent


def _join_ids(ids: list, cap: int) -> str:
    flat, more = [], 0
    for x in ids:
        if x.startswith("…"):
            more += int(x[1:] or 1)
        else:
            flat.append(x)
    if len(flat) > cap:
        more += len(flat) - cap
        flat = flat[:cap]
    return "+".join(flat) + (f"+…{more}" if more else "")


def _walk(nodes: list, node) -> list:
    out = []
    while node is not None and node >= 0:
        n = nodes[node]
        out.append(list(n[1:]))
        node = n[0]
    out.reverse()
    for k in range(1, len(out)):
        if out[k][4] == 0:
            out[k][4] = out[k - 1][4]
    return out


def etym_list(table: EtymTable, node: int) -> list:
    """A node's chain, oldest first, as [kyr, lect, process, ipa, gloss(, note)] steps (for readers of the json)."""
    return _walk(table.nodes, node)


def lexicon_json(lect, sp: Speller, full: bool, et: EtymTable) -> dict:
    out = {}
    for k, w in sorted(lect.lexicon.words.items()):
        if not full and k not in LX.CORE100 and w.pos != "NAME":
            continue
        out[k] = {"ipa": w.ipa, "roman": sp.form(w.form), "pos": w.pos, "freq": w.freq_class, "etym": et.chain(w.etym),
                  "roots": list(w.roots), "etym_roots": list(LX.etym_roots(w))}
        et.note_roots(w)
    return out


def grammar_json(lect, sp: Speller) -> dict:
    from . import grammar as GR
    g = lect.grammar
    if g is None:
        return {"typology": {}, "grams": [], "paradigms": {}, "complexity": {}}
    grams = [{"function": gr.function, "form_ipa": GR.ipa(gr.form), "form_roman": sp.form(gr.form), "level": gr.level,
              "level_name": GR.LEVELS[gr.level], "side": gr.side, "host": gr.host, "source": list(gr.source),
              "born_kyr": _r(gr.born_kyr), **({"alt_ipa": GR.ipa(gr.alt)} if gr.alt else {})} for gr in g.grams if gr.live]
    pt = GR.paradigm_table(g)
    for key in ("nouns", "verbs"):
        for row in (pt.get(key) or {}).get("rows", []):
            row["cells"] = {c: {"ipa": v, "roman": sp.ipa(v)} for c, v in row["cells"].items()}
    for p in pt.get("periphrastic", []):
        p["roman"] = sp.ipa(p["ipa"])
    cs = g.class_system
    classes = {"kind": cs.kind, "classes": [[c.k, c.group, f"CLASS:{c.k}"] for c in cs.classes]} if cs and cs.classes else None
    typ = {**g.typology, "case_count": GR.case_bin(g)}   # (the WALS 49A bin beside the none/few/many label: PW-1569)
    return {"typology": typ, "grams": grams, "paradigms": pt, "complexity": GR.complexity(g), "classes": classes,
            "processes": dict(getattr(g, "processes", None) or {})}


def thin_snapshots(snaps: list, every: int) -> list:
    """Every `every`-th snapshot (and the last), with `core_roman` (the core forms in the house spelling under that frame's
    inventory) added, re-encoded as deltas."""
    if not snaps:
        return snaps
    from .history import snapshot_delta, snapshot_full
    full = snapshot_full(snaps)
    keep = full[::every] + ([full[-1]] if (len(full) - 1) % every else []) if every > 1 and len(full) > 2 else full
    prev_key, prev_core, prev_rom, cs, invs = None, None, None, None, None
    for _k, sn in keep:
        key = (tuple(sn.get("c") or ()), tuple(sn.get("v") or ()))
        if key != prev_key:
            invs = frozenset(x for c in key[0] + key[1] for x in from_ipa(c))
            cs = RO.contrasts_of(list(invs))
            prev_core = None
        rom = []
        for j, ipa in enumerate(sn["core"]):
            if prev_core is not None and prev_core[j] == ipa:
                rom.append(prev_rom[j])
            else:
                rom.append(_roman(ipa, cs, invs))
        sn["core_roman"] = rom
        prev_key, prev_core, prev_rom = key, sn["core"], rom
    out = [keep[0]]
    for (_k0, a), (k1, b) in zip(keep, keep[1:]):
        out.append([k1, snapshot_delta(a, b)])
    return out


def _roman(ipa, cs, invs):
    if ipa is None:
        return None
    try:
        return RO.romanize_word(from_ipa(ipa), cs, invs)
    except Exception:
        return ipa


def rules_table(lects, h) -> dict:
    """{rule id: plain words} for every rule id in the change logs (rules.describe), plus the made-up ones: dispersion
    pushes, koine replacements and inventory simplifications (their ids say what moved)."""
    from . import lect as LC, rules as RU
    used = {c["rule"] for l in lects for c in l.changes} | {k for l in lects for k in l.rule_text if k.startswith("tone.default/")}
    known: dict = {}
    for key in sorted({l.profile_key for l in lects}):
        prof = h.profile(key)
        try:
            for r in LC.catalogue_for(prof, key):
                if r.id in used and r.id not in known:
                    known[r.id] = RU.describe(r)
        except Exception:
            continue
    for l in lects:
        for k, v in l.rule_text.items():
            known.setdefault(k, v)
    out = {}
    for rid in sorted(used):
        if rid in known:
            out[rid] = known[rid]
        elif rid == "simplification":
            out[rid] = "rare sounds merged into their nearest neighbours, as listed in the change's 'merged' (dispersion: the inventory had grown past its cap)"
        elif rid == "koine.level":
            out[rid] = "a mixed city's minority speech levelled toward the city majority's lect of the same language: its sound changes taken up and core words borrowed (koine levelling)"
        elif rid == "koine":
            out[rid] = "sounds most of a mixed city's heads could not say replaced, as listed in the change's 'merged' (koine)"
        else:
            out[rid] = rid
    return out


def lect_json(lect, full: bool, et: EtymTable, snap_every: int = 1, phonology: dict | None = None,
              snapshots: list | None = None) -> dict:
    sp = Speller(lect)
    inv = lect.inventory
    gj = grammar_json(lect, sp)
    return {"id": lect.id, "deme": lect.deme, "people": lect.people, "parent": lect.parent, "how": lect.how,
            "substrate": lect.substrate, "born_kyr": _r(lect.born_kyr), "died_kyr": _r(lect.died_kyr), "end": lect.end,
            "minority": bool(getattr(lect, "minority", False)), "orth": list(getattr(lect, "orth", None) or ()),
            "rate": _r(lect.rate), "gen_yr": _r(lect.gen_yr, 1), "language": lect.language, "family_true": lect.family_true,
            "family_scholars": lect.family_scholars, "deme_name": lect.deme_name,
            "inventory": None if inv is None else {"consonants": INV.to_json(inv)["consonants"], "vowels": INV.to_json(inv)["vowels"],
                                                   "tones": list(inv.tones), "shapes": dict(inv.shapes), "stress": inv.stress,
                                                   "max_onset": inv.max_onset, "max_coda": inv.max_coda,
                                                   "allophones": INV.allophones_json(inv)},
            "typology": gj["typology"], "grams": gj["grams"], "paradigms": gj["paradigms"], "complexity": gj["complexity"],
            **({"classes": gj["classes"]} if gj.get("classes") else {}),
            **({"processes": gj["processes"]} if gj.get("processes") else {}),   # (split ergativity, reduplication)
            "lexicon": lexicon_json(lect, sp, full, et) if lect.lexicon is not None else {}, "lexicon_full": full,
            "affixes": {m: {"ipa": word_ipa(f), "suffix": s} for m, (f, s) in (lect.lexicon.affixes.items() if lect.lexicon is not None else [])},
            **({"systems": LX.systems_json(lect.lexicon)} if lect.lexicon is not None and lect.lexicon.systems else {}),
            "changes": [[c["kyr"], c["rule"], c["cause"], c["origin_lect"]] + ([{k: c[k] for k in ("city", "peoples", "merged") if k in c}] if "merged" in c else [])
                        for c in lect.changes],
            **({"signatures": [dict(x) for x in lect.signatures]} if getattr(lect, "signatures", None) else {}),
            **({"tendency": {k: round(v, 2) for k, v in sorted(lect.tendency.items())}}
               if getattr(lect, "tendency", None) else {}),   # (the line's family tendencies, log scale; PW-1642)
            "rules_applied": lect.rules_applied, "generations": _r(lect.generations, 1),
            "l2": _r(lect.l2), "population": _r(lect.population, 0), "isolation": _r(lect.isolation),
            "shares_history": lect.shares_history,
            "stats": _round_all(LX.stats(lect.lexicon)) if full and lect.lexicon is not None else None,
            **({"phonology": phonology if phonology is not None else PH.to_json(lect)} if full and lect.lexicon is not None
               else {}),   # (sound lane: live rules)
            "snapshots": thin_snapshots(lect.snapshots, snap_every) if snapshots is None else snapshots}


def split_branches(lects_by_id: dict, mid: str, t: float, living: list) -> dict:
    """{living lect id: branch} for the living lects that came down from lect `mid` at or after its bud at `t` kyr ago: the
    branch is the child that budded off at `t` (its id), or "line" for `mid` itself and the buds it made later. Lects of
    `mid`'s earlier buds are left out (their common ancestor with the rest is older than the split)."""
    out = {}
    for lid in living:
        x, prev, seen = lects_by_id.get(lid), None, set()
        while x is not None and x["id"] != mid and x["id"] not in seen:
            seen.add(x["id"])
            prev = x
            x = lects_by_id.get(x.get("parent"))
        if x is None or x["id"] != mid:
            continue
        if prev is None:
            out[lid] = "line"
        elif abs(float(prev["born_kyr"]) - t) < 1e-6:
            out[lid] = prev["id"]
        elif float(prev["born_kyr"]) < t:
            out[lid] = "line"
    return out


def splits_json(h, lects: list, living_ids: set, et: "EtymTable") -> list:
    """PW-1592: the lects kept as they stood at their first bud in history.SPLIT_KYR (`History.splits`), as lect json with
    `split_of` (the lect), `split_kyr` and `branches` ({living descendant: branch}), for the fable's ancestor; only those
    with living descendants on two or more branches (a real split of living lines)."""
    by = {l.id: {"id": l.id, "parent": l.parent, "born_kyr": l.born_kyr} for l in lects}
    living = sorted(living_ids)
    out = []
    for mid, (t, cp) in sorted(getattr(h, "splits", {}).items()):
        br = split_branches(by, mid, t, living)
        if len(set(br.values())) < 2:
            continue
        m = h.lects.get(mid)
        x = lect_json(cp, full=False, et=et)   # (the core lexicon, as a dead lect keeps: enough for the fable)
        x.update({"id": f"{mid}@{t:g}", "split_of": mid, "split_kyr": _r(t), "parent": m.parent if m else cp.parent,
                  "how": m.how if m else cp.how, "born_kyr": _r(m.born_kyr if m else cp.born_kyr), "died_kyr": _r(t),
                  "end": "split", "branches": br, "snapshots": []})
        out.append(x)
    return out


def thin_dead(doc: dict, result: dict, every: int) -> None:
    """Keep every `every`-th snapshot (and the last) of the dead lects in a built doc (document(thin_dead=every) without
    building the doc again)."""
    living = {l.id for l in result["lects"] if l.alive and l.deme is not None}
    by = {l.id: l for l in result["lects"]}
    for x in doc["lects"]:
        if x["id"] not in living and x["id"] in by:
            x["snapshots"] = thin_snapshots(by[x["id"]].snapshots, every)


def home_feature(ls: dict) -> str | None:
    """The landscape concept a deme lives by, for the per-lect sentence (sentences.s_own): mountains where a third of its
    cells stand above 2000 m, the sea where a third are coast, else its largest river, else its lake; None otherwise."""
    if (ls.get("mountain_share") or 0) >= 1 / 3:
        return "MOUNTAIN"
    if (ls.get("coast_share") or 0) >= 1 / 3:
        return "SEA"
    if ls.get("river") is not None:
        return "RIVER"
    if ls.get("lake") is not None:
        return "LAKE"
    return None


def landscape_json(R) -> dict:
    """Rivers and lakes (fixed: the world's present ones) with the demes that lived on them, oldest first, for river and place
    names (the conservative layer), and each deme's landscape at its first frame in the window."""
    rivers = R.rivers()
    lakes = R.lakes()
    rid, lid = R.river_id(), R.lake_id()
    on_r: dict = {}
    on_l: dict = {}
    first: dict = {}
    for i in range(len(R.frames_kyr)):
        fr = R.frame(i)
        for d, cells in fr.cells.items():
            if not R.alive_at(d, R.kyr(i)):
                continue
            first.setdefault(d, i)
            for r in np.unique(rid[cells]).tolist():
                if r >= 0:
                    on_r.setdefault(int(r), {}).setdefault(d, R.kyr(i))
            for k in np.unique(lid[cells]).tolist():
                if k >= 0:
                    on_l.setdefault(int(k), {}).setdefault(d, R.kyr(i))
    lat, lon = R.g.lat, R.g.lon
    rv = {}
    for r, v in sorted(rivers.items(), key=lambda t: -t[1]["flow"]):
        m = v["mouth_cell"]
        rv[str(r)] = {**v, "lat": round(float(lat[m]), 2), "lon": round(float(lon[m]), 2),
                      "demes": [[d, k] for d, k in sorted(on_r.get(r, {}).items(), key=lambda t: (-t[1], t[0]))]}
    lk = {str(k): {**v, "lat": round(float(lat[k]), 2), "lon": round(float(lon[k]), 2),
                   "demes": [[d, t] for d, t in sorted(on_l.get(k, {}).items(), key=lambda x: (-x[1], x[0]))]}
          for k, v in lakes.items()}
    dm = {}
    for d, i in sorted(first.items()):
        ls = R.deme_landscape(d, i)
        dm[str(d)] = {"kyr": R.kyr(i), **{k: (round(v, 3) if isinstance(v, float) else v) for k, v in ls.items()}}
    return {"rivers": rv, "lakes": lk, "demes": dm, "river_flow_floor": I.RIVER_FLOW}


def document(result: dict, thin_dead: int = 1) -> dict:
    from . import faiths as FT
    from . import history as HI
    Speller.failures.clear()
    R = result["run"]
    h = result["history"]
    lects = result["lects"]
    fam = dict(result.get("families") or {})
    fam.pop("_matrices", None)
    routes = []
    for r in result["food_routes"]:
        rr = dict(r)
        o = h.lects.get(r["origin_lect"])
        rr["roman"] = Speller(o).ipa(r["ipa"]) if o is not None else r["ipa"]
        hops = []
        for hp in r["hops"]:
            l = h.lects.get(hp["lect"])
            hops.append({**hp, "roman": Speller(l).ipa(hp["ipa"]) if l is not None else hp["ipa"],
                         **HI.hop_status(h, hp, r["concept"])})
        rr["hops"] = sorted(hops, key=lambda x: (-x["kyr"], x["deme"]))
        routes.append(rr)
    routes.sort(key=lambda r: (r["concept"], -(r["kyr"] or 0.0), r["origin_lect"]))
    peoples = sorted({l.people for l in lects})
    profiles = {}
    for p in peoples:
        pr = h.profile(p)
        if pr is not None:
            try:
                profiles[p] = pr.to_json()
            except Exception:
                profiles[p] = {"source": getattr(pr, "source", None)}
    no_demes = sorted(l["id"] for l in R.meta["lineages"] if (l.get("overlay") or l.get("origin") in ("hybrid", "template"))
                      and not l.get("group_of"))
    land = landscape_json(R)
    et = EtymTable()
    living_ids = {l.id for l in lects if l.alive and l.deme is not None}
    order = sorted(lects, key=_lect_order)

    def pre(l):   # (the parts of lect_json that read one lect and change nothing: in parallel, PW-1555)
        ph = PH.to_json(l) if l.id in living_ids and l.lexicon is not None else None
        return ph, thin_snapshots(l.snapshots, 1 if l.id in living_ids else thin_dead)
    pr = dict(zip((l.id for l in order), HI.fork_map(pre, order))) if HI.WORKERS > 1 else {}
    lj = [lect_json(l, full=l.id in living_ids, et=et, snap_every=1 if l.id in living_ids else thin_dead,
                    phonology=pr[l.id][0] if pr else None, snapshots=pr[l.id][1] if pr else None)
          for l in order]
    from . import sentences as SN
    last = len(R.frames_kyr) - 1
    for x in lj:   # (round 5: grammar notes and glossed sample sentences for the living lects)
        if x["id"] in living_ids:
            hf = home_feature(R.deme_landscape(x["deme"], last)) if x.get("deme") is not None else None
            if hf:
                x["home"] = hf   # (the landscape the per-lect sentence names: sentences.s_own)
            SN.enrich(x)
    intel = intelligibility_json(R, h)
    splits = splits_json(h, lects, living_ids, et)
    doc = {
        "format": FORMAT, "run": R.id, "seed": result["seed"], "start_kyr": R.frames_kyr[0], "frames_kyr": R.frames_kyr,
        "romanization": RO.ROMANIZATION,
        "profiles": profiles,
        "snapshot_concepts": list(_core_order()),
        "etym_nodes": et.nodes,
        "roots": et.roots,
        "rules": rules_table(lects, h),
        "lects": lj,
        "names": NM.build_names(result, R, landscape=land),
        "shifts": result["shifts"],
        "food_routes": routes,
        "faiths": FT.faiths_json(result),   # (god names, liturgies: faiths.py, 2026-11-08)
        "families": fam,
        "intelligibility": intel,
        "continua": result.get("continua") or [],
        "fable_splits": splits,
        "checks": result.get("checks") or [],
        "landscape": land,
        "peoples_without_lects": {"ids": no_demes, "why": "hybrids, templates and overlays have no demes in the run, so no lects yet"},
        "log": result["log"],
        "romanization_failures": dict(Speller.failures),
        "timing": result.get("timing"),
        "constants": {**constants(), "generation_overrides": dict(getattr(R, "generation_overrides", {}) or {})},
    }
    return doc


def _core_order():
    from .history import CORE
    return CORE


def intelligibility_json(R, h) -> dict:
    """{"frames": [kyr...], "pairs": [[a, b, [v | null per frame]]], "now": [[a, b, v]] (living, v >= 0.05)}."""
    nf = len(R.frames_kyr)
    pairs = []
    for (a, b), d in sorted(h.intel.items()):
        pairs.append([a, b, [d.get(i) for i in range(nf)]])
    return {"frames": R.frames_kyr, "pairs": pairs, "now": h.intel_now,
            "note": "families.intelligibility: blind cognate share on the core-100 x (1 - half the cognates' mean distance "
                    "over COGNATE_DIST) x (1 - grammar penalty: word order 0.15, adposition, case, number 0.05 each)"}


def _lect_order(l):
    return (0 if l.deme is None else 1, l.deme if l.deme is not None else -1, l.born_kyr * -1, l.id)


def constants() -> dict:
    from . import families as FA, history as HI, lect as LC
    return {"RATE_RULE": LC.RATE_RULE, "RATE_SCALE": HI.RATE_SCALE, "REPLACE_SCALE": HI.REPLACE_SCALE,
            "BASE_REPLACE": LX.BASE_REPLACE, "WAVE_K": HI.WAVE_K, "SHIFT_K": HI.SHIFT_K, "KIND_WEIGHT": HI.KIND_WEIGHT,
            "CONTACT_MIN": HI.CONTACT_MIN, "PROTO_LINK": HI.PROTO_LINK, "LANG_SHARE": FA.LANG_SHARE,
            "COGNATE_DIST": FA.COGNATE_DIST}


def summary(doc: dict, file: str = "languages.json", seconds: float | None = None) -> dict:
    """The meta.languages block."""
    lects = doc["lects"]
    living = [l for l in lects if l["died_kyr"] is None and l["deme"] is not None]
    fam = doc["families"]
    return {"file": file, "format": FORMAT, "seed": doc["seed"], "lects": len(lects), "living": len(living),
            "protos": sum(1 for l in lects if l["deme"] is None), "shifts": len(doc["shifts"]),
            "languages": len(fam.get("languages") or []), "families_true": fam.get("true_families"),
            "families_scholars": fam.get("scholars_families"), "horizon_kyr": fam.get("horizon_kyr"),
            "horizon_human_kyr": ((fam.get("horizon_by") or {}).get("human") or {}).get("horizon_kyr"),
            "food_routes": len(doc["food_routes"]),
            "checks": {c["name"]: c["pass"] for c in doc["checks"]}, "generated_in_s": seconds,
            "lexicon_stats": _stats_summary(living)}


def _stats_summary(living: list) -> dict:
    """Run-wide means of the living lects' lexicon.stats."""
    st = [l["stats"] for l in living if l.get("stats")]
    if not st:
        return {}
    return {k: round(float(np.mean([x[k] for x in st])), 3) for k in ("mean_segments", "max_segments", "mean_syllables", "homophone_share")
            if all(k in x for x in st)} | {"lects": len(st)}


def etym_steps(doc: dict, node: int) -> list:
    """A word's etymology from the document, oldest first: [kyr, lect, process, ipa, gloss(, note)] per step (gloss 0 in a
    node resolved to its parent's)."""
    return _walk(doc["etym_nodes"], node)


def export_writing(doc: dict) -> dict:
    """The placeholder hand-off to the writing repo: per living lect, each word's IPA, house spelling, gloss and morphemes
    (from its last word-formation step; boundaries inside the form are not tracked yet). Nothing about scripts."""
    out = {"format": "procgen-lexicon-export/0", "run": doc["run"], "lects": {}}
    for l in doc["lects"]:
        if l["died_kyr"] is not None or l["deme"] is None:
            continue
        words = []
        for c, w in l["lexicon"].items():
            steps = etym_steps(doc, w["etym"])
            form_step = next((s for s in reversed(steps) if s[2].split(":", 1)[0] in ("derive", "compound", "proto", "coin", "shift",
                                                                                            "taboo", "elaborate")), None)
            parts = [c]
            if form_step and form_step[2].startswith("compound:"):
                parts = form_step[2].split(":", 1)[1].split("+")
            elif form_step and form_step[2].startswith("derive:"):
                parts = [steps[0][4], form_step[2].split(":", 1)[1]]
            words.append({"concept": c, "ipa": w["ipa"], "roman": w["roman"], "pos": w["pos"], "morphemes": parts})
        out["lects"][l["id"]] = {"people": l["people"], "language": l["language"], "words": words}
    return out


def _round_all(x, k: int = 3):
    if isinstance(x, float):
        return round(x, k)
    if isinstance(x, dict):
        return {a: _round_all(b, k) for a, b in x.items()}
    if isinstance(x, list):
        return [_round_all(b, k) for b in x]
    return x


# ---- the stored format: procgen-languages/2 (architecture section 11) ------------------------------------------------------
# `document` builds the doc in memory in the shape every reader uses (format /1's shape). On disk it is packed into three
# files: the main file (lects with their words, names, families, checks, ...; each lexicon as columns over a doc-level
# concept table), `<stem>-etym.json` (the etymology nodes, the roots table and each lexicon's etym / roots / etym_roots
# columns) and `<stem>-snapshots.json` (each lect's snapshots). `pack` and `expand` are exact inverses
# (expand(*pack(doc)) == doc apart from "format"); viewer/langcore.js `expand` is the same expander for the browser.
# Sparse columns are {"i": [index gaps], "v": [values]} (sp / unsp).

FORMAT2 = "procgen-languages/2"
SIDECARS = {"etym": "-etym", "snapshots": "-snapshots"}


def sidecar_paths(path) -> dict:
    """{"etym": path, "snapshots": path} beside a main file (languages.json -> languages-etym.json, ...)."""
    from pathlib import Path
    p = Path(path)
    return {k: p.with_name(p.stem + suf + p.suffix) for k, suf in SIDECARS.items()}


class _Intern:
    def __init__(self, items=()):
        self.list: list = []
        self.ix: dict = {}
        for x in items:
            self(x)

    def __call__(self, x) -> int:
        i = self.ix.get(x)
        if i is None:
            i = self.ix[x] = len(self.list)
            self.list.append(x)
        return i


def sp(pairs) -> dict:
    """[(index, value)] in rising index order as {"i": [gaps from the previous index], "v": [values]}."""
    out, last = {"i": [], "v": []}, 0
    for i, v in pairs:
        out["i"].append(i - last)
        out["v"].append(v)
        last = i
    return out


def unsp(s: dict | None) -> dict:
    out, at = {}, 0
    for g, v in zip((s or {}).get("i") or (), (s or {}).get("v") or ()):
        at += g
        out[at] = v
    return out


def _split_root(rid: str):
    lect, sep, rest = rid.partition(":")
    if not sep:
        return None
    concept, at, kyr = rest.rpartition("@")
    return (lect, concept, kyr) if at else (lect, rest, None)


_LEX_MAIN = ("ipa", "roman", "pos", "freq")
_LEX_ETYM = ("etym", "roots", "etym_roots")


def pack(doc: dict) -> tuple[dict, dict]:
    """The in-memory doc as (main, {"etym": ..., "snapshots": ...}) in format procgen-languages/2."""
    lects = doc.get("lects") or []
    roots = doc.get("roots") or {}
    lect_t = _Intern(l["id"] for l in lects)
    # concepts: gloss and pos from the roots table (first root of the concept, in id order), else pos from the lexicons
    cinfo: dict = {}
    for rid in sorted(roots):
        e = roots[rid]
        c = e.get("concept")
        if c is not None and c not in cinfo:
            cinfo[c] = [e.get("gloss"), e.get("pos")]
    for l in lects:
        for c, w in (l.get("lexicon") or {}).items():
            if c not in cinfo:
                cinfo[c] = [None, w.get("pos")]
    concept_t = _Intern(sorted(cinfo))
    # root ids: every id in the roots table or any lexicon, as (lect, concept, kyr text) columns; odd ids kept whole
    ids = set(roots)
    for l in lects:
        for w in (l.get("lexicon") or {}).values():
            ids.update(w.get("roots") or ())
            ids.update(w.get("etym_roots") or ())
    root_ids = sorted(ids)
    rix = {r: i for i, r in enumerate(root_ids)}
    rl, rc, rk, odd = [], [], [], []
    for i, r in enumerate(root_ids):
        s = _split_root(r)
        if s is None or s[1] not in concept_t.ix:
            odd.append((i, r))
            rl.append(-1), rc.append(-1), rk.append(None)
            continue
        rl.append(lect_t(s[0])), rc.append(concept_t.ix[s[1]]), rk.append(s[2])
    main = {k: v for k, v in doc.items() if k not in ("etym_nodes", "roots", "lects")}
    main["format"] = FORMAT2
    main["sidecars"] = dict(SIDECARS)
    out_lects, snaps, lex_et = [], {}, {}
    for l in lects:
        x = {k: v for k, v in l.items() if k not in ("lexicon", "snapshots")}
        lex = l.get("lexicon")
        if lex is not None:
            col = {"c": [], "ipa": [], "roman": [], "freq": []}
            pos, extra = [], []
            ec = {"etym": [], "roots": []}
            er, no_et = [], []
            for j, (c, w) in enumerate(lex.items()):
                col["c"].append(concept_t.ix[c])
                col["ipa"].append(w.get("ipa"))
                col["roman"].append(w.get("roman"))
                col["freq"].append(w.get("freq"))
                if w.get("pos") != cinfo[c][1]:
                    pos.append((j, w.get("pos")))
                ec["etym"].append(w.get("etym"))
                ec["roots"].append([rix[r] for r in w.get("roots") or ()])
                if "etym_roots" not in w:
                    no_et.append(j)
                elif list(w["etym_roots"]) != list(w.get("roots") or ()):
                    er.append((j, [rix[r] for r in w["etym_roots"]]))
                more = {k: v for k, v in w.items() if k not in _LEX_MAIN + _LEX_ETYM}
                if more:
                    extra.append((j, more))
            col["pos"] = sp(pos)
            if extra:
                col["x"] = sp(extra)
            ec["er"] = sp(er)
            if no_et:
                ec["no_er"] = no_et
            x["lexicon"] = col
            lex_et[l["id"]] = ec
        if "snapshots" in l:
            snaps[l["id"]] = l["snapshots"]
        out_lects.append(x)
    main["lects"] = out_lects
    main["concepts"] = [[c, *cinfo[c]] for c in concept_t.list]
    # etymology nodes as columns: parent as a backward gap (0: none), lect, process and note interned, ipa 0 = the parent's
    nodes = doc.get("etym_nodes") or []
    word_ipa = _word_ipa_of_nodes(lects)
    proc_t, note_t = _Intern(), _Intern()
    nc = {"up": [], "kyr": [], "lect": [], "process": [], "ipa": [], "gloss": []}
    notes = []
    for i, n in enumerate(nodes):
        nc["up"].append(0 if n[0] < 0 else i - n[0])
        nc["kyr"].append(n[1])
        nc["lect"].append(-1 if n[0] >= 0 and nodes[n[0]][2] == n[2] else lect_t(n[2]))
        nc["process"].append(proc_t(n[3]))
        nc["ipa"].append(0 if n[0] >= 0 and nodes[n[0]][4] == n[4] else 1 if word_ipa.get(i) == n[4] else n[4])
        nc["gloss"].append(n[5])
        if len(n) > 6:
            notes.append((i, note_t(n[6])))
    nc["note"] = sp(notes)
    rcols = {"node": [], "lect": [], "kyr": [], "ipa": []}
    absent, other = [], []
    for i, r in enumerate(root_ids):
        e = roots.get(r)
        if e is None:
            absent.append(i)
            rcols["node"].append(None), rcols["lect"].append(-1), rcols["kyr"].append(None), rcols["ipa"].append(None)
            continue
        rcols["node"].append(e.get("node"))
        rcols["lect"].append(-1 if rl[i] >= 0 and e.get("lect") == lect_t.list[rl[i]] else lect_t(e.get("lect")))
        nd = nodes[e["node"]] if isinstance(e.get("node"), int) and 0 <= e["node"] < len(nodes) else None
        rcols["kyr"].append(0 if nd is not None and e.get("kyr") == nd[1] and e.get("kyr") != 0 else e.get("kyr"))
        rcols["ipa"].append(0 if nd is not None and e.get("ipa") == nd[4] and e.get("ipa") != 0 else e.get("ipa"))
        c = e.get("concept")
        rest = {k: v for k, v in e.items() if k not in ("node", "lect", "kyr", "ipa")}
        if not (rc[i] >= 0 and c == concept_t.list[rc[i]] and rest == {"concept": c, "gloss": cinfo[c][0], "pos": cinfo[c][1]}):
            other.append((i, rest))
    rcols["absent"], rcols["other"] = absent, sp(other)
    main["lect_ids"] = lect_t.list   # (after the nodes and roots: they may name lects that left no record)
    etym = {"format": FORMAT2, "root_ids": {"lect": rl, "concept": rc, "kyr": rk, "odd": sp(odd)},
            "processes": proc_t.list, "notes": note_t.list, "nodes": nc, "roots": rcols, "lexicons": lex_et}
    return main, {"etym": etym, "snapshots": {"format": FORMAT2, "lects": snaps}}


def expand(main: dict, side: dict | None = None) -> dict:
    """The packed files back as the in-memory doc (format /1's shape). A sidecar left out leaves its part out
    (`etym_nodes`, `roots` and the words' etym / roots / etym_roots; the lects' `snapshots`). A /1 doc is returned as it is."""
    if main.get("format") != FORMAT2:
        return main
    side = side or {}
    lect_ids = main["lect_ids"]
    concepts = main["concepts"]
    et = side.get("etym")
    root_ids = None
    if et is not None:
        ri = et["root_ids"]
        odd = unsp(ri.get("odd"))
        root_ids = [odd[i] if i in odd else f"{lect_ids[a]}:{concepts[c][0]}" + ("" if k is None else f"@{k}")
                    for i, (a, c, k) in enumerate(zip(ri["lect"], ri["concept"], ri["kyr"]))]
    doc = {k: v for k, v in main.items() if k not in ("lects", "concepts", "lect_ids", "sidecars")}
    doc["format"] = FORMAT
    snaps = (side.get("snapshots") or {}).get("lects")
    lects = []
    for x in main["lects"]:
        l = dict(x)
        col = x.get("lexicon")
        if col is not None:
            pos, ex = unsp(col.get("pos")), unsp(col.get("x"))
            ec = (et["lexicons"].get(x["id"]) if et is not None else None)
            er = unsp(ec.get("er")) if ec else {}
            no_er = set(ec.get("no_er") or ()) if ec else set()
            lex = {}
            for j, ci in enumerate(col["c"]):
                w = {"ipa": col["ipa"][j], "roman": col["roman"][j], "pos": pos[j] if j in pos else concepts[ci][2],
                     "freq": col["freq"][j]}
                if ec:
                    rs = [root_ids[r] for r in ec["roots"][j]]
                    w["etym"], w["roots"] = ec["etym"][j], rs
                    if j in er:
                        w["etym_roots"] = [root_ids[r] for r in er[j]]
                    elif j not in no_er:
                        w["etym_roots"] = list(rs)
                if j in ex:
                    w.update(ex[j])
                lex[concepts[ci][0]] = w
            l["lexicon"] = lex
        if snaps is not None and x["id"] in snaps:
            l["snapshots"] = snaps[x["id"]]
        lects.append(l)
    doc["lects"] = lects
    if et is not None:
        nc, procs, notes = et["nodes"], et["processes"], et["notes"]
        note = unsp(nc.get("note"))
        word_ipa = _word_ipa_of_nodes(lects)
        nodes = []
        for i in range(len(nc["kyr"])):
            up = nc["up"][i]
            ipa = nc["ipa"][i]
            n = [i - up if up else -1, nc["kyr"][i], lect_ids[nc["lect"][i]] if nc["lect"][i] >= 0 else nodes[i - up][2],
                 procs[nc["process"][i]],
                 nodes[i - up][4] if ipa == 0 and up else word_ipa.get(i) if ipa == 1 else ipa, nc["gloss"][i]]
            if i in note:
                n.append(notes[note[i]])
            nodes.append(n)
        doc["etym_nodes"] = nodes
        rc, ri = et["roots"], et["root_ids"]
        absent = set(rc.get("absent") or ())
        other = unsp(rc.get("other"))
        roots = {}
        for i, r in enumerate(root_ids):
            if i in absent:
                continue
            lect = lect_ids[rc["lect"][i]] if rc["lect"][i] >= 0 else lect_ids[ri["lect"][i]]
            nd = rc["node"][i]
            kyr = nodes[nd][1] if rc["kyr"][i] == 0 and nd is not None else rc["kyr"][i]
            ipa = nodes[nd][4] if rc["ipa"][i] == 0 and nd is not None else rc["ipa"][i]
            if i in other:
                e = {"node": nd, "lect": lect, "kyr": kyr, **other[i], "ipa": ipa}
            else:
                cc = concepts[ri["concept"][i]]
                e = {"node": nd, "lect": lect, "kyr": kyr, "concept": cc[0], "gloss": cc[1], "ipa": ipa, "pos": cc[2]}
            roots[r] = e
        doc["roots"] = roots
    return doc


def _word_ipa_of_nodes(lects: list) -> dict:
    """{etym node: the ipa of the first word (lect order, then lexicon order) whose etymology ends there}: a node's form is
    stored as 1 when it is that word's (most chains end in a stored word)."""
    out: dict = {}
    for l in lects:
        for w in (l.get("lexicon") or {}).values():
            n = w.get("etym")
            if isinstance(n, int) and n not in out:
                out[n] = w.get("ipa")
    return out


def dumps(x) -> str:
    import json as _json
    return _json.dumps(x, separators=(",", ":"), ensure_ascii=False)


def save(doc: dict, path) -> dict:
    """Write the doc packed (the sidecars first, then the main file, each atomically); {file name: bytes}."""
    from pathlib import Path
    from .. import store as S
    main, side = pack(doc)
    path = Path(path)
    sizes = {}
    for k, p in sidecar_paths(path).items():
        S.write_atomic(p, dumps(side[k]))
        sizes[p.name] = p.stat().st_size
    S.write_atomic(path, dumps(main))
    sizes[path.name] = path.stat().st_size
    return sizes


def load(path, sidecars: bool | tuple = True) -> dict:
    """A languages.json (either format) as the in-memory doc; `sidecars` False reads the main file only, or a tuple names
    the sidecars to read ("etym", "snapshots"). A missing sidecar is skipped."""
    import json as _json
    from pathlib import Path
    path = Path(path)
    main = _json.loads(path.read_text(encoding="utf-8"))
    if main.get("format") != FORMAT2:
        return main
    want = tuple(SIDECARS) if sidecars is True else (sidecars or ())
    side = {}
    for k, p in sidecar_paths(path).items():
        if k in want and p.is_file():
            side[k] = _json.loads(p.read_text(encoding="utf-8"))
    return expand(main, side)
