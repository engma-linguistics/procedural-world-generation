"""The technology tree, a first pass (PW-675 prototype): which people knew what, and since when.

The tree is data (samples/techtree.toml): tracks, techs with prerequisites, land the tech needs (land.GOODS), a real-world
earliest date (sources in the file) and a rate. It is read after a peoples history has run, from what the history saved
(the lines with their start and end, the contact record, the first tamings of crops and animals, each people's present
range and the world's goods), so it can be built in output.save and again for a stored run (`planet techtree RUN`).

Rules, all seeded and simple:
- A people may invent a tech once it knows the tech's needs, its country holds (its present range; a deposit, ore or salt, in a few cells) the goods the tech needs, it has hands if the
  tech needs them, and the time is past the tech's earliest date (elder kinds, [[kind]] elder: the earlier elder date). The
  chance per kyr is the tech's rate x the kind's rate_x x a size factor (bigger peoples invent more often). So language
  arises in each stem on its own, at its own time; dragons, old by hundreds of kyr, get to it first.
- A split inherits what its parent knew at the split, a hybrid what both parents knew; a group (a way of life within a
  people) shares its people's knowledge as it goes; an arrival brings its kind's kit (gnomes from the feywild).
- Diffusion: while two peoples are in contact (contacts.Contacts: the first contact, the border length over time), each
  tech one knows and the other could use passes at contact_rate x spread x border/contact_full_km x openness per kyr
  (openness = 1 - 0.7 insularity): fast for traded things, slow for language.
- The crops and herd animals of the history count: a people that first cultivated a crop (crops.py) knows cultivation
  from then, one that tamed or took up an animal (animals.py) knows herding.
- Language never passes between stems before their minds (below), but once a people is genetically modern (below a stem with a
  sapiens node) it takes language from any neighbour that has it, at the contact rate (modern_contact, PW-971; owner: almost any
  contact spreads language). The other within-a-people techs (spread = 0) never pass by contact.
- The sapiens node gates (PW-971, PW-978): in a line under a stem with `sapient`, nothing arises or spreads before the node but the
  techs marked `bare = true` (knapping, handaxes: Lomekwi/Oldowan/Acheulean; found and hooked tools). Gesture and call systems, language and everything
  past them wait for the node. A kind's starting kit (the dragons' innate magic, with its gesture roots) is not gated: it is body.
- Each body plan its own bare tools (PW-987): a tech's `grip` says what holds its tool (hands, beak or any); a kind's `hands` is
  true, false (dragons) or "node" (hands only from its stem's sapiens node: cats, birds, saurians) and `beak` lets it hold one in its
  beak. So before their minds the hominids and goblinoids knap, the bird stems use found and hooked tools, the cats and saurians none.
- Nothing goes past the tree's era (meta.era), and the fantasy techs are left out in real mode.
A stem that ends as animals (spec.Lineage.animals_end, PW-965: the dragons' wyverns, drakes and pseudodragons) is untracked past its end, so
no animal line exists here to get language or techs.
Megafauna (dragons, giants) count as peoples here; templates (tieflings) do not: they are their hosts.
"""

from __future__ import annotations

import json
import math
import tomllib
import warnings
from pathlib import Path

import numpy as np

FILE = Path(__file__).parent / "samples" / "techtree.toml"
ERAS = ("stone age", "bronze age", "classical", "medieval", "renaissance", "industrial")
STEPS = 360  # time steps, log-spaced from the oldest line to the present
NEAR_KYR = 0.05  # the last step before the present
DEPOSITS = ("metal", "gold", "iron", "copper", "tin", "gems", "mithril", "coal", "salt", "salt_rock", "stone", "volcanic")


