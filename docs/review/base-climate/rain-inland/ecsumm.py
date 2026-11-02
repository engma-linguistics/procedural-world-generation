"""Key earth_check numbers from text outputs."""
import re
import sys

REG = ["W Europe", "European Russia", "W Siberia", "E Siberia", "Gobi/Mongolia", "Central Asia", "Great Plains",
       "NE USA", "SE USA", "Pampas", "India", "SE China", "Japan", "Sahel", "West Africa coast", "E Australia",
       "Mediterranean", "Amazon", "NE China/Korea", "Indochina"]
rows = {}
for f in sys.argv[1:]:
    t = open(f).read()
    d = {}
    m = re.search(r"model   excl\. Antarct\.\s+([\d.]+)\s+([\d.]+)", t)
    d["B %"] = m.group(2)
    m = re.search(r"exact code (\d+)%, main group (\d+)%", t)
    d["exact / group %"] = m.group(1) + " / " + m.group(2)
    d["log-rain r"] = re.search(r"\(log\(P \+ 10\)\): ([\d.]+)", t).group(1)
    d["land P mean"] = re.search(r"^model\s+(\d+)\s+\d+\s+\d+\s+\d+", t, re.M).group(1)
    d["summer share"] = re.search(r"summer half-year: model ([\d.]+)", t).group(1)
    d["runoff/rain"] = re.search(r"runoff / rain on land excl\. Antarctica ([\d.]+)", t).group(1)
    for r in REG:
        m = re.search(r"^" + re.escape(r) + r"\s+(\d+)\s+(\d+)", t, re.M)
        d[r] = m.group(1)
        d.setdefault("_obs", {})[r] = m.group(2)
    rows[f.split("/")[-1].replace(".txt", "")] = d
names = list(rows)
print("| | obs | " + " | ".join(names) + " |")
print("|---" * (len(names) + 2) + "|")
first = rows[names[0]]
for k in [k for k in first if k != "_obs"]:
    obs = first["_obs"].get(k, "")
    print(f"| {k} | {obs} | " + " | ".join(rows[n][k] for n in names) + " |")
