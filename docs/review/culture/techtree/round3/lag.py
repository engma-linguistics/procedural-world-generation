"""Round 3 (PW-1490, PW-1491; lane 207): the neighbour lag, the held shares at fixed dates and the sea peoples' years behind, over
re-rolled draws. Read-only on the stored runs, as spread1/measure.py: the tree is rebuilt in memory with the code it is run from
(the shipped [defaults], or env ARMS for the contact arms), the goods cache is never written.
argv: run_id n_draws out.json jobs.  Env: PLANET_DATA = the data root holding runs/ (the main checkout); ARMS (optional).

The neighbour lag (Daniel, 11-07: "people local to a bunch of others with a tech lagging behind for hundreds+ of years"): for each
living people p and each tech t its land and body allow (goods held or the tech traded, the grip, not a single crop or beast, not
spread 0), the exposure E is the first time a neighbour in contact held t while p was alive; the lag is E - (p's date for t), or E - 0
(censored: still lacking today). A people that held t before any neighbour is not a case. `ready` is the later of E and the date p
held all of t's needs (None: it lacks one today): the lag from ready isolates the front from the prerequisite cascade."""
import json, os, sys, warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

RID, N, OUT, JOBS = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
ARMS = os.environ.get("ARMS")
_C = {}
KINDS = {  # the tech kinds Daniel named; every other eligible tech is "other"
    "farming": ("cultivation", "herding", "plough", "irrigation", "storage", "grinding"),
    "metal": ("native_copper", "copper", "arsenical_copper", "bronze", "iron", "steel", "casting", "iron_tools", "meteoric_iron"),
    "admin": ("writing", "law", "kingship", "coinage", "taxation", "census", "bureaucracy", "alphabet"),
}
KIND_OF = {t: k for k, ts in KINDS.items() for t in ts}
SHARE_TECHS = ("cultivation", "herding", "plough", "copper", "bronze", "iron", "towns", "cities", "chiefdoms", "kingship", "law",
               "writing", "coinage", "taxation", "alphabet", "printing", "pottery", "fire_making", "boats")
DATES = (4.0, 3.0, 2.0, 1.0, 0.5, 0.0)


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
        arms = ARMS if ARMS is not None else TT.arms_of()
        if set(arms) & set(TT.TOWN_ARMS) and m.get("settlements"):
            from planet.lineages.techspread import town_footprint
            towns = town_footprint(R)
        lm = TT.landmass_of(R, m)
        _C["in"] = (m, lines, present, goods, towns, lm, arms)
    return _C["in"]