def load(path: Path | str | None = None) -> dict:
    raw = tomllib.loads(Path(path or FILE).read_text())
    techs = {t["id"]: t for t in raw["tech"]}
    for t in techs.values():
        for n in t.get("needs", []):
            if n not in techs:
                raise ValueError(f"tech {t['id']} needs unknown tech {n}")
        if t["track"] not in {k["id"] for k in raw["track"]}:
            raise ValueError(f"tech {t['id']}: unknown track {t['track']}")
        if t.get("era", "stone age") not in ERAS:
            raise ValueError(f"tech {t['id']}: unknown era {t.get('era')}")
        if t.get("grip", "hands") not in GRIPS:
            raise ValueError(f"tech {t['id']}: unknown grip {t.get('grip')}")
    for k in raw.get("kind", []):
        k["of"] = [k["of"]] if isinstance(k["of"], str) else list(k["of"])  # (one line id or several, PW-1041)
        if k.get("hands", True) not in (True, False, "node"):
            raise ValueError(f"kind {k['of']}: hands must be true, false or \"node\"")
    order, seen = [], set()

    def visit(i, path=()):
        if i in path:
            raise ValueError(f"tech cycle through {i}")
        if i in seen:
            return
        for n in techs[i].get("needs", []):
            visit(n, path + (i,))
        seen.add(i)
        order.append(i)
    for i in techs:
        visit(i)
    raw["order"] = order  # (prerequisites before the techs that need them)
    raw["techs"] = techs
    return raw


def closure(T: dict, ids) -> set:
    """The techs and everything they need."""
    out, todo = set(), list(ids)
    while todo:
        i = todo.pop()
        if i not in out:
            out.add(i)
            todo.extend(T["techs"][i].get("needs", []))
    return out


def _kind(T: dict, line: dict, L: dict) -> dict:
    """The [[kind]] rules that hold for a line (its own, else its nearest ancestor's; first parent up the tree)."""
    kinds = {i: k for k in T.get("kind", []) for i in k["of"]}
    seen, cur = set(), line
    while cur is not None and cur["id"] not in seen:
        seen.add(cur["id"])
        if cur["id"] in kinds:
            return kinds[cur["id"]]
        up = cur.get("group_of") or (cur.get("parents") or [None])[0]
        cur = L.get(up)
    return {}


def _node(line: dict, L: dict) -> float | None:
    """The sapiens node (kyr) of the line's own stem or the nearest stem above it (first parent up the tree; PW-971)."""
    seen, cur = set(), line
    while cur is not None and cur["id"] not in seen:
        seen.add(cur["id"])
        if cur.get("sapient_kyr") is not None:
            return float(cur["sapient_kyr"])
        up = cur.get("group_of") or (cur.get("parents") or [None])[0]
        cur = L.get(up)
    return None


GRIPS = ("hands", "beak", "any")


def _grips(t: dict, k: dict, node: float | None, ago: float) -> bool:
    """Whether a kind can hold the tool of a tech that needs one (PW-987): its grip ("hands", "beak" or "any") against the
    kind's hands (true; false: dragons; "node": from its stem's sapiens node on, or always without a node) and beak."""
    h = k.get("hands", True)
    hands = h is True or (h == "node" and (node is None or ago <= node))
    beak = bool(k.get("beak"))
    g = t.get("grip", "hands")
    return hands if g == "hands" else beak if g == "beak" else hands or beak


def _env_ok(t: dict, have: set | None) -> bool:
    if have is None:  # (no range or no goods to read: not checked)
        return True
    if any(g not in have for g in t.get("env", [])):
        return False
    return not t.get("env_any") or any(g in have for g in t["env_any"])


def goods_held(T: dict, present: np.ndarray | None, goods: dict | None, k: int) -> set | None:
    """The goods a line's country holds (its present range): a good at env_min or more on env_share of its cells."""
    if present is None or goods is None:
        return None
    d = T["defaults"]
    sel = present[k] >= 0.05
    if not sel.any():
        return None
    out = set()
    for g, v in goods.items():
        if g.startswith("_"):
            continue
        a = np.asarray(v, float)
        if a.shape[0] != sel.shape[0]:
            continue
        if g in DEPOSITS:  # (a deposit is a point: a district, mining.ORE_MIN, in a few of the people's cells will do)
            if int((a[sel] >= d["deposit_min"]).sum()) >= max(2, d["deposit_share"] * sel.sum()):
                out.add(g)
        elif float((a[sel] >= d["env_min"]).mean()) >= d["env_share"]:
            out.add(g)
    return out


def rate_of(t: dict, D: dict) -> float:
    """Per kyr: the tech's own rate, else its track's; a late tech (earliest_kyr <= late_kyr) at least late_rate, so the
    short Holocene chains (villages to writing) are climbed within thousands of years, not tens of thousands."""
    r = t.get("rate", D["track_rate"].get(t["track"], D["rate"]))
    if "rate" not in t and t.get("earliest_kyr", 1e9) <= D["late_kyr"]:
        r = max(r, D["late_rate"])
    return r


