"""usage (paired_fork.sh drives it; docs/review/base-climate/fork-judge/round1.md):
  fork.py spin CODE_DIR OUT_DIR --seed S [--fork 300] [--myr 1000] [--level 6] [--set k=v ...]
  fork.py cont CODE_DIR FORK_BASE OUT_DIR [--set k=v ...] [--fill-missing]
  fork.py yard ROOT MAIN_FORK_DIR CAND_FORK_DIR

The forked paired judge's simulation step, with the code in CODE_DIR (a frozen copy, as paired.sh's). Nothing under
planet/ is changed and nothing goes to the store: it is tools/ice_diag.py's run split in two at a fork time.

spin  runs CODE_DIR's simulation of tools/ice_diag.py's draw (seed, level, --set; run_end = --myr) with the diag
      Recorder on to --fork Myr (at or after earth.REF_FREEZE, so the carbon cycle's references are frozen), and writes
      OUT_DIR/seed<S>_L<l>_at<T>.ckpt (zlib pickle of Simulation.state()) and .json.gz beside it (the run's parameters,
      the Recorder's records so far, the frozen references and the spin-up's w_pot).
cont  continues FORK_BASE (the path without .ckpt / .json.gz) with CODE_DIR's code (which may be another arm's) to the
      run's end, with --set applied on top of the spin's parameters (only from the fork on), and writes
      OUT_DIR/seed<S>_L<l>.json.gz in tools/ice_diag.py's layout (what tools/judge.py paired and tools/hard_bar.py read): the spin's
      records, then the continuation's. A run continued with the spin's own code and no --set is bit-identical to the
      unforked ice_diag run (Simulation.state() is complete: tests/test_state.py; checked in tests/test_fork_judge.py).
      If CODE_DIR's Simulation.STATE has names the spin's state lacks (a candidate that adds state), it stops, unless
      --fill-missing: then those names take a fresh CODE_DIR simulation's t=0 values (listed in the output's "fork").
yard  the yardstick part the fork does not measure: for each draw with a spin of both arms (MAIN_FORK_DIR and
      CAND_FORK_DIR under ROOT, each arm's own code spun to the fork), the frozen references' ln source, ln sink, their
      ratio y = ln(src ref / sink ref) and the spin-up's supply-weighted reference plant factor w_pot, cand - main.
"""
import argparse
import gzip
import json
import pickle
import sys
import time
import zlib
from pathlib import Path


def _code(code_dir):
    sys.path.insert(0, str(Path(code_dir).resolve()))
    import planet  # noqa: F401  (first: its thread caps)
    from planet.grid import build_grid
    from planet.tectonics import Params, Simulation, earth
    from planet.tectonics.diag import Recorder
    from tools import ice_diag
    return build_grid, Params, Simulation, earth, Recorder, ice_diag


def _progress(tag, t0):
    def on_step(s):
        s.diag.step(s)
        if int(s.t) % 100 == 0 and abs(s.t - round(s.t)) < 1e-9:
            print(f"  {tag} {s.t:g} Myr  {time.time() - t0:.0f} s  ice {s.sea_ice:.0f} m  dT {s.dT:+.1f}", flush=True)
    return on_step


def _ref_record(sim, steps, fork):
    """The frozen references and the reference plants' factor over the spin-up's last REF_MYR (as the reference
    weights them, roughly: a plain mean)."""
    src, sink = (float(x) for x in sim.refs)
    pot = [r["w_pot"] for r in steps if r.get("w_pot") is not None and r["t"] > fork - 100.0 - 1e-9]
    return {"src_ref": src, "sink_ref": sink, "ln_src_ref": float(_ln(src)), "ln_sink_ref": float(_ln(sink)),
            "y": float(_ln(src) - _ln(sink)), "w_pot": (sum(pot) / len(pot)) if pot else None}


def _ln(x):
    import math
    return math.log(x)


def spin(a):
    build_grid, Params, Simulation, earth, Recorder, ice_diag = _code(a.code)
    if a.fork < earth.REF_FREEZE:
        sys.exit(f"--fork {a.fork:g} is before earth.REF_FREEZE ({earth.REF_FREEZE:g}): the references are still learning")
    sets = {"run_end": float(a.myr), **ice_diag.parse_sets(a.set)}  # (as ice_diag.run)
    sim = Simulation(build_grid(a.level), a.seed, Params(**sets), 2.0)
    sim.diag = Recorder()
    tag, t0 = f"seed{a.seed}_L{a.level}", time.time()
    sim.run(a.fork, _progress(tag, t0))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    base = out / f"{tag}_at{a.fork:g}"
    meta = {"seed": a.seed, "myr": a.myr, "level": a.level, "dt": sim.dt, "fork": float(sim.t), "params": sets,
            "code": str(Path(a.code).resolve()), "seconds": round(time.time() - t0),
            "refs": _ref_record(sim, sim.diag.steps, sim.t), **sim.diag.as_dict()}
    ck, js = Path(f"{base}.ckpt.tmp"), Path(f"{base}.json.gz.tmp")
    ck.write_bytes(zlib.compress(pickle.dumps(sim.state(), protocol=5), 1))
    with gzip.open(js, "wt") as f:
        json.dump(meta, f)
    js.rename(f"{base}.json.gz")
    ck.rename(f"{base}.ckpt")  # (last: the .ckpt's presence means the spin is complete)
    print(f"{tag}: spun to {sim.t:g} Myr in {meta['seconds']} s -> {base}.ckpt; y {meta['refs']['y']:.4f}")


