"""Lane 123: tools/health.measure_run on the L6 sanity runs: late dT (last 200 Myr mean), arid %, trees %, NPP."""
import glob
import os
import sys
from pathlib import Path

sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6")
import numpy as np

SC = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l123"
for root in ("data_base", "data_cand"):
    os.environ["PLANET_DATA"] = f"{SC}/{root}"
    from planet import store as S
    S.set_root(Path(f"{SC}/{root}"))
    from tools import health as HE
    for d in sorted(glob.glob(f"{SC}/{root}/runs/*/")):
        r = HE.measure_run(Path(d))
        fr = r.get("frames") or r.get("measures") or []
        late = [f for f in fr if f["t"] >= max(x["t"] for x in fr) - 200]
        mean = lambda k: float(np.mean([f[k] for f in late if f[k] is not None] or [np.nan]))  # noqa: E731
        print(root, Path(d).name, "seed", r.get("seed"), f"late dT {mean('temp') - 14.5:+.2f} C, arid {mean('dry_pct'):.1f}%, "
              f"trees {mean('trees_pct'):.1f}%, npp {mean('npp'):.0f}, ice {mean('ice_pct'):.1f}%, co2 {mean('co2'):.2f}")
