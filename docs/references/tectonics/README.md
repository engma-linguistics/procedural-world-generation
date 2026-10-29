# Tectonics references

Papers behind the tectonics code. The PDFs are kept locally and are gitignored (`docs/references/**/*.pdf`) for copyright reasons. This README is the committed index. Read a paper here before citing it.

## Have (local PDF)

| File | Citation | Used for |
|---|---|---|
| burke_dewey1973_plume_triple_junctions_jgeol.pdf | Burke & Dewey 1973, "Plume-generated triple junctions: key indicators in applying plate tectonics to old rocks", J. Geol. 81:406-433 | `events.triple_rift` (PW-952). Read 2026-10-29. Rifts meet at about 120 degrees (abstract, p. 406). Of 45 selected junctions, 32 spread on two arms with the third failed, 3 spread on three, 5 on none, and 5 are too young to tell (p. 426). Rifting happens "especially" where the lithosphere is at rest over the plume (pp. 406, 429). Many great rivers flow down failed arms (abstract). |
| mckenzie1978_sedimentary_basins_stretching_epsl.pdf | McKenzie 1978, "Some remarks on the development of sedimentary basins", Earth Planet. Sci. Lett. 40:25-32 | `isostasy.subsidence` thermal sag (PW-054, PW-950). Read 2026-10-29. Table 1 (p. 27): a = 125 km, rho_m 3.33, rho_c 2.8, rho_w 1.0 g/cm3, alpha 3.28e-5 /C, T1 1333 C, tau 62.8 My, E0 3.2 km. Eqs. 10-12 (p. 28): e(t) ~ E0 r exp(-t/tau), r = (beta/pi) sin(pi/beta), E0 = 4 a rho0 alpha T1 / (pi^2 (rho0 - rho_w)), water-loaded. The air-loaded value is 2.2 km (SAG_KM). Initial subsidence Si > 0 where the crust is thicker than 18 km (p. 27). |
