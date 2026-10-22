---
id: PW-448
title: Earth time zoom's glacials are only ~1.7 C colder (real LGM ~5-6 C), so no Laurentide sheet south of ~60 N
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: timezoom
effort: m
impact: high
found_by: owner-2026-10-20
blocked_by: []
relates: [PW-030, PW-435, PW-447]
refs: [planet/timezoom/forcing.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
Owner compared time zoom 755514's glacial maximum with an LGM map (Svendsen et al. 2004): the simulation has no Laurentide below ~60 N, no Hudson Bay ice, no Scandinavian sheet to northern Germany, no Barents sheet. run.txt: global_T 14.5 -> 12.8 C at the deepest glacial (-43 m, 5.9% of the surface iced) against the real ~-5 to -6 C, -125 m, ~8%. Investigate with measurements, not supposition: decompose the glacial cooling into orbit, CO2, ice albedo and any other terms, and compare each with Earth's LGM budget (CO2 ~ -90 ppm ~ -1.5 to -2 C with feedbacks; ice albedo ~ -3 C; dust and vegetation). Check whether the forcing-to-temperature chain lacks the water-vapour/lapse-rate amplification, whether CO2 is tied to the extra ice so small ice gives small CO2 (chicken and egg), whether Earth wrongly gets a run moment's halved CO2 cap, and what summer temperature and snow balance the Canadian interior (Keewatin/Labrador/Hudson Bay) sees at glacial orbits. Fix only what the measurements show is wrong. Planet-relative, no Earth fudges.

## Updates
- 2026-10-20: pw033: correction. The Canadian-interior probe used the frames' Jul-Aug sun metric, whose minimum (t=592, perihelion 356 deg) is not glacial for the mass balance's warm month (-6.5 W/m2; May-Jun +28/+10). At the kernel's coldest orbit (t=309.5, -43.9 W/m2) the orbit cools Keewatin's July by 6.1 C, Keewatin and Baffin nucleate at dTg ~-3 and Labrador at ~-6 on the observed baseline, not -9/-11 (docs/review/audit/PW-033-diagnosis.md section 2).
- 2026-10-20: pw450: vegetation is now in the time zoom (PW-450). At the default zoom's deepest glacial it adds ~0 (-0.02 C, -0.02..-0.07 W/m2); at an Earth-like -6 C, -0.32 W/m2 (LGM -1.1), with the tropics darkening instead of brightening (docs/review/audit/PW-450-vegetation.md).
- 2026-10-20: pw448: diagnosis in docs/review/audit/PW-448-diagnosis.md. At -42.8 m: CO2 -0.65, ice albedo -1.21, sheets' own climate -0.31, orbit +0.03 C global (area mean -1.95 C); 0.044 C per m of sea level vs Earth's ~0.048, so the amplification is there and Earth's CO2 room is 1. The CO2 is slaved to ice (26-36% of its drop vs Earth's ~50% at -40 m), secondary (co2_cool 4.0: -45 m). Main lever: the ice-albedo tanh counts today's ice in the LGM's 2.5-3 C, so 2.8 -> 8% gives 1.3 C, not ~2.6. Near-linear (ice_albedo_max 30): -71 m, -4.1 C, 5 endings, interglacials unchanged. It's the run's shared rule, so a needs-decision draft, no fix merged. Canadian interior: Keewatin/Labrador need dTg ~-9/-11 C for positive balance at glacial orbits; even at -5 C the Laurentide stays 2 Mkm2 (southmost 55 N). Geography is PW-033/PW-435. Missing vegetation and dust (~-1.7 C at the LGM): draft.
