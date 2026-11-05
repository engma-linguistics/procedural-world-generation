"""A humans_only peoples run on 899985 (scratch data root via PLANET_DATA), polities in the history off. argv: seed tag"""
import os, sys, time
from pathlib import Path
ROOT = Path(os.environ["PYTHONPATH"].split(":")[0])
sys.path.insert(0, str(ROOT / "tools"))
import planet
from planet.lineages import spec as SP
from planet.lineages import run as LR
import peoples_robust as PR

seed, tag = int(sys.argv[1]), sys.argv[2]
raw, _ = PR.authored(ROOT / "tools/peoples_robust/trees/humans_only.toml")
raw = PR.with_seed(raw, seed) if hasattr(PR, "with_seed") else raw
tree = SP.parse(raw, None)
tree.seed = seed
t0 = time.time()
out = LR.run(os.environ.get("WORLD", "899985"), tree, 1, None, 30.0, f"l200-{tag}", progress=lambda f, msg: None)
print("run", out.name, round(time.time() - t0, 1), "s", flush=True)
