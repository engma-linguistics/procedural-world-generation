"""Lane 158: option A's check. Continues a lane 144 fork state (300 Myr, code l144/code/main = 4abc1707) with the
frozen yardstick pinned: the sink reference rescaled so y = ln(src ref / sink ref) equals Y (the 36-run mean, 1.316),
the source reference kept. Everything else as fm. Writes OUT/seed<S>_L6.json.gz (tools/ice_diag.py's layout).
Nothing under planet/ is changed.  usage: pin.py CODE_DIR FORK_BASE OUT_DIR Y"""
import gzip, json, math, pickle, sys, time, zlib
from pathlib import Path

code, base, out, Y = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), float(sys.argv[4])
sys.path.insert(0, str(Path(code).resolve()))
import planet  # noqa: F401,E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402
from planet.tectonics.diag import Recorder  # noqa: E402

meta = json.loads(gzip.open(f"{base}.json.gz", "rt").read())
state = pickle.loads(zlib.decompress(Path(f"{base}.ckpt").read_bytes()))
sim = Simulation.from_state(build_grid(meta["level"]), meta["seed"], Params(**meta["params"]), meta["dt"], state)
y0 = math.log(sim.refs[0] / sim.refs[1])
sim.refs = sim.refs.copy()
sim.refs[1] = sim.refs[0] / math.exp(Y)
print(f"y {y0:.4f} -> {math.log(sim.refs[0] / sim.refs[1]):.4f}", flush=True)
rec = Recorder()
rec.steps, rec.updates = meta["steps"], meta["updates"]
sim.diag = rec
t0 = time.time()


def on_step(s):
    s.diag.step(s)
    if int(s.t) % 100 == 0 and abs(s.t - round(s.t)) < 1e-9:
        print(f"  {s.t:g} Myr {time.time() - t0:.0f} s dT {s.dT:+.2f}", flush=True)


sim.run(meta["myr"], on_step)
out.mkdir(parents=True, exist_ok=True)
d = {"seed": meta["seed"], "myr": meta["myr"], "level": meta["level"], "params": meta["params"],
     "pin": {"y_from": y0, "y_to": Y}, "seconds": round(time.time() - t0), **rec.as_dict()}
with gzip.open(out / f"seed{meta['seed']}_L6.json.gz", "wt") as f:
    json.dump(d, f)
print("done", out)
