"""Round 13 (lane 215, PW-1513): round 12's live_run.py with the REVOLT switch (D67 B). A peoples run in a scratch data root
(PLANET_DATA), polities in the history on, round 10's invasion rows (unchanged), world 899985. argv: tree seed revolt(on|off) tag."""
import os
import sys
import time

import planet
print("planet from", planet.__file__, flush=True)
from planet.lineages.history import params as HP  # noqa: E402
from planet.lineages.history import polity_live as PL  # noqa: E402
from planet.lineages import run as LR  # noqa: E402

S = lambda i, a, b, f, t: {"id": i, "who": {"people": a}, "whom": {"people": b}, "from_kyr": f, "to_kyr": t, "strength": "strong"}  # noqa: E731
ROWS = {  # (round 10's rows, as round12/live_run.py)
    "dnd": [S("orc_human", "orc", "human", 2.0, 0.3), S("hob_elf", "hobgoblin", "elf", 1.5, 0.5),
            S("dwarf_hob", "dwarf", "hobgoblin", 2.0, 0.3), S("leonin_human", "leonin", "human", 2.0, 0.3),
            S("human_kenku", "human", "kenku", 1.5, 0.3), S("elf_orc", "elf", "orc", 2.0, 0.3)],
}

tree_name, seed, rv, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
HP.POLITIES_LIVE = True
PL.INVASIONS = ROWS[tree_name]
PL.REVOLT = rv == "on"
tree = LR.load_tree(tree_name, None)
tree.seed = seed
t0 = time.time()
out = LR.run(os.environ.get("WORLD", "899985"), tree, 1, None, 30.0, f"l215-{tag}", progress=lambda f, msg: None)
print("run", out.name, round(time.time() - t0, 1), "s", flush=True)
