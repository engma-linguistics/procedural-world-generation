"""Lane 234: one peoples run on world 899985 (L7) in the lane's scratch data root, polities in the history on or off, no invasion rows.
argv: tree(dnd|path) seed live(on|off) tag. Prints the run dir."""
import os, sys, time
import planet
from planet.lineages.history import params as HP
from planet.lineages import run as LR
tree_name, seed, live, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
HP.POLITIES_LIVE = live == "on"
tree = LR.load_tree(tree_name, None)
tree.seed = seed
t0 = time.time()
out = LR.run(os.environ.get("WORLD", "899985"), tree, 1, None, 30.0, f"l234-{tag}", progress=lambda f, msg: None)
print("RUN", tag, out, round(time.time() - t0, 1), "s", flush=True)