def build(lines: list[dict], contacts: dict | None, pres: dict | None, present: np.ndarray | None = None,
          goods: dict | None = None, mode: str = "fantasy", era: str | None = "renaissance", seed: int = 0,
          T: dict | None = None) -> dict:
    """meta.techtree for a peoples run. `lines` as in meta.lineages (id, origin, parents, group_of, overlay, started_kyr,
    ended_kyr, demography, traits), `contacts` as meta.contacts, `pres` as meta.present (crops and animals: the tamings,
    lines: the populations), `present` the presence per line (lines x cells, 0..1) and `goods` the world's goods."""
    T = T or load()
    D = T["defaults"]
    cap = ERAS.index(era) if era in ERAS else len(ERAS) - 1
    techs = {i: t for i, t in T["techs"].items() if ERAS.index(t.get("era", "stone age")) <= cap
             and (mode != "real" or t.get("mode") != "fantasy")}
    order = [i for i in T["order"] if i in techs]
    rng = np.random.default_rng((seed, 675))
    L = {l["id"]: l for l in lines}
    people = [l for l in lines if not (l.get("overlay") and l.get("origin") == "template")]
    idx = {l["id"]: l.get("index", k) for k, l in enumerate(lines)}
    unmatched = [" | ".join(k["of"]) for k in T.get("kind", []) if not set(k["of"]) & set(L)]
    if unmatched:  # (a rule none of whose ids is a line of this tree applies to nothing, PW-1041)
        warnings.warn(f"tech tree [[kind]] rules name no line of this tree: {', '.join(unmatched)}", stacklevel=2)
    kind = {l["id"]: _kind(T, l, L) for l in people}
    node = {l["id"]: _node(l, L) for l in people}  # (PW-971: the sapiens node, kyr, of the line's stem; None: no stem node above it)
    have = {l["id"]: goods_held(T, present, goods, idx[l["id"]]) for l in people}
    pops = ((pres or {}).get("lines") or {})
    size = {}
    for l in people:
        p = (pops.get(l["id"]) or {}).get("population")
        size[l["id"]] = float(np.clip(math.log10(p + 1) / 5.0, 0.3, 1.5)) if p else 0.5
    start = {l["id"]: float(l.get("started_kyr") if l.get("started_kyr") is not None else l.get("ago_kyr", 0.0)) for l in people}
    end = {l["id"]: float(l["ended_kyr"]) if l.get("ended_kyr") is not None else -1.0 for l in people}
    # forced knowledge: the first tamings of the history (crops.py, animals.py)
    forced: dict[str, list[tuple[float, str]]] = {}
    stock_tech = {t.get("stock"): i for i, t in techs.items() if t.get("stock")}
    for key in ("crops", "animals"):
        st = ((pres or {}).get(key) or {}).get("stocks") or {}
        if key not in stock_tech:
            continue
        for s in st.values():
            for tm in s.get("tamed") or []:
                if tm.get("line") in L:
                    forced.setdefault(tm["line"], []).append((float(tm["ago_kyr"]), stock_tech[key]))
            for lid, ago in (s.get("took_up_kyr") or {}).items():
                if lid in L and ago is not None:
                    forced.setdefault(lid, []).append((float(ago), stock_tech[key]))
    # contacts as intervals: (a, b, from kyr, to kyr, border km)
    links = []
    for p in (contacts or {}).get("pairs", []):
        if p["a"] in kind and p["b"] in kind:
            ser = p.get("series") or []
            to = 0.0 if p.get("in_contact_now") else (min(q[0] for q in ser) if ser else p["first_contact_kyr"])
            km = float(np.median([q[1] for q in ser])) if ser else float(p.get("border_km_peak", 0))
            links.append((p["a"], p["b"], float(p["first_contact_kyr"]), to, km))
    t0 = max(start.values(), default=1.0)
    grid = np.concatenate([np.geomspace(max(t0, 1.0), NEAR_KYR, STEPS), [0.0]])
    known: dict[str, dict[str, list]] = {l["id"]: {} for l in people}

    def give(lid, tid, ago, how, frm=None):
        if tid in techs and tid not in known[lid]:
            known[lid][tid] = [round(float(ago), 3), how, frm]

    def held(lid, tid, at):  # (PW-987: a line cannot inherit a tool it cannot hold: the cats take no found tools from the mammal root)
        t = techs[tid]
        return not t.get("hands", True) or _grips(t, kind[lid], node[lid], at)

    def can(lid, tid, ago, inventing, needs=True):
        t = techs[tid]
        k = kind[lid]
        if tid in known[lid] or (needs and any(n not in known[lid] for n in t.get("needs", []))):
            return False
        if node[lid] is not None and ago > node[lid] and not t.get("bare"):  # (PW-971: before its stem's minds only bare-bones tools)
            return False
        if t.get("hands", True) and not _grips(t, k, node[lid], ago):
            return False
        if (inventing or not t.get("traded")) and not _env_ok(t, have[lid]):  # (a traded tech, bronze, comes without the ore)
            return False
        if inventing:
            first = t.get("elder_kyr", t.get("earliest_kyr", 0)) if k.get("elder") else t.get("earliest_kyr", 0)
            return ago <= first
        return True

    began = set()
    prev = grid[0]
    for ago in grid:
        dt = max(prev - ago, 1e-6) if ago != grid[0] else 0.0
        prev = ago
        alive = [l for l in people if start[l["id"]] >= ago and (end[l["id"]] < 0 or ago > end[l["id"]])]
        for l in alive:  # (inheritance and kits, once, at the line's start)
            lid = l["id"]
            if lid in began:
                continue
            began.add(lid)
            at = min(start[lid], grid[0])
            if l.get("origin") in ("split", "group") or l.get("group_of"):
                src = l.get("group_of") or (l.get("parents") or [None])[0]
                for tid, v in (known.get(src) or {}).items():
                    if v[0] >= at - 1e-9 and not (node[lid] is not None and at > node[lid] and not techs[tid].get("bare")) and held(lid, tid, at):  # (PW-971: a stem under a node inherits only bare tools from before it)
                        give(lid, tid, at, "inherited", src)
            elif l.get("origin") == "hybrid":
                for src in l.get("parents") or []:
                    for tid in list((known.get(src) or {})):
                        if not (node[lid] is not None and at > node[lid] and not techs[tid].get("bare")) and held(lid, tid, at):
                            give(lid, tid, at, "inherited", src)
            kit = closure(T, [i for i in kind[lid].get("kit", []) if i in T["techs"]])
            for tid in [i for i in order if i in kit]:
                give(lid, tid, at, "kit" if l.get("origin") == "arrival" else "inherited", None)
        for l in alive:  # (tamings recorded by the history)
            for when, tid in forced.get(l["id"], []):
                if when >= ago and tid not in known[l["id"]]:
                    for n in [i for i in order if i in closure(T, [tid]) and i != tid]:
                        give(l["id"], n, when, "with " + tid, None)
                    give(l["id"], tid, when, "tamed", None)
        if dt <= 0:
            continue
        for l in alive:  # (inventing)
            lid = l["id"]
            rx = kind[lid].get("rate_x", 1.0) * size[lid]
            for tid in order:
                if can(lid, tid, ago, True):
                    t = techs[tid]
                    r = rate_of(t, D)
                    if rng.random() < 1 - math.exp(-r * rx * dt):
                        give(lid, tid, ago, "invented", None)
        for a, b, fr, to, km in links:  # (diffusion over borders)
            if not (fr >= ago >= to):
                continue
            w = min(km / D["contact_full_km"], 1.0)
            for x, y in ((a, b), (b, a)):
                if x not in began or y not in began:
                    continue
                op = 1 - 0.7 * float((L[y].get("demography") or {}).get("insularity", 0.3))
                for tid in order:
                    lang = bool(techs[tid].get("modern_contact"))  # (language: to any genetically modern people, PW-971)
                    if lang and node[y] is None:
                        continue
                    if tid in known[x] and known[x][tid][0] >= ago and can(y, tid, ago, False, needs=not lang):
                        r = D["contact_rate"] * techs[tid].get("spread", D["spread"]) * w * op
                        if r > 0 and rng.random() < 1 - math.exp(-r * dt):
                            for n in [i for i in order if lang and i in closure(T, [tid]) and i != tid]:
                                give(y, n, ago, "with " + tid, x)  # (its roots, gesture, come with it)
                            give(y, tid, ago, "contact", x)
        for l in alive:  # (a group and its people share what they know as they go)
            g = l.get("group_of")
            if g and g in known:
                for x, y in ((g, l["id"]), (l["id"], g)):
                    for tid, v in list(known[x].items()):
                        if v[0] >= ago and tid not in known[y] and can(y, tid, ago, False):
                            give(y, tid, ago, "shared", x)
    firsts = firsts_of(known)
    return {"file": str(T.get("_file", FILE.name)), "era": era, "mode": mode,
            "tracks": [{"id": k["id"], "name": k["name"]} for k in T["track"]],
            "techs": [{"id": i, "name": techs[i]["name"], "track": techs[i]["track"], "needs": techs[i].get("needs", []),
                       "env": techs[i].get("env", []), "env_any": techs[i].get("env_any", []),
                       "earliest_kyr": techs[i].get("earliest_kyr"), "elder_kyr": techs[i].get("elder_kyr"),
                       "era": techs[i].get("era", "stone age"), "fantasy": techs[i].get("mode") == "fantasy",
                       "source": techs[i].get("source", "")} for i in order],
            "known": known, "firsts": firsts,
            "goods_checked": {lid: sorted(v) if v is not None else None for lid, v in have.items()}}


