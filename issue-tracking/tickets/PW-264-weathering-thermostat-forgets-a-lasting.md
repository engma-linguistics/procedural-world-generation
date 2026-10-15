---
id: PW-264
title: Weathering thermostat forgets a lasting change in degassing in ~200 Myr (rates vs learning baselines, not a CO2 stock)
type: task
status: in-progress
parent: PW-245
subsystem: climate
effort: s
impact: low
found_by: audit-climate-ocean
blocked_by: []
relates: [PW-235]
refs: [planet/tectonics/earth.py, docs/review/audit/climate-ocean.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
In `earth.global_temperature` (earth.py:64-87, 120), `co2 = log(source/source_ref) − log(sink/sink_ref)`. Both references learn toward the current rates over ≤200 Myr, and the index is clipped to ±1.5 (±4.5 °C).

A permanent doubling of degassing first warms ~+1.5 °C: the weathering feedback is `WEATHER_K` = 0.12 on 3 °C per unit. That warming then decays to 0 as the references catch up. In the real carbonate–silicate cycle, CO2 is a stock: it builds until weathering matches degassing, which here would be a permanent +5.8 °C. So the thermostat only damps transients, and long-term temperature is set by `drift`.

This is a sound simplification, not a bandaid, and it is documented ("only changes count"). It is a judgement call.

Options:
- A: keep it, and say in overview §2.6 that sustained forcings fade.
- B: integrate a stock, d(ln CO2)/dt = k·(source − sink(T))/baseline, so weathering is the only restoring force (needs a retune of k and the drift).
- C: slow the references to ≥1 Gyr so sustained forcings persist over a run; the smallest change.

Lean: C, then check on 3–4 L6 seeds that the temperature spread stays sane (test_envelopes).

## Updates
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-climate-ocean-co2-rate-not-stock.md (found by audit-climate-ocean).
