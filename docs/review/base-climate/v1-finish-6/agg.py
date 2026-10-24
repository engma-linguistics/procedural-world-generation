"""Aggregate passrate_*.txt per-seed lines: deep-ice share, share distribution."""
import re
import sys

for f in sys.argv[1:]:
    rows = [(float(a), float(b)) for a, b in re.findall(r"icehouse +([\d.]+)% .*?deep +([\d.]+)%", open(f).read())]
    sh = [a for a, _ in rows]; dp = [b for _, b in rows]
    print(f"{f.split('/')[-1]:>20}: n {len(rows)}, deep mean {sum(dp)/len(dp):4.1f}%, deep>=20% {sum(d >= 20 for d in dp)}, "
          f"share<=40 {sum(s <= 40 for s in sh)}, 40-50 {sum(40 < s <= 50 for s in sh)}, >=60 {sum(s >= 60 for s in sh)}, "
          f"mean share {sum(sh)/len(sh):.0f}%")