def _source_rank(how: str) -> int:
    """How much a record says the people found the tech itself: invented, then tamed or brought (a kit, or the roots
    that come with a taming), then got from someone else (contact, shared, inherited)."""
    if how == "invented":
        return 0
    if how in ("tamed", "kit") or how.startswith("with "):
        return 1
    return 2


def firsts_of(known: dict) -> dict:
    """Each tech's first people: the oldest date; on a tie (two records on the same grid step) the one that found it
    itself, so a same-step contact taker is never credited over its giver (PW-1012)."""
    firsts = {}
    for lid, kn in known.items():
        for tid, v in kn.items():
            f = firsts.get(tid)
            if f is None or v[0] > f["ago_kyr"] or (v[0] == f["ago_kyr"] and _source_rank(v[1]) < _source_rank(f["how"])):
                firsts[tid] = {"line": lid, "ago_kyr": v[0], "how": v[1]}
    return firsts


def lines_for_report(tt: dict, lines: list[dict]) -> list[str]:
    """A few lines for run.txt: when each people came to language and how many techs each knows now."""
    alive = [l for l in lines if l.get("leaf") and l["id"] in tt["known"]]
    out = [f"technology (techtree.py, PW-675 v0): {len(tt['techs'])} techs in {len(tt['tracks'])} tracks"]
    lang = sorted(((tt["known"][l["id"]].get("language") or [None])[0] or -1, l["id"]) for l in alive)
    out.append("  language: " + "; ".join(f"{lid} {'none' if a < 0 else f'{a:g} kyr ({tt['known'][lid]['language'][1]})'}"
                                         for a, lid in sorted(lang, key=lambda x: -x[0])))
    out.append("  techs known now: " + ", ".join(f"{l['id']} {len(tt['known'][l['id']])}" for l in
                                                 sorted(alive, key=lambda l: -len(tt["known"][l["id"]]))))
    return out


def for_run(run_dir: Path) -> dict:
    """Builds (or rebuilds) meta.techtree of a stored peoples run in place; returns it."""
    from .. import store as S
    from . import land as LD
    p = Path(run_dir) / "run.json"
    run = json.loads(p.read_text())
    m = run["meta"]
    pp = m.get("presence_present")
    present = None
    if pp:
        present = np.frombuffer((Path(run_dir) / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0
    goods = LD.goods(m.get("world")) if m.get("world") else None
    tt = build(m["lineages"], m.get("contacts"), m.get("present"), present, goods, m.get("mode", "fantasy"),
               m.get("era"), int(m.get("try_seed") or 0))
    S.update_meta(run_dir, lambda r: r["meta"].__setitem__("techtree", tt))  # (re-read under the lock, PW-1040)
    return tt
