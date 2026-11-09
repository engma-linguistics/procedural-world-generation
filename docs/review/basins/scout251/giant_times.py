"""giant_times.py DATA_ROOT NAME...: the frames (t, largest lake Mkm2) with a lake over 1 Mkm2 in each named run."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools import health as Hh  # noqa: E402

root = Path(sys.argv[1])
ids = {json.loads((d / "run.json").read_text()).get("name"): d for d in (root / "runs").iterdir() if (d / "run.json").exists()}
for name in sys.argv[2:]:
    r = Hh.measure_run(ids[name])
    g = [(f["t"], f["lake_max_mkm2"]) for f in r["frames"] if f["t"] > 200 and f["lake_max_mkm2"] > 1]
    print(name, " ".join(f"{t:.0f}:{v:.2f}" for t, v in g), flush=True)
