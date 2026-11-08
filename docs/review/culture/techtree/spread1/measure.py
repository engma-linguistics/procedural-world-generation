"""Spread 1 (PW-1485, D58): how the techs are spread over the living peoples at the present-day finish, over re-rolled draws.
Read-only on the stored runs: the tree is rebuilt in memory (techtree.rebuild's path, shipped defaults), the goods cache is never
written. argv: run_id n_draws out.json jobs.  Env: PLANET_DATA = the data root holding runs/ (the main checkout).
Per draw and living people: what it knows (tech -> [kyr ago, how]), its attributes, and for every tech some other living people holds
but it lacks, the first thing in the way (techtree.Calendar.can's own checks, in its order) at the present."""
import json, math, os, sys, warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

RID, N, OUT, JOBS = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
_C = {}


def inputs():
    if "in" not in _C:
        from planet import store as S
        from planet.lineages import land as LD, techtree as TT
        LD._disk_write = lambda *a, **k: None  # (never write the goods cache into the owner's worlds/)
        R = S.runs_dir() / RID
        m = json.loads((R / "run.json").read_text())["meta"]
        pp = m.get("presence_present")
        present = np.frombuffer((R / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0 if pp else None
        goods = LD.goods(m.get("world")) if m.get("world") else None
        lines = TT.with_generations(m["lineages"], m.get("tree"))
        towns = None
        D = TT.load()["defaults"]
        if set(str(TT._arm(D, "contact_arms"))) & {"B", "E"} and m.get("settlements"):
            from planet.lineages.techspread import town_footprint
            towns = town_footprint(R)
        lm = TT.landmass_of(R, m)
        cell_km2 = None
        try:
            from planet.grid import shared_grid
            g = shared_grid(m["level"])
            cell_km2 = float(np.mean(g.area)) if hasattr(g, "area") else None
        except Exception:
            pass
        _C["in"] = (m, lines, present, goods, towns, lm, cell_km2)
    return _C["in"]


def stem_of(L, lid):
    """The people's kind: the stem it split from (saurian, chromatic_dragon, hominid ...); an arrival or hybrid is its own."""
    l = L.get(lid) or {}
    return l["parents"][0] if l.get("origin") == "split" and l.get("parents") else lid


def one(seed):
    from planet.lineages import techtree as TT
    m, lines, present, goods, towns, lm, cell_km2 = inputs()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = TT.Calendar(lines, m.get("mode", "fantasy"), m.get("era"), seed, None, m.get("gods_mode", "faith_made"), towns, None)
        have = {l["id"]: TT.goods_held(c.T, present, goods, c.idx[l["id"]]) for l in c.people}
        c.feed(lines, TT.links_of(m.get("contacts"), c.kind), TT.forced_of(m.get("present"), c.techs, c.L), have,
               (m.get("present") or {}).get("lines") or {}, c.region_shares(present, lm))
        c.advance()
        res = c.result()
    alive = list(res["drivers"])
    known = {p: res["known"][p] for p in alive}
    world = sorted({t for p in alive for t in known[p]})
    L = c.L
    now_links = {}  # (contacts in force at the present: neighbour -> border km)
    for a, b, fr, to_, km in c.links:
        if to_ <= 1e-9:
            now_links.setdefault(a, {})[b] = km
            now_links.setdefault(b, {})[a] = km
    ppl = {}
    for p in alive:
        l = L[p]
        ser = c.series[p]
        area = TT._area_at(ser, 0.0) if ser is not None else None
        n, dens = TT._at(ser, 0.0) if ser is not None else (None, None)
        rg = c.regions.get(p) or []
        lms = None
        if present is not None and lm is not None:
            pr = present[c.idx[p]]
            cells = pr > 0.05
            if cells.any():
                labs, cnt = np.unique(lm[cells], return_counts=True)
                big = labs[np.argmax(cnt)]
                lms = {"landmasses": int(len(labs)), "main_lm": int(big), "main_lm_cells": int((lm == big).sum()),
                       "cells": int(cells.sum())}
        # the gaps: techs some living people holds that this one lacks, and whose needs it holds (the frontier, not the cascade)
        gaps = {}
        kn = c.known[p]
        for t in world:
            if t in kn:
                continue
            tt = c.techs[t]
            if any(x not in kn for x in tt.get("needs", [])) or (tt.get("needs_any") and not any(x in kn for x in tt["needs_any"])):
                continue  # (a cascade gap: counted under the missing prerequisite)
            node = c.node[p]
            if tt.get("hands", True) and not TT._grips(tt, c.kind[p], node, 0.0):
                why = "body"  # (cannot hold the tool: dragons, PW-987)
            elif not TT._env_ok(tt, c.have[p]) and not tt.get("traded"):
                why = "land"  # (its country lacks the goods; not a traded tech)
            elif tt.get("stock"):
                why = "stock"  # (a crop or animal of the history's tamings)
            else:
                holders = [q for q in now_links.get(p, {}) if t in known.get(q, {})]
                spread = tt.get("spread", c.D["spread"])
                inv = c.can(p, t, 0.0, True)
                if spread == 0:
                    why = "own_only"  # (never passes by contact; invent or nothing)
                elif not holders:
                    why = "no_holder_neighbour"
                else:
                    arr = [c.arrive.get((q, p, t)) for q in holders]
                    why = "front_en_route" if any(a is not None for a in arr) else "neighbour_no_front"
                if why in ("no_holder_neighbour", "front_en_route", "neighbour_no_front") and not inv:
                    why += "+cannot_invent"
            gaps[t] = why
        s_all, s_spec, s = c.strengths(p, 0.0)
        ppl[p] = {"name": l.get("name", p), "stem": stem_of(L, p), "origin": l.get("origin"), "way": l.get("way"),
                  "traits": l.get("traits") or [], "insularity": (l.get("demography") or {}).get("insularity"),
                  "pop": res["drivers"][p]["population"], "area_mkm2": area, "dens": dens, "gen_yr": c.gens[p],
                  "s": s, "S_all": s_all, "S_spec": s_spec, "regions": len(rg), "lm": lms,
                  "neighbours": {q: round(km) for q, km in now_links.get(p, {}).items() if q in known},
                  "started_kyr": c.start.get(p), "known": known[p], "gaps": gaps}
    techs = {t["id"]: {"era": t["era"], "track": t["track"], "pool": t["pool"], "fantasy": t["fantasy"],
                       "spread": c.techs[t["id"]].get("spread", c.D["spread"]), "traded": bool(c.techs[t["id"]].get("traded")),
                       "env": t["env"] + t["env_any"], "stock": c.techs[t["id"]].get("stock"), "domains": t["domains"]}
             for t in res["techs"]}
    return {"seed": seed, "people": ppl, "techs": techs, "firsts": res["firsts"]}


if __name__ == "__main__":
    m = json.loads((Path(os.environ["PLANET_DATA"]) / "runs" / RID / "run.json").read_text())["meta"]
    base = int(m.get("try_seed") or 0)
    seeds = list(range(base, base + N))
    with Pool(JOBS) as P:
        rows = P.map(one, seeds)
    Path(OUT).write_text(json.dumps({"run": RID, "era": m.get("era"), "seeds": seeds, "draws": rows}))
    print("wrote", OUT)
