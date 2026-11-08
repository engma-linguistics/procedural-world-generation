"""Lane 158: the pulse runs' carbon balance against fm, by part (10 Myr means of the differences, 700-800 Myr)."""
import sys
import numpy as np
from pulse_read import rec, J, S, draw, seed
fm = rec(f"{J}/m_{draw}/seed{seed}_L6.json.gz")
P = {"dT": lambda x: x["dT"], "ln src": lambda x: np.log(x["src"]), "ln sink@1": lambda x: np.log(x["sink"]),
     "ln supply": lambda x: np.log(x["w_supply"]), "ln temp": lambda x: np.log(x["w_temp"]),
     "ln plant": lambda x: np.log(x["w_plant"]), "w_T": lambda x: x["w_T"], "area": lambda x: x["w_area"],
     "lnX": lambda x: x["co2"], "a": lambda x: x["w_a"], "albedo": lambda x: x["albedo_term"], "ghg": lambda x: x["ghg"]}
for arm in sys.argv[1:]:
    p = rec(f"{S}/l158/pulse/{arm}/seed{seed}_L6.json.gz")
    print(f"== {arm} minus fm")
    print(f"{'Myr':>9} " + " ".join(f"{k:>9}" for k in P))
    for a in range(700, 800, 10):
        ts = [t for t in p if a < t <= a + 10 and t in fm]
        print(f"{a:>4}-{a + 10:<4} " + " ".join(f"{np.mean([f(p[t]) - f(fm[t]) for t in ts]):+9.3f}" for f in P.values()))
