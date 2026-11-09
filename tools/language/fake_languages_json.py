"""A small synthetic languages.json in the shape of planet/language/output.py's document (30 lects, 10 frames), for developing
and testing the languages viewer (viewer/languages.html) without a full pass. Not a model of anything: random but consistent
(parents, snapshots as deltas, intelligibility falling with time apart, a continuum, names filled in the architecture's shape).

    uv run python tools/language/fake_languages_json.py [out.json]
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

CORE = sorted(["ALL", "ASH", "BIG", "BIRD", "BLOOD", "BONE", "DOG", "DRINK", "EAT", "EYE", "FIRE", "FISH", "HAND", "HEAD", "I", "MAN",
               "MOON", "NAME", "ONE", "PERSON", "SEE", "STAR", "STONE", "SUN", "THOU", "TREE", "TWO", "WATER", "WE", "WOMAN"])
CONS = ["p", "b", "t", "d", "k", "ɡ", "q", "ʔ", "m", "n", "ɲ", "ŋ", "f", "s", "z", "ʃ", "x", "χ", "h", "ts", "tʃ", "l", "r", "ɾ", "j", "w",
        "pʰ", "tʰ", "kʼ", "ɓ", "ɗ", "ǀ", "ŋ‼"]
VOWS = ["i", "e", "a", "o", "u", "ɛ", "ɔ", "ə", "ɨ", "y", "ã", "ĩ", "aː", "uː"]
GRAMS = ["PAST", "PL", "DIM", "LOC", "NEG", "FUT", "PERF", "ACC"]


def word(rng, cs, vs, n=None):
    return "".join(rng.choice(cs) + rng.choice(vs) for _ in range(n or rng.randint(1, 3)))


def mutate(rng, w, cs, vs):
    if not w or rng.random() < 0.6:
        return w
    k = rng.randrange(len(w))
    return w[:k] + rng.choice(cs + vs) + w[k + 1:]


def build(seed: int = 1, n_lects: int = 30, n_frames: int = 10) -> dict:
    rng = random.Random(seed)
    frames = [round(20.0 - i * 20.0 / (n_frames - 1), 3) for i in range(n_frames)]
    peoples = ["human", "elf", "kobold"]
    lects, nodes = [], []
    # three protos (no deme), then daughters budding or shifting
    for k, p in enumerate(peoples):
        lects.append({"id": f"p{k}", "deme": None, "people": p, "parent": None, "how": "proto", "born_kyr": 20.0, "died_kyr": 20.0,
                      "end": "split", "substrate": None})
    for j in range(n_lects - 3):
        par = rng.choice([l for l in lects if l["deme"] is not None or l["how"] == "proto"][: 3 + j])
        born = 20.0 if par["how"] == "proto" else round(rng.choice([f for f in frames if f < par["born_kyr"]] or [par["born_kyr"]]), 3)
        how = "bud" if par["how"] == "proto" or rng.random() < 0.8 else "shift"
        lects.append({"id": f"d{j}", "deme": j, "people": par["people"], "parent": par["id"], "how": how, "born_kyr": born,
                      "died_kyr": None, "end": None, "substrate": f"d{max(0, j - 1)}" if how == "shift" else None})
    for l in lects[3:]:  # some die
        if rng.random() < 0.25:
            later = [f for f in frames if f < l["born_kyr"]]
            if later:
                l["died_kyr"], l["end"] = rng.choice(later), "extinct"
    living = [l for l in lects if l["died_kyr"] is None and l["deme"] is not None]
    by = {l["id"]: l for l in lects}
    for l in lects:
        l["family_true"] = l["id"] if l["parent"] is None else None
    for l in lects:
        x = l
        while x["parent"]:
            x = by[x["parent"]]
        l["family_true"] = x["id"]
    # snapshots and lexicons
    base = {}
    for l in lects:
        cs = rng.sample(CONS, rng.randint(14, 24))
        vs = rng.sample(VOWS, rng.randint(4, 8))
        par = by.get(l["parent"]) if l["parent"] else None
        core = [mutate(rng, w, cs, vs) for w in base[par["id"]]["core"]] if par else [word(rng, cs, vs) for _ in CORE]
        base[l["id"]] = {"c": cs, "v": vs, "core": core}
        snaps, prev = [], None
        if l["deme"] is not None:
            for f in frames:
                if not (l["born_kyr"] >= f and (l["died_kyr"] is None or l["died_kyr"] < f)):
                    continue
                if prev is not None and rng.random() < 0.5:
                    cs = cs[:-1] + [rng.choice(CONS)] if rng.random() < 0.5 else cs
                    core = [mutate(rng, w, cs, vs) for w in core]
                grams = [[g, word(rng, cs, vs, 1), min(3, int((20 - f) / 6) + k % 2)] for k, g in enumerate(GRAMS[: 3 + int((20 - f) / 5)])]
                full = {"c": list(cs), "v": list(vs), "core": list(core), "typ": {"order": rng.choice(["SOV", "SVO"]), "adp": "post", "case": "none",
                                                                                 "number": "none", "gender": "none", "n_case": 0, "n_number": 0, "n_class": 0},
                        "grams": grams, "cx": round(0.5 + (20 - f) / 10 + rng.random(), 3), "shares": {}}
                if prev is None:
                    snaps.append([f, full])
                else:
                    d = {"d": 1, "core": {str(i): b for i, (a, b) in enumerate(zip(prev["core"], full["core"])) if a != b}}
                    for k in ("c", "v", "typ", "grams", "cx", "shares"):
                        if full[k] != prev[k]:
                            d[k] = full[k]
                    snaps.append([f, d])
                prev = full
        lex = {}
        for c, w in zip(CORE, core):
            nodes.append([-1, 20.0, l["family_true"], "proto", w[::-1] or "a", c.lower()])
            nodes.append([len(nodes) - 1, l["born_kyr"], l["id"], "sound_change:S001+S014", w or "a", 0])
            lex[c] = {"ipa": w, "roman": w.replace("ʃ", "sh").replace("ŋ", "ng"), "pos": "N", "freq": 2, "etym": len(nodes) - 1}
        l.update({"rate": 1.0, "gen_yr": 25.0, "language": None, "family_scholars": None,
                  "deme_name": None if l["deme"] is None else f"{l['people']} {l['deme'] + 1} (the north of Fakeland)",
                  "inventory": {"consonants": cs, "vowels": vs, "tones": [], "shapes": {"CV": 1.0}, "stress": "initial", "max_onset": 1, "max_coda": 0},
                  "typology": {"word_order": "SOV"}, "grams": [], "paradigms": {}, "complexity": {"score": 1.0},
                  "lexicon": lex, "lexicon_full": l in living, "affixes": {},
                  "changes": [[f, f"S{rng.randint(1, 180):03d}", rng.choice(["effort", "coarticulation", "perception"]), None]
                              for f in frames if l["born_kyr"] >= f and (l["died_kyr"] is None or l["died_kyr"] < f) and rng.random() < 0.7],
                  "rules_applied": 3, "generations": 800.0, "l2": 0.1, "population": float(rng.randint(500, 50000)), "isolation": 0.2,
                  "shares_history": [], "stats": None, "snapshots": snaps})
    # intelligibility: by shared core words between snapshots at each frame
    def at(l, i):
        sn = None
        cur = None
        for f, s in l["snapshots"]:
            cur = dict(s) if not s.get("d") else {**cur, **{k: v for k, v in s.items() if k not in ("d", "core")},
                                                     "core": [s["core"].get(str(j), x) for j, x in enumerate(cur["core"])]}
            if f >= frames[i]:
                sn = cur
        return sn
    pairs, now = [], []
    dl = [l for l in lects if l["deme"] is not None]
    for x in range(len(dl)):
        for y in range(x + 1, len(dl)):
            a, b = sorted([dl[x]["id"], dl[y]["id"]])
            if dl[x]["family_true"] != dl[y]["family_true"] and rng.random() < 0.7:
                continue
            vals = []
            for i in range(n_frames):
                sa, sb = at(by[a], i), at(by[b], i)
                alive = all(l["born_kyr"] >= frames[i] and (l["died_kyr"] is None or l["died_kyr"] < frames[i]) for l in (by[a], by[b]))
                vals.append(round(sum(p == q for p, q in zip(sa["core"], sb["core"])) / len(CORE), 3) if (sa and sb and alive) else None)
            pairs.append([a, b, vals])
            if vals[-1] is not None and vals[-1] >= 0.05:
                now.append([a, b, vals[-1]])
    # languages: living lects grouped by family (fake)
    fams = {}
    for l in living:
        fams.setdefault(l["family_true"], []).append(l["id"])
    langs = []
    for k, (f, ids) in enumerate(sorted(fams.items())):
        for i in ids:
            by[i]["language"], by[i]["family_scholars"] = f"lang{k}", f"fam{k}"
        langs.append({"id": f"lang{k}", "name": f"speech of {by[ids[0]]['deme_name']}", "largest_lect": ids[0], "lects": sorted(ids),
                      "peoples": sorted({by[i]["people"] for i in ids})})

    def upgma_like(ids):
        t = {"lect": ids[0]}
        for i in ids[1:]:
            t = {"distance": round(rng.uniform(0.3, 1.0), 3), "children": [t, {"lect": i}]}
        return t
    sch = [upgma_like([l["id"] for l in living])] if living else []
    chain = [l["id"] for l in living if l["family_true"] == living[0]["family_true"]][:4] if living else []
    cont = [{"family": living[0]["family_true"], "chain": chain, "adjacent": [0.8] * (len(chain) - 1), "ends": 0.3}] if len(chain) >= 3 else []
    names = {"peoples": {}, "demes": {}, "common": None}
    for p in peoples:
        src = next((l for l in living if l["people"] == p), None)
        if src is None:
            continue
        w = src["lexicon"]["PERSON"]
        n = {"ipa": w["ipa"], "roman": w["roman"].capitalize(), "gloss": "the people", "pattern": "E1", "lect": src["id"], "etym": w["etym"]}
        names["peoples"][p] = {"endonym": n, "glossonym": {**n, "gloss": "our speech"},
                               "set": {"land": {**n, "gloss": "land of the people"}, "people": n, "person": n, "language": n},
                               "exonyms": [{"by_people": q, "by_lect": None, "ipa": w["ipa"][::-1], "roman": w["roman"][::-1], "gloss": "the strangers",
                                            "pattern": "X2", "basis": "neighbours", "era_kyr": 5.0, "relay": [], "etym": w["etym"]} for q in peoples if q != p]}
    for l in living:
        names["demes"][str(l["deme"])] = {"name": {"ipa": l["lexicon"]["STONE"]["ipa"], "roman": l["lexicon"]["STONE"]["roman"]},
                                          "places": [{"kind": "river", "ipa": l["lexicon"]["WATER"]["ipa"], "roman": l["lexicon"]["WATER"]["roman"],
                                                      "gloss": "water", "lect": l["id"], "kyr": l["born_kyr"], "substrate_of": None}]}
    routes = []
    if len(living) >= 3:
        hops = [{"deme": living[k]["deme"], "lect": living[k]["id"], "kyr": frames[-2], "ipa": "nama", "from_deme": living[k - 1]["deme"],
                 "from_lect": living[k - 1]["id"], "from_ipa": "nama", "changes": ["sound_change:S001"], "roman": "nama"} for k in (1, 2)]
        routes.append({"concept": "crop:alliums", "origin_deme": living[0]["deme"], "origin_lect": living[0]["id"], "kyr": frames[-3], "ipa": "nama",
                       "origin": "first known here", "hops": hops, "roman": "nama"})
    shifts = [{"deme": l["deme"], "kyr": l["born_kyr"], "from_lect": l["substrate"], "to_lect": l["id"], "ruler_lect": l["parent"], "ruler_deme": None,
               "trigger": {"kind": "takeover", "source": "fake"}, "substrate_words": ["FISH", "RIVER"], "accent": [["x", "k"]], "calques": [],
               "speakers": l["people"], "ruler_people": l["people"]} for l in lects if l["how"] == "shift"]
    return {"format": "procgen-languages/1", "run": "fake", "seed": seed, "start_kyr": 20.0, "frames_kyr": frames, "romanization": "house/2",
            "profiles": {p: {"source": "human_default", "modality": "spoken", "articulators": ["lips", "tongue_tip"], "make_cost": {"click": 3.0, "purr": "inf"},
                             "hear": {"tone": 1.0}, "notes": ["Human default"]} for p in peoples},
            "snapshot_concepts": CORE, "etym_nodes": nodes, "lects": lects, "names": names, "shifts": shifts, "food_routes": routes,
            "families": {"living": len(living), "lang_share": 0.7, "cognate_dist": 0.45, "chance": {"mean": 0.001, "sd": 0.003, "floor": 0.007, "pairs": 400},
                         "true": [], "scholars": sch, "languages": langs, "scholars_families": len(langs), "true_families": len(fams),
                         "horizon_kyr": 8.0, "horizon_by": {"human": {"horizon_kyr": 7.0}}},
            "intelligibility": {"frames": frames, "pairs": pairs, "now": now}, "continua": cont,
            "checks": [{"name": "fake check", "value": {"a": 1}, "target": "> 0", "pass": True, "note": "synthetic"}],
            "landscape": {"rivers": {}, "lakes": {}, "demes": {}, "river_flow_floor": 4900.0}, "log": [], "timing": {}, "constants": {}}


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/78e89d74-f837-4b74-a7da-25a178d37d96/scratchpad/viewer/languages.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = build()
    out.write_text(json.dumps(doc, ensure_ascii=False))
    print(out, len(doc["lects"]), "lects", len(doc["frames_kyr"]), "frames")
