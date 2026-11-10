"""Forked screens with a real null (PW-1618).

A forked screen spins one state to the fork (200 Myr) with main's code, then continues it to the end with main and with
a candidate, several draws each, and asks whether the candidate's measures sit outside main's draw-to-draw spread.
Scouts 251/260/261 drew with a 1e-5 C climate offset after the fork: on seed 77 L6 three of main's four draws were the
same trajectory, so main's "spread" was no null at all. The draws here perturb the state or the noise, so they diverge:

  rng K    the per-step random streams (np.random.default_rng([seed, step_no, ...])) get the extra key K after the
           fork: a different future of drift, volcanism and rifting from the same state (the strong null: what the
           state at the fork pins down, and what it doesn't)
  elev K   the crust thickness of every plate cell (so the elevation) times 1 + amp x N(0, 1) at the fork (amp
           default 1e-12, a few thousand ulps: far below any physical meaning; the chaos null)
  offset K the old draw: climate_offset = K x 1e-5 C (kept to compare; weak)
  base 0   no perturbation (= every kind's draw 0)
and a code-change null arm:
  --fp-null  main's code with a no-op that changes the floating-point rounding: the elevation surface.erode sees
             each step is (elev + 1000) - 1000 (identical in exact arithmetic; last-bit changes, as reordering a sum
             does). A candidate's shift no bigger than --fp-null's is no evidence of an effect.

Subcommands (CODE = a frozen copy of the code: a directory holding planet/; data root = $PLANET_DATA, scratch):
  spin CODE CKPT --seed S --level L [--fork 200] [--myr 400]          main spun to the fork, the state pickled
  cont CODE CKPT --seed S --level L [--myr 400] --arm A --kind K --draw D [--amp 1e-12] [--fp-null]
                                                                      one continuation, run named s{S}_{A}_{K}{D}
  queue JOBS [--parallel 2] [--max-load 30] [--pids FILE]             each line of JOBS = this tool's arguments;
                                                                      a job starts only below the 1-min load
  measure DATA_ROOT [--fork 200] [--out measure.json]                 health's measures of each finished run, frames
                                                                      after the fork (+ discharge to the sea)
  spread MEASURE_JSON [--null main fpnull] [--cand ARM]               per seed: the null's range (every draw of the
                                                                      null arms) and each candidate draw against it
The measures: inland median % of land (p10-p90), lakes % of land (mean), largest lake median Mkm2, giant-lake frames %
(largest > 1 Mkm2; also over t >= 300), discharge to the sea (mean, k m3/s), and div_t: the first keyframe at which a
run differs from its seed's base draw (None: never: that draw is no draw). README: docs/coordination.md, "Forked
screens".
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import shlex
import subprocess
import sys
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _import_code(code: str):
    sys.path.insert(0, str(Path(code).resolve()))
    import planet
    assert Path(planet.__file__).resolve().is_relative_to(Path(code).resolve()), planet.__file__
    return planet


def spin(a):
    _import_code(a.code)
    from planet.grid import build_grid
    from planet.tectonics import Params, Simulation
    t0 = time.time()
    sim = Simulation(build_grid(a.level), a.seed, Params(run_end=a.myr), 2.0)
    sim.run(a.fork)
    Path(a.path).write_bytes(zlib.compress(pickle.dumps(sim.state(), protocol=5), 1))
    print(f"spin s{a.seed} L{a.level} to {sim.t:g} in {time.time() - t0:.0f} s", flush=True)


def _salt_streams(salt: int, sim_ref: dict):
    """np.random.default_rng([seed, step_no, ...]) -> [..., 1_000_003 + salt] for the run's per-step streams (the
    run-constant ones, [seed, 7/11/13], are left: the fork is past step 13, so step_no never collides)."""
    import numpy as np
    orig = np.random.default_rng

    def rng(seed=None, *a, **kw):
        sim = sim_ref.get("sim")
        if (sim is not None and isinstance(seed, (list, tuple)) and len(seed) >= 2 and seed[0] == sim.seed
                and seed[1] == sim.step_no):
            seed = [*seed, 1_000_003 + salt]
        return orig(seed, *a, **kw)
    np.random.default_rng = rng


def _fp_null():
    """The code-change null: surface.erode sees (elev + 1000) - 1000 (a no-op in exact arithmetic)."""
    from planet import surface
    orig = surface.erode

    def erode(grid, elev, *a, **kw):
        return orig(grid, (elev + 1000.0) - 1000.0, *a, **kw)
    surface.erode = erode


def cont(a):
    _import_code(a.code)
    import numpy as np
    from planet import timeline as T
    from planet.grid import build_grid
    from planet.tectonics import Params, Simulation
    t0 = time.time()
    state = pickle.loads(zlib.decompress(Path(a.path).read_bytes()))
    for n in Simulation.STATE:
        state.setdefault(n, None)  # (a candidate's new state: set at its next update)
    params = Params(run_end=a.myr, climate_offset=a.draw * 1e-5 if a.kind == "offset" else 0.0)
    ref = {}
    if a.kind == "elev" and a.draw:
        th = state["plates"].thick
        rng = np.random.default_rng([a.seed, 4242, a.draw])
        th *= 1.0 + a.amp * rng.standard_normal(th.shape)
    if a.kind == "rng" and a.draw:
        _salt_streams(a.draw, ref)
    if a.fp_null:
        _fp_null()
    sim = Simulation.from_state(build_grid(a.level), a.seed, params, 2.0, state)
    ref["sim"] = sim
    T.Simulation = lambda *args, **kw: sim
    name = f"s{a.seed}_{a.arm}_{a.kind}{a.draw}"
    out = T.simulate(a.seed, a.level, a.myr, 2.0, 4.0, name, params, checkpoint_every=0)
    print(f"cont {name}: {out.name} in {time.time() - t0:.0f} s", flush=True)


def _load() -> float:
    return float(Path("/proc/loadavg").read_text().split()[0])


def queue(a):
    """Runs JOBS' lines (this tool's arguments) a.parallel at a time, each started only while the 1-min load is
    below a.max_load; each job's log next to JOBS (logs/NAME.log); PIDs appended to a.pids."""
    lines = [ln.strip() for ln in Path(a.jobs).read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    logs = Path(a.jobs).parent / "logs"
    logs.mkdir(exist_ok=True)
    live = []
    for i, ln in enumerate(lines):
        while True:
            live = [p for p in live if p.poll() is None]
            if len(live) < a.parallel and _load() < a.max_load:
                break
            time.sleep(20)
        log = logs / f"job{i:03d}.log"
        with open(log, "w") as fh:
            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), *shlex.split(ln)], stdout=fh,
                                 stderr=subprocess.STDOUT)
        live.append(p)
        if a.pids:
            with open(a.pids, "a") as fh:
                fh.write(f"{p.pid} {ln}\n")
        print(f"{time.strftime('%T')} start {i} pid {p.pid}: {ln}", flush=True)
        time.sleep(10)
    for p in live:
        p.wait()
    print(f"{time.strftime('%T')} queue done", flush=True)


