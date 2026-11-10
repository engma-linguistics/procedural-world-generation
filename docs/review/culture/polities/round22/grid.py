"""Lane 265 (PW-1597): the tree steps of a stored run between two dates (ya), read off every date its tree gave any people any
tech (the tree's dates are its steps), so an on/off gap can be counted in steps. Read-only. argv: run_dir from_ya to_ya."""
import json
import sys
from pathlib import Path

d, a, b = Path(sys.argv[1]), float(sys.argv[2]) / 1000, float(sys.argv[3]) / 1000
kn = json.loads((d / "run.json").read_text())["meta"]["techtree"]["known"]
ds = sorted({v[0] for k in kn.values() for v in k.values() if min(a, b) - 1e-6 <= v[0] <= max(a, b) + 1e-6})
print(d.name, [round(x * 1000) for x in ds])
