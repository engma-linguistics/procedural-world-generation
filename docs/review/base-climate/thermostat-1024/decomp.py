"""usage: decomp.py LABEL=DIAG_DIR ... -- the CO2 answer split as thermostat.md's stage 4 (laneB4/decomp.py): with the stock
near its steady state, co2 ~ (ln src - ln sink) / WEATHER_CO2, so the answer on the drift (trends out, iv = cov(., drift)
/ cov(dT, drift) after a 200 Myr running mean is taken out of each series) is
    answer ~ (sink fb - source fb) x the forcing's tanh slope,
sink fb = sens x iv(ln sink) / WEATHER_CO2, source fb = sens x iv(ln src) / WEATHER_CO2 (sens: C per e-fold).
Per seed, then medians; plus the sink fb's parts (area, supply, temperature, plants). Steps after 300 Myr."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

T0, TREND = 300.0, 200.0
WEATHER_CO2, CO2_MAX = 0.4, 6.0


def hp(y, n):
    pad = np.r_[np.full(n, y[:n].mean()), y, np.full(n, y[-n:].mean())]
    return y - np.convolve(pad, np.ones(2 * n + 1) / (2 * n + 1), "same")[n:-n]


for arg in sys.argv[1:]:
    label, d = arg.split("=", 1)
    rows = []
    for p in sorted(Path(d).glob("seed*_L6.json.gz")):
        r = json.load(gzip.open(p))
        sens = r.get("params", {}).get("co2_sensitivity", 3.0) / np.log(2.0)
        st = [s for s in r["steps"] if s["t"] >= T0 and s.get("w_supply") and s.get("sink_raw", 0) > 0]
        f = lambda k: np.array([s[k] if s.get(k) is not None else np.nan for s in st], float)
        t, dT, drift, co2t, co2 = f("t"), f("dT"), f("drift"), f("co2_term"), f("co2")
        parts = {"sink": np.log(f("sink")), "src": np.log(f("src")), "area": np.log(f("w_area")),
                 "supply": np.log(f("w_supply") / f("w_area")), "temp": np.log(f("w_temp")), "plant": np.log(f("w_plant"))}
        ok = np.all([np.isfinite(v) for v in parts.values()], 0) & np.isfinite(dT)
        n = max(1, int(round(TREND / 2 / float(np.median(np.diff(t))))))
        dh = hp(drift[ok], n)
        cdh = float(np.cov(hp(dT[ok], n), dh)[0, 1])
        iv = lambda y: float(np.cov(hp(y[ok], n), dh)[0, 1]) / cdh
        slope = float(np.mean(1 / np.cosh(co2[ok] / CO2_MAX) ** 2))
        row = {"seed": p.name.split("_")[0][4:], "answer": -iv(co2t), "sink": sens * iv(parts["sink"]) / WEATHER_CO2,
               "source": sens * iv(parts["src"]) / WEATHER_CO2, "slope": slope}
        for k in ("area", "supply", "temp", "plant"):
            row[k] = sens * iv(parts[k]) / WEATHER_CO2
        row["split"] = (row["sink"] - row["source"]) * slope
        # how much of ln src's own variance there is (C of CO2 term per sd of ln src)
        row["src_sd_C"] = sens / WEATHER_CO2 * float(np.std(hp(parts["src"][ok], n)))
        rows.append(row)
    keys = ["answer", "split", "sink", "source", "slope", "area", "supply", "temp", "plant", "src_sd_C"]
    print(f"== {label} ({len(rows)} seeds): per seed " + " ".join(keys))
    for r in rows:
        print(f"  {r['seed']:>5}: " + " ".join(f"{r[k]:+.2f}" for k in keys))
    print("  median: " + " ".join(f"{k} {np.median([r[k] for r in rows]):+.2f}" for k in keys))
