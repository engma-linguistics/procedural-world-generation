---
id: PW-1334
title: Land humidity layer cloud (cloud_rh) is the whole shade excess over warm moist land, on Earth and every world
type: task
status: done
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane125
blocked_by: []
relates: [PW-1330, PW-1327, PW-808, PW-232, PW-1261]
refs: ["planet/climate.py::clouds", "planet/climate.py::shade", "planet/climate.py::_summer_split", "planet/climate.py::open_water_evap", docs/review/base-climate/tropical-cloud/diagnosis.md, docs/review/base-climate/tropical-cloud/bands.py, docs/review/base-climate/tropical-cloud/components.py, docs/review/base-climate/summer-heat/diagnosis.md, docs/review/vegetation/npp-check/diagnosis.md, "tools/earth_check.py::CLOUD_REGIONS", "world dba204", "world 899985", "world 1df1c3", "world 6909cb", "world 3e9e7d", "https://www.fao.org/4/x0490e/x0490e07.htm"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the Earth run of the model itself is cloudier than Africa at the same rain (shade 0.40 / 0.55 / 0.69 vs
observed 0.27 / 0.41 / 0.53 for 400-900 / 900-1500 / >1500 mm, same cells), and the worlds match the Earth model
(0.38-0.44 / 0.47-0.52 / 0.58-0.66), so PW-1330's cloud half is the cloud scheme, not a world effect. Switching off the
land humidity layer cloud (cloud_rh x rh^1.5) drops the shade by 0.16-0.18 in each band, more than the whole gap;
deep cloud is worth 0.1-0.14 and cumulus 0.04. See the diagnosis for the tables.
Try: scale the humidity layer cloud down in warm air (stratus belongs to cool air), check the three bands above and W
Europe / Pacific NW / Siberia in tools/earth_check.py's cloud regions, then PW-1327's split change in the same ticket.
It needs an external source for the stratus-vs-convective split first (none read).
- [ ] Earth model warm-land shade within ~0.05 of observed in the three rain bands, W Europe cloud still passes

## Updates
- 2026-11-02: Status todo -> done. Lane 126 (merged fdc631a4): see docs/review/base-climate/tropical-cloud/round1.md. Earth warm-land shade 0.31/0.42/0.54 vs CRU 0.27/0.41/0.53; land >=35 C 7.9% -> 0.9% (NCEP 1.7%); Lake Victoria evap 1357 -> 1635 mm. L6 judge 32/36 vs 32/36, no hard failures, dT/CO2 unmoved; arid -2.0 pts, trees +5.7.
- 2026-11-02: Created from inbox draft draft-cloud-rh-warm-moist-land.md (found by lane125).
