"""A peoples run on 899985 (scratch data root via PLANET_DATA), polities in the history on or off. argv: tree seed on|off [arms|-] tag"""
import os, sys, time
import planet
print("planet from", planet.__file__, flush=True)
from planet.lineages.history import params as HP
from planet.lineages import techtree as TT
from planet.lineages import run as LR

tree_name, seed, sw = sys.argv[1], int(sys.argv[2]), sys.argv[3]
arms = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else None
tag = sys.argv[5]
HP.POLITIES_LIVE = sw == "on"
if arms:  # (a test override of the tree's default arms)
    _load = TT.load
    def load(path=None):
        T = _load(path)
        T["defaults"]["contact_arms"] = arms
        return T
    TT.load = load
tree = LR.load_tree(tree_name, None)
tree.seed = seed
t0 = time.time()
out = LR.run(os.environ.get("WORLD", "899985"), tree, 1, None, 30.0, f"l196-{tag}", progress=lambda f, msg: None)
print("run", out.name, round(time.time() - t0, 1), "s", flush=True)
