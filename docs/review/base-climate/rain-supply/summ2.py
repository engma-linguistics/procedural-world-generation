"""Lane 132 running table: summ.py TAG [TAG...] (from $S/ec_TAG.txt, mr_TAG.txt, cl_TAG.txt)."""
import re
import sys
S = "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l134/"
INT = ["W Siberia", "European Russia", "Great Plains", "Gobi/Mongolia", "Central Asia"]  # 40-60 N interiors
COAST = ["SE USA", "Pampas", "India", "SE China", "Japan", "E Australia"]  # humid coasts
REG = ["W Europe", "European Russia", "W Siberia", "Gobi/Mongolia", "Central Asia", "Great Plains", "NE USA",
       "SE USA", "Pampas", "India", "SE China", "Japan", "E Australia", "Indochina", "Sahel", "Amazon",
       "Mediterranean", "West Africa coast"]
SEA = ["N Atlantic storm track", "N Pacific storm track", "Gulf of Mexico", "W Atlantic subtropics",
       "E Atlantic subtropics", "NW Pacific subtropics", "SW Atlantic", "Tropical Atlantic"]
rows, obs = {}, {}
for t in sys.argv[1:]:
    d = {}
    e = open(S + f"ec_{t}.txt").read()
    d["B % (Kottek 30.1)"] = re.search(r"model   excl\. Antarct\.\s+([\d.]+)\s+([\d.]+)", e).group(2)
    m = re.search(r"exact code (\d+)%, main group (\d+)%", e)
    d["exact / group %"] = m.group(1) + " / " + m.group(2)
    d["log-rain r"] = re.search(r"\(log\(P \+ 10\)\): ([\d.]+)", e).group(1)
    d["land P (GPCC 791)"] = re.search(r"^model\s+(\d+)\s+\d+\s+\d+\s+\d+", e, re.M).group(1)
    rat = {}
    for r in REG:
        m = re.search(r"^" + re.escape(r) + r"\s+(\d+)\s+(\d+)", e, re.M)
        d[r] = m.group(1)
        obs[r] = m.group(2)
        rat[r] = float(m.group(1)) / float(m.group(2))
    d["interiors 40-60N x obs"] = f"{sum(rat[r] for r in INT) / len(INT):.2f}"
    d["humid coasts x obs"] = f"{sum(rat[r] for r in COAST) / len(COAST):.2f}"
    mr = open(S + f"mr_{t}.txt").read()
    for b in SEA:
        for h in ("Apr-Sep", "Oct-Mar"):
            m = re.search(r"^\| " + re.escape(b) + r" \| " + h + r" \| (\d+) / (\d+) \| (\d+) / (\d+) \|.*\| ([\d.]+) / ([\d.]+) \| [\d.]+ / [\d.]+ \| \d+ \| \d+ \| [\d/-]+ \| ([\d.]+) \|", mr, re.M)
            k = f"{b} {h[:3]} P/E/PW"
            d[k] = f"{m.group(1)}/{m.group(3)}/{m.group(5)}"
            obs[k] = f"{m.group(2)}/{m.group(4)}/{m.group(6)}"
    c = open(S + f"cl_{t}.txt").read()
    for lab in ("0-20", "20-40", "40-60"):
        d[f"warm month {lab}"] = re.search(r"^  " + lab + r":\s+([\d.]+) vs\s+([\d.]+)", c, re.M).group(1)
        obs[f"warm month {lab}"] = re.search(r"^  " + lab + r":\s+([\d.]+) vs\s+([\d.]+)", c, re.M).group(2)
    for lab in ("10-20", "20-40", "40-60"):
        m = re.search(r"summer sunshine share " + lab + r": model ([\d.]+)  CRU ([\d.]+)", c)
        d[f"summer sun {lab}"], obs[f"summer sun {lab}"] = m.group(1), m.group(2)
    for lab in ("Congo basin", "Amazon", "W Europe"):
        m = re.search(r"^  " + lab + r"\s+sky\s+([\d.]+) \(([\d-]+)\)", c, re.M)
        d[f"sky {lab}"], obs[f"sky {lab}"] = m.group(1), m.group(2)
    rows[t] = d
names = list(rows)
print("| | obs | " + " | ".join(names) + " |")
print("|---" * (len(names) + 2) + "|")
for k in rows[names[0]]:
    print(f"| {k} | {obs.get(k, '')} | " + " | ".join(rows[n][k] for n in names) + " |")