def cont(a, summary=False):
    build_grid, Params, Simulation, earth, Recorder, ice_diag = _code(a.code)
    base = Path(a.fork_base)
    meta = json.loads(gzip.open(f"{base}.json.gz", "rt").read())
    state = pickle.loads(zlib.decompress(Path(f"{base}.ckpt").read_bytes()))
    after = ice_diag.parse_sets(a.set)
    sets = {**meta["params"], **after}
    params, grid = Params(**sets), build_grid(meta["level"])
    missing = [n for n in Simulation.STATE if n not in state]
    if missing and not a.fill_missing:
        sys.exit(f"this code's Simulation.STATE has names the fork's state lacks: {missing} (--fill-missing takes them "
                 "from a fresh simulation's t=0)")
    if missing:
        fresh = Simulation(grid, meta["seed"], params, meta["dt"])
        state = {**{n: getattr(fresh, n) for n in missing}, **state}
    sim = Simulation.from_state(grid, meta["seed"], params, meta["dt"], state)
    rec = Recorder()
    rec.steps, rec.updates = meta["steps"], meta["updates"]
    sim.diag = rec
    tag, t0 = f"seed{meta['seed']}_L{meta['level']}", time.time()
    print(f"{tag}: continuing from {sim.t:g} Myr ({base}) with {Path(a.code).resolve()}; after the fork: {after}", flush=True)
    sim.run(meta["myr"], _progress(tag, t0))
    d = {"seed": meta["seed"], "myr": meta["myr"], "level": meta["level"], "params": sets,
         "seconds": meta["seconds"] + round(time.time() - t0), **rec.as_dict(),
         "fork": {"t": meta["fork"], "from": str(base), "spin_code": meta["code"], "code": str(Path(a.code).resolve()),
                  "sets_after": after, "filled": missing, "refs": meta["refs"]}}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{tag}.json.gz"
    with gzip.open(path, "wt") as f:
        json.dump(d, f)
    if summary:  # (as ice_diag's main, into the log; it needs a long run)
        ice_diag.summary(path)
    return path


def yard(a):
    import numpy as np
    root = Path(a.root)
    rows = []
    for pm in sorted((root / a.main).glob("*/seed*_at*.json.gz")):
        pc = root / a.cand / pm.parent.name / pm.name
        if not pc.exists():
            continue
        m, c = (json.loads(gzip.open(p, "rt").read())["refs"] for p in (pm, pc))
        rows.append((pm.parent.name, pm.name.split("_")[0][4:], m, c))
    print(f"{'draw':>16} {'seed':>7} {'y main':>7} {'dy':>7} {'dln src':>8} {'dln sink':>8} {'w_pot':>6} {'dln w_pot':>9}")
    for d, s, m, c in rows:
        dw = np.log(c["w_pot"] / m["w_pot"]) if m["w_pot"] and c["w_pot"] else float("nan")
        print(f"{d:>16} {s:>7} {m['y']:7.4f} {c['y'] - m['y']:+7.4f} {c['ln_src_ref'] - m['ln_src_ref']:+8.4f} "
              f"{c['ln_sink_ref'] - m['ln_sink_ref']:+8.4f} {m['w_pot'] or float('nan'):6.4f} {dw:+9.4f}")
    if rows:
        dy = np.array([c["y"] - m["y"] for _, _, m, c in rows])
        print(f"{len(rows)} draws: dy median {np.median(dy):+.4f}, mean {dy.mean():+.4f}, sd {dy.std(ddof=1) if len(dy) > 1 else 0:.4f}"
              " (y = ln(source ref / sink ref); higher y = a colder late run, round1 8a of lane 140d)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("spin")
    s.add_argument("code")
    s.add_argument("out")
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--fork", type=float, default=300.0)
    s.add_argument("--myr", type=float, default=1000.0)
    s.add_argument("--level", type=int, default=6)
    s.add_argument("--set", nargs="*", default=[])
    c = sub.add_parser("cont")
    c.add_argument("code")
    c.add_argument("fork_base")
    c.add_argument("out")
    c.add_argument("--set", nargs="*", default=[])
    c.add_argument("--fill-missing", action="store_true")
    y = sub.add_parser("yard")
    y.add_argument("root")
    y.add_argument("main")
    y.add_argument("cand")
    a = ap.parse_args()
    {"spin": spin, "cont": lambda a: cont(a, summary=True), "yard": yard}[a.cmd](a)


if __name__ == "__main__":
    main()
