"""usage (from a tree root): co2_choices.py -- lane A23's numbers for PW-646's question 1 and the low tail.

1. Earth's time zoom at its glacial maximum (cooling 6.22 C at L6, co2_share 0.5: a CO2 term of -3.11 C) under
   each reading of the CO2 index: the plants' pCO2 for a reference pCO2 and a sensitivity, against the LGM's
   ~185-190 ppm (ice cores: Monnin et al. 2001; Bereiter et al. 2015) and its ratio to the interglacial (190/280).
2. C3 quantum yield (vegetation._q3, Ci = 0.7 Ca, Ca held >= 124 ppm by CO2_RANGE) relative to today's at warm
   monthly means, for the pCO2 of the low tail; and the monthly mean above which a C3 plant gains nothing
   (Ci <= G*, Bernacchi et al. 2001)."""
import numpy as np

from planet import vegetation as V

co2_c = -0.5 * 6.22
print("1. Earth's zoom at the glacial maximum (CO2 term -3.11 C)")
print("reading | C per doubling | reference ppm | doublings | ppm | ratio to interglacial")
for name, per_doubling, ref in (("A: log2, 3 C per e-fold (as A22)", 3.0, 350.0),
                                ("B: ln, 3 C per e-fold (2.08 per doubling)", 3.0 * np.log(2), 350.0),
                                ("C: ppm, 3 C per doubling, ref 350 (this lane)", 3.0, 350.0),
                                ("C': ppm, 3 C per doubling, ref 280 (preindustrial)", 3.0, 280.0),
                                ("C'': ppm, 4 C per doubling, ref 350", 4.0, 350.0)):
    d = co2_c / per_doubling
    print(f"{name} | {per_doubling:.2f} | {ref:.0f} | {d:+.2f} | {ref * 2 ** d:.0f} | {2 ** d:.2f}")
print("Earth: LGM ~185-190 ppm, 0.68 of the preindustrial 280; CO2's own share of the LGM's ~6 C at 3 C per doubling"
      f" is {3 * np.log2(190 / 280):+.2f} C ({-3 * np.log2(190 / 280) / 6.2:.0%}), so co2_share 0.5 overstates it")

print("\n2. C3 quantum yield against today's (350 ppm) at monthly means of 25/30/35/40 C")
for ca in (350, 280, 190, 171, 150, 136, 124, 100):
    cae = max(ca, V.CA_REF * 2 ** -V.CO2_RANGE)
    r = [V._q3(t, 0.7 * cae) / V._q3(t, V.CI_REF) for t in (25.0, 30.0, 35.0, 40.0)]
    print(f"{ca:4d} ppm (as {cae:.0f}): " + " ".join(f"{x:.2f}" for x in r))
for ca in (124, 150, 190):
    ts = np.arange(10, 60, 0.01)
    t0 = ts[np.argmax(V._gstar(ts) >= 0.7 * ca)]
    print(f"C3 gains nothing above a monthly mean of {t0:.1f} C at {ca} ppm (G* = Ci)")
