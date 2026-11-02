"""Lane 121: tabulate diag.py's JSON outputs: summ.py DIR tag [tag ...] [--regions R1,R2,...]"""
import json
import sys
from pathlib import Path

d = Path(sys.argv[1])
args = sys.argv[2:]
regs = []
if "--regions" in args:
    i = args.index("--regions")
    regs = args[i + 1].split(",")
    args = args[:i]
for m in args:
    r = json.loads((d / f"{m}.json").read_text())
    s = r["share"]
    print(f"{m:34} >=30 {100 * s['ge30']:.1f}/{100 * s['ge30_obs']:.1f} >=35 {100 * s['ge35']:.1f}/{100 * s['ge35_obs']:.1f}  "
          + " ".join(f"{k}:{b['warm']:.1f}({b['warm'] - b['warm_obs']:+.1f})" for k, b in r["bands"].items()
                     if k in ("0-20", "20-30", "30-40", "20-40", "40-60")))
    if regs:
        print("    " + " ".join(f"{k}:{r['regions'][k]['warm'] - r['regions'][k]['warm_obs']:+.1f}" for k in regs))
