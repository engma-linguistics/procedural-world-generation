# Lane 135: finished-frame orbit response (PW-1325), CO2 references over the whole spin-up (PW-1316), the spin-up audit

Main fc4e0398. Scratch: `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l135` (S below).

## 1. PW-1325 (owner: A). Done, committed separately

**In plain words:** a finished world used to add its moment's orbit to the months at the ice rule's 0.25 C per W/m2.
Now it uses each cell's seasonal response (`icemass.seasonal_k`, ~0.03 C per W/m2 in the tropics, 0.08-0.09 at mid
and high latitudes), whatever the time zoom's own rule. The time zoom's ice and the runs don't change.

- Code: `planet/finish.py::orbit_dt` forces `orbit_resp='seasons'` (one `dataclasses.replace`), and always builds the
  seasonal response from the frame's climate at the mean orbit (the branch that 'seasons' time zooms already used).
- What it touches: only `finish.orbit_dt`, called by `finish._finish` and `refine` (a finished world's regional zoom).
  Runs have no orbit_dt; the time zoom's own climate and ice use `forcing.orbit_anomaly` with their own `p` (unchanged);
  earth_check doesn't finish a frame. Goldens (`tests/test_golden.py`) pass unchanged. `finish_key` changes with the
  finishing code (provenance hash), so `api.find_slice` won't reuse a world finished under the old rule.
- Test: `tests/test_finish.py::test_finished_climate_has_the_orbit` now checks the anomaly equals the 'seasons' one
  although the fixture's time zoom is 'run', and that its mean size on bare land is under 0.6 of the run rule's.

dba204 (time zoom 56dee1, 202 kyr; orbit obliquity 22.43, eccentricity 0.0348, perihelion 90.7), re-solved on its
stored elevation and ice at the frame's dT with its plants ([pw1325_dba204.py](pw1325_dba204.py); 'before' reproduces
the stored world):

| ice-free land | stored | before (0.25 C per W/m2) | after (seasons) | no orbit |
|---|---|---|---|---|
| warmest month 0-20 deg (C) | 30.5 | 30.6 | **25.5** | 25.4 |
| 20-40 deg | 28.7 | 27.4 | 26.8 | 26.6 |
| 40-60 deg | 22.6 | 22.9 | 20.0 | 18.9 |
| land with warmest month >= 30 C | 45.4% | 45.0% | **15.5%** | 14.8% |
| land >= 35 C | 18.3% | 17.9% | 2.9% | 0.3% |
| mean July anomaly on 0-20 deg land | | 7.7 C | 1.1 C | 0 |

The diagnosis's ~45% -> ~19% was at dT 0.7; this re-solve uses the frame's own dT, hence 15.5%. The ticket's check
(0-20 deg within ~1 C of the no-orbit climate) holds: 25.5 against 25.4.
