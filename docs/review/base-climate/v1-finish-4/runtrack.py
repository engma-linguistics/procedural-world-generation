"""A stored run's keyframes (every 4 Myr, the climate updates) as a tools/ice_criteria 'track', for passrate.py:
writes OUT_DIR/seed<seed>_L<level>.json.gz per run. Read only.
Usage (repo root, PLANET_DATA set): uv run python docs/review/base-climate/v1-finish-4/runtrack.py OUT_DIR RUN [RUN ...]"""
import os
import sys

sys.path[:0] = [os.getcwd()]
import planet  # noqa: E402,F401
import gzip  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

from planet import timeline as T  # noqa: E402

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
for ref in sys.argv[2:]:
    run = json.loads((T.find_run(ref) / "run.json").read_text())
    m = run["meta"]
    track = [{"t": f["t"], "ice": f["stats"]["sea_ice_m"], "tect": f["stats"]["sea_tect_m"],
              "dT": f["stats"]["global_temp_c"] - 14.5, "ice_frac": f["stats"]["ice_pct"],
              "land": f["stats"]["land_pct"]} for f in run["frames"]]
    p = out / f"seed{m['seed']}_L{m['level']}.json.gz"
    with gzip.open(p, "wt") as fh:
        json.dump({"run": run["id"], "seed": m["seed"], "level": m["level"], "track": track}, fh)
    print(ref, m["seed"], m["level"], len(track), "frames ->", p)
