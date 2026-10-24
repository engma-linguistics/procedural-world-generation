"""Windowed means of srcdiag outputs: source = ridge + arc; arc per trench cell / heat^1.5 = the config part."""
import json, sys
import numpy as np
for f in sys.argv[1:]:
    d = json.load(open(f)); c = d["cols"]; r = np.array(d["rows"], float)
    g = {k: r[:, i] for i, k in enumerate(c)}
    print(f.split("/")[-1])
    for a in [100, 300, 500, 700, 1000, 1150]:
        m = (g["t"] >= a - 50) & (g["t"] < a + 50)
        if not m.any():
            continue
        h, ri, ar, n = g["heat"][m].mean(), g["ridge"][m].mean(), g["arc"][m].mean(), g["arc_cells"][m].mean()
        print(f"  {a:5d} heat {h:5.3f} src {ri + ar:6.0f} ridge {ri:5.0f} arc {ar:6.0f} trench_cells {n:5.0f} "
              f"arc/cell/heat {ar / n / h:5.2f} ridge/h^.5 {ri / h ** .5:5.0f} land {g['land'][m].mean():.2f} "
              f"cont {g['cont'][m].mean():.2f} dT {g['dT'][m].mean():+.1f}")
