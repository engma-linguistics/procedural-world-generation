"""Lane 142: the Earth screens' table, per arm (ec_TAG.json from L7 earth_check, mr_TAG.txt from L6
moisture_regions). Usage: summ.py SCRATCH TAG..."""
import json
import re
import sys
from pathlib import Path

S = Path(sys.argv[1])
tags = sys.argv[2:]
rows = {}
for t in tags:
    d = json.load(open(S / f"ec_{t}.json"))
    r = rows[t] = {}
    r["B %"] = d["koppen_shares"]["model_excl_ant"]["B"]
    r["exact/group"] = f"{d['cell_agreement_excl_ant']['exact']:.1f}/{d['cell_agreement_excl_ant']['group']:.1f}"
    r["log-rain r"] = d["log_rain_corr"] if not isinstance(d["log_rain_corr"], dict) else \
        list(d["log_rain_corr"].values())[0]
    r["land P"] = d["land_precip_excl_ant"]["model"]["mean"]
    r["global T"] = d["global_means"]["T_model"]
    for b in d["bands"]:
        if b["band"] in ("30..40", "40..50", "50..60", "60..70", "70..80"):
            r[f"sea P {b['band']}"] = b.get("P_ocean_model")
        if b["band"] in ("-90..-80", "-80..-70", "-70..-60", "60..70", "70..80", "80..90"):
            r[f"land P {b['band']}"] = b.get("P_land_model")
    for g in d["regions"]:
        if g["name"] in ("Greenland", "Antarctica", "W Europe", "Alaska"):
            r[f"{g['name']} P / Tc"] = f"{g['P']:.0f} / {g['Tc']:.1f}"
    txt = open(S / f"mr_{t}.txt").read()
    for box in ("N Atlantic storm track", "N Pacific storm track", "W Europe", "European Russia", "Canada 45-60N"):
        for half in ("Oct-Mar", "Apr-Sep"):
            m = re.search(rf"^\| {re.escape(box)} \| {half} \| (\d+) / (\d+) \| (\d+) / (\d+) ", txt, re.M)
            if m:
                r[f"{box} {half} P/E (obs)"] = f"{m[1]}/{m[3]} ({m[2]}/{m[4]})"
keys = list(dict.fromkeys(k for t in tags for k in rows[t]))
print("| | " + " | ".join(tags) + " |")
print("|---" * (len(tags) + 1) + "|")
for k in keys:
    vals = [rows[t].get(k, "") for t in tags]
    print(f"| {k} | " + " | ".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in vals) + " |")
