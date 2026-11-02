---
id: PW-1325
title: "Finished worlds add the orbit's insolation change at the ice rule's 0.25 C per W/m2: dba204's tropical July is +5 C from it"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: high
found_by: lane121
blocked_by: []
relates: [PW-1279, PW-459, PW-198, PW-555]
refs: [docs/review/base-climate/summer-heat/diagnosis.md, docs/review/base-climate/summer-heat/world_bands.py, "planet/finish.py::orbit_dt", "planet/timezoom/forcing.py::orbit_anomaly", "planet/timezoom/forcing.py::own_k", "planet/icemass.py::seasonal_k", "planet/climate.py::_orbit", worlds/dba204.json, runs/56dee1, "Braconnot et al. 2007 (Clim. Past 3:261)"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: most of what the owner saw on dba204 isn't the climate model. A finished world takes the time
zoom's orbit at that moment and adds its change in sunshine to every month's temperature. It converts sunshine into
degrees with the ice rule's number, 0.25 C per W/m2. PW-459 already found that number is about 3x the land's real
seasonal response. dba204's frame has eccentricity 0.035 with the near-sun point in northern summer. That's +32
W/m2 in July at the equator, so +8 C on tropical land.

Measured (lane 121, world_bands.py --orbit, which reproduces the stored world exactly):

| dba204, ice-free land | stored world (orbit_resp 'run') | same orbit, 'seasons' response | no orbit |
|---|---|---|---|
| warmest month 0-20 deg | 30.5 C | 25.2 | 25.2 |
| warmest month 20-40 deg | 28.6 | 28.2 | 28.0 |
| warmest month 40-60 deg | 22.7 | 19.8 | 18.6 |
| land with warmest month >= 30 C | 45.4% | 19.0% | 18.4% |
| land with warmest month >= 35 C | 18.1% | 6.3% | 5.4% |

Source for the size of the response: Braconnot et al. 2007 (PMIP2, Clim. Past 3:261), mid-Holocene. Orbital
forcing adds 26 W/m2 to the NH seasonal cycle of insolation. The summer warming peaks at ~2 C over central
Eurasia and Tibet. West Africa to N India gets *colder* (more monsoon rain and cloud). That is <= ~0.08 C per
W/m2 on land, and below zero in the monsoon tropics. 0.25 gives +6.5 C.

Options:
- A. **finish.py::orbit_dt uses the 'seasons' response** (icemass.seasonal_k, PW-459's option a) for the finished
  world's climate, whatever the time zoom's own ice rule is. Cost: a frame's displayed climate no longer matches
  the response its ice was grown under. Small at high latitudes (0.08 vs 0.25 changes the ice's summer). The
  ice is the time zoom's, already settled.
- B. Wait for PW-459 (run and zoom move together to the seasons response). That's in the parked ice-age epic
  (PW-470), so finished worlds keep +5-8 C tropical summers until then.
- C. Use 'seasons' in the finish only below some latitude. That's a point fix, so I don't recommend it.

Lean: A. It's one line in finish.py::orbit_dt (`p.orbit_resp` forced to 'seasons'), and the visible tropical
summers are the owner's complaint. The ice doesn't change.

- [ ] dba204 re-finished with A: warmest month 0-20 deg within ~1 C of the no-orbit climate

## Updates
- 2026-11-02: Status needs-decision -> todo. Owner 2026-11-02: A (apply the orbit to a finished world's months at the land's seasonal response). Slam dunk; should have been done and reported rather than asked.
- 2026-11-02: Created from inbox draft draft-finished-frame-orbit-response-too-strong.md (found by lane121).
