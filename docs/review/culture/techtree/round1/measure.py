"""PW-1471/1483/1461 measures: a stored run's tree over N draws under several variants (read-only on the run).
argv: run_dir n_draws out.json jobs variants(comma: main,wait,floor,regions,regionsB,regionsBt)
  main     main's techtree.py + main's techtree.toml (the baseline)
  wait     this branch, own_floor off, no regions (PW-1483 alone)
  floor    + D55's floor (own_floor on)
  regions  + region learners (landmass from the run)
  regionsB / regionsBt  + arm B (town network) / + arm B weighted by trade (contact_arms "B" / "T")"""
import importlib.util, json, sys, warnings
from multiprocessing import Pool
from pathlib import Path
import numpy as np

SCR = Path(__file__).parent
RUN = Path(sys.argv[1]); N = int(sys.argv[2]); OUT = sys.argv[3]; JOBS = int(sys.argv[4]); VARS = sys.argv[5].split(",")
W = ["huts", "villages", "towns", "chiefdoms", "tokens", "proto_writing", "writing", "cities", "kingship", "law"]
_C = {}


def inputs():
    if "in" not in _C:
        from planet.lineages import land as LD, techtree as TT
        m = json.loads((RUN / "run.json").read_text())["meta"]
        pp = m.get("presence_present")
        present = np.frombuffer((RUN / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0 if pp else None
        goods = LD.goods(m.get("world")) if m.get("world") else None
        lines = TT.with_generations(m["lineages"], m.get("tree"))
        _C["in"] = (m, lines, present, goods, TT.landmass_of(RUN, m))
    return _C["in"]


def one(job):
    var, seed = job
    m, lines, present, goods, lm = inputs()
    kw = {}
    if var == "main":
        spec = importlib.util.spec_from_file_location("planet.lineages.tt_main", SCR / "tt_main.py")
        M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
        T = M.load()
    else:
        from planet.lineages import techtree as M
        T = M.load()
        T["defaults"]["own_floor"] = var != "wait"; T["defaults"]["regions"] = var.startswith("regions")
        if var.startswith("regions"):
            kw["landmass"] = lm
        if var == "regionsB" or var == "regionsBt":
            T["defaults"]["contact_arms"] = "B" if var == "regionsB" else "BT"
            from planet.lineages.techspread import town_footprint
            kw["towns"] = town_footprint(RUN)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tt = M.build(lines, m.get("contacts"), m.get("present"), present, goods, m.get("mode", "fantasy"), m.get("era"), seed, T=T,
                     gods_mode=m.get("gods_mode", "faith_made"), **kw)
    return job, {p: {t: (kn.get(t) or [None, None])[:2] for t in W} for p, kn in tt["known"].items()}


if __name__ == "__main__":
    base = int(json.loads((RUN / "run.json").read_text())["meta"].get("try_seed") or 0)
    seeds = list(range(base, base + N))
    with Pool(JOBS) as P:
        r = P.map(one, [(v, s) for v in VARS for s in seeds])
    Path(OUT).write_text(json.dumps({"run": RUN.name, "seeds": seeds, "vars": VARS,
                                     "rows": [{"var": v, "seed": s, "known": K} for (v, s), K in r]}))
    print("wrote", OUT)
