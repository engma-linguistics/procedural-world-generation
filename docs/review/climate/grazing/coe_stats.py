"""Scout 202: where the model's Earth herds sit in Coe, Cumming & Phillipson 1976's scatter (Table 1, pp. 344-345, on file:
docs/references/megafauna/coe1976_african_herbivore_biomass_rainfall_oecologia.pdf). Biomass kg/km2 live weight, rain mm."""
import numpy as np

# 1-24 wildlife areas, 25-30 pastoral areas (Watson 1972, not recalculated by Coe et al.)
W = [(17448, 863), (19928, 1010), (13261, 1150), (19189, 915), (7561, 893), (6688, 878), (4348, 350), (7568, 813), (405, 165),
     (2018, 375), (4824, 844), (4033, 553), (4388, 553), (1731, 425), (5423, 784), (8352, 803), (3909, 625), (3980, 785), (4315, 597),
     (2869, 406), (984, 312), (3783, 650), (3344, 520), (4385, 650)]
P = [(1901, 228), (1151, 218), (3818, 398), (2406, 330), (6514, 500), (7884, 710)]
RAIN = 626  # the model's 550-700 mm band mean (round3.md, section 1)
MODEL = {"main before PW-1261 (4.10)": 4100.0, "after PW-1261 (3.07)": 3070.0}


def fit(d):
    b = np.log10([x[0] for x in d])
    r = np.log10([x[1] for x in d])
    s, i = np.polyfit(r, b, 1)
    res = b - (s * r + i)
    return s, i, res.std(ddof=2)


for name, d in (("all 30", W + P), ("wildlife 24", W), ("wildlife < 700 mm", [x for x in W if x[1] < 700])):
    s, i, sd = fit(d)
    pred = 10 ** (s * np.log10(RAIN) + i)
    zs = ", ".join(f"{k}: z {(np.log10(v) - np.log10(pred)) / sd:+.2f}" for k, v in MODEL.items())
    print(f"{name}: n={len(d)} log-log slope {s:.3f} intercept {i:.3f}, residual sd {sd:.3f} dex (x{10 ** sd:.2f}); "
          f"fit at {RAIN} mm {pred / 1000:.2f} t/km2; {zs}")
lo = [x for x in W if x[1] < 700]
b = np.array([x[0] for x in lo], float)
r = np.array([x[1] for x in lo], float)
s, i = np.polyfit(r, b, 1)
res = b - (s * r + i)
print(f"linear < 700 mm (n={len(lo)}): {s:.3f} R {i:+.1f} (paper p. 348: 8.684 R - 1205.9); residual sd {res.std(ddof=2):.0f} kg/km2;"
      f" at {RAIN} mm {s * RAIN + i:.0f}; z of 3070 {(3070 - (s * RAIN + i)) / res.std(ddof=2):+.2f}")
print("wildlife areas 550-700 mm, t/km2:", [round(x[0] / 1000, 2) for x in sorted(W) if 550 <= x[1] < 700])
print("all areas 500-750 mm (kg, mm):", sorted(x for x in W + P if 500 <= x[1] < 750))
print(f"Rosenzweig 1968 NAAP at AE = {RAIN} mm (Coe p. 345): {10 ** (1.66 * np.log10(RAIN) - 1.66):.0f} g dry/m2/yr")

# every band of round3.md section 1 (band mean rain, herds main / after PW-1261, t/km2 median over warm African grassy cells)
BANDS = [(328, 1.28, 0.96), (468, 2.57, 1.89), (626, 4.10, 3.07), (804, 5.44, 4.10)]
print("\nband z-scores against the log-log fits (before / after PW-1261):")
for name, d in (("all 30", W + P), ("wildlife 24", W)):
    s, i, sd = fit(d)
    row = []
    for r, m0, m1 in BANDS:
        pred = 10 ** (s * np.log10(r) + i) / 1000
        row.append(f"{r} mm fit {pred:.2f}: {(np.log10(m0 / pred)) / sd:+.2f} / {(np.log10(m1 / pred)) / sd:+.2f}")
    print(f"  {name}: " + "; ".join(row))
