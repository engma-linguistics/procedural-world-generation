"""PW-1483 sensitivity: the tree of a stored run, main's code against this branch's, over N draws, base and nudged.
argv: run_dir n_draws out.json [jobs]. Read-only on the run. Nudges:
  border: every contact's border x 0.9 (fronts a little slower everywhere, as round 9's short early borders)
  pop:    the population of one people x 1.05 (the base draw's first writer: its own hazard a little higher)
"""
import importlib.util, json, sys, warnings
from multiprocessing import Pool
from pathlib import Path
import numpy as np

SCR = Path(__file__).parent
RUN = Path(sys.argv[1]); N = int(sys.argv[2]); OUT = sys.argv[3]; JOBS = int(sys.argv[4]) if len(sys.argv) > 4 else 6
_C = {}


def mod(code):
    if code not in _C:
        if code == "main":
            spec = importlib.util.spec_from_file_location("planet.lineages.tt_main", SCR / "tt_main.py")
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        else:
            from planet.lineages import techtree as m
        _C[code] = m
    return _C[code]


def inputs():
    if "in" not in _C:
        from planet.lineages import land as LD, techtree as TT
        m = json.loads((RUN / "run.json").read_text())["meta"]
        pp = m.get("presence_present")
        present = np.frombuffer((RUN / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0 if pp else None
        goods = LD.goods(m.get("world")) if m.get("world") else None
        lines = TT.with_generations(m["lineages"], m.get("tree"))
        _C["in"] = (m, lines, present, goods)
    return _C["in"]


def one(job):
    code, seed, nudge, who = job
    M = mod(code)
    m, lines, present, goods = inputs()
    contacts = m.get("contacts")
    if nudge == "border":
        contacts = {**contacts, "pairs": [{**p, "series": [[q[0], q[1] * 0.9, *q[2:]] for q in (p.get("series") or [])],
                                           "border_km_peak": p.get("border_km_peak", 0) * 0.9} for p in contacts["pairs"]]}
    if nudge == "pop" and who:
        lines = [{**l, "track": [[*r[:4], r[4] * 1.05, *r[5:]] for r in l["track"]]} if l["id"] == who and l.get("track") else l for l in lines]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tt = M.build(lines, contacts, m.get("present"), present, goods, m.get("mode", "fantasy"), m.get("era"), seed,
                     gods_mode=m.get("gods_mode", "faith_made"))
    W = ["villages", "towns", "chiefdoms", "tokens", "proto_writing", "writing", "cities", "kingship", "law"]
    return job, {p: {t: (kn.get(t) or [None, None])[:2] for t in W} for p, kn in tt["known"].items()}


if __name__ == "__main__":
    base = int(json.loads((RUN / "run.json").read_text())["meta"].get("try_seed") or 0)
    seeds = list(range(base, base + N))
    with Pool(JOBS) as P:
        r0 = dict(P.map(one, [(c, s, "base", None) for c in ("main", "new") for s in seeds]))
        first = {}
        for (c, s, _, _), K in r0.items():
            w = [(v["writing"][0], p) for p, v in K.items() if v["writing"][0] is not None]
            first[(c, s)] = max(w)[1] if w else None
        jobs = [(c, s, "border", None) for c in ("main", "new") for s in seeds] + \
               [(c, s, "pop", first[(c, s)]) for c in ("main", "new") for s in seeds]
        r1 = dict(P.map(one, jobs))
    res = {"run": RUN.name, "seeds": seeds, "rows": []}
    for (c, s, nd, who), K in {**r0, **r1}.items():
        res["rows"].append({"code": c, "seed": s, "nudge": nd, "who": who, "known": K})
    Path(OUT).write_text(json.dumps(res))
    print("wrote", OUT)
