"""Lane 131: one table row per arm from ec2.sh's outputs (screen2.py text + earth_check json).
    python3 docs/review/base-climate/tropical-cloud/table2.py DIR arm1 arm2 ..."""
import json
import re
import sys

D = sys.argv[1]
arms = sys.argv[2:]


def grab(txt, pat, n=1):
    m = re.search(pat, txt)
    return m.groups() if m and n > 1 else (m.group(1) if m else "?")


rows = {}
for a in arms:
    t = open(f"{D}/{a}.txt").read()
    e = json.load(open(f"{D}/ec_{a}.json"))
    r = {}
    sh = re.findall(r"  (\d+)-(\d+): n=\s*\d+\s+[\d.]+/[\d.]+/([\d.]+)\s+\|\s+[\d.]+/[\d.]+ ;\s+([\d.-]+)/\s*([\d.-]+)/\s*([\d.-]+)", t)
    r["shade 400-900/900-1500/>1500 (obs .27/.41/.53)"] = "/".join(x[2] for x in sh)
    r["Tc 400-900 same cells (NCEP 16.4)"] = sh[0][3]
    r["Tc 900-1500 same cells (NCEP 20.0)"] = sh[1][3]
    r["MAT 400-900 same cells (NCEP 22.6)"] = sh[0][4]
    for b in ("0-10", "10-20", "20-40", "40-60"):
        r[f"summer sun {b}"] = grab(t, rf"sunshine share {b}: summer model ([\d.]+) CRU")
    for b in ("0-20", "20-40", "40-60"):
        x = grab(t, rf"  {b}: warm\s+([\d.-]+) vs\s+[\d.-]+ \(([+-][\d.]+)\)\s+cold\s+([\d.-]+) vs\s+[\d.-]+ \(([+-][\d.]+)\)", 4)
        r[f"warm month {b}"] = f"{x[0]} ({x[1]})"
        r[f"cold month {b}"] = f"{x[2]} ({x[3]})"
    r["land >= 35 C (NCEP 1.7)"] = grab(t, r"land >= 35 C: ([\d.]+)%")
    for name in ("India", "Mexico N", "Sahel", "S Africa sav", "W Europe", "Congo"):
        x = grab(t, rf"  {re.escape(name)}\s+[\d.-]+\s*/\s*[\d.-]+ \(([+-][\d.]+)\)\s+[\d.-]+\s*/\s*[\d.-]+ \(([+-][\d.]+)\)\s+([\d.]+) / ([\d.]+)", 4)
        r[f"{name}: dTw / dTc / summer sun (CRU)"] = f"{x[0]} / {x[1]} / {x[2]} ({x[3]})"
    for name in ("Amazon", "Congo basin", "W Europe", "Siberia", "Pacific NW", "Australia interior"):
        x = grab(t, rf"  {re.escape(name)}\s+sky\s+([\d.]+) \((\d+-\d+)\)", 2)
        r[f"sky % {name}"] = f"{x[0]} ({x[1]})"
    k = e["koppen_shares"]["model_excl_ant"]
    r["Köppen A/B/C/D/E (Kottek 21.9/30.1/15.9/24.8/7.3)"] = "/".join(f"{k[g]:.1f}" for g in "ABCDE")
    r["BWh (Kottek 14.8)"] = f"{e['code_shares_excl_ant']['BWh']['model']:.1f}"
    ca = e["cell_agreement_excl_ant"]
    r["Köppen exact / group"] = f"{ca['exact']:.1f} / {ca['group']:.1f}"
    r["log-rain r"] = f"{e['log_rain_corr']:.3f}"
    ps = e["point_score"]
    r["points exact/group/miss"] = f"{ps['exact']}/{ps['group']}/{ps['miss']}"
    r["land sun RMSE"] = f"{e['clouds']['land_sun_rmse']:.1f}"
    rows[a] = r
keys = list(rows[arms[0]].keys())
print("| Earth L7 | " + " | ".join(arms) + " |")
print("|---|" + "---|" * len(arms))
for k_ in keys:
    print(f"| {k_} | " + " | ".join(rows[a].get(k_, "") for a in arms) + " |")