def measure(a):
    sys.path.insert(0, str(ROOT))
    import numpy as np
    from tools import health as Hh
    from planet.hydrology import discharge

    Hh.MEASURE_LAYERS = tuple(Hh.MEASURE_LAYERS) + tuple(k for k in ("flow",) if k not in Hh.MEASURE_LAYERS)
    mf = Hh.measure_frame

    def measure_frame(grid, L, stats):
        out = mf(grid, L, stats)
        land = Hh.is_land(np.asarray(L["elevation"], float), grid=grid)
        down = np.asarray(L["downstream"]).astype(np.int64)
        mouth = land & (down >= 0) & ~land[np.maximum(down, 0)]
        out["sea_q"] = float(discharge(grid, np.asarray(L["flow"], float)[mouth]).sum())  # m3/s into the sea
        return out
    Hh.measure_frame = measure_frame

    root = Path(a.root)
    rows, series = {}, {}
    for rd in sorted((root / "runs").iterdir()):
        try:
            head = json.loads((rd / "run.json").read_text())
        except Exception:
            continue
        if head.get("status") == "running" or "frames" not in head:
            continue
        r = Hh.measure_run(rd)
        fr = [f for f in r["frames"] if f["t"] > a.fork + 1e-6 and f["inland_pct"] is not None]
        v = np.array([f["inland_pct"] for f in fr])
        mx = np.array([f["lake_max_mkm2"] for f in fr])
        late = np.array([f["lake_max_mkm2"] for f in fr if f["t"] >= 300])
        series[head["name"]] = [(f["t"], f["inland_pct"], f["land_pct"], f["lake_pct"]) for f in fr]
        rows[head["name"]] = dict(id=rd.name, n=len(fr), inland=float(np.median(v)), p10=float(np.percentile(v, 10)),
                                  p90=float(np.percentile(v, 90)), lakes=float(np.mean([f["lake_pct"] for f in fr])),
                                  lmax=float(np.median(mx)), giant=float(100 * (mx > 1).mean()),
                                  giant300=float(100 * (late > 1).mean()) if len(late) else 0.0,
                                  sea_q=float(np.mean([f["sea_q"] for f in fr])),
                                  secs=head["meta"].get("generated_in_s"))
    for name, d in rows.items():  # div_t: the first frame that differs from the seed's base draw (same arm)
        s, arm, _ = name.split("_", 2)
        own = f"{s}_{arm}_base0"
        base = series.get(own) if name != own and own in series else series.get(f"{s}_main_base0")
        d["div_t"] = None
        if base:
            for x, y in zip(series[name], base):
                if x != y:
                    d["div_t"] = x[0]
                    break
    for k in sorted(rows):
        d = rows[k]
        print(f"{k:20s} {d['id']} n={d['n']} inland {d['inland']:.1f} ({d['p10']:.1f}-{d['p90']:.1f}) lakes "
              f"{d['lakes']:.2f}% lmax {d['lmax']:.2f} giant {d['giant']:.1f}% (>=300 {d['giant300']:.1f}%) "
              f"sea {d['sea_q'] / 1e3:.0f}k div_t {d['div_t']} {d['secs']} s")
    Path(a.out).write_text(json.dumps(rows, indent=1))


