import glob
import json
import sys

for f in sorted(glob.glob(sys.argv[1] + "/eq_*.json")):
    d = json.load(open(f))
    for k, recs in d["res"].items():
        r0, r = recs[0], recs[-1]
        print(f"{d['run']} @{d['t']:g} {k:>9}: upd1 {r0['sea_ice']:7.1f} m / {100 * r0['iced_land']:5.1f}% | "
              f"upd{len(recs)} {r['sea_ice']:7.1f} m / {100 * r['iced_land']:5.1f}%  snow_land {100 * r0['snow_land']:.2f}% "
              f"T {r['temp']:.2f} land {r['land']:.4f} p99 {r['e_land_p99']}")