def one(seed):
    from planet.lineages import techtree as TT
    m, lines, present, goods, towns, lm, arms = inputs()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = TT.Calendar(lines, m.get("mode", "fantasy"), m.get("era"), seed, None, m.get("gods_mode", "faith_made"), towns, arms)
        have = {l["id"]: TT.goods_held(c.T, present, goods, c.idx[l["id"]]) for l in c.people}
        c.feed(lines, TT.links_of(m.get("contacts"), c.kind), TT.forced_of(m.get("present"), c.techs, c.L), have,
               (m.get("present") or {}).get("lines") or {}, c.region_shares(present, lm))
        c.advance()
        res = c.result()
    alive = list(res["drivers"])
    known = {p: c.known[p] for p in alive}
    hand = [p for p in alive if len(known[p]) > 30]  # (the dragons hold their 10 body techs only)
    nbr: dict = {}  # p -> [(q, from, to)]
    for a, b, fr, to_, km in c.links:
        nbr.setdefault(a, []).append((b, fr, to_, km))
        nbr.setdefault(b, []).append((a, fr, to_, km))
    cases = []  # (people, tech, kind, exposure, date or None, ready or None, how, border km of the exposing link)
    for p in hand:
        sp = c.start.get(p, 0.0)
        kp = known[p]
        for t, tt in c.techs.items():
            if tt.get("spread", c.D["spread"]) == 0 or tt.get("modern_contact") or ":" in str(tt.get("stock") or ""):
                continue
            if tt.get("hands", True) and not TT._grips(tt, c.kind[p], c.node[p], 0.0):
                continue
            if not tt.get("traded") and not TT._env_ok(tt, c.have[p]):
                continue
            if getattr(TT, "sea_ok", None) and not TT.sea_ok(tt, c.L[p], c.L) and t not in kp:  # (a sea tech: sea peoples only)
                continue
            E, ekm = None, 0.0
            for q, fr, to_, km in nbr.get(p, []):
                v = c.known.get(q, {}).get(t)
                if v is None:
                    continue
                e = min(fr, v[0], sp)
                if e >= to_ - 1e-9 and (E is None or e > E):
                    E, ekm = e, km
            if E is None:
                continue
            tp = kp[t][0] if t in kp else None
            if tp is not None and tp >= E - 1e-9:
                continue  # (held it before any neighbour: not a lag case)
            nd = list(tt.get("needs", []))
            na = [n for n in tt.get("needs_any", []) if n in c.techs]
            rd = E
            ok = True
            for n in nd:
                if n not in kp:
                    ok = False
                    break
                rd = min(rd, kp[n][0])
            if ok and na:
                held = [kp[n][0] for n in na if n in kp]
                ok = bool(held)
                if ok:
                    rd = min(rd, max(held))
            cases.append((p, t, KIND_OF.get(t, "other"), round(E, 3), tp, round(rd, 3) if ok else None,
                          kp[t][1] if t in kp else None, round(ekm)))
    # held shares at fixed dates (today's peoples with hands; and by population now)
    shares = {}
    pop = {p: (res["drivers"][p]["population"] or 0) for p in hand}
    for t in SHARE_TECHS:
        if t not in c.techs:
            continue
        shares[t] = [sum(1 for p in hand if t in known[p] and known[p][t][0] >= d - 1e-9) for d in DATES]
    shares_pop = {t: sum(pop[p] for p in hand if t in known[p]) / max(sum(pop.values()), 1) for t in SHARE_TECHS if t in c.techs}
    # years behind the world (spread1/tables.py's clock) and the count of world techs held
    first = {}
    for p in hand:
        for t, v in known[p].items():
            first[t] = max(first.get(t, -1.0), v[0])
    ds = sorted(first.values(), reverse=True)
    behind = {}
    for p in hand:
        n = sum(1 for t in known[p] if t in first)
        behind[p] = (n, ds[min(n, len(ds)) - 1] if n > 0 else ds[0])
    L = c.L
    sea = {p: {"realm": L[p].get("realm", "land"), "swims": "swims" in (L[p].get("traits") or []), "n": len(known[p]),
               "behind_kyr": behind.get(p, (0, None))[1], "techs": sorted(known[p]), "have": sorted(c.have[p] or [])}
           for p in alive if L[p].get("realm", "land") != "land" or "swims" in (L[p].get("traits") or [])}
    ppl = {p: {"way": L[p].get("way"), "group_of": L[p].get("group_of"), "pop": pop[p], "realm": L[p].get("realm", "land"),
               "area": TT._area_at(c.series[p], 0.0) if c.series[p] is not None else None,
               "ins": (L[p].get("demography") or {}).get("insularity"), "n": len(known[p]), "behind_kyr": behind[p][1],
               "towns_now": TT.town_cells_at((towns or {}).get(p), 0.0) if towns else None,
               "towns_first": (float((towns or {})[p][0][int(np.argmax(np.asarray(towns[p][1]) >= 1))])
                               if towns and p in towns and (np.asarray(towns[p][1]) >= 1).any() else None),
               "admin": {t: known[p][t][0] for t in KINDS["admin"] if t in known[p]}}
           for p in hand}
    return {"seed": seed, "arms": "".join(sorted(c.arms)), "n_hand": len(hand), "cases": cases, "shares": shares,
            "shares_pop": shares_pop, "dates": DATES, "people": ppl, "sea": sea, "n_world": len(first)}


if __name__ == "__main__":
    m = json.loads((Path(os.environ["PLANET_DATA"]) / "runs" / RID / "run.json").read_text())["meta"]
    base = int(m.get("try_seed") or 0)
    seeds = list(range(base, base + N))
    with Pool(JOBS) as P:
        rows = P.map(one, seeds)
    Path(OUT).write_text(json.dumps({"run": RID, "seeds": seeds, "draws": rows}))
    print("wrote", OUT)
