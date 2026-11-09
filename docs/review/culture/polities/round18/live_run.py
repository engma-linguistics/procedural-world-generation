"""Lane 248: one peoples run in the lane's scratch data root, polities in the history on or off, languages skipped (as lane 241's
runner). argv: tree seed live(on|off) tag kyr world [arm]. arm: base (the code as is), mem (MEMORY flag on, when the code has it)."""
import sys
import time

from planet.lineages.history import params as HP
from planet.lineages.history import polity_live as PLV
from planet.lineages import run as LR
import planet.language.run as LANG


def _skip(out):
    raise RuntimeError("skipped by lane 248's runner")


LANG.write = _skip
tree_name, seed, live, tag, kyr, world = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6]
arm = sys.argv[7] if len(sys.argv) > 7 else "base"
HP.POLITIES_LIVE = live == "on"
if arm != "base":
    for a in arm.split("+"):
        name, _, val = a.partition("=")
        setattr(PLV, name, float(val) if val else True)
        print("ARM", name, getattr(PLV, name), flush=True)
tree = LR.load_tree(tree_name, None)
tree.seed = seed
t0 = time.time()
out = LR.run(world, tree, 1, None, kyr, f"l248-{tag}", progress=lambda f, msg: None)
print("RUN", tag, out, round(time.time() - t0, 1), "s", flush=True)
