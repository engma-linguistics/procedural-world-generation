"""Static check of two-sided flexure (PW-284 lean B) on stored frames: swap the 0.15 one-sided moat for
deflection = root - smooth(root, km) (volume kept), and see peaks, land and hollow potential. Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from planet.climate import smooth
from planet.geo import is_land
from planet.grid import build_grid
from planet import timeline as T
from planet.tectonics import isostasy as I

sys.path.insert(0, "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s247/scripts")
root_dir, rid, every = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
kms = [float(x) for x in sys.argv[4:]] or [150.0, 75.0]
run, arr = T.load_frames(root_dir / "runs" / rid, ("elevation", "crust", "crust_thickness"))
grid = build_grid(run["meta"]["level"])
for i, fr in enumerate(run["frames"]):
    t = fr["stats"]["t"]
    if t < 50 or i % every:
        continue
    elev = np.asarray(T.frame(run, arr, "elevation", i, grid), float)
    cont = np.asarray(T.frame(run, arr, "crust", i, grid)) > 0
    thick = np.asarray(T.frame(run, arr, "crust_thickness", i, grid), float)
    root = np.where(cont, I.ROOT * np.maximum(thick - I.CONT_KM, 0.0), 0.0)
    sm = smooth(grid, root, 150.0)
    old = -I.MOAT_MAX * np.tanh(0.15 * np.maximum(sm - root, 0.0) * cont / I.MOAT_MAX)
    base = elev - old
    line = f"t={t:.0f} now: max {elev.max()/1e3:.2f} km land {100*is_land(elev, grid=grid).mean():.1f}%"
    for km in kms:
        s = smooth(grid, root, km)
        s *= root.sum() / max(s.sum(), 1e-9)
        new = root - s
        e2 = base + new
        line += (f" | {km:.0f}km: max {e2.max()/1e3:.2f} cells>9.5 {(e2 > 9500).sum()} uplift max {new.max()/1e3:.1f} "
                 f"p99.9 {np.percentile(new[cont], 99.9)/1e3:.1f} moat min {new.min()/1e3:.1f} land {100*is_land(e2, grid=grid).mean():.1f}%")
    print(line, flush=True)
