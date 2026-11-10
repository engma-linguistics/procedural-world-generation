"""planet lineages WORLD --tree everyone --tries 1, without the languages pass (lane 277: L7 cost). Usage: run_nolang.py WORLD NAME [KEY=VALUE...]"""
import json, sys, time
from planet.lineages import run as LR
from planet.lineages.history import params as HP

world, name = sys.argv[1], sys.argv[2]
for kv in sys.argv[3:]:
    k, v = kv.split("=", 1)
    assert hasattr(HP, k), k
    setattr(HP, k, json.loads(v))
    print(f"  history.params.{k} = {getattr(HP, k)!r}", flush=True)
t0 = time.time()
tree = LR.load_tree("everyone")
out = LR.run(world, tree, 1, None, 30.0, name, progress=lambda f, msg: print(f"  {100 * f:3.0f}% {msg} [{time.time() - t0:.0f}s]", flush=True),
             climate_every=2.0, split=True, languages=False)
print("RUN", out, f"{time.time() - t0:.0f}s", flush=True)
