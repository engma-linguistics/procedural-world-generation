"""Summarise moisture_regions text outputs: annual P per box (mean of halves), winter conv, residence."""
import re
import sys

BOX = ["W Europe", "European Russia", "W Siberia", "E Siberia", "Gobi/Mongolia", "Central Asia", "Great Plains",
       "NE USA", "SE USA", "Canada 45-60N", "Pampas", "N Atlantic storm track", "Gulf of Mexico"]
files = sys.argv[1:]
data = []
for f in files:
    d = {}
    for line in open(f):
        m = re.match(r"\| ([^|]+) \| (Apr-Sep|Oct-Mar) \| (\d+) / (\d+) \|", line)
        if m:
            cols = [c.strip() for c in line.split("|")]
            conv = cols[9].split("/")[0].strip()
            d.setdefault(m.group(1), {})[m.group(2)] = (int(m.group(3)), int(m.group(4)), conv)
        m = re.match(r"- land \(to 60S\), (\S+): vapour residence \(PW / P\) model ([\d.]+) d", line)
        if m:
            d["res " + m.group(1)] = m.group(2)
    data.append(d)
print("box | obs | " + " | ".join(f.split("/")[-1].replace(".txt", "") for f in files))
for b in BOX:
    row = []
    for d in data:
        h = d.get(b, {})
        if len(h) == 2:
            row.append("%d (w %d, s %d)" % (round((h["Apr-Sep"][0] + h["Oct-Mar"][0]) / 2), h["Oct-Mar"][0], h["Apr-Sep"][0]))
            obs = round((h["Apr-Sep"][1] + h["Oct-Mar"][1]) / 2)
        else:
            row.append("-")
    print(f"{b} | {obs} | " + " | ".join(row))
for k in ("res Apr-Sep", "res Oct-Mar"):
    print(k + " | | " + " | ".join(d.get(k, "-") for d in data))