KEYS = (("inland", "inland median %", 1), ("lakes", "lakes % of land", 2), ("giant", "giant-lake frames %", 1),
        ("giant300", "giant >= 300 %", 1), ("sea_q", "to the sea, k m3/s", -3))


def _fmt(v, nd):
    return f"{v / 1e3:.0f}" if nd < 0 else f"{v:.{nd}f}"


def spread(a):
    rows = json.loads(Path(a.json).read_text())
    seeds = sorted({k.split("_")[0] for k in rows}, key=lambda s: int(s[1:]))
    print("| seed | arm | draws | " + " | ".join(t for _, t, _ in KEYS) + " |")
    print("|---|---|---|" + "---|" * len(KEYS))
    for s in seeds:
        null = {k: v for k, v in rows.items() if k.startswith(s + "_") and k.split("_")[1] in a.null}
        for arm in [*a.null, *a.cand]:
            mine = {k: v for k, v in rows.items() if k.startswith(f"{s}_{arm}_")}
            if not mine:
                continue
            cells = []
            for key, _, nd in KEYS:
                vals = [v[key] for v in mine.values()]
                lo, hi = min(vals), max(vals)
                cell = f"{_fmt(lo, nd)}-{_fmt(hi, nd)}" if len(vals) > 1 else _fmt(lo, nd)
                if arm in a.cand and null:
                    nv = [v[key] for v in null.values()]
                    out = sum(x < min(nv) - 1e-9 or x > max(nv) + 1e-9 for x in vals)
                    cell += f" ({out}/{len(vals)} out)" if out else " (in)"
                cells.append(cell)
            nd_ = sum(v["div_t"] is None for k, v in mine.items() if k != f"{s}_{arm}_base0" or arm != "main")
            dr = f"{len(mine)}" + (f", {nd_} never diverged" if nd_ else "")
            print(f"| {s} | {arm} | {dr} | " + " | ".join(cells) + " |")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    for m in ("spin", "cont"):
        p = sub.add_parser(m)
        p.add_argument("code")
        p.add_argument("path")
        p.add_argument("--seed", type=int, required=True)
        p.add_argument("--level", type=int, required=True)
        p.add_argument("--myr", type=float, default=400.0)
        if m == "spin":
            p.add_argument("--fork", type=float, default=200.0)
        else:
            p.add_argument("--arm", default="main")
            p.add_argument("--kind", choices=("base", "rng", "elev", "offset"), default="rng")
            p.add_argument("--draw", type=int, default=0)
            p.add_argument("--amp", type=float, default=1e-12)
            p.add_argument("--fp-null", action="store_true")
    p = sub.add_parser("queue")
    p.add_argument("jobs")
    p.add_argument("--parallel", type=int, default=2)
    p.add_argument("--max-load", type=float, default=30.0)
    p.add_argument("--pids")
    p = sub.add_parser("measure")
    p.add_argument("root")
    p.add_argument("--fork", type=float, default=200.0)
    p.add_argument("--out", default="measure.json")
    p = sub.add_parser("spread")
    p.add_argument("json")
    p.add_argument("--null", nargs="+", default=["main"])
    p.add_argument("--cand", nargs="*", default=[])
    a = ap.parse_args()
    {"spin": spin, "cont": cont, "queue": queue, "measure": measure, "spread": spread}[a.mode](a)


if __name__ == "__main__":
    os.environ.setdefault("NUMBA_NUM_THREADS", "4")
    main()
