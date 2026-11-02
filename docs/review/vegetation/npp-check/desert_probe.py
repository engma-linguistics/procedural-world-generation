"""Lane 123: the ideal desert cells of tests/test_vegetation.py: cover by PFT, with the herbs' root respiration factor."""
import sys

sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6")
sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6/tests")
import numpy as np
from planet import vegetation as V
import test_vegetation as TV

f = float(sys.argv[1])
V._KP[V.HERBS, 9] *= f / V.HERB_ROOT_RESP
ideal = TV.ideal.__wrapped__()
g, k, names, v, lat = ideal
de = TV._cells(ideal, "desert")
nu, sm = v["eq"]["nu"], v["sm"]
print("factor", f, "npp med", np.median(sm["npp"][de]), "cover max", sm["cover"][de].max(), "cover med", np.median(sm["cover"][de]))
for i, c in enumerate(V.CODES):
    if nu[i, de].mean() > 0.005:
        print(f"  {c} mean {nu[i, de].mean():.3f} max {nu[i, de].max():.3f} npp {np.median(v['pot']['npp'][i, de]):.0f}")
