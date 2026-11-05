"""Round 2 measures (PW-1471/1461): a stored run's tree over N draws under several variants (read-only on the run).
argv: run_dir n_draws out.json jobs variants
A variant is `main` (main's techtree.py + toml at 01b03c34, saved as ../round1/../tt_main.py in the scratch dir: TT_MAIN env) or
dot-joined tokens over this branch's tree, every switch off by default:
  R   region learners on (landmass from the run)       F   D55's floor on (own_floor)
  aX  region_mkm2 = X (a_5: 0.5)     pN  anchor_peers = N                                  B   arm B (town network)     T   arm B weighted by trade (contact_arms BT)
  Y   tallies' earliest_kyr 44 (its source's date; 45 left its band unused)
  def this branch's shipped defaults, untouched (as the toml says)"""
import importlib.util, json, os, sys, warnings
from multiprocessing import Pool
from pathlib import Path
import numpy as np

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
        spec = importlib.util.spec_from_file_location("planet.lineages.tt_main", os.environ["TT_MAIN"])
        M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
        T = M.load()
    else:
        from planet.lineages import techtree as M
        T = M.load()
        D = T["defaults"]
        tok = var.split(".")
        if "def" not in tok:
            D["own_floor"] = "F" in tok; D["regions"] = "R" in tok; D["contact_arms"] = ""
            for t in tok:
                if t.startswith("p") and t[1:].isdigit():
                    D["anchor_peers"] = int(t[1:])
                if t.startswith("a") and t[1:].replace("_", "").isdigit():
                    D["region_mkm2"] = float(t[1:].replace("_", "."))
            if "B" in tok or "T" in tok:
                D["contact_arms"] = "BT" if "T" in tok else "B"
        if "Y" in tok:  # (tallies dated as their cited source, d'Errico et al. 2012: ~44 kyr, so the band applies)
            T["techs"]["tallies"]["earliest_kyr"] = 44
        if D.get("regions"):
            kw["landmass"] = lm
        if set(str(D.get("contact_arms") or "")) & {"B", "E"}:
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
