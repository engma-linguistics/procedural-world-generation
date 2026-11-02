---
title: The model's eastern equatorial Atlantic (off Gabon and Angola) hardly cools in its cool season, so the Congo's dry-season stratus has no inversion
type: task
status: todo
parent: null
milestone: v2
subsystem: ocean
effort: m
impact: low
found_by: lane131
blocked_by: []
relates: [PW-1347, PW-1334]
refs: ["planet/climate.py::sea_surface", "planet/climate.py::upwelling_cooling", "planet/climate.py::clouds", docs/review/base-climate/tropical-cloud/round2-diagnosis.md, docs/review/base-climate/tropical-cloud/screen2.py, docs/review/base-climate/tropical-cloud/round2.patch, paper:Champagne2023, paper:Berger2025, paper:Philippon2019]
---

## Description
In plain words: Gabon and the western Congo are dark in June-September because cool air off the south-east Atlantic
blows inland under warm air aloft and makes a low stratus deck. In the model that sea is too warm in its cool
season, so there is no inversion and no deck. Lane 131 measured it on Earth L7 (main afed2ced). Off Gabon (5S-2N, 4-9E),
model sst in July is 25.8 C. NCEP's 2 m air over the same sea in its coldest month is 23.7 C (a rough stand-in for the
water). The model's air aloft is only 1.3 C warmer than that sea, and the Sc deck there is 0.01. Gabon's July sunshine
is 0.78 against CRU 0.33.

Sources (read, see round2-diagnosis.md section 1): Champagne et al. 2023 says the coastal upwelling extends north to
Cape Lopez in boreal summer and the equatorial upwelling cools the eastern equatorial Atlantic. Warm-SST years have less
Gabon stratus. Berger et al. 2025 says the deck persists with "surface westerlies advecting cooler maritime air
increasing the lower-tropospheric stability".

Try: measure the model's E equatorial Atlantic / Benguela seasonal cycle against an SST climatology first (earth_data
has none yet; NCEP air is only a proxy). If the cold tongue is missing, see whether `upwelling_cooling`'s equatorial
term has a season. Then re-try lane 131's candidate c (`cloud_seastab_km` in round2.patch: the sea's inversion carried
inland for the land stratus gate). It did nothing on today's sea.
- [ ] model cool-season SST off Gabon within ~1 C of an SST climatology; then Congo sky re-measured with candidate c
