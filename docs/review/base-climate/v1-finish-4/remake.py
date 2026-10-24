"""Re-run `planet make`'s chain after the simulation on an existing run (PW-736: the showcase's time zooms were made
before the time zoom's margin fix): its time zoom, finished world, highlights and zooms, as `planet make --seed SEED
--level LEVEL` would at the same representative moment, via make.make's resume state (the run reused, not
re-simulated); then the world's resource and coast layers (`planet resources`, `planet coast`). Prints make's
JSON. Usage (repo root, PLANET_DATA set): uv run python docs/review/base-climate/v1-finish-4/remake.py RUN STATE.json"""
import os
import sys

sys.path[:0] = [os.getcwd()]
import planet  # noqa: E402,F401
import json  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

from planet import highlights as H, make as M, timeline as T  # noqa: E402

run_ref, state = sys.argv[1], Path(sys.argv[2])
run = json.loads((T.find_run(run_ref) / "run.json").read_text())
m = run["meta"]
req = {"seed": m["seed"], "level": m["level"]}
spec = M.parse_make_request(req)
t = H.representative_time(run["frames"], plant_groups=m.get("plant_groups"))
state.write_text(json.dumps({"spec": spec, "out": {"run": run["id"], "t_myr": t}}))
out = M.make(req, lambda f, msg: print(f"[{100 * f:3.0f}%] {msg}", flush=True), state=state, resume=True)
assert out["run"] == run["id"], out
for what in ("resources", "coast"):
    subprocess.run([sys.executable, "-m", "planet", what, out["world"]], check=True)
print(json.dumps(out))
