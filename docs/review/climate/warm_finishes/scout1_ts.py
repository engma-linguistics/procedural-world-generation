"""Scout 203: the last 300 Myr of one or more draws (every 20 Myr, every 4 Myr in the last 24), for the warm finishers.
usage: python scout1_ts.py RUN.json.gz [...]"""
import gzip
import json
import math
import sys

for p in sys.argv[1:]:
    r = json.load(gzip.open(p))
    st = [s for s in r["steps"] if s["t"] > 0]
    print("==", "/".join(p.split("/")[-2:]))
    print("    t    dT  targ   co2  co2t   alb  ghg drift lnsrc lnsink  w_rate  land iced%  T-13.8")
    for s in st:
        t = s["t"]
        if abs(t - round(t)) > 1e-9 or t < 700:
            continue
        t = round(t)
        if not (t % 20 == 0 or (t >= 976 and t % 4 == 0)):
            continue
        ice = s.get("iced_land_pct")
        tt = s.get("true_temp_c")
        print(f"{t:5d} {s['dT']:+5.1f} {s['target']:+5.1f} {s['co2']:+5.2f} {s['co2_term']:+5.1f} {s['albedo_term']:+5.1f} {s['ghg']:+4.1f} "
              f"{s['drift']:+5.2f} {math.log(s['src']):+5.2f} {math.log(s['sink']):+5.2f} {s['w_rate']:.4f} {s['land']:.3f} "
              f"{ice if ice is not None else float('nan'):5.1f} {(tt if tt is not None else float('nan')) - 13.8:+5.1f}")
